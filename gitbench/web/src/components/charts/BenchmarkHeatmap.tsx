import { useState, useEffect } from 'react';
import type { GitBenchData } from '../../lib/types';
import { loadData } from '../../lib/load-data';
import ModelSelector from './ModelSelector';

function heatBg(ratio: number): string {
  if (ratio >= 0.9) return 'rgba(16,185,129,0.28)';
  if (ratio >= 0.8) return 'rgba(16,185,129,0.18)';
  if (ratio >= 0.7) return 'rgba(245,158,11,0.18)';
  if (ratio >= 0.5) return 'rgba(245,158,11,0.12)';
  return 'rgba(244,63,94,0.15)';
}

function heatColor(ratio: number): string {
  if (ratio >= 0.8) return 'var(--pass)';
  if (ratio >= 0.5) return 'var(--warn)';
  return 'var(--fail)';
}

export default function BenchmarkHeatmap() {
  const [data, setData] = useState<GitBenchData | null>(null);
  const [selectedModels, setSelectedModels] = useState<string[]>([]);

  useEffect(() => {
    loadData().then(d => {
      setData(d);
      setSelectedModels(d.models.map(m => m.name));
    });
  }, []);

  if (!data) return <div>Loading...</div>;

  return (
    <div>
      <ModelSelector
        initialSelected={selectedModels}
        onChange={setSelectedModels}
      />
      <div className="card" style={{ overflowX: 'auto', padding: '1.25rem' }}>
        <table className="data-table">
          <thead>
            <tr>
              <th>Benchmark</th>
              {selectedModels.map(m => (
                <th key={m}>
                  <a
                    href={`/models/${encodeURIComponent(m)}`}
                    style={{ color: 'inherit', textDecoration: 'none' }}
                  >
                    {m}
                  </a>
                </th>
              ))}
            </tr>
          </thead>
          <tbody>
            {data.benchmarks.map(bench => (
              <tr key={bench}>
                <td style={{ fontFamily: 'var(--font-mono)', fontSize: '0.75rem', color: 'var(--text-mid)' }}>
                  <a
                    href={`/benchmarks/${bench}`}
                    style={{ color: 'inherit', textDecoration: 'none' }}
                  >
                    {bench}
                  </a>
                </td>
                {selectedModels.map(m => {
                  const cell = data.matrix[m]?.[bench];
                  if (!cell) {
                    return (
                      <td key={m}>
                        <span style={{ color: 'var(--text-dim)', opacity: 0.4, fontFamily: 'var(--font-mono)', fontSize: '0.75rem' }}>—</span>
                      </td>
                    );
                  }
                  return (
                    <td key={m}>
                      <a
                        href={`/benchmarks/${bench}`}
                        style={{ textDecoration: 'none' }}
                      >
                        <span
                          className="heat-pill"
                          style={{
                            background: heatBg(cell.pass_at_k),
                            color: heatColor(cell.pass_at_k),
                            border: `1px solid ${heatColor(cell.pass_at_k)}33`,
                          }}
                        >
                          {Math.round(cell.pass_at_k * 1000) / 10}%
                        </span>
                        <span style={{
                          fontFamily: 'var(--font-mono)',
                          fontSize: '0.65rem',
                          color: 'var(--text-dim)',
                          marginLeft: '0.3rem',
                        }}>
                          {cell.passed}/{cell.total}
                        </span>
                      </a>
                    </td>
                  );
                })}
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  );
}
