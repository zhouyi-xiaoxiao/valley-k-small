# valley-k-small site

Next.js static-export site for interactive report browsing, bilingual routes, and agent-sync visibility.

## Commands

Run from this directory (`platform/web/`):

```bash
npm install
npm run build
```

Build via unified repo command (run from repo root):

```bash
python3 scripts/reportctl.py web-build --mode full
```

Preview static output:

```bash
python3 scripts/reportctl.py web-preview --port 4173
```

For GitHub Pages project-site deployment, set base path at build time:

```bash
NEXT_PUBLIC_BASE_PATH=/your-repo npm run build
```

## Dev server

`npm run dev` defaults to port **3000** and silently falls back to **3001** if 3000 is in use. Always read the actual port from stdout before opening a browser or asserting URL paths in tests — do not hardcode the port.

## Components — gotchas

- **`src/components/TalkRevealDeck.tsx` is a custom React component, NOT reveal.js.** Do not import `reveal.js` APIs (`Reveal.initialize`, `data-state` attributes, slide events). Slide navigation is internal React state driven by URL hash (`#slide-N`); see the file header for the actual API.

## Data contract

- `public/data/v1/index.json`
- `public/data/v1/reports/<report_id>/meta.json`
- `public/data/v1/reports/<report_id>/meta.cn.json`
- `public/data/v1/reports/<report_id>/figures.json`
- `public/data/v1/reports/<report_id>/series/<series_id>.json`
- `public/data/v1/agent/{manifest.json,reports.jsonl,events.jsonl}`
