import React, { useEffect, useState } from 'react';
import { Target, CheckCircle } from 'lucide-react';
import { getDatasetSummary, getDatasetImages, inspectDatasetImage } from '../services/api';
import type { DatasetSummary, DatasetInspectResult } from '../types';

interface DatasetLabPageProps {
  selectedBin: 'Wet Waste' | 'Dry Waste';
  confidenceThreshold: number;
}

export const DatasetLabPage: React.FC<DatasetLabPageProps> = ({
  selectedBin,
  confidenceThreshold
}) => {
  const [summary, setSummary] = useState<DatasetSummary | null>(null);
  const [activeSplit, setActiveSplit] = useState<string>('test');
  const [images, setImages] = useState<string[]>([]);
  const [selectedImage, setSelectedImage] = useState<string>('');
  const [inspectResult, setInspectResult] = useState<DatasetInspectResult | null>(null);

  useEffect(() => {
    const fetchSummary = async () => {
      try {
        const s = await getDatasetSummary();
        setSummary(s);
      } catch (e) {
        console.error('Failed to load dataset summary:', e);
      }
    };
    fetchSummary();
  }, []);

  useEffect(() => {
    const fetchImages = async () => {
      try {
        const res = await getDatasetImages(activeSplit);
        setImages(res.images || []);
        if (res.images && res.images.length > 0) {
          setSelectedImage(res.images[0]);
        }
      } catch (e) {
        console.error('Failed to load images for split:', e);
      }
    };
    fetchImages();
  }, [activeSplit]);

  const handleInspect = async () => {
    if (!selectedImage) return;
    try {
      const res = await inspectDatasetImage(activeSplit, selectedImage, selectedBin, confidenceThreshold);
      setInspectResult(res);
    } catch (e) {
      console.error('Inspection failed:', e);
    }
  };

  useEffect(() => {
    if (selectedImage) {
      handleInspect();
    }
  }, [selectedImage, selectedBin, confidenceThreshold]);

  return (
    <div className="space-y-6 max-w-6xl mx-auto">
      <div>
        <h2 className="text-xl font-bold text-slate-800">Roboflow Dataset Testing Lab</h2>
        <p className="text-xs text-slate-500">
          Verify YOLO detection accuracy against verified ground-truth labels across 13,104 dataset split images
        </p>
      </div>

      {/* Dataset Summary Cards */}
      {summary && (
        <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
          <div className="bg-white p-4 rounded-xl border border-slate-200 shadow-sm">
            <span className="text-xs font-semibold text-slate-500 uppercase">Dataset Classes</span>
            <p className="text-xl font-black text-slate-800 mt-1">{summary.num_classes} Classes</p>
          </div>
          <div className="bg-white p-4 rounded-xl border border-slate-200 shadow-sm">
            <span className="text-xs font-semibold text-slate-500 uppercase">Train Split</span>
            <p className="text-xl font-black text-emerald-600 mt-1">11,466 Images</p>
          </div>
          <div className="bg-white p-4 rounded-xl border border-slate-200 shadow-sm">
            <span className="text-xs font-semibold text-slate-500 uppercase">Valid Split</span>
            <p className="text-xl font-black text-teal-600 mt-1">1,092 Images</p>
          </div>
          <div className="bg-white p-4 rounded-xl border border-slate-200 shadow-sm">
            <span className="text-xs font-semibold text-slate-500 uppercase">Test Split</span>
            <p className="text-xl font-black text-slate-700 mt-1">546 Images</p>
          </div>
        </div>
      )}

      {/* Controls Row */}
      <div className="bg-white p-5 rounded-2xl border border-slate-200 shadow-sm flex flex-wrap items-center justify-between gap-4">
        <div className="flex items-center space-x-3">
          <span className="text-xs font-bold text-slate-600 uppercase">Dataset Split:</span>
          <div className="inline-flex p-1 bg-slate-100 rounded-lg border border-slate-200 text-xs font-medium">
            {['test', 'valid', 'train'].map((sp) => (
              <button
                key={sp}
                onClick={() => setActiveSplit(sp)}
                className={`px-3 py-1 rounded-md uppercase font-bold transition-all ${
                  activeSplit === sp ? 'bg-emerald-600 text-white shadow-xs' : 'text-slate-600 hover:text-slate-900'
                }`}
              >
                {sp}
              </button>
            ))}
          </div>
        </div>

        <div className="flex items-center space-x-3">
          <span className="text-xs font-bold text-slate-600 uppercase">Sample Image:</span>
          <select
            value={selectedImage}
            onChange={(e) => setSelectedImage(e.target.value)}
            className="px-3 py-1.5 bg-slate-50 border border-slate-200 rounded-lg text-xs font-mono text-slate-800"
          >
            {images.map((img) => (
              <option key={img} value={img}>
                {img}
              </option>
            ))}
          </select>
        </div>
      </div>

      {/* Side-by-side Overlays */}
      {inspectResult && (
        <div className="space-y-6">
          <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
            {/* Model Predictions */}
            <div className="bg-white p-5 rounded-2xl border border-slate-200 shadow-sm space-y-3">
              <div className="flex items-center justify-between">
                <span className="text-sm font-bold text-slate-800 flex items-center space-x-1.5">
                  <Target className="w-4 h-4 text-emerald-600" />
                  <span>Model Prediction & Rules</span>
                </span>
                <span className="text-xs text-slate-500 font-mono">
                  {inspectResult.predictions.length} Detections
                </span>
              </div>
              <div className="rounded-xl overflow-hidden bg-slate-900 border border-slate-800 flex items-center justify-center min-h-[300px]">
                <img
                  src={inspectResult.prediction_overlay_base64}
                  alt="Prediction overlay"
                  className="max-h-[380px] w-auto mx-auto object-contain"
                />
              </div>
            </div>

            {/* Ground Truth Annotations */}
            <div className="bg-white p-5 rounded-2xl border border-slate-200 shadow-sm space-y-3">
              <div className="flex items-center justify-between">
                <span className="text-sm font-bold text-slate-800 flex items-center space-x-1.5">
                  <CheckCircle className="w-4 h-4 text-purple-600" />
                  <span>Ground-Truth Labels (Dataset)</span>
                </span>
                <span className="text-xs text-slate-500 font-mono">
                  {inspectResult.ground_truths.length} Annotations
                </span>
              </div>
              <div className="rounded-xl overflow-hidden bg-slate-900 border border-slate-800 flex items-center justify-center min-h-[300px]">
                <img
                  src={inspectResult.ground_truth_overlay_base64}
                  alt="Ground truth overlay"
                  className="max-h-[380px] w-auto mx-auto object-contain"
                />
              </div>
            </div>
          </div>

          {/* Evaluation Metrics */}
          <div className="bg-white p-5 rounded-2xl border border-slate-200 shadow-sm">
            <h3 className="text-sm font-bold text-slate-800 mb-3">Quantitative Comparison Metrics</h3>
            <div className="grid grid-cols-2 md:grid-cols-5 gap-4">
              <div className="p-3 bg-slate-50 rounded-xl border border-slate-100">
                <span className="text-[11px] font-semibold text-slate-500 uppercase">True Positives (TP)</span>
                <p className="text-lg font-black text-emerald-700 mt-0.5">{inspectResult.metrics.tp}</p>
              </div>
              <div className="p-3 bg-slate-50 rounded-xl border border-slate-100">
                <span className="text-[11px] font-semibold text-slate-500 uppercase">False Positives (FP)</span>
                <p className="text-lg font-black text-red-700 mt-0.5">{inspectResult.metrics.fp}</p>
              </div>
              <div className="p-3 bg-slate-50 rounded-xl border border-slate-100">
                <span className="text-[11px] font-semibold text-slate-500 uppercase">Precision</span>
                <p className="text-lg font-black text-slate-800 mt-0.5">
                  {(inspectResult.metrics.precision * 100).toFixed(1)}%
                </p>
              </div>
              <div className="p-3 bg-slate-50 rounded-xl border border-slate-100">
                <span className="text-[11px] font-semibold text-slate-500 uppercase">Recall</span>
                <p className="text-lg font-black text-slate-800 mt-0.5">
                  {(inspectResult.metrics.recall * 100).toFixed(1)}%
                </p>
              </div>
              <div className="p-3 bg-slate-50 rounded-xl border border-slate-100">
                <span className="text-[11px] font-semibold text-slate-500 uppercase">Mean IoU</span>
                <p className="text-lg font-black text-teal-700 mt-0.5">
                  {(inspectResult.metrics.mean_iou * 100).toFixed(1)}%
                </p>
              </div>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};
