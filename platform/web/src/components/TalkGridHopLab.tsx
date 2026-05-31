'use client';

import { useEffect, useMemo, useState } from 'react';
import type { Lang, TalkSlide } from '@/types';

type Point = { x: number; y: number };
type WalkMode = 'unbiased' | 'east' | 'target';
type TargetMode = 'one' | 'two';

type WalkState = {
  position: Point;
  path: Point[];
  steps: number;
  runSteps: number;
  hits: number;
  lastHit: number | null;
  seed: number;
};

const GRID_SIZE = 13;
const CELL = 42;
const PAD = 48;
const SOURCE: Point = { x: 2, y: 6 };
const TARGET_A: Point = { x: 10, y: 4 };
const TARGET_B: Point = { x: 10, y: 9 };
const SPEEDS = [520, 280, 130];

const MODES: Array<{ id: WalkMode; en: string; cn: string }> = [
  { id: 'unbiased', en: 'Unbiased', cn: '无偏' },
  { id: 'east', en: 'East drift', cn: '向右偏置' },
  { id: 'target', en: 'Target pull', cn: '目标牵引' },
];

function localized(lang: Lang, en: string, cn: string) {
  return lang === 'cn' ? cn : en;
}

function slideTitle(lang: Lang, slide: TalkSlide) {
  return localized(lang, slide.title_en ?? slide.title, slide.title_cn ?? slide.title);
}

function slideSentence(lang: Lang, slide: TalkSlide) {
  return localized(lang, slide.sentence_en ?? slide.sentence, slide.sentence_cn ?? slide.sentence);
}

function initialState(seed = 246813579): WalkState {
  return {
    position: SOURCE,
    path: [SOURCE],
    steps: 0,
    runSteps: 0,
    hits: 0,
    lastHit: null,
    seed,
  };
}

function nextRandom(seed: number) {
  const nextSeed = (seed * 1664525 + 1013904223) >>> 0;
  return { nextSeed, value: nextSeed / 2 ** 32 };
}

function manhattan(a: Point, b: Point) {
  return Math.abs(a.x - b.x) + Math.abs(a.y - b.y);
}

function isSamePoint(a: Point, b: Point) {
  return a.x === b.x && a.y === b.y;
}

function isTarget(point: Point, targetMode: TargetMode) {
  return isSamePoint(point, TARGET_A) || (targetMode === 'two' && isSamePoint(point, TARGET_B));
}

function nearestTargetDistance(point: Point, targetMode: TargetMode) {
  const a = manhattan(point, TARGET_A);
  return targetMode === 'one' ? a : Math.min(a, manhattan(point, TARGET_B));
}

function clampPoint(point: Point): Point {
  return {
    x: Math.max(0, Math.min(GRID_SIZE - 1, point.x)),
    y: Math.max(0, Math.min(GRID_SIZE - 1, point.y)),
  };
}

function chooseNext(state: WalkState, mode: WalkMode, targetMode: TargetMode): WalkState {
  const directions = [
    { dx: 1, dy: 0, label: 'E' },
    { dx: -1, dy: 0, label: 'W' },
    { dx: 0, dy: 1, label: 'S' },
    { dx: 0, dy: -1, label: 'N' },
  ];
  const currentDistance = nearestTargetDistance(state.position, targetMode);
  const weighted = directions.map((direction) => {
    const next = clampPoint({ x: state.position.x + direction.dx, y: state.position.y + direction.dy });
    let weight = 1;
    if (mode === 'east') {
      weight = direction.label === 'E' ? 3.2 : 1;
    }
    if (mode === 'target') {
      const improvement = currentDistance - nearestTargetDistance(next, targetMode);
      weight = improvement > 0 ? 4 : improvement === 0 ? 1.2 : 0.45;
    }
    if (isSamePoint(next, state.position)) {
      weight *= 0.25;
    }
    return { next, weight };
  });

  const { nextSeed, value } = nextRandom(state.seed);
  const total = weighted.reduce((sum, item) => sum + item.weight, 0);
  let cursor = value * total;
  const chosen = weighted.find((item) => {
    cursor -= item.weight;
    return cursor <= 0;
  }) ?? weighted[weighted.length - 1];
  const nextPosition = chosen.next;
  const nextRunSteps = state.runSteps + 1;
  const nextSteps = state.steps + 1;

  if (isTarget(nextPosition, targetMode)) {
    return {
      position: SOURCE,
      path: [SOURCE],
      steps: nextSteps,
      runSteps: 0,
      hits: state.hits + 1,
      lastHit: nextRunSteps,
      seed: nextSeed,
    };
  }

  return {
    position: nextPosition,
    path: [...state.path.slice(-70), nextPosition],
    steps: nextSteps,
    runSteps: nextRunSteps,
    hits: state.hits,
    lastHit: state.lastHit,
    seed: nextSeed,
  };
}

function gridToSvg(point: Point) {
  return {
    x: PAD + point.x * CELL,
    y: PAD + point.y * CELL,
  };
}

