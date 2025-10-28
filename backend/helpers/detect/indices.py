# backend/helpers/detect/indices.py
import numpy as np

def nearest_indices(time_array: np.ndarray, target_times: np.ndarray | list[float]) -> list[int]:
    """Map float times (e.g., PeakTime) to nearest indices on a monotonic time grid."""
    t = np.asarray(time_array, float)
    targets = np.asarray(target_times, float)
    idx = [int(np.argmin(np.abs(t - tt))) for tt in targets]
    return idx
