# TypeSpec開発環境用のDockerファイル
FROM node:18-alpine

# 作業ディレクトリの設定
WORKDIR /app

# 必要なツールのインストール（Python環境を追加）
RUN apk add --no-cache \
    git \
    curl \
    python3 \
    py3-pip \
    && npm install -g @typespec/compiler

# package.jsonとpackage-lock.jsonをコピー
COPY package*.json ./

# Node.js依存関係のインストール
RUN npm install

# requirements.txtをコピーしてPython依存関係をインストール
COPY requirements.txt ./
RUN pip3 install --break-system-packages -r requirements.txt

# ソースコードをコピー
COPY . .

# ポート番号の設定（開発用）
EXPOSE 8080 4200

# 開発用のエントリーポイント
CMD ["npm", "run", "generate:all"]