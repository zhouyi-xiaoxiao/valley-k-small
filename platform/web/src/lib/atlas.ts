// Reader-facing layer of the atlas: which reports are written up, how they are
// grouped, which three to open first, and where each report's PDF lives.
// Everything here is presentation; report text and data come from public/data/v1.
import fs from 'fs';
import path from 'path';
import type { DatasetMeta, Lang, ReportMeta, WebIndex } from '@/types';

export const REPO_URL = 'https://github.com/zhouyi-xiaoxiao/valley-k-small';
export const OWNER_SITE = 'https://zhouyixiaoxiao.com/';
export const OWNER_SITE_ZH = 'https://zhouyixiaoxiao.com/zh/';

const REPO_ROOT = path.join(process.cwd(), '..', '..');

export type ReportStatus = 'active' | 'wip';

let registryCache: Record<string, ReportStatus> | null = null;

// Minimal reader for research/reports/report_registry.yaml: only `id` and `status`.
export function loadRegistryStatus(): Record<string, ReportStatus> {
  if (registryCache) {
    return registryCache;
  }
  const out: Record<string, ReportStatus> = {};
  const file = path.join(REPO_ROOT, 'research', 'reports', 'report_registry.yaml');
  if (fs.existsSync(file)) {
    let current: string | null = null;
    for (const line of fs.readFileSync(file, 'utf-8').split('\n')) {
      const id = line.match(/^\s*-\s+id:\s*([A-Za-z0-9_\-]+)/);
      if (id) {
        current = id[1];
        out[current] = 'active';
        continue;
      }
      const status = line.match(/^\s+status:\s*([A-Za-z]+)/);
      if (status && current) {
        out[current] = status[1] === 'wip' ? 'wip' : 'active';
      }
    }
  }
  registryCache = out;
  return out;
}

export type ManuscriptLink = { lang: 'en' | 'cn'; href: string };

// The written report for each language: only the copy published with the site
// (the web-data build always copies manuscript/<id>_{en,cn}.pdf). Readers are
// never sent to the repository itself.
export function manuscriptLinks(reportId: string, meta: ReportMeta | null, withBase: (url: string) => string): ManuscriptLink[] {
  const links: ManuscriptLink[] = [];
  const candidates: Array<{ lang: 'en' | 'cn'; names: string[] }> = [
    { lang: 'en', names: [`${reportId}_en.pdf`, `${reportId}.pdf`] },
    { lang: 'cn', names: [`${reportId}_cn.pdf`] },
  ];
  for (const { lang, names } of candidates) {
    let href: string | null = null;
    for (const name of names) {
      const hosted = meta?.assets.find(
        (asset) => asset.kind === 'pdf' && asset.web_path.endsWith(`/${reportId}/manuscript/${name}`),
      );
      if (hosted) {
        href = withBase(hosted.web_path);
        break;
      }
    }
    if (href) {
      links.push({ lang, href });
    }
  }
  return links;
}

export type Family = 'ring' | 'grid2d' | 'across';

export function reportFamily(reportId: string, group: string): Family {
  if (group === 'ring' || reportId.startsWith('ring_')) {
    return 'ring';
  }
  if (group === 'grid2d' || reportId.startsWith('grid2d_')) {
    return 'grid2d';
  }
  return 'across';
}

export const FAMILY_ORDER: Family[] = ['ring', 'grid2d', 'across'];

export function familyLabel(lang: Lang, family: Family): string {
  const labels: Record<Family, [string, string]> = {
    ring: ['On a ring', '环'],
    grid2d: ['On a two-dimensional lattice', '二维格点'],
    across: ['Across models', '跨模型'],
  };
  return lang === 'cn' ? labels[family][1] : labels[family][0];
}

export function familyNote(lang: Lang, family: Family): string {
  const notes: Record<Family, [string, string]> = {
    ring: [
      'A walker on a ring of N sites steps to one of its K nearest neighbours (K/2 on each side); in the lazy versions it may also stay put. Most reports add one directed shortcut between two sites and ask when the time of first arrival at a target site has an early and a late peak; later reports add a second target, a drift or a second walker.',
      '游走者在 N 个格点的环上，每步跳到最近的 K 个邻居之一（每侧 K/2 个）；懒惰版本中也可以原地不动。多数报告加一条连接两个格点的有向捷径，研究首次到达目标格点的时间何时出现一早一晚两个峰；后面的报告还加入第二个目标、漂移或第二个游走者。',
    ],
    grid2d: [
      'Square and rectangular lattices, reflecting walls, corridors, membranes and two competing targets: when does a second peak survive?',
      '方形与矩形格点、反射壁、走廊、膜、两个相互竞争的目标：第二个峰什么时候还能存活？',
    ],
    across: [
      'Comparisons between models and methods, and the synthesis that collects the accepted results.',
      '模型之间、方法之间的比较，以及汇总已确认结果的综述。',
    ],
  };
  return lang === 'cn' ? notes[family][1] : notes[family][0];
}

