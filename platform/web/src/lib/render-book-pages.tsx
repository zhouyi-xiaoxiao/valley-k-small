import Link from 'next/link';
import { AppShell } from '@/components/AppShell';
import { LazyDisclosure } from '@/components/LazyDisclosure';
import { ReportPlotPanel } from '@/components/ReportPlotPanel';
import {
  loadBookBackbone,
  loadBookClaimCoverage,
  loadBookChapter,
  loadBookManifest,
  loadContentMap,
  loadGlossary,
  loadReportMeta,
  localizedText,
  prefixPath,
} from '@/lib/content';
import {
  displayEvidenceSnippet,
  displayTitle,
  evidenceKindLabel,
  formulaBlockClass,
  formulaCardClass,
  formulaKey,
  isClaimTextEcho,
  isGeneratedAssetDatasetPath,
  isReaderDataset,
  isGeneratedMathStoryDescription,
  isGeneratedMathStoryStage,
  isGenericMathStoryContext,
  isLatexResidue,
  isPlaceholderText,
  isSiteGlossaryTerm,
  mergeEvidenceRows,
  renderGlossaryFormula,
  readerText,
  renderLatex,
  renderProse,
  withoutInlineMath,
} from '@/lib/atlas';
import type { BookChapter, Lang } from '@/types';

function chapterTitle(chapter: BookChapter, lang: Lang): string {
  return lang === 'cn' ? chapter.title_cn : chapter.title_en;
}

function chapterKicker(chapter: BookChapter, lang: Lang): string {
  return lang === 'cn' ? chapter.kicker_cn : chapter.kicker_en;
}

function chapterIntro(chapter: BookChapter, lang: Lang): string[] {
  return lang === 'cn' ? chapter.intro_cn : chapter.intro_en;
}

function chapterSummary(chapter: BookChapter, lang: Lang): string {
  return lang === 'cn' ? chapter.summary_cn : chapter.summary_en;
}

// "Chapter 4: Shortcut variants" → "Shortcut variants", "第4章：捷径的各种变体" →
// "捷径的各种变体", for cards whose badge already gives the number.
function titleWithoutChapterNumber(title: string): string {
  const stripped = title.replace(/^(?:Chapter\s+\d+\s*[:：]|第\s*\d+\s*章\s*[:：])\s*/, '').trim();
  return stripped || title;
}

function bookReportTitle(lang: Lang, reportId: string): string {
  return displayTitle(lang, loadReportMeta(reportId, lang), loadReportMeta(reportId, 'en'), reportId);
}

const CLAIM_STAGE_LABELS: Record<string, [string, string]> = {
  model: ['Model', '模型'],
  method: ['Method', '方法'],
  result: ['Result', '结果'],
  finding: ['Finding', '发现'],
};

function claimStageLabel(lang: Lang, stage: string): string {
  const label: [string, string] | undefined = CLAIM_STAGE_LABELS[stage.trim().toLowerCase()];
  if (!label) {
    return localizedText(lang, 'Claim', '结论');
  }
  return lang === 'cn' ? label[1] : label[0];
}

function reportCountLabel(lang: Lang, count: number): string {
  return lang === 'cn' ? `${count} 份报告` : `${count} ${count === 1 ? 'report' : 'reports'}`;
}

function claimCountLabel(lang: Lang, count: number): string {
  return lang === 'cn' ? `${count} 条结论` : `${count} ${count === 1 ? 'claim' : 'claims'}`;
}

// A concept card counts every report in the atlas that uses the concept, not
// only this chapter's reports.
function conceptReportCountLabel(lang: Lang, count: number): string {
  return lang === 'cn' ? `共有 ${count} 份报告用到` : `Used in ${count} ${count === 1 ? 'report' : 'reports'} of the atlas`;
}

// "Interactive figure", as on report pages.
function chartCountLabel(lang: Lang, count: number): string {
  return lang === 'cn' ? `${count} 张交互图` : `${count} ${count === 1 ? 'interactive figure' : 'interactive figures'}`;
}

function chartSectionTitle(lang: Lang, count: number): string {
  return count === 1
    ? localizedText(lang, 'Interactive figure from the report', '报告中的交互图')
    : localizedText(lang, 'Interactive figures from the reports', '报告中的交互图');
}

