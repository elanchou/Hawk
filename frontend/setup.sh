#!/bin/bash

# 确保使用最新的 yarn
corepack enable
corepack prepare yarn@stable --activate

# 创建 React TypeScript 项目
yarn create react-app . --template typescript

# 安装必要的依赖
yarn add @ant-design/pro-components @ant-design/icons antd
yarn add @types/react @types/react-dom
yarn add recharts @types/recharts
yarn add axios
yarn add moment
yarn add @emotion/react @emotion/styled