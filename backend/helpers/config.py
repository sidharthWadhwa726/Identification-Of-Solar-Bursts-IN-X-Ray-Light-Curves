from dataclasses import dataclass

@dataclass
class DenoiseParams:
    bin_size_s: float = 120.0
    sigma_g: float = 2.0

@dataclass
class DetectParams:
    peak_prominence: float = 200.0     # initial peaks
    slope_threshold: float = 0.5
    merge_threshold_s: float = 600.0

@dataclass
class ClipParams:
    n_sigma_clip: float = 0.3

@dataclass
class FitParams:
    final_peak_prominence: float = 50.0
    final_peak_height: float = 1.0
    count_to_nw_m2: float = 1.0
    y_label_flux: str = r"Flux (nW/m$^2$)"

@dataclass
class Config:
    denoise: DenoiseParams = DenoiseParams()
    detect:  DetectParams  = DetectParams()
    clip:    ClipParams    = ClipParams()
    fit:     FitParams     = FitParams()
