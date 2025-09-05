# TypeSpec専用のDockerファイル
FROM node:24-slim

# 作業ディレクトリの設定
WORKDIR /app/typespec

# 必要なツールのインストール  
RUN apt-get update && apt-get install -y \
    git \
    curl \
    && rm -rf /var/lib/apt/lists/*

# TypeSpecとTypeScriptをグローバルインストール
RUN npm install -g @typespec/compiler
RUN npm install -g typescript

# workspace構造に対応
COPY typespec/package*.json ./
COPY typespec/packages/ ./packages/
RUN npm install
# 全workspaceの依存関係をインストール
RUN npm install --workspaces

# 開発用のエントリーポイント
CMD ["npm", "run", "typespec:compile"]