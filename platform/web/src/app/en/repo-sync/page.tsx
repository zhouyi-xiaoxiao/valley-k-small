import { renderRepoSyncPage } from '@/lib/render-pages';

export const metadata = { title: 'Repository sync' };

export default function EnRepoSyncPage() {
  return renderRepoSyncPage('en', '/en');
}
