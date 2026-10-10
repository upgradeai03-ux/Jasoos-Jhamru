import React, { useEffect, useState } from 'react';
import { Activity, Cpu, Database } from 'lucide-react';
import { getHealth, getModelStatus, getDatasetSummary } from '../services/api';
import type { HealthStatus, ModelStatus, DatasetSummary } from '../types';

export const HealthPage: React.FC = () => {
  const [health, setHealth] = useState<HealthStatus | null>(null);
  const [model, setModel] = useState<ModelStatus | null>(null);
  const [dataset, setDataset] = useState<DatasetSummary | null>(null);

  useEffect(() => {
    getHealth().then(setHealth).catch(console.error);
    getModelStatus().then(setModel).catch(console.error);
    getDatasetSummary().then(setDataset).catch(console.error);
  }, []);

  return (
    <div className="space-y-6 max-w-5xl mx-auto">
      <div>
        <h2 className="text-xl font-bold text-slate-800">System & Model Health Diagnostics</h2>
        <p className="text-xs text-slate-500">Live operational status of computer vision models, API services, and datasets</p>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
        {/* Backend API Health */}
        <div className="bg-white p-6 rounded-2xl border border-slate-200 shadow-sm space-y-4">
          <div className="flex items-center space-x-3">
            <div className="w-10 h-10 rounded-xl bg-emerald-100 text-emerald-600 flex items-center justify-center">
              <Activity className="w-5 h-5" />
            </div>
            <div>
              <h3 className="text-sm font-bold text-slate-800">FastAPI Backend</h3>
              <p className="text-[11px] text-slate-400">REST API Gateway</p>
            </div>
          </div>

          <div className="space-y-2 text-xs border-t border-slate-100 pt-3">
            <div className="flex justify-between">
              <span className="text-slate-500">Service Status:</span>
              <span className="font-bold text-emerald-600">● {health?.status?.toUpperCase() || 'OFFLINE'}</span>
            </div>
            <div className="flex justify-between">
              <span className="text-slate-500">API Version:</span>
              <span className="font-mono text-slate-700">{health?.version || '1.0.0'}</span>
            </div>
            <div className="flex justify-between">
              <span className="text-slate-500">Server Time:</span>
              <span className="font-mono text-[10px] text-slate-500">{health?.timestamp || '-'}</span>
            </div>
          </div>
        </div>

        {/* YOLO Model Health */}
        <div className="bg-white p-6 rounded-2xl border border-slate-200 shadow-sm space-y-4">
          <div className="flex items-center space-x-3">
            <div className="w-10 h-10 rounded-xl bg-teal-100 text-teal-600 flex items-center justify-center">
              <Cpu className="w-5 h-5" />
            </div>
            <div>
              <h3 className="text-sm font-bold text-slate-800">YOLO Model Engine</h3>
              <p className="text-[11px] text-slate-400">Object Detection Pipeline</p>
            </div>
          </div>

          <div className="space-y-2 text-xs border-t border-slate-100 pt-3">
            <div className="flex justify-between">
              <span className="text-slate-500">Active Model:</span>
              <span className="font-bold text-slate-800">{model?.model_name || 'None'}</span>
            </div>
            <div className="flex justify-between">
              <span className="text-slate-500">Model Weights:</span>
              <span className="font-mono text-[10px] text-slate-500 truncate max-w-[150px]">{model?.model_path || '-'}</span>
            </div>
            <div className="flex justify-between">
              <span className="text-slate-500">Classes Loaded:</span>
              <span className="font-bold text-slate-700">{model?.total_classes || 0}</span>
            </div>
          </div>
        </div>

        {/* Dataset Status */}
        <div className="bg-white p-6 rounded-2xl border border-slate-200 shadow-sm space-y-4">
          <div className="flex items-center space-x-3">
            <div className="w-10 h-10 rounded-xl bg-purple-100 text-purple-600 flex items-center justify-center">
              <Database className="w-5 h-5" />
            </div>
            <div>
              <h3 className="text-sm font-bold text-slate-800">Dataset Validation</h3>
              <p className="text-[11px] text-slate-400">13,104 Annotated Images</p>
            </div>
          </div>

          <div className="space-y-2 text-xs border-t border-slate-100 pt-3">
            <div className="flex justify-between">
              <span className="text-slate-500">Configuration:</span>
              <span className="font-bold text-emerald-600">{dataset?.is_valid ? '● VALIDATED' : 'INVALID'}</span>
            </div>
            <div className="flex justify-between">
              <span className="text-slate-500">Configured Classes:</span>
              <span className="font-bold text-slate-700">{dataset?.num_classes || 42}</span>
            </div>
            <div className="flex justify-between">
              <span className="text-slate-500">Train/Val/Test:</span>
              <span className="font-mono text-[11px] text-slate-600">11.4k / 1.1k / 546</span>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};
