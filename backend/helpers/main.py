# backend/helpers/main.py
from __future__ import annotations
import argparse
import warnings
from astropy.units import UnitsWarning
import pandas as pd

from .config import Config
from .pipeline import full_analysis_no_stitching

# post-pipeline goodies
from .post.filters import filter_flare_catalog
from .detect.indices import nearest_indices
from .viz.efp_plots import plot_efp_on_selected_peaks
from .viz.plots import final_overlay

warnings.filterwarnings("ignore", category=UnitsWarning)  # silence 'counts/s' unit warning


def build_argparser():
    ap = argparse.ArgumentParser("solarburst")
    ap.add_argument("--in", dest="infile", required=True, help="Input .lc/.fits path")
    ap.add_argument("--plot", action="store_true", help="Show pipeline overview plot")

    # sensitivity knobs
    ap.add_argument("--bin", type=float, dest="bin_size", help="Binning in seconds (default from Config)")
    ap.add_argument("--sigma-g", type=float, dest="sigma_g", help="Gaussian sigma for smoothing")
    ap.add_argument("--prom", type=float, dest="prom", help="Initial peak prominence")
    ap.add_argument("--slope", type=float, dest="slope", help="Slope threshold for durations")
    ap.add_argument("--merge", type=float, dest="merge", help="Merge threshold in seconds")
    ap.add_argument("--clip", type=float, dest="clip", help="MAD sigma clip for subtracted signal")

    # efp fit gates
    ap.add_argument("--fit-prom", type=float, dest="fit_prom", help="Final EFP peak prominence")
    ap.add_argument("--fit-height", type=float, dest="fit_height", help="Final EFP min height")
    ap.add_argument("--count-to-nw", type=float, dest="count_to_nw", help="Counts→nW/m^2 factor")

    # post-filter thresholds
    ap.add_argument("--snr-min", type=float, default=8.0, help="Post filter: min FittedSNR (default 8.0)")
    ap.add_argument("--r2-min", type=float, default=0.5, help="Post filter: min R^2 (default 0.5)")
    ap.add_argument("--tau-max", type=float, default=1.0e7, help="Post filter: max DecayTau (default 1e7)")
    ap.add_argument("--no-adaptive", action="store_true", help="Disable adaptive SNR relaxation")
    ap.add_argument("--min-keep", type=int, default=5, help="Adaptive target minimum rows to keep")

    # per-peak EFP plotting
    ap.add_argument("--plot-efp", action="store_true", help="Draw EFP fits around catalog/filtered peaks")
    ap.add_argument("--topk", type=int, default=0, help="If >0, plot only top-K by FittedSNR")
    ap.add_argument("--save-dir", type=str, default=None, help="Folder to save per-peak plots")

    # debug dumps
    ap.add_argument("--write-debug", action="store_true", help="Write raw/filtered catalogs to CSV")
    return ap


def main():
    args = build_argparser().parse_args()

    # Compose config (allow CLI overrides)
    cfg = Config()
    if args.bin_size   is not None: cfg.denoise.bin_size_s = args.bin_size
    if args.sigma_g    is not None: cfg.denoise.sigma_g = args.sigma_g
    if args.prom       is not None: cfg.detect.peak_prominence = args.prom
    if args.slope      is not None: cfg.detect.slope_threshold = args.slope
    if args.merge      is not None: cfg.detect.merge_threshold_s = args.merge
    if args.clip       is not None: cfg.clip.n_sigma_clip = args.clip
    if args.fit_prom   is not None: cfg.fit.final_peak_prominence = args.fit_prom
    if args.fit_height is not None: cfg.fit.final_peak_height = args.fit_height
    if args.count_to_nw is not None: cfg.fit.count_to_nw_m2 = args.count_to_nw

    # -------------- PIPELINE --------------
    t, y, cat, bg = full_analysis_no_stitching(args.infile, cfg, do_plot=args.plot)

    # -------------- POST-FILTER --------------
    df_fitted = cat.copy() if isinstance(cat, pd.DataFrame) else pd.DataFrame()
    filtered, report = filter_flare_catalog(
        df_fitted,
        thresholds={
            "snr_min": args.snr_min,
            "r2_min": args.r2_min,
            "decay_tau_max": args.tau_max
        },
        adaptive=not args.no_adaptive,
        min_keep=args.min_keep
    )

    print("\n--- Filter report ---")
    for k, v in report.items():
        print(f"{k}: {v}")

    if args.write_debug:
        df_fitted.to_csv("flare_catalog_raw.csv", index=False)
        filtered.to_csv("flare_catalog_filtered.csv", index=False)
        print(f"[OK] wrote flare_catalog_raw.csv ({len(df_fitted)} rows)")
        print(f"[OK] wrote flare_catalog_filtered.csv ({len(filtered)} rows)")

    # -------------- FINAL OVERLAY PLOT --------------
    if args.plot:
        cat_for_plot = filtered if not filtered.empty else df_fitted
        final_overlay(
            t,
            y,
            cat_for_plot,
            bg=bg,
            show_bg=False,
            show_raw=False,
            include_bg_in_signal=True
        )

    # -------------- PER-PEAK PLOTS (optional) --------------
    if args.plot_efp:
        # choose set to visualize: filtered if non-empty, else raw
        cat_vis = filtered if not filtered.empty else df_fitted
        if not cat_vis.empty:
            # top-K by SNR if requested
            if args.topk and "FittedSNR" in cat_vis.columns:
                cat_vis = cat_vis.sort_values("FittedSNR", ascending=False).head(args.topk)
            elif args.topk:
                cat_vis = cat_vis.head(args.topk)

            # robust time column
            time_col = "PeakTime" if "PeakTime" in cat_vis.columns else cat_vis.columns[0]
            peak_times = cat_vis[time_col].astype(float).values
            peak_idx = nearest_indices(t, peak_times)

            plot_efp_on_selected_peaks(
                time_array=t,
                signal_array=y,      # BG-sub + clipped
                peak_indices=peak_idx,
                background_array=bg, # overlay BG in green
                save_dir=args.save_dir,
                show=True,
                title_prefix="EFP Fit"
            )
        else:
            print("[INFO] No rows to visualize for per-peak plots.")

    # Always write a unified catalog CSV for downstream (filtered preferred)
    out = filtered if not filtered.empty else df_fitted
    if out is not None:
        out.to_csv("final_flare_catalog.csv", index=False)
        print(f"[OK] wrote final_flare_catalog.csv ({len(out)} rows)")


if __name__ == "__main__":
    main()
