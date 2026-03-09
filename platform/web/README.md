# valley-k-small site

Next.js static-export site for interactive report browsing, bilingual routes, and agent-sync visibility.

## Commands

```bash
cd site
npm install
npm run build
```

Build via unified repo command:

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

## Data contract

- `public/data/v1/index.json`
- `public/data/v1/reports/<report_id>/meta.json`
- `public/data/v1/reports/<report_id>/meta.cn.json`
- `public/data/v1/reports/<report_id>/figures.json`
- `public/data/v1/reports/<report_id>/series/<series_id>.json`
- `public/data/v1/agent/{manifest.json,reports.jsonl,events.jsonl}`
