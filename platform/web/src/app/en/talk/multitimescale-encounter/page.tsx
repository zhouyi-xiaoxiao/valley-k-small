import { renderTalkPage } from '@/lib/render-talk-pages';

export const metadata = {
  title: 'Hidden Routes, Real Peaks',
  description:
    'An interactive 10-minute talk (web slides prepared in May 2026) on when a double peak in a first-passage-time distribution counts as evidence: ring shortcuts, 2D lattices and exact two-walker encounter checks.',
};

export default function EnMultitimescaleEncounterTalkPage() {
  return renderTalkPage('en', '/en', 'multitimescale-encounter');
}
