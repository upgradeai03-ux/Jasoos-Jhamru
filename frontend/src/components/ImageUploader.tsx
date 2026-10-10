import React, { useState, useRef } from 'react';
import { UploadCloud, Image as ImageIcon, X, RefreshCw, AlertTriangle, CheckCircle2, ShieldAlert } from 'lucide-react';
import { detectImage } from '../services/api';
import type { ImageDetectionResponse } from '../types';

interface ImageUploaderProps {
  selectedBin: 'Wet Waste' | 'Dry Waste';
  confidenceThreshold: number;
  onAnalysisComplete: (result: ImageDetectionResponse) => void;
}

export const ImageUploader: React.FC<ImageUploaderProps> = ({
  selectedBin,
  confidenceThreshold,
  onAnalysisComplete
}) => {
  const [selectedFile, setSelectedFile] = useState<File | null>(null);
  const [previewUrl, setPreviewUrl] = useState<string | null>(null);
  const [isDragOver, setIsDragOver] = useState<boolean>(false);
  const [isLoading, setIsLoading] = useState<boolean>(false);
  const [errorMessage, setErrorMessage] = useState<string | null>(null);
  const [analysisResult, setAnalysisResult] = useState<ImageDetectionResponse | null>(null);

  const fileInputRef = useRef<HTMLInputElement>(null);

  const ALLOWED_TYPES = ['image/jpeg', 'image/png', 'image/webp', 'image/jpg'];
  const MAX_SIZE_MB = 15;

  const validateAndSetFile = (file: File) => {
    setErrorMessage(null);
    setAnalysisResult(null);

    if (!ALLOWED_TYPES.includes(file.type)) {
      setErrorMessage(`Invalid file format '${file.type}'. Allowed formats: JPG, PNG, WEBP.`);
      return;
    }

    if (file.size > MAX_SIZE_MB * 1024 * 1024) {
      setErrorMessage(`File size (${(file.size / (1024 * 1024)).toFixed(1)}MB) exceeds limit of ${MAX_SIZE_MB}MB.`);
      return;
    }

    setSelectedFile(file);
    const url = URL.createObjectURL(file);
    setPreviewUrl(url);
  };

  const handleDrop = (e: React.DragEvent<HTMLDivElement>) => {
    e.preventDefault();
    setIsDragOver(false);
    if (e.dataTransfer.files && e.dataTransfer.files.length > 0) {
      validateAndSetFile(e.dataTransfer.files[0]);
    }
  };

  const handleFileSelect = (e: React.ChangeEvent<HTMLInputElement>) => {
    if (e.target.files && e.target.files.length > 0) {
      validateAndSetFile(e.target.files[0]);
    }
  };

  const handleAnalyze = async () => {
    if (!selectedFile) return;

    setIsLoading(true);
    setErrorMessage(null);

    try {
      const res = await detectImage(selectedFile, selectedBin, confidenceThreshold, true);
      setAnalysisResult(res);
      onAnalysisComplete(res);
    } catch (err: any) {
      const detail = err.response?.data?.detail || err.message || 'Image detection request failed.';
      setErrorMessage(detail);
    } finally {
      setIsLoading(false);
    }
  };

  const handleClear = () => {
    setSelectedFile(null);
    if (previewUrl) URL.revokeObjectURL(previewUrl);
    setPreviewUrl(null);
    setAnalysisResult(null);
    setErrorMessage(null);
    if (fileInputRef.current) fileInputRef.current.value = '';
  };

  return (
    <div className="bg-white rounded-2xl border border-slate-200 p-6 shadow-sm">
      {/* Upload Header */}
      <div className="flex items-center justify-between mb-4">
        <div>
          <h3 className="text-base font-bold text-slate-800">Waste Image Inspector</h3>
          <p className="text-xs text-slate-500">Upload waste image for object detection & segregation verification</p>
        </div>
        {selectedFile && (
          <button
            onClick={handleClear}
            className="text-xs font-semibold text-slate-500 hover:text-red-600 flex items-center space-x-1 px-2.5 py-1 rounded-lg border border-slate-200 hover:border-red-200 bg-slate-50 hover:bg-red-50 transition-all"
          >
            <X className="w-3.5 h-3.5" />
            <span>Remove Image</span>
          </button>
        )}
      </div>

      {/* Error Message Box */}
      {errorMessage && (
        <div className="mb-4 p-3.5 bg-red-50 border border-red-200 rounded-xl flex items-start space-x-3 text-red-700 text-xs">
          <AlertTriangle className="w-4 h-4 text-red-600 shrink-0 mt-0.5" />
          <div className="flex-1">
            <p className="font-semibold">{errorMessage}</p>
          </div>
        </div>
      )}

      {/* Dropzone & Preview Box */}
      {!selectedFile ? (
        <div
          onDragOver={(e) => {
            e.preventDefault();
            setIsDragOver(true);
          }}
          onDragLeave={() => setIsDragOver(false)}
          onDrop={handleDrop}
          onClick={() => fileInputRef.current?.click()}
          className={`border-2 border-dashed rounded-2xl p-10 text-center cursor-pointer transition-all duration-200 ${
            isDragOver
              ? 'border-emerald-500 bg-emerald-50/60 shadow-inner'
              : 'border-slate-300 hover:border-emerald-400 bg-slate-50/50 hover:bg-slate-50'
          }`}
        >
          <input
            type="file"
            ref={fileInputRef}
            onChange={handleFileSelect}
            accept="image/png, image/jpeg, image/webp"
            className="hidden"
          />
          <div className="w-14 h-14 mx-auto mb-3 rounded-2xl bg-emerald-100 text-emerald-600 flex items-center justify-center">
            <UploadCloud className="w-7 h-7" />
          </div>
          <h4 className="text-sm font-semibold text-slate-800">
            Drag & Drop image here, or <span className="text-emerald-600 underline">browse</span>
          </h4>
          <p className="text-xs text-slate-400 mt-1">Supports PNG, JPG, JPEG, WEBP up to 15MB</p>
        </div>
      ) : (
        <div className="space-y-4">
          <div className="relative rounded-2xl overflow-hidden border border-slate-200 bg-slate-900 min-h-[260px] max-h-[460px] flex items-center justify-center">
            <img
              src={analysisResult?.annotated_image_base64 || previewUrl!}
              alt="Waste preview"
              className="max-h-[440px] w-auto max-w-full object-contain mx-auto"
            />

            {isLoading && (
              <div className="absolute inset-0 bg-slate-900/70 backdrop-blur-xs flex flex-col items-center justify-center text-white space-y-3">
                <RefreshCw className="w-8 h-8 animate-spin text-emerald-400" />
                <p className="text-xs font-medium tracking-wide">Running YOLO Waste Analysis...</p>
              </div>
            )}
          </div>

          {/* Action Button & Metadata */}
          <div className="flex items-center justify-between gap-4">
            <div className="text-xs text-slate-500">
              <span>File: <strong className="text-slate-700">{selectedFile.name}</strong></span>
              <span className="mx-2">•</span>
              <span>Size: <strong className="text-slate-700">{(selectedFile.size / (1024 * 1024)).toFixed(2)}MB</strong></span>
            </div>

            <button
              onClick={handleAnalyze}
              disabled={isLoading}
              className="px-6 py-2.5 bg-emerald-600 hover:bg-emerald-700 text-white font-semibold text-xs rounded-xl shadow-md shadow-emerald-900/20 disabled:opacity-50 flex items-center space-x-2 transition-all cursor-pointer"
            >
              {isLoading ? (
                <>
                  <RefreshCw className="w-4 h-4 animate-spin" />
                  <span>Processing...</span>
                </>
              ) : (
                <>
                  <ImageIcon className="w-4 h-4" />
                  <span>Run Waste AI Detection</span>
                </>
              )}
            </button>
          </div>
        </div>
      )}

      {/* Inference Results Banner */}
      {analysisResult && (
        <div className="mt-6 pt-6 border-t border-slate-200">
          <div className="flex items-center justify-between mb-3">
            <div className="flex items-center space-x-2">
              <span className="text-sm font-bold text-slate-800">Inference Results</span>
              <span className="text-xs font-semibold px-2.5 py-0.5 rounded-full bg-slate-100 text-slate-600">
                {analysisResult.total_detected} Objects Found
              </span>
            </div>
            <span className="text-xs font-mono text-slate-500">
              Inference: {analysisResult.inference_time_ms}ms
            </span>
          </div>

          {analysisResult.detections.length === 0 ? (
            <div className="p-4 bg-slate-50 rounded-xl text-center text-xs text-slate-500">
              No waste objects detected in this image above confidence threshold ({(confidenceThreshold * 100).toFixed(0)}%).
            </div>
          ) : (
            <div className="space-y-2.5 max-h-60 overflow-y-auto pr-1">
              {analysisResult.detections.map((det, idx) => (
                <div
                  key={idx}
                  className={`p-3.5 rounded-xl border flex items-center justify-between text-xs ${
                    det.is_violation
                      ? 'bg-red-50/70 border-red-200 text-red-900'
                      : det.is_correct
                      ? 'bg-emerald-50/70 border-emerald-200 text-emerald-900'
                      : 'bg-amber-50/70 border-amber-200 text-amber-900'
                  }`}
                >
                  <div className="flex items-center space-x-3">
                    {det.is_violation ? (
                      <ShieldAlert className="w-4 h-4 text-red-600 shrink-0" />
                    ) : det.is_correct ? (
                      <CheckCircle2 className="w-4 h-4 text-emerald-600 shrink-0" />
                    ) : (
                      <AlertTriangle className="w-4 h-4 text-amber-600 shrink-0" />
                    )}
                    <div>
                      <p className="font-bold text-sm">{det.class_name}</p>
                      <p className="text-[11px] opacity-80">{det.reason}</p>
                    </div>
                  </div>

                  <div className="text-right">
                    <span className="font-bold font-mono text-xs block">{(det.confidence * 100).toFixed(1)}%</span>
                    <span className="text-[10px] font-semibold uppercase tracking-wide opacity-75">{det.status}</span>
                  </div>
                </div>
              ))}
            </div>
          )}
        </div>
      )}
    </div>
  );
};
