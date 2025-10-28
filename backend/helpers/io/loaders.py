import os
import pandas as pd
from astropy.table import Table

def load_single_day_lc(path):
    if not os.path.exists(path):
        raise FileNotFoundError(path)
    lc = Table.read(path)
    df = pd.DataFrame({
        "TIME": lc["TIME"].value.astype(float),
        "RATE": lc["RATE"].value.astype(float),
    })
    return df
