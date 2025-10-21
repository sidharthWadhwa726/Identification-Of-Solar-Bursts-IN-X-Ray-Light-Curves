# core/fit/flare_model.py
import numpy as np
from dataclasses import dataclass
from scipy.optimize import curve_fit


def flare_fun(t, F0, A, t0, tau_r, tau_d):
    z = np.maximum(0.0, t - t0)
    return F0 + A*(1 - np.exp(-z/(tau_r+1e-9))) * np.exp(-z/(tau_d+1e-9))


@dataclass
class FitResult:
    F0: float; A: float; t0: float; tau_r: float; tau_d: float
    Fp: float; tp: float; duration: float; cov: np.ndarray

def fit_segment(t, y):
    F0 = float(np.percentile(y, 10))
    A  = max(1e-6, float(y.max() - F0))
    t0 = float(t[np.argmax(np.gradient(y))]) if len(t) > 3 else float(t[0])
    span = max(1e-3, t[-1] - t[0])
    p0 = [F0, A, t0, 0.1*span, 0.3*span]
    bounds = ([-np.inf, 0, t[0]-span, 1e-3, 1e-3],
              [ np.inf, np.inf, t[-1],  10*span, 10*span])
    popt, pcov = curve_fit(flare_fun, t, y, p0=p0, bounds=bounds, maxfev=20000)
    F0,A,t0,tau_r,tau_d = map(float, popt)
    ts = np.linspace(t0, t[-1], 2048)
    ys = flare_fun(ts, *popt)
    k  = int(np.argmax(ys)); Fp, tp = float(ys[k]), float(ts[k])
    thr = F0 + 0.1*(Fp - F0)
    mask = ys >= thr
    dur = float(ts[mask][-1] - ts[mask][0]) if mask.any() else 0.0
    return FitResult(F0,A,t0,tau_r,tau_d,Fp,tp,dur,pcov)
