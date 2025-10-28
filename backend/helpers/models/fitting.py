import numpy as np
import pandas as pd
from dataclasses import dataclass
from typing import Dict, Optional
from scipy.optimize import curve_fit
from .efp import elementary_flare_profile

def robust_mad_sigma(y):
    med = np.median(y)
    mad = np.median(np.abs(y - med)) + 1e-12
    return 1.4826 * mad

@dataclass
class FitProps:
    PeakTime: float
    PeakFlux_nW_m2: float
    StartFWTM: float
    EndFWTM: float
    FittedSNR: float
    DecayTau: float
    RiseSigma: float
    Fitted_A: float
    R_squared: float

def characterize_segment(t, rate, p_opt, background, count_to_nw_m2=1.0) -> Optional[Dict]:
    A, mu, sigma, tau = map(float, p_opt[:4])
    if not np.isfinite([A,mu,sigma,tau]).all() or sigma<=0 or tau<=0:
        return None

    S = elementary_flare_profile(t, A, mu, sigma, tau)
    B = np.maximum(0.0, background)
    Spos = np.maximum(0.0, S)
    denom = Spos + 2*B
    denom[denom < 1e-9] = 1e-9
    snr = float(np.sum(Spos/np.sqrt(denom)))

    td = np.linspace(float(t.min()), float(t.max()), 500)
    yd = elementary_flare_profile(td, A, mu, sigma, tau)
    if yd.size == 0 or not np.isfinite(yd).any(): return None
    k = int(np.nanargmax(yd))
    tpk = float(td[k]); fpk_counts = float(yd[k])
    fpk_nw = fpk_counts * count_to_nw_m2

    ss_res = float(np.sum((rate - S)**2))
    ss_tot = float(np.sum((rate - np.mean(rate))**2) + 1e-12)
    r2 = 1.0 - ss_res/ss_tot

    start_fwtm = tpk - 1.5*abs(sigma)
    end_fwtm   = tpk + 5.0*abs(tau)

    return FitProps(
        PeakTime=tpk,
        PeakFlux_nW_m2=fpk_nw,
        StartFWTM=start_fwtm,
        EndFWTM=end_fwtm,
        FittedSNR=snr,
        DecayTau=abs(tau),
        RiseSigma=abs(sigma),
        Fitted_A=A,
        R_squared=r2
    ).__dict__

def efp_fit_catalog(t, y_sub, bg, prominence, height, count_to_nw_m2=1.0):
    from scipy.signal import find_peaks
    pk, _ = find_peaks(y_sub, prominence=prominence, height=height)
    if pk.size == 0: return pd.DataFrame()

    done = np.zeros_like(y_sub, dtype=bool)
    rows = []
    for p in pk:
        if done[p]: continue
        s = p; e = p
        for i in range(p-1, -1, -1):
            if y_sub[i] <= 0 or i == 0: s = i; break
        for i in range(p+1, len(y_sub)):
            if y_sub[i] <= 0 or i == len(y_sub)-1: e = i; break
        seg_idx = np.arange(s, e+1)
        if seg_idx.size < 5: continue
        tseg, yseg = t[seg_idx], y_sub[seg_idx]
        bseg = bg[seg_idx] if e < len(bg) else None
        if bseg is None: continue
        A0 = float(yseg.max()); mu0 = float(tseg[np.argmax(yseg)])
        p0 = [A0, mu0, 50.0, 200.0]
        lb = [0.0, float(tseg.min()), 1.0, 5.0]
        ub = [A0*2.5, float(tseg.max()), 1000.0, 2000.0]
        try:
            popt,_ = curve_fit(elementary_flare_profile, tseg, yseg, p0=p0, bounds=(lb,ub), maxfev=5000)
            props = characterize_segment(tseg, yseg, popt, bseg, count_to_nw_m2)
            if props and np.isfinite(props["PeakTime"]):
                rows.append(props)
                done[seg_idx] = True
        except Exception:
            continue
    return pd.DataFrame(rows)
