import React from 'react';
import { ImageUploader } from '../components/ImageUploader';
import type { ImageDetectionResponse } from '../types';

interface ImageAnalysisPageProps {
  selectedBin: 'Wet Waste' | 'Dry Waste';
  confidenceThreshold: number;
}

export const ImageAnalysisPage: React.FC<ImageAnalysisPageProps> = ({
  selectedBin,
  confidenceThreshold
}) => {
  const handleAnalysisComplete = (res: ImageDetectionResponse) => {
    console.log('Analysis completed:', res);
  };

  return (
    <div className="space-y-6 max-w-5xl mx-auto">
      <div>
        <h2 className="text-xl font-bold text-slate-800">Image Waste Inspector</h2>
        <p className="text-xs text-slate-500">
          Upload any waste material photo to test real-time object detection and target bin rule evaluation.
        </p>
      </div>

      <ImageUploader
        selectedBin={selectedBin}
        confidenceThreshold={confidenceThreshold}
        onAnalysisComplete={handleAnalysisComplete}
      />
    </div>
  );
};
