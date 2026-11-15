import { renderAtlasHome } from '@/lib/render-home';

export const metadata = {
  title: { absolute: 'Valley-K Small · 首达时间研究图谱' },
  description: '随机游走者到达目标所需的时间，什么时候会分成两个峰？关于带捷径格点上首达时间的中英双语报告、演讲与书。周易潇潇。',
};

export default function CnHomePage() {
  return renderAtlasHome('cn', '/cn');
}
