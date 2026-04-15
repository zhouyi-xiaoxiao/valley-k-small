'use client';

import katex from 'katex';
import { KATEX_MACROS } from '@/lib/latex';
import type { TalkSlide } from '@/types';

function renderLatex(latex: string) {
  return katex.renderToString(latex, {
    displayMode: true,
    throwOnError: false,
    macros: KATEX_MACROS,
  });
}

const EQUATIONS = [
  {
    label: '2D lattice evolution',
    latex:
      String.raw`P_{x,y}(t+1)=\sum_{(x',y')\in\mathcal{N}(x,y)} w_{(x',y')\to(x,y)}\,P_{x',y'}(t)`,
    copy: 'Probability mass moves one discrete step at a time under the local transition rule.',
  },
  {
    label: 'First-hit time',
    latex: String.raw`T=\inf\{t\ge 0:\,(X_t,Y_t)=(x_{\mathrm{target}},y_{\mathrm{target}})\}`,
    copy: 'The target is absorbing because the process stops when this event first happens.',
  },
  {
    label: 'Survival probability',
    latex: String.raw`S(t)=\mathbb{P}(T>t)`,
    copy: 'This is the probability that the walker has not yet reached the target by time t.',
  },
  {
    label: 'First-passage distribution',
    latex: String.raw`f(t)=\mathbb{P}(T=t)=S(t-1)-S(t)`,
    copy: 'The hitting-time curve is the step-by-step loss of survival probability.',
  },
];

export function TalkFormulaSlide({ slide }: { slide: TalkSlide }) {
  return (
    <div className="talk-formula-shell">
      <div className="talk-formula-head">
        <span className="talk-reveal-kicker">
          {slide.start} - {slide.end}
        </span>
        <h1>{slide.title}</h1>
        <p>{slide.sentence}</p>
      </div>

      <div className="talk-formula-grid">
        {EQUATIONS.map((item) => (
          <section key={item.label} className="talk-formula-card">
            <span className="talk-formula-label">{item.label}</span>
            <div
              className="talk-formula-math"
              dangerouslySetInnerHTML={{ __html: renderLatex(item.latex) }}
            />
            <p>{item.copy}</p>
          </section>
        ))}
      </div>
    </div>
  );
}
