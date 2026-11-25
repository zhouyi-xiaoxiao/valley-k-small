import Link from 'next/link';
import katex from 'katex';
import { AppShell } from '@/components/AppShell';
import { ReportPlotPanel } from '@/components/ReportPlotPanel';
import {
  loadAgentManifest,
  loadBookBackbone,
  loadBookManifest,
  loadContentMap,
  loadFigures,
  loadGlossary,
  loadIndex,
  loadRepoSync,
  loadReportNetwork,
  loadReportMeta,
  loadTheoryMap,
  localizedText,
  prefixPath,
  withBasePath,
} from '@/lib/content';
import { KATEX_MACROS } from '@/lib/latex';
import {
  FAMILY_ORDER,
  OWNER_SITE,
  OWNER_SITE_ZH,
  SUPERSEDED_BY,
  formatDay,
  START_HERE,
  displayTitle,
  familyLabel,
  familyNote,
  isPlaceholderText,
  reportFamily,
  loadRegistryStatus,
  scaffoldReports,
  writtenReports,
} from '@/lib/atlas';
import { PdfLinks } from '@/components/PdfLinks';
import type { AssetRecord, ContentMap, Lang, ReportMeta, ReportNetwork } from '@/types';

type LatexRenderResult = {
  html: string;
  error: string | null;
};

function escapeHtml(value: string): string {
  return value
    .replaceAll('&', '&amp;')
    .replaceAll('<', '&lt;')
    .replaceAll('>', '&gt;')
    .replaceAll('"', '&quot;')
    .replaceAll("'", '&#39;');
}

function renderLatex(latex: string, displayMode = true): LatexRenderResult {
  try {
    return {
      html: katex.renderToString(latex, {
        throwOnError: true,
        displayMode,
        strict: 'error',
        macros: KATEX_MACROS,
      }),
      error: null,
    };
  } catch (error: unknown) {
    const reason = error instanceof Error ? error.message : 'Unknown KaTeX parse error';
    return {
      html: `<code>${escapeHtml(latex)}</code>`,
      error: reason,
    };
  }
}

function renderGlossaryFormula(latex: string, lang: Lang, context: string) {
  const rendered = renderLatex(latex, false);
  return (
    <>
      <div
        className="math-inline"
        dangerouslySetInnerHTML={{
          __html: rendered.html,
        }}
      />
      {rendered.error ? renderFormulaWarning(lang, context, rendered.error) : null}
    </>
  );
}

function renderMathBlockCard(
  block: { context: string; lang: string; latex: string; source_path: string },
  key: string,
) {
  const rendered = renderLatex(block.latex);

  return (
    <article key={key} className="card">
      {block.context && !/fallback/i.test(block.context) ? (
        <p>
          <span className="badge">{block.context}</span>
        </p>
      ) : null}
      <div
        className="math-block"
        dangerouslySetInnerHTML={{
          __html: rendered.html,
        }}
      />
      {rendered.error ? renderFormulaWarning(block.lang === 'cn' ? 'cn' : 'en', block.source_path, rendered.error) : null}
      <details>
        <summary>{block.lang === 'cn' ? '公式来源' : 'Formula source'}</summary>
        <p style={{ marginBottom: 0 }}>
          <code>{block.source_path}</code>
        </p>
      </details>
    </article>
  );
}

function renderFormulaWarning(lang: Lang, context: string, error: string) {
  return (
    <details style={{ marginBottom: '0.5rem' }}>
      <summary>{localizedText(lang, 'Formula render warning (KaTeX)', '公式渲染警告（KaTeX）')}</summary>
      <p style={{ margin: '0.45rem 0 0.3rem' }}>
        {localizedText(lang, 'Fallback to raw LaTeX text. Context:', '已回退为原始 LaTeX 文本。上下文：')} <code>{context}</code>
      </p>
      <pre style={{ whiteSpace: 'pre-wrap', margin: 0 }}>{error}</pre>
    </details>
  );
}

function groupAssets(assets: AssetRecord[]) {
  const groups = new Map<string, { primary: AssetRecord; variants: AssetRecord[] }>();
  for (const asset of assets) {
    const key = `${asset.kind}:${asset.label.toLowerCase()}`;
    const existing = groups.get(key);
    if (!existing) {
      groups.set(key, { primary: asset, variants: [asset] });
      continue;
    }
    existing.variants.push(asset);
    if (asset.size > existing.primary.size) {
      existing.primary = asset;
    }
  }
  return [...groups.values()].sort((a, b) => b.primary.size - a.primary.size);
}

function compactText(text: string, maxChars: number): string {
  const normalized = text.replace(/\s+/g, ' ').trim();
  if (normalized.length <= maxChars) {
    return normalized;
  }
  const clipped = normalized.slice(0, maxChars);
  const stop = Math.max(clipped.lastIndexOf('. '), clipped.lastIndexOf('。'), clipped.lastIndexOf('; '), clipped.lastIndexOf('；'));
  if (stop > maxChars * 0.45) {
    // Ends on a complete sentence: no ellipsis.
    return clipped.slice(0, stop + 1).trim().replace(/;$/, '.').replace(/；$/, '。');
  }
  const space = clipped.lastIndexOf(' ');
  const cut = space > maxChars * 0.6 ? clipped.slice(0, space) : clipped;
  return `${cut.replace(/[\s,;:.，；：。、]+$/, '')}…`;
}

function extractReportPreview(meta: ReportMeta | null, reportId: string, lang: Lang): { title: string; summary: string } {
  if (!meta) {
    return {
      title: reportId,
      summary:
        lang === 'cn'
          ? `该报告 ${reportId} 已收录，可进入详情页查看数学逻辑链与交互图。`
          : `Report ${reportId} is indexed. Open it to view mathematical logic and interactive plots.`,
    };
  }
  return {
    title: meta.title || reportId,
    summary: compactText(meta.summary || '', 280),
  };
}

function isPlaceholderCardSummary(heading: string, summary: string): boolean {
  const normalizedHeading = heading.replace(/\s+/g, ' ').trim().toLowerCase();
  const normalizedSummary = summary.replace(/\s+/g, ' ').trim().toLowerCase();
  if (!normalizedSummary) {
    return true;
  }
  if (normalizedSummary === normalizedHeading) {
    return true;
  }
  if (/section summary\.?$/i.test(normalizedSummary)) {
    return true;
  }
  if (/fallback narrative card/i.test(normalizedSummary)) {
    return true;
  }
  if (/^(figures?|tables?):\s*this section (interprets|summarizes|presents)/i.test(normalizedSummary)) {
    return true;
  }
  if (/^this section (interprets|summarizes|presents)\s+(the\s+)?(key\s+)?(figures?|tables?)/i.test(normalizedSummary)) {
    return true;
  }
  if (/^本节(主要)?(解释|总结|汇总|呈现).*(图|表)/.test(normalizedSummary)) {
    return true;
  }
  const pathHits = normalizedSummary.match(
    /(?:reports|inputs|figures|data|scripts|code|artifacts)\/[\w./-]+\.(?:tex|pdf|json|csv|png|jpg|jpeg|svg|md|py|npz)/g,
  );
  if (pathHits && (pathHits.length >= 2 || normalizedSummary.length < 160)) {
    return true;
  }
  if (normalizedSummary.length < 18) {
    return true;
  }
  if (/^research report [a-z0-9_]+\.?$/.test(normalizedSummary) || /^[a-z0-9_]+\s*研究报告。?$/.test(normalizedSummary)) {
    return true;
  }
  return false;
}

function pruneSectionCards(cards: Array<{ heading: string; summary: string; source_path: string }>) {
  const byHeading = new Map<string, { heading: string; summary: string; source_path: string }>();
  const summaryQuality = (summary: string) => {
    const normalized = summary.replace(/\s+/g, ' ').trim().toLowerCase();
    let score = 0;
    if (!normalized) {
      score -= 50;
    }
    score += Math.min(48, normalized.length);
    if (/this section /i.test(normalized)) {
      score -= 8;
    }
    if (/本节/.test(normalized)) {
      score -= 6;
    }
    if (/asset size profile|manifest|placeholder|fallback/i.test(normalized)) {
      score -= 12;
    }
    if (
      /(?:reports|inputs|figures|data|scripts|code|artifacts)\/[\w./-]+\.(?:tex|pdf|json|csv|png|jpg|jpeg|svg|md|py|npz)/i.test(
        normalized,
      )
    ) {
      score -= 12;
    }
    return score;
  };

  for (const card of cards) {
    if (isPlaceholderCardSummary(card.heading, card.summary)) {
      continue;
    }
    const headingKey = card.heading.replace(/\s+/g, ' ').trim().toLowerCase();
    if (!headingKey) {
      continue;
    }
    const current = byHeading.get(headingKey);
    if (!current) {
      byHeading.set(headingKey, card);
      continue;
    }
    if (summaryQuality(card.summary) > summaryQuality(current.summary)) {
      byHeading.set(headingKey, card);
    }
  }
  return [...byHeading.values()];
}

function lookupReportTitle(reportId: string, lang: Lang, network: ReportNetwork): string {
  const node = network.reports.find((row) => row.report_id === reportId);
  if (node) {
    return lang === 'cn' ? node.title_cn : node.title_en;
  }
  const meta = loadReportMeta(reportId, lang);
  return meta?.title || reportId;
}

function renderConnectionReason(
  lang: Lang,
  network: ReportNetwork,
  row: {
    adjacent_in_track: boolean;
    shared_notion_ids: string[];
  },
) {
  const reasonBadges: string[] = [];
  if (row.adjacent_in_track) {
    reasonBadges.push(localizedText(lang, 'adjacent in track', '同轨道相邻'));
  }
  const notionLabels = row.shared_notion_ids
    .slice(0, 3)
    .map((notionId) => network.notion_labels[notionId])
    .filter(Boolean)
    .map((payload) => (lang === 'cn' ? payload.label_cn : payload.label_en));
  reasonBadges.push(...notionLabels);
  if (reasonBadges.length === 0) {
    return null;
  }
  return (
    <p style={{ marginTop: '0.25rem' }}>
      {reasonBadges.map((badge) => (
        <span key={badge} className="badge" style={{ marginRight: '0.35rem' }}>
          {badge}
        </span>
      ))}
    </p>
  );
}

function reportClaims(contentMap: ContentMap, reportId: string) {
  return contentMap.claims.filter((row) => row.report_id === reportId);
}

function reportGuide(contentMap: ContentMap, reportId: string) {
  return contentMap.report_guides.find((row) => row.report_id === reportId) ?? null;
}

function reportArcs(contentMap: ContentMap, reportId: string) {
  return contentMap.arcs.filter((row) => row.report_ids.includes(reportId));
}

