import numpy as np
import pandas as pd
from scipy.stats import binned_statistic
from scipy.ndimage import gaussian_filter1d

def bin_interpolate_smooth(df, bin_size_s, sigma_g):
    t = df["TIME"].values; r = df["RATE"].values
    edges = np.arange(t.min(), t.max() + bin_size_s, bin_size_s)
    r_bin, _, _ = binned_statistic(t, r, statistic="mean", bins=edges)
    t_bin = (edges[:-1] + edges[1:]) / 2.0
    tmp = pd.DataFrame({"TIME": t_bin, "RATE": r_bin}).interpolate("linear", limit_direction="both")
    t_i = tmp["TIME"].values; r_i = tmp["RATE"].values
    smoothed = gaussian_filter1d(r_i, sigma_g, mode="nearest")
    return t_i, r_i, smoothed
