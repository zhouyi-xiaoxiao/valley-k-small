'use client';

import { useEffect, useMemo, useState } from 'react';
import type { Lang, RingDemoPayload } from '@/types';

type TalkRingDemoProps = {
  lang: Lang;
  payload: RingDemoPayload;
};

function localize(lang: Lang, en: string, cn: string) {
  return lang === 'cn' ? cn : en;
}

function pointOnRing(index: number, total: number, radius: number, center: number) {
  const angle = -Math.PI / 2 + ((Math.PI * 2 * index) / total);
  return {
    x: center + radius * Math.cos(angle),
    y: center + radius * Math.sin(angle),
  };
}

function interpolate(points: Array<{ x: number; y: number }>, progress: number) {
  if (points.length <= 1) {
    return points[0] ?? { x: 0, y: 0 };
  }
  const scaled = progress * (points.length - 1);
  const index = Math.min(points.length - 2, Math.floor(scaled));
  const frac = scaled - index;
  const start = points[index];
  const end = points[index + 1];
  return {
    x: start.x + (end.x - start.x) * frac,
    y: start.y + (end.y - start.y) * frac,
  };
}

function linePath(xValues: number[], yValues: number[], width: number, height: number, padding = 24) {
  const minX = Math.min(...xValues);
  const maxX = Math.max(...xValues);
  const maxY = Math.max(...yValues, 1e-6);
  const points = xValues.map((value, index) => ({
    x: padding + ((width - padding * 2) * (value - minX)) / Math.max(1, maxX - minX),
    y: height - padding - ((height - padding * 2) * yValues[index]) / maxY,
  }));
  if (points.length <= 1) {
    return points.length === 1 ? `M ${points[0].x.toFixed(2)} ${points[0].y.toFixed(2)}` : '';
  }
  let path = `M ${points[0].x.toFixed(2)} ${points[0].y.toFixed(2)}`;
  for (let index = 0; index < points.length - 1; index += 1) {
    const current = points[index];
    const next = points[index + 1];
    const midX = (current.x + next.x) / 2;
    const midY = (current.y + next.y) / 2;
    path += ` Q ${current.x.toFixed(2)} ${current.y.toFixed(2)} ${midX.toFixed(2)} ${midY.toFixed(2)}`;
  }
  const last = points[points.length - 1];
  path += ` T ${last.x.toFixed(2)} ${last.y.toFixed(2)}`;
  return path;
}

function projectPoint(
  valueX: number,
  valueY: number,
  xValues: number[],
  yValues: number[],
  width: number,
  height: number,
  padding = 24,
) {
  const minX = Math.min(...xValues);
  const maxX = Math.max(...xValues);
  const maxY = Math.max(...yValues, 1e-6);
  return {
    x: padding + ((width - padding * 2) * (valueX - minX)) / Math.max(1, maxX - minX),
    y: height - padding - ((height - padding * 2) * valueY) / maxY,
  };
}

