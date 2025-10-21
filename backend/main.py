import argparse, numpy as np, pandas as pd
from preprocess.resample import uniform
from preprocess.denoise import median, zscore
from preprocess.detrend import remove_trend
from peaks import adaptive_threshold
from postprocess import merge_intervals
from flare_fit import fit_segment

def main(in_csv, out_csv, dt=None, hi=3.0, lo=1.5, min_len=10, gap=5):
    df = pd.read_csv(in_csv)  # cols: time, flux
    t, y = df.iloc[:,0].values.astype(float), df.iloc[:,1].values.astype(float)

    t, y, dt = uniform(t, y, dt)
    y_d, base = remove_trend(t, y, method="quantile", win=max(301,int(60/dt)|1))
    y_dn = median(y_d, k=max(5, int(3/dt)|1))
    yz, *_ = zscore(y_dn)

    iv = adaptive_threshold(yz, hi=hi, lo=lo, min_len=int(min_len/dt))
    iv = merge_intervals(iv, gap=int(gap/dt))

    rows = []
    for a,b in iv:
        res = fit_segment(t[a:b+1], y[a:b+1])
        rows.append({
            "t_start": t[a], "t_end": t[b],
            "F0": res.F0, "A": res.A, "t0": res.t0,
            "tau_r": res.tau_r, "tau_d": res.tau_d,
            "F_peak": res.Fp, "t_peak": res.tp, "duration": res.duration
        })
    pd.DataFrame(rows).to_csv(out_csv, index=False)

if __name__ == "__main__":
    p = argparse.ArgumentParser()
    p.add_argument("--in", dest="in_csv", required=True)
    p.add_argument("--out", dest="out_csv", required=True)
    p.add_argument("--dt", type=float, default=None)
    p.add_argument("--hi", type=float, default=3.0)
    p.add_argument("--lo", type=float, default=1.5)
    p.add_argument("--min-len", type=float, default=10.0)
    p.add_argument("--gap", type=float, default=5.0)
    a = p.parse_args()
    main(a.in_csv, a.out_csv, a.dt, a.hi, a.lo, a.min_len, a.gap)
