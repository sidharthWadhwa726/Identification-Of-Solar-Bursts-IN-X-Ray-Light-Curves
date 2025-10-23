from flask import Flask, request, jsonify
from flask_cors import CORS
import tempfile
import os
import pandas as pd
from pathlib import Path
import sys
import plotly.graph_objects as go
from plotly.subplots import make_subplots

# Add the project root to sys.path to import backend modules
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from backend.main_input_parser import process_file_to_df
# Import main.py functions directly to avoid module issues
# from backend.main import main as run_main
import subprocess

app = Flask(__name__)
CORS(app)  # Enable CORS for all routes

@app.route('/analyze', methods=['POST'])
def analyze():
    if 'file' not in request.files:
        return jsonify({'error': 'No file part'}), 400

    file = request.files['file']
    if file.filename == '':
        return jsonify({'error': 'No selected file'}), 400

    # Save uploaded file to temp
    with tempfile.NamedTemporaryFile(delete=False, suffix=Path(file.filename).suffix) as temp_file:
        file.save(temp_file.name)
        temp_path = temp_file.name

    try:
        # Process file to DataFrame
        df = process_file_to_df(temp_path)
        if df is None:
            return jsonify({'error': 'Failed to process file'}), 400

        # Convert to CSV string
        input_csv = df.to_csv(index=False)

        # Save to temp CSV for main.py
        with tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.csv') as temp_csv:
            df.to_csv(temp_csv, index=False)
            temp_csv_path = temp_csv.name

        # Run main.py to get bursts CSV using subprocess
        with tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.csv') as temp_out:
            temp_out_path = temp_out.name

        # Run main.py to get bursts CSV using subprocess
        subprocess.run(['python', 'main.py', '--in', temp_csv_path, '--out', temp_out_path], check=True)

        # Read bursts CSV
        bursts_df = pd.read_csv(temp_out_path)
        bursts_csv = bursts_df.to_csv(index=False)

        # Generate Plotly plot
        fig = make_subplots(rows=1, cols=1)

        # Add light curve
        fig.add_trace(go.Scatter(x=df.iloc[:, 0], y=df.iloc[:, 1], mode='lines', name='Light Curve', line=dict(color='blue')))

        # Add burst regions
        for _, burst in bursts_df.iterrows():
            fig.add_vrect(
                x0=burst['t_start'], x1=burst['t_end'],
                fillcolor="red", opacity=0.7, layer="below", line_width=1,
                annotation_text=f"Burst {burst.name+1}", annotation_position="top left"
            )

        fig.update_layout(
            title='X-ray Light Curve Analysis',
            xaxis_title='Time (s)',
            yaxis_title='Flux (counts/s)',
            margin=dict(l=20, r=20, t=50, b=20),  # Reduced empty space around the plot
        )

        # Convert to dict for JSON serialization
        plot_data = fig.to_dict()

        return jsonify({
            'bursts_csv': bursts_csv,
            'plot_data': plot_data,
        })

    except Exception as e:
        return jsonify({'error': str(e)}), 500

    finally:
        # Clean up temp files
        if os.path.exists(temp_path):
            os.unlink(temp_path)
        if 'temp_csv_path' in locals() and os.path.exists(temp_csv_path):
            os.unlink(temp_csv_path)
        if 'temp_out_path' in locals() and os.path.exists(temp_out_path):
            os.unlink(temp_out_path)

if __name__ == '__main__':
    app.run(debug=True)
