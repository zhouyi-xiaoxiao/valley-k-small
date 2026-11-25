'use client';

import katex from 'katex';
import { KATEX_MACROS } from '@/lib/latex';
import type { Lang, TalkSlide } from '@/types';

function renderLatex(latex: string) {
  return katex.renderToString(latex, {
    displayMode: true,
    throwOnError: false,
    macros: KATEX_MACROS,
  });
}

const EQUATIONS = [
  {
    label_en: 'Master equation',
    label_cn: '主方程',
    latex: String.raw`P_i(t+1)=\sum_{j\in\mathcal{N}(i)\cup\{i\}} w_{j\to i}\,P_j(t),\qquad P_{\mathrm{target}}(t)=0`,
    copy_en:
      'Probability moves one step at a time over the sites (ring sites or lattice cells): w_{j→i} is the probability of a step from j to i, 𝒩(i) the sites that can step to i, and staying put is included. Mass that reaches the target is removed: the target is absorbing.',
    copy_cn:
      '概率每一步在格点（环上的格点或二维格子）之间移动：w_{j→i} 是从 j 一步走到 i 的概率，𝒩(i) 是能一步走到 i 的格点，留在原地也算在内。到达目标的概率被移除：目标是吸收态。',
  },
  {
    label_en: 'First-hit time',
    label_cn: '首达时间',
    latex: String.raw`T=\inf\{t\ge 1:\,X_t=\mathrm{target}\},\qquad X_0=\mathrm{start}\neq\mathrm{target}`,
    copy_en: 'X_t is the walker’s site after t steps. The walk stops the first time it reaches the target; T is that step.',
    copy_cn: 'X_t 是第 t 步后游走者所在的格点。游走在第一次到达目标时停止，T 就是这一步的步数。',
  },
  {
    label_en: 'Survival and first-passage distribution',
    label_cn: '存活概率与首达时间分布',
    latex: String.raw`\begin{aligned}S(t)&=\mathbb{P}(T>t)=\textstyle\sum_{i\neq\mathrm{target}}P_i(t)\\ f(t)&=\mathbb{P}(T=t)=S(t-1)-S(t)\end{aligned}`,
    copy_en:
      'S(t) is the probability that the target has not been reached by step t; the first-passage distribution f(t) is the probability S loses at step t.',
    copy_cn: 'S(t) 是到第 t 步仍未到达目标的概率；首达时间分布 f(t) 是第 t 步 S 减少的那部分概率。',
  },
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

function slideKicker(lang: Lang, slide: TalkSlide) {
  return localized(lang, slide.kicker_en ?? '', slide.kicker_cn ?? slide.kicker_en ?? '');
}

export function TalkFormulaSlide({ slide, lang }: { slide: TalkSlide; lang: Lang }) {
  return (
    <div className="talk-formula-shell">
      <div className="talk-formula-head">
        {slideKicker(lang, slide) ? (
          <span className="talk-reveal-kicker">{slideKicker(lang, slide)}</span>
        ) : null}
        <h1>{slideTitle(lang, slide)}</h1>
        <p>{slideSentence(lang, slide)}</p>
      </div>

      <div className="talk-formula-grid">
        {EQUATIONS.map((item) => (
          <section key={item.label_en} className="talk-formula-card">
            <span className="talk-formula-label">{localized(lang, item.label_en, item.label_cn)}</span>
            <div
              className="talk-formula-math"
              dangerouslySetInnerHTML={{ __html: renderLatex(item.latex) }}
            />
            <p>{localized(lang, item.copy_en, item.copy_cn)}</p>
          </section>
        ))}
      </div>
    </div>
  );
}