export function TalkRingDemo({ lang, payload }: TalkRingDemoProps) {
  const [selectedId, setSelectedId] = useState(
    payload.presets.find((preset) => preset.id === 'bimodal')?.id ?? payload.presets[0]?.id ?? '',
  );
  const [progress, setProgress] = useState(0);
  const [reducedMotion, setReducedMotion] = useState(false);

  const selected = payload.presets.find((preset) => preset.id === selectedId) ?? payload.presets[0];

  useEffect(() => {
    if (typeof window === 'undefined') {
      return;
    }
    const media = window.matchMedia('(prefers-reduced-motion: reduce)');
    const sync = () => setReducedMotion(media.matches);
    sync();
    media.addEventListener('change', sync);
    return () => media.removeEventListener('change', sync);
  }, []);

  useEffect(() => {
    setProgress(0);
  }, [selectedId]);

  useEffect(() => {
    if (reducedMotion) {
      setProgress(0.66);
      return;
    }
    const timer = window.setInterval(() => {
      setProgress((value) => {
        const next = value + 0.018;
        return next > 1 ? 0 : next;
      });
    }, 90);
    return () => window.clearInterval(timer);
  }, [reducedMotion, selectedId]);

  const ringNodes = useMemo(
    () => Array.from({ length: payload.ring_size }, (_, index) => pointOnRing(index, payload.ring_size, 118, 144)),
    [payload.ring_size],
  );

  const fastPoints = selected.fast_path.map((index) => ringNodes[index]);
  const slowPoints = selected.slow_path.map((index) => ringNodes[index]);
  const fastDot = interpolate(fastPoints, progress);
  const slowDot = interpolate(slowPoints, Math.min(1, progress * 0.86));
  const sourcePoint = ringNodes[payload.source];
  const targetPoint = ringNodes[payload.target];
  const shortcutStart = ringNodes[payload.shortcut_from];
  const shortcutEnd = ringNodes[selected.dst];
  const curveWidth = 420;
  const curveHeight = 220;
  const curvePath = linePath(selected.curve.times, selected.curve.density, curveWidth, curveHeight, 30);
  const peak1 = projectPoint(
    selected.t1,
    selected.h1,
    selected.curve.times,
    selected.curve.density,
    curveWidth,
    curveHeight,
    30,
  );
  const peak2 =
    selected.t2 && selected.h2
      ? projectPoint(
          selected.t2,
          selected.h2,
          selected.curve.times,
          selected.curve.density,
          curveWidth,
          curveHeight,
          30,
        )
      : null;

  return (
    <div className="talk-ring-stage">
      <div className="talk-preset-list">
        {payload.presets.map((preset) => (
          <button
            key={preset.id}
            type="button"
            className={`talk-preset-button${preset.id === selected.id ? ' active' : ''}`}
            onClick={() => setSelectedId(preset.id)}
          >
            {lang === 'cn' ? preset.label_cn : preset.label_en}
          </button>
        ))}
      </div>

      <div className="talk-demo-grid">
        <div className="talk-demo-panel">
          <svg viewBox="0 0 288 288" className="talk-demo-svg" role="img" aria-label="Ring fast and slow branches">
            <circle cx="144" cy="144" r="118" className="talk-ring-track" />
            {ringNodes.map((point, index) => (
              <circle key={index} cx={point.x} cy={point.y} r="3.2" className="talk-ring-node" />
            ))}
            <path
              d={`M ${shortcutStart.x} ${shortcutStart.y} Q 144 44 ${shortcutEnd.x} ${shortcutEnd.y}`}
              className="talk-ring-shortcut"
            />
            <polyline points={fastPoints.map((point) => `${point.x},${point.y}`).join(' ')} className="talk-ring-fast-path" />
            <polyline points={slowPoints.map((point) => `${point.x},${point.y}`).join(' ')} className="talk-ring-slow-path" />
            <circle cx={sourcePoint.x} cy={sourcePoint.y} r="9" className="talk-ring-source" />
            <circle cx={targetPoint.x} cy={targetPoint.y} r="9" className="talk-ring-target" />
            <circle cx={fastDot.x} cy={fastDot.y} r="7" className="talk-ring-fast-dot" />
            {selected.slow_weight > 0 ? (
              <circle cx={slowDot.x} cy={slowDot.y} r="6.5" className="talk-ring-slow-dot" />
            ) : null}
            <text x={sourcePoint.x - 18} y={sourcePoint.y - 16} className="talk-ring-label">source</text>
            <text x={targetPoint.x - 18} y={targetPoint.y - 16} className="talk-ring-label">target</text>
          </svg>
          <div className="talk-chip-row">
            <div className="talk-metric-chip">
              <strong>{localize(lang, 'shortcut dst', 'shortcut 终点')}</strong>
              <span>{selected.dst}</span>
            </div>
            <div className="talk-metric-chip">
              <strong>{localize(lang, 'fast branch share', '快分支占比')}</strong>
              <span>{Math.round(selected.fast_weight * 100)}%</span>
            </div>
            <div className="talk-metric-chip">
              <strong>{localize(lang, 'late branch share', '慢分支占比')}</strong>
              <span>{Math.round(selected.slow_weight * 1000) / 10}%</span>
            </div>
          </div>
        </div>

        <div className="talk-demo-panel">
          <svg viewBox={`0 0 ${curveWidth} ${curveHeight}`} className="talk-demo-svg" role="img" aria-label="Measured ring timing profile">
            <rect x="0" y="0" width={curveWidth} height={curveHeight} rx="22" fill="#fffdf8" />
            {selected.window ? (
              <rect
                x={projectPoint(selected.window[0], 0, selected.curve.times, selected.curve.density, curveWidth, curveHeight, 30).x}
                y="26"
                width={
                  projectPoint(selected.window[1], 0, selected.curve.times, selected.curve.density, curveWidth, curveHeight, 30).x -
                  projectPoint(selected.window[0], 0, selected.curve.times, selected.curve.density, curveWidth, curveHeight, 30).x
                }
                height={curveHeight - 52}
                fill="rgba(217,119,6,0.12)"
              />
            ) : null}
            <path d={curvePath} fill="none" stroke="#1f2937" strokeWidth="5" />
            <circle cx={peak1.x} cy={peak1.y} r="7" fill="#0f766e" />
            {peak2 ? <circle cx={peak2.x} cy={peak2.y} r="7" fill="#d97706" /> : null}
            <text x={peak1.x + 8} y={peak1.y - 10} className="talk-chart-annotation">t₁</text>
            {peak2 ? <text x={peak2.x + 8} y={peak2.y - 10} className="talk-chart-annotation">t₂</text> : null}
          </svg>
          <p className="talk-callout">{lang === 'cn' ? selected.callout_cn : selected.callout_en}</p>
          <p className="muted">{lang === 'cn' ? selected.summary_cn : selected.summary_en}</p>
        </div>
      </div>
    </div>
  );
}
