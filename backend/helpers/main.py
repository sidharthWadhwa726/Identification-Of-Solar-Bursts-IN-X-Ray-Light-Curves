# backend/helpers/main.py
from __future__ import annotations
import argparse
import warnings
from astropy.units import UnitsWarning
import pandas as pd

from .config import Config
from .pipeline import full_analysis_no_stitching
from .post.filters import filter_flare_catalog
from .detect.indices import nearest_indices
from .viz.efp_plots import plot_efp_on_selected_peaks
from .viz.plots import final_overlay
from .post.anomaly import score_with_autoencoder   # <--- added

warnings.filterwarnings("ignore", category=UnitsWarning)


def build_argparser():
    ap = argparse.ArgumentParser("solarburst")
    ap.add_argument("--in", dest="infile", required=True, help="Input .lc/.fits path")
    ap.add_argument("--plot", action="store_true", help="Show overview plot")

    # sensitivity knobs
    ap.add_argument("--bin", type=float, dest="bin_size")
    ap.add_argument("--sigma-g", type=float, dest="sigma_g")
    ap.add_argument("--prom", type=float, dest="prom")
    ap.add_argument("--slope", type=float, dest="slope")
    ap.add_argument("--merge", type=float, dest="merge")
    ap.add_argument("--clip", type=float, dest="clip")

    # efp fit
    ap.add_argument("--fit-prom", type=float, dest="fit_prom")
    ap.add_argument("--fit-height", type=float, dest="fit_height")
    ap.add_argument("--count-to-nw", type=float, dest="count_to_nw")

    # post-filter thresholds
    ap.add_argument("--snr-min", type=float, default=8.0)
    ap.add_argument("--r2-min", type=float, default=0.5)
    ap.add_argument("--tau-max", type=float, default=1.0e7)
    ap.add_argument("--no-adaptive", action="store_true")
    ap.add_argument("--min-keep", type=int, default=5)

    # plotting
    ap.add_argument("--plot-efp", action="store_true")
    ap.add_argument("--topk", type=int, default=0)
    ap.add_argument("--save-dir", type=str, default=None)

    # debug dumps
    ap.add_argument("--write-debug", action="store_true")

    # --- NEW AE options ---
    ap.add_argument("--ae-artifacts", type=str, default=None,
                    help="Folder containing trained AE artifacts")
    ap.add_argument("--ae-output", type=str, default=None,
                    help="Write scored catalog with anomaly labels")
    ap.add_argument("--drop-anomalies", action="store_true",
                    help="Remove anomalies from final catalog automatically")
    ap.add_argument("--anomalies-out", type=str, default=None,
                    help="Optional CSV to save only anomalous events")
    return ap


def main():
    args = build_argparser().parse_args()

    # compose config
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

    # ---------- PIPELINE ----------
    t, y, cat, bg = full_analysis_no_stitching(args.infile, cfg, do_plot=args.plot)

    # ---------- FILTER ----------
    df_fitted = cat.copy() if isinstance(cat, pd.DataFrame) else pd.DataFrame()
    filtered, report = filter_flare_catalog(
        df_fitted,
        thresholds={"snr_min": args.snr_min,
                    "r2_min": args.r2_min,
                    "decay_tau_max": args.tau_max},
        adaptive=not args.no_adaptive,
        min_keep=args.min_keep
    )

    print("\n--- Filter report ---")
    for k, v in report.items():
        print(f"{k}: {v}")

    if args.write_debug:
        df_fitted.to_csv("flare_catalog_raw.csv", index=False)
        filtered.to_csv("flare_catalog_filtered.csv", index=False)
        print(f"[OK] wrote flare_catalog_raw.csv ({len(df_fitted)})")
        print(f"[OK] wrote flare_catalog_filtered.csv ({len(filtered)})")

    # ---------- AUTOENCODER ANOMALY DETECTION ----------
    base = filtered if not filtered.empty else df_fitted
    if args.ae_artifacts:
        try:
            scored = score_with_autoencoder(base, artifacts_dir=args.ae_artifacts)
            if args.ae_output:
                scored.to_csv(args.ae_output, index=False)
                print(f"[OK] AE-scored catalog → {args.ae_output}")

            # remove anomalies if requested
            if "anomaly" in scored.columns:
                total = len(scored)
                n_anom = int(scored["anomaly"].sum())
                print(f"[AE] anomalies detected: {n_anom}/{total}")

                if args.drop_anomalies:
                    anomalies = scored[scored["anomaly"] == 1]
                    base = scored[scored["anomaly"] == 0].drop(columns=["anomaly", "recon_error"])
                    if args.anomalies_out:
                        anomalies.to_csv(args.anomalies_out, index=False)
                        print(f"[AE] wrote anomalies → {args.anomalies_out} ({len(anomalies)} rows)")
                    print(f"[CLEAN] removed anomalies; {len(base)} rows remain.")
                else:
                    base = scored.drop(columns=["recon_error"])  # keep anomaly label for info

        except Exception as e:
            print(f"[AE] Skipped: {e}")

    # ---------- FINAL OVERLAY ----------
    if args.plot:
        final_overlay(
            t, y, base,
            bg=bg,
            show_bg=False,
            show_raw=False,
            include_bg_in_signal=True
        )

    # ---------- PER-PEAK PLOTS ----------
    if args.plot_efp:
        cat_vis = base
        if not cat_vis.empty:
            if args.topk and "FittedSNR" in cat_vis.columns:
                cat_vis = cat_vis.sort_values("FittedSNR", ascending=False).head(args.topk)
            elif args.topk:
                cat_vis = cat_vis.head(args.topk)

            time_col = "PeakTime" if "PeakTime" in cat_vis.columns else cat_vis.columns[0]
            peak_times = cat_vis[time_col].astype(float).values
            peak_idx = nearest_indices(t, peak_times)

            plot_efp_on_selected_peaks(
                time_array=t,
                signal_array=y,
                peak_indices=peak_idx,
                background_array=bg,
                save_dir=args.save_dir,
                show=True,
                title_prefix="EFP Fit"
            )
        else:
            print("[INFO] No rows to visualize.")

    # ---------- FINAL SAVE ----------
    base.to_csv("final_flare_catalog.csv", index=False)
    print(f"[OK] wrote final_flare_catalog.csv ({len(base)} rows)")


if __name__ == "__main__":
    main()