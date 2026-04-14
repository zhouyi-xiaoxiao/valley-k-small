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
            <h3>{localize(lang, 'Repeated trials build the distribution', '重复试验会长出分布')}</h3>
            <p className="muted">
              {localize(
                lang,
                'Every time the walker first lands on the target, we record that hitting time once.',
                '每次 walker 第一次碰到 target，我们只记录这一次命中时间。',
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
          <p className="talk-basic-callout">
            {localize(
              lang,
              'First-passage time means the first hit, not the average time spent near the target.',
              'First-passage time 只看第一次命中，不是看在目标附近平均停留多久。',
            )}
          </p>
        </div>
      </div>
    </div>
  );
}
