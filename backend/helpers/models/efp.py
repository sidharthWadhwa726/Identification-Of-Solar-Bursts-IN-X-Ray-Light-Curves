import numpy as np
from scipy.special import erfc

MAX_EXP_ARG_CLIP = 50.0

def elementary_flare_profile(t, A, mu, sigma, tau):
    """Stable 4-param EFP profile."""
    t = np.asarray(t, float)
    sigma = abs(float(sigma)); tau = abs(float(tau))
    sigma = max(sigma, 1e-4);  tau = max(tau, 1e-4)

    if tau < 1e-3:
        A_ = A * sigma * np.sqrt(np.pi/2.0)
        arg = -0.5 * ((t - mu)/sigma)**2
        arg = np.clip(arg, -np.inf, MAX_EXP_ARG_CLIP)
        return A_ * np.exp(arg)

    A_ = A * (sigma/tau) * np.sqrt(np.pi/2.0)
    exp_arg = 0.5*(sigma/tau)**2 - (t - mu)/tau
    exp_arg = np.clip(exp_arg, -np.inf, MAX_EXP_ARG_CLIP)
    erfc_arg = (1.0/np.sqrt(2.0)) * (sigma/tau - (t - mu)/sigma)
    y = A_ * np.exp(exp_arg) * erfc(erfc_arg)
    return np.nan_to_num(y)
