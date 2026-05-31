import { renderTalkPage } from '@/lib/render-talk-pages';

export const metadata = {
  title: '首达时间中的隐藏路径',
  description: '一个关于随机游走首达分布中隐藏路径机制的 10 分钟 SMET PhD 演讲。',
};

export default function CnSmetTalkPage() {
  return renderTalkPage('cn', '/cn', 'smet-phd');
}
