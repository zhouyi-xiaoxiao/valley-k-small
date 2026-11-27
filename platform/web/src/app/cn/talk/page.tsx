import { renderTalkIndexRedirect } from '@/lib/render-talk-pages';

export const metadata = {
  title: '演讲',
  description: '研究图谱里列出的演讲。',
};

export default function CnTalkIndexPage() {
  return renderTalkIndexRedirect('cn', '/cn');
}
