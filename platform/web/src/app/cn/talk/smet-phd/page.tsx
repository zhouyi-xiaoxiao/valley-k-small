import { renderTalkRedirect } from '@/lib/render-talk-pages';

export const metadata = {
  title: '首达时间中的隐藏路径',
  description: '10 分钟研究报告（布里斯托大学 SEMT Ideas Exchange Week，2026 年 4 月 15 日，面向 SEMT 各方向博士生）：随机游走首达时间分布中的隐藏路径。',
};

export default function CnSmetTalkPage() {
  return renderTalkRedirect('cn', '/cn');
}
