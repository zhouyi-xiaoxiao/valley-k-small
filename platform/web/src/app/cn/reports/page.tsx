import { renderReportsPage } from '@/lib/render-pages';

export const metadata = { title: '报告' };

export default function CnReportsPage() {
  return renderReportsPage('cn', '/cn');
}
