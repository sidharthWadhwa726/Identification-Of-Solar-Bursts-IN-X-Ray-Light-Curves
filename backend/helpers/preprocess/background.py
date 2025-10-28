import numpy as np
from scipy.interpolate import interp1d
from scipy.ndimage import gaussian_filter1d

def estimate_background(t, sig, intervals, sigma_g):
    mask = np.ones_like(t, dtype=bool)
    for s,e in intervals:
        mask[(t >= s) & (t <= e)] = False
    qt, qr = t[mask], sig[mask]
    if qt.size < 2:
        return gaussian_filter1d(sig, sigma_g, mode="nearest")
    try:
        f = interp1d(qt, qr, kind="linear", fill_value="extrapolate")
        return f(t)
    except Exception:
        return gaussian_filter1d(sig, sigma_g, mode="nearest")
