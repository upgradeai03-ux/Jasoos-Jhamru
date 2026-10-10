import React, { useEffect, useState } from 'react';
import { BarChart, Bar, XAxis, YAxis, Tooltip, ResponsiveContainer, PieChart, Pie, Cell } from 'recharts';
import { getAnalytics } from '../services/api';
import type { AnalyticsData } from '../types';

export const AnalyticsPage: React.FC = () => {
  const [analytics, setAnalytics] = useState<AnalyticsData | null>(null);

  useEffect(() => {
    getAnalytics().then(setAnalytics).catch(console.error);
  }, []);

  const classData = analytics?.class_distribution
    ? Object.entries(analytics.class_distribution).map(([name, count]) => ({ name, count }))
    : [];

  const resultData = analytics?.result_distribution
    ? Object.entries(analytics.result_distribution).map(([name, value]) => ({ name, value }))
    : [];

  const COLORS = ['#059669', '#dc2626', '#d97706', '#64748b'];

  return (
    <div className="space-y-6">
      <div>
        <h2 className="text-xl font-bold text-slate-800">Advanced Analytics & Segregation Trends</h2>
        <p className="text-xs text-slate-500">Distribution patterns, frequent contaminants, and waste category statistics</p>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
        {/* Class Distribution Bar Chart */}
        <div className="bg-white p-5 rounded-2xl border border-slate-200 shadow-sm space-y-3">
          <h3 className="text-sm font-bold text-slate-800">Frequency by Waste Class</h3>
          <div className="h-72">
            {classData.length > 0 ? (
              <ResponsiveContainer width="100%" height="100%">
                <BarChart data={classData}>
                  <XAxis dataKey="name" stroke="#64748b" fontSize={10} interval={0} angle={-30} textAnchor="end" height={60} />
                  <YAxis stroke="#64748b" fontSize={11} />
                  <Tooltip />
                  <Bar dataKey="count" fill="#059669" radius={[4, 4, 0, 0]} />
                </BarChart>
              </ResponsiveContainer>
            ) : (
              <div className="flex items-center justify-center h-full text-slate-400 text-xs">
                No class events recorded yet.
              </div>
            )}
          </div>
        </div>

        {/* Compliance Result Pie Chart */}
        <div className="bg-white p-5 rounded-2xl border border-slate-200 shadow-sm space-y-3">
          <h3 className="text-sm font-bold text-slate-800">Compliance Ratio</h3>
          <div className="h-72 flex items-center justify-center">
            {resultData.length > 0 ? (
              <ResponsiveContainer width="100%" height="100%">
                <PieChart>
                  <Pie data={resultData} dataKey="value" nameKey="name" cx="50%" cy="50%" outerRadius={90} label>
                    {resultData.map((_, index) => (
                      <Cell key={`cell-${index}`} fill={COLORS[index % COLORS.length]} />
                    ))}
                  </Pie>
                  <Tooltip />
                </PieChart>
              </ResponsiveContainer>
            ) : (
              <div className="text-slate-400 text-xs">No disposal data recorded.</div>
            )}
          </div>
        </div>
      </div>
    </div>
  );
};