// Where an evidence row points, in reader words: "English manuscript" or a
// file name, never the report folder name (which is the report id).
function evidenceSourceLabel(lang: Lang, sourcePath: string): string {
  const clean = sourcePath.trim().replace(/[?#].*$/, '').replace(/\/+$/, '');
  const reportId = clean.match(/(?:^|\/)reports\/([^/]+)/)?.[1] ?? '';
  const name = clean.split('/').pop() ?? '';
  if (!name || name === reportId) {
    return localizedText(lang, 'Report folder', '报告目录');
  }
  const manuscript = name.match(/_(en|cn)\.(?:tex|pdf)$/i);
  if (/(?:^|\/)manuscript\//.test(clean) && manuscript && reportId && name.startsWith(reportId)) {
    return manuscript[1].toLowerCase() === 'cn'
      ? localizedText(lang, 'Chinese manuscript', '中文稿')
      : localizedText(lang, 'English manuscript', '英文稿');
  }
  const readable = reportId ? name.split(reportId).join('').replace(/^[_.-]+/, '') : name;
  return readable || localizedText(lang, 'Report file', '报告文件');
}

function displayChapterClaimText(lang: Lang, text: string, englishText = ''): string {
  const own = text.trim();
  if (!isPlaceholderText(own) && !isLatexResidue(own)) {
    return own;
  }
  if (lang === 'cn' && englishText && !isPlaceholderText(englishText) && !isLatexResidue(englishText)) {
    return englishText.trim();
  }
  return '';
}

type ChapterClaim = BookChapter['claim_ledger'][number];

// Claims the book builder wrote itself rather than took from a report (older
// data had notes on how the repository is run for chapters 6 and 7; the
// builder's stand-in for a chapter without claims is one too). Their ids start
// with the chapter id. They are not shown.
function isChapterOwnClaim(chapterId: string, claim: ChapterClaim): boolean {
  return claim.claim_id.startsWith(`${chapterId}-`);
}

function chapterClaimText(lang: Lang, claim: ChapterClaim): string {
  return displayChapterClaimText(lang, lang === 'cn' ? claim.text_cn : claim.text_en, claim.text_en);
}

// The claims a chapter shows: taken from a report, with text in this language.
function readerClaims(chapter: BookChapter, lang: Lang): ChapterClaim[] {
  return chapter.claim_ledger.filter(
    (claim) => !isChapterOwnClaim(chapter.chapter_id, claim) && Boolean(chapterClaimText(lang, claim)),
  );
}

function visibleChapterEvidence(claim: ChapterClaim, lang: Lang) {
  const reportTitle = loadReportMeta(claim.report_id, 'en')?.title ?? '';
  const claimText = chapterClaimText(lang, claim);
  let previousKey = '';
  const rows = claim.evidence
    .filter((ev) => !isGeneratedAssetDatasetPath(ev.path))
    .map((ev) => {
      const snippet = displayEvidenceSnippet(
        lang,
        lang === 'cn' ? ev.snippet_cn : ev.snippet_en,
        ev.snippet_en,
        reportTitle,
      );
      return {
        path: ev.path,
        kind: evidenceKindLabel(lang, ev.evidence_type),
        file: evidenceSourceLabel(lang, ev.path),
        snippet: isClaimTextEcho(snippet, claimText) ? '' : snippet,
      };
    })
    .filter((ev) => {
      const key = `${ev.kind}\u0000${ev.file}\u0000${ev.snippet}`;
      if (key === previousKey) {
        return false;
      }
      previousKey = key;
      return true;
    });
  return mergeEvidenceRows(lang, rows);
}

function normalizeReaderText(text: string): string {
  return text.replace(/\s+/g, ' ').trim().toLowerCase();
}

type TheoryItem = BookChapter['theory_chain'][number];

// Formulas the book builder wrote rather than took from a report: its
// placeholder for a chapter without formulas, its stand-in f, S, h definition
// for a report with no extracted formula (context "Fallback"), and, in older
// data, the chapter 6 and 7 notes on how the repository is run (stages
// "validation" and "outlook"). They are not shown.
function isBuilderTheoryItem(item: TheoryItem): boolean {
  const stage = item.stage.trim().toLowerCase();
  return (
    stage === 'theory_placeholder' ||
    stage === 'validation' ||
    stage === 'outlook' ||
    item.context.trim().toLowerCase() === 'fallback'
  );
}

// In the book a formula is shown only if the page tells the reader what it is:
// a section heading in the page's language, or a description. An uncaptioned
// line is usually a parameter setting or an assignment
// ("(g_x, g_y, δ) = (−0.25, 0.40, 0.70)", "Δ = δ p_stay") that says nothing
// outside its report. Report pages show all formulas.
function isBookReaderFormula(lang: Lang, item: TheoryItem): boolean {
  return Boolean(formulaCaption(lang, item) || formulaDescription(lang, item));
}

// A chapter's formulas, each formula once (under the first report that has it).
function readerTheoryItems(chapter: BookChapter, lang: Lang): TheoryItem[] {
  const seen = new Set<string>();
  return chapter.theory_chain.filter((item) => {
    const key = formulaKey(item.latex);
    if (isBuilderTheoryItem(item) || !key || seen.has(key) || !isBookReaderFormula(lang, item)) {
      return false;
    }
    seen.add(key);
    return true;
  });
}

// Consecutive formulas from the same report share one card.
function groupTheoryChain(items: TheoryItem[]): Array<{ reportId: string; items: TheoryItem[] }> {
  const groups: Array<{ reportId: string; items: TheoryItem[] }> = [];
  for (const item of items) {
    const last = groups[groups.length - 1];
    if (last && last.reportId === item.report_id) {
      last.items.push(item);
    } else {
      groups.push({ reportId: item.report_id, items: [item] });
    }
  }
  return groups;
}

function isPageLanguage(lang: Lang, text: string): boolean {
  const han = /[㐀-鿿]/.test(text);
  return lang === 'cn' ? han : !han;
}

// The formula's source section heading, as a caption: only a real heading in
// the page's language. Older data wrote "Report title · stage"; the part
// before " · " repeats the card's link and is dropped.
function formulaCaption(lang: Lang, item: TheoryItem): string {
  const raw = (lang === 'cn' ? item.label_cn : item.label_en).trim();
  const heading = raw.includes(' · ') ? raw.slice(raw.lastIndexOf(' · ') + 3).trim() : raw;
  if (
    !heading ||
    !isPageLanguage(lang, heading) ||
    isGenericMathStoryContext(heading) ||
    isGeneratedMathStoryStage(heading)
  ) {
    return '';
  }
  return heading;
}

// A description is prose in its language with any mathematics inside $…$:
// not a generated sentence, and no TeX (commands, ^, _, braces) outside the
// dollar signs.
function isReaderDescription(lang: Lang, text: string): boolean {
  const value = text.trim();
  if (!value || isGeneratedMathStoryDescription(value) || isPlaceholderText(value) || !isPageLanguage(lang, value)) {
    return false;
  }
  const outsideMath = withoutInlineMath(value);
  return !outsideMath.includes('$') && !/\\[A-Za-z]|[\^_{}]/.test(outsideMath);
}

// Printed in both languages or in neither, so the two pages stay in step.
function formulaDescription(lang: Lang, item: TheoryItem): string {
  if (!isReaderDescription('en', item.description_en) || !isReaderDescription('cn', item.description_cn)) {
    return '';
  }
  return (lang === 'cn' ? item.description_cn : item.description_en).trim();
}

function renderTheoryGroupCard(
  lang: Lang,
  prefix: string,
  group: { reportId: string; items: TheoryItem[] },
  key: string,
) {
  let previousCaption = '';
  let previousDescription = '';
  const rows = group.items.map((item) => {
    const caption = formulaCaption(lang, item);
    const description = formulaDescription(lang, item);
    const row = {
      caption: caption && caption !== previousCaption ? caption : '',
      description: description && normalizeReaderText(description) !== normalizeReaderText(previousDescription) ? description : '',
      html: renderLatex(item.latex).html,
      latex: item.latex,
    };
    previousCaption = caption || previousCaption;
    previousDescription = description || previousDescription;
    return row;
  });
  // The same width rules as on report pages, taken from the card's longest formula.
  const longest = group.items.reduce((best, item) => (item.latex.trim().length > best.trim().length ? item.latex : best), '');
  return (
    <article key={key} className={formulaCardClass(longest)}>
      <p>
        <Link href={prefixPath(prefix, `/reports/${group.reportId}`)}>{readerText(bookReportTitle(lang, group.reportId))}</Link>
      </p>
      {rows.map((row, idx) => (
        <div key={`${key}-formula-${idx}`}>
          {row.caption ? <p className="math-caption">{readerText(row.caption)}</p> : null}
          {row.description ? <p>{renderProse(row.description)}</p> : null}
          <div className={formulaBlockClass(row.latex)} dangerouslySetInnerHTML={{ __html: row.html }} />
        </div>
      ))}
    </article>
  );
}

// Shorten a text for the examples block. A text is cut only after a full
// sentence, with nothing appended. If the first sentence alone is too long, it
// is cut at its last clause boundary and "…" follows directly.
function shortLine(text: string, max: number): string {
  const value = String(text || '').replace(/\s+/g, ' ').trim();
  if (value.length <= max) {
    return value;
  }
  const sentenceEnd = /[.!?](?=\s)|[。！？]/g;
  let cut = -1;
  let match: RegExpExecArray | null;
  while ((match = sentenceEnd.exec(value)) !== null) {
    const end = match.index + match[0].length;
    if (end > max) {
      break;
    }
    if ((value.slice(0, end).match(/\$/g) || []).length % 2 === 0) {
      cut = end;
    }
  }
  if (cut > 0) {
    return value.slice(0, cut).trimEnd();
  }
  const head = value.slice(0, max);
  const clause = Math.max(head.lastIndexOf(', '), head.lastIndexOf('; '), head.lastIndexOf('，'), head.lastIndexOf('；'));
  const space = head.lastIndexOf(' ');
  let end = clause > 0 ? clause : space > 0 ? space : max;
  if ((head.slice(0, end).match(/\$/g) || []).length % 2 === 1) {
    // Never end inside a $…$ formula.
    end = head.lastIndexOf('$', end - 1);
  }
  return `${head.slice(0, end).replace(/[\s.,;:!?，。；：、！？]+$/, '')}…`;
}

type ChapterExample = { claimId: string; reportId: string; label: string; text: string };

// One claim per stage, each shown on its own with the report it comes from.
// The claims usually come from different reports, so they are not joined
// into one story.
function chapterExamples(chapter: BookChapter, lang: Lang): ChapterExample[] {
  const stages = ['model', 'method', 'result', 'finding'] as const;
  return stages.flatMap((stage) => {
    const claim = readerClaims(chapter, lang).find((row) => row.stage === stage);
    if (!claim) {
      return [];
    }
    const text = chapterClaimText(lang, claim);
    const max = /[\u3400-\u9fff]/.test(text) ? 260 : 420;
    return [{ claimId: claim.claim_id, reportId: claim.report_id, label: claimStageLabel(lang, stage), text: shortLine(text, max) }];
  });
}

function renderChapterExamples(lang: Lang, prefix: string, examples: ChapterExample[]) {
  return examples.map((example) => (
    <p key={`example-${example.claimId}`} data-claim-id={example.claimId}>
      <strong>{example.label}</strong>
      {lang === 'cn' ? '：' : ': '}
      {renderProse(example.text)}
      {lang === 'cn' ? '' : ' '}
      <span className="muted">
        {lang === 'cn' ? '（' : '('}
        <Link href={prefixPath(prefix, `/reports/${example.reportId}`)}>{readerText(bookReportTitle(lang, example.reportId))}</Link>
        {lang === 'cn' ? '）' : ')'}
      </span>
    </p>
  ));
}

function renderClaimCard(lang: Lang, prefix: string, claim: ChapterClaim, key: string) {
  const evidence = visibleChapterEvidence(claim, lang);
  return (
    <article key={key} className="card" data-claim-id={claim.claim_id} data-report-id={claim.report_id}>
      <p>
        <span className="badge">{claimStageLabel(lang, claim.stage)}</span>{' '}
        <Link href={prefixPath(prefix, `/reports/${claim.report_id}`)}>{readerText(bookReportTitle(lang, claim.report_id))}</Link>
      </p>
      <p>{renderProse(chapterClaimText(lang, claim))}</p>
      {evidence.length > 0 ? (
        <details>
          <summary>{localizedText(lang, 'Show sources', '展开出处')}</summary>
          <ul>
            {evidence.map((ev, index) => (
              <li key={`${claim.claim_id}-${index}`} data-path={ev.path}>
                <span className="badge">{ev.kind}</span> {ev.file}
                {ev.snippet ? <p>{renderProse(ev.snippet)}</p> : null}
              </li>
            ))}
          </ul>
        </details>
      ) : null}
    </article>
  );
}

function readerPanels(chapter: BookChapter, lang: Lang) {
  return chapter.interactive_panels.flatMap((panel) => {
    const meta = loadReportMeta(panel.report_id, lang);
    const availableDatasets = (meta?.datasets || []).filter((dataset) => isReaderDataset(dataset));
    const configuredDataset = availableDatasets.find((dataset) => dataset.series_id === panel.dataset_series_id);
    const selectedDatasets = configuredDataset ? [configuredDataset] : availableDatasets.slice(0, 1);
    return selectedDatasets.length > 0 ? [{ panel, selectedDatasets }] : [];
  });
}

function loadOrderedBookChapters(): BookChapter[] {
  const manifest = loadBookManifest();
  if (!manifest) {
    return [];
  }
  return [...manifest.chapters]
    .sort((a, b) => a.order - b.order)
    .map((meta) => loadBookChapter(meta.chapter_id))
    .filter((row): row is BookChapter => Boolean(row));
}

export function renderBookPage(lang: Lang, prefix: string) {
  const manifest = loadBookManifest();
  const backbone = loadBookBackbone();
  const claimCoverage = loadBookClaimCoverage();
  const glossary = loadGlossary();

  if (!manifest) {
    return (
      <AppShell lang={lang} prefix={prefix}>
        <section className="card section-enter">
          <h1>{localizedText(lang, 'Book data missing', '未找到书籍数据')}</h1>
          <p>{localizedText(lang, 'Run reportctl book-data first.', '请先运行 reportctl book-data。')}</p>
        </section>
      </AppShell>
    );
  }

  const chapterRows = [...manifest.chapters].sort((a, b) => a.order - b.order);
  const chapterTitleById = new Map<string, string>(
    chapterRows.map((row): [string, string] => [row.chapter_id, lang === 'cn' ? row.title_cn : row.title_en]),
  );
  const glossaryPreview = (glossary?.terms || []).filter((term) => !isSiteGlossaryTerm(term)).slice(0, 8);
  // Claims no chapter uses, counted per report so the list names reports, not claim ids.
  const excludedByReport: Array<{ reportId: string; count: number }> = [];
  if (claimCoverage && claimCoverage.excluded_claim_ids.length > 0) {
    const reportOfClaim = new Map<string, string>(
      loadContentMap().claims.map((claim): [string, string] => [claim.claim_id, claim.report_id]),
    );
    const counts = new Map<string, number>();
    for (const claimId of claimCoverage.excluded_claim_ids) {
      const reportId = reportOfClaim.get(claimId) ?? claimId.replace(/-c\d+$/, '');
      counts.set(reportId, (counts.get(reportId) ?? 0) + 1);
    }
    counts.forEach((count, reportId) => excludedByReport.push({ reportId, count }));
  }

  return (
    <AppShell lang={lang} prefix={prefix}>
      <section className="card section-enter book-hero">
        <div className="kicker">{localizedText(lang, 'Book', '书')}</div>
        <h1>{localizedText(lang, 'Valley-K Small research book', 'Valley-K Small 研究电子书')}</h1>
        <p className="lead">
          {localizedText(
            lang,
            'The reports read as one argument, from notation (Chapter 0) to open questions (Chapter 7). Each chapter links to the reports, figures and claims it rests on.',
            '把各份报告串成一条论证：从记号（第0章）到开放问题（第7章）。每章都连回它所依据的报告、图和结论。',
          )}
        </p>
        <p>
          <Link href={prefixPath(prefix, '/book/continuous')} className="badge">
            {localizedText(lang, 'Start continuous reading', '开始整本通读')}
          </Link>{' '}
          <Link href={prefixPath(prefix, '/book/chapter-0-reading-guide')} className="badge">
            {localizedText(lang, 'Open Chapter 0', '从第0章开始')}
          </Link>
        </p>
      </section>

      <section className="card section-enter" style={{ marginTop: '1rem' }}>
        <h2>{localizedText(lang, 'Contents', '目录')}</h2>
        <div className="book-toc-grid">
          {chapterRows.map((chapter) => (
            <article key={chapter.chapter_id} className="card book-chapter-card">
              <p className="badge">{lang === 'cn' ? `第${chapter.order}章` : `Chapter ${chapter.order}`}</p>
              <h3>
                <Link
                  href={prefixPath(prefix, `/book/${chapter.chapter_id}`)}
                  aria-label={lang === 'cn' ? chapter.title_cn : chapter.title_en}
                >
                  {readerText(titleWithoutChapterNumber(lang === 'cn' ? chapter.title_cn : chapter.title_en))}
                </Link>
              </h3>
              <p>{renderProse(lang === 'cn' ? chapter.summary_cn : chapter.summary_en)}</p>
              <p>
                <span className="badge">{reportCountLabel(lang, chapter.report_ids.length)}</span>{' '}
                <span className="badge">{claimCountLabel(lang, chapter.claim_count)}</span>
              </p>
            </article>
          ))}
        </div>
      </section>

      {backbone ? (
        <section className="card section-enter" style={{ marginTop: '1rem' }}>
          <h2>{localizedText(lang, 'Parts of the book', '全书的几个部分')}</h2>
          <p className="lead">
            {localizedText(
              lang,
              `The ${chapterRows.length} chapters fall into ${backbone.acts.length} parts.`,
              `${chapterRows.length} 章分为 ${backbone.acts.length} 个部分。`,
            )}
          </p>
          <div className="grid grid-2">
            {backbone.acts.map((act) => (
              <article key={act.act_id} className="card">
                <h3>{readerText(lang === 'cn' ? act.title_cn : act.title_en)}</h3>
                <p>{renderProse(lang === 'cn' ? act.objective_cn : act.objective_en)}</p>
                <ul>
                  {act.chapter_ids.map((chapterId) => (
                    <li key={`act-${act.act_id}-${chapterId}`}>
                      <Link href={prefixPath(prefix, `/book/${chapterId}`)}>
                        {readerText(chapterTitleById.get(chapterId) ?? localizedText(lang, 'Chapter', '章节'))}
                      </Link>
                    </li>
                  ))}
                </ul>
              </article>
            ))}
          </div>
        </section>
      ) : null}

      <section className="card section-enter" style={{ marginTop: '1rem' }}>
        <h2>{localizedText(lang, 'Glossary', '术语表')}</h2>
        <p>
          {localizedText(
            lang,
            'Terms used across the chapters.',
            '各章共用的术语。',
          )}
        </p>
        <div className="grid grid-2">
          {glossaryPreview.map((term) => (
            <article key={term.term_id} className="card">
              <h3>{readerText(lang === 'cn' ? term.term_cn : term.term_en)}</h3>
              <p>{renderProse(lang === 'cn' ? term.definition_cn : term.definition_en)}</p>
              {renderGlossaryFormula(term.formula ?? '')}
            </article>
          ))}
        </div>
      </section>

      {claimCoverage ? (
        <section className="card section-enter" style={{ marginTop: '1rem' }}>
          <h2>{localizedText(lang, 'Claims in the chapters', '章节里的结论')}</h2>
          <p className="lead">{renderProse(lang === 'cn' ? claimCoverage.policy_cn : claimCoverage.policy_en)}</p>
          <p>
            <span className="badge">
              {localizedText(lang, 'Claims in all reports', '全部报告的结论')} {claimCoverage.global_claim_count}
            </span>{' '}
            <span className="badge">
              {localizedText(lang, 'Used in a chapter', '选入章节')} {claimCoverage.chapter_claim_count}
            </span>{' '}
            <span className="badge">
              {localizedText(lang, 'Only on report pages', '只在报告页上')} {claimCoverage.excluded_claim_count}
            </span>
          </p>
          {excludedByReport.length > 0 ? (
            <details>
              <summary>{localizedText(lang, 'Show the reports with claims not used in a chapter', '展开有结论未选入章节的报告')}</summary>
              <ul>
                {excludedByReport.map((row) => (
                  <li key={`excluded-${row.reportId}`}>
                    <Link href={prefixPath(prefix, `/reports/${row.reportId}`)}>{readerText(bookReportTitle(lang, row.reportId))}</Link>{' '}
                    <span className="muted">({claimCountLabel(lang, row.count)})</span>
                  </li>
                ))}
              </ul>
            </details>
          ) : null}
        </section>
      ) : null}
    </AppShell>
  );
}

function renderChapterNav(lang: Lang, prefix: string, chapter: BookChapter) {
  return (
    <div className="book-chapter-nav">
      {chapter.previous_chapter_id ? (
        <Link href={prefixPath(prefix, `/book/${chapter.previous_chapter_id}`)}>
          {localizedText(lang, '← Previous chapter', '← 上一章')}
        </Link>
      ) : (
        <span className="muted">{localizedText(lang, 'Start of book', '全书起点')}</span>
      )}
      <Link href={prefixPath(prefix, '/book')}>{localizedText(lang, 'Back to contents', '返回目录')}</Link>
      {chapter.next_chapter_id ? (
        <Link href={prefixPath(prefix, `/book/${chapter.next_chapter_id}`)}>
          {localizedText(lang, 'Next chapter →', '下一章 →')}
        </Link>
      ) : (
        <span className="muted">{localizedText(lang, 'Final chapter', '最后一章')}</span>
      )}
    </div>
  );
}

export function renderBookChapterPage(lang: Lang, prefix: string, chapterId: string) {
  const chapter = loadBookChapter(chapterId);
  const manifest = loadBookManifest();
  const glossary = loadGlossary();

  if (!chapter || !manifest) {
    return (
      <AppShell lang={lang} prefix={prefix}>
        <section className="card section-enter">
          <h1>{localizedText(lang, 'Chapter not found', '章节不存在')}</h1>
          <p>{chapterId}</p>
        </section>
      </AppShell>
    );
  }

  const chapterMeta = manifest.chapters.find((row) => row.chapter_id === chapterId);
  const chapterTerms = (glossary?.terms || [])
    .filter((term) => term.related_chapter_ids.includes(chapterId) && !isSiteGlossaryTerm(term))
    .slice(0, 10);
  const examples = chapterExamples(chapter, lang);
  const chapterPanels = readerPanels(chapter, lang);
  const visibleClaims = readerClaims(chapter, lang);
  const theoryGroups = groupTheoryChain(readerTheoryItems(chapter, lang));
  // A chapter marked as not yet written prints its one-line note, its reports
  // and their claims, and nothing that reads like finished chapter text.
  const written = chapterMeta?.written !== false;

  return (
    <AppShell lang={lang} prefix={prefix}>
      <section className="card section-enter">
        <div className="kicker">{readerText(chapterKicker(chapter, lang))}</div>
        <h1>{readerText(chapterTitle(chapter, lang))}</h1>
        <p className="lead">{renderProse(chapterSummary(chapter, lang))}</p>
        {chapterMeta ? (
          <p>
            <span className="badge">{reportCountLabel(lang, chapterMeta.report_ids.length)}</span>
            {chapterPanels.length > 0 ? (
              <>
                {' '}
                <span className="badge">{chartCountLabel(lang, chapterPanels.length)}</span>
              </>
            ) : null}
          </p>
        ) : null}
        {renderChapterNav(lang, prefix, chapter)}
      </section>

      {written ? (
        <section className="card section-enter book-prose" style={{ marginTop: '1rem' }}>
          <h2>{localizedText(lang, 'Chapter guide', '章节导读')}</h2>
          {chapterIntro(chapter, lang).map((paragraph) => (
            <p key={paragraph}>{renderProse(paragraph)}</p>
          ))}
        </section>
      ) : null}

      {written && examples.length > 0 ? (
        <section className="card section-enter book-prose chapter-storyline" style={{ marginTop: '1rem' }}>
          <h2>{localizedText(lang, "Examples from this chapter's reports", '本章报告中的例子')}</h2>
          {renderChapterExamples(lang, prefix, examples)}
        </section>
      ) : null}

      {written && chapter.concept_cards.length > 0 ? (
        <section className="card section-enter" style={{ marginTop: '1rem' }}>
          <h2>{localizedText(lang, 'Concept cards', '概念卡片')}</h2>
          <div className="grid grid-2">
            {chapter.concept_cards.map((card) => (
              <article key={card.id} className="card">
                <h3>{readerText(lang === 'cn' ? card.label_cn : card.label_en)}</h3>
                <p>{renderProse(lang === 'cn' ? card.description_cn : card.description_en)}</p>
                <p>
                  <span className="badge">{conceptReportCountLabel(lang, card.report_ids.length)}</span>
                </p>
              </article>
            ))}
          </div>
        </section>
      ) : null}

      {theoryGroups.length > 0 ? (
        <section className="card section-enter" style={{ marginTop: '1rem' }}>
          <h2>{localizedText(lang, 'Formulas used in this chapter', '本章用到的公式')}</h2>
          <div className="grid grid-2">
            {theoryGroups.map((group, idx) => renderTheoryGroupCard(lang, prefix, group, `${group.reportId}-${idx}`))}
          </div>
        </section>
      ) : null}

      {chapterPanels.length > 0 ? (
        <section className="card section-enter" style={{ marginTop: '1rem' }}>
          <h2>{chartSectionTitle(lang, chapterPanels.length)}</h2>
          <div style={{ display: 'grid', gap: '1rem' }}>
            {chapterPanels.map(({ panel, selectedDatasets }) => (
              <article key={panel.panel_id} className="card">
                <h3>
                  <Link href={prefixPath(prefix, `/reports/${panel.report_id}`)}>{readerText(bookReportTitle(lang, panel.report_id))}</Link>
                </h3>
                <ReportPlotPanel reportId={panel.report_id} datasets={selectedDatasets} lang={lang} />
              </article>
            ))}
          </div>
        </section>
      ) : null}

      <section className="card section-enter" style={{ marginTop: '1rem' }}>
        <h2>{localizedText(lang, 'Sources', '来源')}</h2>
        <p className="lead">{localizedText(lang, 'The reports this chapter draws on.', '本章用到的报告。')}</p>
        <details open={!written}>
          <summary>{localizedText(lang, 'Show the list', '展开列表')}</summary>
          <ul>
            {chapter.linked_reports.map((report) => (
              <li key={report.report_id}>
                <Link href={prefixPath(prefix, `/reports/${report.report_id}`)}>{readerText(bookReportTitle(lang, report.report_id))}</Link>
              </li>
            ))}
          </ul>
        </details>
      </section>

      {visibleClaims.length > 0 ? (
        <section className="card section-enter" style={{ marginTop: '1rem' }}>
          <h2>{localizedText(lang, 'Claims and sources', '结论与出处')}</h2>
          <div style={{ display: 'grid', gap: '0.8rem' }}>
            {visibleClaims.map((claim) => renderClaimCard(lang, prefix, claim, claim.claim_id))}
          </div>
        </section>
      ) : null}

      <section className="card section-enter" style={{ marginTop: '1rem' }}>
        {/* The chapter's one-line description is already printed under the title. */}
        {chapterTerms.length > 0 ? (
          <>
            <h2>{localizedText(lang, 'Terms in this chapter', '本章术语')}</h2>
            <details>
              <summary>{localizedText(lang, 'Show terms', '展开术语')}</summary>
              <ul>
                {chapterTerms.map((term) => (
                  <li key={term.term_id}>
                    <strong>{readerText(lang === 'cn' ? term.term_cn : term.term_en)}</strong>
                    {lang === 'cn' ? '：' : ': '}
                    {renderProse(lang === 'cn' ? term.definition_cn : term.definition_en)}
                  </li>
                ))}
              </ul>
            </details>
          </>
        ) : null}
        {renderChapterNav(lang, prefix, chapter)}
      </section>
    </AppShell>
  );
}

export function renderBookContinuousPage(lang: Lang, prefix: string) {
  const chapters = loadOrderedBookChapters();
  const manifest = loadBookManifest();
  if (!manifest || chapters.length === 0) {
    return (
      <AppShell lang={lang} prefix={prefix}>
        <section className="card section-enter">
          <h1>{localizedText(lang, 'Continuous book unavailable', '整本通读页面不可用')}</h1>
          <p>{localizedText(lang, 'Run reportctl book-data first.', '请先运行 reportctl book-data。')}</p>
        </section>
      </AppShell>
    );
  }

  return (
    <AppShell lang={lang} prefix={prefix}>
      <section id="book-continuous-top" className="card section-enter book-hero">
        <div className="kicker">{localizedText(lang, 'Continuous reading', '连续通读')}</div>
        <h1>{localizedText(lang, 'Valley-K Small: all chapters on one page', 'Valley-K Small：全部章节在一页')}</h1>
        <p className="lead">
          {localizedText(
            lang,
            `All ${chapters.length} chapters on one page, in order. Under each chapter, its formulas, interactive figures and claims can be opened in place.`,
            `${chapters.length} 章按顺序排在同一页上；每章下面可以就地展开这一章的公式、交互图和结论。`,
          )}
        </p>
        <div className="quick-nav continuous-progress">
          {chapters.map((chapter) => (
            <a key={`jump-${chapter.chapter_id}`} className="badge" href={`#${chapter.chapter_id}`}>
              {lang === 'cn' ? `第${chapter.order}章` : `Ch.${chapter.order}`}
            </a>
          ))}
        </div>
      </section>

      {chapters.map((chapter, idx) => {
        const examples = chapterExamples(chapter, lang);
        const chapterPanels = readerPanels(chapter, lang);
        const prevChapter = idx > 0 ? chapters[idx - 1] : null;
        const nextChapter = idx + 1 < chapters.length ? chapters[idx + 1] : null;
        const written = manifest.chapters.find((row) => row.chapter_id === chapter.chapter_id)?.written !== false;
        const visibleIntro = written ? chapterIntro(chapter, lang) : [];
        const visibleClaims = readerClaims(chapter, lang);
        const theoryItems = readerTheoryItems(chapter, lang);
        return (
          <section id={chapter.chapter_id} key={`continuous-${chapter.chapter_id}`} className="card section-enter" style={{ marginTop: '1rem' }}>
            <div className="kicker">{readerText(chapterKicker(chapter, lang))}</div>
            <h2>{readerText(chapterTitle(chapter, lang))}</h2>
            <p className="lead">{renderProse(chapterSummary(chapter, lang))}</p>
            <div className="book-prose">
              {visibleIntro.map((paragraph) => (
                <p key={`intro-${chapter.chapter_id}-${paragraph}`}>{renderProse(paragraph)}</p>
              ))}
            </div>
            {written && examples.length > 0 ? (
              <div className="book-prose chapter-storyline">
                <h3>{localizedText(lang, "Examples from this chapter's reports", '本章报告中的例子')}</h3>
                {renderChapterExamples(lang, prefix, examples)}
              </div>
            ) : null}

            {theoryItems.length > 0 ? (
              <details className="chapter-disclosure">
                <summary>
                  {localizedText(lang, 'Formulas used in this chapter', '本章用到的公式')} ({theoryItems.length})
                </summary>
                <div className="grid grid-2">
                  {groupTheoryChain(theoryItems).map((group, theoryIdx) =>
                    renderTheoryGroupCard(lang, prefix, group, `${chapter.chapter_id}-${group.reportId}-${theoryIdx}`),
                  )}
                </div>
              </details>
            ) : null}

            {chapterPanels.length > 0 ? (
              <LazyDisclosure
                className="chapter-disclosure"
                summary={
                  <>
                    {chapterPanels.length === 1
                      ? localizedText(lang, 'Open the interactive figure', '展开交互图')
                      : localizedText(lang, 'Open the interactive figures', '展开交互图')}{' '}
                    ({chapterPanels.length})
                  </>
                }
                placeholder={
                  <p className="muted" style={{ marginTop: '0.6rem' }}>
                    {localizedText(lang, 'The interactive figures load when this section is opened.', '展开后才加载交互图。')}
                  </p>
                }
              >
                <div style={{ display: 'grid', gap: '0.8rem' }}>
                  {chapterPanels.map(({ panel, selectedDatasets }) => (
                    <article key={`panel-${chapter.chapter_id}-${panel.panel_id}`} className="card">
                      <h4>
                        <Link href={prefixPath(prefix, `/reports/${panel.report_id}`)}>{readerText(bookReportTitle(lang, panel.report_id))}</Link>
                      </h4>
                      <ReportPlotPanel reportId={panel.report_id} datasets={selectedDatasets} lang={lang} />
                    </article>
                  ))}
                </div>
              </LazyDisclosure>
            ) : null}

            {visibleClaims.length > 0 ? (
              <details className="chapter-disclosure">
                <summary>
                  {localizedText(lang, 'Claims and sources', '结论与出处')} ({visibleClaims.length})
                </summary>
                <div className="grid grid-2">
                  {visibleClaims.map((claim) =>
                    renderClaimCard(lang, prefix, claim, `claim-${chapter.chapter_id}-${claim.claim_id}`),
                  )}
                </div>
              </details>
            ) : null}
            <div className="chapter-endcap">
              {prevChapter ? (
                <a href={`#${prevChapter.chapter_id}`}>{localizedText(lang, '← Previous chapter', '← 上一章')}</a>
              ) : (
                <span className="muted">{localizedText(lang, 'Start of book', '全书起点')}</span>
              )}
              <Link href={prefixPath(prefix, `/book/${chapter.chapter_id}`)}>
                {localizedText(lang, 'Open chapter page', '打开章节页')}
              </Link>
              {nextChapter ? (
                <a href={`#${nextChapter.chapter_id}`}>{localizedText(lang, 'Next chapter →', '下一章 →')}</a>
              ) : (
                <a href="#book-continuous-top">{localizedText(lang, 'Back to top', '返回顶部')}</a>
              )}
            </div>
          </section>
        );
      })}
    </AppShell>
  );
}
