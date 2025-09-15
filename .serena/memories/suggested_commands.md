# 開発コマンド一覧

## Docker環境の起動・管理
```bash
# Docker Composeでコンテナを起動
docker compose up -d

# TypeSpec開発コンテナに接続
docker compose exec typespec /bin/sh

# Python Generator環境に接続
docker compose exec generator /bin/bash
```

## TypeSpec関連コマンド
```bash
# デコレーターとenumをビルド（初回必須）
docker compose exec typespec npm run build:all

# 全APIを一括コンパイル
docker compose exec typespec npm run typespec:compile-all

# 個別APIコンパイル
docker compose exec typespec npm run typespec:compile-user
docker compose exec typespec npm run typespec:compile-product
docker compose exec typespec npm run typespec:compile-auth
```

## コード生成コマンド
```bash
# マルチAPIから全コンポーネント生成
docker compose exec generator python generator/main.py --target all --input output/openapi

# 個別生成
docker compose exec generator python generator/main.py --target csv --input output/openapi
docker compose exec generator python generator/main.py --target spring --input output/openapi
docker compose exec generator python generator/main.py --target angular --input output/openapi
docker compose exec generator python generator/main.py --target ddl --input output/openapi
```

## Python開発コマンド（generator内）
```bash
# リント実行
docker compose exec generator flake8 generator/

# コードフォーマット
docker compose exec generator black generator/

# テスト実行
docker compose exec generator pytest generator/
```

## ファイル削除・クリーンアップ
```bash
# 生成ファイル一括削除
rm -rf output/*

# OpenAPI仕様書のみ削除
rm -rf output/openapi/*.yaml

# 個別削除
rm -rf output/csv/*
rm -rf output/ddl/*
rm -rf output/backend/*
rm -rf output/frontend/*
```