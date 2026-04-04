# 🌐 Portal Site Zero

**零依赖、单文件的站点聚合面板，完全由 [OpenCode](https://github.com/anomalyco/opencode) 编写。**

[English](README.md)

---

## 命名小故事

"ps0" 是 Portal Site Zero 的缩写，意为"第零号门户"。一个面向所有自托管服务的起始页。

你在家庭实验室里跑着十几个服务，分散在不同端口、不同子域名下。你需要一个页面把它们列在一起。不是带健康检查和各种组件的仪表盘，只要一份干净的列表，用 Markdown 就能编辑。

整个项目的每一行代码都是通过 [OpenCode](https://github.com/anomalyco/opencode) 完成的。人类提供构思，OpenCode 负责工程实现。

> **作者：dw with opencode**

---

## 功能概览

Portal Site Zero 是一个**单 HTML 文件**（约 547 行），读取 `sites.md` 文件并渲染双列分组的站点门户。在 Markdown 中编辑你的站点清单，刷新页面，搞定。

![Portal Site Zero 截屏](../screenshot/ps0.jpg)

### 核心功能

| 功能 | 说明 |
|------|------|
| **单文件架构** | 一个 `ps0.html`，无需构建，无需框架 |
| **Markdown 配置** | 用 `#`/`##` 标题和 `- key: value` 字段定义服务 |
| **双列布局** | 分组分布在左右两列；可用 `[L]`/`[R]` 强制指定列 |
| **双模式加载** | HTTP 下用 `fetch()`（no-cache）；`file://` 下用 File System Access API + IndexedDB 持久化 |
| **箭头形分组标签** | clip-path 多边形标签，drop-shadow 立体感，固定 100px 宽，每组独立配色 |
| **按钮式站点条目** | 边框、阴影、悬停上浮；站点名链接到 URL，描述链接到 source |
| **6 色系循环** | 蓝、绿、黄、红、紫、青——逐组循环，深色先出现 |
| **一键刷新** | ⟳ 按钮重新加载 `sites.md`，无需刷新整个页面 |
| **响应式设计** | <768px 切换为单列；<600px 收窄内边距 |
| **零依赖** | 无第三方库、无 CDN、无 npm，纯原生 HTML/CSS/JS |
| **CSP 安全策略** | 内容安全策略禁止加载图片、字体、iframe 和外部脚本 |

---

## 快速开始

### 1. 创建 `sites.md`

将 `sites.md` 文件放在 `ps0.html` 同目录下：

```markdown
# 开发工具 [R]

## Gitea
- url: https://git.example.com
- source: https://github.com/go-gitea/gitea
- desc: 轻量级自托管 Git 服务

## Drone CI
- url: https://ci.example.com
- desc: 容器原生 CI/CD 平台

# 监控

## Grafana
- url: https://grafana.example.com
- source: https://github.com/grafana/grafana
- desc: 可视化分析平台
```

#### 格式说明

| 元素 | 语法 | 必填 |
|------|------|------|
| **分组标题** | `# 组名` | 是 |
| **列标记** | `# 组名 [L]` 或 `[R]` | 否——省略时自动左右交替分配 |
| **站点标题** | `## 站点名` | 是 |
| **URL** | `- url: https://...` | 是（必须是 `http://` 或 `https://`） |
| **源码** | `- source: https://...` | 否——如有，描述文字将变为指向此 URL 的链接 |
| **描述** | `- desc: 一些文字` | 否 |

- 站点名渲染为指向 `url` 的链接
- 描述文字在有 `source` 时渲染为指向 `source` 的链接，否则为纯文本
- 没有有效站点（缺少 URL 或非 HTTP 链接）的分组会被过滤掉
- 不带 `[L]`/`[R]` 标记的分组按顺序自动左右交替分配

### 2. 打开页面

#### 方式 A：HTTP 服务器

```bash
cd ps0
python3 -m http.server 8000
# 打开 http://localhost:8000/ps0.html
```

#### 方式 B：本地文件（Chrome / Edge）

双击 `ps0.html` 通过 `file://` 协议打开。页面会提示你授权目录访问权限（File System Access API）。授权后，目录句柄通过 IndexedDB 持久化——后续访问无需重新授权。

---

## 浏览器兼容性

| 浏览器 | HTTP 模式 | file:// 模式 |
|--------|-----------|--------------|
| **Chrome / Edge** | ✅ fetch | ✅ File System Access API + IndexedDB |
| **Firefox / Safari** | ✅ fetch | ❌ 需要 HTTP 服务器 |

Firefox 和 Safari 不支持 File System Access API。在这些浏览器中通过 `file://` 打开时，ps0 会显示提示信息，建议使用 HTTP 服务器。

---

## 架构设计

```
ps0.html（约 547 行，单文件）
├── <head>
│   ├── CSP 元标签               — 禁止图片、字体、iframe、外部脚本
│   └── Referrer 策略            — no-referrer
├── <style>
│   ├── CSS 变量                 — 配色方案、阴影、间距令牌
│   ├── 页面背景                 — 巨大 "psØ" 水印，等宽字体，居中，rgba(0,0,0,0.08)
│   ├── 顶栏                     — 深蓝色（#0d2137），固定定位，标题居中
│   ├── 双列布局                 — Flexbox 两列，最大宽度 1200px
│   ├── 分组标签                 — 箭头形 clip-path，固定 100px 宽，drop-shadow 立体感
│   ├── 站点条目                 — 边框、阴影、悬停 translateY(-1px) 上浮
│   └── 响应式适配               — <768px 单列，<600px 收窄内边距
└── <script>
    ├── parseSitesMd()           — 解析 # 分组（含 [L]/[R]）、## 站点、- key: value 字段
    ├── escapeHtml() / sanitizeUrl() — 防 XSS
    ├── groupColors[]            — 6 种色系 [深、浅、标签色]，逐组循环
    ├── renderGroup()            — 构建单组 HTML：箭头标签 + 站点条目
    ├── renderSites()            — 按 [L]/[R] 或自动交替将分组分配到左右列
    ├── IndexedDB (openDB, save/loadHandleToDB) — file:// 模式目录句柄持久化
    ├── readSitesMdFromDir()     — 从授权目录句柄读取 sites.md
    ├── loadSitesViaFetch()      — HTTP 模式：带 no-cache 的 fetch
    ├── loadSitesFromDir()       — file:// 模式：从目录句柄读取
    └── loadSites()              — 入口：根据协议路由到 fetch 或 File System Access API
```

---

## 已知局限

- **无搜索功能**：不支持在服务列表中搜索或筛选。
- **无暗色模式**：仅支持浅色主题。
- **无健康检查**：不会探测服务状态，无法显示在线/离线。
- **无离线支持**：需要 HTTP 服务器可达或本地文件可访问。
- **file:// 模式依赖浏览器**：仅 Chrome/Edge 支持 File System Access API，其他浏览器需 HTTP 服务器。

---

## 许可

本项目基于 **GNU 通用公共许可证 v3.0**（GPL-3.0）发布。

你可以自由使用、修改和分发本软件，但须遵循 GPL v3 条款。任何衍生作品必须以相同许可证发布。

完整许可证文本参见 [LICENSE](LICENSE)。

---

*一份 Markdown，一个门户，OpenCode 工程实现。*
