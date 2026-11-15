import { renderAboutPage } from '@/lib/render-pages';

export const metadata = { title: 'About' };

export default function EnAboutPage() {
  return renderAboutPage('en', '/en');
}