// Reports replaced by a later revision (from the reports' own README
// "Successor" lines): the page says so at the top and links the successor.
export const SUPERSEDED_BY: Record<string, string> = {
  ring_lazy_jump_ext: 'ring_lazy_jump_ext_rev2',
};

// Three reports to open first, in reading order.
export const START_HERE: Array<{ reportId: string; en: string; cn: string }> = [
  {
    reportId: 'ring_lazy_jump',
    en: 'The mechanism. A lazy walk (at each step it may stay put) on a ring with one directed shortcut, under two step rules (K\u00a0=\u00a02: one site either way; K\u00a0=\u00a04: one or two sites either way), and which routes make the fast and the delayed arrivals.',
    cn: '机制本身。环上带一条有向捷径的懒惰随机游走（每一步都可能原地不动），两种步长规则（K\u00a0=\u00a02：每步向左或向右走 1 格；K\u00a0=\u00a04：走 1 格或 2 格），以及快、慢两类到达分别来自哪些路径。',
  },
  {
    reportId: 'ring_lazy_jump_ext_rev2',
    en: 'Which routes make each peak, at N\u00a0=\u00a0100 and shortcut strength β\u00a0=\u00a00.01: Monte Carlo trajectories sorted by route, with checks that the shares do not depend on the choice of time windows or peak thresholds.',
    cn: '每个峰由哪些路径构成：N\u00a0=\u00a0100、捷径强度 β\u00a0=\u00a00.01 时，把蒙特卡洛轨迹按路径分类，并检查各类占比不随时间窗和峰判据的选取而变。',
  },
  {
    reportId: 'grid2d_bimodality',
    en: 'The same question on a square lattice: which two-channel mechanisms give a genuine second peak, and which shapes are artefacts.',
    cn: '同一个问题放到方形格点上：哪些双通道机制带来真正的第二个峰，哪些形状只是假象。',
  },
];

export type TalkInfo = {
  id: string;
  title: [string, string];
  line: [string, string];
  when: [string, string];
};

export const TALKS: TalkInfo[] = [
  {
    id: 'semt-phd',
    title: ['Hidden Routes in First-Passage Time', '首达时间中的隐藏路径'],
    line: [
      'One target on a ring, one directed shortcut: a fast branch, a valley and a delayed branch. With a live random-walk animation.',
      '环上一个目标、一条有向捷径：快分支、谷、慢分支。附实时随机游走动画。',
    ],
    when: [
      'Ten-minute talk by Xiaoxiao Zhouyi to PhD students at the Ideas Exchange Week of the School of Engineering Mathematics and Technology (SEMT), University of Bristol, 15\u00a0April 2026 · nine slides',
      '周易潇潇在布里斯托大学工程数学与技术学院（SEMT）Ideas Exchange Week 上面向博士生的十分钟演讲，2026 年 4 月 15 日 · 九张幻灯片',
    ],
  },
  {
    id: 'multitimescale-encounter',
    title: ['Hidden Routes, Real Peaks', '隐藏路径与真实双峰'],
    line: [
      'When a double peak counts as evidence: the ring mechanism, a live two-dimensional walk, and exact encounter checks.',
      '双峰什么时候才算证据：环上的机制、实时二维格点游走，以及精确的相遇核对。',
    ],
    when: [
      'Web slide deck for a ten-minute talk, prepared in May 2026 · nine slides',
      '为十分钟演讲准备的网页幻灯片，2026 年 5 月制作 · 九张幻灯片',
    ],
  },
];

export function formatDay(lang: Lang, iso: string): string {
  const date = new Date(iso);
  if (Number.isNaN(date.getTime()) || date.getTime() === 0) {
    return '';
  }
  if (lang === 'cn') {
    return `${date.getUTCFullYear()} 年 ${date.getUTCMonth() + 1} 月 ${date.getUTCDate()} 日`;
  }
  return date.toLocaleDateString('en-GB', { day: 'numeric', month: 'long', year: 'numeric', timeZone: 'UTC' });
}

