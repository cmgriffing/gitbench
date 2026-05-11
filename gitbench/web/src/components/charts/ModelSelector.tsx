import { useState, useEffect, useCallback } from 'react';
import type { GitBenchData, ModelInfo } from '../../lib/types';
import { loadData } from '../../lib/load-data';

interface ModelSelectorProps {
  initialSelected?: string[];
  onChange?: (selected: string[]) => void;
}

export default function ModelSelector({ initialSelected, onChange }: ModelSelectorProps) {
  const [models, setModels] = useState<ModelInfo[]>([]);
  const [selected, setSelected] = useState<Set<string>>(new Set(initialSelected || []));

  useEffect(() => {
    loadData().then(data => {
      setModels(data.models);
      if (!initialSelected || initialSelected.length === 0) {
        setSelected(new Set(data.models.map(m => m.name)));
      }
    });
  }, []);

  useEffect(() => {
    if (initialSelected && initialSelected.length > 0) {
      setSelected(new Set(initialSelected));
    }
  }, [initialSelected?.join(',')]);

  const toggle = useCallback((name: string) => {
    setSelected(prev => {
      const next = new Set(prev);
      if (next.has(name)) {
        next.delete(name);
      } else {
        next.add(name);
      }
      const arr = Array.from(next);
      onChange?.(arr);
      return next;
    });
  }, [onChange]);

  const selectAll = () => {
    const all = models.map(m => m.name);
    setSelected(new Set(all));
    onChange?.(all);
  };

  const clearAll = () => {
    setSelected(new Set());
    onChange?.([]);
  };

  return (
    <div style={{ marginBottom: '1rem', display: 'flex', flexWrap: 'wrap', gap: '0.3rem', alignItems: 'center' }}>
      {models.map(m => (
        <label
          key={m.name}
          className={`tag-pill ${selected.has(m.name) ? '' : ''}`}
          style={{
            cursor: 'pointer',
            opacity: selected.has(m.name) ? 1 : 0.4,
            borderColor: selected.has(m.name) ? 'var(--border-accent)' : undefined,
          }}
        >
          <input
            type="checkbox"
            checked={selected.has(m.name)}
            onChange={() => toggle(m.name)}
            style={{ display: 'none' }}
          />
          {m.name}
        </label>
      ))}
      <button
        onClick={selectAll}
        style={{
          fontFamily: 'var(--font-mono)',
          fontSize: '0.6rem',
          background: 'none',
          border: '1px solid var(--border)',
          color: 'var(--text-dim)',
          borderRadius: '4px',
          padding: '0.2rem 0.5rem',
          cursor: 'pointer',
          marginLeft: '0.25rem',
        }}
      >
        All
      </button>
      <button
        onClick={clearAll}
        style={{
          fontFamily: 'var(--font-mono)',
          fontSize: '0.6rem',
          background: 'none',
          border: '1px solid var(--border)',
          color: 'var(--text-dim)',
          borderRadius: '4px',
          padding: '0.2rem 0.5rem',
          cursor: 'pointer',
        }}
      >
        None
      </button>
    </div>
  );
}
