import React, { useEffect, useState } from 'react';
import { BarChart, Bar, XAxis, YAxis, Tooltip, ResponsiveContainer, Cell } from 'recharts';
import { CheckCircle2, AlertOctagon, HelpCircle, Activity, TrendingUp } from 'lucide-react';
import { getAnalytics, getEvents } from '../services/api';
import type { AnalyticsData, EventRecord } from '../types';

export const OverviewPage: React.FC = () => {
  const [analytics, setAnalytics] = useState<AnalyticsData | null>(null);
  const [recentEvents, setRecentEvents] = useState<EventRecord[]>([]);

  useEffect(() => {
    const fetchData = async () => {
      try {
        const [aData, eData] = await Promise.all([
          getAnalytics(),
          getEvents(10)
        ]);
        setAnalytics(aData);
        setRecentEvents(eData);
      } catch (err) {
        console.error('Failed to fetch analytics:', err);
      }
    };
    fetchData();
  }, []);

  const summary = analytics?.summary || {
    total_events: 0,
    correct_events: 0,
    confirmed_violations: 0,
    needs_review_events: 0,
    violation_rate_pct: 0
  };

  const resultChartData = [
    { name: 'Correct Disposal', count: summary.correct_events, color: '#059669' },
    { name: 'Confirmed Violation', count: summary.confirmed_violations, color: '#dc2626' },
    { name: 'Needs Review', count: summary.needs_review_events, color: '#d97706' },
  ];

  const classChartData = analytics?.class_distribution
    ? Object.entries(analytics.class_distribution).slice(0, 8).map(([name, count]) => ({ name, count }))
    : [];

  return (
    <div className="space-y-6">
      {/* Header Banner */}
      <div>
        <h2 className="text-xl font-bold text-slate-800">System Overview & Performance</h2>
        <p className="text-xs text-slate-500">Real-time waste segregation compliance metrics and event stream</p>
      </div>

      {/* KPI Cards */}
      <div className="grid grid-cols-1 md:grid-cols-5 gap-4">
        <div className="bg-white p-4 rounded-xl border border-slate-200 shadow-sm flex items-center justify-between">
          <div>
            <p className="text-xs font-semibold text-slate-500 uppercase">Total Events</p>
            <p className="text-2xl font-black text-slate-800 mt-1">{summary.total_events.toLocaleString()}</p>
          </div>
          <div className="w-10 h-10 rounded-xl bg-slate-100 text-slate-600 flex items-center justify-center">
            <Activity className="w-5 h-5" />
          </div>
        </div>

        <div className="bg-white p-4 rounded-xl border border-slate-200 shadow-sm flex items-center justify-between">
          <div>
            <p className="text-xs font-semibold text-emerald-600 uppercase">Correct Disposals</p>
            <p className="text-2xl font-black text-emerald-700 mt-1">{summary.correct_events.toLocaleString()}</p>
          </div>
          <div className="w-10 h-10 rounded-xl bg-emerald-100 text-emerald-600 flex items-center justify-center">
            <CheckCircle2 className="w-5 h-5" />
          </div>
        </div>

        <div className="bg-white p-4 rounded-xl border border-slate-200 shadow-sm flex items-center justify-between">
          <div>
            <p className="text-xs font-semibold text-red-600 uppercase">Violations</p>
            <p className="text-2xl font-black text-red-700 mt-1">{summary.confirmed_violations.toLocaleString()}</p>
          </div>
          <div className="w-10 h-10 rounded-xl bg-red-100 text-red-600 flex items-center justify-center">
            <AlertOctagon className="w-5 h-5" />
          </div>
        </div>

        <div className="bg-white p-4 rounded-xl border border-slate-200 shadow-sm flex items-center justify-between">
          <div>
            <p className="text-xs font-semibold text-amber-600 uppercase">Needs Review</p>
            <p className="text-2xl font-black text-amber-700 mt-1">{summary.needs_review_events.toLocaleString()}</p>
          </div>
          <div className="w-10 h-10 rounded-xl bg-amber-100 text-amber-600 flex items-center justify-center">
            <HelpCircle className="w-5 h-5" />
          </div>
        </div>

        <div className="bg-white p-4 rounded-xl border border-slate-200 shadow-sm flex items-center justify-between">
          <div>
            <p className="text-xs font-semibold text-slate-500 uppercase">Violation Rate</p>
            <p className="text-2xl font-black text-slate-800 mt-1">{summary.violation_rate_pct}%</p>
          </div>
          <div className="w-10 h-10 rounded-xl bg-slate-100 text-teal-600 flex items-center justify-center">
            <TrendingUp className="w-5 h-5" />
          </div>
        </div>
      </div>

      {/* Charts Row */}
      <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
        <div className="bg-white p-5 rounded-2xl border border-slate-200 shadow-sm">
          <h3 className="text-sm font-bold text-slate-800 mb-4">Compliance Distribution</h3>
          <div className="h-64">
            <ResponsiveContainer width="100%" height="100%">
              <BarChart data={resultChartData}>
                <XAxis dataKey="name" stroke="#64748b" fontSize={11} />
                <YAxis stroke="#64748b" fontSize={11} />
                <Tooltip />
                <Bar dataKey="count" radius={[6, 6, 0, 0]}>
                  {resultChartData.map((entry, index) => (
                    <Cell key={`cell-${index}`} fill={entry.color} />
                  ))}
                </Bar>
              </BarChart>
            </ResponsiveContainer>
          </div>
        </div>

        <div className="bg-white p-5 rounded-2xl border border-slate-200 shadow-sm">
          <h3 className="text-sm font-bold text-slate-800 mb-4">Top Detected Classes</h3>
          <div className="h-64">
            {classChartData.length > 0 ? (
              <ResponsiveContainer width="100%" height="100%">
                <BarChart data={classChartData} layout="vertical">
                  <XAxis type="number" stroke="#64748b" fontSize={11} />
                  <YAxis dataKey="name" type="category" stroke="#64748b" fontSize={10} width={90} />
                  <Tooltip />
                  <Bar dataKey="count" fill="#0d9488" radius={[0, 6, 6, 0]} />
                </BarChart>
              </ResponsiveContainer>
            ) : (
              <div className="flex items-center justify-center h-full text-slate-400 text-xs">
                No detection records found in database.
              </div>
            )}
          </div>
        </div>
      </div>

      {/* Recent Stream Table */}
      <div className="bg-white p-5 rounded-2xl border border-slate-200 shadow-sm">
        <h3 className="text-sm font-bold text-slate-800 mb-3">Recent Disposal Stream</h3>
        {recentEvents.length === 0 ? (
          <p className="text-xs text-slate-400 py-4 text-center">No recent events logged yet.</p>
        ) : (
          <div className="overflow-x-auto">
            <table className="w-full text-left text-xs border-collapse">
              <thead>
                <tr className="border-b border-slate-200 text-slate-500 font-semibold uppercase">
                  <th className="py-2.5 px-3">Timestamp</th>
                  <th className="py-2.5 px-3">Mode</th>
                  <th className="py-2.5 px-3">Class</th>
                  <th className="py-2.5 px-3">Conf</th>
                  <th className="py-2.5 px-3">Bin Target</th>
                  <th className="py-2.5 px-3">Status</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-slate-100">
                {recentEvents.map((evt) => (
                  <tr key={evt.event_id} className="hover:bg-slate-50">
                    <td className="py-2.5 px-3 font-mono text-slate-600">{evt.timestamp}</td>
                    <td className="py-2.5 px-3 text-slate-600">{evt.source_mode}</td>
                    <td className="py-2.5 px-3 font-semibold text-slate-800">{evt.detected_class}</td>
                    <td className="py-2.5 px-3 font-mono">{(evt.confidence * 100).toFixed(0)}%</td>
                    <td className="py-2.5 px-3 text-slate-600">{evt.selected_bin}</td>
                    <td className="py-2.5 px-3">
                      <span
                        className={`px-2 py-0.5 rounded-full text-[10px] font-bold ${
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
