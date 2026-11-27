import { displayTitle, isPlaceholderText, plainText } from '@/lib/atlas';
import { loadIndex, loadReportMeta } from '@/lib/content';
import { renderReportPage } from '@/lib/render-pages';

export function generateStaticParams() {
  return loadIndex().reports.map((item) => ({ reportId: item.report_id }));
}

export function generateMetadata({ params }: { params: { reportId: string } }) {
  const meta = loadReportMeta(params.reportId, 'en');
  const metaEn = loadReportMeta(params.reportId, 'en');
  const summary = meta?.summary ?? '';
  return {
    title: displayTitle('en', meta, metaEn, params.reportId),
    description: isPlaceholderText(summary) ? undefined : plainText(summary.replace(/\*\*/g, '')).slice(0, 220),
  };
}

export default function ReportPage({ params }: { params: { reportId: string } }) {
  return renderReportPage('en', '', params.reportId);
}
