import numpy as np

def mad_clip(y, n_sigma):
    nz = y[y > 1e-6]
    if len(nz) <= 10:
        return y, None
    med = float(np.median(nz))
    mad = float(np.median(np.abs(nz - med)))
    sigma = 1.4826 * mad
    thr = n_sigma * sigma
    clipped = np.where(y >= thr, y, 0.0)
    return clipped, thr
