import { renderTheoryPage } from '@/lib/render-pages';

export const metadata = { title: 'Theory' };

export default function EnTheoryPage() {
  return renderTheoryPage('en', '/en');
}
