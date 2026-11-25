import { renderTalkPage } from '@/lib/render-talk-pages';

export const metadata = {
  title: '隐藏路径与真实双峰',
  description:
    '十分钟交互式报告（网页幻灯 2026 年 5 月制作）：首达时间分布里的双峰什么时候算证据——环上捷径、二维格点，以及两个游走者相遇时间的精确核对。',
};

export default function CnMultitimescaleEncounterTalkPage() {
  return renderTalkPage('cn', '/cn', 'multitimescale-encounter');
}
