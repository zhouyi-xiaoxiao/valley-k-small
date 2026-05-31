'use client';

// Custom React deck — NOT reveal.js. Do not import reveal.js APIs.
// Slide navigation is internal React state, driven by URL hash (#slide-N).

import { useEffect, useMemo, useRef, useState } from 'react';
import { TalkBasicIdeaDemo } from '@/components/TalkBasicIdeaDemo';
import { TalkFormulaSlide } from '@/components/TalkFormulaSlide';
import { TalkGridHopLab } from '@/components/TalkGridHopLab';
import { TalkMechanismLab } from '@/components/TalkMechanismLab';
import { withBasePath } from '@/lib/url';
import type {
  BasicDemoPayload,
  Lang,
  TalkDeckManifest,
  TalkScriptPayload,
  TalkSlide,
  TalkSlideNote,
} from '@/types';

type TalkRevealDeckProps = {
  lang: Lang;
  prefix: string;
  manifest: TalkDeckManifest;
  scriptEn: TalkScriptPayload;
  scriptCn: TalkScriptPayload;
  basicDemo: BasicDemoPayload;
};

function localized(lang: Lang, en: string, cn: string) {
  return lang === 'cn' ? cn : en;
}

function slideTitle(lang: Lang, slide: TalkSlide) {
  return localized(lang, slide.title_en ?? slide.title, slide.title_cn ?? slide.title);
}

function slideSentence(lang: Lang, slide: TalkSlide) {
  return localized(lang, slide.sentence_en ?? slide.sentence, slide.sentence_cn ?? slide.sentence);
}