function reportBookPlacement(reportId: string, lang: Lang, manifest: ReturnType<typeof loadBookManifest>) {
  if (!manifest) {
    return null;
  }
  const mapping = manifest.report_chapter_map?.[reportId];
  // listed === false: no chapter discusses the report (fallback mapping only).
  if (!mapping || mapping.listed === false) {
    return null;
  }
  const chapters = manifest.chapters;
  const chapterTitle = (chapterId: string | null) => {
    if (!chapterId) {
      return '';
    }
    const row = chapters.find((item) => item.chapter_id === chapterId);
    return row ? (lang === 'cn' ? row.title_cn : row.title_en) : chapterId;
  };
  const primary = manifest.chapters.find((row) => row.chapter_id === mapping.primary_chapter_id);
  if (!primary) {
    return null;
  }
  return {
    chapterId: primary.chapter_id,
    chapterTitle: lang === 'cn' ? primary.title_cn : primary.title_en,
    previousChapterId: primary.previous_chapter_id,
    previousChapterTitle: chapterTitle(primary.previous_chapter_id),
    nextChapterId: primary.next_chapter_id,
    nextChapterTitle: chapterTitle(primary.next_chapter_id),
    otherChapters: mapping.chapter_ids
      .filter((chapterId) => chapterId !== primary.chapter_id)
      .map((chapterId) => ({ chapterId, title: chapterTitle(chapterId) })),
  };
}

const CLAIM_STAGE_ORDER: Record<'model' | 'method' | 'result' | 'finding', number> = {
  model: 0,
  method: 1,
  result: 2,
  finding: 3,
};

function isImageFigure(webPath: string): boolean {
  return /\.(png|jpg|jpeg|webp|svg)$/i.test(webPath);
}

function formatTimestamp(lang: Lang, iso: string): string {
  const locale = lang === 'cn' ? 'zh-CN' : 'en-GB';
  return `${new Intl.DateTimeFormat(locale, {
    dateStyle: 'medium',
    timeStyle: 'medium',
    timeZone: 'UTC',
  }).format(new Date(iso))} UTC`;
}

function formatBytes(size: number): string {
  if (!Number.isFinite(size) || size <= 0) {
    return '0 B';
  }
  const units = ['B', 'KB', 'MB', 'GB'];
  let value = size;
  let idx = 0;
  while (value >= 1024 && idx < units.length - 1) {
    value /= 1024;
    idx += 1;
  }
  return `${value.toFixed(value >= 100 || idx === 0 ? 0 : 1)} ${units[idx]}`;
}

function summarizeCheckDetails(details: unknown, lang: Lang): string[] {
  if (details === null || details === undefined) {
    return [];
  }
  if (Array.isArray(details)) {
    if (details.length === 0) {
      return [localizedText(lang, 'No issues detected.', '未发现问题。')];
    }
    const preview = details.slice(0, 3).map((item) => {
      if (typeof item === 'string') {
        return item;
      }
      if (item && typeof item === 'object') {
        const row = item as { report_id?: string; text?: string; latex?: string; count?: number };
        if (row.report_id) {
          return `${row.report_id}: ${row.count ?? ''}`.trim();
        }
        if (row.text) {
          return compactText(row.text, 100);
        }
        if (row.latex) {
          return compactText(row.latex, 100);
        }
      }
      return compactText(String(item), 100);
    });
    if (details.length > preview.length) {
      preview.push(
        localizedText(
          lang,
          `${details.length - preview.length} more items in raw JSON.`,
          `其余 ${details.length - preview.length} 条见原始 JSON。`,
        ),
      );
    }
    return preview;
  }
  if (typeof details === 'object') {
    const payload = details as Record<string, unknown>;
    const lines: string[] = [];
    const preferredKeys = ['redundant_count', 'shared_core_count', 'unmapped_report_ids', 'duplicate_count', 'total_assets'];
    for (const key of preferredKeys) {
      if (payload[key] !== undefined) {
        lines.push(`${key}: ${String(payload[key])}`);
      }
    }
    if (lines.length > 0) {
      return lines;
    }
    for (const [key, value] of Object.entries(payload).slice(0, 5)) {
      if (Array.isArray(value)) {
        lines.push(`${key}: ${value.length}`);
      } else if (value && typeof value === 'object') {
        lines.push(`${key}: ${Object.keys(value as Record<string, unknown>).length}`);
      } else {
        lines.push(`${key}: ${String(value)}`);
      }
    }
    if (Object.keys(payload).length > 5) {
      lines.push(
        localizedText(
          lang,
          `${Object.keys(payload).length - 5} more fields in raw JSON.`,
          `其余 ${Object.keys(payload).length - 5} 个字段见原始 JSON。`,
        ),
      );
    }
    return lines;
  }
  return [String(details)];
}

function rawCheckPayloadPreview(details: unknown, lang: Lang): string {
  let raw = '';
  try {
    raw = JSON.stringify(details, null, 2);
  } catch {
    raw = String(details);
  }
  const maxChars = 1800;
  if (raw.length <= maxChars) {
    return raw;
  }
  const clipped = raw.slice(0, maxChars);
  const cut = Math.max(clipped.lastIndexOf('\n'), Math.floor(maxChars * 0.65));
  const body = clipped.slice(0, Math.max(0, cut)).trimEnd();
  const omitted = raw.length - body.length;
  return `${body}\n\n${localizedText(
    lang,
    `... truncated ${omitted} chars. Open /data/v1/theory_map.json for full payload.`,
    `... 已截断 ${omitted} 个字符。完整内容请查看 /data/v1/theory_map.json。`,
  )}`;
}

function stageLabel(lang: Lang, stage: string): string {
  const key = stage.toLowerCase();
  if (key === 'model') {
    return localizedText(lang, 'Model', '模型');
  }
  if (key === 'method') {
    return localizedText(lang, 'Method', '方法');
  }
  if (key === 'result') {
    return localizedText(lang, 'Result', '结果');
  }
  if (key === 'finding') {
    return localizedText(lang, 'Finding', '发现');
  }
  return stage;
}

function extractFormulaCoverage(map: ReturnType<typeof loadTheoryMap>): Record<string, number> {
  const target = map.consistency_checks.find((item) => item.check === 'all_reports_have_formula');
  if (!target || typeof target.details !== 'object' || Array.isArray(target.details) || target.details === null) {
    return {};
  }
  const coverage: Record<string, number> = {};
  for (const [key, value] of Object.entries(target.details as Record<string, unknown>)) {
    const count = typeof value === 'number' ? value : Number(value);
    if (Number.isFinite(count)) {
      coverage[key] = Math.max(0, Math.round(count));
    }
  }
  return coverage;
}

function extractDuplicationBuckets(map: ReturnType<typeof loadTheoryMap>) {
  const target = map.consistency_checks.find((item) => item.check === 'duplicate_math_signatures');
  const empty = { sharedCore: [] as Array<{ latex: string; count: number; report_ids: string[] }>, redundant: [] as Array<{ latex: string; count: number; report_ids: string[] }>, sharedCoreCount: 0, redundantCount: 0 };
  if (!target || typeof target.details !== 'object' || Array.isArray(target.details) || target.details === null) {
    return empty;
  }
  const details = target.details as Record<string, unknown>;
  const pickRows = (value: unknown) =>
    Array.isArray(value)
      ? value
          .map((row) => {
            if (!row || typeof row !== 'object') {
              return null;
            }
            const item = row as Record<string, unknown>;
            return {
              latex: String(item.latex ?? ''),
              count: Number(item.count ?? 0),
              report_ids: Array.isArray(item.report_ids) ? item.report_ids.map((rid) => String(rid)) : [],
            };
          })
          .filter((row): row is { latex: string; count: number; report_ids: string[] } => Boolean(row?.latex))
      : [];
  const sharedCore = pickRows(details.shared_core_signatures);
  const redundant = pickRows(details.redundant_signatures);
  return {
    sharedCore,
    redundant,
    sharedCoreCount: Number(details.shared_core_count ?? sharedCore.length) || sharedCore.length,
    redundantCount: Number(details.redundant_count ?? redundant.length) || redundant.length,
  };
}

function buildStageCoverageRows(contentMap: ContentMap, network: ReportNetwork) {
  const byReport = new Map<
    string,
    { model: number; method: number; result: number; finding: number; total: number }
  >();
  for (const claim of contentMap.claims) {
    const reportId = claim.report_id;
    const row = byReport.get(reportId) ?? { model: 0, method: 0, result: 0, finding: 0, total: 0 };
    const stage = claim.stage;
    if (stage in row) {
      row[stage] += 1;
    }
    row.total += 1;
    byReport.set(reportId, row);
  }
  const rows = network.reports.map((report) => ({
    report_id: report.report_id,
    title_en: report.title_en,
    title_cn: report.title_cn,
    coverage: byReport.get(report.report_id) ?? { model: 0, method: 0, result: 0, finding: 0, total: 0 },
  }));
  rows.sort((left, right) => right.coverage.total - left.coverage.total || left.report_id.localeCompare(right.report_id));
  return rows;
}

function buildNotionClaimDigests(map: ReturnType<typeof loadTheoryMap>, contentMap: ContentMap) {
  return map.cards.map((card) => {
    const claims = contentMap.claims
      .filter((claim) => card.report_ids.includes(claim.report_id))
      .sort((left, right) => {
        const stageDelta = CLAIM_STAGE_ORDER[left.stage] - CLAIM_STAGE_ORDER[right.stage];
        if (stageDelta !== 0) {
          return stageDelta;
        }
        return right.evidence.length - left.evidence.length;
      })
      .slice(0, 5);
    return {
      card,
      claims,
    };
  });
}

function compactLatex(latex: string): string {
  return compactText(latex.replace(/\s+/g, ' '), 120);
}

type FormulaPolicyRow = {
  report_id: string;
  group: string;
  formula_count: number;
  min_required: number;
  target: number;
  pass: boolean;
  exception_tag: string;
  exception_reason: string;
};

function extractFormulaPolicyRows(map: ReturnType<typeof loadTheoryMap>): FormulaPolicyRow[] {
  const target = map.consistency_checks.find((item) => item.check === 'formula_depth_policy');
  if (!target || typeof target.details !== 'object' || Array.isArray(target.details) || target.details === null) {
    return [];
  }
  const rows = (target.details as { rows?: unknown[] }).rows;
  if (!Array.isArray(rows)) {
    return [];
  }
  return rows
    .map((row) => {
      if (!row || typeof row !== 'object') {
        return null;
      }
      const item = row as Record<string, unknown>;
      return {
        report_id: String(item.report_id ?? ''),
        group: String(item.group ?? ''),
        formula_count: Number(item.formula_count ?? 0),
        min_required: Number(item.min_required ?? 1),
        target: Number(item.target ?? 1),
        pass: Boolean(item.pass),
        exception_tag: String(item.exception_tag ?? ''),
        exception_reason: String(item.exception_reason ?? ''),
      };
    })
    .filter((row): row is FormulaPolicyRow => Boolean(row?.report_id))
    .sort((left, right) => left.report_id.localeCompare(right.report_id));
}

