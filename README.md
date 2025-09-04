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
- **生成ツール**: Python 3.12.3

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
│   ├── package.json      # TypeSpec依存関係
│   ├── package-lock.json # NPMロックファイル
│   ├── tspconfig.yaml    # TypeSpecコンパイル設定
│   └── tsp/              # TypeSpec定義ファイル
│       └── main.tsp
├── generator/             # Python生成ツール
│   ├── Dockerfile        # Python生成環境用イメージ
│   ├── requirements.txt  # Python依存関係
│   ├── main.py           # メイン生成スクリプト
│   └── scripts/          # 各生成スクリプト
├── output/                # 生成ファイル出力先
│   ├── openapi/          # OpenAPI仕様書
│   ├── csv/              # テーブル定義CSV
│   ├── ddl/              # PostgreSQL DDLファイル
│   ├── backend/          # Spring Boot生成ファイル
│   └── frontend/         # Angular生成ファイル
├── frontend/              # Angularフロントエンド（将来追加予定）
├── backend/               # Spring Bootバックエンド（将来追加予定）
├── database/              # データベース関連
│   └── ddl/              # 初期化用DDLファイル
├── config/                # 生成設定
├── templates/             # Jinja2テンプレート
└── docker-compose.yml     # Docker環境設定
```

## 開発環境の起動

### 1. Docker環境の起動

```bash
# Docker Composeでコンテナを起動
docker compose up -d

# TypeSpec開発コンテナに接続
docker compose exec typespec /bin/sh
```

### 2. Python環境の準備

```bash
# Python 3.12.3依存関係のインストール（generatorコンテナ内で自動実行）
# 手動で実行する場合：
docker compose exec generator pip install -r generator/requirements.txt
```

### 3. TypeSpecからのコード生成

```bash
# 1. TypeSpecコンパイル（OpenAPI仕様書生成）
docker compose exec typespec npm run typespec:compile

# 2. 全てのコンポーネントを生成
docker compose exec generator python generator/main.py --target all

# 個別生成も可能
docker compose exec generator python generator/main.py --target csv        # CSVのみ
docker compose exec generator python generator/main.py --target ddl        # DDLのみ
docker compose exec generator python generator/main.py --target spring     # Spring Bootのみ
docker compose exec generator python generator/main.py --target angular    # Angularのみ
```

### 4. 生成されたファイルの確認

```bash
# 全ての出力ファイル
ls -la output/

# OpenAPI仕様書
ls -la output/openapi/

# CSVファイル（テーブル定義）
ls -la output/csv/

# DDLファイル
ls -la output/ddl/

# Spring Bootファイル
ls -la output/backend/

# Angularファイル
ls -la output/frontend/
```

## 使い方

### 1. TypeSpec定義の作成・編集

TypeSpecファイル（`typespec/tsp/main.tsp`）でAPIとモデルを定義します：

```bash
# TypeSpec専用コンテナに接続
docker compose exec typespec /bin/sh

# TypeSpecファイルを編集（vim、nanoなどを使用）
vi typespec/tsp/main.tsp
```

### 2. TypeSpecのコンパイル

定義を変更した後は、まずTypeSpecをOpenAPI仕様にコンパイルします：

```bash
# TypeSpec専用コンテナでコンパイル
docker compose exec typespec npm run typespec:compile
```

### 3. コード生成の実行

#### 3.1 全コンポーネントの一括生成

```bash
# Generator専用コンテナで全コンポーネント生成
docker compose exec generator python generator/main.py --target all
```

#### 3.2 段階的生成（推奨）

```bash
# 1. CSVファイル生成（テーブル定義の確認用）
docker compose exec generator python generator/main.py --target csv

# 2. CSV内容を確認
cat database/csv/table_definitions.csv

# 3. DDL生成（PostgreSQL DDL）
docker compose exec generator python generator/main.py --target ddl

# 4. Spring Boot生成（Controller、DTO、Entity）
docker compose exec generator python generator/main.py --target spring

# 5. Angular生成（TypeScript型定義、サービス）
docker compose exec generator python generator/main.py --target angular
```

#### 3.3 個別コンポーネント生成

```bash
# CSVのみ生成
docker compose exec generator python generator/main.py --target csv

