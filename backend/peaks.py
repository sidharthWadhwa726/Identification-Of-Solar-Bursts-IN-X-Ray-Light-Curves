import numpy as np

def adaptive_threshold(yz, hi=3.0, lo=1.5, min_len=10):
    """
    yz: z-scored series
    hi/lo: hysteresis thresholds in sigma
    min_len: min contiguous samples for a burst
    """
    above_hi = yz > hi
    above_lo = yz > lo
    starts, ends = [], []
    i, n = 0, len(yz)
    while i < n:
        if above_hi[i]:
            s = i
            i += 1
            while i < n and above_lo[i]: i += 1
            e = i - 1
            if e - s + 1 >= min_len:
                starts.append(s); ends.append(e)
        else:
            i += 1
    return list(zip(starts, ends))
