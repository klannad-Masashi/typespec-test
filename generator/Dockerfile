# Python Generator専用のDockerファイル
FROM python:3.12.3-slim

# 作業ディレクトリの設定
WORKDIR /app

# 必要なツールのインストール
RUN apt-get update && apt-get install -y \
    git \
    curl \
    && rm -rf /var/lib/apt/lists/*

# requirements.txtをコピーしてPython依存関係をインストール
COPY generator/requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

# generatorコードとconfigをコピー
COPY generator/ ./generator/
COPY config/ ./config/
COPY templates/ ./templates/

# 開発用のエントリーポイント
CMD ["python", "generator/main.py", "--help"]