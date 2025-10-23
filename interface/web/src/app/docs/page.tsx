import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";

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
                The system accepts various file formats containing time series data: FITS (.fits, .fit, .fts), Light Curve (.lc), CSV (.csv), TXT (.txt), DAT (.dat), ASCII (.ascii), and Excel (.xls, .xlsx) files. Data should contain columns for time and flux/counts.
              </p>
            </div>
            <div>
              <h3 className="font-semibold">Parameter Configuration</h3>
              <p className="text-sm text-muted-foreground">
                Analysis parameters are currently fixed in the backend: detection threshold of 3.0σ above background, minimum burst length of 10 seconds, and gap merging of 5 seconds. Future versions may allow user configuration.
              </p>
            </div>
            <div>
              <h3 className="font-semibold">Interpreting Results</h3>
              <p className="text-sm text-muted-foreground">
                Results include detected burst parameters: start/end times, peak flux, and total fluence (energy output).
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
              <h3 className="font-semibold">Burst Detection Algorithm</h3>
              <p className="text-sm text-muted-foreground">
                Uses statistical thresholding to identify significant deviations from background noise in X-ray light curves.
              </p>
            </div>
            <div>
              <h3 className="font-semibold">Model Fitting</h3>
              <p className="text-sm text-muted-foreground">
                Applies exponential rise/decay models: F(t) = F0 + A * (1 - exp(-(t-t0)/τ_r)) * exp(-(t-t0)/τ_d) for burst profiles, where F0 is baseline flux, A is amplitude, t0 is start time, τ_r is rise time constant, and τ_d is decay time constant.
              </p>
            </div>
            <div>
              <h3 className="font-semibold">Parameter Estimation</h3>
              <ul className="text-sm text-muted-foreground list-disc list-inside space-y-1">
                <li><strong>Fluence:</strong> Total energy output, calculated as integral of flux over burst duration.</li>
                <li><strong>Peak Flux:</strong> Maximum flux value during the burst.</li>
                <li><strong>Temporal Parameters:</strong> Rise and decay time constants.</li>
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
                <li>Upload a supported file format (FITS, CSV, TXT, etc.) with time and flux/counts columns</li>
                <li>Click "Run Analysis" to process the data with default parameters</li>
                <li>View the interactive light curve plot with detected burst regions highlighted</li>
                <li>Review detected bursts in the results table showing timing and flux parameters</li>
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
