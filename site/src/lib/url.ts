const BASE_PATH = (process.env.NEXT_PUBLIC_BASE_PATH || '').replace(/\/$/, '');

export function withBasePath(url: string): string {
  if (!url.startsWith('/')) {
    return url;
  }
  if (!BASE_PATH || url.startsWith(BASE_PATH + '/')) {
    return url;
  }
  return `${BASE_PATH}${url}`;
}
