import { manuscriptLinks } from '@/lib/atlas';
import { loadReportMeta, localizedText, withBasePath } from '@/lib/content';
import type { Lang } from '@/types';

export function PdfLinks({ lang, reportId }: { lang: Lang; reportId: string }) {
  const links = manuscriptLinks(reportId, loadReportMeta(reportId, 'en'), withBasePath);
  if (links.length === 0) {
    return null;
  }
  return (
    <>
      {links.map((link) => (
        <a key={link.lang} href={link.href} className="pdf-link">
          {link.lang === 'en' ? localizedText(lang, 'PDF (English)', 'PDF（英文）') : localizedText(lang, 'PDF (中文)', 'PDF（中文）')}
        </a>
      ))}
    </>
  );
}
