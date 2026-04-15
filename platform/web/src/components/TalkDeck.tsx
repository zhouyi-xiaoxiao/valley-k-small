'use client';

import Image from 'next/image';
import { useEffect, useMemo, useState } from 'react';
import { withBasePath } from '@/lib/url';
import { TalkBasicIdeaDemo } from '@/components/TalkBasicIdeaDemo';
import { TalkGatingDemo } from '@/components/TalkGatingDemo';
import { TalkRingDemo } from '@/components/TalkRingDemo';
import type {
  BasicDemoPayload,
  GatingDemoPayload,
  Lang,
  RingDemoPayload,
  SeriesPayload,
  TalkDeckManifest,
  TalkScriptPayload,
  TalkSlide,
  TalkSlideNote,
} from '@/types';

type TalkDeckProps = {
  lang: Lang;
  manifest: TalkDeckManifest;
  scriptEn: TalkScriptPayload;
  scriptCn: TalkScriptPayload;
  basicDemo: BasicDemoPayload;
  ringDemo: RingDemoPayload;
  gatingDemo: GatingDemoPayload;
  ringScanProbability: SeriesPayload | null;
  ringScanTiming: SeriesPayload | null;
};

function localize(lang: Lang, en: string, cn: string) {
  return lang === 'cn' ? cn : en;
}

function slideHash(index: number) {
  return `slide-${index + 1}`;
}

function readSlideIndex(hash: string, slideCount: number) {
  const match = hash.match(/slide-(\d+)/);
  if (!match) {
    return 0;
  }
  const parsed = Number(match[1]) - 1;
  if (!Number.isFinite(parsed)) {
    return 0;
  }
  return Math.max(0, Math.min(slideCount - 1, parsed));
}

function linePath(
  xValues: number[],
  yValues: number[],
  width: number,
  height: number,
  padding = 24,
) {
  if (xValues.length === 0 || yValues.length === 0) {
    return '';
  }
  const minX = Math.min(...xValues);
  const maxX = Math.max(...xValues);
  const maxY = Math.max(...yValues, 1e-6);
  return xValues
    .map((value, index) => {
      const x =
        padding +
        ((width - padding * 2) * (value - minX)) / Math.max(1e-6, maxX - minX);
      const y = height - padding - ((height - padding * 2) * yValues[index]) / maxY;
      return `${index === 0 ? 'M' : 'L'} ${x.toFixed(2)} ${y.toFixed(2)}`;
    })
    .join(' ');
}

function pointInChart(
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
    x:
      padding +
      ((width - padding * 2) * (valueX - minX)) / Math.max(1e-6, maxX - minX),
    y: height - padding - ((height - padding * 2) * valueY) / maxY,
  };
}

function OpeningVisual() {
  return (
    <div className="talk-opening-visual">
      <div className="talk-opening-grid">
        <figure className="talk-opening-tile">
          <figcaption>Single-target ring evidence</figcaption>
          <Image
            unoptimized
            className="talk-opening-image"
            src={withBasePath('/talk-assets/smet-phd/lazy_K2_clean_example_N100.png')}
            alt="Ring example curve with early and delayed structure"
            width={1716}
            height={1038}
          />
        </figure>
        <figure className="talk-opening-tile">
          <figcaption>2D gated geometry</figcaption>
          <Image
            unoptimized
            className="talk-opening-image"
            src={withBasePath('/talk-assets/smet-phd/one_target_gate_geometry.png')}
            alt="One-target gate geometry"
            width={1917}
            height={686}
          />
        </figure>
      </div>
    </div>
  );
}

