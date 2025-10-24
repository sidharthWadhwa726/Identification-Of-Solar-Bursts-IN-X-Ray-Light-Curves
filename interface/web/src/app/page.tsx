import Link from "next/link";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";

export default function Home() {
  return (
    <div className="space-y-12">
      {/* Hero Section */}
      <section className="text-center space-y-6">
        <h1 className="text-4xl font-bold tracking-tight sm:text-5xl">
          Solar Burst Identification
        </h1>
        <p className="text-xl text-muted-foreground max-w-2xl mx-auto">
          Automated detection and classification of solar bursts in X-ray light curves using advanced algorithms.
        </p>
        <Button asChild size="lg">
          <Link href="/analyze">Start Analysis</Link>
        </Button>
      </section>

      {/* Overview Section */}
      <section className="space-y-6">
        <h2 className="text-2xl font-semibold text-center">Overview</h2>
        <div className="grid md:grid-cols-2 gap-6">
          <Card>
            <CardHeader>
              <CardTitle>Burst Detection Pipeline</CardTitle>
              <CardDescription>
                Our system processes X-ray light curves to identify solar bursts through threshold-based detection and model fitting.
              </CardDescription>
            </CardHeader>
            <CardContent>
              <p className="text-sm text-muted-foreground">
                The pipeline includes data preprocessing, burst detection using statistical thresholds, and parameter fitting using exponential rise/decay models.
              </p>
            </CardContent>
          </Card>
          <Card>
            <CardHeader>
              <CardTitle>Scientific Basis</CardTitle>
              <CardDescription>
                Based on established methods for solar flare analysis in X-ray observations.
              </CardDescription>
            </CardHeader>
            <CardContent>
              <p className="text-sm text-muted-foreground">
                Utilizes physical models for burst characteristics including fluence, peak flux, and temporal parameters.
              </p>
            </CardContent>
          </Card>
        </div>
      </section>

      {/* Supported Formats */}
      <section className="space-y-6">
        <h2 className="text-2xl font-semibold text-center">Supported Formats</h2>
        <div className="grid sm:grid-cols-2 md:grid-cols-4 gap-4">
          <Card className="text-center">
            <CardHeader>
              <CardTitle className="text-lg">FITS</CardTitle>
            </CardHeader>
            <CardContent>
              <p className="text-sm text-muted-foreground">
                Flexible Image Transport System files commonly used in astronomy (.fits, .fit, .fts).
              </p>
            </CardContent>
          </Card>
          <Card className="text-center">
            <CardHeader>
              <CardTitle className="text-lg">LC</CardTitle>
            </CardHeader>
            <CardContent>
              <p className="text-sm text-muted-foreground">
                Light curve files in FITS format (.lc).
              </p>
            </CardContent>
          </Card>
          <Card className="text-center">
            <CardHeader>
              <CardTitle className="text-lg">CSV</CardTitle>
            </CardHeader>
            <CardContent>
              <p className="text-sm text-muted-foreground">
                Comma-separated values for time series data (.csv).
              </p>
            </CardContent>
          </Card>
          <Card className="text-center">
            <CardHeader>
              <CardTitle className="text-lg">TXT</CardTitle>
            </CardHeader>
            <CardContent>
              <p className="text-sm text-muted-foreground">
                Plain text files with tabular data (.txt).
              </p>
            </CardContent>
          </Card>
          <Card className="text-center">
            <CardHeader>
              <CardTitle className="text-lg">DAT</CardTitle>
            </CardHeader>
            <CardContent>
              <p className="text-sm text-muted-foreground">
                Data files in ASCII format (.dat).
              </p>
            </CardContent>
          </Card>
          <Card className="text-center">
            <CardHeader>
              <CardTitle className="text-lg">ASCII</CardTitle>
            </CardHeader>
            <CardContent>
              <p className="text-sm text-muted-foreground">
                ASCII tabular data files (.ascii).
              </p>
            </CardContent>
          </Card>
          <Card className="text-center">
            <CardHeader>
              <CardTitle className="text-lg">XLS</CardTitle>
            </CardHeader>
            <CardContent>
              <p className="text-sm text-muted-foreground">
                Microsoft Excel files (.xls).
              </p>
            </CardContent>
          </Card>
          <Card className="text-center">
            <CardHeader>
              <CardTitle className="text-lg">XLSX</CardTitle>
            </CardHeader>
            <CardContent>
              <p className="text-sm text-muted-foreground">
                Modern Microsoft Excel files (.xlsx).
              </p>
            </CardContent>
          </Card>
        </div>
      </section>

      {/* Deployment Info */}
      <section className="space-y-6">
        <h2 className="text-2xl font-semibold text-center">Deployment</h2>
        <Card className="max-w-2xl mx-auto">
          <CardContent className="pt-6">
            <p className="text-center text-muted-foreground">
              Available as both a web application for interactive analysis and a standalone package for batch processing.
            </p>
          </CardContent>
        </Card>
      </section>

      {/* Links */}
      <section className="text-center space-y-4">
        <h2 className="text-2xl font-semibold">Resources</h2>
        <div className="flex justify-center space-x-4">
          <Button variant="outline" asChild>
            <Link href="/docs">Documentation</Link>
          </Button>
          <Button variant="outline" asChild>
            <a href="https://github.com/priyanshsingh-dev/Identification-Of-Solar-Bursts-IN-X-Ray-Light-Curves" target="_blank" rel="noopener noreferrer">
              GitHub Repository
            </a>
          </Button>
        </div>
      </section>
    </div>
  );
}
