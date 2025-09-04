# TypeSpec専用のDockerファイル
FROM node:24-slim

# 作業ディレクトリの設定
WORKDIR /app

# 必要なツールのインストール  
RUN apt-get update && apt-get install -y \
    git \
    curl \
    && rm -rf /var/lib/apt/lists/* \
    && npm install -g @typespec/compiler

# package.jsonをルートにコピーしてインストール
COPY typespec/package*.json ./
RUN npm install

# TypeSpec関連ファイルをコピー
COPY typespec/tsp/ ./tsp/
COPY typespec/tspconfig.yaml ./

# 開発用のエントリーポイント
CMD ["npm", "run", "typespec:compile"]