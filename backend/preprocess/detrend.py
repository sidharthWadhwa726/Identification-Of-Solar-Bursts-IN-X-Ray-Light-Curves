import numpy as np
from scipy.signal import savgol_filter

def rolling_quantile_baseline(y, win=301, q=0.2):
    win = max(5, int(win) | 1)
    pad = win//2
    ypad = np.pad(y, (pad, pad), mode="edge")
    bas = np.array([np.quantile(ypad[i:i+win], q) for i in range(len(y))])
    return bas

def remove_trend(time, flux, method="quantile", **kw):
    if method == "quantile":
        base = rolling_quantile_baseline(flux, **kw)
    elif method == "savgol":
        base = savgol_filter(flux, kw.get("win", 301)|1, kw.get("poly", 3))
    else:
        raise ValueError("unknown detrend method")
    return flux - base, base
