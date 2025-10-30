# backend/helpers/viz/plots.py
import numpy as np
import matplotlib.pyplot as plt

def final_overlay(time_array,
                  sub_clipped_signal,
                  final_catalog,
                  bg=None,
                  raw=None,
                  show_bg: bool = True,
                  show_raw: bool = False,
                  include_bg_in_signal: bool = False):
    """
    Final overview plot:
      - Signal line: BG-subtracted & clipped, or optionally re-added background
      - optional Background curve (green, dashed) if show_bg and bg provided
      - optional Raw binned signal (light gray) if show_raw and raw provided
      - EFP peak markers from final_catalog (red 'x')
    """
    plt.figure(figsize=(14, 6))

    if show_raw and raw is not None:
        plt.plot(time_array, raw, color='0.8', linewidth=0.8, label='Raw (binned)')

    # Main signal (optionally re-add background)
    if include_bg_in_signal and bg is not None:
        signal = sub_clipped_signal + bg
        label = 'Signal (background added)'
    else:
        signal = sub_clipped_signal
        label = 'BG-subtracted (clipped)'

    plt.plot(time_array, signal, color='black', linewidth=1.2, label=label)

    # Background curve
    if show_bg and bg is not None:
        plt.plot(time_array, bg, color='green', linestyle='--', linewidth=1.2,
                 label='Background')

    # Detected peaks from catalog
    if final_catalog is not None and len(final_catalog) > 0:
        xcol = "PeakTime" if "PeakTime" in final_catalog.columns else None
        ycol = ("PeakFlux_nW/m2" if "PeakFlux_nW/m2" in final_catalog.columns
                else ("PeakFlux_nW_m2" if "PeakFlux_nW_m2" in final_catalog.columns else None))
        if xcol:
            xvals = final_catalog[xcol].astype(float).values
            yvals = (final_catalog[ycol].astype(float).values
                     if ycol is not None else np.interp(xvals, time_array, signal))

            if include_bg_in_signal and bg is not None and ycol is not None:
                bg_at_peaks = np.interp(xvals, time_array, bg)
                yvals = yvals + bg_at_peaks

            plt.scatter(xvals, yvals,
                        color='red', marker='x', s=60, zorder=10,
                        label='EFP Peaks')

    plt.title("Final Flare Catalog – Signal and (optional) Background")
    plt.xlabel("Time (s)")
    plt.ylabel(r"Flux / Counts")
    plt.yscale("log")
    plt.grid(True, linestyle='--', alpha=0.5)
    plt.legend()
    plt.tight_layout()
    plt.show()
