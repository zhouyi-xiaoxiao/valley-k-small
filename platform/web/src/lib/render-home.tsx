import Link from 'next/link';
import { AppShell } from '@/components/AppShell';
import { ArrivalCurve } from '@/components/ArrivalCurve';
import { PdfLinks } from '@/components/PdfLinks';
import {
  FAMILY_ORDER,
  START_HERE,
  TALKS,
  displayTitle,
  familyLabel,
  reportFamily,
  writtenReports,
} from '@/lib/atlas';
import { loadBookManifest, loadIndex, loadReportMeta, localizedText, prefixPath } from '@/lib/content';
import type { Lang } from '@/types';

export function renderAtlasHome(lang: Lang, prefix: string) {
  const index = loadIndex();
  const written = writtenReports(index);
  const book = loadBookManifest();
  const chapterCount = book?.chapter_count ?? 0;
  const titleOf = (reportId: string) =>
    displayTitle(lang, loadReportMeta(reportId, lang), loadReportMeta(reportId, 'en'), reportId);
  const figureReport = 'ring_lazy_jump_ext_rev2';

  return (
    <AppShell lang={lang} prefix={prefix}>
      <section className="home-hero">
        <div className="home-hero-text">
          <p className="kicker">{localizedText(lang, 'Research atlas · first-passage times', '研究图谱 · 首达时间')}</p>
          <h1>{localizedText(lang, 'How long until a random walker arrives?', '随机游走者要多久才到？')}</h1>
          <p className="home-lede">
            {localizedText(
              lang,
              'A walker wanders on a lattice until it first reaches a target. The time that takes, the first-passage time, usually has a single most likely value. Add one directed shortcut and the distribution can split: an early hump from walkers that found the shortcut, a late one from walkers that went the long way round, and a valley between.',
              '游走者在格点上随机行走，直到第一次碰到目标。这段时间叫首达时间，它的分布通常只有一个最可能的值。可只要加上一条有向捷径，分布就可能一分为二：找到捷径的游走者形成早到的峰，绕远路的形成晚到的峰，中间隔着一道谷。',
            )}
          </p>
          <p>
            {localizedText(
              lang,
              `These ${written.length} reports work out, by exact computation checked against simulation, when that split appears, when it is a real second peak and when it is an artefact: first on rings, then on two-dimensional lattices, with two competing targets, and for pairs of walkers that react when they meet.`,
              `这 ${written.length} 份报告用精确计算（并以模拟核对）回答：这种分裂什么时候出现，什么时候是真正的第二个峰，什么时候只是假象。先是环，然后是二维格点、两个相互竞争的目标，以及相遇即反应的两个游走者。`,
            )}
          </p>
          <p className="home-byline">
            {localizedText(
              lang,
              'Xiaoxiao Zhouyi · PhD research, University of Bristol · public since February 2026, in English and Chinese',
              '周易潇潇 · 布里斯托大学博士研究 · 2026 年 2 月起公开，中英双语',
            )}
          </p>
        </div>
        <div className="home-hero-figure">
          <ArrivalCurve
            labels={{
              early: localizedText(lang, 'early: mostly via the shortcut', '早到：多数走了捷径'),
              late: localizedText(lang, 'late: mostly the long way round', '晚到：多数绕了远路'),
              axis: localizedText(lang, 'time t, log scale', '时间 t，对数刻度'),
            }}
          />
          <p className="figure-caption">
            {localizedText(
              lang,
              'Exact first-passage-time distribution f(t) on a lazy ring of N = 100 sites with one directed shortcut (K = 4, β = 0.01): an early hump, a valley and a late hump. The curve is drawn to t = 1200. Drawn from the data behind Fig. 1 of ',
              '一个 N = 100 的懒惰环加一条有向捷径（K = 4，β = 0.01）上的精确首达时间分布 f(t)：早峰、谷、晚峰。曲线画到 t = 1200，取自报告《',
            )}
            <Link href={prefixPath(prefix, `/reports/${figureReport}`)}>{titleOf(figureReport)}</Link>
            {localizedText(lang, '.', '》的图 1。')}
          </p>
        </div>
      </section>

      <p className="home-paper">
        {localizedText(
          lang,
          'The line of work led to a single-author paper, “Geometry-controlled folds of first-passage-time bimodality under localized absorption”, submitted to Physical Review E in July 2026.',
          '这条研究线产出了一篇单作者论文《Geometry-controlled folds of first-passage-time bimodality under localized absorption》，2026 年 7 月投稿《物理评论 E》（Physical Review E）。',
        )}
      </p>

      <section className="home-section" aria-labelledby="start-here">
        <h2 id="start-here">{localizedText(lang, 'Start here', '从这里开始')}</h2>
        <p className="home-section-note">{localizedText(lang, 'Three reports, in reading order.', '三份报告，按阅读顺序。')}</p>
        <ol className="start-list">
          {START_HERE.map((item, i) => {
            const row = index.reports.find((r) => r.report_id === item.reportId);
            if (!row) {
              return null;
            }
            return (
              <li key={item.reportId} className="start-item">
                <span className="start-num" aria-hidden="true">
                  {i + 1}
                </span>
                <p className="start-family">{familyLabel(lang, reportFamily(row.report_id, row.group))}</p>
                <h3>
                  <Link href={prefixPath(prefix, `/reports/${item.reportId}`)}>{titleOf(item.reportId)}</Link>
                </h3>
                <p>{lang === 'cn' ? item.cn : item.en}</p>
                <p className="start-links">
                  <Link href={prefixPath(prefix, `/reports/${item.reportId}`)}>{localizedText(lang, 'Read online', '在线阅读')}</Link>
                  <PdfLinks lang={lang} reportId={item.reportId} />
                </p>
              </li>
            );
          })}
        </ol>
      </section>

      <section className="home-section" id="talks" aria-labelledby="talks-heading">
        <h2 id="talks-heading">{localizedText(lang, 'Talks', '演讲')}</h2>
        <p className="home-section-note">
          {localizedText(
            lang,
            'Web slide decks, bilingual. Arrow keys or the buttons move between slides.',
            '网页幻灯片，中英双语。用方向键或按钮翻页。',
          )}
        </p>
        <div className="talk-list">
          {TALKS.map((talk) => (
            <article key={talk.id} className="talk-item">
              <h3>
                <Link href={prefixPath(prefix, `/talk/${talk.id}`)}>{lang === 'cn' ? talk.title[1] : talk.title[0]}</Link>
              </h3>
              <p>{lang === 'cn' ? talk.line[1] : talk.line[0]}</p>
              <p className="talk-when">{lang === 'cn' ? talk.when[1] : talk.when[0]}</p>
              <p className="start-links">
                <Link href={`/en/talk/${talk.id}`}>English</Link>
                <Link href={`/cn/talk/${talk.id}`}>中文</Link>
              </p>
            </article>
          ))}
        </div>
      </section>

      <section className="home-section" aria-labelledby="whole-atlas">
        <h2 id="whole-atlas">{localizedText(lang, 'The whole atlas', '全部内容')}</h2>
        <p className="home-section-note">
          {localizedText(
            lang,
            `All ${written.length} written reports, by setting. Each has a page with its findings, figures and mathematics, and a PDF.`,
            `全部 ${written.length} 份已成文的报告，按模型分组。每份都有一页，列出结论、图和数学，并附 PDF。`,
          )}
        </p>
        <div className="family-columns">
          {FAMILY_ORDER.map((family) => {
            const rows = written.filter((row) => reportFamily(row.report_id, row.group) === family);
            if (rows.length === 0) {
              return null;
            }
            return (
              <div key={family} className="family-column">
                <h3>
                  {familyLabel(lang, family)} <span className="count">{rows.length}</span>
                </h3>
                <ul>
                  {rows.map((row) => (
                    <li key={row.report_id}>
                      <Link href={prefixPath(prefix, `/reports/${row.report_id}`)}>{titleOf(row.report_id)}</Link>
                    </li>
                  ))}
                </ul>
              </div>
            );
          })}
        </div>
        <ul className="more-ways">
          <li>
            <Link href={prefixPath(prefix, '/reports')}>{localizedText(lang, 'All reports, with summaries', '全部报告与摘要')}</Link>
            <span>{localizedText(lang, 'including work in progress', '包括进行中的工作')}</span>
          </li>
          {chapterCount > 0 ? (
            <li>
              <Link href={prefixPath(prefix, '/book')}>{localizedText(lang, 'Read it as a book', '按书来读')}</Link>
              <span>
                {localizedText(
                  lang,
                  `${chapterCount} chapters, from notation to open questions, each tied to the reports behind it`,
                  `${chapterCount} 章，从记号到开放问题，每章都连回背后的报告`,
                )}
              </span>
            </li>
          ) : null}
          <li>
            <Link href={prefixPath(prefix, '/theory')}>{localizedText(lang, 'Theory', '理论')}</Link>
            <span>{localizedText(lang, 'the notions and formulas the reports share', '各报告共用的概念与公式')}</span>
          </li>
        </ul>
      </section>
    </AppShell>
  );
}
