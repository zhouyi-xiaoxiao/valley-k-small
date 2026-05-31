'use client';

import { useMemo, useState } from 'react';
import { withBasePath } from '@/lib/url';
import type { Lang, TalkSlide } from '@/types';

type MechanismCase = {
  id: 'ring' | 'grid' | 'encounter';
  labelEn: string;
  labelCn: string;
  headlineEn: string;
  headlineCn: string;
  mechanismEn: string;
  mechanismCn: string;
  verdictEn: string;
  verdictCn: string;
  reportHref: string;
  reportLabelEn: string;
  reportLabelCn: string;
  values: number[];
  color: string;
};

const CASES: MechanismCase[] = [
  {
    id: 'ring',
    labelEn: 'Ring shortcut',
    labelCn: '环上 shortcut',
    headlineEn: 'Two route families survive as two visible time scales.',
    headlineCn: '两类路径族保留下来，就会形成两个可见时间尺度。',
    mechanismEn: 'A shortcut can create a fast branch while the ordinary ring route keeps delayed mass.',
    mechanismCn: 'shortcut 产生快速分支，同时普通环路仍保留延迟质量。',
    verdictEn: 'Positive mechanism candidate',
    verdictCn: '正向机制候选',
    reportHref: '/reports/ring_lazy_jump_ext_rev2/',
    reportLabelEn: 'Ring shortcut evidence',
    reportLabelCn: '环 shortcut 证据',
    values: [0.02, 0.08, 0.2, 0.36, 0.25, 0.1, 0.06, 0.11, 0.2, 0.16],
    color: '#0f766e',
  },
  {
    id: 'grid',
    labelEn: 'Grid2D target geometry',
    labelCn: 'Grid2D target 几何',
    headlineEn: 'Geometry decides whether route and target competition stay visible.',
    headlineCn: '几何决定路径竞争和 target 竞争是否仍然可见。',
    mechanismEn: 'Outside budget, membrane crossing, and target placement split the arrival mass.',
    mechanismCn: 'outside budget、membrane crossing 与 target 布置共同拆分首达质量。',
    verdictEn: 'Mechanism depends on decomposition',
    verdictCn: '机制依赖分解证据',
    reportHref: '/reports/grid2d_membrane_near_target/',
    reportLabelEn: 'Grid2D mechanism evidence',
    reportLabelCn: 'Grid2D 机制证据',
    values: [0.01, 0.05, 0.18, 0.31, 0.22, 0.09, 0.07, 0.14, 0.24, 0.18],
    color: '#b45309',
  },
  {
    id: 'encounter',
    labelEn: 'Exact encounter guardrail',
    labelCn: 'exact encounter 护栏',
    headlineEn: 'Not every late shoulder is a real second mode.',
    headlineCn: '不是每个 late shoulder 都是真正第二峰。',
    mechanismEn: 'The reflecting synchronous co-location model exposes parity artifacts and same-target tails.',
    mechanismCn: 'reflecting synchronous co-location 模型暴露出 parity artifact 与 same-target tail。',
    verdictEn: 'Guardrail: no robust F2 double peak',
    verdictCn: '护栏：没有稳健 F2 双峰',
    reportHref: '/reports/final_multitimescale_fpt_encounter/',
    reportLabelEn: 'Final encounter report',
    reportLabelCn: '最终 encounter 报告',
    values: [0.04, 0.17, 0.3, 0.21, 0.11, 0.07, 0.05, 0.04, 0.03, 0.02],
    color: '#b91c1c',
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

function pathFor(values: number[], width: number, height: number) {
  const padX = 20;
  const padY = 18;
  const maxY = Math.max(...values);
  return values
    .map((value, index) => {
      const x = padX + (index * (width - padX * 2)) / (values.length - 1);
      const y = height - padY - (value / maxY) * (height - padY * 2);
      return `${index === 0 ? 'M' : 'L'} ${x.toFixed(1)} ${y.toFixed(1)}`;
    })
    .join(' ');
}

export function TalkMechanismLab({ lang, slide }: { lang: Lang; slide: TalkSlide }) {
  const [selectedId, setSelectedId] = useState<MechanismCase['id']>('ring');
  const [strictness, setStrictness] = useState(1);
  const selected = useMemo(
    () => CASES.find((item) => item.id === selectedId) ?? CASES[0],
    [selectedId],
  );
  const artifactOpacity = selected.id === 'encounter' ? 0.78 + strictness * 0.08 : 0.2 + strictness * 0.08;

  return (
    <div className="talk-mechanism-lab">
      <header className="talk-mechanism-head">
        <span className="talk-reveal-kicker">{slide.start} - {slide.end}</span>
        <h1>{slideTitle(lang, slide)}</h1>
        <p>{slideSentence(lang, slide)}</p>
      </header>

      <div className="talk-mechanism-body">
        <section className="talk-mechanism-controls" aria-label={localized(lang, 'Mechanism selector', '机制选择器')}>
          <div className="talk-mechanism-segments">
            {CASES.map((item) => (
              <button
                key={item.id}
                type="button"
                className={item.id === selected.id ? 'is-active' : ''}
                onClick={() => setSelectedId(item.id)}
              >
                {localized(lang, item.labelEn, item.labelCn)}
              </button>
            ))}
          </div>

          <label className="talk-mechanism-slider">
            <span>{localized(lang, 'Artifact strictness', 'artifact 排除强度')}</span>
            <input
              type="range"
              min="0"
              max="2"
              step="1"
              value={strictness}
              onChange={(event) => setStrictness(Number(event.currentTarget.value))}
            />
          </label>

          <div className="talk-mechanism-verdict">
            <span>{localized(lang, 'Current reading', '当前解读')}</span>
            <strong>{localized(lang, selected.verdictEn, selected.verdictCn)}</strong>
          </div>

          <a className="talk-mechanism-link" href={withBasePath(selected.reportHref)}>
            {localized(lang, selected.reportLabelEn, selected.reportLabelCn)}
          </a>
        </section>

        <section className="talk-mechanism-visual" aria-label={localized(lang, 'Distribution sketch', '分布草图')}>
          <svg viewBox="0 0 720 420" role="img">
            <rect x="0" y="0" width="720" height="420" rx="0" fill="#f7f7f3" />
            <g opacity="0.9">
              <line x1="58" y1="348" x2="658" y2="348" stroke="#25313b" strokeWidth="3" />
              <line x1="58" y1="56" x2="58" y2="348" stroke="#25313b" strokeWidth="3" />
              <text x="358" y="390" textAnchor="middle" className="talk-mechanism-axis">
                {localized(lang, 'first-passage time', 'first-passage time')}
              </text>
              <text x="28" y="74" textAnchor="middle" className="talk-mechanism-axis">
                f(t)
              </text>
            </g>
            <path
              d={pathFor(selected.values, 620, 270)}
              transform="translate(58 62)"
              fill="none"
              stroke={selected.color}
              strokeWidth="12"
              strokeLinecap="round"
              strokeLinejoin="round"
            />
            <path
              d={pathFor(selected.values.map((value, index) => (index % 2 === 0 ? value * 1.18 : value * 0.72)), 620, 270)}
              transform="translate(58 62)"
              fill="none"
              stroke="#25313b"
              strokeWidth="5"
              strokeDasharray="12 14"
              strokeLinecap="round"
              strokeLinejoin="round"
              opacity={artifactOpacity}
            />
            <g transform="translate(94 76)">
              <rect width="240" height="88" rx="12" fill="#ffffff" stroke="#d6d6ca" />
              <text x="20" y="34" className="talk-mechanism-small-title">
                {localized(lang, selected.labelEn, selected.labelCn)}
              </text>
              <text x="20" y="62" className="talk-mechanism-small">
                {localized(lang, 'solid = mechanism trace', 'solid = mechanism trace')}
              </text>
            </g>
            <g transform="translate(424 246)">
              <rect width="226" height="88" rx="12" fill="#ffffff" stroke="#d6d6ca" />
              <text x="18" y="34" className="talk-mechanism-small-title">
                {localized(lang, 'artifact check', 'artifact check')}
              </text>
              <text x="18" y="62" className="talk-mechanism-small">
                {localized(lang, 'dashed trace must be explained', 'dashed trace must be explained')}
              </text>
            </g>
          </svg>
        </section>

        <section className="talk-mechanism-reading">
          <h2>{localized(lang, selected.headlineEn, selected.headlineCn)}</h2>
          <p>{localized(lang, selected.mechanismEn, selected.mechanismCn)}</p>
          <ul>
            <li>{localized(lang, 'Separate route mass from target mass.', '区分 route mass 与 target mass。')}</li>
            <li>{localized(lang, 'Compare raw shape with decomposition evidence.', '把 raw shape 与 decomposition evidence 对照。')}</li>
            <li>{localized(lang, 'Use the encounter model as a negative-control discipline.', '把 encounter model 当作 negative-control discipline。')}</li>
          </ul>
        </section>
      </div>
    </div>
  );
}
