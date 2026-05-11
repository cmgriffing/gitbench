import { useState, useEffect } from 'react';
import { ScatterChart, Scatter, XAxis, YAxis, CartesianGrid, ResponsiveContainer, Tooltip, ZAxis } from 'recharts';
import type { GitBenchData } from '../../lib/types';
import { loadData } from '../../lib/load-data';

interface Props {
  modelA?: string;
  modelB?: string;
}

function dotColor(aPassed: boolean, bPassed: boolean): string {
  if (aPassed && bPassed) return '#10b981';
  if (!aPassed && !bPassed) return '#f43f5e';
  return '#f59e0b';
}

export default function ScatterPlot({ modelA, modelB }: Props) {
  const [data, setData] = useState<GitBenchData | null>(null);
  const [a, setA] = useState(modelA || '');
  const [b, setB] = useState(modelB || '');

  useEffect(() => {
    loadData().then(d => {
      setData(d);
      if (!modelA) setA(d.models[0]?.name || '');
      if (!modelB) setB(d.models[1]?.name || d.models[0]?.name || '');
    });
  }, []);

  if (!data || !a || !b) return <div>Loading...</div>;

  // Collect per-fixture similarities for both models
  const aFixtures = data.fixtures[a] || {};
  const bFixtures = data.fixtures[b] || {};

  const scatterData: { x: number; y: number; fixture: string; aPassed: boolean; bPassed: boolean }[] = [];

  for (const bench of data.benchmarks) {
    const aResults = aFixtures[bench] || [];
    const bResults = bFixtures[bench] || [];
    for (const ar of aResults) {
      const br = bResults.find(r => r.fixture_id === ar.fixture_id);
      if (br) {
        scatterData.push({
          x: Math.round(ar.similarity * 1000) / 10,
          y: Math.round(br.similarity * 1000) / 10,
          fixture: `${bench}/${ar.fixture_id}`,
          aPassed: ar.passed,
          bPassed: br.passed,
        });
      }
    }
  }

  // Agreement matrix
  let bothPass = 0, bothFail = 0, aOnly = 0, bOnly = 0;
  for (const d of scatterData) {
    if (d.aPassed && d.bPassed) bothPass++;
    else if (!d.aPassed && !d.bPassed) bothFail++;
    else if (d.aPassed) aOnly++;
    else bOnly++;
  }

  const modelNames = data.models.map(m => m.name);

  return (
    <div>
      <div style={{ display: 'flex', gap: '1rem', marginBottom: '1rem', flexWrap: 'wrap', alignItems: 'center' }}>
        <label style={{ fontFamily: 'var(--font-mono)', fontSize: '0.72rem', color: 'var(--text-dim)' }}>
          X:{' '}
          <select
            value={a}
            onChange={e => setA(e.target.value)}
            style={{
              background: 'var(--card)',
              color: 'var(--text)',
              border: '1px solid var(--border)',
              borderRadius: '4px',
              padding: '0.25rem 0.5rem',
              fontFamily: 'var(--font-mono)',
              fontSize: '0.72rem',
            }}
          >
            {modelNames.map(m => <option key={m} value={m}>{m}</option>)}
          </select>
        </label>
        <label style={{ fontFamily: 'var(--font-mono)', fontSize: '0.72rem', color: 'var(--text-dim)' }}>
          Y:{' '}
          <select
            value={b}
            onChange={e => setB(e.target.value)}
            style={{
              background: 'var(--card)',
              color: 'var(--text)',
              border: '1px solid var(--border)',
              borderRadius: '4px',
              padding: '0.25rem 0.5rem',
              fontFamily: 'var(--font-mono)',
              fontSize: '0.72rem',
            }}
          >
            {modelNames.map(m => <option key={m} value={m}>{m}</option>)}
          </select>
        </label>
      </div>

      <div className="card" style={{ marginBottom: '1rem' }}>
        <ResponsiveContainer width="100%" height={340}>
          <ScatterChart margin={{ top: 20, right: 20, bottom: 20, left: 20 }}>
            <CartesianGrid stroke="rgba(255,255,255,0.04)" />
            <XAxis
              type="number"
              dataKey="x"
              name={a}
              domain={[0, 100]}
              tick={{ fill: 'var(--text-dim)', fontSize: 11, fontFamily: 'var(--font-mono)' }}
              tickFormatter={(v: number) => `${v}%`}
              axisLine={false}
              tickLine={false}
              label={{ value: `${a} similarity`, position: 'bottom', fill: 'var(--text-dim)', fontSize: 11, fontFamily: 'var(--font-mono)' }}
            />
            <YAxis
              type="number"
              dataKey="y"
              name={b}
              domain={[0, 100]}
              tick={{ fill: 'var(--text-dim)', fontSize: 11, fontFamily: 'var(--font-mono)' }}
              tickFormatter={(v: number) => `${v}%`}
              axisLine={false}
              tickLine={false}
              label={{ value: `${b} similarity`, angle: -90, position: 'left', fill: 'var(--text-dim)', fontSize: 11, fontFamily: 'var(--font-mono)' }}
            />
            <ZAxis range={[30, 30]} />
            <Tooltip
              contentStyle={{
                background: 'var(--card)',
                border: '1px solid var(--border)',
                borderRadius: '8px',
                fontFamily: 'var(--font-mono)',
                fontSize: '0.72rem',
                color: 'var(--text)',
              }}
              formatter={(value: number, name: string) => [`${value}%`, name]}
            />
            <Scatter
              data={scatterData}
              fill="#8884d8"
              shape={(props: any) => {
                const { cx, cy, payload } = props;
                return (
                  <a href={`/fixtures/${encodeURIComponent(payload.fixture.split('/')[0])}/${payload.fixture.split('/')[1]}`}>
                    <circle
                      cx={cx}
                      cy={cy}
                      r={4}
                      fill={dotColor(payload.aPassed, payload.bPassed)}
                      opacity={0.7}
                      style={{ cursor: 'pointer' }}
                    />
                  </a>
                );
              }}
              isAnimationActive={false}
            />
          </ScatterChart>
        </ResponsiveContainer>
      </div>

      <div className="card" style={{ marginBottom: '1rem' }}>
        <div className="section-label"><span>Agreement Matrix</span></div>
        <table className="data-table" style={{ maxWidth: '400px' }}>
          <thead>
            <tr>
              <th></th>
              <th>{b} pass</th>
              <th>{b} fail</th>
            </tr>
          </thead>
          <tbody>
            <tr>
              <td style={{ fontFamily: 'var(--font-mono)', fontSize: '0.75rem', color: 'var(--text-mid)' }}>{a} pass</td>
              <td style={{ color: 'var(--pass)', fontFamily: 'var(--font-mono)', fontSize: '0.85rem', fontWeight: 600 }}>{bothPass}</td>
              <td style={{ color: 'var(--warn)', fontFamily: 'var(--font-mono)', fontSize: '0.85rem', fontWeight: 600 }}>{aOnly}</td>
            </tr>
            <tr>
              <td style={{ fontFamily: 'var(--font-mono)', fontSize: '0.75rem', color: 'var(--text-mid)' }}>{a} fail</td>
              <td style={{ color: 'var(--warn)', fontFamily: 'var(--font-mono)', fontSize: '0.85rem', fontWeight: 600 }}>{bOnly}</td>
              <td style={{ color: 'var(--fail)', fontFamily: 'var(--font-mono)', fontSize: '0.85rem', fontWeight: 600 }}>{bothFail}</td>
            </tr>
          </tbody>
        </table>
      </div>

      {scatterData.length > 0 && (
        <div className="card">
          <div className="section-label"><span>Per-Fixture Detail</span></div>
          <table className="data-table">
            <thead>
              <tr>
                <th>Benchmark</th>
                <th>Fixture</th>
                <th>{a}</th>
                <th>{b}</th>
              </tr>
            </thead>
            <tbody>
              {scatterData.map(d => {
                const [bench, fid] = d.fixture.split('/');
                return (
                  <tr key={d.fixture}>
                    <td style={{ fontFamily: 'var(--font-mono)', fontSize: '0.72rem', color: 'var(--text-mid)' }}>
                      <a href={`/benchmarks/${bench}`} style={{ color: 'inherit' }}>{bench}</a>
                    </td>
                    <td>
                      <a href={`/fixtures/${encodeURIComponent(bench)}/${fid}`} className="heat-pill" style={{
                        background: 'rgba(255,255,255,0.04)',
                        color: 'var(--text-mid)',
                        border: '1px solid var(--border)',
                        textDecoration: 'none',
                      }}>{fid}</a>
                    </td>
                    <td>
                      <span className="result-pill pass" style={{ opacity: d.aPassed ? 1 : 0.3 }}>{d.x}%</span>
                    </td>
                    <td>
                      <span className="result-pill pass" style={{ opacity: d.bPassed ? 1 : 0.3 }}>{d.y}%</span>
                    </td>
                  </tr>
                );
              })}
            </tbody>
          </table>
        </div>
      )}
    </div>
  );
}
