import numpy as np

def slope_windows(time, smoothed, peak_idx, slope_thresh):
    n = len(time)
    if peak_idx < 4 or peak_idx >= n-4: return None
    # left
    s = peak_idx
    for i in range(peak_idx-4, 0, -1):
        x = time[i-3:i+1]; y = smoothed[i-3:i+1]
        if len(x) != 4 or np.isnan(x).any() or np.isnan(y).any(): continue
        slope = np.polyfit(x, y, 1)[0]
        if abs(slope) < slope_thresh: s = i; break
    # right
    e = peak_idx
    for i in range(peak_idx, n-4):
        x = time[i:i+4]; y = smoothed[i:i+4]
        if len(x) != 4 or np.isnan(x).any() or np.isnan(y).any(): continue
        slope = np.polyfit(x, y, 1)[0]
        if abs(slope) < slope_thresh: e = i+4; break
    return (time[s], time[e]) if (s < e) else None

def durations(time, smoothed, peak_indices, slope_thresh):
    out = []
    for p in peak_indices:
        de = slope_windows(time, smoothed, p, slope_thresh)
        if de is None:
            # tiny fallback window
            i0 = max(0, p-2); i1 = min(len(time)-1, p+2)
            if i0 < i1: out.append((time[i0], time[i1]))
        else:
            out.append(de)
    return out
