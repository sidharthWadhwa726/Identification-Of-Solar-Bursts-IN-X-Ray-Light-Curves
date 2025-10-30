# backend/helpers/post/anomaly.py
# -- coding: utf-8 --
"""
Score a flare catalog with a saved autoencoder (artifacts from training).
Returns the catalog with `recon_error` and `anomaly` columns added.
"""

from __future__ import annotations
import os, json, pickle
import numpy as np
import pandas as pd
import torch

# We reuse the utilities defined in your train script
from train_autoencoder import canonicalize, feature_engineering, AutoEncoder  # noqa


def score_with_autoencoder(catalog: pd.DataFrame,
                           artifacts_dir: str = "ae_artifacts") -> pd.DataFrame:
    """
    Parameters
    ----------
    catalog : DataFrame
        Filtered EFP catalog (any column names; will be canonicalized).
    artifacts_dir : str
        Folder containing autoencoder.pt, scaler.pkl, threshold.json, features.json

    Returns
    -------
    DataFrame
        Input catalog subset (rows with all required features) + recon_error + anomaly
    """
    # --- Load artifacts ---
    with open(os.path.join(artifacts_dir, "features.json"), "r") as f:
        feat_cfg = json.load(f)
    with open(os.path.join(artifacts_dir, "scaler.pkl"), "rb") as f:
        scaler = pickle.load(f)
    with open(os.path.join(artifacts_dir, "threshold.json"), "r") as f:
        thr_cfg = json.load(f)
    state = torch.load(os.path.join(artifacts_dir, "autoencoder.pt"), map_location="cpu")

    # --- Prepare features from catalog ---
    df = canonicalize(catalog.copy())
    X, features = feature_engineering(df)

    # ensure exact order/columns as training
    need = feat_cfg["features"]
    for c in need:
        if c not in X.columns:
            X[c] = np.nan
    X = X[need].astype(float)
    X = X.replace([np.inf, -np.inf], np.nan).dropna(axis=0)

    if X.empty:
        # No rows had the required features
        out = df.iloc[0:0].copy()
        out["recon_error"] = []
        out["anomaly"] = []
        return out

    Xt = scaler.transform(X)

    # --- Load model & score ---
    model = AutoEncoder(in_dim=len(need))
    model.load_state_dict(state)
    model.eval()
    with torch.no_grad():
        Xt_t = torch.tensor(Xt.values, dtype=torch.float32)
        recon = model(Xt_t).numpy()
    errs = np.mean((Xt.values - recon) ** 2, axis=1)
    thr = float(thr_cfg["value"])
    labels = (errs > thr).astype(int)

    # --- Attach to matching rows only ---
    out = df.loc[X.index].copy()
    out["recon_error"] = errs
    out["anomaly"] = labels
    return out