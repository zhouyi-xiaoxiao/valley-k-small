import { loadIndex } from '@/lib/content';
import { renderReportPage } from '@/lib/render-pages';

export function generateStaticParams() {
  return loadIndex().reports.map((item) => ({ reportId: item.report_id }));
}

export default function CnReportPage({ params }: { params: { reportId: string } }) {
  return renderReportPage('cn', '/cn', params.reportId);
}
