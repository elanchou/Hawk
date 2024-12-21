#!/bin/bash

# 安装 poetry（如果没有安装）
if ! command -v poetry &> /dev/null; then
    curl -sSL https://install.python-poetry.org | python3 -
fi

# 配置 poetry 在项目目录下创建虚拟环境
poetry config virtualenvs.in-project true

# 安装依赖
poetry install

# 创建必要的目录
mkdir -p logs
mkdir -p data