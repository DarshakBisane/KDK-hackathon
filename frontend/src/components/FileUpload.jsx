import React, { useState, useRef } from 'react';
import { UploadCloud, FileText, X, CheckCircle, Loader2 } from 'lucide-react';
import { Button } from './Button';

export const FileUpload = ({
  onFileSelect,
  onAnalyze,
  isProcessing = false,
  processingStep = '',
  selectedFile = null,
  onRemoveFile,
}) => {
  const [isDragOver, setIsDragOver] = useState(false);
  const fileInputRef = useRef(null);

  const handleDragOver = (e) => {
    e.preventDefault();
    setIsDragOver(true);
  };

  const handleDragLeave = (e) => {
    e.preventDefault();
    setIsDragOver(false);
  };

  const handleDrop = (e) => {
    e.preventDefault();
    setIsDragOver(false);
    if (e.dataTransfer.files && e.dataTransfer.files.length > 0) {
      const file = e.dataTransfer.files[0];
      if (file.type === 'application/pdf' || file.name.toLowerCase().endsWith('.pdf')) {
        onFileSelect(file);
      }
    }
  };

  const handleFileInput = (e) => {
    if (e.target.files && e.target.files.length > 0) {
      const file = e.target.files[0];
      onFileSelect(file);
    }
  };

  const formatFileSize = (bytes) => {
    if (!bytes) return '0 KB';
    const kb = bytes / 1024;
    if (kb < 1024) return `${kb.toFixed(1)} KB`;
    return `${(kb / 1024).toFixed(2)} MB`;
  };

  // Pipeline steps
  const steps = [
    'Uploading',
    'Extracting Resume',
    'Analyzing Skills with AI',
    'Calculating Skill Gap',
    'Complete',
  ];

  return (
    <div className="w-full flex flex-col gap-4">
      {/* Dropzone */}
      {!selectedFile ? (
        <div
          onDragOver={handleDragOver}
          onDragLeave={handleDragLeave}
          onDrop={handleDrop}
          onClick={() => fileInputRef.current?.click()}
          className={`border-2 border-dashed rounded-2xl p-8 sm:p-12 text-center transition-all cursor-pointer flex flex-col items-center justify-center gap-3 ${
            isDragOver
              ? 'border-brand bg-brand-light/30 scale-[1.01]'
              : 'border-border-subtle bg-white hover:border-brand/40 hover:bg-bg-secondary/40'
          }`}
        >
          <input
            ref={fileInputRef}
            type="file"
            accept=".pdf,application/pdf"
            onChange={handleFileInput}
            className="hidden"
          />
          <div className="w-14 h-14 rounded-2xl bg-brand-light flex items-center justify-center text-brand mb-1 shadow-soft">
            <UploadCloud className="w-7 h-7" />
          </div>
          <div className="flex flex-col gap-1">
            <p className="text-base font-semibold text-text-primary">
              Drag & drop your resume here
            </p>
            <p className="text-xs text-text-secondary">
              Supports text-based PDF format up to 10MB
            </p>
          </div>
          <button
            type="button"
            className="mt-2 px-4 py-2 text-xs font-semibold text-brand bg-lavender rounded-xl hover:bg-brand hover:text-white transition-all pointer-events-none"
          >
            Choose PDF
          </button>
        </div>
      ) : (
        <div className="bg-white rounded-2xl border border-border-subtle p-5 shadow-soft flex flex-col gap-4">
          <div className="flex items-center justify-between">
            <div className="flex items-center gap-3.5">
              <div className="w-11 h-11 rounded-xl bg-paleblue-light text-paleblue-text flex items-center justify-center">
                <FileText className="w-6 h-6" />
              </div>
              <div>
                <p className="text-sm font-semibold text-text-primary truncate max-w-xs sm:max-w-md">
                  {selectedFile.name}
                </p>
                <p className="text-xs text-text-secondary">
                  {formatFileSize(selectedFile.size)} • PDF Document
                </p>
              </div>
            </div>
            {!isProcessing && (
              <button
                onClick={onRemoveFile}
                className="p-1.5 rounded-lg text-text-muted hover:text-status-danger hover:bg-red-50 transition-colors"
                title="Remove file"
              >
                <X className="w-5 h-5" />
              </button>
            )}
          </div>

          {/* Processing Status Pipeline UI */}
          {isProcessing ? (
            <div className="bg-bg-secondary p-4 rounded-xl border border-border-subtle flex flex-col gap-3">
              <div className="flex items-center gap-2.5">
                <Loader2 className="w-4 h-4 animate-spin text-brand" />
                <span className="text-xs font-semibold text-text-primary">
                  {processingStep || 'Processing your resume...'}
                </span>
              </div>
              <div className="grid grid-cols-2 sm:grid-cols-4 gap-2 text-[11px]">
                {steps.slice(0, 4).map((step, idx) => {
                  const isCurrent = processingStep.toLowerCase().includes(step.toLowerCase().slice(0, 5));
                  return (
                    <div
                      key={step}
                      className={`p-2 rounded-lg border text-center transition-all ${
                        isCurrent
                          ? 'bg-lavender text-brand font-semibold border-brand/30'
                          : 'bg-white text-text-secondary border-border-subtle'
                      }`}
                    >
                      {step}
                    </div>
                  );
                })}
              </div>
            </div>
          ) : (
            <Button
              variant="primary"
              size="lg"
              onClick={onAnalyze}
              className="w-full"
            >
              Analyze Resume with Gemini AI
            </Button>
          )}
        </div>
      )}
    </div>
  );
};