function ComparisonVisual() {
  const x = Array.from({ length: 140 }, (_, index) => index / 139);
  const gaussian = (value: number, mu: number, sigma: number) =>
    Math.exp(-((value - mu) ** 2) / (2 * sigma ** 2));
  const single = x.map((value) => gaussian(value, 0.48, 0.14));
  const double = x.map(
    (value) => 0.92 * gaussian(value, 0.28, 0.09) + 0.74 * gaussian(value, 0.76, 0.11),
  );
  return (
    <div className="talk-comparison-card">
      <article className="talk-comparison-panel">
        <h3>One dominant route</h3>
        <svg viewBox="0 0 320 180" className="talk-chart-svg" role="img" aria-label="Single peak comparison">
          <path d={linePath(x, single, 320, 180)} fill="none" stroke="#0f766e" strokeWidth="6" />
        </svg>
        <p className="muted">If one arrival route dominates, the distribution keeps one main timescale.</p>
      </article>
      <article className="talk-comparison-panel">
        <h3>Competing routes</h3>
        <svg viewBox="0 0 320 180" className="talk-chart-svg" role="img" aria-label="Double peak comparison">
          <path d={linePath(x, double, 320, 180)} fill="none" stroke="#d97706" strokeWidth="6" />
          <line x1="160" y1="24" x2="160" y2="156" stroke="rgba(29,41,53,0.18)" strokeDasharray="8 6" />
        </svg>
        <p className="muted">A valley appears when fast and slow arrivals no longer share one scale.</p>
      </article>
    </div>
  );
}

function RingScanFigure({
  lang,
  probability,
  timing,
  ringDemo,
}: {
  lang: Lang;
  probability: SeriesPayload | null;
  timing: SeriesPayload | null;
  ringDemo: RingDemoPayload;
}) {
  const primary = probability?.series[0];
  const secondary = timing?.series[0];
  if (!primary || !secondary) {
    return (
      <div className="talk-figure-shell">
        <p>{localize(lang, 'Ring scan data missing.', 'Ring 扫描数据缺失。')}</p>
      </div>
    );
  }

  const chartWidth = 760;
  const chartHeight = 360;
  const primaryX = primary.x.map(Number);
  const primaryY = primary.y;
  const secondaryX = secondary.x.map(Number);
  const secondaryY = secondary.y;
  const insetWidth = 230;
  const insetHeight = 150;

  return (
    <div className="talk-figure-shell">
      <div className="talk-figure-header">
        <h3>{localize(lang, 'Destination Scan Reweights the Fast Branch', '终点扫描会重配快通道')}</h3>
        <p className="muted">
          {localize(
            lang,
            'A route change shifts both peak weight and visibility time. The main curve is the measured first-peak height scan; the inset tracks first-peak timing.',
            '路径配置的变化同时会移动峰权重和峰出现时间。主图是实测第一峰高度扫描，右上角 inset 是第一峰时间扫描。',
          )}
        </p>
      </div>
      <div className="talk-series-stage">
        <svg viewBox={`0 0 ${chartWidth} ${chartHeight}`} className="talk-chart-svg" role="img" aria-label="Ring destination scan">
          <rect x="0" y="0" width={chartWidth} height={chartHeight} rx="24" fill="#fffdf8" />
          <path d={linePath(primaryX, primaryY, chartWidth, chartHeight, 44)} fill="none" stroke="#0f766e" strokeWidth="5" />
          {ringDemo.presets.map((preset) => {
            const point = pointInChart(
              preset.dst,
              preset.h1,
              primaryX,
              primaryY,
              chartWidth,
              chartHeight,
              44,
            );
            return (
              <g key={preset.id}>
                <circle cx={point.x} cy={point.y} r="8" fill={preset.bimodal ? '#d97706' : '#1f2937'} />
                <text x={point.x + 10} y={point.y - 12} className="talk-chart-annotation">
                  {preset.label_en}
                </text>
              </g>
            );
          })}
          <g transform="translate(486,34)">
            <rect x="0" y="0" width={insetWidth} height={insetHeight} rx="18" fill="rgba(255,255,255,0.94)" stroke="rgba(29,41,53,0.12)" />
            <path d={linePath(secondaryX, secondaryY, insetWidth, insetHeight, 18)} fill="none" stroke="#d97706" strokeWidth="4" />
            <text x="18" y="24" className="talk-chart-inset-label">t₁ vs destination</text>
          </g>
        </svg>
      </div>
      <div className="talk-chip-row">
        {ringDemo.presets.map((preset) => (
          <div key={preset.id} className="talk-metric-chip">
            <strong>{preset.label_en}</strong>
            <span>dst={preset.dst}</span>
            <span>
              {preset.t2 ? `t₁=${preset.t1}, t₂=${preset.t2}` : `t₁=${preset.t1}`}
            </span>
          </div>
        ))}
      </div>
    </div>
  );
}

