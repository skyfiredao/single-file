# 🔀 Cat Git

**A zero-dependency, single-file browser-based Git repository browser, built entirely with [OpenCode](https://github.com/anomalyco/opencode).**

[中文版](README_zh.md)

---

## The Name Story

Cat Git was born from a simple question: *What if you could browse Git history right in the browser — no server, no CLI, no install?*

It started as a companion to [Cat Doc](../cat_doc/) — a single-file document manager. While Cat Doc handles document reading and editing, there was no way to view version history for files living in Git repositories under the same `doc/` workspace.

So the idea was: embed a full Git engine into a single HTML file, let it walk the commit graph, and show diffs — all offline, all client-side. The `isomorphic-git` library made it possible: a complete JavaScript Git implementation that runs in the browser.

Every single line of code was written through [OpenCode](https://github.com/anomalyco/opencode) — an AI-powered coding assistant. The human provided direction; OpenCode did the engineering.

> **Author: dw with opencode**

---

## What It Does

Cat Git is a **single HTML file** (~84KB of application logic + embedded isomorphic-git) that lets you browse local Git repositories, view file history, compare diffs, and checkout historical versions — all in the browser.

![Cat Git Screenshot](../screenshot/cat_git.jpg)

### Core Features

| Feature | Description |
|---------|-------------|
| **Single-file architecture** | One `cat_git.html` — drop it anywhere, open in browser, done |
| **Auto-detect Git repos** | Scans the `doc/` directory and lists all Git repositories found |
| **Repository & branch switching** | Dropdown selectors for repo and branch |
| **Lazy tree navigation** | Expands directories one level at a time — handles large repos efficiently |
| **File-specific commit history** | Shows only commits that modified the selected file, not the full repo log |
| **Optimized history algorithm** | Walks the parent chain from HEAD, compares blob OIDs with `treeWalkCache` — avoids scanning full commit history |
| **Progressive rendering** | History entries appear incrementally as they are found |
| **Side-by-side diff** | Myers diff with context lines (±3) and fold separators for unchanged regions |
| **Version checkout** | Roll back a file to any historical version via `git checkout --force` (with confirmation) |
| **Deep link to Cat Doc** | Opens files in Cat Doc for full syntax highlighting via URL hash |
| **Auto-restore** | Remembers authorized directory via IndexedDB — no re-authorization needed |
| **Bilingual UI** | All labels in Chinese with English translations |

### History Entry Display

Each version entry in the right-side panel shows:

| Field | Style |
|-------|-------|
| Commit time | Black bold |
| Commit hash (short) | Black normal weight |
| Author name (first word only) | Black bold, on second line |
| Commit message | Normal weight, same line as author |

Entries use alternating background colors for visual clarity, with white highlight on hover and selection.

---

## Browser Compatibility

Cat Git requires the **File System Access API**, which is only available in Chromium-based browsers:

| Browser | Support |
|---------|---------|
| Google Chrome | ✅ Full support |
| Microsoft Edge | ✅ Full support |
| Safari | ❌ Not supported |
| Firefox | ❌ Not supported |

---

## Getting Started

### 1. Deploy

Place `cat_git.html` alongside your `doc/` directory. No server required.

```bash
my-workspace/
├── cat_git.html
├── cat_doc.html    # optional — for syntax-highlighted file viewing
├── cat_md.html     # optional — lightweight markdown viewer
└── doc/
    ├── my-repo/    # a Git repository
    └── notes/      # regular files
```

### 2. Authorize

On first open, click **"授权访问 (Authorize)"**. The browser will ask you to select the parent directory. Cat Git automatically uses the `doc/` subdirectory inside it and scans for Git repositories.

### 3. Browse

- **Top bar**: Select repository and branch from dropdowns.
- **Left sidebar**: Navigate the file tree. Click to expand directories, click a file to view.
- **Center panel**: File content display.
- **Right panel**: Commit history for the selected file. Click a version to see the diff against the current version.
- **Version checkout**: After viewing a diff, click "切换到此版本 (Checkout)" to revert the file (requires confirmation).

---

## Architecture

```
cat_git.html (single file)
├── <style>        — CSS variables, layout, light-green theme, diff styles
├── <script>       — isomorphic-git (embedded, full Git engine in JavaScript)
├── <script>       — lightning-fs (embedded, in-memory filesystem for Git operations)
└── <script>       — Application logic
    ├── Security   — Directory validation, path constraints
    ├── State      — Directory handle, repo handle, branch, selected file
    ├── IndexedDB  — Handle persistence for auto-restore
    ├── Init       — Auto-restore or welcome screen
    ├── Repo Scan  — Detect .git directories under doc/
    ├── Tree       — Lazy directory expansion, file tree rendering
    ├── History    — Parent-chain walk algorithm with treeWalkCache
    │              — Progressive rendering of commit entries
    ├── Diff       — Myers diff algorithm, side-by-side HTML rendering
    ├── Checkout   — Force-checkout to historical version with reset
    └── Cat Doc    — Deep link integration via URL hash
```

### Design Decisions

- **Single file**: No build step, no bundler, no CDN — works offline, works anywhere
- **Embedded isomorphic-git**: Full Git implementation in JavaScript, no server needed
- **Custom history algorithm**: Standard `git.log({ filepath })` is too slow for large repos — custom parent-chain walker with blob OID comparison and tree walk caching
- **`doc/` subdirectory lock**: All operations confined to `doc/` — prevents accidental access to system files
- **No remote operations**: Clone and fetch must be done externally — keeps the tool simple and secure
- **Light green theme**: Visually distinct from Cat Doc's warm yellow theme

---

## Relationship with Cat Doc & Cat md

Cat Git is part of the Cat toolset, but each tool is fully independent:

| Aspect | Detail |
|--------|--------|
| **Independence** | Cat Git, Cat Doc, and Cat md are standalone single-file tools — none requires the others |
| **Link navigation** | Tools link to each other via the top navigation bar |
| **Shared workspace** | All tools operate within the same `doc/` directory root |
| **Deep linking** | Cat Git opens files in Cat Doc/Cat md for syntax highlighting via URL hash (e.g., `cat_doc.html#file=path`) |

---

## Technical Notes

- **Embedded Git engine**: `isomorphic-git` provides `git.log`, `git.readBlob`, `git.resolveRef`, `git.walk` and more — all running client-side
- **History performance**: Avoids O(N) full-log scan; instead walks the parent chain and compares tree/blob OIDs directly, with `treeWalkCache` for deduplication
- **Diff engine**: Built-in Myers diff generates side-by-side comparison with context lines and fold markers — no external library
- **No network dependency**: Everything runs locally; repositories must be pre-cloned by external tools

---

## Limitations

- **Chromium only**: Requires File System Access API — no Safari/Firefox support
- **No remote operations**: Cannot clone, fetch, or push — repositories must exist locally
- **No merge/rebase**: Only supports browsing, diff, and single-file checkout
- **File size**: Large binary files are not supported
- **Performance**: Very large repositories (100K+ commits) may experience slower history loading

---

## License

This project is licensed under the **GNU General Public License v3.0** (GPL-3.0).

You are free to use, modify, and distribute this software under the terms of the GPL v3. Any derivative work must also be distributed under the same license.

See [LICENSE](LICENSE) for the full license text.

---

*Built with 🐱 spirit and OpenCode engineering.*
