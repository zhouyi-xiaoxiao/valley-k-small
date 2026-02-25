import { loadIndex } from '@/lib/content';
import { renderReportPage } from '@/lib/render-pages';

export function generateStaticParams() {
  return loadIndex().reports.map((item) => ({ reportId: item.report_id }));
}

export default function ReportPage({ params }: { params: { reportId: string } }) {
  return renderReportPage('en', '', params.reportId);
}
