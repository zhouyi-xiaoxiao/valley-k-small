import { renderTalkPage } from '@/lib/render-talk-pages';

export const metadata = {
  title: 'Hidden routes in first-passage time',
  description: 'A 10-minute talk for SEMT PhD researchers (SEMT Ideas Exchange Day, University of Bristol, 15 April 2026) on hidden routes in random-walk first-passage-time distributions.',
};

export default function SmetTalkPage() {
  return renderTalkPage('en', '', 'smet-phd');
}