// Placeholder text produced for reports that have no write-up yet.
export function isPlaceholderText(text: string): boolean {
  const t = text.trim();
  const reportId = '[a-z0-9]+(?:_[a-z0-9]+)+';
  const cnSource = '(?:该研究报告|二维格点体系|环模型体系|Grid2D 体系|Ring 体系|跨模型综合)';
  const cnSection = new RegExp(
    `${cnSource}：(?:本报告围绕|本节(?:说明状态空间、参数约束与边界条件设定|给出解析/数值流程、反演方法与验证协议|总结峰谷结构、通道机制与跨报告对比结论|整理关键证据、图表说明与复现路径))。`,
  );
  const cnFinding = new RegExp(
    `${cnSource}(?:（${reportId}）)?：关键结论见本页公式链、交互图与原始资产。`,
  );
  const cnReportTitle = new RegExp(`${cnSource}：${reportId}\\s*研究报告`);
  const cnMechanismDataset = new RegExp(`${cnSource}：${reportId}\\s*研究报告 的机制数据集：asset-size-profile`);
  const enPlaceholder = new RegExp(`(?:Model|Method|Result) summary placeholder for ${reportId}\\.`, 'i');
  const enReport = new RegExp(`(?:^|:\\s*)Research report(?:\\s+${reportId})?\\.?$`, 'i');
  return (
    t.length === 0 ||
    /WIP scaffold|not yet started|summary placeholder|^该研究报告：|[a-z0-9]+_[a-z0-9_]+\s*研究报告|^该证据片段以英文记录，请结合路径在源文档核对。$/.test(t) ||
    cnSection.test(t) ||
    cnFinding.test(t) ||
    cnReportTitle.test(t) ||
    cnMechanismDataset.test(t) ||
    enPlaceholder.test(t) ||
    enReport.test(t)
  );
}

