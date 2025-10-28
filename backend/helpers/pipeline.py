# backend/helpers/pipeline.py
from __future__ import annotations
import numpy as np
import pandas as pd

from .config import Config
from .io.loaders import load_single_day_lc
from .preprocess.denoise import bin_interpolate_smooth
from .detect.peaks import initial_peaks
from .detect.durations import durations
from .detect.merge import merge_intervals
from .preprocess.background import estimate_background
from .detect.clip import mad_clip
from .models.fitting import efp_fit_catalog
from .viz.plots import final_overlay


def full_analysis_no_stitching(path: str, cfg: Config = Config(), do_plot: bool = True):
    """
    End-to-end pipeline (no stitching) that:
      0) loads LC
      1) bins/interpolates/smooths
      2) detects initial peaks
      3-4) builds/merges durations
      5) estimates background
      6) subtracts & MAD-clips
      7) fits EFP and builds catalog

    Returns:
        t_bin (np.ndarray): binned time
        sub_clip (np.ndarray): background-subtracted (and clipped) signal
        cat (pd.DataFrame): EFP-fitted catalog (columns normalized)
        bg (np.ndarray): estimated background (len == len(t_bin))
    """
    # Step 0: load
    df = load_single_day_lc(path)

    # Step 1: bin + interp + smooth
    t_bin, r_bin, r_smooth = bin_interpolate_smooth(
        df, cfg.denoise.bin_size_s, cfg.denoise.sigma_g
    )

    # Step 2: initial peaks
    pidx = initial_peaks(r_bin, cfg.detect.peak_prominence)

    # Step 3–4: durations + merge
    ints = durations(t_bin, r_smooth, pidx, cfg.detect.slope_threshold)
    merged = merge_intervals(ints, cfg.detect.merge_threshold_s)

    # Step 5: background (quiet interpolation, fallback gaussian)
    bg = estimate_background(t_bin, r_bin, merged, cfg.denoise.sigma_g)

    # Step 6: subtract + clip
    sub = np.maximum(0.0, r_bin - bg)
    sub_clip, thr = mad_clip(sub, cfg.clip.n_sigma_clip)

    # Step 7: EFP fit on clipped (bg used inside for SNR calc)
    cat = efp_fit_catalog(
        t_bin, sub_clip, bg,
        cfg.fit.final_peak_prominence,
        cfg.fit.final_peak_height,
        count_to_nw_m2=cfg.fit.count_to_nw_m2
    )

    # normalize peak-flux column spelling for downstream (slash)
    if isinstance(cat, pd.DataFrame) and not cat.empty:
        if "PeakFlux_nW_m2" in cat.columns and "PeakFlux_nW/m2" not in cat.columns:
            cat = cat.rename(columns={"PeakFlux_nW_m2": "PeakFlux_nW/m2"})

    if do_plot and isinstance(cat, pd.DataFrame):
        final_overlay(t_bin, sub_clip, cat)

    return t_bin, sub_clip, cat, bg
