# -- coding: utf-8 --
"""
Train an unsupervised autoencoder on EFP-fitted flare catalogs for anomaly detection.
- Learns to reconstruct "normal" events; anomalies = high reconstruction error
- Saves: model.pt, scaler.pkl, threshold.json, features.json
"""

import argparse, json, math, os, pickle, random, sys
import numpy as np
import pandas as pd

# ---- Torch (install if missing): pip install torch --extra-index-url https://download.pytorch.org/whl/cpu
import torch
import torch.nn as nn
from torch.utils.data import DataLoader, TensorDataset, random_split

# ----------------------- Config -----------------------
ALIASES = {
    "PeakTime":   ["PeakTime","peak_time","t_peak"],
    "PeakFlux":   ["PeakFlux_nW/m2","PeakFlux_nW_m2","PeakFlux","peak_flux"],
    "StartFWTM":  ["StartFWTM","t_start_fwtm"],
    "EndFWTM":    ["EndFWTM","t_end_fwtm"],
    "FittedSNR":  ["FittedSNR","SNR","snr"],
    "DecayTau":   ["DecayTau","tau_d","tau_decay"],
    "RiseSigma":  ["RiseSigma","sigma_rise","sigma"],
    "R_squared":  ["R_squared","R2","r2"],
}

# Primary features we’ll use (robust to unit/scales)
BASE_FEATURES = [
    "PeakFlux", "FittedSNR", "DecayTau", "RiseSigma",
    "Duration", "R_squared"
]

def find_col(df, names):
    low = {c.lower(): c for c in df.columns}
    for n in names:
        if n in df.columns: return n
        if n.lower() in low: return low[n.lower()]
    return None

def canonicalize(df):
    df = df.copy()
    for canon, opts in ALIASES.items():
        col = find_col(df, opts)
        if col and col != canon:
            df.rename(columns={col: canon}, inplace=True)
    return df

def feature_engineering(df):
    # Duration = EndFWTM - StartFWTM (fallback to NaN if missing)
    if "StartFWTM" in df.columns and "EndFWTM" in df.columns:
        df["Duration"] = pd.to_numeric(df["EndFWTM"], errors="coerce") - pd.to_numeric(df["StartFWTM"], errors="coerce")
    else:
        df["Duration"] = np.nan

    # cast key columns to numeric
    for c in ["PeakFlux","FittedSNR","DecayTau","RiseSigma","Duration","R_squared"]:
        if c in df.columns:
            df[c] = pd.to_numeric(df[c], errors="coerce")

    # log transforms for skewed stuff (safe log)
    def safe_log(x):
        x = np.asarray(x, float)
        return np.log(np.clip(x, 1e-12, None))

    df["log_PeakFlux"] = safe_log(df.get("PeakFlux", np.nan))
    df["log_DecayTau"] = safe_log(df.get("DecayTau", np.nan))
    df["log_RiseSigma"] = safe_log(df.get("RiseSigma", np.nan))
    df["log_Duration"]  = safe_log(df.get("Duration", np.nan))

    # final feature set (choose between raw/log variants)
    features = [
        "log_PeakFlux", "FittedSNR", "log_DecayTau",
        "log_RiseSigma", "log_Duration", "R_squared"
    ]
    X = df[features].astype(float)
    X = X.replace([np.inf,-np.inf], np.nan).dropna(axis=0)
    return X, features

class StandardScaler:
    def fit(self, x):
        self.mean_ = x.mean(axis=0)
        self.std_  = x.std(axis=0).replace(0, 1.0)
        return self
    def transform(self, x):
        return (x - self.mean_) / self.std_
    def fit_transform(self, x): return self.fit(x).transform(x)

class AutoEncoder(nn.Module):
    def __init__(self, in_dim, hidden=(32,16,8)):
        super().__init__()
        h1,h2,h3 = hidden
        self.enc = nn.Sequential(
            nn.Linear(in_dim, h1), nn.ReLU(),
            nn.Linear(h1, h2),     nn.ReLU(),
            nn.Linear(h2, h3),     nn.ReLU()
        )
        self.dec = nn.Sequential(
            nn.Linear(h3, h2),     nn.ReLU(),
            nn.Linear(h2, h1),     nn.ReLU(),
            nn.Linear(h1, in_dim)
        )
    def forward(self, x):
        z = self.enc(x)
        out = self.dec(z)
        return out

def set_seed(seed=42):
    random.seed(seed); np.random.seed(seed); torch.manual_seed(seed)

def choose_threshold(errors, method="quantile", q=0.99):
    errors = np.asarray(errors, float)
    errors = errors[~np.isnan(errors)]
    if method == "quantile":
        return float(np.quantile(errors, q))
    # robust IQR
    q1, q3 = np.quantile(errors, [0.25, 0.75])
    iqr = q3 - q1
    return float(q3 + 1.5*iqr)

