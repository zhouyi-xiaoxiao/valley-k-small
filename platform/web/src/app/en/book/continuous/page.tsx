import { renderBookContinuousPage } from '@/lib/render-book-pages';

export const metadata = { title: 'Book, read through' };

export default function EnBookContinuousPage() {
  return renderBookContinuousPage('en', '/en');
}
