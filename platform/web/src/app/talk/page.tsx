import { renderTalkIndexRedirect } from '@/lib/render-talk-pages';

export const metadata = {
  title: 'Talks',
  description: 'Talks listed in the research atlas.',
};

export default function TalkIndexPage() {
  return renderTalkIndexRedirect('en', '');
}
