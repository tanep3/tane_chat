#!/bin/bash
# 生成AIをコマンドで動かすスクリプト

# 引数がない場合、ヘルプメッセージを表示
if [ -z $1 ]; then
  echo "使用方法: $0 '質問'"
  exit 1
fi

curl -X POST -H "Content-Type: application/json" --no-buffer -d "{\"system_prompt\": \"50文字程度に要約して回答してください。\", \"user_input\": \"$1\", \"max_tokens\": 512, \"stream\": true}" http://127.0.0.1:5005/generate

echo