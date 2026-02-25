import fs from 'fs';
import path from 'path';
import type {
  AgentManifest,
  BookBackbone,
  BookChapter,
  BookClaimCoverage,
  BookManifest,
  ContentMap,
  FigureRecord,
  GlossaryPayload,
  Lang,
  ReportMeta,
  ReportNetwork,
  TheoryMap,
  TranslationQC,
  WebIndex,
} from '@/types';
import { withBasePath } from '@/lib/url';

const DATA_ROOT = path.join(process.cwd(), 'public', 'data', 'v1');
function readJson<T>(filePath: string): T | null {
  if (!fs.existsSync(filePath)) {
    return null;
  }
  return JSON.parse(fs.readFileSync(filePath, 'utf-8')) as T;
}

export function loadIndex(): WebIndex {
  const fallback: WebIndex = {
    version: 'v1',
    generated_at: new Date(0).toISOString(),
    reports: [],
  };
  return readJson<WebIndex>(path.join(DATA_ROOT, 'index.json')) ?? fallback;
}

export function loadReportMeta(reportId: string, lang: Lang): ReportMeta | null {
  const reportDir = path.join(DATA_ROOT, 'reports', reportId);
  if (lang === 'cn') {
    return (
      readJson<ReportMeta>(path.join(reportDir, 'meta.cn.json')) ??
      readJson<ReportMeta>(path.join(reportDir, 'meta.json'))
    );
  }
  return readJson<ReportMeta>(path.join(reportDir, 'meta.json'));
}

export function loadFigures(reportId: string): FigureRecord[] {
  return readJson<FigureRecord[]>(path.join(DATA_ROOT, 'reports', reportId, 'figures.json')) ?? [];
}

export function loadAgentManifest(): AgentManifest | null {
  return readJson<AgentManifest>(path.join(DATA_ROOT, 'agent', 'manifest.json'));
}

export function loadTheoryMap(): TheoryMap {
  return (
    readJson<TheoryMap>(path.join(DATA_ROOT, 'theory_map.json')) ?? {
      version: 'v1',
      generated_at: new Date(0).toISOString(),
      cards: [],
      consistency_checks: [],
    }
  );
}

export function loadReportNetwork(): ReportNetwork {
  return (
    readJson<ReportNetwork>(path.join(DATA_ROOT, 'report_network.json')) ?? {
      version: 'v1',
      generated_at: new Date(0).toISOString(),
      notion_labels: {},
      group_paths: [],
      global_storyline: {
        label_en: '',
        label_cn: '',
        report_ids: [],
      },
      reports: [],
    }
  );
}

export function loadContentMap(): ContentMap {
  return (
    readJson<ContentMap>(path.join(DATA_ROOT, 'content_map.json')) ?? {
      version: 'v1',
      generated_at: new Date(0).toISOString(),
      report_count: 0,
      arcs: [],
      claims: [],
      report_guides: [],
      consistency_checks: [],
    }
  );
}

export function loadBookManifest(): BookManifest | null {
  return readJson<BookManifest>(path.join(DATA_ROOT, 'book', 'book_manifest.json'));
}

export function loadBookChapter(chapterId: string): BookChapter | null {
  return readJson<BookChapter>(path.join(DATA_ROOT, 'book', 'chapters', `${chapterId}.json`));
}

export function loadBookBackbone(): BookBackbone | null {
  return readJson<BookBackbone>(path.join(DATA_ROOT, 'book', 'backbone.json'));
}

export function loadBookClaimCoverage(): BookClaimCoverage | null {
  return readJson<BookClaimCoverage>(path.join(DATA_ROOT, 'book', 'book_claim_coverage.json'));
}

export function loadBookToc(): { version: string; generated_at: string; en: Array<{ chapter_id: string; order: number; title: string; path: string }>; cn: Array<{ chapter_id: string; order: number; title: string; path: string }>; } | null {
  return readJson(path.join(DATA_ROOT, 'book', 'toc.json'));
}

export function loadGlossary(): GlossaryPayload | null {
  return readJson<GlossaryPayload>(path.join(DATA_ROOT, 'glossary', 'terms.json'));
}

export function loadTranslationQC(): TranslationQC | null {
  return readJson<TranslationQC>(path.join(DATA_ROOT, 'agent', 'translation_qc.json'));
}

export function groupReports(index: WebIndex): Record<string, WebIndex['reports']> {
  return index.reports.reduce<Record<string, WebIndex['reports']>>((acc, item) => {
    if (!acc[item.group]) {
      acc[item.group] = [];
    }
    acc[item.group].push(item);
    return acc;
  }, {});
}

export function localizedText(lang: Lang, en: string, cn: string): string {
  return lang === 'cn' ? cn : en;
}

export function prefixPath(prefix: string, segment: string): string {
  if (!prefix) {
    return segment;
  }
  if (segment === '/') {
    return `${prefix}/`;
  }
  return `${prefix}${segment}`;
}
export { withBasePath };