export function renderReportsPage(lang: Lang, prefix: string) {
  const index = loadIndex();
  const bookManifest = loadBookManifest();
  const written = writtenReports(index);
  const scaffolds = scaffoldReports(index);
  const startIds = new Set(START_HERE.map((item) => item.reportId));
  const entry = (reportId: string) => {
    const meta = loadReportMeta(reportId, lang);
    const metaEn = loadReportMeta(reportId, 'en');
    const summary = (meta?.summary ?? '').replace(/\*\*/g, '');
    const mapping = bookManifest?.report_chapter_map?.[reportId];
    const chapterId = mapping && mapping.listed !== false ? mapping.primary_chapter_id : undefined;
    const chapter = chapterId ? bookManifest?.chapters.find((row) => row.chapter_id === chapterId) : undefined;
    const successorId = SUPERSEDED_BY[reportId];
    return {
      title: displayTitle(lang, meta, metaEn, reportId),
      summary: meta?.teaser ? meta.teaser : isPlaceholderText(summary) ? '' : compactText(summary, 520),
      chapter,
      successor: successorId
        ? { id: successorId, title: displayTitle(lang, loadReportMeta(successorId, lang), loadReportMeta(successorId, 'en'), successorId) }
        : null,
    };
  };

  return (
    <AppShell lang={lang} prefix={prefix}>
      <header className="page-head">
        <p className="kicker">{localizedText(lang, 'Reports', '报告')}</p>
        <h1>{localizedText(lang, 'All reports', '全部报告')}</h1>
        <p className="page-lede">
          {localizedText(
            lang,
            `${written.length} written reports on first-passage times, grouped by the setting they study. They are working research reports, not peer-reviewed papers. Each page gives the findings, interactive figures and mathematics; the PDF is the full report. New here? Begin with the three marked “start here”.`,
            `${written.length} 份已成文的首达时间报告，按所研究的模型分组。它们是研究工作报告，不是经过同行评审的论文。每页列出结论、交互图和数学推导，PDF 是报告全文。第一次来，可以先读标着「从这里开始」的三份。`,
          )}
        </p>
        <p className="page-note">
          {localizedText(
            lang,
            'Abbreviations: FPT, first-passage time (the step at which the walker first reaches a target); MFPT, mean first-passage time; MC, Monte Carlo simulation.',
            '缩写：FPT 指首达时间（游走者第一次到达目标的那一步）；MFPT 指平均首达时间；MC 指蒙特卡洛模拟。',
          )}
        </p>
      </header>

      {FAMILY_ORDER.map((family) => {
        const rows = written.filter((row) => reportFamily(row.report_id, row.group) === family);
        if (rows.length === 0) {
          return null;
        }
        return (
          <section key={family} className="family-section" aria-labelledby={`family-${family}`}>
            <h2 id={`family-${family}`}>
              {familyLabel(lang, family)} <span className="count">{rows.length}</span>
            </h2>
            <p className="family-note">{familyNote(lang, family)}</p>
            <ul className="report-list">
              {rows.map((row) => {
                const info = entry(row.report_id);
                return (
                  <li key={row.report_id} className="report-row">
                    <h3>
                      <Link href={prefixPath(prefix, `/reports/${row.report_id}`)}>{info.title}</Link>
                      {startIds.has(row.report_id) ? (
                        <span className="tag">{localizedText(lang, 'start here', '从这里开始')}</span>
                      ) : null}
                    </h3>
                    {info.summary ? <p>{info.summary}</p> : null}
                    {info.successor ? (
                      <p className="superseded-note">
                        {localizedText(lang, 'Superseded by ', '已被新版取代：')}
                        <Link href={prefixPath(prefix, `/reports/${info.successor.id}`)}>{info.successor.title}</Link>
                      </p>
                    ) : null}
                    <p className="report-row-meta">
                      <PdfLinks lang={lang} reportId={row.report_id} />
                      {info.chapter ? (
                        <span>
                          {localizedText(lang, 'In the book: ', '书中：')}
                          <Link href={prefixPath(prefix, `/book/${info.chapter.chapter_id}`)}>
                            {lang === 'cn' ? info.chapter.title_cn : info.chapter.title_en}
                          </Link>
                        </span>
                      ) : null}
                    </p>
                  </li>
                );
              })}
            </ul>
          </section>
        );
      })}

      {scaffolds.length > 0 ? (
        <section className="family-section" aria-labelledby="family-wip">
          <h2 id="family-wip">
            {localizedText(lang, 'In progress', '进行中')} <span className="count">{scaffolds.length}</span>
          </h2>
          <p className="family-note">
            {localizedText(
              lang,
              'Reports whose scope is set but which are not written up yet. Their pages show what exists so far, which may be only a plan.',
              '范围已经定下、但尚未成文的报告。它们的页面只展示目前已有的内容，有些还只是计划。',
            )}
          </p>
          <details className="wip-details">
            <summary>{localizedText(lang, `Show the ${scaffolds.length} reports in progress`, `展开 ${scaffolds.length} 份进行中的报告`)}</summary>
            <ul className="wip-list">
              {scaffolds.map((row) => (
                <li key={row.report_id}>
                  <Link href={prefixPath(prefix, `/reports/${row.report_id}`)}>{entry(row.report_id).title}</Link>
                </li>
              ))}
            </ul>
          </details>
        </section>
      ) : null}
    </AppShell>
  );
}