def train(args):
    set_seed(args.seed)

    # ---------- Load & features ----------
    df = pd.read_csv(args.input)
    df = canonicalize(df)
    X, features = feature_engineering(df)
    if len(X) < 50:
        print(f"[FATAL] Not enough rows after cleaning (got {len(X)})."); sys.exit(1)

    # Optional: pick "normal" subset to train (e.g., central SNR band)
    if args.normal_band:
        low, high = args.normal_band
        if "FittedSNR" in X.columns:
            mask = (X["FittedSNR"] >= low) & (X["FittedSNR"] <= high)
            X_train = X.loc[mask].copy()
            if len(X_train) < 30:
                X_train = X.copy()
        else:
            X_train = X.copy()
    else:
        X_train = X.copy()

    # Standardize
    scaler = StandardScaler()
    Xs = scaler.fit_transform(X_train)
    Xt = scaler.transform(X)  # full data for scoring

    # Torch datasets
    Xs_t = torch.tensor(Xs.values, dtype=torch.float32)
    ds = TensorDataset(Xs_t)
    n_val = max(1, int(len(ds)*args.val_split))
    n_tr  = len(ds) - n_val
    tr, va = random_split(ds, [n_tr, n_val])
    dl_tr = DataLoader(tr, batch_size=args.batch, shuffle=True)
    dl_va = DataLoader(va, batch_size=args.batch, shuffle=False)

    # Model
    model = AutoEncoder(in_dim=Xs_t.shape[1], hidden=tuple(args.hidden))
    device = torch.device("cpu")
    model.to(device)
    optim = torch.optim.Adam(model.parameters(), lr=args.lr, weight_decay=1e-5)
    crit  = nn.MSELoss()

    # Train
    best_va = math.inf
    patience = args.patience
    wait = 0
    for epoch in range(args.epochs):
        model.train()
        tr_loss = 0.0
        for (xb,) in dl_tr:
            xb = xb.to(device)
            optim.zero_grad()
            recon = model(xb)
            loss = crit(recon, xb)
            loss.backward()
            optim.step()
            tr_loss += loss.item() * len(xb)
        tr_loss /= max(1, len(tr))

        # val
        model.eval()
        with torch.no_grad():
            va_loss = 0.0
            for (xb,) in dl_va:
                xb = xb.to(device)
                recon = model(xb)
                loss = crit(recon, xb)
                va_loss += loss.item() * len(xb)
            va_loss /= max(1, len(va))

        print(f"Epoch {epoch+1:03d} | train {tr_loss:.6f} | val {va_loss:.6f}")

        if va_loss + 1e-8 < best_va:
            best_va = va_loss; wait = 0
            best_state = {k: v.cpu().clone() for k, v in model.state_dict().items()}
        else:
            wait += 1
            if wait >= patience:
                print(f"[EarlyStop] best val {best_va:.6f} at epoch {epoch+1-wait}")
                break

    if 'best_state' in locals():
        model.load_state_dict(best_state)

    # Score full dataset
    model.eval()
    with torch.no_grad():
        Xt_t = torch.tensor(Xt.values, dtype=torch.float32)
        recon = model(Xt_t).numpy()
    errs = np.mean((Xt.values - recon)**2, axis=1)

    # Threshold
    thr = choose_threshold(errs, method=args.thr_method, q=args.thr_q)
    labels = (errs > thr).astype(int)

    # Save artifacts
    os.makedirs(args.outdir, exist_ok=True)
    torch.save(model.state_dict(), os.path.join(args.outdir, "autoencoder.pt"))
    with open(os.path.join(args.outdir, "scaler.pkl"), "wb") as f:
        pickle.dump(scaler, f)
    with open(os.path.join(args.outdir, "threshold.json"), "w") as f:
        json.dump({"method": args.thr_method, "q": args.thr_q, "value": float(thr)}, f)
    with open(os.path.join(args.outdir, "features.json"), "w") as f:
        json.dump({"features": features}, f, indent=2)

    # Write scored CSV
    out = df.loc[X.index].copy()
    out["recon_error"] = errs
    out["anomaly"] = labels
    out_path = os.path.join(args.outdir, "scored_catalog.csv")
    out.to_csv(out_path, index=False)

    print(f"[OK] Saved model + scaler + threshold in: {args.outdir}")
    print(f"[OK] Scored catalog: {out_path}")
    print(f"[INFO] Threshold = {thr:.6g}  (method={args.thr_method}, q={args.thr_q})")
    print(f"[INFO] Anomalies flagged: {int(labels.sum())}/{len(labels)}")

def parse_args():
    p = argparse.ArgumentParser()
    p.add_argument("--input", required=True, help="Path to EFP-fitted CSV (e.g., final_flare_catalog.csv)")
    p.add_argument("--outdir", default="ae_artifacts", help="Output directory")
    p.add_argument("--epochs", type=int, default=200)
    p.add_argument("--batch", type=int, default=64)
    p.add_argument("--lr", type=float, default=1e-3)
    p.add_argument("--hidden", type=int, nargs=3, default=[32,16,8], help="Three hidden sizes")
    p.add_argument("--val-split", type=float, default=0.1)
    p.add_argument("--patience", type=int, default=20)
    p.add_argument("--thr-method", choices=["quantile","iqr"], default="quantile")
    p.add_argument("--thr-q", type=float, default=0.99, help="Quantile for threshold if thr-method=quantile")
    p.add_argument("--seed", type=int, default=42)
    p.add_argument("--normal-band", type=float, nargs=2, metavar=("SNR_LOW","SNR_HIGH"),
                   help="If set, train only on rows with SNR in [low, high] (e.g., 3 20)")
    return p.parse_args()

if __name__ == "__main__":
    args = parse_args()
    train(args)