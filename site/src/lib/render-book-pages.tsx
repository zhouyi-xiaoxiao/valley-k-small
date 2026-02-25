import Link from 'next/link';
import katex from 'katex';
import { AppShell } from '@/components/AppShell';
import { ReportPlotPanel } from '@/components/ReportPlotPanel';
import {
  loadBookBackbone,
  loadBookChapter,
  loadBookManifest,
  loadGlossary,
  loadReportMeta,
  loadTranslationQC,
  localizedText,
  prefixPath,
} from '@/lib/content';
import type { BookChapter, Lang } from '@/types';

function escapeHtml(value: string): string {
  return value
    .replaceAll('&', '&amp;')
    .replaceAll('<', '&lt;')
    .replaceAll('>', '&gt;')
    .replaceAll('"', '&quot;')
    .replaceAll("'", '&#39;');
}

function renderLatex(latex: string): { html: string; error: string | null } {
  try {
    return {
      html: katex.renderToString(latex, { throwOnError: true, displayMode: true, strict: 'error' }),
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
              {term.formula ? <p><code>{term.formula}</code></p> : null}
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
  const chapterTerms = (glossary?.terms || []).filter((term) => term.related_chapter_ids.includes(chapterId)).slice(0, 10);

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
                {rendered.error ? (
                  <p className="muted" style={{ marginBottom: 0 }}>
                    {localizedText(lang, 'Formula fallback rendered as plain text.', '公式已回退为纯文本渲染。')}
                  </p>
                ) : null}
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
            return (
              <article key={panel.panel_id} className="card">
                <h3>{lang === 'cn' ? panel.title_cn : panel.title_en}</h3>
                <p>{lang === 'cn' ? panel.parameter_hint_cn : panel.parameter_hint_en}</p>
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
            'This page stitches all 8 chapters into one uninterrupted narrative from notation and assumptions to mechanism, evidence, and outlook.',
            '本页把 8 章串成一条不中断叙事，从符号与假设一直推进到机制、证据与展望。',
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
        const primaryPanel = chapter.interactive_panels[0];
        const primaryMeta = primaryPanel ? loadReportMeta(primaryPanel.report_id, lang) : null;
        const primaryDatasets = primaryPanel
          ? (primaryMeta?.datasets || []).filter((ds) => ds.series_id === primaryPanel.dataset_series_id)
          : [];
        const selectedDatasets = primaryPanel
          ? primaryDatasets.length > 0
            ? primaryDatasets
            : (primaryMeta?.datasets || []).slice(0, 1)
          : [];
        const prevChapter = idx > 0 ? chapters[idx - 1] : null;
        const nextChapter = idx + 1 < chapters.length ? chapters[idx + 1] : null;
        const visibleIntro = chapterIntro(chapter, lang).slice(0, 2);
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

            <details className="chapter-disclosure">
              <summary>{localizedText(lang, 'Open core derivation', '展开核心推导')}</summary>
              <div className="grid grid-2">
                {chapter.theory_chain.slice(0, 6).map((item, theoryIdx) => {
                  const rendered = renderLatex(item.latex);
                  return (
                    <article key={`${chapter.chapter_id}-${item.report_id}-${theoryIdx}`} className="card">
                      <p>
                        <span className="badge">{item.stage}</span>{' '}
                        <span className="badge">{item.report_id}</span>
                      </p>
                      <p>{lang === 'cn' ? item.description_cn : item.description_en}</p>
                      <div className="math-block" dangerouslySetInnerHTML={{ __html: rendered.html }} />
                    </article>
                  );
                })}
              </div>
            </details>

            <details className="chapter-disclosure">
              <summary>{localizedText(lang, 'Open interactive lab', '展开交互实验区')}</summary>
              {primaryPanel && selectedDatasets.length > 0 ? (
                <article className="card">
                  <h4>{lang === 'cn' ? primaryPanel.title_cn : primaryPanel.title_en}</h4>
                  <p>{lang === 'cn' ? primaryPanel.parameter_hint_cn : primaryPanel.parameter_hint_en}</p>
                  <ReportPlotPanel reportId={primaryPanel.report_id} datasets={selectedDatasets} lang={lang} />
                </article>
              ) : (
                <p className="muted">{localizedText(lang, 'No interactive panel available for this chapter.', '本章暂无可用交互图。')}</p>
              )}
            </details>

            <details className="chapter-disclosure">
              <summary>{localizedText(lang, 'Open claims and evidence', '展开 Claim 与证据')}</summary>
              <div className="grid grid-2">
                {chapter.claim_ledger.slice(0, 6).map((claim) => (
                  <article key={`claim-${chapter.chapter_id}-${claim.claim_id}`} className="card">
                    <p>
                      <span className="badge">{claim.stage}</span>{' '}
                      <span className="badge">{claim.claim_id}</span>
                    </p>
                    <p>{lang === 'cn' ? claim.text_cn : claim.text_en}</p>
                    <p className="muted">
                      {localizedText(lang, 'Evidence items', '证据项')} {claim.evidence.length}
                    </p>
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
