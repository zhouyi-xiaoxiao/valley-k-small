import { renderAboutPage } from '@/lib/render-pages';

export const metadata = { title: 'About' };

export default function AboutPage() {
  return renderAboutPage('en', '');
}
