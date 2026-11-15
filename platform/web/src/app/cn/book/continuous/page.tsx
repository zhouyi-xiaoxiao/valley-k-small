import { renderBookContinuousPage } from '@/lib/render-book-pages';

export const metadata = { title: '书 · 通读' };

export default function CnBookContinuousPage() {
  return renderBookContinuousPage('cn', '/cn');
}
