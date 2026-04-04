# 🐱 Cat Doc

**A zero-dependency, single-file web document manager built entirely with [OpenCode](https://github.com/anomalyco/opencode).**

[中文版](README_zh.md)

---

## The Name Story

It started with a simple idea: *What if you could `cat` a Markdown file and see it rendered beautifully — right in the browser?*

Inspired by the Linux `cat` command, the original goal was just a viewer — open `.md` files and see formatted output with bold text, tables, and headings, without installing anything.

Then came the itch: *"What if I could edit too?"* So editing was added. Then: *"What about shell scripts and Python files?"* So code viewing was added with syntax highlighting. Then the UI got a proper coat of paint — a green-themed, cat-branded design.

Every single line of code was written through [OpenCode](https://github.com/anomalyco/opencode) — an AI-powered coding assistant. The human provided direction; OpenCode did the engineering. That's why it's called **Cat Doc**: the `cat` command spirit, built by a doc-wielding AI.

> **Author: dw with opencode**

---

## What It Does

Cat Doc is a **single HTML file** (~2100 lines, ~155KB) that lets you browse, read, edit, and create documents directly in your browser — no server, no build step, no dependencies.

![Cat Doc Screenshot](../screenshot/cat_doc.jpg)

### Core Features

| Feature | Description |
|---------|-------------|
| **Single-file architecture** | One `cat_doc.html` — drop it anywhere, open in browser, done |
| **Markdown preview** | Headings, bold, italic, tables, lists, code blocks, blockquotes, links, horizontal rules |
| **Syntax highlighting** | 40+ languages via embedded highlight.js (GitHub theme) |
| **Code file viewer** | `.py`, `.sh`, `.c`, `.java`, `.js`, `.go`, `.rs`, `.rb`, `.ts`, `.swift`, `.kt`, and more |
| **Plain text viewer** | `.txt`, `.log`, `.csv` — whitespace and formatting preserved |
| **File tree sidebar** | Expandable/collapsible directory navigation |
| **Create files & folders** | New `.md`, `.txt`, and other allowed file types |
| **Read-only by default** | Safe browsing mode; uncheck "ReadOnly" to enable editing |
| **Auto-restore** | Remembers your last directory via IndexedDB — no re-authorization needed |
| **Keyboard shortcut** | `Ctrl/Cmd+S` to save |
| **Bilingual UI** | All labels in Chinese with English translations |

### Security Hardening

| Constraint | Limit |
|------------|-------|
| Allowed file types | `.md`, `.txt`, `.sh`, `.py`, `.c`, `.java`, `.js`, `.css`, `.html`, `.json`, `.xml`, `.yaml`, `.yml`, `.toml`, `.ini`, `.cfg`, `.conf`, `.log`, `.csv`, `.sql`, `.rb`, `.go`, `.rs`, `.cpp`, `.hpp`, `.ts`, `.swift`, `.kt`, `.pl`, `.lua`, `.r`, `.bat`, `.ps1`, `.php` |
| Max file size | 1 MB |
| Max directory depth | 3 levels |
| Max filename/folder name length | 30 characters |
| Max files per directory | 100 |
| Forbidden characters | `< > : " \| ? *`, control chars, dot-prefix names |
| XSS protection | HTML escaping, `javascript:`/`data:`/`vbscript:` link blocking |

---

## Browser Behavior

Cat Doc adapts its behavior based on browser capabilities:

### Chrome / Edge (Full Read-Write)

| Behavior | Detail |
|----------|--------|
| **API** | File System Access API (`showDirectoryPicker`) |
| **Read** | ✅ Full access |
| **Write** | ✅ Create, edit, save files and folders |
| **Authorization** | Browser prompts for directory access; once granted, persisted via IndexedDB |
| **Auto-restore** | On next visit, if permission is still granted, auto-opens without prompt |
| **Read-only toggle** | Checked by default; uncheck to enable write operations |

### Safari / Firefox (Read-Only Fallback)

| Behavior | Detail |
|----------|--------|
| **API** | `<input webkitdirectory>` fallback |
| **Read** | ✅ Can browse and view files |
| **Write** | ❌ Not supported — always read-only |
| **Authorization** | Uses file input dialog to select directory |
| **Read-only badge** | Permanently displayed — write buttons hidden |
| **Limitation** | No IndexedDB handle persistence; must re-select directory each visit |
| **Limitation** | Safari does not support `showDirectoryPicker`; falls back gracefully |

### Key Differences at a Glance

|                 | Chrome/Edge | Safari/Firefox |
|-----------------|-------------|----------------|
| Read files      | ✅          | ✅             |
| Write files     | ✅          | ❌             |
| Create files    | ✅          | ❌             |
| Create folders  | ✅          | ❌             |
| Auto-restore    | ✅          | ❌             |
| Directory pick  | Native API  | File input     |
| Persistence     | IndexedDB   | None           |

---

## Getting Started

### 1. Deploy

Just put `cat_doc.html` in any directory. No server required.

```bash
mkdir my-docs
cp cat_doc.html my-docs/
open my-docs/cat_doc.html    # macOS
# or: xdg-open my-docs/cat_doc.html  (Linux)
# or: start my-docs/cat_doc.html     (Windows)
```

### 2. Authorize

On first open, click **"授权访问 (Authorize)"**. The browser will ask you to select the directory where `cat_doc.html` lives. Cat Doc automatically uses the `doc/` subdirectory inside it (creates it if missing).

### 3. Browse & Edit

- **Left sidebar**: Navigate the file tree. Click a file to open it.
- **Read-only mode** (default): Files open in rendered preview mode.
- **Edit mode**: Uncheck the "只读 (ReadOnly)" checkbox, then click "编辑 (Edit)" to switch to the textarea editor.
- **Save**: Click "保存 (Save)" or press `Ctrl/Cmd+S`.
- **Create**: Use "📄 新建文件 (New File)" or "📁 新建文件夹 (New Folder)".

---

## Architecture

```
cat_doc.html (~155KB, single file)
├── <style>        — CSS variables, layout, markdown preview styles, highlight.js GitHub theme
├── <script>       — highlight.js v11.9.0 (embedded, 40+ languages, ~122KB)
└── <script>       — Application logic
    ├── Security   — File validation, size limits, path depth, XSS protection
    ├── State      — Directory handle, file handle, read-only mode, modification tracking
    ├── IndexedDB  — Handle persistence for auto-restore
    ├── Init       — Auto-restore saved directory or show welcome screen
    ├── Fallback   — Safari/Firefox read-only file input handler
    ├── Directory  — openDirectory(), refreshTree(), readDir()
    ├── File Ops   — openFile(), saveFile(), promptNewFile(), promptNewFolder()
    ├── Preview    — Markdown renderer, plain text viewer, syntax-highlighted code viewer
    ├── Markdown   — Custom parser (~120 lines): headings, bold, italic, tables, lists,
    │                code blocks (with hljs), inline code, blockquotes, links, HR, line breaks
    └── Dialog     — Modal dialog system for file/folder name input
```

### Design Decisions

- **Single file**: No build step, no bundler, no CDN — works offline, works anywhere
- **Embedded highlight.js**: Adds ~122KB but guarantees offline syntax highlighting for 40+ languages
- **File System Access API**: The only way to read/write local files from a pure HTML page without a server
- **`doc/` subdirectory lock**: All operations are confined to `doc/` — prevents accidental access to system files
- **Read-only by default**: Safety first — users must explicitly opt into write mode
- **Three rendering paths**: `.md` → Markdown parser, `.txt`/`.log`/`.csv` → plain `<pre>`, everything else → highlight.js

---

## Supported Languages (Syntax Highlighting)

JavaScript, TypeScript, Python, Bash, C, C++, Java, Kotlin, Swift, Go, Rust, Ruby, Perl, Lua, R, PHP, SQL, HTML/XML, CSS, JSON, YAML, INI/TOML/Config, DOS Batch, PowerShell

---

## Related Tools

### 🔀 Cat Git — Browser-Based Git Repository Browser

A single-file Git browser that lets you view commit history, compare diffs, and checkout file versions — all in the browser, no server needed. See [Cat Git README](../cat_git/README.md).

### 🐱 Cat md — Lightweight Markdown Viewer

Cat md is a **stripped-down version of Cat Doc**, designed for quick, lightweight Markdown viewing. It shares the same codebase and architecture as Cat Doc but removes most syntax highlighting — keeping only Bash/Shell highlighting. All other file types are displayed as plain text.

| Feature | Cat Doc | Cat md |
|---------|---------|--------|
| **File size** | ~155KB | ~84KB |
| **Markdown preview** | ✅ Full | ✅ Full |
| **Syntax highlighting** | 40+ languages | Bash/Shell only |
| **Code files** | Syntax-highlighted | Plain text |
| **Plain text files** | ✅ | ✅ |
| **File editing** | ✅ | ✅ |
| **IndexedDB name** | `DocManager` | `Catmd` |
| **Theme** | Warm yellow-green | Warm yellow-green (same) |

**When to use Cat md instead of Cat Doc:**
- You primarily work with Markdown files and shell scripts
- You want a smaller, faster-loading page
- You don't need syntax highlighting for languages other than Bash

Cat md links to both Cat Doc and Cat Git via the top navigation bar. All three tools share the same `doc/` workspace and are fully independent — each works standalone.

---

## Limitations

- **No server-side features**: No search across files, no git integration, no collaboration
- **Browser-dependent**: Full functionality requires Chrome or Edge; Safari/Firefox are read-only
- **No image support**: Only text-based file types are supported
- **File size cap**: 1 MB per file (by design, for security)
- **No offline-first PWA**: No service worker; requires the HTML file to be accessible

---

## License

This project is licensed under the **GNU General Public License v3.0** (GPL-3.0).

You are free to use, modify, and distribute this software under the terms of the GPL v3. Any derivative work must also be distributed under the same license.

See [LICENSE](LICENSE) for the full license text.

---

*Built with 🐱 spirit and OpenCode engineering.*
