# Pin to Prompt

**A shell script that batch-converts Pinterest images into text descriptions using a local vision model, built with [OpenCode](https://github.com/anomalyco/opencode).**

[中文版](README_zh.md)

---

## What It Does

Download images from Pinterest with gallery-dl, then run `img2prompt.sh` to generate a plain text description for each image using a local Ollama or LM Studio vision model. Output files are named by md5 hash, so re-runs skip already-processed images.

> **Author: dw with opencode**

---

## Prerequisites

- [gallery-dl](https://github.com/mikf/gallery-dl) -- download images from Pinterest
- [Ollama](https://ollama.com/) or [LM Studio](https://lmstudio.ai/) with a vision-capable model
- `jq`
- `md5sum` (Linux) or `md5` (macOS)
- `curl`, `base64`

---

## Step 1: Download Images

Install gallery-dl:

```bash
pip install gallery-dl
# or
brew install gallery-dl
```

Download a Pinterest board:

```bash
gallery-dl "https://www.pinterest.com/username/board/"
```

Pinterest may require authentication. Pass cookies from your browser:

```bash
gallery-dl --cookies-from-browser chrome "https://www.pinterest.com/username/board/"
```

Download images only (skip videos):

```bash
gallery-dl -o "videos=false" "https://www.pinterest.com/username/board/"
# or
gallery-dl --filter "extension not in ('mp4', 'webm', 'mov')" "https://www.pinterest.com/username/board/"
```

Permanent config at `~/.config/gallery-dl/config.json`:

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

## Step 2: Generate Descriptions

```bash
./img2prompt.sh /path/to/images
```

The script recursively finds all images (jpg, png, webp, gif, bmp) in the directory and subdirectories, sends each to the vision model, and saves the description as a `.txt` file in the input directory.

---

## Configuration

Create `~/.env` to override defaults:

```bash
VISION_MODEL=gemma4:e4b
PROMPT_LANG=en
API_URL=http://localhost:11434
```

| Variable | Description | Default |
|----------|-------------|---------|
| `VISION_MODEL` | Model name for the vision API | `gemma4:e4b` |
| `PROMPT_LANG` | Output language: `en` (English) or `zh` (Chinese) | `en` |
| `API_URL` | API endpoint; auto-detects Ollama vs OpenAI-compatible by URL path | `http://localhost:11434` |

### Backend Detection

The script auto-detects the backend by checking if `API_URL` contains `/v1`:

- **Ollama**: `http://localhost:11434` or `http://192.168.1.100:11434`
- **LM Studio / OpenAI-compatible**: `http://localhost:1234/v1` or `http://192.168.1.100:1234/v1`

LAN addresses are supported for both backends.

---

## How It Works

1. Recursively finds all images (jpg, png, webp, gif, bmp) under the given directory
2. Computes md5 hash of each image, uses it as the output filename
3. Skips images that already have a corresponding `<md5>.txt` file
4. Base64-encodes the image and sends it to the vision API
5. Saves the plain text description as `<md5>.txt` in the input directory

---

## License

This project is licensed under the **GNU General Public License v3.0** (GPL-3.0).

You are free to use, modify, and distribute this software under the terms of the GPL v3. Any derivative work must also be distributed under the same license.

---

*Built with OpenCode engineering.*
