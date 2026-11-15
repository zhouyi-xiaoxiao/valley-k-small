import { renderBookPage } from '@/lib/render-book-pages';

export const metadata = { title: 'Book' };

export default function BookIndexPage() {
  return renderBookPage('en', '');
}
