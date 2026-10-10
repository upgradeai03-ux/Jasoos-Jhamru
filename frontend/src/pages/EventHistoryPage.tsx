import React, { useEffect, useState } from 'react';
import { Download, Filter, History } from 'lucide-react';
import { getEvents, exportEventsCSVUrl } from '../services/api';
import type { EventRecord } from '../types';

export const EventHistoryPage: React.FC = () => {
  const [events, setEvents] = useState<EventRecord[]>([]);
  const [filterMode, setFilterMode] = useState<string>('All');
  const [filterResult, setFilterResult] = useState<string>('All');

  const fetchEvents = async () => {
    try {
      const data = await getEvents(500, filterMode, filterResult);
      setEvents(data);
    } catch (e) {
      console.error('Failed to load events:', e);
    }
  };

  useEffect(() => {
    fetchEvents();
  }, [filterMode, filterResult]);

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex flex-wrap items-center justify-between gap-4">
        <div>
          <h2 className="text-xl font-bold text-slate-800">Disposal Event Audit History</h2>
          <p className="text-xs text-slate-500">Persistent SQLite database records of all verified and flagged disposal events</p>
        </div>

        <a
          href={exportEventsCSVUrl()}
          download="wasteguard_event_history.csv"
          className="px-4 py-2 bg-emerald-600 hover:bg-emerald-700 text-white font-semibold text-xs rounded-xl shadow-sm flex items-center space-x-2 transition-all"
        >
          <Download className="w-4 h-4" />
          <span>Export History (CSV)</span>
        </a>
      </div>

      {/* Filter Toolbar */}
      <div className="bg-white p-4 rounded-2xl border border-slate-200 shadow-sm flex flex-wrap items-center gap-4">
        <div className="flex items-center space-x-2 text-xs">
          <Filter className="w-4 h-4 text-slate-400" />
          <span className="font-semibold text-slate-600">Source Mode:</span>
          <select
            value={filterMode}
            onChange={(e) => setFilterMode(e.target.value)}
            className="px-3 py-1.5 bg-slate-50 border border-slate-200 rounded-lg text-xs text-slate-700"
          >
            <option value="All">All Modes</option>
            <option value="Image Upload">Image Upload</option>
            <option value="Live Camera">Live Camera</option>
            <option value="Video Simulation">Video Simulation</option>
            <option value="Dataset Testing">Dataset Testing</option>
          </select>
        </div>

        <div className="flex items-center space-x-2 text-xs">
          <span className="font-semibold text-slate-600">Compliance Result:</span>
          <select
            value={filterResult}
            onChange={(e) => setFilterResult(e.target.value)}
            className="px-3 py-1.5 bg-slate-50 border border-slate-200 rounded-lg text-xs text-slate-700"
          >
            <option value="All">All Results</option>
            <option value="Correct Disposal">Correct Disposal</option>
            <option value="Confirmed Violation">Confirmed Violation</option>
            <option value="Needs Review">Needs Review</option>
          </select>
        </div>

        <span className="text-xs text-slate-400 ml-auto font-mono">
          Showing {events.length} records
        </span>
      </div>

      {/* Table */}
      <div className="bg-white rounded-2xl border border-slate-200 shadow-sm overflow-hidden">
        {events.length === 0 ? (
          <div className="p-8 text-center text-slate-400 text-xs">
            <History className="w-8 h-8 mx-auto mb-2 opacity-40" />
            <p>No matching event logs found in SQLite storage.</p>
          </div>
        ) : (
          <div className="overflow-x-auto">
            <table className="w-full text-left text-xs border-collapse">
              <thead>
                <tr className="bg-slate-50 border-b border-slate-200 text-slate-500 font-semibold uppercase">
                  <th className="py-3 px-4">Event ID</th>
                  <th className="py-3 px-4">Timestamp</th>
                  <th className="py-3 px-4">Mode</th>
                  <th className="py-3 px-4">Detected Item</th>
                  <th className="py-3 px-4">Confidence</th>
                  <th className="py-3 px-4">Bin Target</th>
                  <th className="py-3 px-4">Category</th>
                  <th className="py-3 px-4">Status</th>
                  <th className="py-3 px-4">Audio Alert</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-slate-100">
                {events.map((evt) => (
                  <tr key={evt.event_id} className="hover:bg-slate-50/70 transition-colors">
                    <td className="py-3 px-4 font-mono text-slate-400">#{evt.event_id}</td>
                    <td className="py-3 px-4 font-mono text-slate-600">{evt.timestamp}</td>
                    <td className="py-3 px-4 text-slate-600">{evt.source_mode}</td>
                    <td className="py-3 px-4 font-bold text-slate-800">{evt.detected_class}</td>
                    <td className="py-3 px-4 font-mono">{(evt.confidence * 100).toFixed(1)}%</td>
                    <td className="py-3 px-4 text-slate-600">{evt.selected_bin}</td>
                    <td className="py-3 px-4 text-slate-600">{evt.rule_category}</td>
                    <td className="py-3 px-4">
                      <span
                        className={`px-2.5 py-0.5 rounded-full text-[10px] font-bold ${
                          evt.rule_result === 'Confirmed Violation'
                            ? 'bg-red-100 text-red-700'
                            : evt.rule_result === 'Correct Disposal'
                            ? 'bg-emerald-100 text-emerald-700'
                            : 'bg-amber-100 text-amber-700'
                        }`}
                      >
                        {evt.rule_result}
                      </span>
                    </td>
                    <td className="py-3 px-4 font-mono text-[11px] text-slate-500">{evt.alert_status}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        )}
      </div>
    </div>
  );
};