// Extraction can leave a prose card with pieces of a LaTeX formula but no
// operators or delimiters. Keep those cards out of the reader-facing page.
// The checks deliberately target malformed signatures rather than ordinary
// inline mathematics such as `f(t) = ...` in curated copy.
export function isLatexResidue(text: string): boolean {
  const t = text.replace(/\s+/g, ' ').trim();
  if (!t) {
    return false;
  }
  if (/\\[A-Za-z]+/.test(t)) {
    return true;
  }
  // Chinese-source text with the characters stripped leaves only full-width
  // punctuation behind.
  const fullWidthMarks = (t.match(/[，。、；：（）]/g) || []).length;
  const hanChars = (t.match(/[\u4e00-\u9fff]/g) || []).length;
  if (fullWidthMarks >= 3 && hanChars === 0) {
    return true;
  }
  return (
    /\(\s*[A-Za-z]\s+(?:[A-Za-z]|\d+)(?:\(t\))?\s*\)/.test(t) ||
    /\bq\s+i\b/i.test(t) ||
    /\b(?:p|q|f|r|Q|P)\s+t(?:\+?\d|\s|=)/.test(t) ||
    /\bt\s+valley\b/i.test(t) ||
    /\bT\s+\[/.test(t) ||
    /\beq:[A-Za-z]/.test(t) ||
    /\bp\s+pass\b/.test(t) ||
    /(?:e-1|->|·)/.test(t) && /\b(?:alpha|lambda|max|Delta|tau|P|Q|R|f|F)\b/i.test(t)
  );
}

export function isGeneratedAssetDatasetPath(pathname: string): boolean {
  return /(?:^|\/)series\/asset-size-profile\.json(?:$|[?#])/i.test(pathname.trim());
}

export function isGeneratedMechanismDatasetSnippet(text: string): boolean {
  return /^(?:Mechanism dataset for .+|.+的机制数据集)[:：]\s*[A-Za-z0-9_.-]+\.?$/i.test(text.trim());
}

export function evidenceKindLabel(lang: Lang, kind: string): string {
  const labels: Record<string, [string, string]> = {
    section_summary: ['Section', '章节'],
    math_block: ['Formula', '公式'],
    dataset: ['Data', '数据'],
    source_document: ['Source', '来源'],
    figure: ['Figure', '图'],
  };
  const normalized = kind.trim().toLowerCase();
  const label = labels[normalized];
  if (label) {
    return lang === 'cn' ? label[1] : label[0];
  }
  if (lang === 'cn') {
    return '证据';
  }
  return kind
    .trim()
    .replace(/[_-]+/g, ' ')
    .replace(/\b\w/g, (letter) => letter.toUpperCase()) || 'Evidence';
}

function escapeRegExp(value: string): string {
  return value.replace(/[.*+?^${}()|[\]\\]/g, '\\$&');
}

/** Remove generated stage wrappers from evidence snippets before display. */
export function cleanEvidenceSnippet(text: string, reportTitle = ''): string {
  const value = text.trim();
  if (!value) {
    return '';
  }
  if (reportTitle) {
    const exact = new RegExp(
      `^(?:Model|Method|Result|Finding) formula context in ${escapeRegExp(reportTitle)}:\\s*`,
      'i',
    );
    const stripped = value.replace(exact, '').trim();
    if (stripped !== value) {
      return stripped;
    }
  }
  // Keep a fallback for older payloads whose title differs from current metadata.
  return value.replace(/^(?:Model|Method|Result|Finding) formula context in .+?:\s*/i, '').trim();
}

/** Localise an evidence snippet while suppressing generated filler. */
export function displayEvidenceSnippet(
  lang: Lang,
  text: string,
  englishText = '',
  reportTitle = '',
): string {
  const localized = cleanEvidenceSnippet(text, reportTitle);
  if (isGeneratedMechanismDatasetSnippet(localized)) {
    return '';
  }
  if (lang === 'cn' && (isPlaceholderText(localized) || isLatexResidue(localized) || !localized)) {
    const english = cleanEvidenceSnippet(englishText, reportTitle);
    return isPlaceholderText(english) || isLatexResidue(english) || isGeneratedMechanismDatasetSnippet(english) ? '' : english;
  }
  return isPlaceholderText(localized) || isLatexResidue(localized) ? '' : localized;
}

// The web-data fallback uses this stable series id and derived asset provenance
// when a report has no research dataset. It must never be presented as a plot.
export function isGeneratedAssetDataset(dataset: DatasetMeta): boolean {
  return dataset.series_id.trim().toLowerCase() === 'asset-size-profile'
    && dataset.provenance.type.trim().toLowerCase() === 'derived'
    && dataset.provenance.source.trim().toLowerCase().startsWith('assets:');
}

const GENERATED_MATH_STAGES = new Set([
  'derivation link',
  'distribution setup',
  'model constraint',
  'spectral / inversion step',
  '推导连接',
  '分布定义',
  '模型约束',
  '谱分解 / 反演步骤',
]);

const GENERATED_MATH_DESCRIPTIONS = new Set([
  'adds a relation that links neighboring steps in the derivation chain.',
  'defines first-passage probability objects used by later diagnostics.',
  'states the structural constraints and parameter ranges of the model.',
  'provides analytic inversion machinery for computing trajectories.',
  '补充连接推导相邻步骤的关系式。',
  '定义后续诊断所依赖的首达时间概率对象。',
  '给出模型结构约束与参数范围。',
  '提供用于计算轨迹分布的解析反演机制。',
]);

export function isGeneratedMathStoryStage(value: string): boolean {
  return GENERATED_MATH_STAGES.has(value.replace(/\s+/g, ' ').trim().toLowerCase());
}

export function isGeneratedMathStoryDescription(value: string): boolean {
  return GENERATED_MATH_DESCRIPTIONS.has(value.replace(/\s+/g, ' ').trim().toLowerCase());
}

export function isGenericMathStoryContext(value: string): boolean {
  const normalized = value.replace(/\s+/g, ' ').trim().toLowerCase();
  return normalized === 'overview' || normalized === '概览' || normalized === 'fallback' || normalized === '兜底';
}

export function isReaderDataset(dataset: DatasetMeta): boolean {
  if (isGeneratedAssetDataset(dataset) || /schema/i.test(dataset.series_id)) {
    return false;
  }
  // Only charts with a written caption are offered to readers. Automatic picks
  // from raw tables carry internal column names and no explanation.
  if (!dataset.caption || !dataset.caption.trim()) {
    return false;
  }
  const points = typeof dataset.point_count === 'number' ? dataset.point_count : 3;
  const numericX = typeof dataset.numeric_x_count === 'number' ? dataset.numeric_x_count : 3;
  return points >= 3 && numericX >= 3;
}

// Title to show: the Chinese title when the generator produced a real one,
// otherwise the English title.
export function displayTitle(lang: Lang, metaLang: ReportMeta | null, metaEn: ReportMeta | null, reportId: string): string {
  const own = metaLang?.title ?? '';
  if (lang === 'cn' && isPlaceholderText(own)) {
    return metaEn?.title || reportId;
  }
  return own || metaEn?.title || reportId;
}

export function writtenReports(index: WebIndex) {
  const status = loadRegistryStatus();
  return index.reports.filter((row) => (status[row.report_id] ?? 'active') !== 'wip');
}

export function scaffoldReports(index: WebIndex) {
  const status = loadRegistryStatus();
  return index.reports.filter((row) => status[row.report_id] === 'wip');
}
