import numpy as np

def uniform(time, flux, dt=None):
    if dt is None:
        dt = np.median(np.diff(time))
    grid = np.arange(time[0], time[-1] + 0.5*dt, dt)
    y = np.interp(grid, time, flux)
    return grid, y, dt
