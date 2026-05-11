import { useState, useEffect } from 'react';
import { BarChart, Bar, XAxis, YAxis, CartesianGrid, ResponsiveContainer, Cell } from 'recharts';
import type { GitBenchData } from '../../lib/types';
import { loadData } from '../../lib/load-data';
import ModelSelector from './ModelSelector';

function getColor(passRate: number): string {
  if (passRate >= 0.8) return 'var(--pass)';
  if (passRate >= 0.5) return 'var(--warn)';
  return 'var(--fail)';
}

export default function PassRateBarChart() {
  const [data, setData] = useState<GitBenchData | null>(null);
  const [selectedModels, setSelectedModels] = useState<string[]>([]);

  useEffect(() => {
    loadData().then(d => {
      setData(d);
      setSelectedModels(d.models.map(m => m.name));
    });
  }, []);

  if (!data) return <div>Loading...</div>;

  const chartData = selectedModels
    .map(name => {
      const summary = data.model_summaries[name];
      if (!summary) return null;
      return {
        name,
        passRate: Math.round(summary.pass_at_k * 1000) / 10,
        raw: summary.pass_at_k,
      };
    })
    .filter((d): d is NonNullable<typeof d> => d !== null)
    .sort((a, b) => b.passRate - a.passRate);

  return (
    <div>
      <ModelSelector
        initialSelected={selectedModels}
        onChange={setSelectedModels}
      />
      <div className="card">
        <ResponsiveContainer width="100%" height={Math.max(200, chartData.length * 32)}>
          <BarChart
            data={chartData}
            layout="vertical"
            margin={{ top: 5, right: 30, left: 20, bottom: 5 }}
          >
            <CartesianGrid horizontal={false} stroke="rgba(255,255,255,0.04)" />
            <XAxis
              type="number"
              domain={[0, 100]}
              tick={{ fill: 'var(--text-dim)', fontSize: 11, fontFamily: 'var(--font-mono)' }}
              tickFormatter={(v: number) => `${v}%`}
              axisLine={false}
              tickLine={false}
            />
            <YAxis
              type="category"
              dataKey="name"
              tick={{ fill: 'var(--text-mid)', fontSize: 11, fontFamily: 'var(--font-mono)' }}
              axisLine={false}
              tickLine={false}
              width={140}
            />
            <Bar dataKey="passRate" radius={[0, 4, 4, 0]} barSize={16}>
              {chartData.map((entry, index) => (
                <Cell key={index} fill={getColor(entry.raw)} />
              ))}
            </Bar>
          </BarChart>
        </ResponsiveContainer>
      </div>
    </div>
  );
}
