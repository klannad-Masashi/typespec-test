# TypeSpec専用のDockerファイル
FROM node:18-alpine

# 作業ディレクトリの設定
WORKDIR /app

# 必要なツールのインストール
RUN apk add --no-cache \
    git \
    curl \
    && npm install -g @typespec/compiler

# package.jsonとpackage-lock.jsonをコピー
COPY package*.json ./

# Node.js依存関係のインストール
RUN npm install

# TypeSpec関連ファイルをコピー
COPY typespec/ ./typespec/
COPY tspconfig.yaml ./

# 開発用のエントリーポイント
CMD ["npm", "run", "typespec:compile"]