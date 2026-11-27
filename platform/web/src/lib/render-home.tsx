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
  readerText,
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
          <p className="kicker">{readerText(localizedText(lang, 'Research atlas · first-passage times', '研究图谱 · 首达时间'))}</p>
          <h1>{readerText(localizedText(lang, 'How long until a random walker arrives?', '随机游走者要多久才到？'))}</h1>
          <p className="home-lede">
            {readerText(localizedText(
              lang,
              'A walker wanders on a lattice until it first reaches a target. The time this takes, the first-passage time, usually has a single most likely value. Add one directed shortcut, for instance, and the distribution can split: an early hump from walkers that found the shortcut, a late one from walkers that went the long way round, and a valley between.',
              '游走者在格点上随机行走，直到第一次碰到目标。这段时间叫首达时间，它的分布通常只有一个最可能的值。比如加上一条有向捷径，分布就可能一分为二：找到捷径的游走者形成早到的峰，绕远路的形成晚到的峰，中间隔着一道谷。',
            ))}
          </p>
          <p>
            {readerText(localizedText(
              lang,
              `Most of these ${written.length} reports work out, by exact numerical computation, often checked against Monte Carlo simulation, when that split appears, when it is a real second peak and when it is an artefact: first on rings, then on two-dimensional lattices, with two competing targets, and for pairs of walkers that react when they meet. Two are of another kind: a derivation of the ring formulas and a comparison of solver speed.`,
              `这 ${written.length} 份报告大多用精确的数值计算（不少还用蒙特卡洛模拟核对）回答：这种分裂什么时候出现，什么时候是真正的第二个峰，什么时候只是假象。先是环，然后是二维格点、两个相互竞争的目标，以及相遇即反应的两个游走者。另有两份性质不同：一份推导环模型的公式，一份比较求解器的速度。`,
            ))}
          </p>
          <p className="home-byline">
            {readerText(localizedText(
              lang,
              'Xiaoxiao Zhouyi · PhD research, University of Bristol · public since February 2026, in English and Chinese',
              '周易潇潇 · 布里斯托大学博士研究 · 2026 年 2 月起公开，中英双语',
            ))}
          </p>
        </div>
        <div className="home-hero-figure">
          <ArrivalCurve
            labels={{
              early: localizedText(lang, 'early: all via the shortcut', '早到：全部走了捷径'),
              late: localizedText(lang, 'late: mostly the long way round', '晚到：多数绕了远路'),
              axis: localizedText(lang, 'time t in steps, log scale', '时间 t（步），对数坐标'),
            }}
          />
          <p className="figure-caption">
            {readerText(localizedText(
              lang,
              'f(t) is the probability that the walker first reaches the target at step t, computed by numerically inverting the exact generating function. The walk is lazy, on a ring of N\u00a0=\u00a0100 sites: at each step it stays put with probability 1/3, otherwise it moves one or two sites either way (K\u00a0=\u00a04). The target is opposite the start; one directed shortcut runs from five sites along from the start to the site next to the target, and a walker at its source takes it with probability β/3 per step (β\u00a0=\u00a00.01). Peaks at t\u00a0=\u00a032 and t\u00a0=\u00a0495, valley at t\u00a0=\u00a084; the curve is drawn to t\u00a0=\u00a04000, by which time 96% of walkers have arrived. On a log time axis, area under the curve is not probability: the early hump holds under 1% of arrivals. Data behind Fig.\u00a01 of ',
              'f(t) 是游走者恰好在第 t 步首次到达目标的概率，由精确生成函数数值反演得到。模型是 N\u00a0=\u00a0100 个格点的环上的懒惰随机游走：每一步以 1/3 的概率原地不动，否则向左或向右走 1 格或 2 格（K\u00a0=\u00a04）。目标在起点正对面；一条有向捷径从起点往前第 5 个格点通到目标旁边的格点，游走者位于捷径起点时，每步以 β/3 的概率走捷径（β\u00a0=\u00a00.01）。两个峰在 t\u00a0=\u00a032 和 t\u00a0=\u00a0495，谷在 t\u00a0=\u00a084；曲线画到 t\u00a0=\u00a04000，此时已有 96% 的游走者到达。横轴是对数坐标，曲线下的面积不等于概率：早峰只占全部到达的不到 1%。数据取自报告《',
            ))}
            <Link href={prefixPath(prefix, `/reports/${figureReport}`)}>{readerText(titleOf(figureReport))}</Link>
            {readerText(localizedText(lang, '.', '》的图 1。'))}
          </p>
        </div>
      </section>

      <p className="home-paper">
        {readerText(localizedText(
          lang,
          'The line of work led to a single-author paper, “Geometry-controlled folds of first-passage-time bimodality under localized absorption”, submitted to Physical Review E in July 2026. It studies a related setting: under localized absorption, how the geometry decides whether a delayed second peak exists and where it disappears. Code and data to reproduce it: ',
          '这条研究线产出了一篇单作者论文《Geometry-controlled folds of first-passage-time bimodality under localized absorption》，2026 年 7 月投稿《物理评论 E》（Physical Review E）。论文研究的是相关但不同的设定：在局部吸收下，几何结构如何决定延迟到达的第二个峰是否存在、在哪里消失。复现代码与数据：',
        ))}
        <a href="https://github.com/zhouyi-xiaoxiao/delayed-first-passage-peak">delayed-first-passage-peak</a>
        {readerText(localizedText(lang, ' (v1.0.1).', '（v1.0.1）。'))}
      </p>

      <section className="home-section" aria-labelledby="start-here">
        <h2 id="start-here">{readerText(localizedText(lang, 'Start here', '从这里开始'))}</h2>
        <p className="home-section-note">{readerText(localizedText(lang, 'Three reports, in reading order.', '三份报告，按阅读顺序。'))}</p>
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
                <p className="start-family">{readerText(familyLabel(lang, reportFamily(row.report_id, row.group)))}</p>
                <h3>
                  <Link href={prefixPath(prefix, `/reports/${item.reportId}`)}>{readerText(titleOf(item.reportId))}</Link>
                </h3>
                <p>{readerText(lang === 'cn' ? item.cn : item.en)}</p>
                <p className="start-links">
                  <Link href={prefixPath(prefix, `/reports/${item.reportId}`)}>{readerText(localizedText(lang, 'Read online', '在线阅读'))}</Link>
                  <PdfLinks lang={lang} reportId={item.reportId} />
                </p>
              </li>
            );
          })}
        </ol>
      </section>

      <section className="home-section" id="talks" aria-labelledby="talks-heading">
        <h2 id="talks-heading">{readerText(localizedText(lang, 'Talks', '演讲'))}</h2>
        <p className="home-section-note">
          {readerText(localizedText(
            lang,
            'Web slide decks, bilingual. Arrow keys or the buttons move between slides.',
            '网页幻灯片，中英双语。用方向键或按钮翻页。',
          ))}
        </p>
        <div className="talk-list">
          {TALKS.map((talk) => (
            <article key={talk.id} className="talk-item">
              <h3>
                <Link href={prefixPath(prefix, `/talk/${talk.id}`)}>{readerText(lang === 'cn' ? talk.title[1] : talk.title[0])}</Link>
              </h3>
              <p>{readerText(lang === 'cn' ? talk.line[1] : talk.line[0])}</p>
              <p className="talk-when">{readerText(lang === 'cn' ? talk.when[1] : talk.when[0])}</p>
              <p className="start-links">
                <Link href={`/en/talk/${talk.id}`}>English</Link>
                <Link href={`/cn/talk/${talk.id}`}>中文</Link>
              </p>
            </article>
          ))}
        </div>
      </section>

      <section className="home-section" aria-labelledby="whole-atlas">
        <h2 id="whole-atlas">{readerText(localizedText(lang, 'The whole atlas', '全部内容'))}</h2>
        <p className="home-section-note">
          {readerText(localizedText(
            lang,
            `All ${written.length} written reports, by setting. Each has a page with its findings, figures and mathematics, and a PDF.`,
            `全部 ${written.length} 份已成文的报告，按模型分组。每份都有一页，列出结论、图和数学，并附 PDF。`,
          ))}
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
                  {readerText(familyLabel(lang, family))} <span className="count">{rows.length}</span>
                </h3>
                <ul>
                  {rows.map((row) => (
                    <li key={row.report_id}>
                      <Link href={prefixPath(prefix, `/reports/${row.report_id}`)}>{readerText(titleOf(row.report_id))}</Link>
                    </li>
                  ))}
                </ul>
              </div>
            );
          })}
        </div>
        <ul className="more-ways">
          <li>
            <Link href={prefixPath(prefix, '/reports')}>{readerText(localizedText(lang, 'All reports, with summaries', '全部报告与摘要'))}</Link>
            <span>{readerText(localizedText(lang, 'including work in progress', '包括进行中的工作'))}</span>
          </li>
          {chapterCount > 0 ? (
            <li>
              <Link href={prefixPath(prefix, '/book')}>{readerText(localizedText(lang, 'Read it as a book', '按书来读'))}</Link>
              <span>
                {readerText(localizedText(
                  lang,
                  `${chapterCount} chapters, starting from notation, each tied to the reports behind it`,
                  `${chapterCount} 章，从记号讲起，每章都连回背后的报告`,
                ))}
              </span>
            </li>
          ) : null}
          <li>
            <Link href={prefixPath(prefix, '/theory')}>{readerText(localizedText(lang, 'Theory', '理论'))}</Link>
            <span>{readerText(localizedText(lang, 'the notions and formulas the reports share', '各报告共用的概念与公式'))}</span>
          </li>
        </ul>
      </section>
    </AppShell>
  );
}
