import { renderAboutPage } from '@/lib/render-pages';

export const metadata = { title: '关于' };

export default function CnAboutPage() {
  return renderAboutPage('cn', '/cn');
}
