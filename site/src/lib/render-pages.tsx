import Link from 'next/link';
import katex from 'katex';
import { AppShell } from '@/components/AppShell';
import { ReportPlotPanel } from '@/components/ReportPlotPanel';
import {
  groupReports,
  loadAgentManifest,
  loadBookManifest,
  loadContentMap,
  loadFigures,
  loadIndex,
  loadReportNetwork,
  loadReportMeta,
  loadTheoryMap,
  localizedText,
  prefixPath,
  withBasePath,
} from '@/lib/content';
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

function renderLatex(latex: string): LatexRenderResult {
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

function renderMathBlockCard(
  block: { context: string; lang: string; latex: string; source_path: string },
  key: string,
) {
  const rendered = renderLatex(block.latex);

  return (
    <article key={key} className="card">
      <p>
        <span className="badge">{block.context}</span> <span className="badge">{block.lang.toUpperCase()}</span>
      </p>
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
    return `${clipped.slice(0, stop + 1).trim()}…`;
  }
  return `${clipped.trim()}…`;
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
  if (normalizedSummary.length < 18) {
    return true;
  }
  return false;
}

function pruneSectionCards(cards: Array<{ heading: string; summary: string; source_path: string }>) {
  const seen = new Set<string>();
  return cards.filter((card) => {
    if (isPlaceholderCardSummary(card.heading, card.summary)) {
      return false;
    }
    const key = `${card.heading.toLowerCase()}::${card.summary.toLowerCase()}`;
    if (seen.has(key)) {
      return false;
    }
    seen.add(key);
    return true;
  });
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
  if (!mapping) {
    return null;
  }
  const primary = manifest.chapters.find((row) => row.chapter_id === mapping.primary_chapter_id);
  if (!primary) {
    return null;
  }
  return {
    chapterId: primary.chapter_id,
    chapterTitle: lang === 'cn' ? primary.title_cn : primary.title_en,
    previousChapterId: primary.previous_chapter_id,
    nextChapterId: primary.next_chapter_id,
    chapterIds: mapping.chapter_ids,
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

export function renderHomePage(lang: Lang, prefix: string) {
  const index = loadIndex();
  const grouped = groupReports(index);
  const groups = Object.keys(grouped).sort();
  const network = loadReportNetwork();
  const contentMap = loadContentMap();

  return (
    <AppShell lang={lang} prefix={prefix}>
      <section className="card section-enter">
        <div className="kicker">Research Network</div>
        <h1>{localizedText(lang, 'Valley-K Small Interactive Atlas', 'Valley-K Small 交互研究总览')}</h1>
        <p>
          {lang === 'cn'
            ? `面向 ${index.reports.length} 份报告的在线界面，提供广覆盖中英文内容、交互图形、数学原理说明和机器可读同步产物。`
            : `A full online interface for ${index.reports.length} reports with broad CN/EN coverage, interactive figures, mathematical context, and machine-readable synchronization outputs.`}
        </p>
        <p>
          <Link href={prefixPath(prefix, '/book')} className="badge">
            {localizedText(lang, 'Start Book Mainline', '进入书籍主线')}
          </Link>
        </p>
        <div className="grid grid-3">
          <div className="card">
            <h3>{index.reports.length}</h3>
            <p>{localizedText(lang, 'Registered reports', '已注册报告')}</p>
          </div>
          <div className="card">
            <h3>{groups.length}</h3>
            <p>{localizedText(lang, 'Research groups', '研究分组')}</p>
          </div>
          <div className="card">
            <h3>{formatTimestamp(lang, index.generated_at)}</h3>
            <p>{localizedText(lang, 'Data generated', '数据生成时间')}</p>
          </div>
        </div>
      </section>

      <section className="card section-enter" style={{ marginTop: '1rem' }}>
        <h2>{localizedText(lang, 'Topic Map', '主题地图')}</h2>
        <div className="grid grid-3">
          {groups.map((group) => (
            <article key={group} className="card">
              <h3>{group}</h3>
              <ul>
                {grouped[group].slice(0, 5).map((item) => (
                  <li key={item.report_id}>
                    <Link href={prefixPath(prefix, `/reports/${item.report_id}`)}>{item.report_id}</Link>
                  </li>
                ))}
              </ul>
            </article>
          ))}
        </div>
      </section>

      <section className="card section-enter" style={{ marginTop: '1rem' }}>
        <h2>{localizedText(lang, 'Research Storyline', '研究主线串联')}</h2>
        <p className="lead">
          {localizedText(
            lang,
            'Reports are connected as one chain: foundations, mechanism extensions, and cross-report synthesis.',
            '报告不是孤立页面，而是同一条研究链：基础模型、机制扩展、跨报告综合。',
          )}
        </p>
        <div className="grid grid-3">
          {network.group_paths.map((pathRow) => (
            <article key={pathRow.group} className="card">
              <h3>{pathRow.group}</h3>
              <ol>
                {pathRow.report_ids.map((rid) => (
                  <li key={`${pathRow.group}-${rid}`}>
                    <Link href={prefixPath(prefix, `/reports/${rid}`)}>{lookupReportTitle(rid, lang, network)}</Link>
                  </li>
                ))}
              </ol>
            </article>
          ))}
        </div>
      </section>

      <section className="card section-enter" style={{ marginTop: '1rem' }}>
        <h2>{localizedText(lang, 'Narrative Arcs', '叙事弧线')}</h2>
        <p className="lead">
          {localizedText(
            lang,
            'Each arc links concrete claims to evidence, so readers can verify the story step by step.',
            '每条弧线都把具体 claim 对应到证据，方便逐步核对。',
          )}
        </p>
        <div className="grid grid-2">
          {contentMap.arcs.slice(0, 4).map((arc) => (
            <article key={arc.arc_id} className="card">
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
            </article>
          ))}
        </div>
      </section>
    </AppShell>
  );
}

export function renderReportsPage(lang: Lang, prefix: string) {
  const index = loadIndex();
  const network = loadReportNetwork();
  const bookManifest = loadBookManifest();
  const enriched = index.reports.map((item) => {
    const meta = loadReportMeta(item.report_id, lang);
    const preview = extractReportPreview(meta, item.report_id, lang);
    const mapping = bookManifest?.report_chapter_map?.[item.report_id];
    return { item, preview, mapping };
  });

  return (
    <AppShell lang={lang} prefix={prefix}>
      <section className="card section-enter">
        <div className="kicker">Catalog</div>
        <h1>{localizedText(lang, 'All Reports', '全部报告')}</h1>
        <p className="lead">
          {localizedText(
            lang,
            'Browse by concise previews first. Enter a report only when the topic matches your current question.',
            '先看每份报告的简短预览，再进入与你当前问题最相关的报告详情页。',
          )}
        </p>
        <details style={{ marginTop: '0.8rem' }}>
          <summary>{localizedText(lang, 'Open cross-report storyline', '展开跨报告主线')}</summary>
          <div className="grid grid-3" style={{ marginTop: '0.8rem' }}>
            {network.group_paths.map((pathRow) => (
              <article key={`path-${pathRow.group}`} className="card">
                <h3>{pathRow.group}</h3>
                <ol>
                  {pathRow.report_ids.map((rid) => (
                    <li key={`path-${pathRow.group}-${rid}`}>
                      <Link href={prefixPath(prefix, `/reports/${rid}`)}>{lookupReportTitle(rid, lang, network)}</Link>
                    </li>
                  ))}
                </ol>
              </article>
            ))}
          </div>
        </details>
        <div className="grid grid-2">
          {enriched.map(({ item, preview, mapping }) => (
            <article key={item.report_id} className="card">
              <p style={{ marginBottom: '0.35rem' }}>
                <span className="badge">{item.group}</span>
                {mapping?.primary_chapter_id ? (
                  <>
                    {' '}
                    <span className="badge">
                      {localizedText(lang, 'Book', '书籍')}:{' '}
                      <Link href={prefixPath(prefix, `/book/${mapping.primary_chapter_id}`)}>{mapping.primary_chapter_id}</Link>
                    </span>
                  </>
                ) : null}
              </p>
              <h3>
                <Link href={prefixPath(prefix, `/reports/${item.report_id}`)}>{preview.title}</Link>
              </h3>
              <p className="muted">{item.report_id}</p>
              <p>{preview.summary}</p>
              <p>
                {localizedText(lang, 'Languages', '语言')}: {item.languages.join(', ')}
              </p>
              <p>
                {localizedText(lang, 'Updated', '更新')}: {formatTimestamp(lang, item.updated_at)}
              </p>
              <p style={{ marginBottom: 0 }}>
                <Link href={prefixPath(prefix, `/reports/${item.report_id}`)}>
                  {localizedText(lang, 'Read this report', '进入阅读')}
                </Link>
              </p>
            </article>
          ))}
        </div>
      </section>
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
  const filteredSections = pruneSectionCards(meta.section_cards);
  const sectionsPreview = filteredSections.slice(0, 6);
  const sectionsExtra = filteredSections.slice(6);
  const navItems = [
    { id: 'book-position', label: localizedText(lang, 'Book Position', '书籍定位') },
    { id: 'reading-path', label: localizedText(lang, 'Reading Path', '阅读路径') },
    { id: 'connected-reports', label: localizedText(lang, 'Connected Reports', '关联报告链') },
    { id: 'narrative-arcs', label: localizedText(lang, 'Narrative Arc Position', '叙事弧线定位') },
    { id: 'verifiable-claims', label: localizedText(lang, 'Verifiable Claims', '可核对 Claim') },
    { id: 'interactive', label: localizedText(lang, 'Interactive Figures', '交互图形') },
    { id: 'math-chain', label: localizedText(lang, 'Mathematical Logic', '数学逻辑') },
    { id: 'math-principles', label: localizedText(lang, 'Formula Library', '公式库') },
    { id: 'narrative-sections', label: localizedText(lang, 'Narrative Notes', '叙事笔记') },
    { id: 'appendix-assets', label: localizedText(lang, 'Appendix & Assets', '附录与资源') },
  ];

  return (
    <AppShell lang={lang} prefix={prefix}>
      <section className="card section-enter">
        <div className="kicker">{meta.report_id}</div>
        <h1>{meta.title}</h1>
        <p className="lead">{meta.summary}</p>
        <div className="quick-nav">
          {navItems.map((item) => (
            <a key={item.id} className="badge" href={`#${item.id}`}>
              {item.label}
            </a>
          ))}
        </div>
        <p>
          <span className="badge">
            {localizedText(lang, 'Updated', '更新')}: {formatTimestamp(lang, meta.updated_at)}
          </span>
        </p>
        <div className="grid grid-3">
          <article className="card">
            <h3>{localizedText(lang, 'Model', '模型')}</h3>
            <p>{meta.narrative.model_overview}</p>
          </article>
          <article className="card">
            <h3>{localizedText(lang, 'Method', '方法')}</h3>
            <p>{meta.narrative.method_overview}</p>
          </article>
          <article className="card">
            <h3>{localizedText(lang, 'Result', '结论')}</h3>
            <p>{meta.narrative.result_overview}</p>
          </article>
        </div>
      </section>

      <section id="book-position" className="card section-enter" style={{ marginTop: '1rem' }}>
        <h3>{localizedText(lang, 'Book Position', '书籍定位')}</h3>
        {bookPlacement ? (
          <>
            <p className="lead">
              {localizedText(
                lang,
                'This report is part of the chapterized mainline. Use chapter links to keep continuity instead of reading reports in isolation.',
                '该报告已纳入章节化主线。建议通过章节链接保持连续阅读，而不是把报告孤立阅读。',
              )}
            </p>
            <p>
              <span className="badge">{localizedText(lang, 'Primary chapter', '主章节')}</span>{' '}
              <Link href={prefixPath(prefix, `/book/${bookPlacement.chapterId}`)}>{bookPlacement.chapterTitle}</Link>
            </p>
            <p>
              <span className="badge">{localizedText(lang, 'Also appears in', '同时出现于')}</span>{' '}
              {bookPlacement.chapterIds.map((chapterId) => (
                <Link key={`${reportId}-${chapterId}`} href={prefixPath(prefix, `/book/${chapterId}`)} style={{ marginRight: '0.45rem' }}>
                  {chapterId}
                </Link>
              ))}
            </p>
            <p>
              {bookPlacement.previousChapterId ? (
                <Link href={prefixPath(prefix, `/book/${bookPlacement.previousChapterId}`)}>
                  {localizedText(lang, '← Previous chapter', '← 上一章')}
                </Link>
              ) : null}
              {'  '}
              {bookPlacement.nextChapterId ? (
                <Link href={prefixPath(prefix, `/book/${bookPlacement.nextChapterId}`)}>
                  {localizedText(lang, 'Next chapter →', '下一章 →')}
                </Link>
              ) : null}
            </p>
          </>
        ) : (
          <p>{localizedText(lang, 'No chapter mapping found yet.', '尚未生成章节映射。')}</p>
        )}
      </section>

      <section id="reading-path" className="card section-enter" style={{ marginTop: '1rem' }}>
        <h3>{localizedText(lang, 'Reading Path', '阅读路径')}</h3>
        <ol>
          <li>
            {localizedText(
              lang,
              'Scan key findings first to decide whether this report is relevant.',
              '先看关键结论，确认这份报告是否与你当前问题匹配。',
            )}
          </li>
          <li>
            {localizedText(
              lang,
              'Use the interactive panel to test parameter and shape sensitivity.',
              '进入交互图面板，快速验证参数与形状敏感性。',
            )}
          </li>
          <li>
            {localizedText(
              lang,
              'Then read the mathematical chain and formula library for derivation details.',
              '再阅读数学逻辑链与公式库，把结论连到推导细节。',
            )}
          </li>
        </ol>
        <h3>{localizedText(lang, 'Key Findings', '关键结论')}</h3>
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
        <h3>{localizedText(lang, 'Narrative Arc Position', '叙事弧线定位')}</h3>
        <p className="lead">
          {localizedText(
            lang,
            'This report appears in one or more global arcs. Use these checkpoints to keep reading continuity across pages.',
            '该报告处于一个或多个全局叙事弧线中，可按检查点保持跨页面阅读连续性。',
          )}
        </p>
        {arcsForReport.length > 0 ? (
          <div className="grid grid-2">
            {arcsForReport.map((arc) => (
              <article key={`arc-placement-${arc.arc_id}`} className="card">
                <h4>{lang === 'cn' ? arc.label_cn : arc.label_en}</h4>
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
                  <summary>{localizedText(lang, 'Open arc sequence', '展开弧线序列')}</summary>
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
          <p>{localizedText(lang, 'No narrative arc placement found.', '未找到叙事弧线定位信息。')}</p>
        )}
      </section>

      <section id="verifiable-claims" className="card section-enter" style={{ marginTop: '1rem' }}>
        <h3>{localizedText(lang, 'Verifiable Claims', '可核对 Claim')}</h3>
        <p className="lead">
          {localizedText(
            lang,
            'Claims below are tied to explicit evidence paths so each statement can be audited.',
            '下列 claim 都绑定了证据路径，便于逐条审计核对。',
          )}
        </p>
        {guide ? (
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
                        <p>
                          <span className="badge">{claim.stage}</span> <span className="badge">{claim.claim_id}</span>
                        </p>
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

      <div id="interactive" style={{ marginTop: '1rem' }}>
        <ReportPlotPanel reportId={reportId} datasets={meta.datasets} lang={lang} />
      </div>

      <section id="math-chain" className="card section-enter" style={{ marginTop: '1rem' }}>
        <h3>{localizedText(lang, 'Mathematical Logic Chain', '数学逻辑链')}</h3>
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
                <p style={{ marginBottom: 0 }}>
                  <span className="badge">{item.context}</span>
                </p>
              </article>
            );
          })}
        </div>
      </section>

      <section id="math-principles" className="card section-enter" style={{ marginTop: '1rem' }}>
        <h3>{localizedText(lang, 'Mathematical Principles', '数学原理')}</h3>
        <p>
          {localizedText(lang, 'Showing', '当前展示')} {Math.min(6, meta.math_blocks.length)} / {meta.math_blocks.length}
        </p>
        <div className="grid grid-2">
          {meta.math_blocks.slice(0, 6).map((block, idx) => renderMathBlockCard(block, `${block.source_path}-${idx}`))}
        </div>
        {meta.math_blocks.length > 6 ? (
          <details style={{ marginTop: '0.8rem' }}>
            <summary>{localizedText(lang, 'Show remaining formulas', '展开剩余公式')}</summary>
            <div className="grid grid-2" style={{ marginTop: '0.8rem' }}>
              {meta.math_blocks
                .slice(6)
                .map((block, idx) => renderMathBlockCard(block, `extra-${block.source_path}-${idx}`))}
            </div>
          </details>
        ) : null}
      </section>

      <section id="narrative-sections" className="card section-enter" style={{ marginTop: '1rem' }}>
        <h3>{localizedText(lang, 'Narrative Sections', '叙事章节')}</h3>
        <p className="muted">
          {localizedText(
            lang,
            'Cleaned chapter summaries are shown first; low-value placeholders are hidden.',
            '优先展示清洗后的章节摘要，低信息量占位段落已隐藏。',
          )}
        </p>
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

      <section className="card section-enter" style={{ marginTop: '1rem' }}>
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
        <h3>{localizedText(lang, 'Download Assets', '下载资源')}</h3>
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

      <section className="card section-enter" style={{ marginTop: '1rem' }}>
        <h3>{localizedText(lang, 'Figure Gallery', '图形预览')}</h3>
        <p>
          {localizedText(lang, 'Showing', '当前展示')} {Math.min(12, figures.length)} / {figures.length}
        </p>
        <div className="grid grid-3">
          {figures.slice(0, 12).map((fig) => (
            <article key={fig.id} className="card">
              <p>{fig.title}</p>
              {isImageFigure(fig.web_path) ? (
                <a href={withBasePath(fig.web_path)} target="_blank" rel="noreferrer">
                  {/* eslint-disable-next-line @next/next/no-img-element */}
                  <img
                    src={withBasePath(fig.web_path)}
                    alt={fig.title}
                    style={{ width: '100%', borderRadius: '10px', border: '1px solid #d8ccb3' }}
                  />
                </a>
              ) : null}
              <a href={withBasePath(fig.web_path)} target="_blank" rel="noreferrer">
                {localizedText(lang, 'Open Figure', '打开图件')}
              </a>
            </article>
          ))}
        </div>
        {figures.length > 12 ? (
          <details style={{ marginTop: '0.8rem' }}>
            <summary>{localizedText(lang, 'Show remaining figures', '展开剩余图形')}</summary>
            <div className="grid grid-3" style={{ marginTop: '0.8rem' }}>
              {figures.slice(12).map((fig) => (
                <article key={`extra-${fig.id}`} className="card">
                  <p>{fig.title}</p>
                  {isImageFigure(fig.web_path) ? (
                    <a href={withBasePath(fig.web_path)} target="_blank" rel="noreferrer">
                      {/* eslint-disable-next-line @next/next/no-img-element */}
                      <img
                        src={withBasePath(fig.web_path)}
                        alt={fig.title}
                        style={{ width: '100%', borderRadius: '10px', border: '1px solid #d8ccb3' }}
                      />
                    </a>
                  ) : null}
                  <a href={withBasePath(fig.web_path)} target="_blank" rel="noreferrer">
                    {localizedText(lang, 'Open Figure', '打开图件')}
                  </a>
                </article>
              ))}
            </div>
          </details>
        ) : null}
      </section>
    </AppShell>
  );
}

export function renderTheoryPage(lang: Lang, prefix: string) {
  const map = loadTheoryMap();
  const network = loadReportNetwork();
  const contentMap = loadContentMap();
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
      </section>

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
                  <details style={{ marginTop: '0.35rem' }}>
                    <summary>{localizedText(lang, 'Raw JSON (advanced)', '原始 JSON（高级）')}</summary>
                    <pre style={{ whiteSpace: 'pre-wrap', margin: '0.45rem 0 0' }}>
                      {JSON.stringify(check.details, null, 2)}
                    </pre>
                  </details>
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

export function renderAboutPage(lang: Lang, prefix: string) {
  return (
    <AppShell lang={lang} prefix={prefix}>
      <section className="card section-enter">
        <div className="kicker">Reproducibility</div>
        <h1>{localizedText(lang, 'Build & Validation', '构建与校验')}</h1>
        <p>
          {localizedText(
            lang,
            'The web layer is generated from existing report assets through Python scripts and validated by JSON schema + CI checks.',
            '网页层通过 Python 脚本从现有报告资产生成，并通过 JSON schema 与 CI 检查校验。',
          )}
        </p>
        <ul>
          <li>
            <code>python3 scripts/reportctl.py web-data</code>
          </li>
          <li>
            <code>python3 scripts/reportctl.py book-data</code>
          </li>
          <li>
            <code>python3 scripts/reportctl.py translation-qc</code>
          </li>
          <li>
            <code>python3 scripts/reportctl.py agent-sync</code>
          </li>
          <li>
            <code>python3 scripts/reportctl.py content-iterate --rounds 3 --mode full</code>
          </li>
          <li>
            <code>python3 scripts/validate_web_data.py</code>
          </li>
          <li>
            <code>cd site && npm run build</code>
          </li>
          <li>
            <code>python3 scripts/reportctl.py deliverables --mode full</code>
          </li>
        </ul>
      </section>
    </AppShell>
  );
}
