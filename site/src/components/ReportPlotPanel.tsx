'use client';

import dynamic from 'next/dynamic';
import { useEffect, useMemo, useState } from 'react';
import type { DatasetMeta, Lang, SeriesPayload } from '@/types';
import { withBasePath } from '@/lib/url';

const Plot = dynamic(() => import('react-plotly.js'), { ssr: false });

type Props = {
  reportId: string;
  datasets: DatasetMeta[];
  lang: Lang;
};

type SeriesType = 'metric' | 'probability' | 'binary' | 'parameter';

type SeriesSemantic = {
  name: string;
  series_type: SeriesType;
  unit: string;
  min: number;
  max: number;
  positive_ratio: number;
  source?: 'declared' | 'inferred';
};

function uniqueStrings(values: string[]): string[] {
  const seen = new Set<string>();
  const out: string[] = [];
  for (const value of values) {
    const normalized = value.trim();
    if (!normalized || seen.has(normalized)) {
      continue;
    }
    seen.add(normalized);
    out.push(normalized);
  }
  return out;
}

export function ReportPlotPanel({ reportId, datasets, lang }: Props) {
  const [selectedId, setSelectedId] = useState<string>(datasets[0]?.series_id ?? '');
  const [payload, setPayload] = useState<SeriesPayload | null>(null);
  const [status, setStatus] = useState<'idle' | 'loading' | 'ready' | 'error'>('idle');
  const [yScale, setYScale] = useState<'linear' | 'log'>('linear');
  const [normalize, setNormalize] = useState<boolean>(false);
  const [smoothWindow, setSmoothWindow] = useState<number>(1);
  const [markers, setMarkers] = useState<boolean>(true);
  const [visibleSeries, setVisibleSeries] = useState<string[]>([]);
  const [autoScaleNotice, setAutoScaleNotice] = useState<string | null>(null);
  const [errorMessage, setErrorMessage] = useState<string | null>(null);

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
      setErrorMessage('Missing dataset path in report metadata.');
      return;
    }
    setStatus('loading');
    setErrorMessage(null);
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
        setErrorMessage(null);
      })
      .catch((err: unknown) => {
        if (err instanceof DOMException && err.name === 'AbortError') {
          return;
        }
        setPayload(null);
        setStatus('error');
        setErrorMessage(err instanceof Error ? err.message : String(err));
      });
    return () => controller.abort();
  }, [selected?.series_path]);

  const semanticAudit = useMemo(() => {
    const out = new Map<string, SeriesSemantic>();
    const missing: string[] = [];
    const conflicts: string[] = [];
    if (!payload) {
      return { map: out, missing, conflicts };
    }
    for (const item of payload.series_semantics ?? []) {
      out.set(item.name, { ...item, source: 'declared' });
    }
    for (const series of payload.series) {
      const declared = out.get(series.name);
      if (declared) {
        const declaredType = (series.series_type || '').trim();
        const declaredUnit = (series.unit || '').trim();
        if (declaredType && declared.series_type && declaredType !== declared.series_type) {
          conflicts.push(`${series.name}: series_type ${declaredType} != ${declared.series_type}`);
        }
        if (declaredUnit && declared.unit && declaredUnit !== declared.unit) {
          conflicts.push(`${series.name}: unit ${declaredUnit} != ${declared.unit}`);
        }
        continue;
      }
      missing.push(series.name);
      const finite = series.y.filter((v) => Number.isFinite(v));
      const min = finite.length > 0 ? Math.min(...finite) : 0;
      const max = finite.length > 0 ? Math.max(...finite) : 0;
      const positiveRatio = finite.length > 0 ? finite.filter((v) => v > 0).length / finite.length : 0;
      out.set(series.name, {
        name: series.name,
        series_type: 'metric',
        unit: 'value',
        min,
        max,
        positive_ratio: positiveRatio,
        source: 'inferred',
      });
    }
    return { map: out, missing, conflicts };
  }, [payload]);
  const semanticsByName = semanticAudit.map;

  useEffect(() => {
    if (!payload || payload.series.length === 0) {
      setVisibleSeries([]);
      return;
    }
    const available = payload.series.map((item) => item.name);
    const preferred = uniqueStrings([
      ...(selected?.default_series ?? []),
      ...(payload.default_series ?? []),
      ...available.filter((name) => {
        const semantic = semanticsByName.get(name);
        return semantic?.series_type === 'metric' || semantic?.series_type === 'probability';
      }),
    ]);
    const seeded = preferred.length > 0 ? preferred : [available[0]];
    const defaults = seeded.filter((name) => available.includes(name));
    setVisibleSeries(defaults.length > 0 ? defaults : [available[0]]);
  }, [payload, selected?.default_series, semanticsByName]);

  const visibleSet = useMemo(() => new Set(visibleSeries), [visibleSeries]);

  const rawVisibleSeries = useMemo(() => {
    if (!payload) {
      return [];
    }
    return payload.series.filter((series) => visibleSet.has(series.name));
  }, [payload, visibleSet]);

  const logEligible = useMemo(() => {
    if (rawVisibleSeries.length === 0) {
      return false;
    }
    return rawVisibleSeries.some((series) => {
      const semantic = semanticsByName.get(series.name);
      const inferred = semantic?.series_type ?? 'metric';
      if (inferred === 'binary' || inferred === 'parameter') {
        return false;
      }
      return series.y.some((value) => value > 0);
    });
  }, [rawVisibleSeries, semanticsByName]);

  useEffect(() => {
    if (!logEligible && yScale === 'log') {
      setYScale('linear');
      setAutoScaleNotice(
        lang === 'cn'
          ? '当前可见序列均不满足 log 条件，已自动切回线性坐标。'
          : 'Visible series do not satisfy log requirements; switched back to linear scale.',
      );
    }
  }, [lang, logEligible, yScale]);

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

    return payload.series
      .filter((series) => visibleSet.has(series.name))
      .map((series) => {
        const semantic = semanticsByName.get(series.name);
        const canTransform = semantic ? semantic.series_type === 'metric' || semantic.series_type === 'probability' : true;
        const smooth = canTransform ? movingAverage(series.y, smoothWindow) : series.y;
        const maxAbs = Math.max(...smooth.map((item) => Math.abs(item)), 1e-12);
        const normalized = canTransform && normalize ? smooth.map((item) => item / maxAbs) : smooth;
        const y = yScale === 'log' ? normalized.map((item) => (item > 0 ? item : null)) : normalized;
        return {
          ...series,
          y,
          series_type: semantic?.series_type ?? 'metric',
          unit: semantic?.unit ?? 'value',
          canTransform,
        };
      });
  }, [normalize, payload, semanticsByName, smoothWindow, visibleSet, yScale]);

  const droppedForLog = useMemo(() => {
    if (yScale !== 'log') {
      return 0;
    }
    return transformed.reduce((acc, series) => acc + series.y.filter((v) => v === null).length, 0);
  }, [transformed, yScale]);

  const perSeriesDrop = useMemo(() => {
    if (yScale !== 'log') {
      return [];
    }
    return transformed.map((series) => {
      const total = Math.max(1, series.y.length);
      const dropped = series.y.filter((v) => v === null).length;
      const ratio = dropped / total;
      return { name: series.name, dropped, total, ratio };
    });
  }, [transformed, yScale]);

  const transformSuppressed = useMemo(
    () => transformed.filter((series) => !series.canTransform).map((series) => series.name),
    [transformed],
  );

  const transformAppliedSeries = useMemo(
    () =>
      transformed
        .filter((series) => series.canTransform && (normalize || smoothWindow > 1))
        .map((series) => series.name),
    [normalize, smoothWindow, transformed],
  );

  const effectiveYLabel = useMemo(() => {
    const parts: string[] = [];
    const visibleCount = transformed.length;
    const transformedCount = transformAppliedSeries.length;
    if (normalize && transformedCount > 0) {
      parts.push(
        transformedCount === visibleCount
          ? lang === 'cn'
            ? '归一化'
            : 'normalized'
          : lang === 'cn'
            ? `归一化 ${transformedCount}/${visibleCount}`
            : `normalized ${transformedCount}/${visibleCount}`,
      );
    }
    if (smoothWindow > 1 && transformedCount > 0) {
      parts.push(
        transformedCount === visibleCount
          ? lang === 'cn'
            ? `平滑 w=${smoothWindow}`
            : `smooth w=${smoothWindow}`
          : lang === 'cn'
            ? `平滑 w=${smoothWindow} (${transformedCount}/${visibleCount})`
            : `smooth w=${smoothWindow} (${transformedCount}/${visibleCount})`,
      );
    }
    if (yScale === 'log' && logEligible) {
      parts.push('log');
    }
    if (parts.length === 0) {
      return selected?.y_label;
    }
    return `${selected?.y_label} (${parts.join(', ')})`;
  }, [lang, logEligible, normalize, selected?.y_label, smoothWindow, transformAppliedSeries, transformed.length, yScale]);

  const applySeriesPreset = (mode: 'metric' | 'all') => {
    if (!payload) {
      return;
    }
    if (mode === 'all') {
      setVisibleSeries(payload.series.map((item) => item.name));
      return;
    }
    const preferred = payload.series
      .map((item) => item.name)
      .filter((name) => {
        const semantic = semanticsByName.get(name);
        return semantic?.series_type === 'metric' || semantic?.series_type === 'probability';
      });
    setVisibleSeries(preferred.length > 0 ? preferred : [payload.series[0].name]);
  };

  const toggleSeries = (name: string, checked: boolean) => {
    setVisibleSeries((prev) => {
      const next = new Set(prev);
      if (checked) {
        next.add(name);
      } else {
        next.delete(name);
      }
      if (next.size === 0) {
        next.add(name);
      }
      return [...next];
    });
  };

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

      {payload ? (
        <details style={{ marginTop: '0.75rem' }}>
          <summary>{lang === 'cn' ? '可见序列与语义' : 'Visible series and semantics'}</summary>
          <div style={{ display: 'flex', gap: '0.5rem', margin: '0.5rem 0 0.7rem', flexWrap: 'wrap' }}>
            <button type="button" onClick={() => applySeriesPreset('metric')}>
              {lang === 'cn' ? '仅指标/概率' : 'Metric/probability only'}
            </button>
            <button type="button" onClick={() => applySeriesPreset('all')}>
              {lang === 'cn' ? '显示全部' : 'Show all'}
            </button>
          </div>
          <div style={{ display: 'grid', gap: '0.35rem' }}>
            {payload.series.map((series) => {
              const semantic = semanticsByName.get(series.name);
              const checked = visibleSet.has(series.name);
              const transformable = semantic
                ? semantic.series_type === 'metric' || semantic.series_type === 'probability'
                : true;
              return (
                <label key={series.name}>
                  <input type="checkbox" checked={checked} onChange={(event) => toggleSeries(series.name, event.target.checked)} />{' '}
                  {series.name}{' '}
                  <span className="badge">
                    {(semantic?.series_type ?? 'metric')}/{semantic?.unit ?? 'value'}
                  </span>
                  <span className="badge">{transformable ? (lang === 'cn' ? '可变换' : 'transformable') : lang === 'cn' ? '原始' : 'raw'}</span>
                </label>
              );
            })}
          </div>
        </details>
      ) : null}

      <details style={{ marginTop: '0.55rem' }}>
        <summary>{lang === 'cn' ? '图表控制' : 'Plot controls'}</summary>
        <div className="plot-controls">
          <label htmlFor="scale-select">{lang === 'cn' ? 'Y 轴' : 'Y scale'}</label>
          <select
            id="scale-select"
            value={yScale}
            onChange={(event) => {
              const nextScale = event.target.value as 'linear' | 'log';
              if (nextScale === 'log' && !logEligible) {
                setAutoScaleNotice(
                  lang === 'cn'
                    ? '当前可见序列没有正值，log 模式不可用。'
                    : 'Log mode is unavailable because visible series contain no positive values.',
                );
                return;
              }
              setYScale(nextScale);
            }}
          >
            <option value="linear">{lang === 'cn' ? '线性' : 'Linear'}</option>
            <option value="log" disabled={!logEligible}>
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
      </details>

      <p>
        <span className="badge">{selected?.x_label}</span> <span className="badge">{effectiveYLabel}</span>
      </p>
      {semanticAudit.missing.length > 0 || semanticAudit.conflicts.length > 0 ? (
        <p style={{ marginBottom: '0.2rem' }}>
          {lang === 'cn'
            ? `语义告警：missing=${semanticAudit.missing.length}, conflicts=${semanticAudit.conflicts.length}。`
            : `Semantic warning: missing=${semanticAudit.missing.length}, conflicts=${semanticAudit.conflicts.length}.`}
          {semanticAudit.missing.length > 0 ? (
            <>
              {' '}
              {lang === 'cn' ? '缺失序列: ' : 'Missing series: '}
              {semanticAudit.missing.slice(0, 3).join(', ')}
              {semanticAudit.missing.length > 3 ? ', …' : ''}
              .
            </>
          ) : null}
          {semanticAudit.conflicts.length > 0 ? (
            <>
              {' '}
              {lang === 'cn' ? '冲突示例: ' : 'Conflict examples: '}
              {semanticAudit.conflicts.slice(0, 2).join(' | ')}
              {semanticAudit.conflicts.length > 2 ? ' | …' : ''}
            </>
          ) : null}
        </p>
      ) : null}
      {transformSuppressed.length > 0 ? (
        <p style={{ marginBottom: '0.2rem' }}>
          {lang === 'cn' ? '以下序列按原始值展示（不做平滑/归一化）: ' : 'These series stay raw (no smoothing/normalization): '}
          {transformSuppressed.join(', ')}
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
        transformed.length > 0 ? (
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
            style={{ width: '100%', height: 'clamp(260px, 45vh, 420px)' }}
            config={{ responsive: true, displaylogo: false, displayModeBar: false }}
            useResizeHandler
          />
        ) : (
          <p>{lang === 'cn' ? '当前没有可见序列，请在上方勾选至少一个。' : 'No visible series. Please enable at least one above.'}</p>
        )
      ) : (
        <p>
          {status === 'error'
            ? lang === 'cn'
              ? `数据加载失败，请切换数据集或重试。当前路径：${selected?.series_path ?? 'unknown'}`
              : `Failed to load dataset. Please switch dataset or retry. Current path: ${selected?.series_path ?? 'unknown'}`
            : lang === 'cn'
              ? '加载图表数据中…'
              : 'Loading plot data…'}
        </p>
      )}
      {status === 'error' && errorMessage ? (
        <details>
          <summary>{lang === 'cn' ? '错误详情' : 'Error details'}</summary>
          <pre style={{ whiteSpace: 'pre-wrap', margin: 0 }}>{errorMessage}</pre>
        </details>
      ) : null}
      <p style={{ marginBottom: 0 }}>
        {lang === 'cn' ? '来源' : 'Provenance'}: <code>{selected?.provenance.source}</code>
      </p>
    </section>
  );
}
