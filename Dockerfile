# TypeSpec開発環境用のDockerファイル
FROM node:18-alpine

# 作業ディレクトリの設定
WORKDIR /app

# 必要なツールのインストール
RUN apk add --no-cache \
    git \
    curl \
    openjdk11 \
    && npm install -g @typespec/compiler @openapitools/openapi-generator-cli

# package.jsonとpackage-lock.jsonをコピー
COPY package*.json ./

# 依存関係のインストール
RUN npm install

# ソースコードをコピー
COPY . .

# ポート番号の設定（開発用）
EXPOSE 8080 4200

# 開発用のエントリーポイント
CMD ["npm", "run", "generate:all"]