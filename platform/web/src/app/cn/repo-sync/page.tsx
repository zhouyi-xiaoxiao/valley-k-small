import { renderRepoSyncPage } from '@/lib/render-pages';

export const metadata = { title: '仓库同步' };

export default function CnRepoSyncPage() {
  return renderRepoSyncPage('cn', '/cn');
}
