import pandas as pd
import matplotlib.pyplot as plt
from astropy.io import fits
from astropy.table import Table
from pathlib import Path
import warnings
import numpy as np
import os
import sys

warnings.filterwarnings('ignore', category=fits.verify.VerifyWarning)
OUTPUT_GRAPH_DIR = Path('output_graphs')

def convert_raw_fits_to_lc(raw_fits_file_path):
    
    try:
        with fits.open(raw_fits_file_path) as hdul:
            data = hdul[1].data
            column_names = data.columns.names
            
            time_col_name = 'Time' if 'Time' in column_names else ('TIME' if 'TIME' in column_names else None)
            data_array_col_name = 'DataArray'
            
            if time_col_name is None:
                raise KeyError("Time column ('Time' or 'TIME') not found.")
            if data_array_col_name not in column_names:
                raise ValueError("'DataArray' column not found.")
            
            light_curve_1d = np.sum(data[data_array_col_name], axis=1)
            time_data = data[time_col_name]

        lc_table = Table({
            'Time': time_data, 
            'RATE': light_curve_1d.astype(np.float32), 
            'ERROR': np.zeros(len(time_data), dtype=np.float32), 
            'FRACEXP': np.ones(len(time_data), dtype=np.float32)
        })
        print(f"[CONVERSION] Raw FITS converted to in-memory LC table (N={len(lc_table)}).")
        return lc_table

    except Exception as e:
        print(f"[ERROR] Failed to convert raw FITS to LC structure: {e}")
        return None

def _plot_and_display(df, time_col, rate_col, file_name, data_type):
    try:
        plt.figure(figsize=(12, 6))
        plt.plot(df[time_col], df[rate_col], linewidth=0.5)
        
        plt.title(f'Light Curve ({data_type}): {file_name}')
        plt.xlabel(f'{time_col} (Seconds)')
        plt.ylabel(f'{rate_col} (Counts/s)')
        plt.grid(True)
        
        plt.show()
        plt.close()
        print("Graph displayed successfully.")

    except Exception as e:
        print(f"\n[ERROR] An error occurred during plotting/display: {e}")


def process_fits_lightcurve(file_path):
    try:
        with fits.open(file_path) as hdul:
            data = hdul[1].data
            
            df = Table(data).to_pandas()

            time_col = 'TIME' if 'TIME' in df.columns else ('Time' if 'Time' in df.columns else None)
            rate_col = 'RATE' if 'RATE' in df.columns else None
            
            if time_col is None or rate_col is None:
                raise KeyError("Required columns ('Time'/'TIME' and 'RATE') not found.")

            _plot_and_display(df, time_col, rate_col, file_path.name, "FITS/LC")
            return df 

    except Exception as e:
        print(f"\n[ERROR] Failed to read FITS/LC file: {e}")
        return None


def plot_ascii_lightcurve(file_path, time_column='TIME', rate_column='RATE', separator=','):
    try:
        df = pd.read_csv(file_path, sep=separator) 
        
        time_col = time_column
        rate_col = rate_column

        if time_col not in df.columns or rate_col not in df.columns:
             raise KeyError("Required columns not found in ASCII file.")
             
        _plot_and_display(df, time_col, rate_col, file_path.name, "ASCII/CSV")
        return df 
        
    except Exception as e:
        print(f"\n[ERROR] Failed to read ASCII/CSV file: {e}")
        return None


def plot_excel_lightcurve(file_path, time_column='TIME', rate_column='RATE', sheet_name=0):
    try:
        df = pd.read_excel(file_path, sheet_name=sheet_name)
        
        time_col = time_column
        rate_col = rate_column

        if time_col not in df.columns or rate_col not in df.columns:
            raise KeyError("Required columns not found in EXCEL file.")
            
        _plot_and_display(df, time_col, rate_col, file_path.name, "EXCEL")
        return df 

    except Exception as e:
        print(f"\n[ERROR] Failed to read EXCEL file: {e}")
        return None
    

# main function 
def main_lightcurve_parser():
    
    file_path_str = input("Enter the full path to the light curve file (.lc, .fits, .csv, .xlsx, etc.): ")
    file_path = Path(file_path_str.strip().strip("'\"")) # Clean up path string
    
    if not file_path.exists():
        print(f"\n[FAILURE] File not found at: {file_path_str}")
        return

    extension = file_path.suffix.lower()
    processed_df = None
    
    print(f"\n[DISPATCHER] Analyzing file type: {extension}")
    print("-" * 50)
    
    if extension in ['.fits', '.fit', '.fts']:
        lc_table = convert_raw_fits_to_lc(file_path)
        if lc_table is not None:
            processed_df = lc_table.to_pandas()
            _plot_and_display(processed_df, 'Time', 'RATE', file_path.name, "CONVERTED_LC")
        
    elif extension in ['.lc']:
        processed_df = process_fits_lightcurve(file_path)
        
    elif extension in ['.csv', '.txt', '.dat', '.ascii']:
        processed_df = plot_ascii_lightcurve(file_path)
        
    elif extension in ['.xls', '.xlsx']:
        processed_df = plot_excel_lightcurve(file_path)
        
    else:
        print(f"[WARNING] Unsupported file extension: {extension}. Cannot plot.")
    
    # After plotting and summary
    if processed_df is not None:
        # create output directory
        output_dir = Path("output_csv")
        output_dir.mkdir(exist_ok=True)

        # standardize filename: same base name, .csv extension
        csv_path = output_dir / (file_path.stem + "_processed.csv")
        processed_df.to_csv(csv_path, index=False)

        print(f"\n[SAVED] Processed data written to: {csv_path}")

    if processed_df is not None:
        print("\n[SUMMARY] Processed DataFrame (First 5 rows):")
        print(processed_df.head())
        print(f"Total records: {len(processed_df)}")
    
    print("-" * 50)


if __name__ == "__main__":
    main_lightcurve_parser()
