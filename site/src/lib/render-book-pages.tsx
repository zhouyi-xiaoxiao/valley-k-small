import Link from 'next/link';
import katex from 'katex';
import { AppShell } from '@/components/AppShell';
import { ReportPlotPanel } from '@/components/ReportPlotPanel';
import {
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

export function renderBookPage(lang: Lang, prefix: string) {
  const manifest = loadBookManifest();
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
                <span className="badge">{localizedText(lang, 'Reports', '关联报告')} {chapter.report_ids.length}</span>{' '}
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
        <h2>{localizedText(lang, 'Linked Reports', '关联报告')}</h2>
        <div className="grid grid-2">
          {chapter.linked_reports.map((report) => (
            <article key={report.report_id} className="card">
              <p className="badge">{report.group}</p>
              <h3>
                <Link href={prefixPath(prefix, `/reports/${report.report_id}`)}>
                  {lang === 'cn' ? report.title_cn : report.title_en}
                </Link>
              </h3>
              <p>{lang === 'cn' ? report.summary_cn : report.summary_en}</p>
              <p className="muted">{lang === 'cn' ? report.book_role_cn : report.book_role_en}</p>
            </article>
          ))}
        </div>
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
