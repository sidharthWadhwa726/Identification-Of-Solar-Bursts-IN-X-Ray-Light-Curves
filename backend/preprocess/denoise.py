import numpy as np
from scipy.signal import medfilt

def median(y, k=5):
    k = max(3, int(k) | 1)
    return medfilt(y, k)

def zscore(y, eps=1e-9):
    mu, sd = np.mean(y), np.std(y) + eps
    return (y - mu) / sd, mu, sd
