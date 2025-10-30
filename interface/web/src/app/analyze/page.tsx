"use client";

import { useState, useRef } from "react";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import AnalysisForm from "@/components/AnalysisForm";
import AnalysisResults from "@/components/AnalysisResults";
import { AnalysisResult } from "@/lib/analysis";

export default function AnalyzePage() {
  const [file, setFile] = useState<File | null>(null);
  const [results, setResults] = useState<AnalysisResult[]>([]);
  const [isLoading, setIsLoading] = useState(false);
  const resultsRef = useRef<HTMLDivElement>(null);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!file) return;

    setIsLoading(true);
    try {
      const backendUri = process.env.NEXT_PUBLIC_BACKEND_URI;
      if (!backendUri) throw new Error("Backend URI not configured");

      const formData = new FormData();
      formData.append('file', file);

      const response = await fetch(`${backendUri}/analyze`, {
        method: "POST",
        body: formData,
      });

      if (!response.ok) throw new Error("Analysis failed");

      const responseData = await response.json();

      // Parse bursts CSV
      const burstLines = responseData.bursts_csv.split('\n').filter((line: string) => line.trim());
      let detectedBursts: any[] = [];
      if (burstLines.length >= 2) {
        const burstHeaders = burstLines[0].split(',').map((h: string) => h.trim());
        detectedBursts = burstLines.slice(1).map((line: string) => {
          const values = line.split(',').map((v: string) => v.trim());
          const data: any = {};
          burstHeaders.forEach((header: string, index: number) => {
            data[header] = parseFloat(values[index]) || values[index];
          });
          return {
            t_start: data.StartFWTM,
            t_end: data.EndFWTM,
            F0: data.PeakFlux,
            A: data.Fitted_A,
            t0: data.PeakTime,
            tau_r: data.RiseSigma,
            tau_d: data.DecayTau,
            F_peak: data.PeakFlux,
            t_peak: data.PeakTime,
            duration: data.EndFWTM - data.StartFWTM,
          };
        }).filter((burst: any) => !isNaN(burst.t_start));
      }

      // Parse plot CSV
      const plotLines = responseData.plot_df.split('\n').filter((line: string) => line.trim());
      const plotHeaders = plotLines[0].split(',').map((h: string) => h.trim());
      const plotDataArray = plotLines.slice(1).map((line: string) => {
        const values = line.split(',').map((v: string) => parseFloat(v.trim()));
        return {
          time: values[0],
          flux: values[1],
          background: values[2],
        };
      }).filter((d: any) => !isNaN(d.time));

      // Calculate total flux
      const totalFlux = plotDataArray.map((d: any) => d.flux + d.background);
      const yMin = Math.min(...totalFlux);
      const yMax = Math.max(...totalFlux);

      // Create shapes for bursts: vertical lines at t_peak
      const shapes = detectedBursts.map((burst: any) => ({
        type: 'line',
        x0: burst.t_peak,
        y0: yMin,
        x1: burst.t_peak,
        y1: yMax,
        line: { color: '#ff000035', width: 3 },
      }));

      // Annotations for '*' at start and end times on the curve
      const annotations: any[] = [];
      detectedBursts.forEach((burst: any) => {
        // Find closest index for t_start
        const startIdx = plotDataArray.reduce((prev: number, curr: any, idx: number) =>
          Math.abs(curr.time - burst.t_start) < Math.abs(plotDataArray[prev].time - burst.t_start) ? idx : prev, 0);
        annotations.push({
          x: burst.t_start,
          y: totalFlux[startIdx],
          xref: 'x',
          yref: 'y',
          text: '*',
          showarrow: false,
          font: { color: 'red', size: 14 },
        });

        // Find closest index for t_end
        const endIdx = plotDataArray.reduce((prev: number, curr: any, idx: number) =>
          Math.abs(curr.time - burst.t_end) < Math.abs(plotDataArray[prev].time - burst.t_end) ? idx : prev, 0);
        annotations.push({
          x: burst.t_end,
          y: totalFlux[endIdx],
          xref: 'x',
          yref: 'y',
          text: '*',
          showarrow: false,
          font: { color: 'red', size: 14 },
        });
      });

      const plotData = {
        data: [
          {
            x: plotDataArray.map((d: any) => d.time),
            y: totalFlux,
            type: 'scatter',
            mode: 'lines',
            name: 'Flux',
          },
        ],
        layout: {
          title: 'X-ray Light Curve',
          xaxis: { title: 'Time (s)' },
          yaxis: { title: 'Flux (counts/s)' },
          shapes: shapes,
          annotations: annotations,
        },
      };

      const newResult: AnalysisResult = {
        id: Date.now().toString(),
        timestamp: new Date().toISOString(),
        plotData,
        detectedBursts,
      };
      setResults((prev) => [newResult, ...prev]);

      // Smooth scroll to results
      setTimeout(() => {
        resultsRef.current?.scrollIntoView({ behavior: "smooth", block: "start" });
      }, 500);
    } catch (error) {
      console.error("Analysis error:", error);
    } finally {
      setIsLoading(false);
    }
  };

  const clearSession = () => {
    setResults([]);
  };

  return (
    <div className="space-y-8">
      <div className="text-center">
        <h1 className="text-3xl font-bold">Analysis Workspace</h1>
        <p className="text-muted-foreground mt-2">
          Upload your X-ray light curve data and configure analysis parameters.
        </p>
      </div>

      {/* Upload Section */}
      <div className="mx-auto">
        <Card>
          <CardHeader>
            <CardTitle>Input Configuration</CardTitle>
            <CardDescription>
              Upload your data file and set analysis parameters.
            </CardDescription>
          </CardHeader>
          <CardContent>
            <AnalysisForm
              file={file}
              setFile={setFile}
              onSubmit={handleSubmit}
              isPending={isLoading}
              clearSession={clearSession}
            />
          </CardContent>
        </Card>
      </div>

      {/* Results Section */}
      <AnalysisResults results={results} resultsRef={resultsRef} />
    </div>
  );
}