function manifestTitle(lang: Lang, manifest: TalkDeckManifest) {
  return localized(lang, manifest.title_en, manifest.title_cn);
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

function imageAlt(lang: Lang, slide: TalkSlide) {
  if (slide.evidence?.kind !== 'image') {
    return slideTitle(lang, slide);
  }
  return lang === 'cn' ? slide.evidence.alt_cn : slide.evidence.alt_en;
}

function PresenterPanel({
  lang,
  slide,
  english,
  chinese,
}: {
  lang: Lang;
  slide: TalkSlide;
  english?: TalkSlideNote;
  chinese?: TalkSlideNote;
}) {
  const active = lang === 'cn' ? chinese : english;
  const secondary = lang === 'cn' ? english : chinese;
  return (
    <aside className="talk-reveal-notes" aria-label="Presenter notes">
      <div className="talk-reveal-notes-block">
        <span className="talk-reveal-notes-label">{localized(lang, 'Timing', '时间')}</span>
        <strong>
          {slide.start} - {slide.end}
        </strong>
        <p>{active?.timing_prompt ?? english?.timing_prompt ?? ''}</p>
      </div>
      <div className="talk-reveal-notes-block">
        <span className="talk-reveal-notes-label">{localized(lang, 'Audience question', '听众问题')}</span>
        <p>{localized(lang, slide.question_en, slide.question_cn)}</p>
      </div>
      <div className="talk-reveal-notes-block">
        <span className="talk-reveal-notes-label">
          {localized(lang, 'Speaker script', '演讲稿')}
        </span>
        <p>{active?.spoken_text ?? ''}</p>
      </div>
      <div className="talk-reveal-notes-block">
        <span className="talk-reveal-notes-label">
          {localized(lang, 'Other-language note', '另一语言提示')}
        </span>
        <p>{secondary?.speaker_notes ?? secondary?.spoken_text ?? ''}</p>
      </div>
    </aside>
  );
}

function FigureSlide({ slide, lang }: { slide: TalkSlide; lang: Lang }) {
  if (slide.evidence?.kind !== 'image') {
    return (
      <div className="talk-reveal-unsupported">
        <h2>{slide.title}</h2>
        <p>{slide.sentence}</p>
      </div>
    );
  }

  if (slide.evidence.show_overlay) {
    return (
      <div className="talk-claim-slide">
        <div className="talk-claim-copy">
          <span className="talk-reveal-kicker">
            {slide.start} - {slide.end}
          </span>
          <h1>{slideTitle(lang, slide)}</h1>
          <p>{slideSentence(lang, slide)}</p>
          {slide.links?.length ? (
            <div className="talk-claim-links">
              {slide.links.map((link) => (
                <a key={link.href} href={withBasePath(link.href)}>
                  {localized(lang, link.label_en, link.label_cn)}
                </a>
              ))}
            </div>
          ) : null}
        </div>
        <figure className="talk-claim-visual">
          <img
            src={withBasePath(slide.evidence.src)}
            alt={imageAlt(lang, slide)}
          />
          {slide.evidence.hide_caption ? null : (
            <figcaption>{localized(lang, slide.evidence.caption_en, slide.evidence.caption_cn)}</figcaption>
          )}
        </figure>
      </div>
    );
  }

  return (
    <div className="talk-reveal-slide-shell">
      <img
        className="talk-reveal-fullslide-image"
        src={withBasePath(slide.evidence.src)}
        alt={imageAlt(lang, slide)}
      />
    </div>
  );
}

function BasicIdeaSlide({
  slide,
  basicDemo,
  lang,
}: {
  slide: TalkSlide;
  basicDemo: BasicDemoPayload;
  lang: Lang;
}) {
  return (
    <div className="talk-reveal-basic-shell">
      <div className="talk-reveal-basic-head">
        <span className="talk-reveal-kicker">
          {slide.start} - {slide.end}
        </span>
        <h1>{slideTitle(lang, slide)}</h1>
        <p>{slideSentence(lang, slide)}</p>
      </div>
      <div className="talk-reveal-basic-card">
        <TalkBasicIdeaDemo lang={lang} payload={basicDemo} />
      </div>
    </div>
  );
}

function SlideViewport({
  slide,
  lang,
  basicDemo,
}: {
  slide: TalkSlide;
  lang: Lang;
  basicDemo: BasicDemoPayload;
}) {
  return (
    <div className="talk-reveal-stage-inner">
      {slide.animation?.kind === 'basic-walk' ? (
        <BasicIdeaSlide slide={slide} basicDemo={basicDemo} lang={lang} />
      ) : slide.animation?.kind === 'formula-foundations' ? (
        <TalkFormulaSlide slide={slide} lang={lang} />
      ) : slide.animation?.kind === 'mechanism-lab' ? (
        <TalkMechanismLab slide={slide} lang={lang} />
      ) : slide.animation?.kind === 'grid-hop-lab' ? (
        <TalkGridHopLab slide={slide} lang={lang} />
      ) : (
        <FigureSlide slide={slide} lang={lang} />
      )}
    </div>
  );
}

export function TalkRevealDeck({
  lang,
  prefix: _prefix,
  manifest,
  scriptEn,
  scriptCn,
  basicDemo,
}: TalkRevealDeckProps) {
  const rootRef = useRef<HTMLDivElement | null>(null);
  const slides = manifest.slides;
  const [currentIndex, setCurrentIndex] = useState(0);
  const [presenterMode, setPresenterMode] = useState(false);
  const [isFullscreen, setIsFullscreen] = useState(false);
  const [immersiveMode, setImmersiveMode] = useState(false);
  const [controlsVisible, setControlsVisible] = useState(true);
  const englishById = useMemo(
    () => new Map(scriptEn.blocks.map((block) => [block.slide_id, block])),
    [scriptEn.blocks],
  );
  const chineseById = useMemo(
    () => new Map(scriptCn.blocks.map((block) => [block.slide_id, block])),
    [scriptCn.blocks],
  );

  useEffect(() => {
    const syncFromHash = () => setCurrentIndex(readSlideIndex(window.location.hash, slides.length));
    syncFromHash();
    window.addEventListener('hashchange', syncFromHash);
    return () => window.removeEventListener('hashchange', syncFromHash);
  }, [slides.length]);

  useEffect(() => {
    const hash = `#slide-${currentIndex + 1}`;
    if (window.location.hash !== hash) {
      window.history.replaceState(null, '', hash);
    }
  }, [currentIndex]);

  useEffect(() => {
    const syncFullscreen = () => {
      const doc = document as Document & { webkitFullscreenElement?: Element | null };
      setIsFullscreen(Boolean(document.fullscreenElement || doc.webkitFullscreenElement));
    };
    syncFullscreen();
    document.addEventListener('fullscreenchange', syncFullscreen);
    document.addEventListener('webkitfullscreenchange', syncFullscreen as EventListener);
    return () => {
      document.removeEventListener('fullscreenchange', syncFullscreen);
      document.removeEventListener('webkitfullscreenchange', syncFullscreen as EventListener);
    };
  }, []);

  useEffect(() => {
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

  const currentSlide = slides[currentIndex];
  const english = currentSlide ? englishById.get(currentSlide.id) : undefined;
  const chinese = currentSlide ? chineseById.get(currentSlide.id) : undefined;
  const progressPercent = ((currentIndex + 1) / slides.length) * 100;
  const fullscreenLike = immersiveMode || isFullscreen;
  const languageHref = withBasePath(
    `${lang === 'cn' ? '' : '/cn'}/talk/${manifest.talk_id}/#slide-${currentIndex + 1}`,
  );

  useEffect(() => {
    if (!fullscreenLike) {
      setControlsVisible(true);
      return;
    }
    let timeout: number | null = null;
    const revealControls = () => {
      setControlsVisible(true);
      if (timeout) {
        window.clearTimeout(timeout);
      }
      timeout = window.setTimeout(() => setControlsVisible(false), 2200);
    };
    revealControls();
    const events: Array<keyof WindowEventMap> = ['mousemove', 'mousedown', 'touchstart', 'keydown'];
    for (const eventName of events) {
      window.addEventListener(eventName, revealControls, { passive: true });
    }
    return () => {
      if (timeout) {
        window.clearTimeout(timeout);
      }
      for (const eventName of events) {
        window.removeEventListener(eventName, revealControls);
      }
    };
  }, [fullscreenLike, currentIndex]);

  const toggleFullscreen = async () => {
    if (!rootRef.current) {
      return;
    }
    const doc = document as Document & {
      webkitFullscreenElement?: Element | null;
      webkitExitFullscreen?: () => Promise<void> | void;
    };
    const el = rootRef.current as HTMLDivElement & {
      webkitRequestFullscreen?: () => Promise<void> | void;
    };
    if (fullscreenLike) {
      setImmersiveMode(false);
      if (document.fullscreenElement) {
        await document.exitFullscreen();
      } else if (doc.webkitFullscreenElement && doc.webkitExitFullscreen) {
        await doc.webkitExitFullscreen();
      }
      return;
    }
    setImmersiveMode(true);
    try {
      if (el.requestFullscreen) {
        await el.requestFullscreen();
      } else if (el.webkitRequestFullscreen) {
        await el.webkitRequestFullscreen();
      }
    } catch {
      // Keep the immersive layout even if the browser declines the fullscreen request.
    }
  };

  return (
    <div
      ref={rootRef}
      className={`talk-reveal-page${fullscreenLike ? ' is-fullscreen' : ''}${presenterMode ? ' is-presenter' : ''}${fullscreenLike && !controlsVisible ? ' is-toolbar-hidden' : ''}`}
    >
      <div
        className="talk-reveal-toolbar"
        onMouseEnter={() => fullscreenLike && setControlsVisible(true)}
        onFocus={() => fullscreenLike && setControlsVisible(true)}
      >
        <div className="talk-reveal-toolbar-brand">
          <strong>{manifestTitle(lang, manifest)}</strong>
          <span>
            {currentIndex + 1} / {slides.length}
          </span>
        </div>
        <div className="talk-reveal-progress">
          <span style={{ width: `${progressPercent}%` }} />
        </div>
        <div className="talk-reveal-toolbar-actions">
          <a className="talk-reveal-lang-link" href={languageHref}>
            {lang === 'cn' ? 'EN' : '中文'}
          </a>
          <button type="button" onClick={toggleFullscreen}>
            {fullscreenLike
              ? localized(lang, 'Exit full screen', '退出全屏')
              : localized(lang, 'Full screen', '全屏')}
          </button>
          <button type="button" onClick={() => setPresenterMode((value) => !value)}>
            {presenterMode
              ? localized(lang, 'Audience mode', '观众模式')
              : localized(lang, 'Presenter mode', '演讲者模式')}
          </button>
          <button type="button" onClick={() => setCurrentIndex((value) => Math.max(0, value - 1))}>
            {localized(lang, 'Prev', '上一页')}
          </button>
          <button
            type="button"
            onClick={() => setCurrentIndex((value) => Math.min(slides.length - 1, value + 1))}
          >
            {localized(lang, 'Next', '下一页')}
          </button>
        </div>
      </div>

      <div className="talk-reveal-layout">
        <div className="talk-reveal-stage">
          {currentSlide ? <SlideViewport slide={currentSlide} lang={lang} basicDemo={basicDemo} /> : null}
        </div>

        {presenterMode && currentSlide ? (
          <PresenterPanel lang={lang} slide={currentSlide} english={english} chinese={chinese} />
        ) : null}
      </div>
    </div>
  );
}
