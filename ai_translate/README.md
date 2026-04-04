# ❤️ AI Translate

**A zero-dependency, single-file AI translator built entirely with [OpenCode](https://github.com/anomalyco/opencode).**

[中文版](README_zh.md)

---

## The Name Story

"爱翻译" (Ài Fānyì) — "爱" means love, and sounds exactly like "AI". It is a local AI-powered translator you will love to use.

The project was inspired by the need for private, offline translation using local LLMs. No cloud, no API keys, and no data leaving your machine.

Every line of code was written through [OpenCode](https://github.com/anomalyco/opencode). The human provided the vision; OpenCode handled the engineering.

> **Author: dw with opencode**

---

## What It Does

AI Translate is a **single HTML file** (~52KB, ~1450 lines) that connects to local Ollama or LM Studio servers for AI-powered text translation. It features a Google Translate-inspired bilingual (中英文) UI and supports multiple language pairs with custom language extensions.

![AI Translate Screenshot](../screenshot/ai_translate.jpg)

### Core Features

| Feature | Description |
|---------|-------------|
| **Single-file architecture** | One `index.html` — open in browser, done |
| **Dual backend support** | Ollama and LM Studio integration with configurable endpoints |
| **Built-in language pairs** | 简体中文 ↔ English / 日本語 / 繁體中文 |
| **Custom languages** | Add any language pair via Settings (e.g. Deutsch, Français, 한국어) |
| **One-click swap** | ⇄ button swaps source/target languages, text, and auto-translates |
| **Copy/Paste/Clear** | One-click clipboard operations with toast feedback; paste auto-triggers translation |
| **Character limit** | 5000 character limit with real-time counter |
| **Translation history** | Auto-saves up to 100 entries in localStorage with restore/delete |
| **Settings persistence** | Backend, endpoint, and model selection stored locally and restored on page load |
| **Default language pair** | Always resets to English → 简体中文 on page refresh |
| **Auto-translate on switch** | Switching language tabs auto-triggers translation when source text exists |
| **Reset config** | One-click reset in Settings to clear all data and restore defaults |
| **Auto-grow text areas** | Input and output boxes expand with content, no scrollbars |
| **Loading animation** | Animated dots while waiting for translation response |
| **Bilingual UI** | All labels and messages shown in 中英文 (except language tabs) |
| **Smart prompts** | Specialized prompt engineering for 简繁 conversion (bidirectional) |
| **Responsive design** | Side-by-side on desktop, stacked on mobile (<768px) |
| **Error handling** | Clear inline messages for API failures, CORS issues, or missing models |

### Security

| Measure | Description |
|---------|-------------|
| **Content Security Policy** | CSP meta tag restricts connections to localhost and private LAN networks (10.x, 172.16-31.x, 192.168.x), blocks external resources |
| **XSS prevention** | All user input escaped via `textContent`/`escapeHtml()` — no raw innerHTML injection |
| **URL validation** | Backend endpoints validated with `sanitizeUrl()` — only http/https accepted |
| **No global exposure** | No unnecessary functions on `window` object |
| **Referrer policy** | `no-referrer` — prevents URL leakage to external servers |
| **No inline handlers** | All event handlers attached via `addEventListener` — no inline `onclick` |

---

## Prerequisites

To use AI Translate, you need a local LLM server running on your machine.

### 1. Local LLM Server
- **Ollama** (Recommended)
- **LM Studio**

### 2. Configure CORS (Critical for Ollama)
Browsers opening local HTML files send an `Origin: null` header, which Ollama blocks by default. You must allow all origins to enable browser access.

**macOS:**
```bash
# Set environment variable to allow all origins
launchctl setenv OLLAMA_ORIGINS "*"
# Then restart the Ollama application from the menu bar
```

**Linux:**
```bash
# For systemd-managed Ollama, edit the service file
sudo systemctl edit ollama.service
# Add under [Service]:
# Environment="OLLAMA_ORIGINS=*"
sudo systemctl restart ollama
```

For **LM Studio**, CORS is typically enabled by default. If you encounter errors, check the server settings in the LM Studio sidebar.

---

## Getting Started

### 1. Start Your Server
Ensure Ollama or LM Studio is running and configured as described in the Prerequisites section.

### 2. Open the App
Open `index.html` in your browser by double-clicking it or using the terminal:

```bash
open ai_translate/index.html
```

### 3. Configure Backend
Click the **gear icon** to open settings. Select your backend (Ollama or LM Studio), click **Refresh** to load available models, and select the model you want to use.

### 4. Translate
Select your language pair, type or paste your text, and click **Translate**.

### 5. Add Custom Languages (Optional)
In Settings, scroll to **Custom Languages**. Type a language name (e.g. `Deutsch`, `Français`, `한국어`) and click **+ Add**. The language will appear in the language selector bar immediately.

---

## Architecture

```
index.html (~52KB, single file)
├── <head>
│   ├── CSP meta tag         — Restrict connections to localhost and private LAN
│   └── Referrer policy      — no-referrer
├── <style>
│   ├── CSS variables         — Theming and consistent design tokens
│   ├── Responsive layout     — Flexbox, mobile breakpoint at 768px
│   ├── Loading animation     — @keyframes blink for dot animation
│   └── Visual styling        — Green output panel, coral swap button
└── <script>
    ├── Security helpers      — escapeHtml(), sanitizeUrl()
    ├── State management      — Config and history in localStorage; language pair resets to default on load
    ├── API integration       — Ollama (/api/chat) and LM Studio (/v1/chat/completions)
    ├── Language logic         — Built-in + custom languages, swap/switch/paste all auto-translate
    ├── Prompt engineering     — Specialized prompts for 简繁 conversion
    ├── Custom languages       — Add/delete, stored in localStorage, merged at runtime
    ├── History management     — Save, render, restore, delete, clear (max 100 entries)
    ├── UI components          — Settings modal, history panel, toast notifications
    └── Clipboard              — Copy/paste with navigator.clipboard API
```

---

## Limitations

- **Text only**: No support for document, image, or website translation.
- **Manual selection**: No automatic language detection.
- **No audio**: Voice input and output are not supported.
- **Server dependency**: Requires a running local LLM server (Ollama or LM Studio).
- **Model quality**: Translation quality depends entirely on the local model used.
- **Clipboard permission**: `file://` protocol may prompt for clipboard access each time; use `http://localhost` to allow persistent permission.

---

## License

This project is licensed under the **GNU General Public License v3.0** (GPL-3.0).

You are free to use, modify, and distribute this software under the terms of the GPL v3. Any derivative work must also be distributed under the same license.

See [LICENSE](LICENSE) for the full license text.

---

*Built with 爱 (love) and OpenCode engineering.*
