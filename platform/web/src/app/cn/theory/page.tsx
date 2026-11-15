import { renderTheoryPage } from '@/lib/render-pages';

export const metadata = { title: '理论' };

export default function CnTheoryPage() {
  return renderTheoryPage('cn', '/cn');
}
