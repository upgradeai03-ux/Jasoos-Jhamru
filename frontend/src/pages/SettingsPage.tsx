import React, { useEffect, useState } from 'react';
import { getSegregationConfig } from '../services/api';

export const SettingsPage: React.FC = () => {
  const [config, setConfig] = useState<any>(null);

  useEffect(() => {
    getSegregationConfig().then(setConfig).catch(console.error);
  }, []);

  return (
    <div className="space-y-6 max-w-5xl mx-auto">
      <div>
        <h2 className="text-xl font-bold text-slate-800">System & Segregation Policy Settings</h2>
        <p className="text-xs text-slate-500">Configure waste classification mappings, confidence tolerances, and alert parameters</p>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
        {/* Wet Waste Classes */}
        <div className="bg-white p-5 rounded-2xl border border-slate-200 shadow-sm space-y-3">
          <div className="flex items-center space-x-2">
            <span className="w-3 h-3 rounded-full bg-emerald-500" />
            <h3 className="text-sm font-bold text-slate-800">Wet Waste Policy</h3>
          </div>
          <p className="text-xs text-slate-500">Classes mapped strictly to Organic/Compostable bin</p>
          <div className="space-y-1.5 max-h-60 overflow-y-auto pr-1">
            {config?.categories?.['Wet Waste']?.map((item: string) => (
              <div key={item} className="px-3 py-1.5 bg-emerald-50 text-emerald-800 rounded-lg text-xs font-semibold">
                {item}
              </div>
            ))}
          </div>
        </div>

        {/* Dry Waste Classes */}
        <div className="bg-white p-5 rounded-2xl border border-slate-200 shadow-sm space-y-3">
          <div className="flex items-center space-x-2">
            <span className="w-3 h-3 rounded-full bg-teal-500" />
            <h3 className="text-sm font-bold text-slate-800">Dry Waste Policy</h3>
          </div>
          <p className="text-xs text-slate-500">Classes mapped to Recyclable/Dry Materials bin</p>
          <div className="space-y-1.5 max-h-60 overflow-y-auto pr-1">
            {config?.categories?.['Dry Waste']?.map((item: string) => (
              <div key={item} className="px-3 py-1.5 bg-teal-50 text-teal-800 rounded-lg text-xs font-semibold">
                {item}
              </div>
            ))}
          </div>
        </div>

        {/* Needs Review Classes */}
        <div className="bg-white p-5 rounded-2xl border border-slate-200 shadow-sm space-y-3">
          <div className="flex items-center space-x-2">
            <span className="w-3 h-3 rounded-full bg-amber-500" />
            <h3 className="text-sm font-bold text-slate-800">Needs Review Policy</h3>
          </div>
          <p className="text-xs text-slate-500">Hazardous, electronic, or unmapped items</p>
          <div className="space-y-1.5 max-h-60 overflow-y-auto pr-1">
            {config?.categories?.['Needs Review']?.map((item: string) => (
              <div key={item} className="px-3 py-1.5 bg-amber-50 text-amber-800 rounded-lg text-xs font-semibold">
                {item}
              </div>
            ))}
          </div>
        </div>
      </div>
    </div>
  );
};