# DDLのみ生成
docker compose exec generator python generator/main.py --target ddl

# Spring Bootのみ生成
docker compose exec generator python generator/main.py --target spring

# Angularのみ生成
docker compose exec generator python generator/main.py --target angular
```

### 4. 生成フローの詳細

このプロジェクトは以下のような生成フローに従います：

```
TypeSpec定義 (.tsp)
    ↓
TypeSpecコンパイル（typespecコンテナ）
    ↓
OpenAPI仕様 (output/openapi/openapi.yaml)
    ↓
CSV生成（generatorコンテナ）
    ↓
DDL生成 (output/ddl/[モデル名].sql)
    ↓
Spring Boot生成 (output/backend/)
    ↓  
Angular生成 (output/frontend/)
```

### コンテナ構成
- **typespecコンテナ**: TypeSpec → OpenAPI変換専用（Node.js 24-slim環境）
- **generatorコンテナ**: OpenAPI → 各種コード生成専用（Python 3.12.3-slim環境）
- **postgresコンテナ**: データベース環境（PostgreSQL 15-alpine）

### 5. 生成されるファイル

#### DDLファイル
- **場所**: `output/ddl/[テーブル名].sql`
- **内容**: PostgreSQL DDL、インデックス、トリガー、サンプルデータ

#### Spring Bootファイル
- **場所**: `output/backend/main/java/com/example/userapi/`
- **内容**: Controller、DTO、Entity、Repository、Service

#### Angularファイル
- **場所**: `output/frontend/app/`
- **内容**: TypeScript型定義、APIサービス、モデル

#### CSVファイル（中間生成物）
- **場所**: `output/csv/table_definitions.csv`
- **内容**: テーブル定義の詳細（カラム名、データ型、制約など）

#### OpenAPI仕様書
- **場所**: `output/openapi/openapi.yaml`
- **内容**: TypeSpecから生成されたOpenAPI 3.0仕様書

### 6. 設定のカスタマイズ

生成動作は`config/generator_config.yaml`で設定できます：

```yaml
# データベース設定
database:
  name: userdb
  extensions:
    - uuid-ossp
  create_indexes: true
  create_triggers: true
  insert_sample_data: true

# Spring Boot設定
spring:
  base_package: com.example.userapi

# Angular設定
angular:
  api_base_url: http://localhost:8080/api
```

### 7. トラブルシューティング

#### TypeSpecコンパイルエラー
```bash
# TypeSpec構文エラーを確認
docker compose exec typespec npm run typespec:compile
```

#### 生成ファイルが見つからない
```bash
# OpenAPI仕様ファイルの存在確認
ls -la output/openapi/openapi.yaml

# コンテナ状態を確認
docker compose ps

# 全ての出力ディレクトリを確認
ls -la output/
```

#### DDLでエンティティ以外のテーブルが生成される
CSVファイル（`output/csv/table_definitions.csv`）を確認し、不要なテーブル定義が含まれていないかチェックしてください。エンティティフィルタリングにより、ResponseやRequest型は自動的に除外されます。

## 成果物の削除

生成されたファイルのみを削除するためのクリーンアップコマンドです。

### 一括削除

```bash
# すべての生成ファイルを削除
rm -rf output/*
```

### 個別削除

```bash
# OpenAPI仕様書のみ削除
rm -rf output/openapi/*

# CSVファイルのみ削除  
rm -rf output/csv/*

# DDLファイルのみ削除
rm -rf output/ddl/*

# Spring Boot生成ファイルのみ削除
rm -rf output/backend/*

# Angular生成ファイルのみ削除
rm -rf output/frontend/*
```

### 段階的削除（バックアップ保持）

```bash
# バックアップファイルを保持してメインファイルのみ削除
find output/ -name "*_[0-9]*" -prune -o -type f -delete
```

### 注意事項

- 削除コマンドは**output/ディレクトリ内の生成ファイルのみ**を対象とします
- ソースファイル（TypeSpec定義、設定ファイル、テンプレートなど）は削除されません
- 削除前に重要なカスタマイズが含まれていないか確認してください
- 生成ファイルは`.gitignore`により除外されているため、通常は削除後に再生成できます
- バックアップファイル（タイムスタンプ付き）は自動生成されるため、履歴確認に使用できます
