#!/usr/bin/env bash

# 查找匹配 "python3 ...app.py" 的进程 ID 列表
pids=$(pgrep -f "python3 .*app\.py")

if [[ -z "$pids" ]]; then
  echo "未找到 python3 app.py 运行的进程。"
  exit 0
fi

echo "正在停止以下进程： $pids"
# 发送 SIGTERM，若需要强制可改为 kill -9
kill $pids

# 检查是否已停止
sleep 1
still_running=$(pgrep -f "python3 .*app\.py")
if [[ -n "$still_running" ]]; then
  echo "部分进程未响应，正在强制终止： $still_running"
  kill -9 $still_running
else
  echo "全部进程已成功停止。"
fi
