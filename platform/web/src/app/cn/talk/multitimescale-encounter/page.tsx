import { renderTalkPage } from '@/lib/render-talk-pages';

export const metadata = {
  title: '隐藏路径与真实双峰',
  description:
    '一个关于 first-passage 双峰、路径机制与 exact encounter 护栏的 valley-k-small 交互式演讲。',
};

export default function CnMultitimescaleEncounterTalkPage() {
  return renderTalkPage('cn', '/cn', 'multitimescale-encounter');
}
