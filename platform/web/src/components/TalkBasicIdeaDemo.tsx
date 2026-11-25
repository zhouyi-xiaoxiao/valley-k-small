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

function normalizeWalk(
  walk: BasicDemoPayload['walks'][number],
  target: BasicDemoPayload['target'],
) {
  const firstHitIndex = walk.steps.findIndex((step) => step.x === target.x && step.y === target.y);
  const hitStep = firstHitIndex >= 0 ? firstHitIndex : walk.steps.length - 1;
  return {
    id: walk.id,
    frames: walk.steps.slice(0, hitStep + 1),
    hitStep,
  };
}

export function TalkBasicIdeaDemo({ lang, payload }: TalkBasicIdeaDemoProps) {
  const [trialIndex, setTrialIndex] = useState(0);
  const [stepIndex, setStepIndex] = useState(0);
  const [counts, setCounts] = useState<Record<number, number>>({});
  const [paused, setPaused] = useState(0);
  const [reducedMotion, setReducedMotion] = useState(false);

  const normalizedWalks = useMemo(
    () => payload.walks.map((walk) => normalizeWalk(walk, payload.target)),
    [payload.target, payload.walks],
  );
  const hits = useMemo(
    () => normalizedWalks.map((walk) => walk.hitStep).sort((a, b) => a - b),
    [normalizedWalks],
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
      setTrialIndex(normalizedWalks.length - 1);
      setStepIndex(normalizedWalks[normalizedWalks.length - 1]?.hitStep ?? 0);
      return;
    }

    const timer = window.setInterval(() => {
      if (paused > 0) {
        setPaused((value) => value - 1);
        return;
      }

      const walk = normalizedWalks[trialIndex];
      if (!walk) {
        setCounts({});
        setTrialIndex(0);
        setStepIndex(0);
        setPaused(4);
        return;
      }

      if (stepIndex < walk.hitStep) {
        setStepIndex((value) => value + 1);
        return;
      }

      setCounts((current) => ({
        ...current,
        [walk.hitStep]: (current[walk.hitStep] ?? 0) + 1,
      }));
      setTrialIndex((value) => value + 1);
      setStepIndex(0);
      setPaused(2);
    }, 180);

    return () => window.clearInterval(timer);
  }, [hits, normalizedWalks, paused, reducedMotion, stepIndex, trialIndex]);

  const currentWalk = normalizedWalks[Math.min(trialIndex, normalizedWalks.length - 1)];
  const currentSteps = currentWalk?.frames.slice(0, Math.min(stepIndex + 1, currentWalk.frames.length)) ?? [];
  const currentPoint = currentSteps[currentSteps.length - 1] ?? payload.source;
  const maxCount = Math.max(...bins.map((bin) => counts[bin] ?? 0), 1);

  return (
    <div className="talk-basic-demo">
      <div className="talk-basic-grid">
        <div className="talk-basic-panel">
          <svg
            viewBox={`0 0 ${payload.grid_width * 72} ${payload.grid_height * 72}`}
            className="talk-basic-svg"
            role="img"
            aria-label={localize(lang, 'Random walk reaching a target', '随机游走到达目标')}
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
              {localize(lang, 'start', '起点')}
            </text>
            <text x={payload.target.x * 72 - 4} y={payload.target.y * 72 + 14} className="talk-basic-label">
              {localize(lang, 'target', '目标')}
            </text>
          </svg>
        </div>

        <div className="talk-basic-panel">
          <div className="talk-basic-copy">
            <h3>{localize(lang, 'Repeated trials build the distribution', '重复多次，就得到分布')}</h3>
            <p className="muted">
              {localize(
                lang,
                'Every time the walker first lands on the target, we record that hitting time once.',
                '游走者每次第一次到达目标，我们就记下这一次的到达时刻。',
              )}
            </p>
          </div>
          <div className="talk-basic-histogram">
            {bins.map((bin) => (
              <div key={bin} className="talk-basic-bar-group">
                <div
                  className="talk-basic-bar"
                  style={{ height: `${((counts[bin] ?? 0) / maxCount) * 100}%` }}
                />
                <span>{bin}</span>
              </div>
            ))}
          </div>
          <p className="muted">
            {localize(
              lang,
              'Bars: how many trials first reached the target at each step (step number below).',
              '柱高：在该步第一次到达目标的试验次数（下方数字为步数）。',
            )}
          </p>
          <p className="talk-basic-callout">
            {localize(
              lang,
              'First-passage time means the first hit, not the average time spent near the target.',
              '首达时间只看第一次到达，而不是在目标附近平均停留多久。',
            )}
          </p>
        </div>
      </div>
    </div>
  );
}
