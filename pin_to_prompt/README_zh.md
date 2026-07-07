# Pin to Prompt

**通过本地视觉模型将 Pinterest 图片批量转换为文本描述的 Shell 脚本，使用 [OpenCode](https://github.com/anomalyco/opencode) 构建。**

[English](README.md)

---

## 功能简介

用 gallery-dl 从 Pinterest 下载图片，然后运行 `img2prompt.sh`，通过本地 Ollama 或 LM Studio 视觉模型为每张图片生成纯文本描述。输出文件以 md5 哈希命名，重复运行会自动跳过已处理的图片。

> **作者：dw with opencode**

---

## 依赖

- [gallery-dl](https://github.com/mikf/gallery-dl) -- 下载 Pinterest 图片
- [Ollama](https://ollama.com/) 或 [LM Studio](https://lmstudio.ai/)，需安装视觉模型
- `jq`
- `md5sum`（macOS 用 `md5`）
- `curl`、`base64`

---

## 第一步：下载图片

安装 gallery-dl：

```bash
pip install gallery-dl
# 或
brew install gallery-dl
```

下载整个画板：

```bash
gallery-dl "https://www.pinterest.com/username/board/"
```

Pinterest 需要登录才能访问大部分内容，用浏览器 Cookie 认证：

```bash
gallery-dl --cookies-from-browser chrome "https://www.pinterest.com/username/board/"
```

只下载图片，跳过视频：

```bash
gallery-dl -o "videos=false" "https://www.pinterest.com/username/board/"
# 或
gallery-dl --filter "extension not in ('mp4', 'webm', 'mov')" "https://www.pinterest.com/username/board/"
```

也可以写配置文件 `~/.config/gallery-dl/config.json`：

```json
{
  "extractor": {
    "pinterest": {
      "videos": false,
      "domain": "auto"
    }
  }
}
```

---

## 第二步：生成描述

```bash
./img2prompt.sh /path/to/images
```

脚本会递归查找目录及子目录下的所有图片（jpg, png, webp, gif, bmp），逐张发送给视觉模型，将描述保存为 `.txt` 文件到输入目录中。

---

## 配置

在 `~/.env` 中设置：

```bash
VISION_MODEL=gemma4:e4b
PROMPT_LANG=en
API_URL=http://localhost:11434
```

| 变量 | 说明 | 默认值 |
|------|------|--------|
| `VISION_MODEL` | 视觉模型名称 | `gemma4:e4b` |
| `PROMPT_LANG` | 输出语言：`en`（英文）或 `zh`（中文） | `en` |
| `API_URL` | API 地址，通过 URL 路径自动判断 Ollama 或 OpenAI 兼容接口 | `http://localhost:11434` |

### 后端自动检测

脚本通过 `API_URL` 是否包含 `/v1` 自动判断后端类型：

- **Ollama**：`http://localhost:11434` 或 `http://192.168.1.100:11434`
- **LM Studio / OpenAI 兼容**：`http://localhost:1234/v1` 或 `http://192.168.1.100:1234/v1`

支持局域网地址。

---

## 工作原理

1. 递归查找指定目录下的所有图片（jpg, png, webp, gif, bmp）
2. 对每张图片计算 md5 哈希，以哈希值作为输出文件名
3. 如果对应的 `<md5>.txt` 文件已存在，跳过该图片
4. 将图片 base64 编码后发送给视觉 API
5. 生成的纯文本描述保存为 `<md5>.txt`，存放在输入目录中

---

## 许可证

本项目采用 **GNU 通用公共许可证 v3.0**（GPL-3.0）授权。

你可以在 GPL v3 条款下自由使用、修改和分发本软件。任何衍生作品必须以相同许可证分发。

---

*使用 OpenCode 构建。*