export function TalkGridHopLab({ lang, slide }: { lang: Lang; slide: TalkSlide }) {
  const [running, setRunning] = useState(true);
  const [speedIndex, setSpeedIndex] = useState(1);
  const [mode, setMode] = useState<WalkMode>('unbiased');
  const [targetMode, setTargetMode] = useState<TargetMode>('two');
  const [state, setState] = useState<WalkState>(() => initialState());

  useEffect(() => {
    if (!running) {
      return;
    }
    const timer = window.setInterval(() => {
      setState((value) => chooseNext(value, mode, targetMode));
    }, SPEEDS[speedIndex]);
    return () => window.clearInterval(timer);
  }, [mode, running, speedIndex, targetMode]);

  const trail = useMemo(
    () => state.path.map((point) => gridToSvg(point)),
    [state.path],
  );
  const walker = gridToSvg(state.position);
  const targetA = gridToSvg(TARGET_A);
  const targetB = gridToSvg(TARGET_B);
  const source = gridToSvg(SOURCE);
  const polyline = trail.map((point) => `${point.x},${point.y}`).join(' ');

  const reset = () => setState((value) => initialState(value.seed + 97));

  return (
    <div className="talk-grid-hop-lab">
      <header className="talk-grid-hop-head">
        <span className="talk-reveal-kicker">{slide.start} - {slide.end}</span>
        <h1>{slideTitle(lang, slide)}</h1>
        <p>{slideSentence(lang, slide)}</p>
      </header>

      <div className="talk-grid-hop-body">
        <section className="talk-grid-hop-board" aria-label={localized(lang, 'Live 2D lattice walk', '实时二维格点游走')}>
          <svg viewBox="0 0 600 600" role="img">
            <rect x="0" y="0" width="600" height="600" fill="#f8faf7" />
            <g className="talk-grid-hop-lines">
              {Array.from({ length: GRID_SIZE }, (_, index) => (
                <line
                  key={`v-${index}`}
                  x1={PAD + index * CELL}
                  x2={PAD + index * CELL}
                  y1={PAD}
                  y2={PAD + (GRID_SIZE - 1) * CELL}
                />
              ))}
              {Array.from({ length: GRID_SIZE }, (_, index) => (
                <line
                  key={`h-${index}`}
                  x1={PAD}
                  x2={PAD + (GRID_SIZE - 1) * CELL}
                  y1={PAD + index * CELL}
                  y2={PAD + index * CELL}
                />
              ))}
            </g>
            <rect
              x={targetA.x - 17}
              y={targetA.y - 17}
              width="34"
              height="34"
              className="talk-grid-hop-target"
            />
            {targetMode === 'two' ? (
              <rect
                x={targetB.x - 17}
                y={targetB.y - 17}
                width="34"
                height="34"
                className="talk-grid-hop-target is-secondary"
              />
            ) : null}
            <circle cx={source.x} cy={source.y} r="13" className="talk-grid-hop-source" />
            <polyline points={polyline} className="talk-grid-hop-trail" />
            {trail.slice(-18).map((point, index, points) => (
              <circle
                key={`${point.x}-${point.y}-${index}`}
                cx={point.x}
                cy={point.y}
                r={3 + (index / Math.max(1, points.length - 1)) * 5}
                className="talk-grid-hop-trace-dot"
              />
            ))}
            <circle cx={walker.x} cy={walker.y} r="18" className="talk-grid-hop-walker" />
            <g className="talk-grid-hop-neighbours">
              <circle cx={walker.x + CELL} cy={walker.y} r="8" />
              <circle cx={walker.x - CELL} cy={walker.y} r="8" />
              <circle cx={walker.x} cy={walker.y + CELL} r="8" />
              <circle cx={walker.x} cy={walker.y - CELL} r="8" />
            </g>
          </svg>
        </section>

        <aside className="talk-grid-hop-panel">
          <div className="talk-grid-hop-stats" aria-live="polite">
            <div>
              <span>{localized(lang, 'step', '步数')}</span>
              <strong>{state.steps}</strong>
            </div>
            <div>
              <span>{localized(lang, 'current run', '当前 run')}</span>
              <strong>{state.runSteps}</strong>
            </div>
            <div>
              <span>{localized(lang, 'hits', '命中')}</span>
              <strong>{state.hits}</strong>
            </div>
            <div>
              <span>{localized(lang, 'last FPT', '上次 FPT')}</span>
              <strong>{state.lastHit ?? '--'}</strong>
            </div>
          </div>

          <div className="talk-grid-hop-controls">
            <div className="talk-grid-hop-button-row">
              <button type="button" onClick={() => setRunning((value) => !value)}>
                {running ? localized(lang, 'Pause', '暂停') : localized(lang, 'Play', '播放')}
              </button>
              <button type="button" onClick={reset}>
                {localized(lang, 'Reset', '重置')}
              </button>
            </div>

            <label className="talk-grid-hop-slider">
              <span>{localized(lang, 'speed', '速度')}</span>
              <input
                type="range"
                min="0"
                max="2"
                step="1"
                value={speedIndex}
                onChange={(event) => setSpeedIndex(Number(event.currentTarget.value))}
              />
            </label>

            <div className="talk-grid-hop-segments" aria-label={localized(lang, 'Jump rule', '跳动规则')}>
              {MODES.map((item) => (
                <button
                  key={item.id}
                  type="button"
                  className={item.id === mode ? 'is-active' : ''}
                  onClick={() => setMode(item.id)}
                >
                  {localized(lang, item.en, item.cn)}
                </button>
              ))}
            </div>

            <div className="talk-grid-hop-toggle" aria-label={localized(lang, 'Target count', '目标数量')}>
              <button
                type="button"
                className={targetMode === 'one' ? 'is-active' : ''}
                onClick={() => setTargetMode('one')}
              >
                {localized(lang, '1 target', '1 个目标')}
              </button>
              <button
                type="button"
                className={targetMode === 'two' ? 'is-active' : ''}
                onClick={() => setTargetMode('two')}
              >
                {localized(lang, '2 targets', '2 个目标')}
              </button>
            </div>
          </div>

          <p className="talk-grid-hop-reading">
            {localized(
              lang,
              'The curve later called f(t) is just many copies of this local jump process, stopped when a target is hit.',
              '之后叫作 f(t) 的曲线，本质上就是许多条这样的局部跳动过程，在命中目标时停止并计数。',
            )}
          </p>
        </aside>
      </div>
    </div>
  );
}
