# ✨ Prompt Gen

**A zero-dependency, single-file prompt optimizer built entirely with [OpenCode](https://github.com/anomalyco/opencode).**

[中文版](README_zh.md)

---

## The Name Story

"提示词优化" — Take a rough idea, feed it to a local LLM with a preset optimization strategy, and get back a polished, detailed prompt ready to use.

The project was born from a simple need: stop manually rewriting prompts. Let local AI do the heavy lifting — privately, offline, with no data leaving your machine.

Every line of code was written through [OpenCode](https://github.com/anomalyco/opencode). The human provided the vision; OpenCode handled the engineering.

> **Author: dw with opencode**

---

## What It Does

Prompt Gen is a **single HTML file** (~84KB, ~2080 lines) that connects to local LLM servers (Ollama, LM Studio, or any OpenAI-compatible endpoint) to optimize and expand user prompts. It features a bilingual (中英文) UI with a left-right panel layout: input your rough prompt on the left, get an optimized result streamed in real-time on the right.

![Prompt Gen Screenshot](../screenshot/prompt_gen.jpg)

### Core Features

| Feature | Description |
|---------|-------------|
| **Single-file architecture** | One `prompt_gen.html` — open in browser, done |
| **Multi-provider support** | Manage multiple LLM providers with custom name, endpoint, API token, and API type; supports LAN addresses for remote servers |
| **Model selection** | Auto-fetch available models from the active provider; remembers last selection |
| **Preset system** | Customizable system prompts that define optimization strategies (e.g. expand with examples, rewrite for clarity) |
| **Preset ordering** | Drag-free reordering with ⏫🔼🔽⏬ buttons — move to top, up, down, bottom |
| **Output language** | Choose Auto, 中文, or English for the optimized output |
| **Editable output** | Right panel output is editable — refine results directly in-place |
| **Disable Thinking** | Toggle in Settings to auto-prepend `/no_think` to user messages, skipping thinking/reasoning phase on models like Qwen3 |
| **Character counters** | Real-time character count on both input (2500 max) and output (8000 max) panels |
| **Copy/Paste/Clear** | One-click clipboard operations with toast feedback; dedicated green **Copy** button next to Optimize for quick result copying |
| **Streaming output** | Real-time token-by-token streaming via SSE; supports both OpenAI and Ollama stream formats with 30-second idle timeout (only triggers when no data arrives — active generation never times out) |
| **Optimization history** | Auto-saves up to 100 entries in localStorage with restore/delete |
| **Settings persistence** | All configuration stored locally and restored on page load; remembers last provider, model, preset, and output language |
| **Config import/export** | Export all settings and history as JSON; import to restore or transfer between machines |
| **Reset config** | One-click reset in Settings to clear all data and restore defaults |
| **Auto-grow text areas** | Input box expands with content, no scrollbars |
| **Sample prompt** | Pre-filled with a sample sentence so the UI is ready to try immediately |
| **Loading animation** | Animated dots while streaming or waiting for optimization response |
| **Bilingual UI** | All labels and messages shown in 中英文 |
| **CORS guidance** | Built-in banner with fix instructions when running from `file://` protocol |
| **Responsive design** | Side-by-side on desktop (1:2 ratio), stacked on mobile (<768px) |
| **Error handling** | Clear inline messages for API failures, CORS issues, empty responses, or missing models |

### Security

| Measure | Description |
|---------|-------------|
| **Content Security Policy** | CSP meta tag allows http/https connections to any endpoint (supporting localhost, LAN, and remote servers); URL safety enforced by `sanitizeUrl()` at application level; blocks all external resource loading |
| **XSS prevention** | All user input rendered via `textContent`; SVG icons created with DOM API (`createElementNS`); error display uses `escapeHtml()` |
| **URL validation** | All endpoints validated with `sanitizeUrl()` — only http/https accepted |
| **Prototype pollution defense** | `pickKnownKeys()` whitelist filter on all external data (localStorage load, JSON import) — only known config keys accepted |
| **Data validation** | Imported providers, presets, and history items validated with length limits (token ≤500, userPrompt ≤2.5K, optimizedPrompt ≤8K) |
| **Request timeouts** | CORS check (5s) and model list (15s) use `fetchWithTimeout()`; optimization uses `fetchStreaming()` with 30s idle timeout — only triggers when no data arrives for 30 consecutive seconds; active streaming never times out |
| **Response defense** | API responses checked with safe property chains; empty results throw explicit error |
| **Import size limit** | JSON import capped at 5MB; file format and `app` field verified before processing |
| **Referrer policy** | `no-referrer` — prevents URL leakage to external servers |
| **Frozen defaults** | Default presets and providers are `Object.freeze()`'d — cannot be mutated at runtime |
| **Unicode safety** | `safeStringSlice()` with `Array.from` prevents surrogate pair truncation in history display |
| **Password manager suppression** | Token field uses CSS text-security masking instead of `type="password"` to prevent browser save-password prompts; `autocomplete="off"` and extension-specific ignore attributes |

---

## Prerequisites

To use Prompt Gen, you need a local LLM server running on your machine.

### 1. Local LLM Server
- **Ollama** (Recommended)
- **LM Studio**
- Any **OpenAI-compatible** API server

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
Open `prompt_gen.html` in your browser by double-clicking it or using the terminal:

```bash
open prompt_gen/prompt_gen.html
```

### 3. Configure Provider
Click the **gear icon** to open settings. The default providers (Ollama at `localhost:11434` and LM Studio at `127.0.0.1:1234`) are pre-configured. Add, edit, or delete providers as needed — LAN addresses (e.g. `192.168.x.x`) are also supported. Each provider supports a custom name, endpoint URL, API token, and API type (OpenAI-compatible or Ollama native).

### 4. Select Model
On the main interface, select a provider from the toolbar dropdown, then click the **refresh button** to load available models. Select the model you want to use.

### 5. Optimize
Type or paste your prompt on the left (up to 2500 characters — a sample sentence is pre-filled), choose a preset strategy and output language, then click **优化 Optimize**. The optimized result streams in real-time on the right — editable, copyable, with character count (up to 8000 characters). Use the green **复制 Copy** button next to Optimize to quickly copy the result to clipboard.

### 6. Manage Presets (Optional)
In Settings, scroll to **预设管理 Presets**. Add new optimization strategies with custom system prompts, edit existing ones, reorder with the ⏫🔼🔽⏬ buttons, or delete.

### 7. Import/Export (Optional)
In Settings, use **导出 Export** to save all configuration and history as a JSON file. Use **导入 Import** to restore from a backup or transfer settings between machines.

---

## Architecture

```
prompt_gen.html (~84KB, single file)
├── <head>
│   ├── CSP meta tag           — Allow http/https connections; restrict resource loading
│   └── Referrer policy        — no-referrer
├── <style>
│   ├── CSS variables           — Theming and consistent design tokens
│   ├── Responsive layout       — Flexbox, 1:2 panel ratio, mobile breakpoint at 768px
│   ├── Loading animation       — @keyframes blink for dot animation
│   └── Visual styling          — Blue input panel, green output panel, shadow-enhanced borders
└── <script>
    ├── Security helpers        — escapeHtml(), sanitizeUrl(), pickKnownKeys(),
    │                             fetchWithTimeout(), fetchStreaming(), safeStringSlice(),
    │                             createDeleteIcon()
    ├── State management        — Config, history, last preset/lang (all in localStorage)
    ├── Multi-provider system   — Add/edit/delete providers with name, endpoint, token, API type
    ├── API integration         — OpenAI-compatible (/v1/chat/completions) and Ollama native (/api/chat)
    │                             with real-time SSE streaming for both formats
    ├── Model management        — Auto-fetch model list from active provider, persist selection
    ├── Preset system           — CRUD + reorder (top/up/down/bottom), system prompt editor
    ├── Prompt optimization     — Builds system prompt with preset + output language instruction;
    │                             streams response token-by-token with 30s idle timeout
    ├── History management      — Save, render, restore, delete, clear (max 100 entries)
    ├── Import/Export           — Full config + history as JSON, with validation on import
    ├── Data validation         — validateProvider(), validatePreset(), validateHistoryItem()
    ├── UI components           — Settings/Preset/Provider/History modals, CORS banner, toast
    └── Clipboard               — Copy/paste with navigator.clipboard API
```

---

## Limitations

- **Text only**: Prompt input limited to 2500 characters; output limited to 8000 characters; no support for file or image-based prompts.
- **Server dependency**: Requires a running local LLM server (Ollama, LM Studio, or compatible).
- **Model quality**: Optimization quality depends entirely on the local model used.
- **Clipboard permission**: `file://` protocol may prompt for clipboard access each time; use `http://localhost` to allow persistent permission.

---

## License

This project is licensed under the **GNU General Public License v3.0** (GPL-3.0).

You are free to use, modify, and distribute this software under the terms of the GPL v3. Any derivative work must also be distributed under the same license.

See [LICENSE](LICENSE) for the full license text.

---

*Built with ✨ and OpenCode engineering.*
