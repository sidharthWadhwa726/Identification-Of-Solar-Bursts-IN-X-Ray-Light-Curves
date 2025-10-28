import pandas as pd
import numpy as np
from typing import Dict, Any, Tuple

DEFAULT_THRESHOLDS = {"snr_min": 8.0, "r2_min": 0.5, "decay_tau_max": 1.0e7}
ALIASES = {
    "PeakTime": ["PeakTime", "peak_time", "t_peak"],
    "PeakFlux": ["PeakFlux_nW/m2", "PeakFlux_nW_m2", "PeakFlux"],
    "StartFWTM": ["StartFWTM"], "EndFWTM": ["EndFWTM"],
    "FittedSNR": ["FittedSNR","SNR"], "DecayTau": ["DecayTau","tau_d"],
    "RiseSigma": ["RiseSigma","sigma"], "R_squared": ["R_squared","R2","r2"],
}

def _canon(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()
    low = {c.lower(): c for c in df.columns}
    for canon, opts in ALIASES.items():
        for o in opts:
            if o in df.columns: df.rename(columns={o: canon}, inplace=True); break
            if o.lower() in low: df.rename(columns={low[o.lower()]: canon}, inplace=True); break
    return df

def _to_num(df, cols):
    for c in cols:
        if c in df.columns: df[c] = pd.to_numeric(df[c], errors="coerce")

def filter_flare_catalog(catalog: pd.DataFrame,
                         thresholds: Dict[str,float] | None = None,
                         adaptive: bool = True,
                         min_keep: int = 5) -> Tuple[pd.DataFrame, Dict[str,Any]]:
    th = {**DEFAULT_THRESHOLDS, **(thresholds or {})}
    if catalog is None or catalog.empty:
        return pd.DataFrame(), {"initial_rows":0,"kept_rows":0,"reasons_count":{},"thresholds_used":th}

    df = _canon(catalog)
    if "Index" in df.columns: df = df.drop(columns=["Index"])
    _to_num(df, ["FittedSNR","R_squared","DecayTau","PeakTime","PeakFlux","RiseSigma","StartFWTM","EndFWTM"])

    initial = len(df)
    snr_mask = df["FittedSNR"] >= th["snr_min"] if "FittedSNR" in df.columns else pd.Series(False, index=df.index)
    r2_mask  = df["R_squared"] >= th["r2_min"] if "R_squared" in df.columns else pd.Series(False, index=df.index)
    tau_mask = df["DecayTau"]  <  th["decay_tau_max"] if "DecayTau"  in df.columns else pd.Series(True, index=df.index)

    keep = df[snr_mask & r2_mask & tau_mask].copy()

    # Adaptive relaxation on SNR if too strict
    used = th.copy()
    if adaptive and len(keep) < max(1,min_keep) and "FittedSNR" in df.columns:
        for pct in (75, 50):
            snr_p = np.nanpercentile(df["FittedSNR"], pct) if df["FittedSNR"].notna().any() else used["snr_min"]
            if snr_p < used["snr_min"]:
                used["snr_min"] = float(snr_p)
                keep = df[(df["FittedSNR"] >= used["snr_min"]) & r2_mask & tau_mask].copy()
            if len(keep) >= max(1,min_keep):
                break

    dropped = df.loc[~df.index.isin(keep.index)]
    reasons = {}
    if not dropped.empty:
        reasons["SNR"] = int((~snr_mask & dropped.index.isin(dropped.index)).sum())
        reasons["R2"]  = int((~r2_mask & dropped.index.isin(dropped.index)).sum())
        reasons["Tau"] = int((~tau_mask & dropped.index.isin(dropped.index)).sum())

    report = {
        "initial_rows": int(initial),
        "kept_rows": int(len(keep)),
        "drop_rows": int(initial - len(keep)),
        "reasons_count": reasons,
        "thresholds_used": used,
    }
    return keep, report
