# 🌐 Portal Site Zero

**A zero-dependency, single-file site aggregation panel built entirely with [OpenCode](https://github.com/anomalyco/opencode).**

[中文版](README_zh.md)

---

## The Name Story

"ps0" stands for Portal Site Zero. The zeroth portal. A single starting point for all your self-hosted services.

You run a dozen services across your homelab, each on a different port, a different subdomain. You need one page that lists them all. Not a dashboard with health checks and widgets. Just a clean list you can edit in Markdown.

Every line of code was written through [OpenCode](https://github.com/anomalyco/opencode). The human provided the vision; OpenCode handled the engineering.

> **Author: dw with opencode**

---

## What It Does

Portal Site Zero is a **single HTML file** (~547 lines) that reads a `sites.md` file and renders a dual-column, grouped portal of services. Edit your site list in Markdown, refresh the page, done.

![Portal Site Zero Screenshot](../screenshot/ps0.jpg)

### Core Features

| Feature | Description |
|---------|-------------|
| **Single-file architecture** | One `ps0.html`, no build step, no framework |
| **Markdown config** | Define services in `sites.md` with `#`/`##` headings and `- key: value` fields |
| **Dual-column layout** | Groups distributed across two columns; force left/right with `[L]`/`[R]` markers |
| **Dual-mode loading** | HTTP: `fetch()` with no-cache; `file://`: File System Access API with IndexedDB persistence |
| **Arrow-shaped group labels** | Clip-path polygon labels with drop-shadow, fixed 100px width, per-group color |
| **Button-style site entries** | Border, shadow, hover lift effect; site name links to URL, description links to source |
| **6-color palette** | Blue, green, yellow, red, purple, cyan — cycling per group, dark shade first |
| **One-click refresh** | ⟳ button reloads `sites.md` without a full page refresh |
| **Responsive design** | <768px: single column; <600px: tighter padding |
| **Zero dependencies** | No libraries, no CDN, no npm. Vanilla HTML/CSS/JS |
| **CSP security** | Content Security Policy blocks images, fonts, frames, and external scripts |

---

## Getting Started

### 1. Create `sites.md`

Place a `sites.md` file alongside `ps0.html`:

```markdown
# Dev Tools [R]

## Gitea
- url: https://git.example.com
- source: https://github.com/go-gitea/gitea
- desc: Lightweight self-hosted Git service

## Drone CI
- url: https://ci.example.com
- desc: Container-native CI/CD platform

# Monitoring

## Grafana
- url: https://grafana.example.com
- source: https://github.com/grafana/grafana
- desc: Visualization and analytics platform
```

#### Format Rules

| Element | Syntax | Required |
|---------|--------|----------|
| **Group heading** | `# Group Name` | Yes |
| **Column marker** | `# Group Name [L]` or `[R]` | No — auto left/right alternation if omitted |
| **Site heading** | `## Site Name` | Yes |
| **URL** | `- url: https://...` | Yes (must be `http://` or `https://`) |
| **Source** | `- source: https://...` | No — if present, description text becomes a link to this URL |
| **Description** | `- desc: Some text` | No |

- Site name is rendered as a link to `url`
- Description text is rendered as a link to `source` (if source is present), otherwise plain text
- Groups without valid sites (missing or non-HTTP URLs) are filtered out
- Without `[L]`/`[R]` markers, groups alternate left-right automatically

### 2. Open the Page

#### Option A: HTTP Server

```bash
cd ps0
python3 -m http.server 8000
# Open http://localhost:8000/ps0.html
```

#### Option B: Local File (Chrome / Edge)

Double-click `ps0.html` to open via `file://` protocol. The page will prompt you to authorize directory access using the File System Access API. Once authorized, the directory handle is persisted in IndexedDB — no re-authorization needed on subsequent visits.

---

## Browser Compatibility

| Browser | HTTP Mode | file:// Mode |
|---------|-----------|--------------|
| **Chrome / Edge** | ✅ fetch | ✅ File System Access API + IndexedDB |
| **Firefox / Safari** | ✅ fetch | ❌ Requires HTTP server |

Firefox and Safari do not support the File System Access API. When opened via `file://` in these browsers, ps0 displays a message suggesting HTTP server usage.

---

## Architecture

```
ps0.html (~547 lines, single file)
├── <head>
│   ├── CSP meta tag             — Blocks images, fonts, frames, external scripts
│   └── Referrer policy          — no-referrer
├── <style>
│   ├── CSS variables            — Color palette, shadows, spacing tokens
│   ├── Page background          — Giant "psØ" watermark, monospace, centered, rgba(0,0,0,0.08)
│   ├── Header                   — Deep blue (#0d2137), sticky, centered title
│   ├── Dual-column layout       — Flexbox columns, 1200px max-width
│   ├── Group labels             — Arrow clip-path, 100px fixed width, drop-shadow
│   ├── Site entries             — Border, shadow, hover translateY(-1px) lift
│   └── Responsive               — <768px single column, <600px tighter padding
└── <script>
    ├── parseSitesMd()           — Parses # groups (with [L]/[R]), ## sites, - key: value fields
    ├── escapeHtml() / sanitizeUrl() — XSS prevention
    ├── groupColors[]            — 6 color palettes [dark, light, label-bg], cycling per group
    ├── renderGroup()            — Builds arrow-label + site entries HTML per group
    ├── renderSites()            — Distributes groups to left/right columns by [L]/[R] or auto-alternation
    ├── IndexedDB (openDB, save/loadHandleToDB) — Directory handle persistence for file:// mode
    ├── readSitesMdFromDir()     — Reads sites.md from authorized directory handle
    ├── loadSitesViaFetch()      — HTTP mode: fetch with no-cache
    ├── loadSitesFromDir()       — file:// mode: read from directory handle
    └── loadSites()              — Entry point: routes to fetch or File System Access API based on protocol
```

---

## Limitations

- **No search**: No filtering or search across services.
- **No dark mode**: Light theme only.
- **No health checks**: Doesn't ping services or show online/offline status.
- **No offline support**: Requires either the HTTP server or a locally accessible file.
- **file:// mode browser-dependent**: Only Chrome/Edge support File System Access API; other browsers need HTTP.

---

## License

This project is licensed under the **GNU General Public License v3.0** (GPL-3.0).

You are free to use, modify, and distribute this software under the terms of the GPL v3. Any derivative work must also be distributed under the same license.

See [LICENSE](LICENSE) for the full license text.

---

*Built with one Markdown file and OpenCode engineering.*
