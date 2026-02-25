'use client';

import dynamic from 'next/dynamic';
import { useEffect, useMemo, useState } from 'react';
import type { DatasetMeta, SeriesPayload } from '@/types';
import type { Lang } from '@/types';
import { withBasePath } from '@/lib/url';

const Plot = dynamic(() => import('react-plotly.js'), { ssr: false });

type Props = {
  reportId: string;
  datasets: DatasetMeta[];
  lang: Lang;
};

export function ReportPlotPanel({ reportId, datasets, lang }: Props) {
  const [selectedId, setSelectedId] = useState<string>(datasets[0]?.series_id ?? '');
  const [payload, setPayload] = useState<SeriesPayload | null>(null);
  const [status, setStatus] = useState<'idle' | 'loading' | 'ready' | 'error'>('idle');
  const [yScale, setYScale] = useState<'linear' | 'log'>('linear');
  const [normalize, setNormalize] = useState<boolean>(false);
  const [smoothWindow, setSmoothWindow] = useState<number>(1);
  const [markers, setMarkers] = useState<boolean>(true);
  const [autoScaleNotice, setAutoScaleNotice] = useState<string | null>(null);

  const selected = useMemo(
    () => datasets.find((item) => item.series_id === selectedId) ?? datasets[0],
    [datasets, selectedId],
  );

  useEffect(() => {
    setAutoScaleNotice(null);
  }, [selected?.series_id]);

  useEffect(() => {
    if (!selected?.series_path) {
      setPayload(null);
      setStatus('error');
      return;
    }
    setStatus('loading');
    const controller = new AbortController();
    fetch(withBasePath(selected.series_path), { signal: controller.signal })
      .then((res) => {
        if (!res.ok) {
          throw new Error(`Failed to load dataset: ${selected.series_path}`);
        }
        return res.json() as Promise<SeriesPayload>;
      })
      .then((json) => {
        setPayload(json);
        setStatus('ready');
      })
      .catch((err: unknown) => {
        if (err instanceof DOMException && err.name === 'AbortError') {
          return;
        }
        setPayload(null);
        setStatus('error');
      });

    return () => controller.abort();
  }, [selected?.series_path]);

  const transformed = useMemo(() => {
    if (!payload) {
      return [];
    }

    const movingAverage = (values: number[], windowSize: number): number[] => {
      if (windowSize <= 1) {
        return values;
      }
      const half = Math.floor(windowSize / 2);
      return values.map((_, index) => {
        const start = Math.max(0, index - half);
        const end = Math.min(values.length, index + half + 1);
        const slice = values.slice(start, end);
        const sum = slice.reduce((acc, value) => acc + value, 0);
        return sum / Math.max(1, slice.length);
      });
    };

    return payload.series.map((series) => {
      const smooth = movingAverage(series.y, smoothWindow);
      const maxAbs = Math.max(...smooth.map((item) => Math.abs(item)), 1e-12);
      const normalized = normalize ? smooth.map((item) => item / maxAbs) : smooth;
      const y = yScale === 'log' ? normalized.map((item) => (item > 0 ? item : null)) : normalized;
      return {
        ...series,
        y,
      };
    });
  }, [normalize, payload, smoothWindow, yScale]);

  const logBlocked = useMemo(() => {
    if (!payload) {
      return false;
    }
    return payload.series.some((series) => series.y.some((value) => value <= 0));
  }, [payload]);

  const droppedForLog = useMemo(() => {
    if (yScale !== 'log') {
      return 0;
    }
    return transformed.reduce((acc, series) => acc + series.y.filter((v) => v === null).length, 0);
  }, [transformed, yScale]);

  const perSeriesDrop = useMemo(() => {
    if (yScale !== 'log' || !payload) {
      return [];
    }
    return transformed.map((series, idx) => {
      const total = Math.max(1, payload.series[idx]?.y.length ?? 1);
      const dropped = series.y.filter((v) => v === null).length;
      const ratio = dropped / total;
      return { name: series.name, dropped, total, ratio };
    });
  }, [payload, transformed, yScale]);

  const allDroppedInLog = useMemo(() => {
    if (yScale !== 'log' || transformed.length === 0) {
      return false;
    }
    return transformed.every((series) => series.y.every((point) => point === null));
  }, [transformed, yScale]);

  useEffect(() => {
    if (logBlocked && yScale === 'log') {
      setYScale('linear');
      setAutoScaleNotice(
        lang === 'cn'
          ? '检测到非正值数据，log 模式已禁用并自动切回线性坐标。'
          : 'Detected non-positive values. Log mode is disabled and the plot was switched back to linear scale.',
      );
    }
  }, [lang, logBlocked, yScale]);

  useEffect(() => {
    if (allDroppedInLog && yScale === 'log') {
      setYScale('linear');
      setAutoScaleNotice(
        lang === 'cn'
          ? 'log 模式下全部数据点被隐藏，已自动切回线性坐标。'
          : 'All points were hidden in log mode, automatically switched back to linear scale.',
      );
    }
  }, [allDroppedInLog, lang, yScale]);

  const effectiveYLabel = useMemo(() => {
    const parts: string[] = [];
    if (normalize) {
      parts.push(lang === 'cn' ? '归一化' : 'normalized');
    }
    if (smoothWindow > 1) {
      parts.push(lang === 'cn' ? `平滑w=${smoothWindow}` : `smooth w=${smoothWindow}`);
    }
    if (yScale === 'log') {
      parts.push('log');
    }
    if (parts.length === 0) {
      return selected?.y_label;
    }
    return `${selected?.y_label} (${parts.join(', ')})`;
  }, [lang, normalize, selected?.y_label, smoothWindow, yScale]);

  if (datasets.length === 0) {
    return <p>{lang === 'cn' ? `${reportId} 暂无可交互数据集。` : `No interactive datasets are available for ${reportId}.`}</p>;
  }

  return (
    <section className="card section-enter">
      <h3>{lang === 'cn' ? '交互数据面板' : 'Interactive Dataset'}</h3>
      <label htmlFor="dataset-select">{lang === 'cn' ? '数据集' : 'Dataset'}</label>
      <select
        id="dataset-select"
        value={selected?.series_id}
        onChange={(event) => setSelectedId(event.target.value)}
        style={{ marginLeft: '0.6rem' }}
      >
        {datasets.map((item) => (
          <option key={item.series_id} value={item.series_id}>
            {item.title}
          </option>
        ))}
      </select>
      <div className="plot-controls">
        <label htmlFor="scale-select">{lang === 'cn' ? 'Y 轴' : 'Y scale'}</label>
        <select
          id="scale-select"
          value={yScale}
          onChange={(event) => {
            const nextScale = event.target.value as 'linear' | 'log';
            if (nextScale === 'log' && logBlocked) {
              setAutoScaleNotice(
                lang === 'cn'
                  ? '当前数据含非正值，log 模式不可用。'
                  : 'Log scale is unavailable because this dataset includes non-positive values.',
              );
              return;
            }
            setYScale(nextScale);
          }}
        >
          <option value="linear">{lang === 'cn' ? '线性' : 'Linear'}</option>
          <option value="log" disabled={logBlocked}>
            {lang === 'cn' ? '对数' : 'Log'}
          </option>
        </select>
        <label htmlFor="smooth-range">{lang === 'cn' ? '平滑' : 'Smoothing'}</label>
        <input
          id="smooth-range"
          type="range"
          min={1}
          max={15}
          step={2}
          value={smoothWindow}
          onChange={(event) => setSmoothWindow(Number(event.target.value))}
        />
        <span className="badge">{lang === 'cn' ? `窗口=${smoothWindow}` : `window=${smoothWindow}`}</span>
        <label>
          <input type="checkbox" checked={normalize} onChange={(event) => setNormalize(event.target.checked)} />{' '}
          {lang === 'cn' ? '归一化' : 'Normalize'}
        </label>
        <label>
          <input type="checkbox" checked={markers} onChange={(event) => setMarkers(event.target.checked)} />{' '}
          {lang === 'cn' ? '标记点' : 'Markers'}
        </label>
      </div>
      <p>
        <span className="badge">{selected?.x_label}</span> <span className="badge">{effectiveYLabel}</span>
      </p>
      {logBlocked ? (
        <p style={{ marginBottom: '0.2rem' }}>
          {lang === 'cn'
            ? '提示：当前数据包含非正值，log 模式已禁用。'
            : 'Note: this dataset includes non-positive values, so log mode is disabled.'}
        </p>
      ) : null}
      {droppedForLog > 0 ? (
        <p style={{ marginBottom: '0.2rem' }}>
          {lang === 'cn' ? '提示：log 模式已隐藏非正值点，共 ' : 'Note: log mode hides non-positive points, dropped '}
          <strong>{droppedForLog}</strong>
          {lang === 'cn' ? ' 个。' : '.'}
        </p>
      ) : null}
      {perSeriesDrop.length > 0 ? (
        <div style={{ display: 'flex', flexWrap: 'wrap', gap: '0.45rem', marginBottom: '0.4rem' }}>
          {perSeriesDrop.map((item) => (
            <span key={item.name} className="badge">
              {item.name}: {Math.round(item.ratio * 100)}% {lang === 'cn' ? '隐藏' : 'dropped'}
            </span>
          ))}
        </div>
      ) : null}
      {autoScaleNotice ? <p style={{ marginBottom: '0.2rem' }}>{autoScaleNotice}</p> : null}
      {payload && status === 'ready' ? (
        <Plot
          data={transformed.map((series) => ({
            type: 'scatter',
            mode: markers ? 'lines+markers' : 'lines',
            name: series.name,
            x: series.x,
            y: series.y,
            marker: { size: 4 },
            line: { width: 2.1 },
          }))}
          layout={{
            autosize: true,
            margin: { l: 44, r: 20, t: 18, b: 42 },
            paper_bgcolor: 'rgba(0,0,0,0)',
            plot_bgcolor: '#fffdf8',
            font: { family: 'IBM Plex Serif, Georgia, serif', color: '#1a1f1d' },
            xaxis: { title: selected?.x_label, gridcolor: '#e6dbc7' },
            yaxis: { title: effectiveYLabel, gridcolor: '#e6dbc7', type: yScale },
            legend: { orientation: 'h' },
          }}
          style={{ width: '100%', height: '440px' }}
          config={{ responsive: true, displaylogo: false }}
          useResizeHandler
        />
      ) : (
        <p>
          {status === 'error'
            ? lang === 'cn'
              ? '数据加载失败，请切换数据集或重试。'
              : 'Failed to load dataset. Please switch dataset or retry.'
            : lang === 'cn'
              ? '加载图表数据中…'
              : 'Loading plot data…'}
        </p>
      )}
      <p style={{ marginBottom: 0 }}>
        {lang === 'cn' ? '来源' : 'Provenance'}: <code>{selected?.provenance.source}</code>
      </p>
    </section>
  );
}