export function renderReportPage(lang: Lang, prefix: string, reportId: string) {
  const meta = loadReportMeta(reportId, lang);
  if (!meta) {
    return (
      <AppShell lang={lang} prefix={prefix}>
        <section className="card">
          <h1>{localizedText(lang, 'Report not found', '未找到报告')}</h1>
          <p>{reportId}</p>
        </section>
      </AppShell>
    );
  }

  const figures = loadFigures(reportId);
  const network = loadReportNetwork();
  const contentMap = loadContentMap();
  const bookManifest = loadBookManifest();
  const networkNode = network.reports.find((row) => row.report_id === reportId);
  const bookPlacement = reportBookPlacement(reportId, lang, bookManifest);
  const claims = reportClaims(contentMap, reportId);
  const claimsOrdered = [...claims].sort((left, right) => {
    const leftRank = CLAIM_STAGE_ORDER[left.stage] ?? 99;
    const rightRank = CLAIM_STAGE_ORDER[right.stage] ?? 99;
    if (leftRank !== rightRank) {
      return leftRank - rightRank;
    }
    return left.claim_id.localeCompare(right.claim_id);
  });
  const arcsForReport = reportArcs(contentMap, reportId);
  const guide = reportGuide(contentMap, reportId);
  const groupedAssets = groupAssets(meta.assets);
  const duplicateAssetCount = Math.max(0, meta.assets.length - groupedAssets.length);
  const topFindings = meta.key_findings.slice(0, 5);
  const extraFindings = meta.key_findings.slice(5);
  // Formula cards that only repeat the logic chain are not shown twice.
  const storyLatex = new Set(meta.math_story.map((item) => item.latex.replace(/\s+/g, '')));
  const extraMathBlocks = meta.math_blocks.filter((block) => !storyLatex.has(block.latex.replace(/\s+/g, '')));
  const successorId = SUPERSEDED_BY[reportId];
  const successorTitle = successorId
    ? displayTitle(lang, loadReportMeta(successorId, lang), loadReportMeta(successorId, 'en'), successorId)
    : '';
  const filteredSections = pruneSectionCards(meta.section_cards);
  const sectionsPreview = filteredSections.slice(0, 6);
  const sectionsExtra = filteredSections.slice(6);
  const family = reportFamily(reportId, loadIndex().reports.find((row) => row.report_id === reportId)?.group ?? '');
  const isWip = loadRegistryStatus()[reportId] === 'wip';
  const title = displayTitle(lang, meta, loadReportMeta(reportId, 'en'), reportId);
  const rawSummary = (meta.summary || '').replace(/\*\*/g, '');
  // Scaffold reports carry generated template text; show only the status note for them.
  const summary = isWip || isPlaceholderText(rawSummary) ? '' : rawSummary;
  const hasNarrative = !isWip && [meta.narrative.model_overview, meta.narrative.method_overview, meta.narrative.result_overview].some(
    (text) => text && !isPlaceholderText(text),
  );
  const navItems = [
    { id: 'findings', label: localizedText(lang, 'Findings', '结论'), show: topFindings.length > 0 },
    { id: 'interactive', label: localizedText(lang, 'Interactive figures', '交互图'), show: true },
    { id: 'figures', label: localizedText(lang, 'Figures', '图'), show: figures.length > 0 },
    { id: 'math-chain', label: localizedText(lang, 'Mathematics', '数学'), show: meta.math_story.length > 0 },
    { id: 'where-it-fits', label: localizedText(lang, 'Where it fits', '全局位置'), show: true },
    { id: 'working-record', label: localizedText(lang, 'Working record', '工作记录'), show: true },
  ].filter((item) => item.show);

  return (
    <AppShell lang={lang} prefix={prefix}>
      <nav className="crumbs" aria-label={localizedText(lang, 'Breadcrumb', '路径')}>
        <Link href={prefixPath(prefix, '/reports')}>{localizedText(lang, '← All reports', '← 全部报告')}</Link>
      </nav>
      <header className="page-head report-head">
        <p className="kicker">
          {isWip ? localizedText(lang, 'In progress', '进行中') : familyLabel(lang, family)}
        </p>
        <h1>{title}</h1>
        {successorId ? (
          <p className="superseded-banner" role="note">
            <strong>{localizedText(lang, 'Superseded.', '已被取代。')}</strong>{' '}
            {localizedText(lang, 'This is the first version of this study; the revised version is ', '这是该研究的第一版；修订版见：')}
            <Link href={prefixPath(prefix, `/reports/${successorId}`)}>{successorTitle} →</Link>
          </p>
        ) : null}
        {!isWip ? (
          <p className="report-status">
            {localizedText(lang, 'Working research report · not peer-reviewed', '研究工作报告 · 未经同行评审')}
          </p>
        ) : null}
        {isWip ? (
          <p className="status-note">
            {localizedText(
              lang,
              'This report is in progress: its scope is set but it is not written up yet. What follows is what exists so far.',
              '这份报告仍在进行中：范围已经定下，但尚未成文。以下只是目前已有的内容。',
            )}
          </p>
        ) : null}
        {summary ? <p className="page-lede">{summary}</p> : null}
        <p className="report-row-meta">
          <PdfLinks lang={lang} reportId={reportId} />
          {bookPlacement ? (
            <span>
              {localizedText(lang, 'In the book: ', '书中：')}
              <Link href={prefixPath(prefix, `/book/${bookPlacement.chapterId}`)}>{bookPlacement.chapterTitle}</Link>
            </span>
          ) : null}
        </p>
        <nav className="quick-nav" aria-label={localizedText(lang, 'On this page', '本页内容')}>
          {navItems.map((item) => (
            <a key={item.id} href={`#${item.id}`}>
              {item.label}
            </a>
          ))}
        </nav>
      </header>

      {hasNarrative ? (
        <section className="report-overview" aria-label={localizedText(lang, 'Overview', '概览')}>
          <div>
            <h2>{localizedText(lang, 'Model', '模型')}</h2>
            <p>{meta.narrative.model_overview}</p>
          </div>
          <div>
            <h2>{localizedText(lang, 'Method', '方法')}</h2>
            <p>{meta.narrative.method_overview}</p>
          </div>
          <div>
            <h2>{localizedText(lang, 'Result', '结论')}</h2>
            <p>{meta.narrative.result_overview}</p>
          </div>
        </section>
      ) : null}

      {topFindings.length > 0 ? (
        <section id="findings" className="card section-enter" style={{ marginTop: '1rem' }}>
          <h3>{localizedText(lang, 'Key findings', '关键结论')}</h3>
          <ul>
            {topFindings.map((line) => (
              <li key={line}>{line}</li>
            ))}
          </ul>
          {extraFindings.length > 0 ? (
            <details>
              <summary>{localizedText(lang, 'Show remaining findings', '展开剩余结论')}</summary>
              <ul>
                {extraFindings.map((line) => (
                  <li key={`extra-${line}`}>{line}</li>
                ))}
              </ul>
            </details>
          ) : null}
        </section>
      ) : null}

      <div id="interactive" style={{ marginTop: '1rem' }}>
        <ReportPlotPanel reportId={reportId} datasets={meta.datasets} lang={lang} />
      </div>

      {figures.length > 0 ? (
        <section id="figures" className="card section-enter" style={{ marginTop: '1rem' }}>
          <h3>{localizedText(lang, 'Figures', '图')}</h3>
          {figures.some((fig) => isImageFigure(fig.web_path)) ? (
            <div className="grid grid-3">
              {figures
                .filter((fig) => isImageFigure(fig.web_path))
                .slice(0, 12)
                .map((fig) => {
                  const figTitle = (lang === 'cn' && fig.title_cn) || fig.title;
                  return (
                    <article key={fig.id} className="card">
                      <p>{figTitle}</p>
                      <a href={withBasePath(fig.web_path)} target="_blank" rel="noreferrer">
                        {/* eslint-disable-next-line @next/next/no-img-element */}
                        <img
                          src={withBasePath(fig.web_path)}
                          alt={figTitle}
                          style={{ width: '100%', borderRadius: '10px', border: '1px solid #d8ccb3' }}
                        />
                      </a>
                    </article>
                  );
                })}
            </div>
          ) : null}
          {figures.some((fig) => !isImageFigure(fig.web_path)) ? (
            <>
              <p className="muted">
                {localizedText(
                  lang,
                  'Each figure opens as a PDF in a new tab.',
                  '每张图都以 PDF 形式在新标签页中打开。',
                )}
              </p>
              <ul className="figure-list">
                {figures
                  .filter((fig) => !isImageFigure(fig.web_path))
                  .slice(0, 8)
                  .map((fig) => (
                    <li key={fig.id}>
                      <a href={withBasePath(fig.web_path)} target="_blank" rel="noreferrer">
                        {(lang === 'cn' && fig.title_cn) || fig.title}
                      </a>
                    </li>
                  ))}
              </ul>
              {figures.filter((fig) => !isImageFigure(fig.web_path)).length > 8 ? (
                <details>
                  <summary>
                    {localizedText(lang, 'More figures', '更多图')} (
                    {figures.filter((fig) => !isImageFigure(fig.web_path)).length - 8})
                  </summary>
                  <ul className="figure-list">
                    {figures
                      .filter((fig) => !isImageFigure(fig.web_path))
                      .slice(8)
                      .map((fig) => (
                        <li key={`extra-${fig.id}`}>
                          <a href={withBasePath(fig.web_path)} target="_blank" rel="noreferrer">
                            {(lang === 'cn' && fig.title_cn) || fig.title}
                          </a>
                        </li>
                      ))}
                  </ul>
                </details>
              ) : null}
            </>
          ) : null}
        </section>
      ) : null}

      <section id="math-chain" className="card section-enter" style={{ marginTop: '1rem' }}>
        <h3>{localizedText(lang, 'Mathematics', '数学')}</h3>
        <p className="muted">
          {localizedText(
            lang,
            'From model assumptions to interpretation in a short, ordered chain.',
            '从模型假设到解释结论，按步骤给出最短逻辑链。',
          )}
        </p>
        <div className="grid grid-2">
          {meta.math_story.map((item, idx) => {
            const rendered = renderLatex(item.latex);
            return (
              <article key={`${item.stage}-${idx}`} className="card">
                <h4>{item.stage}</h4>
                <p>{item.description}</p>
                <div
                  className="math-block"
                  dangerouslySetInnerHTML={{
                    __html: rendered.html,
                  }}
                />
                {rendered.error ? renderFormulaWarning(lang, item.context, rendered.error) : null}
                {item.context && !/fallback/i.test(item.context) && item.context !== item.stage ? (
                  <p style={{ marginBottom: 0 }}>
                    <span className="badge">{item.context}</span>
                  </p>
                ) : null}
              </article>
            );
          })}
        </div>
      </section>

      {extraMathBlocks.length > 0 ? (
        <section id="math-principles" className="card section-enter" style={{ marginTop: '1rem' }}>
          <h3>{localizedText(lang, 'More formulas from the report', '报告中的其他公式')}</h3>
          <div className="grid grid-2">
            {extraMathBlocks.slice(0, 6).map((block, idx) => renderMathBlockCard(block, `${block.source_path}-${idx}`))}
          </div>
          {extraMathBlocks.length > 6 ? (
            <details style={{ marginTop: '0.8rem' }}>
              <summary>{localizedText(lang, 'Show remaining formulas', '展开剩余公式')}</summary>
              <div className="grid grid-2" style={{ marginTop: '0.8rem' }}>
                {extraMathBlocks
                  .slice(6)
                  .map((block, idx) => renderMathBlockCard(block, `extra-${block.source_path}-${idx}`))}
              </div>
            </details>
          ) : null}
        </section>
      ) : null}

      <div id="where-it-fits" className="report-group-head">
        <h2>{localizedText(lang, 'Where it fits', '在全局中的位置')}</h2>
        <p>
          {localizedText(
            lang,
            'How this report connects to the book and to the other reports.',
            '这份报告与书的章节、与其他报告之间的联系。',
          )}
        </p>
      </div>

      <section id="book-position" className="card section-enter" style={{ marginTop: '1rem' }}>
        <h3>{localizedText(lang, 'In the book', '书中位置')}</h3>
        {bookPlacement ? (
          <>
            <p className="lead">
              {localizedText(
                lang,
                'The book chapters that draw on this report.',
                '引用这份报告的书中章节。',
              )}
            </p>
            <p>
              <span className="badge">{localizedText(lang, 'Primary chapter', '主章节')}</span>{' '}
              <Link href={prefixPath(prefix, `/book/${bookPlacement.chapterId}`)}>{bookPlacement.chapterTitle}</Link>
            </p>
            {bookPlacement.otherChapters.length > 0 ? (
              <p>
                <span className="badge">{localizedText(lang, 'Also appears in', '同时出现于')}</span>{' '}
                {bookPlacement.otherChapters.map((row, idx) => (
                  <span key={`${reportId}-${row.chapterId}`}>
                    {idx > 0 ? '; ' : ''}
                    <Link href={prefixPath(prefix, `/book/${row.chapterId}`)}>{row.title}</Link>
                  </span>
                ))}
              </p>
            ) : null}
            <ul className="chapter-nav">
              {bookPlacement.previousChapterId ? (
                <li>
                  <Link href={prefixPath(prefix, `/book/${bookPlacement.previousChapterId}`)}>
                    ← {bookPlacement.previousChapterTitle}
                  </Link>
                </li>
              ) : null}
              {bookPlacement.nextChapterId ? (
                <li>
                  <Link href={prefixPath(prefix, `/book/${bookPlacement.nextChapterId}`)}>
                    {bookPlacement.nextChapterTitle} →
                  </Link>
                </li>
              ) : null}
            </ul>
          </>
        ) : (
          <p>{localizedText(lang, 'No book chapter discusses this report.', '书中没有专门讨论这份报告的章节。')}</p>
        )}
      </section>

      <section id="connected-reports" className="card section-enter" style={{ marginTop: '1rem' }}>
        <h3>{localizedText(lang, 'Connected Reports', '关联报告链')}</h3>
        <p className="lead">
          {localizedText(
            lang,
            'This report sits inside a shared chain. Use links below to move upstream/downstream and across model families.',
            '该报告位于同一研究链中，可通过下方链接跳转到上游/下游和跨模型家族的关联报告。',
          )}
        </p>
        <div className="grid grid-3">
          <article className="card">
            <h4>{localizedText(lang, 'Track Continuity', '轨道连续关系')}</h4>
            <ul>
              {networkNode?.previous_in_group ? (
                <li>
                  {localizedText(lang, 'Previous', '上游')}:{' '}
                  <Link href={prefixPath(prefix, `/reports/${networkNode.previous_in_group}`)}>
                    {lookupReportTitle(networkNode.previous_in_group, lang, network)}
                  </Link>
                </li>
              ) : (
                <li>{localizedText(lang, 'No previous report in this track.', '该轨道中没有上游报告。')}</li>
              )}
              {networkNode?.next_in_group ? (
                <li>
                  {localizedText(lang, 'Next', '下游')}:{' '}
                  <Link href={prefixPath(prefix, `/reports/${networkNode.next_in_group}`)}>
                    {lookupReportTitle(networkNode.next_in_group, lang, network)}
                  </Link>
                </li>
              ) : (
                <li>{localizedText(lang, 'No next report in this track.', '该轨道中没有下游报告。')}</li>
              )}
            </ul>
          </article>

          <article className="card">
            <h4>{localizedText(lang, 'Same-Group Links', '同组强关联')}</h4>
            {networkNode && networkNode.same_group_links.length > 0 ? (
              <ul>
                {networkNode.same_group_links.slice(0, 4).map((row) => (
                  <li key={`same-${row.report_id}`}>
                    <Link href={prefixPath(prefix, `/reports/${row.report_id}`)}>
                      {lookupReportTitle(row.report_id, lang, network)}
                    </Link>
                    {renderConnectionReason(lang, network, row)}
                  </li>
                ))}
              </ul>
            ) : (
              <p>{localizedText(lang, 'No same-group links detected.', '未检测到同组强关联。')}</p>
            )}
          </article>

          <article className="card">
            <h4>{localizedText(lang, 'Cross-Group Bridges', '跨组桥接')}</h4>
            {networkNode && networkNode.cross_group_links.length > 0 ? (
              <ul>
                {networkNode.cross_group_links.slice(0, 4).map((row) => (
                  <li key={`cross-${row.report_id}`}>
                    <Link href={prefixPath(prefix, `/reports/${row.report_id}`)}>
                      {lookupReportTitle(row.report_id, lang, network)}
                    </Link>
                    {renderConnectionReason(lang, network, row)}
                  </li>
                ))}
              </ul>
            ) : (
              <p>{localizedText(lang, 'No cross-group bridges detected.', '未检测到跨组桥接。')}</p>
            )}
          </article>
        </div>
      </section>

      <section id="narrative-arcs" className="card section-enter" style={{ marginTop: '1rem' }}>
        <h3>{localizedText(lang, 'Reading paths', '阅读路线')}</h3>
        <p className="lead">
          {localizedText(
            lang,
            'Reading paths through the reports that include this one.',
            '包含这份报告的阅读路线。',
          )}
        </p>
        {arcsForReport.length > 0 ? (
          <div className="grid grid-2">
            {arcsForReport.map((arc) => (
              <article key={`arc-placement-${arc.arc_id}`} className="card">
                <h4>{lang === 'cn' ? arc.label_cn : arc.label_en}</h4>
                <p>{lang === 'cn' ? arc.summary_cn : arc.summary_en}</p>
                <details>
                  <summary>
                    {localizedText(lang, `Reports in reading order (${arc.checkpoints.length})`, `按阅读顺序排列的报告（${arc.checkpoints.length} 份）`)}
                  </summary>
                  <ol>
                    {arc.checkpoints.map((cp) => (
                      <li key={`${arc.arc_id}-${cp.report_id}`}>
                        <Link href={prefixPath(prefix, `/reports/${cp.report_id}`)}>
                          {lang === 'cn' ? cp.title_cn : cp.title_en}
                        </Link>
                      </li>
                    ))}
                  </ol>
                </details>
              </article>
            ))}
          </div>
        ) : (
          <p>{localizedText(lang, 'This report is not on any reading path yet.', '这份报告还不在任何阅读路线中。')}</p>
        )}
      </section>


      <div id="working-record" className="report-group-head">
        <h2>{localizedText(lang, 'Working record', '工作记录')}</h2>
        <p>
          {localizedText(
            lang,
            'The claim ledger, source notes, commands and files the report is checked against.',
            '这份报告据以核对的论断清单、来源笔记、命令与文件。',
          )}{' '}
          {localizedText(lang, 'Report ID: ', '报告编号：')}
          <code>{reportId}</code>
        </p>
      </div>

      <details className="working-record">
        <summary>
          {localizedText(lang, 'Show the working record (claims, notes, commands, files)', '展开工作记录（论断、笔记、命令、文件）')}
        </summary>

      <section id="verifiable-claims" className="card section-enter" style={{ marginTop: '1rem' }}>
        <h3>{localizedText(lang, 'Claims and their evidence', '论断与证据')}</h3>
        <p className="lead">
          {localizedText(
            lang,
            'Claims below are tied to explicit evidence paths so each statement can be audited.',
            '下列每条论断都附有证据路径，便于逐条核对。',
          )}
        </p>
        {guide && (lang === 'cn' ? guide.objective_cn : guide.objective_en) !== meta.narrative.result_overview ? (
          <div className="card" style={{ marginBottom: '0.8rem' }}>
            <h4>{localizedText(lang, 'Report Objective', '报告目标')}</h4>
            <p>{lang === 'cn' ? guide.objective_cn : guide.objective_en}</p>
            <details>
              <summary>{localizedText(lang, 'Verification Steps', '核对步骤')}</summary>
              <ol>
                {(lang === 'cn' ? guide.verification_steps_cn : guide.verification_steps_en).map((step) => (
                  <li key={step}>{step}</li>
                ))}
              </ol>
            </details>
          </div>
        ) : null}
        {claimsOrdered.length > 0 ? (
          <div style={{ display: 'grid', gap: '0.9rem' }}>
            {(['model', 'method', 'result', 'finding'] as const).map((stage) => {
              const stageClaims = claimsOrdered.filter((claim) => claim.stage === stage);
              if (stageClaims.length === 0) {
                return null;
              }
              return (
                <article key={`stage-${stage}`} className="card">
                  <h4>
                    {localizedText(
                      lang,
                      stage.toUpperCase(),
                      stage === 'model'
                        ? '模型'
                        : stage === 'method'
                          ? '方法'
                          : stage === 'result'
                            ? '结果'
                            : '关键结论',
                    )}
                  </h4>
                  <div className="grid grid-2">
                    {stageClaims.map((claim) => (
                      <article key={claim.claim_id} className="card">
                        <p>{lang === 'cn' ? claim.text_cn : claim.text_en}</p>
                        <details>
                          <summary>{localizedText(lang, 'Evidence trail', '证据链')}</summary>
                          <ul>
                            {claim.evidence.map((ev) => (
                              <li key={`${claim.claim_id}-${ev.evidence_type}-${ev.path}`}>
                                <code>{ev.evidence_type}</code> <code>{ev.path}</code>
                                <p style={{ margin: '0.35rem 0 0' }}>{lang === 'cn' ? ev.snippet_cn : ev.snippet_en}</p>
                              </li>
                            ))}
                          </ul>
                        </details>
                        {claim.linked_report_ids.length > 0 ? (
                          <p style={{ marginTop: '0.45rem' }}>
                            <span className="badge">{localizedText(lang, 'Linked reports', '关联报告')}</span>{' '}
                            {claim.linked_report_ids.slice(0, 4).map((rid) => (
                              <Link
                                key={`${claim.claim_id}-${rid}`}
                                href={prefixPath(prefix, `/reports/${rid}`)}
                                style={{ marginRight: '0.45rem' }}
                              >
                                {lookupReportTitle(rid, lang, network)}
                              </Link>
                            ))}
                          </p>
                        ) : null}
                      </article>
                    ))}
                  </div>
                </article>
              );
            })}
          </div>
        ) : (
          <p>{localizedText(lang, 'No claim map found for this report.', '该报告尚未生成 claim 映射。')}</p>
        )}
      </section>

      {filteredSections.length > 0 ? (
      <section id="narrative-sections" className="card section-enter" style={{ marginTop: '1rem' }}>
        <h3>{localizedText(lang, 'Section notes', '章节笔记')}</h3>
        <div className="grid grid-2">
          {sectionsPreview.map((card) => (
            <article key={`${card.heading}-${card.source_path}`} className="card">
              <h4>{card.heading}</h4>
              <p>{card.summary}</p>
              <details>
                <summary>{localizedText(lang, 'Source', '来源')}</summary>
                <p style={{ marginBottom: 0 }}>
                  <code>{card.source_path}</code>
                </p>
              </details>
            </article>
          ))}
        </div>
        {sectionsExtra.length > 0 ? (
          <details style={{ marginTop: '0.8rem' }}>
            <summary>{localizedText(lang, 'Show more sections', '显示更多章节')}</summary>
            <div className="grid grid-2" style={{ marginTop: '0.8rem' }}>
              {sectionsExtra.map((card) => (
                <article key={`extra-${card.heading}-${card.source_path}`} className="card">
                  <h4>{card.heading}</h4>
                  <p>{card.summary}</p>
                  <details>
                    <summary>{localizedText(lang, 'Source', '来源')}</summary>
                    <p style={{ marginBottom: 0 }}>
                      <code>{card.source_path}</code>
                    </p>
                  </details>
                </article>
              ))}
            </div>
          </details>
        ) : null}
      </section>
      ) : null}

      <section id="commands" className="card section-enter" style={{ marginTop: '1rem' }}>
        <h3>{localizedText(lang, 'Reproducibility Commands', '复现实验命令')}</h3>
        <details>
          <summary>{localizedText(lang, 'Open command list', '展开命令列表')}</summary>
          {meta.reproducibility_commands.length > 0 ? (
            <ul>
              {meta.reproducibility_commands.map((cmd) => (
                <li key={cmd}>
                  <code>{cmd}</code>
                </li>
              ))}
            </ul>
          ) : (
            <p>{localizedText(lang, 'No explicit command block extracted.', '未提取到显式命令块。')}</p>
          )}
        </details>
      </section>

      <section id="appendix-assets" className="card section-enter" style={{ marginTop: '1rem' }}>
        <h3>{localizedText(lang, 'Files', '文件')}</h3>
        <p>
          {localizedText(lang, 'Showing', '当前展示')} {Math.min(20, groupedAssets.length)} / {groupedAssets.length}
          {duplicateAssetCount > 0 ? (
            <>
              {' '}
              <span className="badge">
                {localizedText(lang, 'collapsed duplicates', '折叠重复')} {duplicateAssetCount}
              </span>
            </>
          ) : null}
        </p>
        <ul>
          {groupedAssets.slice(0, 20).map((assetGroup) => (
            <li key={`${assetGroup.primary.kind}:${assetGroup.primary.label.toLowerCase()}`}>
              <a href={withBasePath(assetGroup.primary.web_path)} target="_blank" rel="noreferrer">
                {assetGroup.primary.label}
              </a>{' '}
              <code>{assetGroup.primary.kind}</code>{' '}
              {assetGroup.variants.length > 1 ? (
                <span className="badge">
                  {localizedText(lang, 'variants', '变体')} x{assetGroup.variants.length}
                </span>
              ) : null}
              {assetGroup.variants.length > 1 ? (
                <details style={{ marginTop: '0.35rem' }}>
                  <summary>{localizedText(lang, 'Show variants', '查看变体')}</summary>
                  <ul>
                    {assetGroup.variants.map((variant) => (
                      <li key={`${variant.sha256}:${variant.web_path}`}>
                        <a href={withBasePath(variant.web_path)} target="_blank" rel="noreferrer">
                          {variant.source_path}
                        </a>{' '}
                        <code>{variant.sha256.slice(0, 10)}</code>
                      </li>
                    ))}
                  </ul>
                </details>
              ) : null}
            </li>
          ))}
        </ul>
      </section>
      </details>
    </AppShell>
  );
}

