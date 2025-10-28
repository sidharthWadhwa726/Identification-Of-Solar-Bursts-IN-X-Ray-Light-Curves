# backend/helpers/viz/plots.py
import matplotlib.pyplot as plt
import pandas as pd

def final_overlay(binned_time, final_clipped_signal, final_catalog: pd.DataFrame):
    plt.figure(figsize=(14,6))
    plt.plot(binned_time, final_clipped_signal, color="black", label="BG Subtracted & Clipped")
    plt.axhline(0, color="green", ls="--", label="Zero BG")

    if final_catalog is not None and not final_catalog.empty:
        # accept both "PeakFlux_nW_m2" and "PeakFlux_nW/m2"
        flux_col = "PeakFlux_nW_m2" if "PeakFlux_nW_m2" in final_catalog.columns else \
                   ("PeakFlux_nW/m2" if "PeakFlux_nW/m2" in final_catalog.columns else None)

        if flux_col is not None and "PeakTime" in final_catalog.columns:
            plt.scatter(final_catalog["PeakTime"], final_catalog[flux_col],
                        color="red", marker="x", s=60, zorder=10, label="EFP Peaks")

            # y-limits on log scale if we have flux
            yvals = final_catalog[flux_col].values
            if yvals.size:
                lo = max(1.0, float(yvals.min())*0.5)
                hi = float(yvals.max())*1.5
                plt.yscale("log")
                plt.ylim(lo, hi)

    plt.title("Final Flare Catalog (EFP)")
    plt.xlabel("Absolute Time (s)")
    plt.ylabel(r"Flare Flux (nW/m$^2$) [log]")
    plt.grid(True, ls="--", alpha=0.5)
    plt.legend()
    plt.show()
