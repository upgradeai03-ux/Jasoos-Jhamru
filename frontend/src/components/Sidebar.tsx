import React from 'react';
import {
  LayoutDashboard,
  Camera,
  UploadCloud,
  Video,
  Database,
  History,
  BarChart3,
  Activity,
  Settings,
  Recycle
} from 'lucide-react';

export type PageId =
  | 'overview'
  | 'scanner'
  | 'image'
  | 'video'
  | 'dataset'
  | 'events'
  | 'analytics'
  | 'health'
  | 'settings';

interface SidebarProps {
  currentPage: PageId;
  onSelectPage: (page: PageId) => void;
}

export const Sidebar: React.FC<SidebarProps> = ({ currentPage, onSelectPage }) => {
  const navItems: { id: PageId; label: string; icon: React.ReactNode }[] = [
    { id: 'overview', label: 'Overview Dashboard', icon: <LayoutDashboard className="w-5 h-5" /> },
    { id: 'image', label: 'Image Analysis', icon: <UploadCloud className="w-5 h-5" /> },
    { id: 'scanner', label: 'AI Live Scanner', icon: <Camera className="w-5 h-5" /> },
    { id: 'video', label: 'Video Simulation', icon: <Video className="w-5 h-5" /> },
    { id: 'dataset', label: 'Dataset Testing Lab', icon: <Database className="w-5 h-5" /> },
    { id: 'events', label: 'Event History', icon: <History className="w-5 h-5" /> },
    { id: 'analytics', label: 'Analytics & Trends', icon: <BarChart3 className="w-5 h-5" /> },
    { id: 'health', label: 'System & Model Health', icon: <Activity className="w-5 h-5" /> },
    { id: 'settings', label: 'Settings', icon: <Settings className="w-5 h-5" /> },
  ];

  return (
    <aside className="w-64 bg-slate-900 text-slate-200 flex flex-col h-screen sticky top-0 border-r border-slate-800 shadow-xl select-none z-30">
      {/* Brand Header */}
      <div className="p-5 border-b border-slate-800 flex items-center space-x-3 bg-slate-950/60">
        <div className="w-10 h-10 rounded-xl bg-gradient-to-br from-emerald-500 to-teal-600 flex items-center justify-center text-white shadow-lg shadow-emerald-900/40">
          <Recycle className="w-6 h-6 animate-spin-slow" />
        </div>
        <div>
          <h1 className="font-bold text-lg text-white tracking-wide">WasteGuard AI</h1>
          <p className="text-xs text-emerald-400 font-medium">Real-Time Segregation System</p>
        </div>
      </div>

      {/* Navigation Links */}
      <nav className="flex-1 px-3 py-4 space-y-1 overflow-y-auto">
        {navItems.map((item) => {
          const isActive = currentPage === item.id;
          return (
            <button
              key={item.id}
              onClick={() => onSelectPage(item.id)}
              className={`w-full flex items-center space-x-3 px-3.5 py-2.5 rounded-lg text-sm font-medium transition-all duration-150 ${
                isActive
                  ? 'bg-emerald-600 text-white shadow-md shadow-emerald-900/30'
                  : 'text-slate-300 hover:bg-slate-800/80 hover:text-white'
              }`}
            >
              <span className={isActive ? 'text-white' : 'text-slate-400'}>{item.icon}</span>
              <span>{item.label}</span>
            </button>
          );
        })}
      </nav>

      {/* Footer Info */}
      <div className="p-4 border-t border-slate-800 text-xs text-slate-500 bg-slate-950/40 text-center">
        <p className="font-semibold text-slate-400">WasteGuard AI v2.0</p>
        <p className="mt-0.5">Environmental Tech AI</p>
      </div>
    </aside>
  );
};
