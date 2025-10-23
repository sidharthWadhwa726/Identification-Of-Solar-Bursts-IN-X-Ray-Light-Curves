"use client";

import { useRef } from "react";
import { Button } from "@/components/ui/button";
import { Label } from "@/components/ui/label";
import { Upload, FileText, X } from "lucide-react";
import { handleDragOver, handleDrop, handleFileSelect, removeFile } from "@/lib/analysis";

interface FileUploadProps {
  file: File | null;
  setFile: (file: File | null) => void;
  clearSession: () => void;
}

export default function FileUpload({ file, setFile, clearSession }: FileUploadProps) {
  const fileInputRef = useRef<HTMLInputElement>(null);

  const onDrop = (e: React.DragEvent) => {
    handleDrop(e, setFile);
  };

  const onFileSelect = (e: React.ChangeEvent<HTMLInputElement>) => {
    handleFileSelect(e, setFile);
  };

  const onRemoveFile = () => {
    removeFile(setFile, fileInputRef);
    clearSession();
  };

  return (
    <div>
      <Label htmlFor="file">Data File</Label>
      <div
        className="mt-2 border-2 border-dashed border-muted-foreground/25 rounded-lg p-8 text-center hover:border-muted-foreground/50 transition-colors cursor-pointer"
        onDragOver={handleDragOver}
        onDrop={onDrop}
        onClick={() => fileInputRef.current?.click()}
      >
        {file ? (
          <div className="flex items-center justify-center space-x-3">
            <FileText className="h-8 w-8 text-muted-foreground" />
            <div className="text-left">
              <p className="font-medium text-sm">{file.name}</p>
              <p className="text-xs text-muted-foreground">
                {(file.size / 1024).toFixed(1)} KB
              </p>
            </div>
            <Button
              type="button"
              variant="ghost"
              size="sm"
              onClick={(e) => {
                e.stopPropagation();
                onRemoveFile();
              }}
              className="h-8 w-8 p-0"
            >
              <X className="h-4 w-4" />
            </Button>
          </div>
        ) : (
          <div className="space-y-2">
            <Upload className="h-12 w-12 text-muted-foreground mx-auto" />
            <div>
              <p className="font-medium">Drop your file here or click to browse</p>
              <p className="text-sm text-muted-foreground">
                Supports CSV, TXT, and FITS files
              </p>
            </div>
          </div>
        )}
      </div>
      <input
        ref={fileInputRef}
        type="file"
        accept="*"
        onChange={onFileSelect}
        className="hidden"
      />
    </div>
  );
}
