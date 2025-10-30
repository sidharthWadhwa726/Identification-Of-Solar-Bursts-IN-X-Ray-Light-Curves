import pandas as pd
import numpy as np
import joblib
import os

SOLAR_CLASS_MAP = {
    0: 'A/B',
    1: 'C',
    2: 'M',
    3: 'X'
}

def compute_features(df: pd.DataFrame):
    """Compute duration-related features needed for classification."""
    df = df.copy()
    df["starting"] = df["PeakTime"] - df["StartFWTM"]
    df["ending"] = df["EndFWTM"] - df["PeakTime"]
    df["duration"] = df["EndFWTM"] - df["StartFWTM"]
    return df


def classify_catalog(df: pd.DataFrame, artifacts_dir="cl_artifacts") -> pd.DataFrame:
    """Attach Solar_Class to flare catalog using pretrained clustering artifacts."""
    scaler_path = os.path.join(artifacts_dir, "scaler.pkl")
    model_path = os.path.join(artifacts_dir, "kmeans_model.pkl")

    if not os.path.exists(scaler_path) or not os.path.exists(model_path):
        print(f"[CL] Missing artifacts in {artifacts_dir}, skipping classification.")
        df["Solar_Class"] = np.nan
        return df

    try:
        scaler = joblib.load(scaler_path)
        kmeans = joblib.load(model_path)
    except Exception as e:
        print(f"[CL] Failed loading artifacts: {e}")
        df["Solar_Class"] = np.nan
        return df

    df = df.rename(columns={"PeakFlux_nW/m2": "PeakFlux"})
    df = compute_features(df)

    features = ["PeakFlux", "FittedSNR", "DecayTau", "RiseSigma", "R_squared", "duration", "starting"]
    if not all(f in df.columns for f in features):
        missing = [f for f in features if f not in df.columns]
        print(f"[CL] Missing required features: {missing}")
        df["Solar_Class"] = np.nan
        return df

    X = df[features]
    X_scaled = scaler.transform(X)
    df["Cluster"] = kmeans.predict(X_scaled)
    df["Solar_Class"] = df["Cluster"].map(SOLAR_CLASS_MAP)
    print(f"[CL] Classification complete — {df['Solar_Class'].notna().sum()} classified.")
    return df