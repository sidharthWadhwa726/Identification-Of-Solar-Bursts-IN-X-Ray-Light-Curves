"use client";

import { Button } from "@/components/ui/button";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { AnalysisResult, downloadResult } from "@/lib/analysis";
import dynamic from 'next/dynamic';

const Plot = dynamic(() => import('react-plotly.js'), { ssr: false });

interface AnalysisResultsProps {
  results: AnalysisResult[];
  resultsRef: React.RefObject<HTMLDivElement | null>;
}

export default function AnalysisResults({ results, resultsRef }: AnalysisResultsProps) {
  // if (results.length === 0) return null;

  return (
    <div ref={resultsRef} className="mt-12">
      <Card>
        <CardHeader>
          <CardTitle>Analysis Results</CardTitle>
          <CardDescription>
            {results.length} analysis{results.length > 1 ? 'es' : ''} completed
          </CardDescription>
        </CardHeader>
        <CardContent>
          <div className="space-y-8">
            {results.map((result) => (
              <div key={result.id} className="border rounded-lg p-6 space-y-6">
                <div>
                  <h4 className="font-semibold text-lg">
                    Analysis {result.timestamp}
                  </h4>
                </div>

                {/* Visualization */}
                <div className="h-96">
                  <Plot
                    data={result.plotData?.data || []}
                    layout={result.plotData?.layout || {}}
                    config={{ responsive: true }}
                    style={{ width: '100%', height: '100%' }}
                  />
                </div>

                {/* Results Table */}
                <div>
                  <h5 className="font-medium text-base mb-3">Detected Bursts</h5>
                  {result.detectedBursts.length === 0 ? (
                    <p className="text-sm text-muted-foreground">No bursts detected.</p>
                  ) : (
                    <div className="overflow-x-auto">
                      <table className="w-full text-sm">
                        <thead>
                          <tr className="border-b">
                            <th className="text-left p-2">Start Time</th>
                            <th className="text-left p-2">Peak Time</th>
                            <th className="text-left p-2">End Time</th>
                            <th className="text-left p-2">Peak Flux</th>
                            <th className="text-left p-2">Amplitude</th>
                            <th className="text-left p-2">Duration</th>
                          </tr>
                        </thead>
                        <tbody>
                          {result.detectedBursts.map((burst, index) => (
                            <tr key={index} className="border-b">
                              <td className="p-2">{burst.t_start.toFixed(2)}</td>
                              <td className="p-2">{burst.t_peak.toFixed(2)}</td>
                              <td className="p-2">{burst.t_end.toFixed(2)}</td>
                              <td className="p-2">{burst.F_peak.toFixed(4)}</td>
                              <td className="p-2">{burst.A.toFixed(4)}</td>
                              <td className="p-2">{burst.duration.toFixed(2)}</td>
                            </tr>
                          ))}
                        </tbody>
                      </table>
                    </div>
                  )}
                </div>

                {/* Download Button for this result */}
                <div className="flex justify-end">
                  <Button onClick={() => downloadResult(result)}>
                    Download CSV
                  </Button>
                </div>
              </div>
            ))}
          </div>
        </CardContent>
      </Card>
    </div>
  );
}
