# GitBench Web Report

The web report is a static Astro site with Vercel API functions for interactive
report data. `gitbench report` generates both compatibility JSON and the SQLite
database used by the API routes:

```text
public/results.json
data/gitbench.db
data/schema.sql
```

`public/results.json` remains a compatibility artifact for static build-time
data. Hydrated React islands should use `/api/*` report endpoints through the
browser report client instead of fetching the full JSON payload.

## SQLite Runtime

API functions use Node's built-in `node:sqlite` module through the project
runtime requirement of Node 22.12 or newer. This avoids adding a native npm
SQLite dependency for Vercel/local development, keeps install friction low, and
isolates runtime-specific access behind `ReportStore` so a future Cloudflare D1
adapter can implement the same contract.

## Commands

Run these from `gitbench/web` unless noted otherwise.

| Command                   | Action                                           |
| :------------------------ | :----------------------------------------------- |
| `pnpm install`            | Installs dependencies                            |
| `pnpm dev`                | Starts Astro only at `localhost:4321`            |
| `pnpm dev:api`            | Starts Astro and Vercel API routes together      |
| `pnpm build`              | Build your production site to `./dist/`          |
| `pnpm preview`            | Preview your build locally, before deploying     |
| `pnpm astro ...`          | Run CLI commands like `astro add`, `astro check` |

Before running `pnpm dev:api`, generate report artifacts from the repository
root:

```sh
gitbench report --no-build
```
