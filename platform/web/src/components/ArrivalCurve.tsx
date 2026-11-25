import fs from 'fs';
import path from 'path';
import { loadSeriesPayload } from '@/lib/content';

// The computed f(t) behind Fig. 1 of ring_lazy_jump_ext_rev2 (K = 4, beta = 0.01),
// drawn on a log time axis so that the early and the late arrivals are both
// visible. The height is f(t) itself; the two arrival groups are told apart by
// the colour of the curve, not by shaded areas (on a log axis the area under
// f(t) is not probability). Pure SVG, rendered at build time.

const W = 560;
const H = 260;
const PAD = { left: 44, right: 14, top: 18, bottom: 34 };

const REPORT_ID = 'ring_lazy_jump_ext_rev2';
const CSV_REL = path.join('research', 'reports', REPORT_ID, 'artifacts', 'data', 'ft_beta0.01.csv');
const COLUMN = 'f_K4';

type Point = { t: number; y: number };

// Full series from the report's data file (t = 1 … 4000); falls back to the
// web payload, which is capped at fewer points.
function loadSeries(): { xs: number[]; ys: number[] } | null {
  const file = path.join(process.cwd(), '..', '..', CSV_REL);
  if (fs.existsSync(file)) {
    const lines = fs.readFileSync(file, 'utf-8').trim().split(/\r?\n/);
    const header = lines[0].split(',');
    const ti = header.indexOf('t');
    const yi = header.indexOf(COLUMN);
    if (ti >= 0 && yi >= 0) {
      const xs: number[] = [];
      const ys: number[] = [];
      for (const line of lines.slice(1)) {
        const cells = line.split(',');
        const t = Number(cells[ti]);
        const y = Number(cells[yi]);
        if (Number.isFinite(t) && Number.isFinite(y)) {
          xs.push(t);
          ys.push(y);
        }
      }
      if (xs.length >= 10) {
        return { xs, ys };
      }
    }
  }
  const payload = loadSeriesPayload(REPORT_ID, 'ft_beta0-01');
  const series = payload?.series.find((row) => row.name === COLUMN);
  if (!series || series.y.length < 10) {
    return null;
  }
  return { xs: series.x.map((value) => Number(value)), ys: series.y };
}

function sample(xs: number[], ys: number[], count: number): Point[] {
  const tMin = Math.max(1, xs[0]);
  const tMax = xs[xs.length - 1];
  const points: Point[] = [];
  let lastT = -1;
  for (let i = 0; i < count; i += 1) {
    const target = Math.exp(Math.log(tMin) + ((Math.log(tMax) - Math.log(tMin)) * i) / (count - 1));
    const t = Math.round(target);
    if (t === lastT) {
      continue;
    }
    lastT = t;
    const idx = Math.min(xs.length - 1, Math.max(0, t - Math.round(xs[0])));
    points.push({ t: xs[idx], y: ys[idx] });
  }
  return points;
}

function localMaxima(points: Point[]): number[] {
  const out: number[] = [];
  for (let i = 1; i < points.length - 1; i += 1) {
    if (points[i].y > points[i - 1].y && points[i].y >= points[i + 1].y) {
      out.push(i);
    }
  }
  return out;
}

export function ArrivalCurve({ labels }: { labels: { early: string; late: string; axis: string } }) {
  const data = loadSeries();
  if (!data) {
    return null;
  }
  const points = sample(data.xs, data.ys, 300);
  const yMax = Math.max(...points.map((p) => p.y)) * 1.1;
  const tMin = points[0].t;
  const tMax = points[points.length - 1].t;
  const sx = (t: number) =>
    PAD.left + ((Math.log(t) - Math.log(tMin)) / (Math.log(tMax) - Math.log(tMin))) * (W - PAD.left - PAD.right);
  const sy = (y: number) => H - PAD.bottom - (y / yMax) * (H - PAD.top - PAD.bottom);

  // The two highest humps and the lowest point between them.
  const maxima = localMaxima(points)
    .sort((a, b) => points[b].y - points[a].y)
    .slice(0, 2)
    .sort((a, b) => a - b);
  let split = Math.floor(points.length / 2);
  if (maxima.length === 2) {
    split = maxima[0];
    for (let i = maxima[0]; i <= maxima[1]; i += 1) {
      if (points[i].y < points[split].y) {
        split = i;
      }
    }
  }

  const path2 = (part: Point[]) =>
    part.map((p, i) => `${i === 0 ? 'M' : 'L'}${sx(p.t).toFixed(1)},${sy(p.y).toFixed(1)}`).join(' ');
  const ticks = [1, 10, 100, 1000].filter((t) => t >= tMin && t <= tMax);
  const early = maxima.length === 2 ? points[maxima[0]] : null;
  const late = maxima.length === 2 ? points[maxima[1]] : null;

  return (
    <figure className="arrival-figure">
      <svg viewBox={`0 0 ${W} ${H}`} role="img" aria-label={`f(t), ${labels.axis}: ${labels.early}; ${labels.late}`}>
        <line x1={PAD.left} x2={W - PAD.right} y1={sy(0)} y2={sy(0)} className="arrival-axis" />
        <line x1={PAD.left} x2={PAD.left} y1={sy(0)} y2={PAD.top} className="arrival-axis" />
        <text x={PAD.left - 8} y={PAD.top + 10} textAnchor="end" className="arrival-tick arrival-ylabel">
          f(t)
        </text>
        <text x={PAD.left - 8} y={sy(0) + 5} textAnchor="end" className="arrival-tick">
          0
        </text>
        <path d={path2(points.slice(0, split + 1))} className="arrival-line arrival-line-fast" />
        <path d={path2(points.slice(split))} className="arrival-line arrival-line-slow" />
        {ticks.map((t) => (
          <g key={t}>
            <line x1={sx(t)} x2={sx(t)} y1={sy(0)} y2={sy(0) + 5} className="arrival-axis" />
            <text x={sx(t)} y={H - 10} textAnchor="middle" className="arrival-tick">
              {t}
            </text>
          </g>
        ))}
        {early ? <circle cx={sx(early.t)} cy={sy(early.y)} r={4.5} className="arrival-dot-fast" /> : null}
        {late ? <circle cx={sx(late.t)} cy={sy(late.y)} r={4.5} className="arrival-dot-slow" /> : null}
      </svg>
      <div className="arrival-legend">
        <span>
          <i className="swatch swatch-fast" aria-hidden="true" />
          {labels.early}
        </span>
        <span>
          <i className="swatch swatch-slow" aria-hidden="true" />
          {labels.late}
        </span>
        <span className="arrival-axis-label">{labels.axis}</span>
      </div>
    </figure>
  );
}
