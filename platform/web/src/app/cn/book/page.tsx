import { renderBookPage } from '@/lib/render-book-pages';

export const metadata = { title: '书' };

export default function CnBookIndexPage() {
  return renderBookPage('cn', '/cn');
}
