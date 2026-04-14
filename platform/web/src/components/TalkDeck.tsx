'use client';

import Image from 'next/image';
import { useEffect, useMemo, useState } from 'react';
import { withBasePath } from '@/lib/url';
import { TalkBasicIdeaDemo } from '@/components/TalkBasicIdeaDemo';
import { TalkRingDemo } from '@/components/TalkRingDemo';
import type {
  BasicDemoPayload,
  Lang,
  RingDemoPayload,
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
  const points = xValues.map((value, index) => ({
    x:
      padding +
      ((width - padding * 2) * (value - minX)) / Math.max(1e-6, maxX - minX),
    y: height - padding - ((height - padding * 2) * yValues[index]) / maxY,
  }));
  if (points.length === 1) {
    return `M ${points[0].x.toFixed(2)} ${points[0].y.toFixed(2)}`;
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
    x:
      padding +
      ((width - padding * 2) * (valueX - minX)) / Math.max(1e-6, maxX - minX),
    y: height - padding - ((height - padding * 2) * valueY) / maxY,
  };
}

function ComparisonVisual() {
  const x = [0, 1, 2, 3, 4, 5, 6, 7];
  const single = [0.01, 0.05, 0.14, 0.29, 0.4, 0.31, 0.14, 0.04];
  const double = [0.02, 0.16, 0.33, 0.19, 0.08, 0.13, 0.26, 0.22];
  return (
    <div className="talk-comparison-card">
      <article className="talk-comparison-panel">
        <h3>One dominant route</h3>
        <svg viewBox="0 0 320 180" className="talk-chart-svg" role="img" aria-label="Single peak comparison">
          <path d={linePath(x, single, 320, 180)} fill="none" stroke="#0f766e" strokeWidth="6" />
        </svg>
        <p className="muted">One main timescale usually gives one main peak.</p>
      </article>
      <article className="talk-comparison-panel">
        <h3>Competing routes</h3>
        <svg viewBox="0 0 320 180" className="talk-chart-svg" role="img" aria-label="Double peak comparison">
          <path d={linePath(x, double, 320, 180)} fill="none" stroke="#d97706" strokeWidth="6" />
          <line x1="161" y1="24" x2="161" y2="156" stroke="rgba(29,41,53,0.22)" strokeDasharray="8 6" />
        </svg>
        <p className="muted">A valley appears when fast and slow arrivals stop sharing one scale.</p>
      </article>
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
    <div className={`talk-figure-shell${figure.full_bleed ? ' is-full-bleed' : ''}`}>
      <Image
        unoptimized
        className="talk-figure-image"
        src={withBasePath(figure.src)}
        alt={lang === 'cn' ? figure.alt_cn : figure.alt_en}
        width={1400}
        height={900}
      />
      {figure.hide_caption ? null : (
        <p className="muted talk-figure-caption">
          {lang === 'cn' ? figure.caption_cn : figure.caption_en}
        </p>
      )}
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
    const syncFullscreen = () => setIsFullscreen(Boolean(document.fullscreenElement));
    syncFullscreen();
    document.addEventListener('fullscreenchange', syncFullscreen);
    return () => document.removeEventListener('fullscreenchange', syncFullscreen);
  }, []);

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

  const slide = slides[currentIndex];
  const english = englishById.get(slide.id);
  const progressPercent = ((currentIndex + 1) / slides.length) * 100;
  const immersiveImage = slide.evidence?.kind === 'image' && slide.evidence.full_bleed;

  const renderVisual = () => {
    if (slide.animation?.kind === 'basic-walk') {
      return <TalkBasicIdeaDemo lang={lang} payload={basicDemo} />;
    }
    if (slide.animation?.kind === 'ring-branches') {
      return <TalkRingDemo lang={lang} payload={ringDemo} />;
    }
    if (slide.evidence?.kind === 'comparison') {
      return <ComparisonVisual />;
    }
    if (slide.evidence?.kind === 'image') {
      return <ImageFigure figure={slide.evidence} lang={lang} />;
    }
    return null;
  };

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
          <button type="button" onClick={() => void toggleFullscreen()}>
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
        <article className={`talk-slide-card talk-slide-${slide.id}${immersiveImage ? ' is-immersive' : ''}`}>
          {immersiveImage ? null : (
            <>
              <div className="talk-slide-topline">
                <span className="talk-slide-kicker">
                  {slide.start} - {slide.end}
                </span>
                <span className="talk-slide-question">
                  {lang === 'cn' ? slide.question_cn : slide.question_en}
                </span>
              </div>
              <header className="talk-slide-header">
                <h1>{slide.title}</h1>
                <p className="talk-slide-sentence">{slide.sentence}</p>
              </header>
            </>
          )}
          <div className="talk-slide-visual">{renderVisual()}</div>
        </article>

        {presenterMode ? (
          <PresenterPanel slide={slide} english={english} />
        ) : null}
      </section>
    </main>
  );
}
