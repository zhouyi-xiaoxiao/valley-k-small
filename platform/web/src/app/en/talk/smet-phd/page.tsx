import { renderTalkRedirect } from '@/lib/render-talk-pages';

export const metadata = {
  title: 'Hidden routes in first-passage time',
  description: 'A 10-minute talk for PhD researchers of the School of Engineering Mathematics and Technology (SEMT), University of Bristol, at its Ideas Exchange Week (15 April 2026), on hidden routes in random-walk first-passage-time distributions.',
};

export default function EnSmetTalkPage() {
  return renderTalkRedirect('en', '/en');
}
