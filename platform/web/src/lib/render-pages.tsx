import Link from 'next/link';
import type { ReactNode } from 'react';
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
import {
  FAMILY_ORDER,
  OWNER_SITE,
  OWNER_SITE_ZH,
  SUPERSEDED_BY,
  arcDisplay,
  formatDay,
  formulaKey,
  START_HERE,
  displayTitle,
  displayEvidenceSnippet,
  evidenceKindLabel,
  isClaimTextEcho,
  isSiteGlossaryTerm,
  mergeEvidenceRows,
  renderGlossaryFormula,
  familyLabel,
  familyNote,
  formulaBlockClass,
  formulaCardClass,
  groupName,
  isMixedLanguageText,
  isPlaceholderText,
  isLatexResidue,
  isGeneratedMathStoryDescription,
  isGeneratedMathStoryStage,
  isGeneratedAssetDatasetPath,
  isGenericMathStoryContext,
  isReaderDataset,
  leadingSentences,
  notionLabel,
  plainText,
  readerText,
  renderLatex,
  renderProse,
  reportFamily,
  loadRegistryStatus,
  scaffoldReports,
  sentencesWithin,
  typesetApostrophes,
  writtenReports,
} from '@/lib/atlas';
import { PdfLinks } from '@/components/PdfLinks';
import type { AssetRecord, ContentMap, FigureRecord, Lang, ReportMeta, ReportNetwork } from '@/types';

// A formula card is captioned with the heading of the section it comes from,
// and only when that heading is in the page's language.
function formulaCaption(lang: Lang, context: string): string {
  const heading = context.replace(/\s+/g, ' ').trim();
  if (!heading || /fallback/i.test(heading) || isGenericMathStoryContext(heading)) {
    return '';
  }
  const isChinese = /[\u3400-\u9fff]/.test(heading);
  return (lang === 'cn') === isChinese ? heading : '';
}

// The first of each set of formulas that differ only in spacing or trailing zeros.
function uniqueFormulas<T extends { latex: string }>(items: T[], seen = new Set<string>()): T[] {
  return items.filter((item) => {
    const key = formulaKey(item.latex);
    if (!key || seen.has(key)) {
      return false;
    }
    seen.add(key);
    return true;
  });
}

// Consecutive formulas whose caption (source section heading) is the same
// form one group; a formula without a caption is a group of its own.
function groupMathStoryByCaption<T extends { context: string }>(
  lang: Lang,
  items: T[],
): Array<{ caption: string; items: T[] }> {
  const groups: Array<{ caption: string; items: T[] }> = [];
  for (const item of items) {
    const caption = formulaCaption(lang, item.context);
    const last = groups[groups.length - 1];
    if (caption && last && last.caption === caption) {
      last.items.push(item);
    } else {
      groups.push({ caption, items: [item] });
    }
  }
  return groups;
}

