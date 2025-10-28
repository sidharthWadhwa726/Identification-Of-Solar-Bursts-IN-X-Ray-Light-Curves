# backend/helpers/post/filters.py
from __future__ import annotations
import numpy as np
import pandas as pd
from typing import Dict, Any, Tuple

# ---------- Defaults & Column Aliases ----------
DEFAULT_THRESHOLDS = {
    "snr_min": 8.0,        # minimum FittedSNR
    "r2_min": 0.5,         # minimum R^2
    "decay_tau_max": 1.0e7 # reject absurdly large DecayTau
}

# Canonical name -> acceptable aliases
ALIASES: dict[str, list[str]] = {
    "PeakTime":   ["PeakTime", "peak_time", "t_peak"],
    "PeakFlux":   ["PeakFlux_nW/m2", "PeakFlux_nW_m2", "PeakFlux", "peak_flux"],
    "StartFWTM":  ["StartFWTM", "t_start_fwtm"],
    "EndFWTM":    ["EndFWTM", "t_end_fwtm"],
    "FittedSNR":  ["FittedSNR", "SNR", "snr"],
    "DecayTau":   ["DecayTau", "tau_d", "tau_decay"],
    "RiseSigma":  ["RiseSigma", "sigma_rise", "sigma"],
    "R_squared":  ["R_squared", "R2", "r2"],
}

# ---------- Helpers ----------
def _canon(df: pd.DataFrame) -> pd.DataFrame:
    """Map various alias column names to a canonical set (in-place rename)."""
    out = df.copy()
    lower_map = {c.lower(): c for c in out.columns}
    for canon, aliases in ALIASES.items():
        for a in aliases:
            if a in out.columns:
                out.rename(columns={a: canon}, inplace=True)
                break
            al = a.lower()
            if al in lower_map:
                out.rename(columns={lower_map[al]: canon}, inplace=True)
                break
    return out

def _to_num(df: pd.DataFrame, cols: list[str]) -> None:
    """Ensure numeric dtype (coerce errors to NaN)."""
    for c in cols:
        if c in df.columns:
            df[c] = pd.to_numeric(df[c], errors="coerce")

# ---------- Main Entry ----------
def filter_flare_catalog(
    catalog: pd.DataFrame,
    thresholds: Dict[str, float] | None = None,
    adaptive: bool = True,
    min_keep: int = 5,
) -> Tuple[pd.DataFrame, Dict[str, Any]]:
    """
    Robustly filter an EFP-fitted flare catalog.

    Parameters
    ----------
    catalog : DataFrame
        Input catalog with columns like PeakTime, PeakFlux, FittedSNR, R_squared, DecayTau, ...
        (Column names are normalized internally.)
    thresholds : dict
        {'snr_min': float, 'r2_min': float, 'decay_tau_max': float}
    adaptive : bool
        If True and too few survive, relax SNR to 75th, then 50th percentile.
    min_keep : int
        Target minimum rows to keep under adaptive relaxation.

    Returns
    -------
    filtered : DataFrame
        Filtered catalog (with canonical column names).
    report : dict
        {'initial_rows', 'kept_rows', 'drop_rows', 'reasons_count', 'thresholds_used', 'stats'}
    """
    th = {**DEFAULT_THRESHOLDS, **(thresholds or {})}

    if catalog is None or catalog.empty:
        return pd.DataFrame(), {
            "initial_rows": 0,
            "kept_rows": 0,
            "drop_rows": 0,
            "reasons_count": {},
            "thresholds_used": th,
            "stats": {},
            "note": "empty input",
        }

    df = _canon(catalog)
    if "Index" in df.columns:
        df = df.drop(columns=["Index"])

    _to_num(df, ["FittedSNR", "R_squared", "DecayTau", "PeakTime",
                 "PeakFlux", "RiseSigma", "StartFWTM", "EndFWTM"])

    initial = len(df)

    # Masks (NaNs will evaluate to False in comparisons)
    snr_mask = (df["FittedSNR"] >= th["snr_min"]) if "FittedSNR" in df.columns else pd.Series(False, index=df.index)
    r2_mask  = (df["R_squared"] >= th["r2_min"]) if "R_squared" in df.columns else pd.Series(False, index=df.index)
    tau_mask = (df["DecayTau"]  <  th["decay_tau_max"]) if "DecayTau"  in df.columns else pd.Series(True,  index=df.index)

    keep_mask = snr_mask & r2_mask & tau_mask
    kept = df.loc[keep_mask].copy()

    thresholds_used = th.copy()

    # Adaptive SNR relaxation if too strict
    if adaptive and len(kept) < max(1, min_keep) and "FittedSNR" in df.columns:
        for pct in (75, 50):
            if df["FittedSNR"].notna().any():
                snr_p = float(np.nanpercentile(df["FittedSNR"], pct))
                if snr_p < thresholds_used["snr_min"]:
                    thresholds_used["snr_min"] = snr_p
                    snr_mask = (df["FittedSNR"] >= thresholds_used["snr_min"])
                    keep_mask = snr_mask & r2_mask & tau_mask
                    kept = df.loc[keep_mask].copy()
            if len(kept) >= max(1, min_keep):
                break

    # ----- Reasons (fixed: use same-shape masks) -----
    dropped_mask = ~keep_mask
    reasons: dict[str, int] = {}
    if "FittedSNR" in df.columns:
        reasons["SNR"] = int((dropped_mask & ~snr_mask).sum())
    if "R_squared" in df.columns:
        reasons["R2"] = int((dropped_mask & ~r2_mask).sum())
    if "DecayTau" in df.columns:
        reasons["Tau"] = int((dropped_mask & ~tau_mask).sum())

    report = {
        "initial_rows": int(initial),
        "kept_rows": int(len(kept)),
        "drop_rows": int(initial - len(kept)),
        "reasons_count": reasons,
        "thresholds_used": thresholds_used,
        "stats": {
            "snr_min": float(np.nanmin(df["FittedSNR"])) if "FittedSNR" in df.columns and df["FittedSNR"].notna().any() else None,
            "snr_med": float(np.nanmedian(df["FittedSNR"])) if "FittedSNR" in df.columns and df["FittedSNR"].notna().any() else None,
            "snr_max": float(np.nanmax(df["FittedSNR"])) if "FittedSNR" in df.columns and df["FittedSNR"].notna().any() else None,
        },
    }

    return kept, report