export function renderTheoryPage(lang: Lang, prefix: string) {
  const map = loadTheoryMap();
  const network = loadReportNetwork();
  const contentMap = loadContentMap();
  const glossary = loadGlossary();
  const bookManifest = loadBookManifest();
  const backbone = loadBookBackbone();
  const formulaCoverage = extractFormulaCoverage(map);
  const formulaPolicyRows = extractFormulaPolicyRows(map);
  const duplicationBuckets = extractDuplicationBuckets(map);
  const stageCoverageRows = buildStageCoverageRows(contentMap, network);
  const notionDigests = buildNotionClaimDigests(map, contentMap);
  return (
    <AppShell lang={lang} prefix={prefix}>
      <section className="card section-enter">
        <div className="kicker">{localizedText(lang, 'Theory Center', '理论中心')}</div>
        <h1>{localizedText(lang, 'Unified Mathematical Map', '统一数学映射')}</h1>
        <p>
          {localizedText(
            lang,
            'The cards below summarize shared mathematical notions across reports and map each notion to concrete report pages.',
            '下列卡片展示跨报告共享的数学概念，并映射到具体报告页面。',
          )}
        </p>
        <p className="muted">
          {localizedText(
            lang,
            'Goal: keep the mathematics continuous from notation to derivation, then to evidence and cross-report verification.',
            '目标：把符号、推导、证据和跨报告核对串成一条连续数学链。',
          )}
        </p>
      </section>

      <section className="card section-enter" style={{ marginTop: '1rem' }}>
        <h2>{localizedText(lang, 'Reading Protocol', '阅读协议')}</h2>
        <ol>
          <li>
            {localizedText(
              lang,
              'Start from Chapter 0/1 in Book for notation and core FPT objects.',
              '先从 Book 第0/1章进入，统一符号和核心 FPT 对象。',
            )}{' '}
            <Link href={prefixPath(prefix, '/book')}>/book</Link>
          </li>
          <li>
            {localizedText(
              lang,
              'Use concept cards below to locate every notion in concrete reports.',
              '使用下方概念卡，把每个理论概念定位到具体报告。',
            )}
          </li>
          <li>
            {localizedText(
              lang,
              'Inspect stage matrix and claim ledger to verify model/method/result/finding continuity.',
              '查看阶段覆盖矩阵与 claim 账本，核对 model/method/result/finding 的连续性。',
            )}
          </li>
          <li>
            {localizedText(
              lang,
              'Use duplication governance to distinguish shared foundations from harmful repetition.',
              '通过重复治理区分“共享基础公式”与“有害重复”。',
            )}
          </li>
        </ol>
        <p>
          <span className="badge">{localizedText(lang, 'Theory cards', '理论卡片')} {map.cards.length}</span>{' '}
          <span className="badge">{localizedText(lang, 'Claims', 'Claim 数')} {contentMap.claims.length}</span>{' '}
          <span className="badge">{localizedText(lang, 'Book chapters', 'Book 章节')} {bookManifest?.chapter_count ?? 0}</span>
        </p>
      </section>

      {backbone ? (
        <section className="card section-enter" style={{ marginTop: '1rem' }}>
          <h2>{localizedText(lang, 'Continuity Spine', '主线脊柱')}</h2>
          <p className="lead">
            {localizedText(
              lang,
              'Acts define the long-form argument structure, and chapter spine transitions show how one verified block feeds the next.',
              '幕结构定义整本论证骨架，章节脊柱过渡说明“上一段已验证结论”如何进入下一段推导。',
            )}
          </p>
          <div className="grid grid-2">
            {backbone.acts.map((act) => (
              <article key={`act-${act.act_id}`} className="card">
                <h3>{lang === 'cn' ? act.title_cn : act.title_en}</h3>
                <p>{lang === 'cn' ? act.objective_cn : act.objective_en}</p>
                <p>
                  <span className="badge">
                    {localizedText(lang, 'Chapters', '章节')}: {act.chapter_ids.length}
                  </span>
                </p>
                <ul>
                  {act.chapter_ids.map((chapterId) => {
                    const chapterMeta = bookManifest?.chapters.find((row) => row.chapter_id === chapterId);
                    const chapterTitle =
                      chapterMeta == null
                        ? chapterId
                        : lang === 'cn'
                          ? chapterMeta.title_cn
                          : chapterMeta.title_en;
                    return (
                      <li key={`act-${act.act_id}-${chapterId}`}>
                        <Link href={prefixPath(prefix, `/book/${chapterId}`)}>{chapterTitle}</Link>
                      </li>
                    );
                  })}
                </ul>
              </article>
            ))}
          </div>
          <details style={{ marginTop: '0.8rem' }}>
            <summary>{localizedText(lang, 'Open chapter transitions', '展开章节过渡')}</summary>
            <ul style={{ marginTop: '0.5rem' }}>
              {[...backbone.chapter_spine]
                .sort((a, b) => a.order - b.order)
                .map((row) => (
                  <li key={`spine-${row.chapter_id}`}>
                    <strong>
                      <Link href={prefixPath(prefix, `/book/${row.chapter_id}`)}>
                        {lang === 'cn' ? row.title_cn : row.title_en}
                      </Link>
                    </strong>
                    : {lang === 'cn' ? row.transition_to_next_cn : row.transition_to_next_en}
                  </li>
                ))}
            </ul>
          </details>
        </section>
      ) : null}

      <section className="card section-enter" style={{ marginTop: '1rem' }}>
        <h2>{localizedText(lang, 'Concept Cards', '概念卡片')}</h2>
        <div className="grid grid-2">
          {map.cards.map((card) => (
            <article key={card.id} className="card">
              <h3>{lang === 'cn' ? card.label_cn : card.label_en}</h3>
              <p>{lang === 'cn' ? card.description_cn : card.description_en}</p>
              <p>
                <span className="badge">
                  {localizedText(lang, 'Reports', '关联报告')}: {card.report_count}
                </span>
              </p>
              <ul>
                {card.report_ids.slice(0, 8).map((reportId) => (
                  <li key={reportId}>
                    <Link href={prefixPath(prefix, `/reports/${reportId}`)}>{reportId}</Link>
                  </li>
                ))}
              </ul>
              {card.report_ids.length > 8 ? (
                <details>
                  <summary>{localizedText(lang, 'Show all linked reports', '显示全部关联报告')}</summary>
                  <ul>
                    {card.report_ids.slice(8).map((reportId) => (
                      <li key={`extra-${reportId}`}>
                        <Link href={prefixPath(prefix, `/reports/${reportId}`)}>{reportId}</Link>
                      </li>
                    ))}
                  </ul>
                </details>
              ) : null}
            </article>
          ))}
        </div>
      </section>

      {glossary ? (
        <section className="card section-enter" style={{ marginTop: '1rem' }}>
          <h2>{localizedText(lang, 'Notation & Term Lock', '符号与术语锁表')}</h2>
          <p className="lead">
            {localizedText(
              lang,
              'These locked terms keep CN/EN semantics aligned and provide formula anchors for quick lookup.',
              '这些锁定术语用于保持中英文语义一致，并提供公式锚点便于快速查阅。',
            )}
          </p>
          <div className="grid grid-2">
            {glossary.terms.slice(0, 12).map((term) => (
              <article key={term.term_id} className="card">
                <h3>{lang === 'cn' ? term.term_cn : term.term_en}</h3>
                <p>{lang === 'cn' ? term.definition_cn : term.definition_en}</p>
                {term.formula ? (
                  renderGlossaryFormula(term.formula, lang, `glossary:${term.term_id}`)
                ) : null}
                <p>
                  <span className="badge">{term.category}</span>{' '}
                  <span className="badge">{localizedText(lang, 'Reports', '关联报告')} {term.related_report_ids.length}</span>
                </p>
              </article>
            ))}
          </div>
        </section>
      ) : null}

      <section className="card section-enter" style={{ marginTop: '1rem' }}>
        <h2>{localizedText(lang, 'Stage Coverage Matrix', '阶段覆盖矩阵')}</h2>
        <p className="lead">
          {localizedText(
            lang,
            'Each row tracks whether one report closes the full chain from assumptions to findings.',
            '每行跟踪单个报告是否完整覆盖从假设到结论的链条。',
          )}
        </p>
        <div className="table-wrap">
          <table className="theory-table">
            <thead>
              <tr>
                <th>{localizedText(lang, 'Report', '报告')}</th>
                <th>{stageLabel(lang, 'model')}</th>
                <th>{stageLabel(lang, 'method')}</th>
                <th>{stageLabel(lang, 'result')}</th>
                <th>{stageLabel(lang, 'finding')}</th>
                <th>{localizedText(lang, 'Claims', 'Claim')}</th>
                <th>{localizedText(lang, 'Formulas', '公式')}</th>
                <th>{localizedText(lang, 'Book', '章节')}</th>
              </tr>
            </thead>
            <tbody>
              {stageCoverageRows.map((row) => {
                const chapter = bookManifest?.report_chapter_map?.[row.report_id]?.primary_chapter_id ?? null;
                return (
                  <tr key={`stage-${row.report_id}`}>
                    <td>
                      <Link href={prefixPath(prefix, `/reports/${row.report_id}`)}>
                        {lang === 'cn' ? row.title_cn : row.title_en}
                      </Link>
                    </td>
                    <td>{row.coverage.model}</td>
                    <td>{row.coverage.method}</td>
                    <td>{row.coverage.result}</td>
                    <td>{row.coverage.finding}</td>
                    <td>{row.coverage.total}</td>
                    <td>{formulaCoverage[row.report_id] ?? 0}</td>
                    <td>
                      {chapter ? <Link href={prefixPath(prefix, `/book/${chapter}`)}>{chapter}</Link> : <span className="muted">-</span>}
                    </td>
                  </tr>
                );
              })}
            </tbody>
          </table>
        </div>
      </section>

      {formulaPolicyRows.length > 0 ? (
        <section className="card section-enter" style={{ marginTop: '1rem' }}>
          <h2>{localizedText(lang, 'Formula Depth Governance', '公式深度治理')}</h2>
          <p className="lead">
            {localizedText(
              lang,
              'Thresholds are applied by report family so lightweight notes are explicit exceptions instead of silent gaps.',
              '按报告族设置公式阈值，轻量文档必须通过显式例外标注，而不是隐性缺口。',
            )}
          </p>
          <div className="table-wrap">
            <table className="theory-table">
              <thead>
                <tr>
                  <th>{localizedText(lang, 'Report', '报告')}</th>
                  <th>{localizedText(lang, 'Group', '分组')}</th>
                  <th>{localizedText(lang, 'Formulas', '公式数')}</th>
                  <th>{localizedText(lang, 'Min', '最低')}</th>
                  <th>{localizedText(lang, 'Target', '目标')}</th>
                  <th>{localizedText(lang, 'Status', '状态')}</th>
                  <th>{localizedText(lang, 'Exception', '例外')}</th>
                </tr>
              </thead>
              <tbody>
                {formulaPolicyRows.map((row) => {
                  const report = network.reports.find((item) => item.report_id === row.report_id);
                  return (
                    <tr key={`formula-policy-${row.report_id}`}>
                      <td>
                        <Link href={prefixPath(prefix, `/reports/${row.report_id}`)}>
                          {lang === 'cn' ? report?.title_cn ?? row.report_id : report?.title_en ?? row.report_id}
                        </Link>
                      </td>
                      <td>{row.group}</td>
                      <td>{row.formula_count}</td>
                      <td>{row.min_required}</td>
                      <td>{row.target}</td>
                      <td>
                        <span className="badge">{row.pass ? localizedText(lang, 'PASS', '通过') : localizedText(lang, 'FAIL', '未通过')}</span>
                      </td>
                      <td>
                        {row.exception_tag ? (
                          <>
                            <span className="badge">{row.exception_tag}</span>
                            {row.exception_reason ? <div className="muted">{compactText(row.exception_reason, 90)}</div> : null}
                          </>
                        ) : (
                          <span className="muted">-</span>
                        )}
                      </td>
                    </tr>
                  );
                })}
              </tbody>
            </table>
          </div>
        </section>
      ) : null}

      <section className="card section-enter" style={{ marginTop: '1rem' }}>
        <h2>{localizedText(lang, 'Notion → Claim → Evidence', '概念 → Claim → 证据')}</h2>
        <div className="grid grid-2">
          {notionDigests.map(({ card, claims }) => (
            <article key={`notion-claims-${card.id}`} className="card">
              <h3>{lang === 'cn' ? card.label_cn : card.label_en}</h3>
              <p className="muted">{lang === 'cn' ? card.description_cn : card.description_en}</p>
              {claims.length > 0 ? (
                <ul>
                  {claims.map((claim) => (
                    <li key={claim.claim_id}>
                      <span className="badge">{stageLabel(lang, claim.stage)}</span>{' '}
                      <Link href={prefixPath(prefix, `/reports/${claim.report_id}`)}>{claim.report_id}</Link>{' '}
                      <span className="muted">({localizedText(lang, 'evidence', '证据')} {claim.evidence.length})</span>
                      <div>{compactText(lang === 'cn' ? claim.text_cn : claim.text_en, 150)}</div>
                    </li>
                  ))}
                </ul>
              ) : (
                <p className="muted">{localizedText(lang, 'No linked claims.', '暂无关联 claim。')}</p>
              )}
            </article>
          ))}
        </div>
      </section>

      <section className="card section-enter" style={{ marginTop: '1rem' }}>
        <h2>{localizedText(lang, 'Duplication Governance', '重复治理')}</h2>
        <div className="grid grid-2">
          <article className="card">
            <h3>{localizedText(lang, 'Shared Foundations', '共享基础公式')}</h3>
            <p>
              <span className="badge">{localizedText(lang, 'Count', '数量')}: {duplicationBuckets.sharedCoreCount}</span>
            </p>
            <ul>
              {duplicationBuckets.sharedCore.slice(0, 6).map((row, idx) => (
                <li key={`shared-core-${idx}`}>
                  <code>{compactLatex(row.latex)}</code> ({row.count})
                </li>
              ))}
            </ul>
          </article>
          <article className="card">
            <h3>{localizedText(lang, 'Redundant Duplicates', '冗余重复')}</h3>
            <p>
              <span className="badge">{localizedText(lang, 'Count', '数量')}: {duplicationBuckets.redundantCount}</span>
            </p>
            {duplicationBuckets.redundant.length > 0 ? (
              <ul>
                {duplicationBuckets.redundant.slice(0, 6).map((row, idx) => (
                  <li key={`redundant-${idx}`}>
                    <code>{compactLatex(row.latex)}</code> ({row.count})
                  </li>
                ))}
              </ul>
            ) : (
              <p className="muted">{localizedText(lang, 'No harmful duplicate signatures detected in current build.', '当前构建未检测到有害重复签名。')}</p>
            )}
          </article>
        </div>
      </section>

      <section className="card section-enter" style={{ marginTop: '1rem' }}>
        <h2>{localizedText(lang, 'Consistency Checks', '一致性检查')}</h2>
        <ul>
          {map.consistency_checks.map((check) => {
            const summaryLines = summarizeCheckDetails(check.details, lang);
            return (
              <li key={check.check}>
                <strong>{check.check}</strong>: {check.pass ? 'PASS' : 'FAIL'}
                <details style={{ marginTop: '0.35rem' }}>
                  <summary>{localizedText(lang, 'Details', '详情')}</summary>
                  <ul style={{ marginTop: '0.35rem' }}>
                    {summaryLines.map((line, index) => (
                      <li key={`${check.check}-${index}`}>{line}</li>
                    ))}
                  </ul>
                  <details style={{ marginTop: '0.45rem' }}>
                    <summary>{localizedText(lang, 'Open raw check payload', '展开原始检查载荷')}</summary>
                    <pre style={{ whiteSpace: 'pre-wrap', marginTop: '0.45rem' }}>
                      {rawCheckPayloadPreview(check.details, lang)}
                    </pre>
                  </details>
                  <p className="muted" style={{ margin: '0.45rem 0 0' }}>
                    {localizedText(lang, 'Raw payload is available in', '原始数据可在此查看')}{' '}
                    <a href={withBasePath('/data/v1/theory_map.json')} target="_blank" rel="noreferrer">
                      /data/v1/theory_map.json
                    </a>
                  </p>
                </details>
              </li>
            );
          })}
        </ul>
      </section>

      <section className="card section-enter" style={{ marginTop: '1rem' }}>
        <h2>{localizedText(lang, 'Cross-Report Routes', '跨报告路线图')}</h2>
        <p className="lead">
          {localizedText(
            lang,
            'These routes stitch reports into continuous tracks instead of isolated pages.',
            '这些路线把报告串成连续轨道，而不是孤立页面。',
          )}
        </p>
        <div className="grid grid-3">
          {network.group_paths.map((route) => (
            <article key={`route-${route.group}`} className="card">
              <h3>{route.group}</h3>
              <ol>
                {route.report_ids.map((reportId) => (
                  <li key={`route-${route.group}-${reportId}`}>
                    <Link href={prefixPath(prefix, `/reports/${reportId}`)}>{lookupReportTitle(reportId, lang, network)}</Link>
                  </li>
                ))}
              </ol>
            </article>
          ))}
        </div>
      </section>

      <section className="card section-enter" style={{ marginTop: '1rem' }}>
        <h2>{localizedText(lang, 'Content-Level Arcs', '内容层叙事弧线')}</h2>
        <div className="grid grid-2">
          {contentMap.arcs.map((arc) => (
            <article key={`arc-${arc.arc_id}`} className="card">
              <h3>{lang === 'cn' ? arc.label_cn : arc.label_en}</h3>
              <p>{lang === 'cn' ? arc.summary_cn : arc.summary_en}</p>
              <p>
                <span className="badge">
                  {localizedText(lang, 'Checkpoints', '检查点')}: {arc.checkpoint_count}
                </span>{' '}
                <span className="badge">
                  {localizedText(lang, 'Claims', 'Claim 数')}: {arc.claim_ids.length}
                </span>
              </p>
              <details>
                <summary>{localizedText(lang, 'Open checkpoints', '展开检查点')}</summary>
                <ol>
                  {arc.checkpoints.map((cp) => (
                    <li key={`${arc.arc_id}-${cp.report_id}`}>
                      <Link href={prefixPath(prefix, `/reports/${cp.report_id}`)}>
                        {lang === 'cn' ? cp.title_cn : cp.title_en}
                      </Link>
                    </li>
                  ))}
                </ol>
              </details>
            </article>
          ))}
        </div>
      </section>
    </AppShell>
  );
}

