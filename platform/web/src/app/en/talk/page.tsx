import { renderTalkIndexRedirect } from '@/lib/render-talk-pages';

export const metadata = {
  title: 'Talks',
  description: 'Talks listed in the research atlas.',
};

export default function EnTalkIndexPage() {
  return renderTalkIndexRedirect('en', '/en');
}
