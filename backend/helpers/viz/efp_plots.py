# backend/helpers/viz/efp_plots.py
from __future__ import annotations
import os
import numpy as np
import matplotlib.pyplot as plt
from dataclasses import dataclass
from typing import Optional, Tuple
from scipy.optimize import curve_fit
from ..models.efp import elementary_flare_profile

@dataclass
class EfpFitResult:
    p_opt: np.ndarray            # [A, mu, sigma, tau]
    t_fit: np.ndarray            # dense time for fitted curve
    y_fit: np.ndarray            # fitted curve values
    start_idx: int
    end_idx: int
    peak_idx: int
    success: bool
    message: str = "ok"

def _window_from_peak(signal: np.ndarray, peak_idx: int) -> Tuple[int,int]:
    """Expand left/right until the BG-subtracted signal crosses <= 0 or edges."""
    n = len(signal)
    i0 = peak_idx
    i1 = peak_idx
    # left
    for i in range(peak_idx-1, -1, -1):
        if signal[i] <= 0 or i == 0:
            i0 = i
            break
    # right
    for i in range(peak_idx+1, n):
        if signal[i] <= 0 or i == n-1:
            i1 = i
            break
    if i1 <= i0:
        # fallback minimal window
        i0 = max(0, peak_idx-2)
        i1 = min(n-1, peak_idx+2)
    return i0, i1

def fit_efp_on_window(time_array: np.ndarray,
                      signal_sub: np.ndarray,
                      start_idx: int,
                      end_idx: int) -> EfpFitResult:
    """Fit EFP on a BG-subtracted segment [start_idx:end_idx] with robust bounds."""
    t_seg = time_array[start_idx:end_idx+1]
    y_seg = signal_sub[start_idx:end_idx+1]
    if len(t_seg) < 5 or np.max(y_seg) <= 0:
        return EfpFitResult(np.array([]), np.array([]), np.array([]),
                            start_idx, end_idx, int(np.argmax(y_seg))+start_idx,
                            False, "too few points or nonpositive segment")

    A0   = float(np.max(y_seg))
    mu0  = float(t_seg[np.argmax(y_seg)])
    p0   = [A0, mu0, 50.0, 200.0]
    lb   = [0.0, float(t_seg.min()), 1.0, 5.0]
    ub   = [A0*2.5, float(t_seg.max()), 1000.0, 2000.0]

    try:
        p_opt, _ = curve_fit(elementary_flare_profile, t_seg, y_seg,
                             p0=p0, bounds=(lb, ub), maxfev=5000)
        t_fit = np.linspace(t_seg.min(), t_seg.max(), 300)
        y_fit = elementary_flare_profile(t_fit, *p_opt)
        return EfpFitResult(p_opt, t_fit, y_fit, start_idx, end_idx,
                            int(np.argmax(y_seg))+start_idx, True, "ok")
    except Exception as e:
        return EfpFitResult(np.array([]), np.array([]), np.array([]),
                            start_idx, end_idx, int(np.argmax(y_seg))+start_idx,
                            False, f"curve_fit failed: {e}")

def plot_efp_on_selected_peaks(time_array: np.ndarray,
                               signal_sub: np.ndarray,
                               peak_indices: list[int],
                               background_array: Optional[np.ndarray] = None,
                               save_dir: Optional[str] = None,
                               show: bool = True,
                               title_prefix: str = "EFP Fit around Peak") -> list[EfpFitResult]:
    """
    Fit + plot EFP per provided peak index. Returns fit results for further analysis.
    - signal_sub: BG-subtracted signal (what you fit/plot in blue)
    - background_array: optional BG trace to overlay (green)
    """
    if save_dir:
        os.makedirs(save_dir, exist_ok=True)

    results: list[EfpFitResult] = []
    for pk in peak_indices:
        i0, i1 = _window_from_peak(signal_sub, pk)
        res = fit_efp_on_window(time_array, signal_sub, i0, i1)
        results.append(res)

        # plotting (even if failed, we still show the window for debugging)
        t_flare = time_array[i0:i1+1]
        y_flare = signal_sub[i0:i1+1]

        fig, ax = plt.subplots(figsize=(8, 4))
        ax.plot(t_flare, y_flare, "--", alpha=0.7, label="Data (BG-sub)")

        if background_array is not None:
            ax.plot(t_flare, background_array[i0:i1+1], ":", color="green", label="Background")

        if res.success:
            ax.plot(res.t_fit, res.y_fit, "-", color="red", lw=2.2, label="EFP Fit")
            peak_time_guess = float(time_array[res.peak_idx])
            ttl = f"{title_prefix} @ {peak_time_guess:.2f} s"
        else:
            ttl = f"{title_prefix} (fit failed: {res.message})"

        ax.set_title(ttl)
        ax.set_xlabel("Time (s)")
        ax.set_ylabel(r"Flux (nW/m$^2$)")
        ax.set_yscale("log")
        ax.grid(True, ls="--", alpha=0.5)
        ax.legend()

        fig.tight_layout()
        if save_dir:
            fname = f"efp_peak_{pk}_t{t_flare[0]:.0f}-{t_flare[-1]:.0f}.png"
            fig.savefig(os.path.join(save_dir, fname), dpi=140)
        if show:
            plt.show()
        else:
            plt.close(fig)

    return results
