from scipy.signal import find_peaks

def initial_peaks(signal, prominence):
    idx, _ = find_peaks(signal, prominence=prominence)
    return idx
