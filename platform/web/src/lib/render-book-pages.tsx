import Link from 'next/link';
import katex from 'katex';
import { AppShell } from '@/components/AppShell';
import { LazyDisclosure } from '@/components/LazyDisclosure';
import { ReportPlotPanel } from '@/components/ReportPlotPanel';
import {
  loadBookBackbone,
  loadBookClaimCoverage,
  loadBookChapter,
  loadBookManifest,
  loadGlossary,
  loadReportMeta,
  loadTranslationQC,
  localizedText,
  prefixPath,
} from '@/lib/content';
import { KATEX_MACROS } from '@/lib/latex';
import type { BookChapter, Lang } from '@/types';

function escapeHtml(value: string): string {
  return value
    .replaceAll('&', '&amp;')
    .replaceAll('<', '&lt;')
    .replaceAll('>', '&gt;')
    .replaceAll('"', '&quot;')
    .replaceAll("'", '&#39;');
}

function renderLatex(latex: string, displayMode = true): { html: string; error: string | null } {
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

function renderMathFallbackNotice(lang: Lang, reason: string) {
  return (
    <details className="math-error-note">
      <summary>{localizedText(lang, 'Formula fallback details', '公式回退详情')}</summary>
      <p className="muted" style={{ marginTop: '0.4rem' }}>
        {localizedText(
          lang,
          'KaTeX parsing failed, so this formula is rendered as escaped plain text for audit continuity.',
          'KaTeX 解析失败，当前公式已回退为转义纯文本以保证可核查连续性。',
        )}
      </p>
      <code>{reason}</code>
    </details>
  );
}

function renderGlossaryFormula(latex: string, lang: Lang) {
  const rendered = renderLatex(latex, false);
  return (
    <>
      <div
        className="math-inline"
        dangerouslySetInnerHTML={{
          __html: rendered.html,
        }}
      />
      {rendered.error ? renderMathFallbackNotice(lang, rendered.error) : null}
    </>
  );
}

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

function shortLine(text: string, max = 260): string {
  const value = String(text || '').replace(/\s+/g, ' ').trim();
  if (value.length <= max) {
    return value;
  }
  const clipped = value.slice(0, max + 1);
  const stop = Math.max(clipped.lastIndexOf('. '), clipped.lastIndexOf('。'), clipped.lastIndexOf('; '), clipped.lastIndexOf('；'));
  const end = stop > Math.floor(max * 0.55) ? stop + 1 : max;
  return `${clipped.slice(0, end).trimEnd()}…`;
}

function chapterStoryline(chapter: BookChapter, lang: Lang, transitionHint?: string): string[] {
  const pickByStage = (stage: 'model' | 'method' | 'result' | 'finding') =>
    chapter.claim_ledger.find((row) => row.stage === stage) || null;
  const model = pickByStage('model');
  const method = pickByStage('method');
  const result = pickByStage('result');
  const finding = pickByStage('finding');

  const lines: string[] = [];
  const modelText = model ? (lang === 'cn' ? model.text_cn : model.text_en) : '';
  const methodText = method ? (lang === 'cn' ? method.text_cn : method.text_en) : '';
  const resultText = result ? (lang === 'cn' ? result.text_cn : result.text_en) : '';
  const findingText = finding ? (lang === 'cn' ? finding.text_cn : finding.text_en) : '';

  if (modelText) {
    lines.push(
      lang === 'cn'
        ? `本章首先固定模型前提：${shortLine(modelText, 170)}`
        : `We begin by fixing the model premise: ${shortLine(modelText, 220)}`,
    );
  }
  if (methodText) {
    lines.push(
      lang === 'cn'
        ? `随后给出可复核的方法链路：${shortLine(methodText, 170)}`
        : `We then move to an auditable method chain: ${shortLine(methodText, 220)}`,
    );
  }
  if (resultText || findingText) {
    const merged = [resultText, findingText].filter(Boolean).join(' ');
    lines.push(
      lang === 'cn'
        ? `在统一判据下得到的结果与发现是：${shortLine(merged, 190)}`
        : `Under the same diagnostic criterion, the chapter-level result and finding are: ${shortLine(merged, 240)}`,
    );
  }
  if (transitionHint) {
    lines.push(shortLine(transitionHint, lang === 'cn' ? 170 : 210));
  }
  return lines.slice(0, 4);
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
  const translationQc = loadTranslationQC();

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
  const glossaryPreview = (glossary?.terms || []).slice(0, 8);

  return (
    <AppShell lang={lang} prefix={prefix}>
      <section className="card section-enter book-hero">
        <div className="kicker">{localizedText(lang, 'Book Mainline', '书籍主线')}</div>
        <h1>{localizedText(lang, 'Valley-K Small Research Book', 'Valley-K Small 研究电子书')}</h1>
        <p className="lead">
          {localizedText(
            lang,
            'Read from Chapter 0 to Chapter 7 as one continuous theory-and-evidence narrative. Each chapter is linked to interactive figures and auditable claims.',
            '按第0章到第7章连续阅读，将理论链、交互证据与可审计 claim 融为同一条主线。',
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
        <div className="grid grid-3">
          <article className="card">
            <h3>{manifest.chapter_count}</h3>
            <p>{localizedText(lang, 'Book chapters', '章节数')}</p>
          </article>
          <article className="card">
            <h3>{Object.keys(manifest.report_chapter_map || {}).length}</h3>
            <p>{localizedText(lang, 'Mapped reports', '映射报告数')}</p>
          </article>
          <article className="card">
            <h3>{translationQc?.passed ? localizedText(lang, 'PASS', '通过') : localizedText(lang, 'CHECK', '待检查')}</h3>
            <p>{localizedText(lang, 'Translation gate', '双语门禁')}</p>
          </article>
        </div>
      </section>

      {backbone ? (
        <section className="card section-enter" style={{ marginTop: '1rem' }}>
          <h2>{localizedText(lang, 'Backbone System', '主干系统')}</h2>
          <p className="lead">
            {localizedText(
              lang,
              'This system extracts a canonical logic spine so we can iterate details without losing narrative continuity.',
              '该系统会先抽取规范化逻辑主干，再在不破坏连续性的前提下迭代细节内容。',
            )}
          </p>
          <div className="grid grid-2">
            {backbone.acts.map((act) => (
              <article key={act.act_id} className="card">
                <h3>{lang === 'cn' ? act.title_cn : act.title_en}</h3>
                <p>{lang === 'cn' ? act.objective_cn : act.objective_en}</p>
                <p className="muted">
                  {localizedText(lang, 'Chapters', '章节')}: {act.chapter_ids.join(', ')}
                </p>
              </article>
            ))}
          </div>
        </section>
      ) : null}

      {claimCoverage ? (
        <section className="card section-enter" style={{ marginTop: '1rem' }}>
          <h2>{localizedText(lang, 'Claim Coverage Policy', 'Claim 覆盖策略')}</h2>
          <p className="lead">{lang === 'cn' ? claimCoverage.policy_cn : claimCoverage.policy_en}</p>
          <p>
            <span className="badge">
              {localizedText(lang, 'Global claims', '全局 claim')} {claimCoverage.global_claim_count}
            </span>{' '}
            <span className="badge">
              {localizedText(lang, 'In chapters', '主线已纳入')} {claimCoverage.chapter_claim_count}
            </span>{' '}
            {typeof claimCoverage.chapter_native_claim_count === 'number' ? (
              <>
                <span className="badge">
                  {localizedText(lang, 'Chapter-native synthesis claims', '章节新增综合 claim')}{' '}
                  {claimCoverage.chapter_native_claim_count}
                </span>{' '}
              </>
            ) : null}
            <span className="badge">
              {localizedText(lang, 'Excluded from mainline', '主线外留存')} {claimCoverage.excluded_claim_count}
            </span>
          </p>
          <details>
            <summary>{localizedText(lang, 'Open excluded claim IDs', '展开主线外 claim ID')}</summary>
            <p className="muted" style={{ marginTop: '0.4rem' }}>
              {localizedText(
                lang,
                'Excluded claims are still available in report pages and content_map for deep audit.',
                '主线外 claim 仍保留在报告页与 content_map，便于深度核验。',
              )}
            </p>
            <div className="table-wrap">
              <table className="theory-table">
                <thead>
                  <tr>
                    <th>{localizedText(lang, 'Claim ID', 'Claim ID')}</th>
                  </tr>
                </thead>
                <tbody>
                  {claimCoverage.excluded_claim_ids.map((claimId) => (
                    <tr key={`excluded-${claimId}`}>
                      <td>
                        <code>{claimId}</code>
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          </details>
        </section>
      ) : null}

      <section className="card section-enter" style={{ marginTop: '1rem' }}>
        <h2>{localizedText(lang, 'Table of Contents', '目录')}</h2>
        <div className="book-toc-grid">
          {chapterRows.map((chapter) => (
            <article key={chapter.chapter_id} className="card book-chapter-card">
              <p className="badge">{localizedText(lang, 'Chapter', '章节')} {chapter.order}</p>
              <h3>
                <Link href={prefixPath(prefix, `/book/${chapter.chapter_id}`)}>
                  {lang === 'cn' ? chapter.title_cn : chapter.title_en}
                </Link>
              </h3>
              <p>{lang === 'cn' ? chapter.summary_cn : chapter.summary_en}</p>
              <p>
                <span className="badge">{localizedText(lang, 'Evidence nodes', '证据节点')} {chapter.report_ids.length}</span>{' '}
                <span className="badge">{localizedText(lang, 'Claims', 'Claim 数')} {chapter.claim_count}</span>
              </p>
            </article>
          ))}
        </div>
      </section>

      <section className="card section-enter" style={{ marginTop: '1rem' }}>
        <h2>{localizedText(lang, 'Glossary Lock Table', '术语锁表')}</h2>
        <p>
          {localizedText(
            lang,
            'Terms are double-written in EN/CN and reused across all chapters to keep notation stable.',
            '术语采用中英双写并在全章节复用，以保证符号与叙事的一致性。',
          )}
        </p>
        <div className="grid grid-2">
          {glossaryPreview.map((term) => (
            <article key={term.term_id} className="card">
              <h3>{lang === 'cn' ? term.term_cn : term.term_en}</h3>
              <p>{lang === 'cn' ? term.definition_cn : term.definition_en}</p>
              {term.formula ? renderGlossaryFormula(term.formula, lang) : null}
            </article>
          ))}
        </div>
      </section>
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
      <Link href={prefixPath(prefix, '/book')}>{localizedText(lang, 'Back to TOC', '返回目录')}</Link>
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
  const backbone = loadBookBackbone();

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
  const spine = backbone?.chapter_spine.find((row) => row.chapter_id === chapter.chapter_id);
  const chapterTerms = (glossary?.terms || []).filter((term) => term.related_chapter_ids.includes(chapterId)).slice(0, 10);
  const storyline = chapterStoryline(chapter, lang, lang === 'cn' ? spine?.transition_to_next_cn : spine?.transition_to_next_en);

  return (
    <AppShell lang={lang} prefix={prefix}>
      <section className="card section-enter">
        <div className="kicker">{chapterKicker(chapter, lang)}</div>
        <h1>{chapterTitle(chapter, lang)}</h1>
        <p className="lead">{chapterSummary(chapter, lang)}</p>
        {chapterMeta ? (
          <p>
            <span className="badge">{localizedText(lang, 'Read time', '阅读时长')} {chapterMeta.estimated_read_minutes} min</span>{' '}
            <span className="badge">{localizedText(lang, 'Reports', '关联报告')} {chapterMeta.report_ids.length}</span>{' '}
            <span className="badge">{localizedText(lang, 'Interactive panels', '交互图段')} {chapterMeta.interactive_count}</span>
          </p>
        ) : null}
        {renderChapterNav(lang, prefix, chapter)}
      </section>

      <section className="card section-enter book-prose" style={{ marginTop: '1rem' }}>
        <h2>{localizedText(lang, 'Chapter Guide', '章节导读')}</h2>
        {chapterIntro(chapter, lang).map((paragraph) => (
          <p key={paragraph}>{paragraph}</p>
        ))}
      </section>

      <section className="card section-enter book-prose chapter-storyline" style={{ marginTop: '1rem' }}>
        <h2>{localizedText(lang, 'Narrative Walkthrough', '叙事主线')}</h2>
        {storyline.map((paragraph) => (
          <p key={`storyline-${paragraph}`}>{paragraph}</p>
        ))}
      </section>

      <section className="card section-enter" style={{ marginTop: '1rem' }}>
        <h2>{localizedText(lang, 'Concept Cards', '概念卡片')}</h2>
        <div className="grid grid-2">
          {chapter.concept_cards.map((card) => (
            <article key={card.id} className="card">
              <h3>{lang === 'cn' ? card.label_cn : card.label_en}</h3>
              <p>{lang === 'cn' ? card.description_cn : card.description_en}</p>
              <p>
                <span className="badge">{localizedText(lang, 'Reports', '关联报告')} {card.report_ids.length}</span>
              </p>
            </article>
          ))}
        </div>
      </section>

      <section className="card section-enter" style={{ marginTop: '1rem' }}>
        <h2>{localizedText(lang, 'Theory Chain', '理论链')}</h2>
        <div className="grid grid-2">
          {chapter.theory_chain.map((item, idx) => {
            const rendered = renderLatex(item.latex);
            return (
              <article key={`${item.report_id}-${item.stage}-${idx}`} className="card">
                <p>
                  <span className="badge">{item.stage}</span>{' '}
                  <span className="badge">{item.report_id}</span>
                </p>
                <h3>{lang === 'cn' ? item.label_cn : item.label_en}</h3>
                <p>{lang === 'cn' ? item.description_cn : item.description_en}</p>
                <div
                  className="math-block"
                  dangerouslySetInnerHTML={{
                    __html: rendered.html,
                  }}
                />
                {rendered.error ? renderMathFallbackNotice(lang, rendered.error) : null}
              </article>
            );
          })}
        </div>
      </section>

      <section className="card section-enter" style={{ marginTop: '1rem' }}>
        <h2>{localizedText(lang, 'Interactive Evidence Panel', '交互证据面板')}</h2>
        <div style={{ display: 'grid', gap: '1rem' }}>
          {chapter.interactive_panels.map((panel) => {
            const meta = loadReportMeta(panel.report_id, lang);
            const datasets = (meta?.datasets || []).filter((ds) => ds.series_id === panel.dataset_series_id);
            const selectedDatasets = datasets.length > 0 ? datasets : (meta?.datasets || []).slice(0, 1);
            const fallbackDatasetId =
              datasets.length === 0 && selectedDatasets.length > 0 ? selectedDatasets[0].series_id : null;
            return (
              <article key={panel.panel_id} className="card">
                <h3>{lang === 'cn' ? panel.title_cn : panel.title_en}</h3>
                <p>{lang === 'cn' ? panel.parameter_hint_cn : panel.parameter_hint_en}</p>
                {fallbackDatasetId ? (
                  <p className="muted">
                    {localizedText(
                      lang,
                      `Audit notice: configured dataset ${panel.dataset_series_id} is missing; fallback to ${fallbackDatasetId}.`,
                      `审计提示：配置数据集 ${panel.dataset_series_id} 缺失，已回退到 ${fallbackDatasetId}。`,
                    )}
                  </p>
                ) : null}
                {selectedDatasets.length > 0 ? (
                  <ReportPlotPanel reportId={panel.report_id} datasets={selectedDatasets} lang={lang} />
                ) : (
                  <p className="muted">{localizedText(lang, 'Dataset unavailable in payload.', '当前数据包中未找到该数据集。')}</p>
                )}
              </article>
            );
          })}
        </div>
      </section>

      <section className="card section-enter" style={{ marginTop: '1rem' }}>
        <h2>{localizedText(lang, 'Evidence Trail', '证据链路')}</h2>
        <p className="lead">
          {localizedText(
            lang,
            'This chapter is presented as one coherent story. The underlying report artifacts are preserved as auditable evidence nodes.',
            '本章按统一叙事组织；底层报告仅作为可核对的证据节点保留。',
          )}
        </p>
        <details>
          <summary>{localizedText(lang, 'Open evidence-node index', '展开证据节点索引')}</summary>
          <ul>
            {chapter.linked_reports.map((report) => (
              <li key={report.report_id}>
                <Link href={prefixPath(prefix, `/reports/${report.report_id}`)}>
                  {lang === 'cn' ? report.title_cn : report.title_en}
                </Link>{' '}
                <span className="muted">({lang === 'cn' ? report.book_role_cn : report.book_role_en})</span>
              </li>
            ))}
          </ul>
        </details>
      </section>

      <section className="card section-enter" style={{ marginTop: '1rem' }}>
        <h2>{localizedText(lang, 'Claim Ledger', 'Claim 台账')}</h2>
        <div style={{ display: 'grid', gap: '0.8rem' }}>
          {chapter.claim_ledger.map((claim) => (
            <article key={claim.claim_id} className="card">
              <p>
                <span className="badge">{claim.stage}</span>{' '}
                <span className="badge">{claim.claim_id}</span>{' '}
                <span className="badge">{claim.report_id}</span>
              </p>
              <p>{lang === 'cn' ? claim.text_cn : claim.text_en}</p>
              <details>
                <summary>{localizedText(lang, 'Open evidence links', '展开证据链接')}</summary>
                <ul>
                  {claim.evidence.map((ev) => (
                    <li key={`${claim.claim_id}-${ev.path}`}>
                      <code>{ev.evidence_type}</code> <code>{ev.path}</code>
                      <p>{lang === 'cn' ? ev.snippet_cn : ev.snippet_en}</p>
                    </li>
                  ))}
                </ul>
              </details>
            </article>
          ))}
        </div>
      </section>

      <section className="card section-enter" style={{ marginTop: '1rem' }}>
        <h2>{localizedText(lang, 'Chapter Summary', '章节总结')}</h2>
        <p>{chapterSummary(chapter, lang)}</p>
        {chapterTerms.length > 0 ? (
          <details>
            <summary>{localizedText(lang, 'Open chapter glossary links', '展开章节术语链接')}</summary>
            <ul>
              {chapterTerms.map((term) => (
                <li key={term.term_id}>
                  <strong>{lang === 'cn' ? term.term_cn : term.term_en}</strong>: {lang === 'cn' ? term.definition_cn : term.definition_en}
                </li>
              ))}
            </ul>
          </details>
        ) : null}
        {renderChapterNav(lang, prefix, chapter)}
      </section>
    </AppShell>
  );
}

export function renderBookContinuousPage(lang: Lang, prefix: string) {
  const chapters = loadOrderedBookChapters();
  const backbone = loadBookBackbone();
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
        <div className="kicker">{localizedText(lang, 'Continuous Reading', '连续通读')}</div>
        <h1>{localizedText(lang, 'Valley-K Small: Full Storyline Edition', 'Valley-K Small：完整叙事版')}</h1>
        <p className="lead">
          {localizedText(
            lang,
            'This page stitches all 8 chapters into one full storyline from notation and assumptions to mechanism, evidence, and outlook, with expandable derivations and claim ledgers in each chapter block.',
            '本页将 8 章串成一条完整主线：从符号与假设推进到机制、证据与展望；每章均可展开推导链与 Claim 证据账本。',
          )}
        </p>
        <div className="quick-nav continuous-progress">
          {chapters.map((chapter) => (
            <a key={`jump-${chapter.chapter_id}`} className="badge" href={`#${chapter.chapter_id}`}>
              {localizedText(lang, 'Ch.', '第')}{chapter.order}
            </a>
          ))}
        </div>
      </section>

      {chapters.map((chapter, idx) => {
        const spineRow = backbone?.chapter_spine.find((row) => row.chapter_id === chapter.chapter_id);
        const storyline = chapterStoryline(chapter, lang, lang === 'cn' ? spineRow?.transition_to_next_cn : spineRow?.transition_to_next_en);
        const chapterPanels = chapter.interactive_panels.map((panel) => {
          const panelMeta = loadReportMeta(panel.report_id, lang);
          const panelDatasets = (panelMeta?.datasets || []).filter((ds) => ds.series_id === panel.dataset_series_id);
          const selectedDatasets = panelDatasets.length > 0 ? panelDatasets : (panelMeta?.datasets || []).slice(0, 1);
          const fallbackDatasetId =
            panelDatasets.length === 0 && selectedDatasets.length > 0 ? selectedDatasets[0].series_id : null;
          return { panel, selectedDatasets, fallbackDatasetId };
        });
        const prevChapter = idx > 0 ? chapters[idx - 1] : null;
        const nextChapter = idx + 1 < chapters.length ? chapters[idx + 1] : null;
        const visibleIntro = chapterIntro(chapter, lang);
        return (
          <section id={chapter.chapter_id} key={`continuous-${chapter.chapter_id}`} className="card section-enter" style={{ marginTop: '1rem' }}>
            <div className="kicker">{chapterKicker(chapter, lang)}</div>
            <p>
              <span className="badge">
                {localizedText(lang, 'Chapter', '章节')} {idx + 1}/{chapters.length}
              </span>{' '}
              <span className="badge">{chapter.chapter_id}</span>
            </p>
            <h2>{chapterTitle(chapter, lang)}</h2>
            <p className="lead">{chapterSummary(chapter, lang)}</p>
            {spineRow ? (
              <p className="muted">
                {lang === 'cn' ? spineRow.core_question_cn : spineRow.core_question_en}
              </p>
            ) : null}
            <div className="book-prose">
              {visibleIntro.map((paragraph) => (
                <p key={`intro-${chapter.chapter_id}-${paragraph}`}>{paragraph}</p>
              ))}
            </div>
            <div className="book-prose chapter-storyline">
              <h3>{localizedText(lang, 'Storyline in this chapter', '本章主线')}</h3>
              {storyline.map((paragraph) => (
                <p key={`storyline-continuous-${chapter.chapter_id}-${paragraph}`}>{paragraph}</p>
              ))}
            </div>

            <details className="chapter-disclosure">
              <summary>
                {localizedText(lang, 'Open core derivation', '展开核心推导')} ({chapter.theory_chain.length})
              </summary>
              <div className="grid grid-2">
                {chapter.theory_chain.map((item, theoryIdx) => {
                  const rendered = renderLatex(item.latex);
                  return (
                    <article key={`${chapter.chapter_id}-${item.report_id}-${theoryIdx}`} className="card">
                      <p>
                        <span className="badge">{item.stage}</span>{' '}
                        <span className="badge">{item.report_id}</span>
                      </p>
                      <p>{lang === 'cn' ? item.description_cn : item.description_en}</p>
                      <div className="math-block" dangerouslySetInnerHTML={{ __html: rendered.html }} />
                      {rendered.error ? renderMathFallbackNotice(lang, rendered.error) : null}
                    </article>
                  );
                })}
              </div>
            </details>

            <LazyDisclosure
              className="chapter-disclosure"
              summary={
                <>
                  {localizedText(lang, 'Open interactive lab', '展开交互实验区')} ({chapter.interactive_panels.length})
                </>
              }
              placeholder={
                <p className="muted" style={{ marginTop: '0.6rem' }}>
                  {localizedText(
                    lang,
                    'Interactive plots are mounted on demand when this panel opens, so continuous reading stays responsive.',
                    '交互图会在展开后按需挂载，以保证整本通读页面保持流畅。',
                  )}
                </p>
              }
            >
              {chapterPanels.length > 0 ? (
                <div style={{ display: 'grid', gap: '0.8rem' }}>
                  {chapterPanels.map(({ panel, selectedDatasets, fallbackDatasetId }) => (
                    <article key={`panel-${chapter.chapter_id}-${panel.panel_id}`} className="card">
                      <h4>{lang === 'cn' ? panel.title_cn : panel.title_en}</h4>
                      <p>{lang === 'cn' ? panel.parameter_hint_cn : panel.parameter_hint_en}</p>
                      {fallbackDatasetId ? (
                        <p className="muted">
                          {localizedText(
                            lang,
                            `Audit notice: configured dataset ${panel.dataset_series_id} is missing; fallback to ${fallbackDatasetId}.`,
                            `审计提示：配置数据集 ${panel.dataset_series_id} 缺失，已回退到 ${fallbackDatasetId}。`,
                          )}
                        </p>
                      ) : null}
                      {selectedDatasets.length > 0 ? (
                        <ReportPlotPanel reportId={panel.report_id} datasets={selectedDatasets} lang={lang} />
                      ) : (
                        <p className="muted">{localizedText(lang, 'Dataset unavailable in payload.', '当前数据包中未找到该数据集。')}</p>
                      )}
                    </article>
                  ))}
                </div>
              ) : (
                <p className="muted">{localizedText(lang, 'No interactive panel available for this chapter.', '本章暂无可用交互图。')}</p>
              )}
            </LazyDisclosure>

            <details className="chapter-disclosure">
              <summary>
                {localizedText(lang, 'Open claims and evidence', '展开 Claim 与证据')} ({chapter.claim_ledger.length})
              </summary>
              <div className="grid grid-2">
                {chapter.claim_ledger.map((claim) => (
                  <article key={`claim-${chapter.chapter_id}-${claim.claim_id}`} className="card">
                    <p>
                      <span className="badge">{claim.stage}</span>{' '}
                      <span className="badge">{claim.claim_id}</span>
                    </p>
                    <p>{lang === 'cn' ? claim.text_cn : claim.text_en}</p>
                    <p className="muted">
                      {localizedText(lang, 'Evidence items', '证据项')} {claim.evidence.length}
                    </p>
                    <ul>
                      {claim.evidence.slice(0, 2).map((ev) => (
                        <li key={`ev-${claim.claim_id}-${ev.path}`}>
                          <code>{ev.evidence_type}</code> <code>{ev.path}</code>
                        </li>
                      ))}
                    </ul>
                  </article>
                ))}
              </div>
            </details>
            {spineRow ? (
              <p className="muted chapter-transition-note">
                {lang === 'cn' ? spineRow.transition_to_next_cn : spineRow.transition_to_next_en}
              </p>
            ) : null}
            <div className="chapter-endcap">
              {prevChapter ? (
                <a href={`#${prevChapter.chapter_id}`}>{localizedText(lang, '← Previous chapter', '← 上一章')}</a>
              ) : (
                <span className="muted">{localizedText(lang, 'Book start', '全书起点')}</span>
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
