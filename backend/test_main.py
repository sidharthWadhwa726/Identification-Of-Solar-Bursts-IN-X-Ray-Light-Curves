#!/usr/bin/env python3
# scripts/plot_peaks.py
import argparse
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from scipy.signal import medfilt, savgol_filter

# ---------- Preprocess ----------
def rolling_quantile_baseline(y, win=301, q=0.2):
    win = int(win) | 1
    pad = win // 2
    ypad = np.pad(y, (pad, pad), mode="edge")
    # sliding quantile (O(N*win), fine for plots)
    base = np.array([np.quantile(ypad[i:i+win], q) for i in range(len(y))])
    return base

def detrend(time, flux, method="quantile", win=301, poly=3):
    if method == "savgol":
        base = savgol_filter(flux, int(win)|1, poly)
    else:  # "quantile" default
        base = rolling_quantile_baseline(flux, win=win, q=0.2)
    return flux - base, base

def zscore(y, eps=1e-9):
    m = np.mean(y)
    s = np.std(y) + eps
    return (y - m) / s, m, s

# ---------- Detection (hysteresis) ----------
def hysteresis_intervals(yz, hi=3.0, lo=1.5, min_len=10, merge_gap=5):
    """
    yz: z-scored series
    hi/lo: hysteresis thresholds (in sigma)
    min_len: minimum contiguous samples for a burst
    merge_gap: max gap (samples) to merge adjacent detections
    """
    above_hi = yz > hi
    above_lo = yz > lo
    n = len(yz)
    raw = []
    i = 0
    while i < n:
        if above_hi[i]:
            s = i
            i += 1
            while i < n and above_lo[i]:
                i += 1
            e = i - 1
            if e - s + 1 >= min_len:
                raw.append([s, e])
        else:
            i += 1
    # merge nearby intervals
    if not raw:
        return []
    out = [raw[0]]
    for s, e in raw[1:]:
        if s - out[-1][1] <= merge_gap:
            out[-1][1] = max(out[-1][1], e)
        else:
            out.append([s, e])
    return [(a, b) for a, b in out]

# ---------- Peak inside an interval ----------
def peak_index(y, a, b):
    local = y[a:b+1]
    return a + int(np.argmax(local))

# ---------- Main ----------
def main(in_csv, out_png, hi, lo, min_len, gap, detrend_method, win, poly, med_k):
    df = pd.read_csv(in_csv)
    # expect two columns: time, flux (any header names are fine)
    time = df.iloc[:, 0].to_numpy(dtype=float)
    flux = df.iloc[:, 1].to_numpy(dtype=float)

    # ensure increasing time
    order = np.argsort(time)
    time = time[order]
    flux = flux[order]

    # detrend + denoise (statistical only)
    y_detr, base = detrend(time, flux, method=detrend_method, win=win, poly=poly)
    y_deno = medfilt(y_detr, int(med_k) | 1)
    yz, _, _ = zscore(y_deno)

    # detect intervals
    ivals = hysteresis_intervals(yz, hi=hi, lo=lo, min_len=int(min_len), merge_gap=int(gap))

    # figure
    fig, ax = plt.subplots(figsize=(12, 5), dpi=130)
    ax.plot(time, flux, lw=1.2, label="Flux")
    ax.plot(time, base, lw=1.0, alpha=0.7, label="Baseline (est.)")

    # color intervals + mark peaks
    for (a, b) in ivals:
        # shaded region
        ax.axvspan(time[a], time[b], alpha=0.18, label=None)
        # peak marker
        pk = peak_index(flux, a, b)
        ax.plot(time[pk], flux[pk], "o", ms=5)

    # legend tweaks
    ax.set_xlabel("Time")
    ax.set_ylabel("Flux")
    title = f"Detected bursts (hi={hi}σ, lo={lo}σ, min_len={min_len}, gap={gap})"
    ax.set_title(title)
    if len(ivals) > 0:
        ax.legend(loc="best")
    else:
        ax.legend(loc="best")
        ax.text(0.01, 0.98, "No intervals detected", transform=ax.transAxes,
                va="top", ha="left", fontsize=10)

    ax.grid(True, alpha=0.25)
    fig.tight_layout()
    if out_png:
        fig.savefig(out_png, bbox_inches="tight")
        print(f"Saved plot → {out_png}")
    else:
        plt.show()

if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--in", dest="in_csv", required=True, help="CSV with columns: time, flux")
    ap.add_argument("--out", dest="out_png", default="", help="Output PNG path (or blank to show)")
    ap.add_argument("--hi", type=float, default=2.8, help="High threshold (sigma)")
    ap.add_argument("--lo", type=float, default=1.4, help="Low threshold (sigma)")
    ap.add_argument("--min-len", type=float, default=10, help="Min length (samples) for a burst")
    ap.add_argument("--gap", type=float, default=5, help="Merge gap (samples)")
    ap.add_argument("--detrend", dest="detrend_method", choices=["quantile", "savgol"],
                    default="quantile")
    ap.add_argument("--win", type=int, default=301, help="Window for detrend (odd)")
    ap.add_argument("--poly", type=int, default=3, help="Poly order for SavGol")
    ap.add_argument("--med-k", type=int, default=5, help="Median filter kernel (odd)")
    args = ap.parse_args()
    main(args.in_csv, args.out_png, args.hi, args.lo, args.min_len, args.gap,
         args.detrend_method, args.win, args.poly, args.med_k)
