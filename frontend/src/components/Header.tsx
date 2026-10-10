import React from 'react';
import { Sliders, Volume2, VolumeX, Cpu } from 'lucide-react';
import type { ModelStatus } from '../types';

interface HeaderProps {
  selectedBin: 'Wet Waste' | 'Dry Waste';
  onBinChange: (bin: 'Wet Waste' | 'Dry Waste') => void;
  confidenceThreshold: number;
  onConfidenceChange: (val: number) => void;
  audioAlertsEnabled: boolean;
  onToggleAudio: () => void;
  modelStatus: ModelStatus | null;
}

export const Header: React.FC<HeaderProps> = ({
  selectedBin,
  onBinChange,
  confidenceThreshold,
  onConfidenceChange,
  audioAlertsEnabled,
  onToggleAudio,
  modelStatus
}) => {
  return (
    <header className="bg-white border-b border-slate-200 px-6 py-3.5 flex flex-wrap items-center justify-between gap-4 sticky top-0 z-20 shadow-sm">
      {/* Title & Model Status Indicator */}
      <div className="flex items-center space-x-4">
        <div className="flex items-center space-x-2 bg-slate-100 border border-slate-200 px-3 py-1.5 rounded-full text-xs font-semibold text-slate-700">
          <span className={`w-2.5 h-2.5 rounded-full ${modelStatus?.is_loaded ? 'bg-emerald-500 animate-pulse' : 'bg-amber-500'}`} />
          <Cpu className="w-3.5 h-3.5 text-slate-500" />
          <span>{modelStatus?.model_name || 'YOLOv8 Model'}</span>
        </div>
      </div>

      {/* Control Tools */}
      <div className="flex items-center space-x-6">
        {/* Disposal Bin Target Switcher */}
        <div className="flex items-center space-x-2">
          <span className="text-xs font-semibold text-slate-500 uppercase tracking-wider">Disposal Bin:</span>
          <div className="inline-flex p-1 bg-slate-100 rounded-lg border border-slate-200 text-xs font-medium">
            <button
              onClick={() => onBinChange('Wet Waste')}
              className={`px-3 py-1 rounded-md transition-all ${
                selectedBin === 'Wet Waste'
                  ? 'bg-emerald-600 text-white font-semibold shadow-sm'
                  : 'text-slate-600 hover:text-slate-900'
              }`}
            >
              💧 Wet Waste
            </button>
            <button
              onClick={() => onBinChange('Dry Waste')}
              className={`px-3 py-1 rounded-md transition-all ${
                selectedBin === 'Dry Waste'
                  ? 'bg-emerald-600 text-white font-semibold shadow-sm'
                  : 'text-slate-600 hover:text-slate-900'
              }`}
            >
              📦 Dry Waste
            </button>
          </div>
        </div>

        {/* Confidence Threshold Slider */}
        <div className="flex items-center space-x-2.5 min-w-[180px]">
          <Sliders className="w-4 h-4 text-slate-400" />
          <span className="text-xs font-semibold text-slate-500">Conf:</span>
          <input
            type="range"
            min="0.10"
            max="0.90"
            step="0.05"
            value={confidenceThreshold}
            onChange={(e) => onConfidenceChange(parseFloat(e.target.value))}
            className="w-24 accent-emerald-600 h-1.5 bg-slate-200 rounded-lg cursor-pointer"
          />
          <span className="text-xs font-bold text-slate-700 font-mono">{(confidenceThreshold * 100).toFixed(0)}%</span>
        </div>

        {/* Audio Alert Toggle */}
        <button
          onClick={onToggleAudio}
          className={`flex items-center space-x-1.5 px-3 py-1.5 rounded-lg border text-xs font-medium transition-all ${
            audioAlertsEnabled
              ? 'bg-emerald-50 border-emerald-200 text-emerald-700 hover:bg-emerald-100'
              : 'bg-slate-50 border-slate-200 text-slate-500 hover:bg-slate-100'
          }`}
          title={audioAlertsEnabled ? 'Audio alerts active' : 'Audio alerts muted'}
        >
          {audioAlertsEnabled ? <Volume2 className="w-4 h-4 text-emerald-600" /> : <VolumeX className="w-4 h-4 text-slate-400" />}
          <span>{audioAlertsEnabled ? 'Alerts ON' : 'Muted'}</span>
        </button>
      </div>
    </header>
  );
};
