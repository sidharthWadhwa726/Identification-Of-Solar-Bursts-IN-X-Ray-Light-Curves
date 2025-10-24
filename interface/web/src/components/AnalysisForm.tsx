"use client";

import { Button } from "@/components/ui/button";
import FileUpload from "./FileUpload";

interface AnalysisFormProps {
  file: File | null;
  setFile: (file: File | null) => void;
  threshold: string;
  setThreshold: (value: string) => void;
  backgroundWindow: string;
  setBackgroundWindow: (value: string) => void;
  modelType: string;
  setModelType: (value: string) => void;
  onSubmit: (e: React.FormEvent) => void;
  isPending: boolean;
  clearSession: () => void;
}

export default function AnalysisForm({
  file,
  setFile,
  onSubmit,
  isPending,
  clearSession,
}: AnalysisFormProps) {
  return (
    <form onSubmit={onSubmit} className="space-y-6">
      <FileUpload file={file} setFile={setFile} clearSession={clearSession} />
      <Button
        type="submit"
        disabled={isPending || !file}
        className="w-full"
      >
        {isPending ? "Running Analysis..." : "Run Analysis"}
      </Button>
    </form>
  );
}
