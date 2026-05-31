import { renderTalkPage } from '@/lib/render-talk-pages';

export const metadata = {
  title: 'Hidden Routes, Real Peaks',
  description:
    'An interactive valley-k-small talk on first-passage double peaks, route mechanisms, and exact encounter guardrails.',
};

export default function MultitimescaleEncounterTalkPage() {
  return renderTalkPage('en', '', 'multitimescale-encounter');
}
