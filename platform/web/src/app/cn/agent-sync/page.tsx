import { renderAgentSyncPage } from '@/lib/render-pages';

export const metadata = { title: 'Agent sync' };

export default function CnAgentSyncPage() {
  return renderAgentSyncPage('cn', '/cn');
}