function ImageFigure({
  figure,
  lang,
}: {
  figure: Extract<TalkSlide['evidence'], { kind: 'image' }>;
  lang: Lang;
}) {
  return (
    <div className="talk-figure-shell">
      <Image
        unoptimized
        className="talk-figure-image"
        src={withBasePath(figure.src)}
        alt={lang === 'cn' ? figure.alt_cn : figure.alt_en}
        width={1400}
        height={900}
      />
      <p className="muted talk-figure-caption">
        {lang === 'cn' ? figure.caption_cn : figure.caption_en}
      </p>
    </div>
  );
}

function OutlookVisual({
  lang,
  slide,
}: {
  lang: Lang;
  slide: TalkSlide;
}) {
  const evidence = slide.evidence;
  if (!evidence || evidence.kind !== 'outlook') {
    return null;
  }
  return (
    <div className="talk-outlook-stage">
      <div className="talk-outlook-copy">
        {(lang === 'cn' ? evidence.cards_cn : evidence.cards_en).map((item) => (
          <article key={item} className="talk-outlook-card">
            {item}
          </article>
        ))}
      </div>
      {evidence.image_src ? (
        <div className="talk-outlook-image">
          <Image
            unoptimized
            className="talk-figure-image"
            src={withBasePath(evidence.image_src)}
            alt={lang === 'cn' ? evidence.image_alt_cn ?? '' : evidence.image_alt_en ?? ''}
            width={1200}
            height={680}
          />
        </div>
      ) : null}
    </div>
  );
}

function PresenterPanel({
  slide,
  english,
}: {
  slide: TalkSlide;
  english?: TalkSlideNote;
}) {
  return (
    <aside className="talk-presenter-panel">
      <div className="talk-presenter-block">
        <span className="talk-presenter-label">Timing</span>
        <strong>
          {slide.start} - {slide.end}
        </strong>
        <p className="muted">{english?.timing_prompt ?? ''}</p>
      </div>
      <div className="talk-presenter-block">
        <span className="talk-presenter-label">Audience question</span>
        <p>{slide.question_en}</p>
      </div>
      <div className="talk-presenter-block">
        <span className="talk-presenter-label">English script</span>
        <p>{english?.spoken_text ?? ''}</p>
      </div>
    </aside>
  );
}

