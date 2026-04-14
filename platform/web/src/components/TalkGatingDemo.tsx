'use client';

import { useEffect, useState } from 'react';
import type { GatingDemoPayload, Lang } from '@/types';

type TalkGatingDemoProps = {
  lang: Lang;
  payload: GatingDemoPayload;
};

function localize(lang: Lang, en: string, cn: string) {
  return lang === 'cn' ? cn : en;
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

export function TalkGatingDemo({ lang, payload }: TalkGatingDemoProps) {
  const [selectedId, setSelectedId] = useState(payload.windows[0]?.id ?? '');
  const [progress, setProgress] = useState(0);
  const [reducedMotion, setReducedMotion] = useState(false);

  const selected = payload.windows.find((window) => window.id === selectedId) ?? payload.windows[0];

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
      setProgress(0.78);
      return;
    }
    const timer = window.setInterval(() => {
      setProgress((value) => {
        const next = value + 0.016;
        return next > 1 ? 0 : next;
      });
    }, 100);
    return () => window.clearInterval(timer);
  }, [reducedMotion, selectedId]);

  const scaleX = 11;
  const scaleY = 16;
  const pad = 26;
  const width = payload.geometry.width * scaleX + pad * 2;
  const height = payload.geometry.height * scaleY + pad * 2;
  const pathPoints = selected.path.map((point) => ({
    x: pad + point.x * scaleX,
    y: pad + (payload.geometry.height - point.y) * scaleY,
  }));
  const dot = interpolate(pathPoints, progress);
  const corridorTop = pad + (payload.geometry.height - payload.geometry.corridor_y_max) * scaleY;
  const corridorHeight =
    (payload.geometry.corridor_y_max - payload.geometry.corridor_y_min + 1) * scaleY;
  const gateX = pad + payload.geometry.gate_x * scaleX;

  return (
    <div className="talk-gating-stage">
      <div className="talk-preset-list">
        {payload.windows.map((window) => (
          <button
            key={window.id}
            type="button"
            className={`talk-preset-button${window.id === selected.id ? ' active' : ''}`}
            onClick={() => setSelectedId(window.id)}
          >
            {lang === 'cn' ? window.label_cn : window.label_en}
          </button>
        ))}
      </div>

      <div className="talk-demo-grid">
        <div className="talk-demo-panel">
          <svg viewBox={`0 0 ${width} ${height}`} className="talk-demo-svg" role="img" aria-label="2D valley mechanism animation">
            <rect x={pad} y={pad} width={payload.geometry.width * scaleX} height={payload.geometry.height * scaleY} rx="20" className="talk-gating-frame" />
            <rect x={pad} y={corridorTop} width={payload.geometry.width * scaleX} height={corridorHeight} rx="18" className="talk-gating-corridor" />
            <line x1={gateX} x2={gateX} y1={pad} y2={pad + payload.geometry.height * scaleY} className="talk-gating-gate" />
            <polyline points={pathPoints.map((point) => `${point.x},${point.y}`).join(' ')} className="talk-gating-path" />
            <circle cx={pad + payload.geometry.source.x * scaleX} cy={pad + (payload.geometry.height - payload.geometry.source.y) * scaleY} r="9" className="talk-ring-source" />
            <circle cx={pad + payload.geometry.target.x * scaleX} cy={pad + (payload.geometry.height - payload.geometry.target.y) * scaleY} r="9" className="talk-ring-target" />
            <circle cx={dot.x} cy={dot.y} r="7" className="talk-gating-dot" />
            <text x={pad + 6} y={corridorTop - 10} className="talk-ring-label">corridor</text>
            <text x={gateX + 8} y={pad + 18} className="talk-ring-label">gate</text>
            <text x={pad + payload.geometry.source.x * scaleX - 12} y={pad + (payload.geometry.height - payload.geometry.source.y) * scaleY - 16} className="talk-ring-label">start</text>
            <text x={pad + payload.geometry.target.x * scaleX - 12} y={pad + (payload.geometry.height - payload.geometry.target.y) * scaleY - 16} className="talk-ring-label">target</text>
          </svg>
          <p className="talk-callout">{lang === 'cn' ? selected.callout_cn : selected.callout_en}</p>
          <p className="muted">{lang === 'cn' ? selected.summary_cn : selected.summary_en}</p>
        </div>

        <div className="talk-demo-panel">
          <div className="talk-window-band">
            {payload.windows.map((window) => (
              <div
                key={window.id}
                className={`talk-window-band-segment${window.id === selected.id ? ' active' : ''}`}
              >
                <span>{window.label_en}</span>
                <strong>{Math.round(window.mean_hit_time)}</strong>
              </div>
            ))}
          </div>

          <div className="talk-budget-card">
            <div className="talk-budget-row">
              <span>corridor</span>
              <div className="talk-budget-bar">
                <div style={{ width: `${selected.corridor_share * 100}%` }} />
              </div>
              <strong>{Math.round(selected.corridor_share * 100)}%</strong>
            </div>
            <div className="talk-budget-row">
              <span>outside</span>
              <div className="talk-budget-bar talk-budget-bar-outside">
                <div style={{ width: `${selected.outside_share * 100}%` }} />
              </div>
              <strong>{Math.round(selected.outside_share * 100)}%</strong>
            </div>
            <div className="talk-budget-row">
              <span>τ_out post</span>
              <div className="talk-budget-bar talk-budget-bar-post">
                <div style={{ width: `${selected.tau_out_post_share * 100}%` }} />
              </div>
              <strong>{Math.round(selected.tau_out_post_share * 100)}%</strong>
            </div>
            <div className="talk-budget-row">
              <span>τ_mem post</span>
              <div className="talk-budget-bar talk-budget-bar-mem">
                <div style={{ width: `${selected.tau_mem_post_share * 100}%` }} />
              </div>
              <strong>{Math.round(selected.tau_mem_post_share * 100)}%</strong>
            </div>
          </div>

          <div className="talk-chip-row">
            <div className="talk-metric-chip">
              <strong>τ_out prob</strong>
              <span>{Math.round(selected.tau_out_prob * 100)}%</span>
            </div>
            <div className="talk-metric-chip">
              <strong>τ_mem prob</strong>
              <span>{Math.round(selected.tau_mem_prob * 100)}%</span>
            </div>
            <div className="talk-metric-chip">
              <strong>{localize(lang, 'outside steps', '外侧步数')}</strong>
              <span>{Math.round(selected.outside_steps)}</span>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}
