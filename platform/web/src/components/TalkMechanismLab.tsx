'use client';

import { useMemo, useState } from 'react';
import { withBasePath } from '@/lib/url';
import type { Lang, TalkSlide } from '@/types';

// Schematic only: the curves below are drawn from simple analytic shapes to
// illustrate each case. They are labelled "schematic" on screen and are not
// computed first-passage data.

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
  xLabelEn: string;
  xLabelCn: string;
  yLabel: string;
  values: number[];
  color: string;
};

const SAMPLES = 80;

// Shape normalised to 1 at its mode, (k - 1) * theta; zero at t = 0.
function hump(t: number, k: number, theta: number) {
  if (t <= 0) {
    return 0;
  }
  const mode = (k - 1) * theta;
  return Math.pow(t / mode, k - 1) * Math.exp(-(t - mode) / theta);
}

function sampleCurve(tMax: number, shape: (t: number) => number) {
  return Array.from({ length: SAMPLES + 1 }, (_, index) => shape((tMax * index) / SAMPLES));
}

const CASES: MechanismCase[] = [
  {
    id: 'ring',
    labelEn: 'Ring shortcut',
    labelCn: '环上捷径',
    headlineEn: 'Two route families can survive as two visible time scales.',
    headlineCn: '两类路径族都保留下来时，会形成两个看得见的时间尺度。',
    mechanismEn:
      'Paths through the shortcut arrive early; paths round the ring arrive late. The split holds only in a middle range of shortcut use.',
    mechanismCn: '走捷径的路径早到，绕环的路径晚到。只有捷径使用概率适中时，两群才分得开。',
    verdictEn: 'Mechanism supported: shortcut route vs ring route',
    verdictCn: '机制成立：走捷径 vs 绕环',
    reportHref: '/reports/ring_lazy_jump_ext_rev2/',
    reportLabelEn: 'Ring shortcut report',
    reportLabelCn: '环上捷径报告',
    xLabelEn: 'first-passage time t',
    xLabelCn: '首达时间 t',
    yLabel: 'f(t)',
    values: sampleCurve(110, (t) => hump(t, 3, 4) + 0.45 * hump(t, 12, 4.5)),
    color: '#0f766e',
  },
  {
    id: 'grid',
    labelEn: '2D lattice targets',
    labelCn: '二维格点与目标',
    headlineEn: 'Geometry decides whether route and target competition stay visible.',
    headlineCn: '几何决定路径竞争和目标竞争是否还能看得见。',
    mechanismEn:
      'Time spent outside the corridor, membrane crossing and target placement each move probability between the early and late windows; a decomposition has to show which one does.',
    mechanismCn: '通道外停留时间、穿过半透膜和目标位置，都会把概率在早、晚两个时间窗之间挪动；必须靠分解说明是哪一个。',
    verdictEn: 'Supported after decomposition',
    verdictCn: '分解后成立',
    reportHref: '/reports/grid2d_membrane_near_target/',
    reportLabelEn: '2D lattice: membrane near the target',
    reportLabelCn: '二维格点：目标附近的半透膜',
    xLabelEn: 'first-passage time t',
    xLabelCn: '首达时间 t',
    yLabel: 'f(t)',
    values: sampleCurve(130, (t) => 0.8 * hump(t, 3, 5) + 0.6 * hump(t, 10, 6)),
    color: '#b45309',
  },
  {
    id: 'encounter',
    labelEn: 'Exact encounter guardrail',
    labelCn: '精确相遇护栏',
    headlineEn: 'Not every late bump is a real second peak.',
    headlineCn: '不是每个晚到的凸起都是真正的第二峰。',
    mechanismEn:
      'Two lazy walkers on a finite 1D reflecting lattice without a shortcut, moving synchronously and meeting only on the same site: raw f(t) alternates between odd and even steps, and once the pairs are merged (F2) one peak and a long tail remain.',
    mechanismCn:
      '两个懒惰游走者在有限长、反射边界、无捷径的一维格点上同步行走，只有走到同一格点才算相遇：原始 f(t) 在奇、偶步之间交替；把奇偶步两两合并（F2）后，只剩一个峰和一条长尾。',
    verdictEn: 'Guardrail: no robust F2 double peak in the scanned no-shortcut 1D cases',
    verdictCn: '护栏：扫描过的无捷径一维情形中，F2 没有稳健双峰',
    reportHref: '/reports/final_multitimescale_fpt_encounter/',
    reportLabelEn: 'Exact encounter report',
    reportLabelCn: '精确相遇报告',
    xLabelEn: 'first-encounter time, odd/even steps paired',
    xLabelCn: '首次相遇时间（奇偶步合并）',
    yLabel: 'F2',
    values: sampleCurve(160, (t) => hump(t, 4, 6) + 0.18 * hump(t, 1.6, 40)),
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

function slideKicker(lang: Lang, slide: TalkSlide) {
  return localized(lang, slide.kicker_en ?? '', slide.kicker_cn ?? '');
}

function pathFor(values: number[], width: number, height: number, maxY: number) {
  return values
    .map((value, index) => {
      const x = (index * width) / (values.length - 1);
      const y = height - (value / maxY) * height;
      return `${index === 0 ? 'M' : 'L'} ${x.toFixed(1)} ${y.toFixed(1)}`;
    })
    .join(' ');
}

export function TalkMechanismLab({ lang, slide }: { lang: Lang; slide: TalkSlide }) {
  const [selectedId, setSelectedId] = useState<MechanismCase['id']>('ring');
  const selected = useMemo(
    () => CASES.find((item) => item.id === selectedId) ?? CASES[0],
    [selectedId],
  );
  const isEncounter = selected.id === 'encounter';
  // For the encounter case the dashed line is the raw curve, which alternates
  // between odd and even steps around the paired (F2) envelope.
  const raw = isEncounter
    ? selected.values.map((value, index) => (index % 2 === 0 ? value * 1.6 : value * 0.4))
    : null;
  const maxY = Math.max(...(raw ?? selected.values)) * 1.08;
  const plotW = 600;
  const plotH = 260;
  const kicker = slideKicker(lang, slide);

  return (
    <div className="talk-mechanism-lab">
      <header className="talk-mechanism-head">
        {kicker ? <span className="talk-reveal-kicker">{kicker}</span> : null}
        <h1>{slideTitle(lang, slide)}</h1>
        <p>{slideSentence(lang, slide)}</p>
      </header>

      <div className="talk-mechanism-body">
        <section className="talk-mechanism-controls" aria-label={localized(lang, 'Case selector', '情形选择')}>
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

          <div className="talk-mechanism-verdict">
            <span>{localized(lang, 'Reading', '结论')}</span>
            <strong>{localized(lang, selected.verdictEn, selected.verdictCn)}</strong>
          </div>

          <a className="talk-mechanism-link" href={withBasePath(selected.reportHref)}>
            {localized(lang, selected.reportLabelEn, selected.reportLabelCn)}
          </a>
        </section>

        <section
          className="talk-mechanism-visual"
          aria-label={localized(
            lang,
            'Schematic curve: illustrative shape, not computed data',
            '示意曲线：仅示意形状，不是计算数据',
          )}
        >
          <svg viewBox="0 0 720 420" role="img">
            <rect x="0" y="0" width="720" height="420" fill="#f7f7f3" />
            <text x="700" y="34" textAnchor="end" className="talk-mechanism-small" fontStyle="italic">
              {localized(lang, 'Schematic: illustrative shapes, not computed data', '示意图：仅示意形状，不是计算数据')}
            </text>
            <g opacity="0.9">
              <line x1="58" y1="348" x2="670" y2="348" stroke="#25313b" strokeWidth="3" />
              <line x1="58" y1="64" x2="58" y2="348" stroke="#25313b" strokeWidth="3" />
              <text x="664" y="386" textAnchor="end" className="talk-mechanism-axis">
                {localized(lang, selected.xLabelEn, selected.xLabelCn)}
              </text>
              <text x="70" y="70" className="talk-mechanism-axis">
                {selected.yLabel}
              </text>
            </g>
            {raw ? (
              <path
                d={pathFor(raw, plotW, plotH, maxY)}
                transform="translate(58 88)"
                fill="none"
                stroke="#25313b"
                strokeWidth="2.5"
                strokeDasharray="6 5"
                strokeLinejoin="round"
                opacity="0.75"
              />
            ) : null}
            <path
              d={pathFor(selected.values, plotW, plotH, maxY)}
              transform="translate(58 88)"
              fill="none"
              stroke={selected.color}
              strokeWidth="8"
              strokeLinecap="round"
              strokeLinejoin="round"
            />
            <g transform="translate(396 92)">
              <rect width="290" height={raw ? 88 : 56} rx="12" fill="#ffffff" stroke="#d6d6ca" />
              <text x="18" y="36" className="talk-mechanism-small-title">
                {localized(lang, selected.labelEn, selected.labelCn)}
              </text>
              {raw ? (
                <text x="18" y="68" className="talk-mechanism-small">
                  {localized(lang, 'dashed: raw f(t), odd/even steps', '虚线：原始 f(t)，奇偶步交替')}
                </text>
              ) : null}
            </g>
          </svg>
        </section>

        <section className="talk-mechanism-reading">
          <h2>{localized(lang, selected.headlineEn, selected.headlineCn)}</h2>
          <p>{localized(lang, selected.mechanismEn, selected.mechanismCn)}</p>
          <ul>
            <li>{localized(lang, 'Separate route probability from target probability.', '把来自路径的概率和来自目标的概率分开。')}</li>
            <li>{localized(lang, 'Compare the raw shape with the decomposition.', '把原始形状和分解结果对照。')}</li>
            <li>{localized(lang, 'Use the encounter model as a negative control.', '把相遇模型当作阴性对照。')}</li>
          </ul>
        </section>
      </div>
    </div>
  );
}