export function renderAgentSyncPage(lang: Lang, prefix: string) {
  const index = loadIndex();
  const manifest = loadAgentManifest();

  return (
    <AppShell lang={lang} prefix={prefix}>
      <section className="card section-enter">
        <div className="kicker">Machine Readable</div>
        <h1>Agent Sync</h1>
        <p>
          {localizedText(
            lang,
            'This endpoint exposes normalized JSONL + manifest outputs for automation agents.',
            '该页面提供面向自动化 agent 的标准化 JSONL + manifest 输出。',
          )}
        </p>
        <ul>
          <li>
            <a href={withBasePath('/data/v1/agent/manifest.json')} target="_blank" rel="noreferrer">
              /data/v1/agent/manifest.json
            </a>
          </li>
          <li>
            <a href={withBasePath('/data/v1/agent/reports.jsonl')} target="_blank" rel="noreferrer">
              /data/v1/agent/reports.jsonl
            </a>
          </li>
          <li>
            <a href={withBasePath('/data/v1/agent/events.jsonl')} target="_blank" rel="noreferrer">
              /data/v1/agent/events.jsonl
            </a>
          </li>
          <li>
            <a href={withBasePath('/data/v1/agent/book_manifest.json')} target="_blank" rel="noreferrer">
              /data/v1/agent/book_manifest.json
            </a>
          </li>
          <li>
            <a href={withBasePath('/data/v1/agent/book_chapters.jsonl')} target="_blank" rel="noreferrer">
              /data/v1/agent/book_chapters.jsonl
            </a>
          </li>
          <li>
            <a href={withBasePath('/data/v1/agent/claim_graph.jsonl')} target="_blank" rel="noreferrer">
              /data/v1/agent/claim_graph.jsonl
            </a>
          </li>
          <li>
            <a href={withBasePath('/data/v1/agent/translation_qc.json')} target="_blank" rel="noreferrer">
              /data/v1/agent/translation_qc.json
            </a>
          </li>
          <li>
            <a href={withBasePath('/data/v1/theory_map.json')} target="_blank" rel="noreferrer">
              /data/v1/theory_map.json
            </a>
          </li>
          <li>
            <a href={withBasePath('/data/v1/report_network.json')} target="_blank" rel="noreferrer">
              /data/v1/report_network.json
            </a>
          </li>
          <li>
            <a href={withBasePath('/data/v1/content_map.json')} target="_blank" rel="noreferrer">
              /data/v1/content_map.json
            </a>
          </li>
          <li>
            <a href={withBasePath('/data/v1/agent/guide.json')} target="_blank" rel="noreferrer">
              /data/v1/agent/guide.json
            </a>
          </li>
        </ul>
        <h3>{localizedText(lang, 'Agent Workflow', 'Agent 使用流程')}</h3>
        <ol>
          <li>{localizedText(lang, 'Read manifest.json and verify hashes first.', '先读取 manifest.json 并校验哈希。')}</li>
          <li>{localizedText(lang, 'Stream reports.jsonl for normalized per-report records.', '再流式读取 reports.jsonl 获取标准化报告记录。')}</li>
          <li>{localizedText(lang, 'Use book_manifest.json + book_chapters.jsonl to follow chapter continuity.', '结合 book_manifest.json 与 book_chapters.jsonl 追踪章节主线。')}</li>
          <li>{localizedText(lang, 'Use claim_graph.jsonl and content_map.json for evidence graph traversal.', '使用 claim_graph.jsonl 与 content_map.json 构建证据图。')}</li>
          <li>{localizedText(lang, 'Check translation_qc.json before language-specific generation.', '在语言生成前先检查 translation_qc.json。')}</li>
          <li>{localizedText(lang, 'Use events.jsonl for incremental sync checkpoints.', '用 events.jsonl 做增量同步检查点。')}</li>
          <li>{localizedText(lang, 'Join with theory_map.json for cross-report concept coverage.', '结合 theory_map.json 做跨报告概念映射。')}</li>
          <li>
            {localizedText(
              lang,
              'Traverse report_network.json to follow upstream/downstream report logic.',
              '通过 report_network.json 追踪上游/下游报告逻辑链。',
            )}
          </li>
          <li>
            {localizedText(
              lang,
              'Use content_map.json for claim-level evidence chains and narrative arcs.',
              '使用 content_map.json 读取 claim 级证据链与叙事弧线。',
            )}
          </li>
        </ol>
        {manifest ? (
          <p>
            {localizedText(lang, 'Manifest generated at', 'Manifest 生成于')}: {formatTimestamp(lang, manifest.generated_at)}
          </p>
        ) : null}
        <p>
          {localizedText(lang, 'Current report count', '当前报告数')}: <strong>{index.reports.length}</strong>
        </p>
      </section>
    </AppShell>
  );
}

