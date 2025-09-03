# Spring Boot バックエンド開発環境
FROM openjdk:17-jdk-slim

# 作業ディレクトリの設定
WORKDIR /app

# 必要なパッケージのインストール
RUN apt-get update && apt-get install -y \
    curl \
    git \
    maven \
    && rm -rf /var/lib/apt/lists/*

# Mavenの設定（キャッシュ用）
COPY pom.xml ./
RUN mvn dependency:go-offline -B

# ソースコードをコピー
COPY . .

# Spring Bootアプリケーション用ポート
EXPOSE 8080

# 開発用のデフォルトコマンド
CMD ["mvn", "spring-boot:run"]