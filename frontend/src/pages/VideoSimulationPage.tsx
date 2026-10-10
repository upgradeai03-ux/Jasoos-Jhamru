import React, { useState } from 'react';
import { UploadCloud } from 'lucide-react';

export const VideoSimulationPage: React.FC = () => {
  const [videoFile, setVideoFile] = useState<File | null>(null);
  const [videoUrl, setVideoUrl] = useState<string | null>(null);

  const handleVideoSelect = (e: React.ChangeEvent<HTMLInputElement>) => {
    if (e.target.files && e.target.files[0]) {
      const file = e.target.files[0];
      setVideoFile(file);
      setVideoUrl(URL.createObjectURL(file));
    }
  };

  return (
    <div className="space-y-6 max-w-5xl mx-auto">
      <div>
        <h2 className="text-xl font-bold text-slate-800">Video Stream Simulation</h2>
        <p className="text-xs text-slate-500">
          Simulate continuous waste disposal streams from recorded video files with frame deduplication
        </p>
      </div>

      <div className="bg-white p-6 rounded-2xl border border-slate-200 shadow-sm space-y-4">
        {!videoFile ? (
          <label className="border-2 border-dashed border-slate-300 hover:border-emerald-500 rounded-2xl p-10 flex flex-col items-center justify-center cursor-pointer bg-slate-50/50 hover:bg-slate-50 transition-all">
            <input type="file" accept="video/mp4,video/avi,video/quicktime" onChange={handleVideoSelect} className="hidden" />
            <div className="w-12 h-12 rounded-2xl bg-emerald-100 text-emerald-600 flex items-center justify-center mb-3">
              <UploadCloud className="w-6 h-6" />
            </div>
            <p className="text-sm font-semibold text-slate-800">Upload Simulation Video File</p>
            <p className="text-xs text-slate-400 mt-1">Supports MP4, AVI, MOV up to 100MB</p>
          </label>
        ) : (
          <div className="space-y-4">
            <div className="rounded-2xl overflow-hidden bg-slate-900 border border-slate-800 max-h-[440px] flex items-center justify-center">
              <video src={videoUrl!} controls className="max-h-[440px] w-auto mx-auto" />
            </div>

            <div className="flex items-center justify-between text-xs border-t border-slate-100 pt-4">
              <span className="font-semibold text-slate-700">File: {videoFile.name}</span>
              <button
                onClick={() => {
                  setVideoFile(null);
                  setVideoUrl(null);
                }}
                className="text-red-600 font-semibold hover:underline"
              >
                Change Video
              </button>
            </div>
          </div>
        )}
      </div>
    </div>
  );
};
