import { renderTalkPage } from '@/lib/render-talk-pages';

export const metadata = {
  title: 'Hidden Routes in First-Passage Time',
  description: 'A 10-minute SMET PhD talk on hidden pathways in random-walk first-passage distributions.',
};

export default function EnSmetTalkPage() {
  return renderTalkPage('en', '/en', 'smet-phd');
}
