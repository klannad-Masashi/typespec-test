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
npm run generate:csv        # CSVのみ
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

## 使い方

### 1. TypeSpec定義の作成・編集

TypeSpecファイル（`typespec/tsp/main.tsp`）でAPIとモデルを定義します：

```bash
# TypeSpec開発コンテナに接続
docker-compose exec typespec-dev /bin/sh

# TypeSpecファイルを編集（vim、nanoなどを使用）
vi typespec/tsp/main.tsp
```

### 2. TypeSpecのコンパイル

定義を変更した後は、まずTypeSpecをOpenAPI仕様にコンパイルします：

```bash
# TypeSpecをコンパイル（OpenAPI仕様を生成）
npm run typespec:compile
```

### 3. コード生成の実行

#### 3.1 全コンポーネントの一括生成

```bash
# すべて（CSV→DDL→Spring Boot→Angular）を生成
python generator/main.py --target all
```

#### 3.2 段階的生成（推奨）

```bash
# 1. CSVファイル生成（テーブル定義の確認用）
python generator/main.py --target csv

# 2. CSV内容を確認
cat database/csv/table_definitions.csv

# 3. DDL生成（PostgreSQL DDL）
python generator/main.py --target ddl

# 4. Spring Boot生成（Controller、DTO、Entity）
python generator/main.py --target spring

# 5. Angular生成（TypeScript型定義、サービス）
python generator/main.py --target angular
```

#### 3.3 個別コンポーネント生成

```bash
# CSVのみ生成
python generator/main.py --target csv

# DDLのみ生成
python generator/main.py --target ddl

# Spring Bootのみ生成
python generator/main.py --target spring

# Angularのみ生成
python generator/main.py --target angular
```

### 4. 生成フローの詳細

このプロジェクトは以下のような生成フローに従います：

```
TypeSpec定義 (.tsp)
    ↓
TypeSpecコンパイル
    ↓
OpenAPI仕様 (temp/openapi/openapi.yaml)
    ↓
CSV生成 (database/csv/table_definitions.csv)
    ↓
DDL生成 (database/ddl/[モデル名].sql)
    ↓
Spring Boot生成 (backend/src/)
    ↓  
Angular生成 (frontend/src/)
```

### 5. 生成されるファイル

#### DDLファイル
- **場所**: `database/ddl/[テーブル名].sql`
- **内容**: PostgreSQL DDL、インデックス、トリガー、サンプルデータ

#### Spring Bootファイル
- **場所**: `backend/src/main/java/com/example/userapi/`
- **内容**: Controller、DTO、Entity、Repository、Service

#### Angularファイル
- **場所**: `frontend/src/app/`
- **内容**: TypeScript型定義、APIサービス、モデル

#### CSVファイル（中間生成物）
- **場所**: `database/csv/table_definitions.csv`
- **内容**: テーブル定義の詳細（カラム名、データ型、制約など）

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
npm run typespec:compile
```

#### 生成ファイルが見つからない
```bash
# OpenAPI仕様ファイルの存在確認
ls -la temp/openapi/openapi.yaml
```

#### DDLでエンティティ以外のテーブルが生成される
CSVファイル（`database/csv/table_definitions.csv`）を確認し、不要なテーブル定義が含まれていないかチェックしてください。エンティティフィルタリングにより、ResponseやRequest型は自動的に除外されます。
