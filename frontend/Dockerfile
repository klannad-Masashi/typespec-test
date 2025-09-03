# Angular フロントエンド開発環境
FROM node:24-slim

# 作業ディレクトリの設定
WORKDIR /app

# 必要なパッケージのインストール
RUN apt-get update && apt-get install -y git curl && rm -rf /var/lib/apt/lists/*

# Angular CLIのグローバルインストール
RUN npm install -g @angular/cli

# package.jsonとpackage-lock.jsonをコピー（存在する場合）
COPY package*.json ./

# 依存関係のインストール
RUN npm install

# ソースコードをコピー
COPY . .

# Angularの開発サーバー用ポート
EXPOSE 4200

# 開発用のデフォルトコマンド
CMD ["ng", "serve", "--host", "0.0.0.0", "--port", "4200"]