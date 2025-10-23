"use client";

import { useState, useRef } from "react";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import AnalysisForm from "@/components/AnalysisForm";
import AnalysisResults from "@/components/AnalysisResults";
import { AnalysisResult } from "@/lib/analysis";

export default function AnalyzePage() {
  const [file, setFile] = useState<File | null>(null);
  const [threshold, setThreshold] = useState("3.0");
  const [backgroundWindow, setBackgroundWindow] = useState("100");
  const [modelType, setModelType] = useState("exponential");
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
      const burstHeaders = burstLines[0].split(',').map((h: string) => h.trim());
      const detectedBursts = burstLines.slice(1).map((line: string) => {
        const values = line.split(',').map((v: string) => v.trim());
        return {
          t_start: parseFloat(values[0]),
          t_end: parseFloat(values[1]),
          F0: parseFloat(values[2]),
          A: parseFloat(values[3]),
          t0: parseFloat(values[4]),
          tau_r: parseFloat(values[5]),
          tau_d: parseFloat(values[6]),
          F_peak: parseFloat(values[7]),
          t_peak: parseFloat(values[8]),
          duration: parseFloat(values[9]),
        };
      }).filter((burst: any) => !isNaN(burst.t_start));

      const newResult: AnalysisResult = {
        id: Date.now().toString(),
        timestamp: new Date().toISOString(),
        plotData: responseData.plot_data,
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
              threshold={threshold}
              setThreshold={setThreshold}
              backgroundWindow={backgroundWindow}
              setBackgroundWindow={setBackgroundWindow}
              modelType={modelType}
              setModelType={setModelType}
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
