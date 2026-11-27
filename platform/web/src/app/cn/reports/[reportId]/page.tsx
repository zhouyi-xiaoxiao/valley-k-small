import { displayTitle, isPlaceholderText, plainText } from '@/lib/atlas';
import { loadIndex, loadReportMeta } from '@/lib/content';
import { renderReportPage } from '@/lib/render-pages';

export function generateStaticParams() {
  return loadIndex().reports.map((item) => ({ reportId: item.report_id }));
}

export function generateMetadata({ params }: { params: { reportId: string } }) {
  const meta = loadReportMeta(params.reportId, 'cn');
  const metaEn = loadReportMeta(params.reportId, 'en');
  const summary = meta?.summary ?? '';
  return {
    title: displayTitle('cn', meta, metaEn, params.reportId),
    description: isPlaceholderText(summary) ? undefined : plainText(summary.replace(/\*\*/g, '')).slice(0, 220),
  };
}

export default function CnReportPage({ params }: { params: { reportId: string } }) {
  return renderReportPage('cn', '/cn', params.reportId);
}