function renderMathBlockCard(
  lang: Lang,
  block: { context: string; lang: string; latex: string; source_path: string },
  key: string,
) {
  const rendered = renderLatex(block.latex);
  const caption = formulaCaption(lang, block.context);

  return (
    <article key={key} className={formulaCardClass(block.latex)}>
      {caption ? <p className="math-caption">{readerText(caption)}</p> : null}
      <div
        className={formulaBlockClass(block.latex)}
        dangerouslySetInnerHTML={{
          __html: rendered.html,
        }}
      />
      <details>
        <summary>{localizedText(lang, 'Formula source', '公式来源')}</summary>
        <p style={{ marginBottom: 0 }}>
          <code>{block.source_path}</code>
        </p>
      </details>
    </article>
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
  let cut = space > maxChars * 0.6 ? clipped.slice(0, space) : clipped;
  if ((cut.match(/\$/g) || []).length % 2 === 1) {
    // Never end inside a $…$ formula.
    cut = cut.slice(0, cut.lastIndexOf('$'));
  }
  return `${cut.replace(/[\s,;:.，；：。、]+$/, '')}…`;
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

function displayReportText(lang: Lang, text: string, englishText = ''): string {
  if (!isPlaceholderText(text) && !isLatexResidue(text)) {
    return text;
  }
  if (lang === 'cn' && englishText && !isPlaceholderText(englishText) && !isLatexResidue(englishText)) {
    return englishText;
  }
  return '';
}

// The checks look only at the prose around any $…$ formula (see isLatexResidue).
function displayWipNoteText(lang: Lang, text: string, englishText = ''): string {
  return displayReportText(lang, text.trim(), englishText.trim());
}

function localizeSectionCards(
  lang: Lang,
  cards: ReportMeta['section_cards'],
  cardsEn: ReportMeta['section_cards'] | undefined,
): ReportMeta['section_cards'] {
  return cards.map((card, index) => {
    const indexedCard = cardsEn?.[index];
    const englishCard = indexedCard?.source_path === card.source_path
      ? indexedCard
      : cardsEn?.find((candidate) => candidate.source_path === card.source_path);
    return {
      ...card,
      heading: displayReportText(lang, card.heading, englishCard?.heading),
      summary:
        displayReportText(lang, card.summary, englishCard?.summary) ||
        (isPlaceholderText(card.summary) ? card.summary : ''),
    };
  });
}

function pruneSectionCards(cards: Array<{ heading: string; summary: string; source_path: string }>) {
  const byHeading = new Map<string, { heading: string; summary: string; source_path: string }>();
  const seenSummaries = new Set<string>();
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
    const heading = isPlaceholderText(card.heading) ? '' : card.heading;
    const summaryIsPlaceholder = isPlaceholderText(card.summary);
    if (summaryIsPlaceholder && !card.summary.trim()) {
      continue;
    }
    if (!summaryIsPlaceholder && isPlaceholderCardSummary(heading, card.summary)) {
      continue;
    }
    const summaryKey = card.summary.replace(/\s+/g, ' ').trim().toLowerCase();
    if (summaryKey && seenSummaries.has(summaryKey)) {
      continue;
    }
    if (summaryKey) {
      seenSummaries.add(summaryKey);
    }
    const headingKey = heading.replace(/\s+/g, ' ').trim().toLowerCase();
    if (!headingKey) {
      continue;
    }
    const candidate = summaryIsPlaceholder ? { ...card, heading, summary: '' } : { ...card, heading };
    const current = byHeading.get(headingKey);
    if (!current) {
      byHeading.set(headingKey, candidate);
      continue;
    }
    if (summaryQuality(candidate.summary) > summaryQuality(current.summary)) {
      byHeading.set(headingKey, candidate);
    }
  }
  return [...byHeading.values()];
}

function lookupReportTitle(reportId: string, lang: Lang, network: ReportNetwork): string {
  const node = network.reports.find((row) => row.report_id === reportId);
  if (node) {
    // Reports with no write-up yet carry a generated Chinese placeholder title; show the English one.
    if (lang === 'cn' && !isPlaceholderText(node.title_cn)) {
      return node.title_cn;
    }
    return node.title_en;
  }
  const meta = loadReportMeta(reportId, lang);
  return meta?.title || reportId;
}

// Chips under a related report: the notions both reports use. The order in
// the group is not repeated here; "Previous and next" already gives it.
function connectionBadges(lang: Lang, network: ReportNetwork, row: { shared_notion_ids: string[] }): string[] {
  return row.shared_notion_ids
    .slice(0, 3)
    .map((notionId) => {
      const payload = network.notion_labels[notionId];
      return payload ? notionLabel(lang, notionId, payload.label_en, payload.label_cn) : '';
    })
    .filter(Boolean);
}

function renderConnectionReason(
  lang: Lang,
  network: ReportNetwork,
  row: { shared_notion_ids: string[] },
  hiddenBadges = new Set<string>(),
) {
  const visibleBadges = connectionBadges(lang, network, row).filter((badge) => !hiddenBadges.has(badge));
  if (visibleBadges.length === 0) {
    return null;
  }
  return (
    <p style={{ marginTop: '0.25rem' }}>
      {visibleBadges.map((badge) => (
        <span key={badge} className="badge" style={{ marginRight: '0.35rem' }}>
          {badge}
        </span>
      ))}
    </p>
  );
}

function repeatedConnectionBadges(
  lang: Lang,
  network: ReportNetwork,
  rows: Array<{ shared_notion_ids: string[] }>,
): Set<string> {
  if (rows.length < 2) {
    return new Set<string>();
  }
  const badgeSets = rows.map((row) => new Set(connectionBadges(lang, network, row)));
  return new Set([...badgeSets[0]].filter((badge) => badgeSets.every((set) => set.has(badge))));
}

function renderWipNote(lang: Lang, prefix: string, text: string, network: ReportNetwork): ReactNode {
  const cleanText = text.replace(/^\s*\[[ xX]\]\s*/, '');
  const linkedId = cleanText.match(/^`?([a-z0-9]+(?:_[a-z0-9]+)+)`?\s+—\s+(.+)$/i);
  const knownReport = linkedId && (
    network.reports.some((row) => row.report_id === linkedId[1]) ||
    loadIndex().reports.some((row) => row.report_id === linkedId[1])
  );
  if (linkedId && knownReport) {
    return (
      <>
        <Link href={prefixPath(prefix, `/reports/${linkedId[1]}`)}>{readerText(lookupReportTitle(linkedId[1], lang, network))}</Link>
        {' — '}
        {renderProse(linkedId[2])}
      </>
    );
  }
  return <>{renderProse(cleanText)}</>;
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

function figureFileName(record: FigureRecord): string {
  return (record.source_path || record.web_path).split('/').pop() || record.title;
}

function visibleFigureRecords(records: FigureRecord[]): FigureRecord[] {
  // Only figure files are listed, and a file kept under both figures/ and
  // standalone/ (or any second folder) is listed once, preferring figures/.
  const figures = records.filter((record) => {
    const fileName = figureFileName(record);
    return /\.(pdf|png|jpg|jpeg|webp|svg)$/i.test(fileName) && !/(?:^|[_-])(description|readme)(?:[_-]|\.)/i.test(fileName);
  });
  const inFigures = (record: FigureRecord) => /(?:^|\/)figures\//.test(record.source_path || record.web_path);
  const chosen = new Map<string, FigureRecord>();
  for (const record of figures) {
    const key = figureFileName(record).toLowerCase();
    const current = chosen.get(key);
    if (!current || (!inFigures(current) && inFigures(record))) {
      chosen.set(key, record);
    }
  }
  const keep = new Set(chosen.values());
  return figures.filter((record) => keep.has(record));
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

// Claim text in one language as the theory page shows it: no placeholder, no
// formula residue, no sentence that mixes English and Chinese, and no
// generated "[group] Result statement:" prefix.
function ownClaimText(text: string, lang: Lang): string {
  const t = text
    .replace(/^\s*\[[a-z0-9_-]+\]\s*(?:Model summary|Method chain|Result statement|Finding)\s*[:：]\s*/i, '')
    .replace(/^\s*\[[a-z0-9_-]+\]\s*(?:模型概述|方法链路|结果陈述|发现)\s*[:：]\s*/, '')
    .trim();
  if (!t || isPlaceholderText(t) || isLatexResidue(t) || isMixedLanguageText(t)) {
    return '';
  }
  const hasChinese = /[㐀-鿿]/.test(t);
  return (lang === 'cn') === hasChinese ? t : '';
}

// Longest English row on the theory page; both languages stop after the same
// number of whole sentences.
const THEORY_ROW_CHARS = 220;

function buildNotionClaimDigests(map: ReturnType<typeof loadTheoryMap>, contentMap: ContentMap, lang: Lang) {
  return map.cards.map((card) => {
    const claims = contentMap.claims
      .filter((claim) => card.report_ids.includes(claim.report_id))
      .map((claim) => {
        // A row is shown only when both languages have their own text, so the
        // English and Chinese pages list the same rows with the same content.
        const english = ownClaimText(claim.text_en, 'en');
        const chinese = ownClaimText(claim.text_cn, 'cn');
        const own = lang === 'cn' ? chinese : english;
        return {
          ...claim,
          text: english && chinese ? leadingSentences(own, sentencesWithin(english, THEORY_ROW_CHARS)) : '',
          sourceCount: claim.evidence.filter((ev) => !isGeneratedAssetDatasetPath(ev.path)).length,
        };
      })
      .filter((claim) => Boolean(claim.text))
      .sort((left, right) => {
        const stageDelta = CLAIM_STAGE_ORDER[left.stage] - CLAIM_STAGE_ORDER[right.stage];
        if (stageDelta !== 0) {
          return stageDelta;
        }
        return right.sourceCount - left.sourceCount;
      })
      .slice(0, 5);
    return {
      card,
      claims,
    };
  });
}

// Reading order of the notation cards: basic quantities first.
const NOTATION_ORDER = [
  'fpt',
  'survival',
  'hazard',
  'bimodality-criterion',
  'selfloop-mode',
  'renormalize-mode',
  'equal4-mode',
  'claim-ledger',
];

const TERM_NAMES: Record<string, [string, string]> = {
  'claim-ledger': ['Claims and sources', '结论与出处'],
};

// English term names in sentence case ("Survival Function" → "Survival function");
// abbreviations and words with digits keep their capitals.
function sentenceCase(text: string): string {
  return text
    .split(' ')
    .map((word, index) =>
      word
        .split('-')
        .map((part, partIndex) =>
          (index > 0 || partIndex > 0) && /^[A-Z][a-z]+$/.test(part) ? part.toLowerCase() : part,
        )
        .join('-'),
    )
    .join(' ');
}

function sourceCountLabel(lang: Lang, count: number): string {
  return lang === 'cn' ? `（${count} 处出处）` : `(${count} ${count === 1 ? 'source' : 'sources'})`;
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
    const summary = displayReportText(
      lang,
      (meta?.summary ?? '').replace(/\*\*/g, ''),
      (metaEn?.summary ?? '').replace(/\*\*/g, ''),
    );
    const teaser = displayReportText(lang, meta?.teaser ?? '', metaEn?.teaser ?? '');
    const mapping = bookManifest?.report_chapter_map?.[reportId];
    const chapterId = mapping && mapping.listed !== false ? mapping.primary_chapter_id : undefined;
    const chapter = chapterId ? bookManifest?.chapters.find((row) => row.chapter_id === chapterId) : undefined;
    const successorId = SUPERSEDED_BY[reportId];
    return {
      title: displayTitle(lang, meta, metaEn, reportId),
      summary: teaser || compactText(summary, 520),
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
            `${written.length} written reports on first-passage times, grouped by the setting they study. They are working research reports, not peer-reviewed papers. Each page gives the findings and mathematics, with interactive figures where a research dataset is available; the PDF is the full report. New here? Begin with the three marked “start here”.`,
            `${written.length} 份已成文的首达时间报告，按所研究的模型分组。它们是研究工作报告，不是经过同行评审的论文。每页列出结论和数学推导，有研究数据集的页面还提供交互图，PDF 是报告全文。第一次来，可以先读标着「从这里开始」的三份。`,
          )}
        </p>
        <p className="page-note">
          {localizedText(
            lang,
            'In the ring reports and the 2D two-walker shortcut report, a lazy walker moves with probability q at each step and stays put with probability 1 − q. β is the strength of the shortcut: at the site where the shortcut starts, a fraction β of the stay-put probability 1 − q goes to the shortcut instead.',
            '在环模型的报告以及二维格点上两个游走者相遇（带捷径）的报告里，懒惰游走者每一步以概率 q 移动、以 1 − q 原地不动。β 是捷径强度：在捷径出发的格点，原地不动的概率 1 − q 中有 β 这一份改走捷径。',
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
                      <Link href={prefixPath(prefix, `/reports/${row.report_id}`)}>{readerText(info.title)}</Link>
                      {startIds.has(row.report_id) ? (
                        <span className="tag">{localizedText(lang, 'start here', '从这里开始')}</span>
                      ) : null}
                    </h3>
                    {info.summary ? <p>{renderProse(info.summary)}</p> : null}
                    {info.successor ? (
                      <p className="superseded-note">
                        {localizedText(lang, 'Superseded by ', '已被新版取代：')}
                        <Link href={prefixPath(prefix, `/reports/${info.successor.id}`)}>{readerText(info.successor.title)}</Link>
                      </p>
                    ) : null}
                    <p className="report-row-meta">
                      <PdfLinks lang={lang} reportId={row.report_id} />
                      {info.chapter ? (
                        <span>
                          {localizedText(lang, 'In the book: ', '书中：')}
                          <Link href={prefixPath(prefix, `/book/${info.chapter.chapter_id}`)}>
                            {readerText(lang === 'cn' ? info.chapter.title_cn : info.chapter.title_en)}
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
                  <Link href={prefixPath(prefix, `/reports/${row.report_id}`)}>{readerText(entry(row.report_id).title)}</Link>
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

  const metaEn = loadReportMeta(reportId, 'en');
  const visibleDatasets = meta.datasets.filter(isReaderDataset);
  const isWip = loadRegistryStatus()[reportId] === 'wip';
  const formulaSeen = new Set<string>();
  const visibleMathStory = uniqueFormulas(
    isWip ? meta.math_story.filter((item) => !/fallback/i.test(item.context)) : meta.math_story,
    formulaSeen,
  );
  const figures = visibleFigureRecords(loadFigures(reportId));
  const hasFigureCaptions = figures.some((figure) => figure.title_is_caption);
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
  const hasConnectedReports = Boolean(
    networkNode &&
      (networkNode.previous_in_group ||
        networkNode.next_in_group ||
        networkNode.same_group_links.length > 0 ||
        networkNode.cross_group_links.length > 0),
  );
  const hasSpecificWhereItFits = !isWip || Boolean(bookPlacement || hasConnectedReports || arcsForReport.length > 0);
  const guide = reportGuide(contentMap, reportId);
  const groupedAssets = groupAssets(meta.assets);
  const duplicateAssetCount = Math.max(0, meta.assets.length - groupedAssets.length);
  const localizedFindings = meta.key_findings
    .map((finding, index) =>
      isWip
        ? displayWipNoteText(lang, finding, metaEn?.key_findings[index] ?? '')
        : displayReportText(lang, finding, metaEn?.key_findings[index] ?? ''),
    )
    .filter(Boolean);
  const topFindings = localizedFindings.slice(0, 5);
  const extraFindings = localizedFindings.slice(5);
  // Formula cards that only repeat the logic chain, or each other, are not shown twice.
  const extraMathBlocks = uniqueFormulas(isWip ? ([] as ReportMeta['math_blocks']) : meta.math_blocks, formulaSeen);
  const successorId = SUPERSEDED_BY[reportId];
  const successorTitle = successorId
    ? displayTitle(lang, loadReportMeta(successorId, lang), loadReportMeta(successorId, 'en'), successorId)
    : '';
  const filteredSections = (isWip ? [] : pruneSectionCards(localizeSectionCards(lang, meta.section_cards, metaEn?.section_cards)))
    // Reports written only in Chinese carry Chinese section headings; an English page does not list them.
    .filter((card) => lang !== 'en' || !/[\u3400-\u9fff]/.test(card.heading));
  const sectionsPreview = filteredSections.slice(0, 6);
  const sectionsExtra = filteredSections.slice(6);
  const family = reportFamily(reportId, loadIndex().reports.find((row) => row.report_id === reportId)?.group ?? '');
  const title = displayTitle(lang, meta, metaEn, reportId);
  const rawSummary = (meta.summary || '').replace(/\*\*/g, '');
  // Scaffold reports carry generated template text; show only the status note for them.
  const summary = isWip ? '' : displayReportText(lang, rawSummary, (metaEn?.summary || '').replace(/\*\*/g, ''));
  const narrative = {
    model_overview: displayReportText(
      lang,
      lang === 'cn' ? meta.narrative.model_overview : metaEn?.narrative.model_overview ?? '',
      metaEn?.narrative.model_overview ?? '',
    ),
    method_overview: displayReportText(
      lang,
      lang === 'cn' ? meta.narrative.method_overview : metaEn?.narrative.method_overview ?? '',
      metaEn?.narrative.method_overview ?? '',
    ),
    result_overview: displayReportText(
      lang,
      lang === 'cn' ? meta.narrative.result_overview : metaEn?.narrative.result_overview ?? '',
      metaEn?.narrative.result_overview ?? '',
    ),
  };
  const narrativeSeen = new Set<string>();
  for (const field of ['model_overview', 'method_overview', 'result_overview'] as const) {
    const key = narrative[field].replace(/\s+/g, ' ').trim().toLowerCase();
    if (!key) {
      continue;
    }
    if (narrativeSeen.has(key)) {
      narrative[field] = '';
    } else {
      narrativeSeen.add(key);
    }
  }
  const hasNarrative = !isWip && Object.values(narrative).some(Boolean);
  const seenClaimTexts = new Set<string>();
  const visibleClaims = claimsOrdered
    .map((claim) => ({
      ...claim,
      text: displayReportText(lang, lang === 'cn' ? claim.text_cn : claim.text_en, claim.text_en),
      originalEvidenceCount: claim.evidence.length,
      evidence: claim.evidence
        .filter((ev) => !isGeneratedAssetDatasetPath(ev.path))
        .map((ev) => ({
          ...ev,
          snippet: displayEvidenceSnippet(
            lang,
            lang === 'cn' ? ev.snippet_cn : ev.snippet_en,
            ev.snippet_en,
            metaEn?.title ?? meta.title,
            ev.evidence_type,
          ),
        }))
        .map((ev) => {
          const claimText = displayReportText(lang, lang === 'cn' ? claim.text_cn : claim.text_en, claim.text_en);
          return {
            ...ev,
            kind: evidenceKindLabel(lang, ev.evidence_type),
            file: ev.path,
            // On a Chinese page the snippet may be the English claim sentence again.
            snippet:
              isClaimTextEcho(ev.snippet, claimText) || isClaimTextEcho(ev.snippet, claim.text_en) ? '' : ev.snippet,
          };
        }),
    }))
    .map((claim) => ({ ...claim, evidence: mergeEvidenceRows(lang, claim.evidence) }))
    .filter((claim) => Boolean(claim.text))
    .filter((claim) => {
      const key = claim.text.replace(/\s+/g, ' ').trim().toLowerCase();
      if (!key || seenClaimTexts.has(key)) {
        return false;
      }
      seenClaimTexts.add(key);
      return true;
    });
  const guideObjective = guide
    ? displayReportText(lang, lang === 'cn' ? guide.objective_cn : guide.objective_en, guide.objective_en)
    : '';
  const guideVerificationSteps = guide
    ? lang === 'cn'
      ? guide.verification_steps_cn
      : guide.verification_steps_en
    : [];
  const hasClaimsBlock = visibleClaims.length > 0 || Boolean(guideObjective && guideObjective !== narrative.result_overview);
  const navItems = [
    { id: 'findings', label: isWip ? localizedText(lang, 'Notes so far', '目前的笔记') : localizedText(lang, 'Findings', '结论'), show: topFindings.length > 0 },
    {
      id: 'interactive',
      label: visibleDatasets.length === 1 ? localizedText(lang, 'Interactive figure', '交互图') : localizedText(lang, 'Interactive figures', '交互图'),
      show: visibleDatasets.length > 0,
    },
    { id: 'figures', label: localizedText(lang, 'Figures', '图'), show: figures.length > 0 },
    { id: 'math-chain', label: localizedText(lang, 'Mathematics', '数学'), show: visibleMathStory.length > 0 },
    { id: 'where-it-fits', label: localizedText(lang, 'Where it fits', '在全局中的位置'), show: hasSpecificWhereItFits },
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
        <h1>{readerText(title)}</h1>
        {successorId ? (
          <p className="superseded-banner" role="note">
            <strong>{localizedText(lang, 'Superseded.', '已被取代。')}</strong>{' '}
            {localizedText(lang, 'This is the first version of this study; the revised version is ', '这是该研究的第一版；修订版见：')}
            <Link href={prefixPath(prefix, `/reports/${successorId}`)}>{readerText(successorTitle)} →</Link>
          </p>
        ) : null}
        {!isWip ? (
          <p className="report-status">
            {localizedText(lang, 'Working research report · not peer-reviewed', '研究工作报告 · 未经同行评审')}
          </p>
        ) : null}
        {reportId === 'ring_lazy_jump_ext' ? (
          <p className="page-note report-parameter-note">
            {localizedText(
              lang,
              'β is the strength of the shortcut: at the site where the shortcut starts, a fraction β of the stay-put probability 1 − q goes to the shortcut, so the walker takes it there with probability β(1 − q).',
              'β 是捷径强度：在捷径出发的格点，原地不动的概率 1 − q 中有 β 这一份改走捷径，所以游走者在该格点走捷径的概率是 β(1 − q)。',
            )}
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
        {summary ? <p className="page-lede">{renderProse(summary)}</p> : null}
        <p className="report-row-meta">
          <PdfLinks lang={lang} reportId={reportId} />
          {bookPlacement ? (
            <span>
              {localizedText(lang, 'In the book: ', '书中：')}
              <Link href={prefixPath(prefix, `/book/${bookPlacement.chapterId}`)}>{readerText(bookPlacement.chapterTitle)}</Link>
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
          {narrative.model_overview ? (
            <div>
              <h2>{localizedText(lang, 'Model', '模型')}</h2>
              <p>{renderProse(narrative.model_overview)}</p>
            </div>
          ) : null}
          {narrative.method_overview ? (
            <div>
              <h2>{localizedText(lang, 'Method', '方法')}</h2>
              <p>{renderProse(narrative.method_overview)}</p>
            </div>
          ) : null}
          {narrative.result_overview ? (
            <div>
              <h2>{localizedText(lang, 'Result', '结果')}</h2>
              <p>{renderProse(narrative.result_overview)}</p>
            </div>
          ) : null}
        </section>
      ) : null}

      {topFindings.length > 0 ? (
        <section id="findings" className="card section-enter" style={{ marginTop: '1rem' }}>
          <h3>{isWip ? localizedText(lang, 'Notes so far', '目前的笔记') : localizedText(lang, 'Key findings', '关键结论')}</h3>
          <ul>
            {topFindings.map((line) => (
              <li key={line}>{isWip ? renderWipNote(lang, prefix, line, network) : renderProse(line)}</li>
            ))}
          </ul>
          {extraFindings.length > 0 ? (
            <details>
              <summary>
                {isWip
                  ? localizedText(lang, 'Show remaining notes', '展开剩余笔记')
                  : localizedText(lang, 'Show remaining findings', '展开剩余结论')}
              </summary>
              <ul>
                {extraFindings.map((line) => (
                  <li key={`extra-${line}`}>{isWip ? renderWipNote(lang, prefix, line, network) : renderProse(line)}</li>
                ))}
              </ul>
            </details>
          ) : null}
        </section>
      ) : null}

      {visibleDatasets.length > 0 ? (
        <div id="interactive" style={{ marginTop: '1rem' }}>
          <ReportPlotPanel reportId={reportId} datasets={visibleDatasets} lang={lang} />
        </div>
      ) : null}

      {figures.length > 0 ? (
        <section id="figures" className="card section-enter" style={{ marginTop: '1rem' }}>
          <h3>{hasFigureCaptions ? localizedText(lang, 'Figures', '图') : localizedText(lang, 'Figure files', '图文件')}</h3>
          {figures.some((fig) => isImageFigure(fig.web_path)) ? (
            <div className="grid grid-3">
              {figures
                .filter((fig) => isImageFigure(fig.web_path))
                .slice(0, 12)
                .map((fig) => {
                  const figTitle = (lang === 'cn' && fig.title_cn) || fig.title;
                  return (
                    <article key={fig.id} className="card">
                      <p>{fig.title_is_caption ? renderProse(figTitle) : <code>{figureFileName(fig)}</code>}</p>
                      <a href={withBasePath(fig.web_path)} target="_blank" rel="noreferrer">
                        {/* eslint-disable-next-line @next/next/no-img-element */}
                        <img
                          src={withBasePath(fig.web_path)}
                          alt={plainText(typesetApostrophes(figTitle))}
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
                        {fig.title_is_caption ? renderProse((lang === 'cn' && fig.title_cn) || fig.title) : <code>{figureFileName(fig)}</code>}
                      </a>
                    </li>
                  ))}
              </ul>
              {figures.filter((fig) => !isImageFigure(fig.web_path)).length > 8 ? (
                <details>
                  <summary>
                    {localizedText(
                      lang,
                      `More figures (${figures.filter((fig) => !isImageFigure(fig.web_path)).length - 8})`,
                      `更多图（${figures.filter((fig) => !isImageFigure(fig.web_path)).length - 8}）`,
                    )}
                  </summary>
                  <ul className="figure-list">
                    {figures
                      .filter((fig) => !isImageFigure(fig.web_path))
                      .slice(8)
                      .map((fig) => (
                        <li key={`extra-${fig.id}`}>
                          <a href={withBasePath(fig.web_path)} target="_blank" rel="noreferrer">
                            {fig.title_is_caption ? renderProse((lang === 'cn' && fig.title_cn) || fig.title) : <code>{figureFileName(fig)}</code>}
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

      {visibleMathStory.length > 0 ? <section id="math-chain" className="card section-enter" style={{ marginTop: '1rem' }}>
        <h3>{localizedText(lang, 'Mathematics', '数学')}</h3>
        <div className="grid grid-2">
          {groupMathStoryByCaption(lang, visibleMathStory).map((group, groupIdx) => {
            // Consecutive formulas under the same caption share one card.
            const longest = group.items.reduce(
              (best, item) => (item.latex.trim().length > best.trim().length ? item.latex : best),
              '',
            );
            const sources = [...new Set(group.items.map((item) => item.source_path ?? '').filter((path) => path.trim()))];
            let previousStage = '';
            return (
              <article key={`math-${groupIdx}`} className={formulaCardClass(longest)}>
                {group.caption ? <p className="math-caption">{readerText(group.caption)}</p> : null}
                {group.items.map((item, idx) => {
                  const showStage =
                    !isGeneratedMathStoryStage(item.stage) && item.stage !== group.caption && item.stage !== previousStage;
                  previousStage = item.stage;
                  return (
                    <div key={`${item.stage}-${idx}`}>
                      {showStage ? <h4>{readerText(item.stage)}</h4> : null}
                      {item.description.trim() && !isGeneratedMathStoryDescription(item.description) ? (
                        <p>{renderProse(item.description)}</p>
                      ) : null}
                      <div
                        className={formulaBlockClass(item.latex)}
                        dangerouslySetInnerHTML={{
                          __html: renderLatex(item.latex).html,
                        }}
                      />
                    </div>
                  );
                })}
                {sources.length > 0 ? (
                  <details>
                    <summary>{localizedText(lang, 'Formula source', '公式来源')}</summary>
                    {sources.map((source) => (
                      <p key={source} style={{ marginBottom: 0 }}><code>{source}</code></p>
                    ))}
                  </details>
                ) : null}
              </article>
            );
          })}
        </div>
      </section> : null}

      {extraMathBlocks.length > 0 ? (
        <section id="math-principles" className="card section-enter" style={{ marginTop: '1rem' }}>
          <h3>{localizedText(lang, 'More formulas from the report', '报告中的其他公式')}</h3>
          <div className="grid grid-2">
            {extraMathBlocks.slice(0, 6).map((block, idx) => renderMathBlockCard(lang, block, `${block.source_path}-${idx}`))}
          </div>
          {extraMathBlocks.length > 6 ? (
            <details style={{ marginTop: '0.8rem' }}>
              <summary>{localizedText(lang, 'Show remaining formulas', '展开剩余公式')}</summary>
              <div className="grid grid-2" style={{ marginTop: '0.8rem' }}>
                {extraMathBlocks
                  .slice(6)
                  .map((block, idx) => renderMathBlockCard(lang, block, `extra-${block.source_path}-${idx}`))}
              </div>
            </details>
          ) : null}
        </section>
      ) : null}

      {hasSpecificWhereItFits ? <div id="where-it-fits" className="report-group-head">
        <h2>{localizedText(lang, 'Where it fits', '在全局中的位置')}</h2>
      </div> : null}

      {!isWip || bookPlacement ? <section id="book-position" className="card section-enter" style={{ marginTop: '1rem' }}>
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
              <Link href={prefixPath(prefix, `/book/${bookPlacement.chapterId}`)}>{readerText(bookPlacement.chapterTitle)}</Link>
            </p>
            {bookPlacement.otherChapters.length > 0 ? (
              <p>
                <span className="badge">{localizedText(lang, 'Also appears in', '同时出现于')}</span>{' '}
                {bookPlacement.otherChapters.map((row, idx) => (
                  <span key={`${reportId}-${row.chapterId}`}>
                    {idx > 0 ? localizedText(lang, '; ', '；') : ''}
                    <Link href={prefixPath(prefix, `/book/${row.chapterId}`)}>{readerText(row.title)}</Link>
                  </span>
                ))}
              </p>
            ) : null}
            <ul className="chapter-nav">
              {bookPlacement.previousChapterId ? (
                <li>
                  <Link href={prefixPath(prefix, `/book/${bookPlacement.previousChapterId}`)}>
                    ← {readerText(bookPlacement.previousChapterTitle)}
                  </Link>
                </li>
              ) : null}
              {bookPlacement.nextChapterId ? (
                <li>
                  <Link href={prefixPath(prefix, `/book/${bookPlacement.nextChapterId}`)}>
                    {readerText(bookPlacement.nextChapterTitle)} →
                  </Link>
                </li>
              ) : null}
            </ul>
          </>
        ) : (
          <p>{localizedText(lang, 'No book chapter discusses this report.', '书中没有专门讨论这份报告的章节。')}</p>
        )}
      </section> : null}

      {!isWip || hasConnectedReports ? <section id="connected-reports" className="card section-enter" style={{ marginTop: '1rem' }}>
        <h3>{localizedText(lang, 'Related reports', '相关报告')}</h3>
        <div className="grid grid-3">
          <article className="card">
            <h4>{localizedText(lang, 'Previous and next in this group', '本组的上一篇与下一篇')}</h4>
            <ul>
              {networkNode?.previous_in_group ? (
                <li>
                  {localizedText(lang, 'Previous: ', '上一篇：')}
                  <Link href={prefixPath(prefix, `/reports/${networkNode.previous_in_group}`)}>
                    {readerText(lookupReportTitle(networkNode.previous_in_group, lang, network))}
                  </Link>
                </li>
              ) : (
                <li>{localizedText(lang, 'This is the first report in its group.', '这是本组的第一份报告。')}</li>
              )}
              {networkNode?.next_in_group ? (
                <li>
                  {localizedText(lang, 'Next: ', '下一篇：')}
                  <Link href={prefixPath(prefix, `/reports/${networkNode.next_in_group}`)}>
                    {readerText(lookupReportTitle(networkNode.next_in_group, lang, network))}
                  </Link>
                </li>
              ) : (
                <li>{localizedText(lang, 'This is the last report in its group.', '这是本组的最后一份报告。')}</li>
              )}
            </ul>
          </article>

          <article className="card">
            <h4>{localizedText(lang, 'Related reports in this group', '同组的相关报告')}</h4>
            {networkNode && networkNode.same_group_links.length > 0 ? (
              <ul>
                {(() => {
                  const rows = networkNode.same_group_links.slice(0, 4);
                  const hiddenBadges = repeatedConnectionBadges(lang, network, rows);
                  return rows.map((row) => (
                    <li key={`same-${row.report_id}`}>
                      <Link href={prefixPath(prefix, `/reports/${row.report_id}`)}>
                        {readerText(lookupReportTitle(row.report_id, lang, network))}
                      </Link>
                      {renderConnectionReason(lang, network, row, hiddenBadges)}
                    </li>
                  ));
                })()}
              </ul>
            ) : (
              <p>{localizedText(lang, 'No other related report in this group.', '本组没有其他相关报告。')}</p>
            )}
          </article>

          <article className="card">
            <h4>{localizedText(lang, 'Related reports in other groups', '其他组的相关报告')}</h4>
            {networkNode && networkNode.cross_group_links.length > 0 ? (
              <ul>
                {(() => {
                  const rows = networkNode.cross_group_links.slice(0, 4);
                  const hiddenBadges = repeatedConnectionBadges(lang, network, rows);
                  return rows.map((row) => (
                    <li key={`cross-${row.report_id}`}>
                      <Link href={prefixPath(prefix, `/reports/${row.report_id}`)}>
                        {readerText(lookupReportTitle(row.report_id, lang, network))}
                      </Link>
                      {renderConnectionReason(lang, network, row, hiddenBadges)}
                    </li>
                  ));
                })()}
              </ul>
            ) : (
              <p>{localizedText(lang, 'No related report in another group.', '其他组没有相关报告。')}</p>
            )}
          </article>
        </div>
      </section> : null}

      {!isWip || arcsForReport.length > 0 ? <section id="narrative-arcs" className="card section-enter" style={{ marginTop: '1rem' }}>
        <h3>{localizedText(lang, 'Reading paths', '阅读路线')}</h3>
        {arcsForReport.length > 0 ? (
          <div className="grid grid-2">
            {arcsForReport.map((arc) => {
              const shown = arcDisplay(lang, arc);
              return (
              <article key={`arc-placement-${arc.arc_id}`} className="card">
                <h4>{readerText(shown.label)}</h4>
                {shown.summary ? <p>{renderProse(shown.summary)}</p> : null}
                <details>
                  <summary>
                    {localizedText(lang, `Reports in reading order (${arc.checkpoints.length})`, `按阅读顺序排列的报告（${arc.checkpoints.length} 份）`)}
                  </summary>
                  <ol>
                    {arc.checkpoints.map((cp) => (
                      <li key={`${arc.arc_id}-${cp.report_id}`}>
                        <Link href={prefixPath(prefix, `/reports/${cp.report_id}`)}>
                          {readerText(lang === 'cn' ? cp.title_cn : cp.title_en)}
                        </Link>
                      </li>
                    ))}
                  </ol>
                </details>
              </article>
              );
            })}
          </div>
        ) : (
          <p>{localizedText(lang, 'This report is not on any reading path yet.', '这份报告还不在任何阅读路线中。')}</p>
        )}
      </section> : null}


      <div id="working-record" className="report-group-head">
        <h2>{localizedText(lang, 'Working record', '工作记录')}</h2>
        <p>
          {localizedText(
            lang,
            'The report’s claims with their sources, its section notes, the commands that reproduce it and its files.',
            '这份报告的结论及出处、章节笔记、复现命令和文件。',
          )}
        </p>
      </div>

      <details className="working-record">
        <summary>
          {localizedText(lang, 'Show the working record (claims, notes, commands, files)', '展开工作记录（结论、笔记、命令、文件）')}
        </summary>
        <p className="muted">
          {localizedText(lang, 'Report folder: ', '报告目录：')}
          <code>{reportId}</code>
        </p>

      {hasClaimsBlock ? (
      <section id="verifiable-claims" className="card section-enter" style={{ marginTop: '1rem' }}>
        <h3>{localizedText(lang, 'Claims and sources', '结论与出处')}</h3>
        <p className="lead">
          {localizedText(
            lang,
            'Each claim lists the files it comes from.',
            '每条结论都列出它所依据的文件。',
          )}
        </p>
        {guide && guideObjective && guideObjective !== narrative.result_overview ? (
          <div className="card" style={{ marginBottom: '0.8rem' }}>
            <h4>{localizedText(lang, 'Report objective', '报告目标')}</h4>
            <p>{renderProse(guideObjective)}</p>
            {guideVerificationSteps.length > 0 ? (
              <details>
                <summary>{localizedText(lang, 'Verification steps', '核对步骤')}</summary>
                <ol>
                  {guideVerificationSteps.map((step) => (
                    <li key={step}>{renderProse(step)}</li>
                  ))}
                </ol>
              </details>
            ) : null}
          </div>
        ) : null}
        {visibleClaims.length > 0 ? (
          <div style={{ display: 'grid', gap: '0.9rem' }}>
            {(['model', 'method', 'result', 'finding'] as const).map((stage) => {
              const stageClaims = visibleClaims.filter((claim) => claim.stage === stage);
              if (stageClaims.length === 0) {
                return null;
              }
              return (
                <article key={`stage-${stage}`} className="card">
                  <h4>{stageLabel(lang, stage)}</h4>
                  <div className="grid grid-2">
                    {stageClaims.map((claim) => (
                      <article key={claim.claim_id} className="card">
                        <p>{renderProse(claim.text)}</p>
                        {claim.evidence.length > 0 || claim.originalEvidenceCount === 0 ? (
                          <details>
                            <summary>{localizedText(lang, 'Show sources', '展开出处')}</summary>
                            <ul>
                              {claim.evidence.map((ev, evIdx) => (
                                <li key={`${claim.claim_id}-${evIdx}-${ev.path}`}>
                                  <span className="badge">{ev.kind}</span>{' '}<code>{ev.path}</code>
                                  {ev.snippet ? <p style={{ margin: '0.35rem 0 0' }}>{renderProse(ev.snippet)}</p> : null}
                                </li>
                              ))}
                            </ul>
                          </details>
                        ) : null}
                        {claim.linked_report_ids.length > 0 ? (
                          <p style={{ marginTop: '0.45rem' }}>
                            <span className="badge">{localizedText(lang, 'Related reports', '相关报告')}</span>{' '}
                            {claim.linked_report_ids.slice(0, 4).map((rid) => (
                              <Link
                                key={`${claim.claim_id}-${rid}`}
                                href={prefixPath(prefix, `/reports/${rid}`)}
                                style={{ marginRight: '0.45rem' }}
                              >
                                {readerText(lookupReportTitle(rid, lang, network))}
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
        ) : null}
      </section>
      ) : null}

      {filteredSections.length > 0 ? (
      <section id="narrative-sections" className="card section-enter" style={{ marginTop: '1rem' }}>
        <h3>{localizedText(lang, 'Section notes', '章节笔记')}</h3>
        <div className="grid grid-2">
          {sectionsPreview.map((card) => (
            <article key={`${card.heading}-${card.source_path}`} className="card">
              <h4>{readerText(card.heading)}</h4>
              {card.summary ? <p>{renderProse(card.summary)}</p> : null}
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
                  <h4>{readerText(card.heading)}</h4>
                  {card.summary ? <p>{renderProse(card.summary)}</p> : null}
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
        <h3>{localizedText(lang, 'Commands to reproduce the results', '复现结果的命令')}</h3>
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
            <p>{localizedText(lang, 'The report lists no commands.', '报告中没有列出命令。')}</p>
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
  const notionDigests = buildNotionClaimDigests(map, contentMap, lang);
  const conceptIds = new Set(map.cards.map((card) => card.id));
  const glossaryTerms = glossary?.terms ?? [];
  // A locked term that is also a concept card (AW inversion, β scan) is shown
  // once, as the concept card, which also carries the term's formula.
  const conceptFormula = new Map(
    glossaryTerms
      .filter((term) => conceptIds.has(term.term_id) && term.formula)
      .map((term) => [term.term_id, term.formula ?? ''] as const),
  );
  const orderOf = (termId: string) => {
    const position = NOTATION_ORDER.indexOf(termId);
    return position < 0 ? NOTATION_ORDER.length : position;
  };
  const notationTerms = glossaryTerms
    .filter(
      (term) =>
        term.category !== 'theory-card' &&
        !term.term_id.startsWith('theory-') &&
        !conceptIds.has(term.term_id) &&
        !isSiteGlossaryTerm(term),
    )
    .sort((left, right) => orderOf(left.term_id) - orderOf(right.term_id) || left.term_id.localeCompare(right.term_id));
  const termName = (term: (typeof glossaryTerms)[number]) => {
    const names = TERM_NAMES[term.term_id];
    if (names) {
      return lang === 'cn' ? names[1] : names[0];
    }
    return lang === 'cn' ? term.term_cn : sentenceCase(term.term_en);
  };
  const reportLink = (reportId: string, key: string) => (
    <li key={key}>
      <Link href={prefixPath(prefix, `/reports/${reportId}`)}>{readerText(lookupReportTitle(reportId, lang, network))}</Link>
    </li>
  );

  return (
    <AppShell lang={lang} prefix={prefix}>
      <section className="card section-enter">
        <div className="kicker">{localizedText(lang, 'Theory', '理论')}</div>
        <h1>{localizedText(lang, 'Mathematics shared across the reports', '各报告共用的数学')}</h1>
        <p>
          {localizedText(
            lang,
            'The ideas that recur across the reports, the reports that use each one, and what those reports state about it.',
            '多份报告反复用到的数学概念、用到每个概念的报告，以及这些报告对它得出的结论。',
          )}
        </p>
      </section>

      <section className="card section-enter" style={{ marginTop: '1rem' }}>
        <h2>{localizedText(lang, 'How to read this page', '怎么读这一页')}</h2>
        <ol>
          <li>
            {lang === 'cn' ? (
              <>
                先读<Link href={prefixPath(prefix, '/book')}>书</Link>
                的第0章和第1章：那里统一了符号，并给出基本的量，即首达时间 T（FPT，游走者第一次到达目标的那一步），它的概率质量函数 f(t) = P(T = t)（PMF），以及累积分布函数（CDF）。
              </>
            ) : (
              <>
                Start with chapters 0 and 1 of <Link href={prefixPath(prefix, '/book')}>the Book</Link>: they set the
                notation and the basic quantities: the first-passage time T (FPT, the step at which the walker first reaches
                the target), its probability mass function f(t) = P(T = t) (PMF) and its cumulative distribution function
                (CDF).
              </>
            )}
          </li>
          <li>
            {localizedText(
              lang,
              'The concept cards name the ideas the reports share and list the reports that use each one. One of them is Abate–Whitt (AW) inversion, which recovers the distribution over time numerically from its generating function.',
              '概念卡片列出各报告共用的概念，以及用到每个概念的报告。其中之一是 Abate–Whitt 反演（AW）：由生成函数用数值方法求出随时间的分布。',
            )}
          </li>
          <li>
            {localizedText(
              lang,
              '“Concepts, claims and sources” gives, for each concept, what the reports state about it and how many sources back each statement.',
              '「概念、结论与出处」一节按概念列出各报告的结论，并注明每条结论有几处出处。',
            )}
          </li>
        </ol>
        <p>
          <span className="badge">{localizedText(lang, `${map.cards.length} concept cards`, `${map.cards.length} 张概念卡片`)}</span>{' '}
          <span className="badge">{localizedText(lang, `${contentMap.claims.length} claims`, `${contentMap.claims.length} 条结论`)}</span>{' '}
          <span className="badge">{localizedText(lang, `${bookManifest?.chapter_count ?? 0} book chapters`, `书中 ${bookManifest?.chapter_count ?? 0} 章`)}</span>
        </p>
      </section>

      {backbone ? (
        <section className="card section-enter" style={{ marginTop: '1rem' }}>
          <h2>{localizedText(lang, 'How the Book is organised', '书的结构')}</h2>
          <p className="lead">
            {localizedText(
              lang,
              `The Book has ${backbone.acts.length} parts. Each part lists its chapters.`,
              `书分为 ${backbone.acts.length} 个部分，下面列出每部分的章节。`,
            )}
          </p>
          <div className="grid grid-2">
            {backbone.acts.map((act) => (
              <article key={`act-${act.act_id}`} className="card">
                <h3>{readerText(lang === 'cn' ? act.title_cn : act.title_en)}</h3>
                <p>{readerText(lang === 'cn' ? act.objective_cn : act.objective_en)}</p>
                <p>
                  <span className="badge">
                    {lang === 'cn'
                      ? `${act.chapter_ids.length} 章`
                      : `${act.chapter_ids.length} ${act.chapter_ids.length === 1 ? 'chapter' : 'chapters'}`}
                  </span>
                </p>
                <ul>
                  {act.chapter_ids.map((chapterId) => {
                    const chapterMeta = bookManifest?.chapters.find((row) => row.chapter_id === chapterId);
                    if (!chapterMeta) {
                      return null;
                    }
                    return (
                      <li key={`act-${act.act_id}-${chapterId}`}>
                        <Link href={prefixPath(prefix, `/book/${chapterId}`)}>
                          {readerText(lang === 'cn' ? chapterMeta.title_cn : chapterMeta.title_en)}
                        </Link>
                      </li>
                    );
                  })}
                </ul>
              </article>
            ))}
          </div>
        </section>
      ) : null}

      <section className="card section-enter" style={{ marginTop: '1rem' }}>
        <h2>{localizedText(lang, 'Concept cards', '概念卡片')}</h2>
        <div className="grid grid-2">
          {map.cards.map((card) => {
            const formula = conceptFormula.get(card.id);
            return (
              <article key={card.id} className="card">
                <h3>{notionLabel(lang, card.id, card.label_en, card.label_cn)}</h3>
                <p>{renderProse(lang === 'cn' ? card.description_cn : card.description_en)}</p>
                {renderGlossaryFormula(formula ?? '')}
                <p>
                  <span className="badge">
                    {lang === 'cn'
                      ? `${card.report_count} 份报告`
                      : `${card.report_count} ${card.report_count === 1 ? 'report' : 'reports'}`}
                  </span>
                </p>
                <ul>{card.report_ids.slice(0, 8).map((reportId) => reportLink(reportId, reportId))}</ul>
                {card.report_ids.length > 8 ? (
                  <details>
                    <summary>{localizedText(lang, 'Show all reports', '展开全部报告')}</summary>
                    <ul>{card.report_ids.slice(8).map((reportId) => reportLink(reportId, `extra-${reportId}`))}</ul>
                  </details>
                ) : null}
              </article>
            );
          })}
        </div>
      </section>

      {notationTerms.length > 0 ? (
        <section className="card section-enter" style={{ marginTop: '1rem' }}>
          <h2>{localizedText(lang, 'Notation and terms', '符号与术语')}</h2>
          <p className="lead">
            {localizedText(
              lang,
              'Symbols and terms used across the reports, each with its definition and, where there is one, its formula.',
              '各报告通用的符号和术语，附定义；有公式的一并给出。',
            )}
          </p>
          <div className="grid grid-2">
            {notationTerms.map((term) => (
              <article key={term.term_id} className="card">
                <h3>{readerText(termName(term))}</h3>
                <p>{renderProse(lang === 'cn' ? term.definition_cn : term.definition_en)}</p>
                {renderGlossaryFormula(term.formula ?? '')}
              </article>
            ))}
          </div>
        </section>
      ) : null}

      <section className="card section-enter" style={{ marginTop: '1rem' }}>
        <h2>{localizedText(lang, 'Concepts, claims and sources', '概念、结论与出处')}</h2>
        <p className="lead">
          {localizedText(
            lang,
            'For each concept, up to five statements from the reports that use it, with the number of sources behind each.',
            '每个概念下列出用到它的报告中的结论，最多五条，并注明每条结论有几处出处。',
          )}
        </p>
        <div className="grid grid-2">
          {notionDigests.map(({ card, claims }) => (
            <article key={`notion-claims-${card.id}`} className="card">
              <h3>{notionLabel(lang, card.id, card.label_en, card.label_cn)}</h3>
              <p className="muted">{renderProse(lang === 'cn' ? card.description_cn : card.description_en)}</p>
              {claims.length > 0 ? (
                <ul>
                  {claims.map((claim) => (
                    <li key={claim.claim_id}>
                      <span className="badge">{stageLabel(lang, claim.stage)}</span>{' '}
                      <Link href={prefixPath(prefix, `/reports/${claim.report_id}`)}>
                        {readerText(lookupReportTitle(claim.report_id, lang, network))}
                      </Link>{' '}
                      <span className="muted">{sourceCountLabel(lang, claim.sourceCount)}</span>
                      <div>{renderProse(claim.text)}</div>
                    </li>
                  ))}
                </ul>
              ) : (
                <p className="muted">{localizedText(lang, 'No statements recorded yet.', '暂无结论。')}</p>
              )}
            </article>
          ))}
        </div>
      </section>

      <section className="card section-enter" style={{ marginTop: '1rem' }}>
        <h2>{localizedText(lang, 'Reading order within each group', '各组的阅读顺序')}</h2>
        <p className="lead">
          {localizedText(lang, 'The reports of each group, in reading order.', '每组报告按阅读顺序排列。')}
        </p>
        <div className="grid grid-3">
          {network.group_paths.map((route) => (
            <article key={`route-${route.group}`} className="card">
              <h3>{groupName(lang, route.group)}</h3>
              <ol>{route.report_ids.map((reportId) => reportLink(reportId, `route-${route.group}-${reportId}`))}</ol>
            </article>
          ))}
        </div>
      </section>

      <section className="card section-enter" style={{ marginTop: '1rem' }}>
        <h2>{localizedText(lang, 'Reading paths', '阅读路线')}</h2>
        <div className="grid grid-2">
          {contentMap.arcs.map((arc) => {
            const shown = arcDisplay(lang, arc);
            return (
              <article key={`arc-${arc.arc_id}`} className="card">
                <h3>{readerText(shown.label)}</h3>
                {shown.summary ? <p>{renderProse(shown.summary)}</p> : null}
                <p>
                  <span className="badge">
                    {localizedText(lang, `Reports: ${arc.checkpoint_count}`, `报告：${arc.checkpoint_count}`)}
                  </span>{' '}
                  <span className="badge">
                    {localizedText(lang, `Claims: ${arc.claim_ids.length}`, `结论数：${arc.claim_ids.length}`)}
                  </span>
                </p>
                <details>
                  <summary>{localizedText(lang, 'Show the reports in reading order', '展开按阅读顺序排列的报告')}</summary>
                  <ol>
                    {arc.checkpoints.map((cp) => (
                      <li key={`${arc.arc_id}-${cp.report_id}`}>
                        <Link href={prefixPath(prefix, `/reports/${cp.report_id}`)}>
                          {readerText(lang === 'cn' ? cp.title_cn : cp.title_en)}
                        </Link>
                      </li>
                    ))}
                  </ol>
                </details>
              </article>
            );
          })}
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
        <div className="kicker">Machine-readable</div>
        <h1>Agent sync</h1>
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
        <h3>{localizedText(lang, 'Agent workflow', 'Agent 使用流程')}</h3>
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
        <div className="kicker">Repository mirror</div>
        <h1>{localizedText(lang, 'Repository sync', '仓库同步视图')}</h1>
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
        <h2>{localizedText(lang, 'Synced sections', '同步分区')}</h2>
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
        <h2>{localizedText(lang, 'Synced file index', '同步文件索引')}</h2>
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
            'Each report is written in LaTeX next to the code and data that produce its figures. The pages here are generated from those sources and rebuilt when the repository changes. Summaries and findings on the pages are extracted from the reports; the PDF is the report itself.',
            '每份报告用 LaTeX 写成，和生成图的代码、数据放在一起。这里的页面由这些源文件生成，仓库一有变动就重新构建。页面上的摘要和结论摘自报告本身；PDF 才是报告全文。',
          )}
        </p>
        <p>
          {generated
            ? readerText(
                localizedText(
                  lang,
                  `This is an active research repository, and reports are revised as the work continues. These pages were generated on ${generated}.`,
                  `这是一个仍在进行的研究仓库，报告会随研究推进而修订。本页面生成于 ${generated}。`,
                ),
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
