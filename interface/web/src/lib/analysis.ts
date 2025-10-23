export interface AnalysisResult {
  id: string;
  timestamp: string;
  plotData: any;
  detectedBursts: Array<{
    t_start: number;
    t_end: number;
    F0: number;
    A: number;
    t0: number;
    tau_r: number;
    tau_d: number;
    F_peak: number;
    t_peak: number;
    duration: number;
  }>;
}

export const handleDragOver = (e: React.DragEvent) => {
  e.preventDefault();
};

export const handleDrop = (
  e: React.DragEvent,
  setFile: (file: File | null) => void
) => {
  e.preventDefault();
  const droppedFile = e.dataTransfer.files[0];
  if (droppedFile && (droppedFile.name.endsWith('.csv') || droppedFile.name.endsWith('.txt') || droppedFile.name.endsWith('.fits'))) {
    setFile(droppedFile);
  }
};

export const handleFileSelect = (
  e: React.ChangeEvent<HTMLInputElement>,
  setFile: (file: File | null) => void
) => {
  const selectedFile = e.target.files?.[0] || null;
  if (selectedFile) {
    setFile(selectedFile);
  }
};

export const removeFile = (
  setFile: (file: File | null) => void,
  fileInputRef: React.RefObject<HTMLInputElement | null>
) => {
  setFile(null);
  if (fileInputRef.current) {
    fileInputRef.current.value = '';
  }
};

export const downloadResult = (result: AnalysisResult) => {
  const csvContent = result.detectedBursts.map(burst =>
    `${result.timestamp},${burst.t_start},${burst.t_peak},${burst.t_end},${burst.F_peak},${burst.A}`
  ).join("\n");

  const blob = new Blob([`timestamp,t_start,t_peak,t_end,F_peak,A\n${csvContent}`], { type: "text/csv" });
  const url = URL.createObjectURL(blob);
  const a = document.createElement("a");
  a.href = url;
  a.download = `analysis_${result.id}.csv`;
  a.click();
  URL.revokeObjectURL(url);
};
