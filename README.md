# typespec-test

TypeSpecをインプットとして、DDL、Controller、DTOを自動生成するツールプロジェクトです。

## 概要

このプロジェクトは、TypeSpec定義ファイルから以下のコンポーネントを自動生成します：

- **DDL（Data Definition Language）**: PostgreSQL用のデータベーススキーマ
- **Controller**: Spring Boot用のAPIコントローラー
- **DTO**: フロントエンド（Angular）とバックエンド（Spring Boot）用のデータ転送オブジェクト

## 技術スタック

- **フロントエンド**: Angular
- **バックエンド**: Spring Boot
- **データベース**: PostgreSQL
- **API定義**: TypeSpec
- **生成ツール**: Python

## 開発環境

### Docker環境での開発

このプロジェクトは、すべての開発作業をDockerコンテナ上で実施することを前提としています。

- TypeSpec定義の編集・コンパイル
- 各レイヤーのコード生成
- ビルドとテストの実行

すべての作業はdocker-compose.ymlで定義された環境内で行います。

## プロジェクト構造

```
typespec-test/
├── typespec/              # TypeSpec関連
│   ├── Dockerfile        # TypeSpec開発環境用イメージ
│   └── tsp/              # TypeSpec定義ファイル
│       └── main.tsp
├── frontend/              # Angularフロントエンド
│   ├── Dockerfile
│   └── src/               # 生成されたAngular DTO/サービス
├── backend/               # Spring Bootバックエンド
│   ├── Dockerfile
│   └── src/               # 生成されたController/DTO
├── database/              # データベース関連
│   ├── Dockerfile
│   └── ddl/               # 生成されたDDLファイル
├── generator/             # Python生成ツール
│   ├── main.py           # メイン生成スクリプト
│   └── scripts/          # 各生成スクリプト
├── config/                # 生成設定
├── templates/             # Jinja2テンプレート
├── temp/                  # 一時ファイル（TypeSpecコンパイル出力）
├── docker-compose.yml     # Docker環境設定
├── package.json          # TypeSpec依存関係
├── requirements.txt       # Python依存関係
└── tspconfig.yaml        # TypeSpecコンパイル設定
```

## 開発環境の起動

### 1. Docker環境の起動

```bash
# Docker Composeでコンテナを起動
docker-compose up -d

# TypeSpec開発コンテナに接続
docker-compose exec typespec-dev /bin/sh
```

### 2. Python環境の準備

```bash
# Python依存関係のインストール
npm run setup:python
```

### 3. TypeSpecからのコード生成

```bash
# 全てのコンポーネントを生成
npm run generate:all

# 個別生成も可能
npm run generate:ddl        # DDLのみ
npm run generate:backend    # Spring Bootのみ
npm run generate:frontend   # Angularのみ
```

### 4. 生成されたファイルの確認

```bash
# DDLファイル
ls -la database/ddl/

# Spring Bootファイル
ls -la backend/src/

# Angularファイル
ls -la frontend/src/
```
