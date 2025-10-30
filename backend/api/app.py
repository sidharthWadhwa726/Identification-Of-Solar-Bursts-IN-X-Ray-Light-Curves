from flask import Flask, request, jsonify
from flask_cors import CORS
import tempfile
import os
import pandas as pd

from pathlib import Path
import sys
sys.path.insert(0, str(Path(__file__).parent.parent.parent))
from backend.helpers.pipeline import full_analysis_no_stitching
from backend.helpers.config import Config
from backend.helpers.post.filters import filter_flare_catalog

app = Flask(__name__)

CORS(app)  # Enable CORS for frontend

@app.route('/analyze', methods=['POST'])
def analyze():
    if 'file' not in request.files:
        return jsonify({'error': 'No file provided'}), 400

    file = request.files['file']
    if file.filename == '':
        return jsonify({'error': 'No file selected'}), 400

    # Save uploaded file to temp
    with tempfile.NamedTemporaryFile(delete=False, suffix=os.path.splitext(file.filename)[1]) as temp_file:
        file.save(temp_file.name)
        temp_path = temp_file.name

    try:
        # Use default config
        cfg = Config()

        # Run pipeline
        t, y, cat, bg = full_analysis_no_stitching(temp_path, cfg, do_plot=False)

        # Post-filter
        df_fitted = cat.copy() if isinstance(cat, pd.DataFrame) else pd.DataFrame()
        filtered, _ = filter_flare_catalog(
            df_fitted,
            thresholds={
                "snr_min": 8.0,
                "r2_min": 0.5,
                "decay_tau_max": 1.0e7
            },
            adaptive=True,
            min_keep=5
        )

        # Create plot_df CSV: time, flux, background
        plot_df = pd.DataFrame({
            'time': t,
            'flux': y,
            'background': bg
        })
        plot_csv = plot_df.to_csv(index=False)

        # Create bursts_csv: filtered catalog
        bursts_csv = filtered.to_csv(index=False) if not filtered.empty else ""

        return jsonify({
            'plot_df': plot_csv,
            'bursts_csv': bursts_csv
        })

    except Exception as e:
        return jsonify({'error': str(e)}), 500

    finally:
        # Clean up temp file
        if os.path.exists(temp_path):
            os.unlink(temp_path)

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)
