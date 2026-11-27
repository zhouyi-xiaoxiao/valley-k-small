import { TalkRevealDeck } from '@/components/TalkRevealDeck';
import {
  loadBasicDemo,
  loadTalkManifest,
  loadTalkScript,
  localizedText,
} from '@/lib/content';
import { withBasePath } from '@/lib/url';
import type { Lang } from '@/types';

export function renderTalkPage(lang: Lang, prefix: string, talkId: string) {
  const manifest = loadTalkManifest(talkId);
  const scriptEn = loadTalkScript(talkId, 'en');
  const scriptCn = loadTalkScript(talkId, 'cn');
  const basicDemo = loadBasicDemo(talkId);

  if (!manifest || !scriptEn || !scriptCn || !basicDemo) {
    return (
      <main className="talk-deck-fallback">
        <section className="talk-fallback-card">
          <h1>{localizedText(lang, 'Talk data missing', '未找到演讲数据')}</h1>
          <p>{talkId}</p>
        </section>
      </main>
    );
  }

  return (
    <TalkRevealDeck
      lang={lang}
      prefix={prefix}
      manifest={manifest}
      scriptEn={scriptEn}
      scriptCn={scriptCn}
      basicDemo={basicDemo}
    />
  );
}

/** /talk/ has no page of its own: the list of talks is a section of the home page. */
export function renderTalkIndexRedirect(lang: Lang, prefix: string) {
  const home = withBasePath(`${prefix}/`);
  const destination = `${home}#talks`;
  return (
    <main className="talk-deck-fallback">
      <meta httpEquiv="refresh" content={`0; url=${destination}`} />
      <link rel="canonical" href={home} />
      <section className="talk-fallback-card">
        <h1>{localizedText(lang, 'Talks', '演讲')}</h1>
        <p>
          <a href={destination}>
            {localizedText(lang, 'See the list of talks.', '查看演讲列表。')}
          </a>
        </p>
      </section>
    </main>
  );
}

export function renderTalkRedirect(lang: Lang, prefix: string) {
  const destination = withBasePath(`${prefix}/talk/semt-phd/`);
  return (
    <main className="talk-deck-fallback">
      <meta httpEquiv="refresh" content={`0; url=${destination}`} />
      <link rel="canonical" href={destination} />
      <section className="talk-fallback-card">
        <h1>{localizedText(lang, 'This talk has moved', '演讲页面已迁移')}</h1>
        <p>
          <a href={destination}>
            {localizedText(lang, 'Open the SEMT talk page.', '打开 SEMT 演讲页面。')}
          </a>
        </p>
      </section>
    </main>
  );
}
