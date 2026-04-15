'use client';

import { useEffect, useMemo, useState } from 'react';
import type { BasicDemoPayload, Lang } from '@/types';

type TalkBasicIdeaDemoProps = {
  lang: Lang;
  payload: BasicDemoPayload;
};

function localize(lang: Lang, en: string, cn: string) {
  return lang === 'cn' ? cn : en;
}

export function TalkBasicIdeaDemo({ lang, payload }: TalkBasicIdeaDemoProps) {
  const [trialIndex, setTrialIndex] = useState(0);
  const [stepIndex, setStepIndex] = useState(0);
  const [counts, setCounts] = useState<Record<number, number>>({});
  const [paused, setPaused] = useState(0);
  const [reducedMotion, setReducedMotion] = useState(false);

  const hits = useMemo(
    () => payload.walks.map((walk) => walk.hit_step).sort((a, b) => a - b),
    [payload.walks],
  );
  const bins = useMemo(() => Array.from(new Set(hits)), [hits]);

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
    if (reducedMotion) {
      const finalCounts: Record<number, number> = {};
      for (const hit of hits) {
        finalCounts[hit] = (finalCounts[hit] ?? 0) + 1;
      }
      setCounts(finalCounts);
      setTrialIndex(payload.walks.length - 1);
      setStepIndex(payload.walks[payload.walks.length - 1]?.hit_step ?? 0);
      return;
    }

    const timer = window.setInterval(() => {
      if (paused > 0) {
        setPaused((value) => value - 1);
        return;
      }

      const walk = payload.walks[trialIndex];
      if (!walk) {
        setCounts({});
        setTrialIndex(0);
        setStepIndex(0);
        setPaused(4);
        return;
      }

      if (stepIndex < walk.hit_step) {
        setStepIndex((value) => value + 1);
        return;
      }

      setCounts((current) => ({
        ...current,
        [walk.hit_step]: (current[walk.hit_step] ?? 0) + 1,
      }));
      setTrialIndex((value) => value + 1);
      setStepIndex(0);
      setPaused(2);
    }, 180);

    return () => window.clearInterval(timer);
  }, [hits, paused, payload.walks, reducedMotion, stepIndex, trialIndex]);

  const currentWalk = payload.walks[Math.min(trialIndex, payload.walks.length - 1)];
  const currentSteps = currentWalk?.steps.slice(0, Math.min(stepIndex + 1, currentWalk.steps.length)) ?? [];
  const currentPoint = currentSteps[currentSteps.length - 1] ?? payload.source;
  const maxCount = Math.max(...bins.map((bin) => counts[bin] ?? 0), 1);
  const chartWidth = 420;
  const chartHeight = 250;
  const chartPadding = 34;

  return (
    <div className="talk-basic-demo">
      <div className="talk-basic-grid">
        <div className="talk-basic-panel">
          <svg
            viewBox={`0 0 ${payload.grid_width * 72} ${payload.grid_height * 72}`}
            className="talk-basic-svg"
            role="img"
            aria-label="Random walk reaching a target"
          >
            {Array.from({ length: payload.grid_width }).map((_, x) =>
              Array.from({ length: payload.grid_height }).map((__, y) => (
                <rect
                  key={`${x}-${y}`}
                  x={x * 72 + 8}
                  y={y * 72 + 8}
                  width="56"
                  height="56"
                  rx="16"
                  className="talk-basic-cell"
                />
              )),
            )}
            <rect
              x={payload.target.x * 72 + 8}
              y={payload.target.y * 72 + 8}
              width="56"
              height="56"
              rx="16"
              className="talk-basic-target"
            />
            <polyline
              points={currentSteps.map((step) => `${step.x * 72 + 36},${step.y * 72 + 36}`).join(' ')}
              className="talk-basic-path"
            />
            <circle
              cx={payload.source.x * 72 + 36}
              cy={payload.source.y * 72 + 36}
              r="12"
              className="talk-basic-source"
            />
            <circle
              cx={currentPoint.x * 72 + 36}
              cy={currentPoint.y * 72 + 36}
              r="11"
              className="talk-basic-walker"
            />
            <text x={payload.source.x * 72 + 20} y={payload.source.y * 72 + 14} className="talk-basic-label">
              start
            </text>
            <text x={payload.target.x * 72 - 4} y={payload.target.y * 72 + 14} className="talk-basic-label">
              target
            </text>
          </svg>
        </div>

        <div className="talk-basic-panel">
          <div className="talk-basic-copy">
            <h3>{localize(lang, 'Record only the first hit', '只记录第一次命中')}</h3>
            <p className="muted">
              {localize(
                lang,
                'Each trial contributes exactly one number: the step when the walker first reaches the target.',
                '每个 trial 只贡献一个数：walker 第一次到 target 的那个步数。',
              )}
            </p>
          </div>
          <svg
            viewBox={`0 0 ${chartWidth} ${chartHeight}`}
            className="talk-chart-svg"
            role="img"
            aria-label="Accumulating first-hit histogram"
          >
            <rect x="0" y="0" width={chartWidth} height={chartHeight} rx="22" fill="#fffdf8" />
            <line
              x1={chartPadding}
              x2={chartPadding}
              y1={chartPadding - 6}
              y2={chartHeight - chartPadding}
              stroke="rgba(29,41,53,0.22)"
              strokeWidth="2"
            />
            <line
              x1={chartPadding}
              x2={chartWidth - chartPadding + 8}
              y1={chartHeight - chartPadding}
              y2={chartHeight - chartPadding}
              stroke="rgba(29,41,53,0.22)"
              strokeWidth="2"
            />
            {bins.map((bin, index) => {
              const barWidth = (chartWidth - chartPadding * 2) / bins.length - 12;
              const x = chartPadding + index * ((chartWidth - chartPadding * 2) / bins.length) + 6;
              const height =
                ((chartHeight - chartPadding * 2) * (counts[bin] ?? 0)) / Math.max(maxCount, 1);
              const y = chartHeight - chartPadding - height;
              const isCurrent = currentWalk?.hit_step === bin && stepIndex >= currentWalk.hit_step;
              return (
                <g key={bin}>
                  <rect
                    x={x}
                    y={y}
                    width={barWidth}
                    height={Math.max(height, 2)}
                    rx="10"
                    fill={isCurrent ? '#d97706' : '#0f766e'}
                    opacity={isCurrent ? 0.95 : 0.88}
                  />
                  <text x={x + barWidth / 2} y={chartHeight - 10} textAnchor="middle" className="talk-basic-axis-label">
                    {bin}
                  </text>
                </g>
              );
            })}
            <text x={chartPadding} y="22" className="talk-basic-axis-title">
              {localize(lang, 'accumulated first hits', '累计第一次命中')}
            </text>
            <text
              x={chartWidth - chartPadding}
              y="22"
              textAnchor="end"
              className="talk-basic-axis-title"
            >
              {localize(lang, `trial ${Math.min(trialIndex + 1, payload.walks.length)}/${payload.walks.length}`, `试验 ${Math.min(trialIndex + 1, payload.walks.length)}/${payload.walks.length}`)}
            </text>
          </svg>
          <p className="talk-basic-callout">
            {localize(
              lang,
              'First-passage time means the first hit, not the time spent near the target afterward.',
              'First-passage time 只看第一次命中，不看之后在目标附近停留多久。',
            )}
          </p>
        </div>
      </div>
    </div>
  );
}