export function renderRepoSyncPage(lang: Lang, prefix: string) {
  const payload = loadRepoSync();
  const sectionLabel = new Map(
    payload.sections.map((row) => [row.key, lang === 'cn' ? row.label_cn : row.label_en]),
  );
  const previewRows = payload.files.slice(0, 800);

  return (
    <AppShell lang={lang} prefix={prefix}>
      <section className="card section-enter">
        <div className="kicker">Repository Mirror</div>
        <h1>{localizedText(lang, 'Repository Sync', '仓库同步视图')}</h1>
        <p>
          {localizedText(
            lang,
            'This view mirrors local repository documents/code indexes into the web payload so website users can trace what is present outside report cards.',
            '该页面把本地仓库中的文档/代码索引同步到网站数据层，方便在报告卡片之外追踪仓库全貌。',
          )}
        </p>
        <ul>
          <li>
            {localizedText(lang, 'Generated at', '生成时间')}: {formatTimestamp(lang, payload.generated_at)}
          </li>
          <li>
            {localizedText(lang, 'Synced files', '同步文件数')}: <strong>{payload.stats.file_count}</strong>
          </li>
          <li>
            {localizedText(lang, 'Total indexed size', '索引总大小')}: <strong>{formatBytes(payload.stats.total_size_bytes)}</strong>
          </li>
          <li>
            {localizedText(lang, 'Raw JSON endpoint', '原始 JSON 地址')}:{' '}
            <a href={withBasePath('/data/v1/repo_sync.json')} target="_blank" rel="noreferrer">
              /data/v1/repo_sync.json
            </a>
          </li>
          {payload.repo.origin_url ? (
            <li>
              {localizedText(lang, 'GitHub repository', 'GitHub 仓库')}:{' '}
              <a href={payload.repo.origin_url} target="_blank" rel="noreferrer">
                {payload.repo.origin_url}
              </a>
            </li>
          ) : null}
        </ul>
      </section>

      <section className="card section-enter" style={{ marginTop: '1rem' }}>
        <h2>{localizedText(lang, 'Synced Sections', '同步分区')}</h2>
        <div className="grid grid-3">
          {payload.sections.map((row) => (
            <article key={`repo-section-${row.key}`} className="card">
              <h3>{lang === 'cn' ? row.label_cn : row.label_en}</h3>
              <p>
                <span className="badge">
                  {localizedText(lang, 'Files', '文件')}: {row.file_count}
                </span>{' '}
                <span className="badge">
                  {localizedText(lang, 'Size', '大小')}: {formatBytes(row.total_size_bytes)}
                </span>
              </p>
            </article>
          ))}
        </div>
      </section>

      <section className="card section-enter" style={{ marginTop: '1rem' }}>
        <h2>{localizedText(lang, 'Synced File Index', '同步文件索引')}</h2>
        <p className="lead">
          {localizedText(
            lang,
            `Showing ${previewRows.length} entries on page (full index is in repo_sync.json).`,
            `页面展示 ${previewRows.length} 条（完整索引见 repo_sync.json）。`,
          )}
        </p>
        <div style={{ overflowX: 'auto' }}>
          <table className="theory-table">
            <thead>
              <tr>
                <th>{localizedText(lang, 'Path', '路径')}</th>
                <th>{localizedText(lang, 'Category', '分类')}</th>
                <th>{localizedText(lang, 'Size', '大小')}</th>
                <th>{localizedText(lang, 'Updated', '更新时间')}</th>
                <th>SHA256</th>
              </tr>
            </thead>
            <tbody>
              {previewRows.map((row) => (
                <tr key={`repo-file-${row.path}`}>
                  <td>
                    {row.github_url ? (
                      <a href={row.github_url} target="_blank" rel="noreferrer">
                        <code>{row.path}</code>
                      </a>
                    ) : (
                      <code>{row.path}</code>
                    )}
                    {row.preview ? (
                      <p style={{ margin: '0.35rem 0 0' }}>
                        {compactText(row.preview, 140)}
                      </p>
                    ) : null}
                  </td>
                  <td>{sectionLabel.get(row.category) ?? row.category}</td>
                  <td>{formatBytes(row.size)}</td>
                  <td>{formatTimestamp(lang, row.updated_at)}</td>
                  <td>
                    <code>{row.sha256.slice(0, 12)}...</code>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </section>
    </AppShell>
  );
}

export function renderAboutPage(lang: Lang, prefix: string) {
  const index = loadIndex();
  const written = writtenReports(index);
  const scaffolds = scaffoldReports(index);
  const generated = formatDay(lang, index.generated_at);
  return (
    <AppShell lang={lang} prefix={prefix}>
      <header className="page-head">
        <p className="kicker">{localizedText(lang, 'About', '关于')}</p>
        <h1>{localizedText(lang, 'About this atlas', '关于本图谱')}</h1>
        <p className="page-lede">
          {localizedText(
            lang,
            'Valley-K Small is the public record of a PhD research line on first-passage times of random walks: when the time a walker needs to reach a target has two peaks rather than one, and why.',
            'Valley-K Small 是一条博士研究线的公开记录，主题是随机游走的首达时间：游走者到达目标所需的时间，什么时候会出现两个峰而不是一个，以及为什么。',
          )}
        </p>
      </header>

      <section className="prose-section">
        <h2>{localizedText(lang, 'What is here', '这里有什么')}</h2>
        <ul>
          <li>
            <Link href={prefixPath(prefix, '/reports')}>
              {localizedText(lang, `${written.length} written reports`, `${written.length} 份已成文的报告`)}
            </Link>
            {localizedText(
              lang,
              `, each with a PDF (most in English and Chinese) and a page of findings, figures and mathematics; ${scaffolds.length} more are in progress.`,
              `，每份都有 PDF（多数有中英两版）和一页结论、图与数学；另有 ${scaffolds.length} 份在进行中。`,
            )}
          </li>
          <li>
            <Link href={prefixPath(prefix, '/book')}>{localizedText(lang, 'A book', '一本书')}</Link>
            {localizedText(
              lang,
              ' that reads the reports as one argument, chapter by chapter, also available ',
              '，把这些报告按章节串成一条论证；也可以',
            )}
            <Link href={prefixPath(prefix, '/book/continuous')}>{localizedText(lang, 'on a single page', '在一页里通读')}</Link>
            {localizedText(lang, '.', '。')}
          </li>
          <li>
            <Link href={prefixPath(prefix, '/theory')}>{localizedText(lang, 'Theory', '理论')}</Link>
            {localizedText(lang, ': the notions and formulas the reports share.', '：各报告共用的概念与公式。')}
          </li>
          <li>
            <Link href={`${prefixPath(prefix, '/')}#talks`}>{localizedText(lang, 'Two talks', '两场演讲')}</Link>
            {localizedText(lang, ', as web slide decks in both languages.', '，网页幻灯片，中英双语。')}
          </li>
        </ul>

        <h2>{localizedText(lang, 'How it is made', '怎么做的')}</h2>
        <p>
          {localizedText(
            lang,
            'Each report is written in LaTeX next to the code and data that produce its figures. The pages here are generated from those sources by scripts in the repository, checked against JSON schemas, and rebuilt when the repository changes. Summaries and findings on the pages are extracted from the reports; the PDF is the report itself.',
            '每份报告用 LaTeX 写成，和生成图的代码、数据放在一起。这里的页面由仓库里的脚本从这些源文件生成，经 JSON schema 校验，仓库一有变动就重新构建。页面上的摘要和结论摘自报告本身；PDF 才是报告全文。',
          )}
        </p>
        <p>
          {generated
            ? localizedText(
                lang,
                `This is an active research repository, and reports are revised as the work continues. These pages were generated on ${generated}.`,
                `这是一个仍在进行的研究仓库，报告会随研究推进而修订。本页面生成于 ${generated}。`,
              )
            : null}
        </p>

        <h2>{localizedText(lang, 'Author', '作者')}</h2>
        <p>
          {localizedText(
            lang,
            'Xiaoxiao Zhouyi, PhD researcher at the University of Bristol. Other work and contact: ',
            '周易潇潇，布里斯托大学博士研究生。其他工作与联系方式：',
          )}
          <a href={lang === 'cn' ? OWNER_SITE_ZH : OWNER_SITE}>zhouyixiaoxiao.com</a>
          {localizedText(lang, '.', '。')}
        </p>
      </section>
    </AppShell>
  );
}
