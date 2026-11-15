import { loadSeriesPayload } from '@/lib/content';

// The exact f(t) behind Fig. 1 of ring_lazy_jump_ext_rev2, drawn on a log time
// axis so that the early and the late arrivals are both visible. Pure SVG,
// rendered at build time; nothing here depends on scripts running.

const W = 560;
const H = 250;
const PAD = { left: 18, right: 14, top: 16, bottom: 34 };

type Point = { t: number; y: number };

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
  const payload = loadSeriesPayload('ring_lazy_jump_ext_rev2', 'ft_beta0-01');
  const series = payload?.series.find((row) => row.name === 'f_K4');
  if (!series || series.y.length < 10) {
    return null;
  }
  const xs = series.x.map((value) => Number(value));
  const points = sample(xs, series.y, 260);
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

  const line = points.map((p, i) => `${i === 0 ? 'M' : 'L'}${sx(p.t).toFixed(1)},${sy(p.y).toFixed(1)}`).join(' ');
  const area = (from: number, to: number) => {
    const part = points.slice(from, to + 1);
    const top = part.map((p, i) => `${i === 0 ? 'M' : 'L'}${sx(p.t).toFixed(1)},${sy(p.y).toFixed(1)}`).join(' ');
    return `${top} L${sx(part[part.length - 1].t).toFixed(1)},${sy(0).toFixed(1)} L${sx(part[0].t).toFixed(1)},${sy(0).toFixed(1)} Z`;
  };
  const ticks = [1, 10, 100, 1000].filter((t) => t >= tMin && t <= tMax);
  const early = maxima.length === 2 ? points[maxima[0]] : null;
  const late = maxima.length === 2 ? points[maxima[1]] : null;

  return (
    <figure className="arrival-figure">
      <svg viewBox={`0 0 ${W} ${H}`} role="img" aria-label={`${labels.early}; ${labels.late}`}>
        <path d={area(0, split)} className="arrival-fast" />
        <path d={area(split, points.length - 1)} className="arrival-slow" />
        <path d={line} className="arrival-line" />
        <line x1={PAD.left} x2={W - PAD.right} y1={sy(0)} y2={sy(0)} className="arrival-axis" />
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
