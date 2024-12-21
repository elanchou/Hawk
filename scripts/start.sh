#!/bin/bash

# 启动后端
cd backend
poetry run python src/main.py &
backend_pid=$!

# 启动前端
cd ../frontend
yarn start &
frontend_pid=$!

# 捕获 CTRL+C 信号
trap "kill $backend_pid $frontend_pid" SIGINT

# 等待任意子进程结束
wait 