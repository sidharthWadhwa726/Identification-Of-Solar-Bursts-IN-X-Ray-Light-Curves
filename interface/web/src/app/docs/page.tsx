import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { InlineMath, BlockMath } from 'react-katex';
import 'katex/dist/katex.min.css';

export default function DocsPage() {
  return (
    <div className="space-y-8">
      <div className="text-center">
        <h1 className="text-3xl font-bold">Documentation</h1>
        <p className="text-muted-foreground mt-2">
          User guide and technical documentation for the Solar Burst Identification system.
        </p>
      </div>

      <div className="grid gap-6">
        <Card>
          <CardHeader>
            <CardTitle>User Guide</CardTitle>
            <CardDescription>
              Learn how to use the web application for solar burst analysis.
            </CardDescription>
          </CardHeader>
          <CardContent className="space-y-4">
            <div>
              <h3 className="font-semibold">Input Data Specifications</h3>
              <p className="text-sm text-muted-foreground">
                The system accepts various file formats containing time series data: FITS (.fits, .fit, .fts), Light Curve (.lc), CSV (.csv), TXT (.txt), DAT (.dat), ASCII (.ascii), and Excel (.xls, .xlsx) files. Data should contain columns for time and flux/counts (e.g., TIME and RATE for FITS files).
              </p>
            </div>
            <div>
              <h3 className="font-semibold">Parameter Configuration</h3>
              <p className="text-sm text-muted-foreground">
                Analysis parameters are currently fixed in the backend: high threshold of 3.0σ and low threshold of 1.5σ for hysteresis-based burst detection, minimum burst length of 10 seconds, and gap merging of 5 seconds. Future versions may allow user configuration.
              </p>
            </div>
            <div>
              <h3 className="font-semibold">Interpreting Results</h3>
              <p className="text-sm text-muted-foreground">
                Results include detected burst parameters: start/end times, baseline flux (F0), amplitude (A), peak time (t0), rise/decay time constants (τ_r, τ_d), peak flux (F_peak), peak time (t_peak), and duration (time above 10% of peak flux).
              </p>
            </div>
          </CardContent>
        </Card>

        <Card>
          <CardHeader>
            <CardTitle>Scientific Basis</CardTitle>
            <CardDescription>
              Understanding the algorithms and physical models used.
            </CardDescription>
          </CardHeader>
          <CardContent className="space-y-4">
            <div>
              <h3 className="font-semibold">Data Preprocessing</h3>
              <p className="text-sm text-muted-foreground">
                Input data undergoes uniform resampling, detrending using quantile-based baseline removal, median filtering for denoising, and z-score normalization to standardize the signal.
              </p>
            </div>
            <div>
              <h3 className="font-semibold">Burst Detection Algorithm</h3>
              <p className="text-sm text-muted-foreground">
                Uses adaptive thresholding with hysteresis on z-scored data: starts when signal exceeds 3.0σ (high threshold) and ends when it drops below 1.5σ (low threshold), with minimum burst length of 10 seconds and gap merging of 5 seconds.
              </p>
            </div>
            <div>
              <h3 className="font-semibold">Model Fitting</h3>
              <p className="text-sm text-muted-foreground">
                Applies exponential rise/decay models for solar flare profiles: <InlineMath math="F(t) = F_0 + A \cdot (1 - \exp(-(t-t_0)/\tau_r)) \cdot \exp(-(t-t_0)/\tau_d)" />, where <InlineMath math="F_0" /> is baseline flux, <InlineMath math="A" /> is amplitude, <InlineMath math="t_0" /> is peak start time, <InlineMath math="\tau_r" /> is rise time constant, and <InlineMath math="\tau_d" /> is decay time constant.
              </p>
            </div>
            <div>
              <h3 className="font-semibold">Parameter Estimation</h3>
              <ul className="text-sm text-muted-foreground list-disc list-inside space-y-1">
                <li><strong>Baseline Flux (F0):</strong> Estimated as 10th percentile of the segment.</li>
                <li><strong>Amplitude (A):</strong> Difference between max flux and F0.</li>
                <li><strong>Peak Flux (F_peak):</strong> Maximum fitted flux value.</li>
                <li><strong>Duration:</strong> Time above 10% of peak flux from baseline.</li>
                <li><strong>Temporal Parameters:</strong> Rise (τ_r) and decay (τ_d) time constants.</li>
              </ul>
            </div>
          </CardContent>
        </Card>

        <Card>
          <CardHeader>
            <CardTitle>Developer Reference</CardTitle>
            <CardDescription>
              Technical details for developers and advanced users.
            </CardDescription>
          </CardHeader>
          <CardContent className="space-y-4">
            <div>
              <h3 className="font-semibold">Project Structure</h3>
              <ul className="text-sm text-muted-foreground list-disc list-inside space-y-1">
                <li><code>backend/</code>: Python analysis engine</li>
                <li><code>interface/web/</code>: Next.js web application</li>
                <li><code>dataset/</code>: Sample data and test files</li>
              </ul>
            </div>
            <div>
              <h3 className="font-semibold">API Endpoints</h3>
              <ul className="text-sm text-muted-foreground list-disc list-inside space-y-1">
                <li><code>POST /analyze</code>: Run burst detection and fitting on uploaded file, returns CSV data and Plotly plot</li>
              </ul>
            </div>
            <div>
              <h3 className="font-semibold">Environment Setup</h3>
              <p className="text-sm text-muted-foreground">
                Requires Node.js for the web app and Python for the backend. Install dependencies using pnpm and pip respectively.
              </p>
            </div>
          </CardContent>
        </Card>

        <Card>
          <CardHeader>
            <CardTitle>Usage Examples</CardTitle>
            <CardDescription>
              Step-by-step examples of analysis workflows.
            </CardDescription>
          </CardHeader>
          <CardContent className="space-y-4">
            <div>
              <h3 className="font-semibold">Basic Analysis</h3>
              <ol className="text-sm text-muted-foreground list-decimal list-inside space-y-1">
                <li>Upload a supported file format (FITS, LC, CSV, TXT, DAT, ASCII, XLS, XLSX) with time and flux/counts columns</li>
                <li>Click "Run Analysis" to process the data with default parameters (hi=3.0σ, lo=1.5σ, min_len=10s, gap=5s)</li>
                <li>View the interactive light curve plot with detected burst regions highlighted</li>
                <li>Review detected bursts in the results table showing fitted parameters (<InlineMath math="F_0" />, <InlineMath math="A" />, <InlineMath math="t_0" />, <InlineMath math="\tau_r" />, <InlineMath math="\tau_d" />, <InlineMath math="F_{\text{peak}}" />, <InlineMath math="t_{\text{peak}}" />, duration)</li>
                <li>Download the analysis results as a CSV file</li>
              </ol>
            </div>
            <div>
              <h3 className="font-semibold">Batch Processing</h3>
              <p className="text-sm text-muted-foreground">
                For processing multiple files or custom parameters, use the standalone Python backend with command-line interface. Run <code>python main.py --in input.csv --out output.csv</code> with optional parameters like <code>--hi</code> (high threshold), <code>--lo</code> (low threshold), <code>--min-len</code> (minimum burst length), and <code>--gap</code> (gap merging threshold).
              </p>
            </div>
          </CardContent>
        </Card>
      </div>
    </div>
  );
}
