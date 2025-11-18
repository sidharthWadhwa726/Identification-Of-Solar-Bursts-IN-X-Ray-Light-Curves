# Identification of Solar Bursts in X-Ray Light Curves

[![License: GPL v3](https://img.shields.io/badge/License-GPLv3-blue.svg)](https://www.gnu.org/licenses/gpl-3.0)

An automated tool for detecting and characterizing solar bursts (flares) in X-ray light curves using advanced algorithms. This project provides a complete pipeline for preprocessing, burst detection, model fitting, and post-processing, with both a web-based interface and command-line options for batch analysis.

## Features

- **Multi-Format Support**: Accepts FITS (.fits, .fit, .fts), Light Curve (.lc), CSV (.csv), TXT (.txt), DAT (.dat), ASCII (.ascii), XLS (.xls), and XLSX (.xlsx) files.
- **Automated Pipeline**: Includes data preprocessing (resampling, detrending, denoising, normalization), hysteresis-based burst detection (3.0σ high / 1.5σ low thresholds), exponential rise/decay model fitting, and filtering (SNR > 8, R² > 0.5, decay τ < 1e7s).
- **Machine Learning Integration**: Optional anomaly detection via autoencoder and burst classification using K-Means clustering.
- **Interactive Web Interface**: Built with Next.js, featuring file upload, real-time plotting with Plotly, results tables, and CSV downloads.
- **REST API**: Flask-based backend for programmatic access.
- **Scientific Accuracy**: Based on established solar physics methods, compatible with data from ISRO XSM, GOES, RHESSI, and SDO missions.

## Quick Start

1. **Clone the Repository**:
   ```bash
   git clone https://github.com/priyanshsingh-dev/Identification-Of-Solar-Bursts-IN-X-Ray-Light-Curves.git

   cd Identification-Of-Solar-Bursts-IN-X-Ray-Light-Curves
   ```

2. **Set Up Backend**:
   - Create a virtual environment: 
   ```
   python3 -m venv env && source env/bin/activate
   ``` 
   (Linux/Mac) or 
   ```
   python -m venv env && ./env\Scripts\activate
   ```
   (Windows).
   - Install dependencies: `pip install -r requirements.txt`.
   - Run the API server: `python backend/api/app.py` (runs on http://localhost:5000).

3. **Set Up Frontend**:
   - Navigate to the web directory: `cd interface/web`.
   - Install dependencies: `npm install`.
   - Set environment variable: Create `.env` with `NEXT_PUBLIC_BACKEND_URI=http://localhost:5000`.
   - Run the development server: `npm run dev` (runs on http://localhost:3000).

4. **Analyze Data**:
   - Open http://localhost:3000/analyze in your browser.
   - Upload a supported file (e.g., from `dataset/`).
   - View the interactive light curve plot and download burst catalog as CSV.

## Installation

### Prerequisites
- **Python 3.8-3.10** for backend.
- **Node.js 18+** for frontend.
- **Git** for cloning.

## Usage

### Web Application
- Start the backend server as above.
- In `interface/web`, run `npm run dev`.
- Visit http://localhost:3000 to explore the home page, upload files on /analyze, and view results with interactive plots.

### API Usage
Send a POST request to `/analyze` with a file:
```bash
curl -X POST -F "file=@your_file.lc" http://localhost:5000/analyze
```
Returns JSON with `plot_df` (CSV for time/flux/background) and `bursts_csv` (CSV for detected bursts).

### Command-Line Interface
For batch processing:
```bash
python backend/helpers/main.py --in input_file.lc --out output.csv [options]
```
Options include `--hi` (high threshold, default 3.0), `--lo` (low threshold, default 1.5), `--min-len` (min burst length in seconds, default 10), `--gap` (gap merge threshold in seconds, default 5).

## Supported Formats
- **FITS/LC**: Flexible Image Transport System and Light Curve files (.fits, .fit, .fts, .lc).
- **CSV/TXT/DAT/ASCII**: Tabular data with time and flux columns.
- **XLS/XLSX**: Microsoft Excel files.

Data should include time (e.g., TIME) and flux/counts (e.g., RATE) columns.

## Scientific Overview
- **Preprocessing**: Uniform resampling, quantile-based detrending, median filtering, z-score normalization.
- **Detection**: Hysteresis thresholding on normalized data with configurable thresholds and merging.
- **Fitting**: Exponential model: $ F(t) = F_0 + A \cdot (1 - \exp(-(t-t_0)/\tau_r)) \cdot \exp(-(t-t_0)/\tau_d) $, estimating parameters like baseline flux $F_0$, amplitude $A$, rise/decay constants $\tau_r$, $\tau_d$, peak flux, and duration.
- **Post-Processing**: Filters bursts by signal-to-noise ratio, fit quality, and temporal constraints; optional ML for anomaly detection and classification.

## Configuration
Parameters are currently fixed (e.g., thresholds, min lengths) via `backend/helpers/config.py`. Future versions may support user customization.

## Development
- **Backend**: Modify `backend/` modules.
- **Frontend**: Edit `interface/web/src/`.
- Contributions welcome: Fork, create a branch, submit PRs. Report issues on GitHub.

## License
This project is licensed under the GNU General Public License v3.0 (GPLv3). See [LICENSE](LICENSE) for details.