export function TalkDeck({
  lang,
  manifest,
  scriptEn,
  scriptCn: _scriptCn,
  basicDemo,
  ringDemo,
  gatingDemo,
  ringScanProbability,
  ringScanTiming,
}: TalkDeckProps) {
  const [currentIndex, setCurrentIndex] = useState(0);
  const [presenterMode, setPresenterMode] = useState(false);
  const [isFullscreen, setIsFullscreen] = useState(false);
  const slides = manifest.slides;

  const englishById = useMemo(
    () => new Map(scriptEn.blocks.map((block) => [block.slide_id, block])),
    [scriptEn.blocks],
  );
  useEffect(() => {
    if (typeof window === 'undefined') {
      return;
    }
    const syncFromHash = () => setCurrentIndex(readSlideIndex(window.location.hash, slides.length));
    syncFromHash();
    window.addEventListener('hashchange', syncFromHash);
    return () => window.removeEventListener('hashchange', syncFromHash);
  }, [slides.length]);

  useEffect(() => {
    if (typeof window === 'undefined') {
      return;
    }
    const hash = `#${slideHash(currentIndex)}`;
    if (window.location.hash !== hash) {
      window.history.replaceState(null, '', hash);
    }
  }, [currentIndex]);

  useEffect(() => {
    if (typeof window === 'undefined') {
      return;
    }
    const onKeyDown = (event: KeyboardEvent) => {
      if (event.key === 'ArrowRight' || event.key === 'PageDown' || event.key === ' ') {
        event.preventDefault();
        setCurrentIndex((value) => Math.min(slides.length - 1, value + 1));
      }
      if (event.key === 'ArrowLeft' || event.key === 'PageUp') {
        event.preventDefault();
        setCurrentIndex((value) => Math.max(0, value - 1));
      }
      if (event.key.toLowerCase() === 'p') {
        setPresenterMode((value) => !value);
      }
    };
    window.addEventListener('keydown', onKeyDown);
    return () => window.removeEventListener('keydown', onKeyDown);
  }, [slides.length]);

  useEffect(() => {
    if (typeof document === 'undefined') {
      return;
    }
    const sync = () => setIsFullscreen(Boolean(document.fullscreenElement));
    sync();
    document.addEventListener('fullscreenchange', sync);
    return () => document.removeEventListener('fullscreenchange', sync);
  }, []);

  const slide = slides[currentIndex];
  const english = englishById.get(slide.id);
  const progressPercent = ((currentIndex + 1) / slides.length) * 100;

  const toggleFullscreen = async () => {
    if (typeof document === 'undefined') {
      return;
    }
    if (document.fullscreenElement) {
      await document.exitFullscreen();
      return;
    }
    await document.documentElement.requestFullscreen();
  };

  const renderVisual = () => {
    if (slide.animation?.kind === 'basic-walk') {
      return <TalkBasicIdeaDemo lang={lang} payload={basicDemo} />;
    }
    if (slide.animation?.kind === 'ring-branches') {
      return <TalkRingDemo lang={lang} payload={ringDemo} />;
    }
    if (slide.animation?.kind === 'valley-budget') {
      return <TalkGatingDemo lang={lang} payload={gatingDemo} />;
    }
    if (slide.id === 'opening') {
      return <OpeningVisual />;
    }
    if (slide.evidence?.kind === 'comparison') {
      return <ComparisonVisual />;
    }
    if (slide.evidence?.kind === 'series') {
      return (
        <RingScanFigure
          lang={lang}
          probability={ringScanProbability}
          timing={ringScanTiming}
          ringDemo={ringDemo}
        />
      );
    }
    if (slide.evidence?.kind === 'image') {
      return <ImageFigure figure={slide.evidence} lang={lang} />;
    }
    if (slide.evidence?.kind === 'outlook') {
      return <OutlookVisual lang={lang} slide={slide} />;
    }
    return null;
  };

  return (
    <main className="talk-deck-page">
      <div className="talk-deck-toolbar">
        <div className="talk-toolbar-left">
          <div className="talk-toolbar-title">
            <strong>{manifest.title_en}</strong>
            <span className="muted">
              {currentIndex + 1}/{slides.length}
            </span>
          </div>
        </div>

        <div className="talk-toolbar-center">
          <div className="talk-progress-bar" aria-hidden="true">
            <div style={{ width: `${progressPercent}%` }} />
          </div>
        </div>

        <div className="talk-toolbar-right">
          <button type="button" onClick={toggleFullscreen}>
            {isFullscreen ? 'Exit full screen' : 'Full screen'}
          </button>
          <button type="button" onClick={() => setPresenterMode((value) => !value)}>
            {presenterMode ? 'Audience mode' : 'Presenter mode'}
          </button>
          <button
            type="button"
            onClick={() => setCurrentIndex((value) => Math.max(0, value - 1))}
            disabled={currentIndex === 0}
          >
            {localize(lang, 'Prev', '上一页')}
          </button>
          <button
            type="button"
            onClick={() => setCurrentIndex((value) => Math.min(slides.length - 1, value + 1))}
            disabled={currentIndex === slides.length - 1}
          >
            {localize(lang, 'Next', '下一页')}
          </button>
        </div>
      </div>

      <section className={`talk-deck-stage${presenterMode ? ' is-presenter' : ''}`}>
        <article className={`talk-slide-card talk-slide-${slide.id}`}>
          {presenterMode ? (
            <div className="talk-slide-topline">
              <span className="talk-slide-kicker">
                {slide.start} - {slide.end}
              </span>
              <span className="talk-slide-question">
                {lang === 'cn' ? slide.question_cn : slide.question_en}
              </span>
            </div>
          ) : null}
          <header className="talk-slide-header">
            <h1>{slide.title}</h1>
            <p className="talk-slide-sentence">{slide.sentence}</p>
          </header>
          <div className="talk-slide-visual">{renderVisual()}</div>
        </article>

        {presenterMode ? (
          <PresenterPanel slide={slide} english={english} />
        ) : null}
      </section>
    </main>
  );
}
