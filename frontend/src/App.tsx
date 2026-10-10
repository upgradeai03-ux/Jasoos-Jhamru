import React, { useState, useEffect } from 'react';
import { Sidebar } from './components/Sidebar';
import type { PageId } from './components/Sidebar';
import { Header } from './components/Header';
import { OverviewPage } from './pages/OverviewPage';
import { ImageAnalysisPage } from './pages/ImageAnalysisPage';
import { ScannerPage } from './pages/ScannerPage';
import { VideoSimulationPage } from './pages/VideoSimulationPage';
import { DatasetLabPage } from './pages/DatasetLabPage';
import { EventHistoryPage } from './pages/EventHistoryPage';
import { AnalyticsPage } from './pages/AnalyticsPage';
import { HealthPage } from './pages/HealthPage';
import { SettingsPage } from './pages/SettingsPage';
import { getModelStatus } from './services/api';
import type { ModelStatus } from './types';

export const App: React.FC = () => {
  const [currentPage, setCurrentPage] = useState<PageId>('overview');
  const [selectedBin, setSelectedBin] = useState<'Wet Waste' | 'Dry Waste'>('Dry Waste');
  const [confidenceThreshold, setConfidenceThreshold] = useState<number>(0.35);
  const [audioAlertsEnabled, setAudioAlertsEnabled] = useState<boolean>(true);
  const [modelStatus, setModelStatus] = useState<ModelStatus | null>(null);

  useEffect(() => {
    getModelStatus().then(setModelStatus).catch(console.error);
  }, []);

  const renderCurrentPage = () => {
    switch (currentPage) {
      case 'overview':
        return <OverviewPage />;
      case 'image':
        return <ImageAnalysisPage selectedBin={selectedBin} confidenceThreshold={confidenceThreshold} />;
      case 'scanner':
        return (
          <ScannerPage
            selectedBin={selectedBin}
            confidenceThreshold={confidenceThreshold}
            audioAlertsEnabled={audioAlertsEnabled}
          />
        );
      case 'video':
        return <VideoSimulationPage />;
      case 'dataset':
        return <DatasetLabPage selectedBin={selectedBin} confidenceThreshold={confidenceThreshold} />;
      case 'events':
        return <EventHistoryPage />;
      case 'analytics':
        return <AnalyticsPage />;
      case 'health':
        return <HealthPage />;
      case 'settings':
        return <SettingsPage />;
      default:
        return <OverviewPage />;
    }
  };

  return (
    <div className="flex min-h-screen bg-slate-50 text-slate-800 font-sans antialiased">
      {/* Sidebar Navigation */}
      <Sidebar currentPage={currentPage} onSelectPage={setCurrentPage} />

      {/* Main App Content Area */}
      <div className="flex-1 flex flex-col min-w-0 overflow-y-auto">
        <Header
          selectedBin={selectedBin}
          onBinChange={setSelectedBin}
          confidenceThreshold={confidenceThreshold}
          onConfidenceChange={setConfidenceThreshold}
          audioAlertsEnabled={audioAlertsEnabled}
          onToggleAudio={() => setAudioAlertsEnabled(!audioAlertsEnabled)}
          modelStatus={modelStatus}
        />

        <main className="flex-1 p-8 max-w-7xl w-full mx-auto">
          {renderCurrentPage()}
        </main>
      </div>
    </div>
  );
};

export default App;
