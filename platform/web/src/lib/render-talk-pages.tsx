import { TalkDeck } from '@/components/TalkDeck';
import {
  loadBasicDemo,
  loadGatingDemo,
  loadRingDemo,
  loadSeriesPayload,
  loadTalkManifest,
  loadTalkScript,
  localizedText,
} from '@/lib/content';
import type { Lang } from '@/types';

export function renderTalkPage(lang: Lang, prefix: string, talkId: string) {
  const manifest = loadTalkManifest(talkId);
  const scriptEn = loadTalkScript(talkId, 'en');
  const scriptCn = loadTalkScript(talkId, 'cn');
  const basicDemo = loadBasicDemo(talkId);
  const ringDemo = loadRingDemo(talkId);
  const gatingDemo = loadGatingDemo(talkId);
  const ringScanProbability = loadSeriesPayload('ring_valley_dst', 'scan-probability-12');
  const ringScanTiming = loadSeriesPayload('ring_valley_dst', 'scan-metric');

  if (!manifest || !scriptEn || !scriptCn || !basicDemo || !ringDemo || !gatingDemo) {
    return (
      <main className="talk-deck-fallback">
        <section className="talk-fallback-card">
          <h1>{localizedText(lang, 'Talk data missing', '未找到 talk 数据')}</h1>
          <p>{talkId}</p>
        </section>
      </main>
    );
  }

  return (
    <TalkDeck
      lang={lang}
      manifest={manifest}
      scriptEn={scriptEn}
      scriptCn={scriptCn}
      basicDemo={basicDemo}
      ringDemo={ringDemo}
      gatingDemo={gatingDemo}
      ringScanProbability={ringScanProbability}
      ringScanTiming={ringScanTiming}
    />
  );
}
