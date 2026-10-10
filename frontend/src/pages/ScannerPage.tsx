import React, { useRef, useState, useEffect } from 'react';
import { Camera, StopCircle, AlertTriangle, Volume2 } from 'lucide-react';
import { detectImage } from '../services/api';
import type { ImageDetectionResponse } from '../types';

interface ScannerPageProps {
  selectedBin: 'Wet Waste' | 'Dry Waste';
  confidenceThreshold: number;
  audioAlertsEnabled: boolean;
}

export const ScannerPage: React.FC<ScannerPageProps> = ({
  selectedBin,
  confidenceThreshold,
  audioAlertsEnabled
}) => {
  const [isStreaming, setIsStreaming] = useState<boolean>(false);
  const [currentResult, setCurrentResult] = useState<ImageDetectionResponse | null>(null);
  const [alertBanner, setAlertBanner] = useState<string | null>(null);

  const videoRef = useRef<HTMLVideoElement>(null);
  const canvasRef = useRef<HTMLCanvasElement>(null);
  const streamRef = useRef<MediaStream | null>(null);
  const timerRef = useRef<number | null>(null);

  const playBeep = () => {
    if (!audioAlertsEnabled) return;
    try {
      const ctx = new (window.AudioContext || (window as any).webkitAudioContext)();
      const osc = ctx.createOscillator();
      osc.type = 'sine';
      osc.frequency.setValueAtTime(880, ctx.currentTime);
      osc.connect(ctx.destination);
      osc.start();
      osc.stop(ctx.currentTime + 0.3);
    } catch (e) {
      console.warn('Audio synth failed:', e);
    }
  };

  const startCamera = async () => {
    try {
      const stream = await navigator.mediaDevices.getUserMedia({
        video: { width: { ideal: 640 }, height: { ideal: 480 }, facingMode: 'user' }
      });
      streamRef.current = stream;
      if (videoRef.current) {
        videoRef.current.srcObject = stream;
        await videoRef.current.play();
      }
      setIsStreaming(true);
    } catch (err) {
      console.error('Webcam access error:', err);
      alert('Unable to access webcam. Please verify camera permissions.');
    }
  };

  const stopCamera = () => {
    if (timerRef.current) {
      clearInterval(timerRef.current);
      timerRef.current = null;
    }
    if (streamRef.current) {
      streamRef.current.getTracks().forEach((track) => track.stop());
      streamRef.current = null;
    }
    setIsStreaming(false);
    setCurrentResult(null);
    setAlertBanner(null);
  };

  useEffect(() => {
    if (isStreaming) {
      timerRef.current = window.setInterval(captureAndDetect, 1200);
    } else {
      if (timerRef.current) clearInterval(timerRef.current);
    }
    return () => {
      if (timerRef.current) clearInterval(timerRef.current);
    };
  }, [isStreaming, selectedBin, confidenceThreshold]);

  const captureAndDetect = async () => {
    if (!videoRef.current || !canvasRef.current) return;
    const video = videoRef.current;
    const canvas = canvasRef.current;

    if (video.videoWidth === 0 || video.videoHeight === 0) return;

    canvas.width = video.videoWidth;
    canvas.height = video.videoHeight;
    const ctx = canvas.getContext('2d');
    if (!ctx) return;

    ctx.drawImage(video, 0, 0, canvas.width, canvas.height);

    canvas.toBlob(async (blob) => {
      if (!blob) return;
      const file = new File([blob], 'webcam_frame.jpg', { type: 'image/jpeg' });
      try {
        const res = await detectImage(file, selectedBin, confidenceThreshold, true);
        setCurrentResult(res);

        if (res.has_violation) {
          setAlertBanner(`🚨 VIOLATION DETECTED! Item placed in ${selectedBin}.`);
          playBeep();
        } else {
          setAlertBanner(null);
        }
      } catch (err) {
        console.error('Frame inference error:', err);
      }
    }, 'image/jpeg', 0.85);
  };

  useEffect(() => {
    return () => stopCamera();
  }, []);

  return (
    <div className="space-y-6 max-w-5xl mx-auto">
      <div>
        <h2 className="text-xl font-bold text-slate-800">AI Live Camera Scanner</h2>
        <p className="text-xs text-slate-500">
          Real-time webcam disposal verification feed with automatic violation sound alarms
        </p>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
        {/* Camera Video View */}
        <div className="md:col-span-2 bg-slate-900 rounded-2xl overflow-hidden border border-slate-800 relative min-h-[380px] flex items-center justify-center">
          <video ref={videoRef} className={`w-full h-auto max-h-[460px] object-contain ${!isStreaming ? 'hidden' : ''}`} muted playsInline />
          <canvas ref={canvasRef} className="hidden" />

          {!isStreaming && (
            <div className="text-center p-8 text-slate-400">
              <Camera className="w-12 h-12 mx-auto mb-3 text-slate-600" />
              <p className="text-sm font-semibold text-slate-300">Webcam Inactive</p>
              <p className="text-xs text-slate-500 mt-1 mb-4">Click below to start live segregation scanning</p>
              <button
                onClick={startCamera}
                className="px-6 py-2.5 bg-emerald-600 hover:bg-emerald-700 text-white font-semibold text-xs rounded-xl shadow-lg transition-all"
              >
                Start Camera Feed
              </button>
            </div>
          )}

          {isStreaming && alertBanner && (
            <div className="absolute top-4 left-4 right-4 bg-red-600/90 backdrop-blur-md text-white px-4 py-2.5 rounded-xl font-bold text-xs flex items-center justify-between shadow-xl animate-bounce">
              <div className="flex items-center space-x-2">
                <AlertTriangle className="w-4 h-4 text-white" />
                <span>{alertBanner}</span>
              </div>
              <Volume2 className="w-4 h-4" />
            </div>
          )}
        </div>

        {/* Live Status Controls */}
        <div className="space-y-4">
          <div className="bg-white p-5 rounded-2xl border border-slate-200 shadow-sm space-y-4">
            <h3 className="text-sm font-bold text-slate-800 border-b border-slate-100 pb-2">Scanner State</h3>

            <div>
              <p className="text-xs text-slate-500 font-medium">Target Bin:</p>
              <p className="text-sm font-bold text-emerald-700">{selectedBin}</p>
            </div>

            <div>
              <p className="text-xs text-slate-500 font-medium">Confidence Cutoff:</p>
              <p className="text-sm font-bold text-slate-800">{(confidenceThreshold * 100).toFixed(0)}%</p>
            </div>

            {isStreaming && (
              <button
                onClick={stopCamera}
                className="w-full py-2.5 bg-red-600 hover:bg-red-700 text-white font-semibold text-xs rounded-xl shadow-sm flex items-center justify-center space-x-2 transition-all"
              >
                <StopCircle className="w-4 h-4" />
                <span>Stop Scanner</span>
              </button>
            )}
          </div>

          {currentResult && (
            <div className="bg-white p-5 rounded-2xl border border-slate-200 shadow-sm">
              <h4 className="text-xs font-bold text-slate-700 uppercase tracking-wider mb-2">Live Detection Result</h4>
              <p className="text-xs text-slate-500 mb-2">Found: <strong>{currentResult.total_detected}</strong> objects</p>
              {currentResult.detections.map((d, i) => (
                <div key={i} className="p-2.5 rounded-lg bg-slate-50 border border-slate-100 text-xs my-1">
                  <div className="flex justify-between font-bold">
                    <span>{d.class_name}</span>
                    <span>{(d.confidence * 100).toFixed(0)}%</span>
                  </div>
                  <p className="text-[10px] text-slate-500 mt-0.5">{d.reason}</p>
                </div>
              ))}
            </div>
          )}
        </div>
      </div>
    </div>
  );
};
