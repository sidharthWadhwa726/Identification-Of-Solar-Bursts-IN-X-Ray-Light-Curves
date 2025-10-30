# backend/helpers/post/anomaly.py
from __future__ import annotations
import os
import json
import pickle
import numpy as np
import pandas as pd
import torch

# IMPORTANT: import the module that DEFINES the classes used in the pickles
# so unpickling can resolve e.g. train_autoencoder.StandardScaler
from backend.helpers.train_autoencoder import (
    canonicalize,
    feature_engineering,
    AutoEncoder,
    StandardScaler,   # noqa: F401 (imported for unpickling side-effect)
)

__all__ = ["score_with_autoencoder"]


def _load_artifacts(artifacts_dir: str):
    """
    Load AE artifacts (features.json, scaler.pkl, threshold.json, autoencoder.pt).
    Assumes they were created by backend.helpers.train_autoencoder.
    """
    feats_path = os.path.join(artifacts_dir, "features.json")
    scaler_path = os.path.join(artifacts_dir, "scaler.pkl")
    thr_path = os.path.join(artifacts_dir, "threshold.json")
    model_path = os.path.join(artifacts_dir, "autoencoder.pt")

    if not os.path.exists(feats_path):
        raise FileNotFoundError(f"Missing features.json at {feats_path}")
    if not os.path.exists(scaler_path):
        raise FileNotFoundError(f"Missing scaler.pkl at {scaler_path}")
    if not os.path.exists(thr_path):
        raise FileNotFoundError(f"Missing threshold.json at {thr_path}")
    if not os.path.exists(model_path):
        raise FileNotFoundError(f"Missing autoencoder.pt at {model_path}")

    with open(feats_path, "r") as f:
        feat_cfg = json.load(f)

    # Because we imported train_autoencoder above, pickle can resolve StandardScaler
    with open(scaler_path, "rb") as f:
        scaler = pickle.load(f)

    with open(thr_path, "r") as f:
        thr_cfg = json.load(f)

    state_dict = torch.load(model_path, map_location="cpu")

    return feat_cfg, scaler, thr_cfg, state_dict


def score_with_autoencoder(df: pd.DataFrame, artifacts_dir: str) -> pd.DataFrame:
    """
    Score a flare catalog with a trained autoencoder and return a copy
    that includes 'recon_error' and 'anomaly' columns.

    Parameters
    ----------
    df : DataFrame
        Catalog after reliability filtering. Must contain the columns expected by
        train_autoencoder.feature_engineering().
    artifacts_dir : str
        Folder containing: features.json, scaler.pkl, threshold.json, autoencoder.pt

    Returns
    -------
    DataFrame
        Input rows aligned (subset if features drop NaNs), with
        'recon_error' (float) and 'anomaly' (0/1) columns appended.
    """
    if df is None or df.empty:
        return pd.DataFrame(columns=list(df.columns) + ["recon_error", "anomaly"]) if df is not None else pd.DataFrame()

    feat_cfg, scaler, thr_cfg, state_dict = _load_artifacts(artifacts_dir)

    # Canonicalize columns and engineer features (uses the same functions as training)
    df_canon = canonicalize(df.copy())
    X, feat_names = feature_engineering(df_canon)

    # Ensure the feature order/availability matches training
    need = feat_cfg.get("features", feat_names)
    for c in need:
        if c not in X.columns:
            X[c] = np.nan  # backfill missing features -> will drop in next line
    X = X[need].astype(float)
    # Clean infinities/NaNs the same way as you did during training
    X = X.replace([np.inf, -np.inf], np.nan).dropna(axis=0)

    if X.empty:
        # Nothing left to score after cleaning
        out = df.loc[[]].copy()
        out["recon_error"] = []
        out["anomaly"] = []
        return out

    # Scale and run model
    Xt = scaler.transform(X)  # StandardScaler from training
    model = AutoEncoder(in_dim=len(need))
    model.load_state_dict(state_dict)
    model.eval()

    with torch.no_grad():
        t_in = torch.tensor(Xt.values, dtype=torch.float32)
        recon = model(t_in).numpy()

    errs = np.mean((Xt.values - recon) ** 2, axis=1)

    # Threshold
    thr = float(thr_cfg.get("value", np.quantile(errs, 0.99)))
    labels = (errs > thr).astype(int)

    # Join back to original rows (only those that survived cleaning)
    scored = df.loc[X.index].copy()
    scored["recon_error"] = errs
    scored["anomaly"] = labels

    return scored


# Optional: tiny CLI for debugging
if __name__ == "__main__":
    import argparse
    ap = argparse.ArgumentParser("anomaly-score")
    ap.add_argument("--input", required=True, help="CSV to score")
    ap.add_argument("--artifacts", required=True, help="Artifacts folder")
    ap.add_argument("--output", default="scored_catalog.csv")
    args = ap.parse_args()

    df_in = pd.read_csv(args.input)
    out = score_with_autoencoder(df_in, artifacts_dir=args.artifacts)
    out.to_csv(args.output, index=False)
    print(f"[OK] wrote {args.output} | anomalies: {int(out['anomaly'].sum())}/{len(out)}")