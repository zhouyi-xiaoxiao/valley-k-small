import { renderBookPage } from '@/lib/render-book-pages';

export const metadata = { title: 'Book' };

export default function EnBookIndexPage() {
  return renderBookPage('en', '/en');
}
