import { renderReportsPage } from '@/lib/render-pages';

export const metadata = { title: 'Reports' };

export default function EnReportsPage() {
  return renderReportsPage('en', '/en');
}
