// Reader-facing layer of the atlas: which reports are written up, how they are
// grouped, which three to open first, and where each report's PDF lives.
// Everything here is presentation; report text and data come from public/data/v1.
import fs from 'fs';
import path from 'path';
import type { Lang, ReportMeta, WebIndex } from '@/types';

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
    reportId: 'ring_lazy_jump_ext',
    en: 'How the strength β of the shortcut moves both peaks, at N\u00a0=\u00a0100, with scans over ring size and a Monte Carlo check of the trajectory classes.',
    cn: '捷径强度 β 如何移动两个峰：N\u00a0=\u00a0100 时的扫描，环长 N 的扫描，以及用蒙特卡洛核对轨迹分类。',
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
    id: 'smet-phd',
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
  return (
    t.length === 0 ||
    /WIP scaffold|not yet started|summary placeholder|^该研究报告：|[a-z0-9]+_[a-z0-9_]+\s*研究报告/.test(t)
  );
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
