#!/bin/bash
# img2prompt.sh - 用 Ollama 视觉模型将图片转为提示词
# 用法: ./img2prompt.sh <图片目录>
#
# Copyright (C) 2025 dw
# License: GPL-3.0 (https://www.gnu.org/licenses/gpl-3.0.html)

MODEL="gemma4:e4b"
PROMPT_LANG="en"
API_URL="http://localhost:11434"
if [ -f "${HOME}/.env" ]; then
  _env_val=$(grep -E '^VISION_MODEL=' "${HOME}/.env" | tail -1 | cut -d'=' -f2-)
  [ -n "$_env_val" ] && MODEL="$_env_val"
  _lang_val=$(grep -E '^PROMPT_LANG=' "${HOME}/.env" | tail -1 | cut -d'=' -f2-)
  [ -n "$_lang_val" ] && PROMPT_LANG="$_lang_val"
  _url_val=$(grep -E '^API_URL=' "${HOME}/.env" | tail -1 | cut -d'=' -f2-)
  [ -n "$_url_val" ] && API_URL="$_url_val"
fi

if [ "$PROMPT_LANG" = "zh" ]; then
  PROMPT="用中文详细描述这张图片的内容。包含主体、风格、光照、颜色、构图、氛围。全部使用中文，不要使用任何英文。只输出纯文本描述，不要使用星号、井号等任何markdown格式，不要其他内容。"
else
  PROMPT="Describe this image in detail. Include subject, style, lighting, colors, composition, mood. Output only plain text description, no markdown formatting such as asterisks or hashtags, nothing else."
fi

DIR="${1:-.}"

if [ ! -d "$DIR" ]; then
  echo "目录不存在: $DIR" >&2
  exit 1
fi

FILES=$(find "$DIR" -type f \( \
  -iname '*.jpg' -o -iname '*.jpeg' -o -iname '*.png' \
  -o -iname '*.webp' -o -iname '*.gif' -o -iname '*.bmp' \) | sort)

if [ -z "$FILES" ]; then
  echo "未找到图片: $DIR" >&2
  exit 1
fi

COUNT=$(echo "$FILES" | wc -l | tr -d ' ')
echo "找到 ${COUNT} 张图片，模型: $MODEL (${API_URL})"
echo "---"

echo "$FILES" | while read -r IMG; do
  HASH=$(md5sum "$IMG" | cut -d' ' -f1)
  OUT_FILE="${DIR}/${HASH}.txt"

  if [ -f "$OUT_FILE" ]; then
    echo "[跳过] $(basename "$IMG") -> ${HASH}.txt (已存在)"
    continue
  fi

  B64=$(base64 < "$IMG")

  if echo "$API_URL" | grep -q '/v1'; then
    PAYLOAD=$(echo "$B64" | jq -Rs \
      --arg model "$MODEL" \
      --arg prompt "$PROMPT" \
      '{model: $model, messages: [{role: "user", content: [{type: "text", text: $prompt}, {type: "image_url", image_url: {url: ("data:image/jpeg;base64," + .)}}]}], stream: false}')
    RESPONSE=$(echo "$PAYLOAD" | curl -s "${API_URL}/chat/completions" -H "Content-Type: application/json" -d @-)
    RESULT=$(echo "$RESPONSE" | jq -r '.choices[0].message.content // empty')
  else
    PAYLOAD=$(echo "$B64" | jq -Rs \
      --arg model "$MODEL" \
      --arg prompt "$PROMPT" \
      '{model: $model, prompt: $prompt, images: [.], stream: false}')
    RESPONSE=$(echo "$PAYLOAD" | curl -s "${API_URL}/api/generate" -d @-)
    RESULT=$(echo "$RESPONSE" | jq -r '.response // empty')
  fi

  if [ -z "$RESULT" ]; then
    echo "[失败] $(basename "$IMG")" >&2
    continue
  fi

  echo "$RESULT" > "$OUT_FILE"
  echo "[完成] $(basename "$IMG") -> ${HASH}.txt"
done

