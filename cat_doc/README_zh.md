# 🐱 Cat Doc

**零依赖、单文件的网页文档管理器，完全由 [OpenCode](https://github.com/anomalyco/opencode) 编写。**

[English](README.md)

---

## 命名小故事

一切始于一个简单的想法：*能不能像 Linux 的 `cat` 命令一样，打开一个 Markdown 文件，直接在浏览器里看到渲染后的效果？*

最初的目标只是一个查看器——打开 `.md` 文件，看到粗体、表格、标题的格式化输出，不需要安装任何东西。

然后手痒了：*"要是能编辑就好了"*——于是加了编辑功能。接着：*"Shell 脚本和 Python 文件也想看"*——于是加了代码查看和语法高亮。最后给界面做了美化——绿色主题，猫咪品牌设计。

整个项目的每一行代码都是通过 [OpenCode](https://github.com/anomalyco/opencode) 完成的——一个 AI 编程助手。人类提供方向，OpenCode 负责工程实现。所以叫 **Cat Doc**：`cat` 命令的精神，由 AI 文档工匠打造。

> **作者：dw with opencode**

---

## 功能概览

Cat Doc 是一个**单 HTML 文件**（约 2100 行，约 155KB），让你直接在浏览器中浏览、阅读、编辑和创建文档——不需要服务器，不需要构建，不需要任何依赖。

![Cat Doc 截屏](../screenshot/cat_doc.jpg)

### 核心功能

| 功能 | 说明 |
|------|------|
| **单文件架构** | 一个 `cat_doc.html`——放到任意目录，浏览器打开，即用 |
| **Markdown 预览** | 标题、粗体、斜体、表格、列表、代码块、引用、链接、分割线 |
| **语法高亮** | 内嵌 highlight.js 支持 40+ 种语言（GitHub 主题） |
| **代码查看器** | `.py`, `.sh`, `.c`, `.java`, `.js`, `.go`, `.rs`, `.rb`, `.ts`, `.swift`, `.kt` 等 |
| **纯文本查看器** | `.txt`, `.log`, `.csv`——保留空格、缩进和格式 |
| **文件树侧栏** | 可展开/折叠的目录导航 |
| **创建文件和文件夹** | 新建 `.md`, `.txt` 及其他允许的文件类型 |
| **默认只读** | 安全浏览模式；取消"只读"才能编辑 |
| **自动恢复** | 通过 IndexedDB 记住上次的目录——无需重复授权 |
| **快捷键** | `Ctrl/Cmd+S` 保存 |
| **双语界面** | 所有标签中文附英文翻译 |

### 安全加固

| 约束 | 限制 |
|------|------|
| 允许的文件类型 | `.md`, `.txt`, `.sh`, `.py`, `.c`, `.java`, `.js`, `.css`, `.html`, `.json`, `.xml`, `.yaml`, `.yml`, `.toml`, `.ini`, `.cfg`, `.conf`, `.log`, `.csv`, `.sql`, `.rb`, `.go`, `.rs`, `.cpp`, `.hpp`, `.ts`, `.swift`, `.kt`, `.pl`, `.lua`, `.r`, `.bat`, `.ps1`, `.php` |
| 最大文件大小 | 1 MB |
| 最大目录深度 | 3 层 |
| 文件名/文件夹名长度 | 最多 30 个字符 |
| 单目录最大文件数 | 100 个 |
| 禁止字符 | `< > : " \| ? *`, 控制字符、以点开头的名称 |
| XSS 防护 | HTML 转义，阻止 `javascript:`/`data:`/`vbscript:` 链接 |

---

## 浏览器行为差异

Cat Doc 根据浏览器能力自动适配不同的工作模式：

### Chrome / Edge（完整读写）

| 行为 | 详情 |
|------|------|
| **API** | File System Access API（`showDirectoryPicker`） |
| **读取** | ✅ 完整访问 |
| **写入** | ✅ 创建、编辑、保存文件和文件夹 |
| **授权** | 浏览器弹窗请求目录访问权限；授权后通过 IndexedDB 持久化 |
| **自动恢复** | 下次访问时，如权限仍有效，自动打开无需弹窗 |
| **只读切换** | 默认勾选；取消勾选以启用写操作 |

### Safari / Firefox（只读回退）

| 行为 | 详情 |
|------|------|
| **API** | `<input webkitdirectory>` 回退方案 |
| **读取** | ✅ 可以浏览和查看文件 |
| **写入** | ❌ 不支持——始终只读 |
| **授权** | 使用文件选择对话框选择目录 |
| **只读标记** | 永久显示——写操作按钮隐藏 |
| **局限** | 无 IndexedDB handle 持久化；每次访问需重新选择目录 |
| **局限** | Safari 不支持 `showDirectoryPicker`；自动优雅降级 |

### 一览对比

|             | Chrome/Edge | Safari/Firefox |
|-------------|-------------|----------------|
| 读取文件     | ✅          | ✅             |
| 写入文件     | ✅          | ❌             |
| 创建文件     | ✅          | ❌             |
| 创建文件夹   | ✅          | ❌             |
| 自动恢复     | ✅          | ❌             |
| 目录选择     | 原生 API    | 文件选择器     |
| 持久化       | IndexedDB   | 无             |

---

## 快速开始

### 1. 部署

把 `cat_doc.html` 放到任意目录即可，不需要服务器。

```bash
mkdir my-docs
cp cat_doc.html my-docs/
open my-docs/cat_doc.html    # macOS
# 或: xdg-open my-docs/cat_doc.html  (Linux)
# 或: start my-docs/cat_doc.html     (Windows)
```

### 2. 授权

首次打开时，点击 **"授权访问 (Authorize)"**。浏览器会要求选择 `cat_doc.html` 所在的目录。Cat Doc 自动使用其中的 `doc/` 子目录（不存在则自动创建）。

### 3. 浏览和编辑

- **左侧栏**：浏览文件树，点击文件打开。
- **只读模式**（默认）：文件以渲染预览模式打开。
- **编辑模式**：取消"只读 (ReadOnly)"复选框，然后点击"编辑 (Edit)"切换到文本编辑器。
- **保存**：点击"保存 (Save)"或按 `Ctrl/Cmd+S`。
- **创建**：使用"📄 新建文件 (New File)"或"📁 新建文件夹 (New Folder)"。

---

## 架构设计

```
cat_doc.html（约 155KB，单文件）
├── <style>        — CSS 变量、布局、Markdown 预览样式、highlight.js GitHub 主题
├── <script>       — highlight.js v11.9.0（内嵌，40+ 语言，约 122KB）
└── <script>       — 应用逻辑
    ├── 安全模块    — 文件验证、大小限制、路径深度检查、XSS 防护
    ├── 状态管理    — 目录句柄、文件句柄、只读模式、修改状态追踪
    ├── IndexedDB  — 句柄持久化，实现自动恢复
    ├── 初始化      — 自动恢复已保存目录或显示欢迎页
    ├── 兼容回退    — Safari/Firefox 只读文件输入处理
    ├── 目录操作    — openDirectory()、refreshTree()、readDir()
    ├── 文件操作    — openFile()、saveFile()、promptNewFile()、promptNewFolder()
    ├── 预览引擎    — Markdown 渲染器、纯文本查看器、语法高亮代码查看器
    ├── Markdown   — 自定义解析器（约 120 行）：标题、粗体、斜体、表格、列表、
    │                代码块（含 hljs 高亮）、行内代码、引用、链接、分割线、换行
    └── 对话框      — 模态对话框系统，用于文件/文件夹名称输入
```

### 设计决策

- **单文件**：无构建步骤、无打包器、无 CDN——离线可用，随处可用
- **内嵌 highlight.js**：增加约 122KB 但保证离线语法高亮，支持 40+ 种语言
- **File System Access API**：纯 HTML 页面读写本地文件的唯一方式，无需服务器
- **`doc/` 子目录锁定**：所有操作限制在 `doc/` 内——防止意外访问系统文件
- **默认只读**：安全优先——用户必须主动选择写模式
- **三种渲染路径**：`.md` → Markdown 解析器，`.txt`/`.log`/`.csv` → 纯文本 `<pre>`，其他 → highlight.js

---

## 支持的语言（语法高亮）

JavaScript、TypeScript、Python、Bash、C、C++、Java、Kotlin、Swift、Go、Rust、Ruby、Perl、Lua、R、PHP、SQL、HTML/XML、CSS、JSON、YAML、INI/TOML/Config、DOS Batch、PowerShell

---

## 相关工具

### 🔀 Cat Git — 浏览器端 Git 仓库浏览器

单文件 Git 浏览工具，可在浏览器中查看提交历史、比较差异、检出文件版本——无需服务器。详见 [Cat Git 说明](../cat_git/README_zh.md)。

### 🐱 Cat md — 轻量 Markdown 查看器

Cat md 是 **Cat Doc 的精简版**，专为快速、轻量的 Markdown 查看而设计。它与 Cat Doc 共享相同的代码架构，但移除了大部分语法高亮——仅保留 Bash/Shell 高亮。其他所有文件类型均以纯文本方式显示。

| 功能 | Cat Doc | Cat md |
|------|---------|--------|
| **文件大小** | ~155KB | ~84KB |
| **Markdown 预览** | ✅ 完整 | ✅ 完整 |
| **语法高亮** | 40+ 种语言 | 仅 Bash/Shell |
| **代码文件** | 语法高亮 | 纯文本 |
| **纯文本文件** | ✅ | ✅ |
| **文件编辑** | ✅ | ✅ |
| **IndexedDB 名称** | `DocManager` | `Catmd` |
| **主题配色** | 暖黄绿色 | 暖黄绿色（相同） |

**什么时候用 Cat md 代替 Cat Doc：**
- 你主要处理 Markdown 文件和 Shell 脚本
- 你想要更小、加载更快的页面
- 你不需要 Bash 以外的语言语法高亮

Cat md 通过顶部导航栏链接到 Cat Doc 和 Cat Git。三个工具共享同一个 `doc/` 工作目录，完全独立——每个都可以单独使用。

---

## 已知局限

- **无服务端功能**：不支持跨文件搜索、Git 集成、多人协作
- **浏览器依赖**：完整功能需要 Chrome 或 Edge；Safari/Firefox 为只读模式
- **不支持图片**：仅支持文本类文件
- **文件大小限制**：每个文件最大 1 MB（安全设计）
- **非 PWA**：无 Service Worker；需要 HTML 文件可访问

---

## 许可

本项目基于 **GNU 通用公共许可证 v3.0**（GPL-3.0）发布。

你可以自由使用、修改和分发本软件，但须遵循 GPL v3 条款。任何衍生作品必须以相同许可证发布。

完整许可证文本参见 [LICENSE](LICENSE)。

---

*以 🐱 精神打造，OpenCode 工程实现。*
