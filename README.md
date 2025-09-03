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
# Python 3.12.3依存関係のインストール（generatorコンテナ内で自動実行）
# 手動で実行する場合：
docker-compose exec generator pip install -r requirements.txt
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

# 成果物削除も可能
npm run clean:all           # すべての生成ファイル削除
npm run clean:ddl           # DDLファイルのみ削除
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
# TypeSpec専用コンテナに接続
docker-compose exec typespec /bin/sh

# TypeSpecファイルを編集（vim、nanoなどを使用）
vi typespec/tsp/main.tsp
```

### 2. TypeSpecのコンパイル

定義を変更した後は、まずTypeSpecをOpenAPI仕様にコンパイルします：

```bash
# TypeSpec専用コンテナでコンパイル
docker-compose exec typespec npm run typespec:compile
```

### 3. コード生成の実行

#### 3.1 全コンポーネントの一括生成

```bash
# Generator専用コンテナで全コンポーネント生成
docker-compose exec generator python generator/main.py --target all
```

#### 3.2 段階的生成（推奨）

```bash
# 1. CSVファイル生成（テーブル定義の確認用）
docker-compose exec generator python generator/main.py --target csv

# 2. CSV内容を確認
cat database/csv/table_definitions.csv

# 3. DDL生成（PostgreSQL DDL）
docker-compose exec generator python generator/main.py --target ddl

# 4. Spring Boot生成（Controller、DTO、Entity）
docker-compose exec generator python generator/main.py --target spring

# 5. Angular生成（TypeScript型定義、サービス）
docker-compose exec generator python generator/main.py --target angular
```

#### 3.3 個別コンポーネント生成

```bash
# CSVのみ生成
docker-compose exec generator python generator/main.py --target csv

# DDLのみ生成
docker-compose exec generator python generator/main.py --target ddl

# Spring Bootのみ生成
docker-compose exec generator python generator/main.py --target spring

# Angularのみ生成
docker-compose exec generator python generator/main.py --target angular
```

### 4. 生成フローの詳細

このプロジェクトは以下のような生成フローに従います：

```
TypeSpec定義 (.tsp)
    ↓
TypeSpecコンパイル（typespecコンテナ）
    ↓
OpenAPI仕様 (temp/openapi/openapi.yaml)
    ↓
CSV生成（generatorコンテナ）
    ↓
DDL生成 (database/ddl/[モデル名].sql)
    ↓
Spring Boot生成 (backend/src/)
    ↓  
Angular生成 (frontend/src/)
```

### コンテナ構成
- **typespecコンテナ**: TypeSpec → OpenAPI変換専用（Node.js 18環境）
- **generatorコンテナ**: OpenAPI → 各種コード生成専用（Python 3.12.3環境）
- **postgresコンテナ**: データベース環境（PostgreSQL 15）

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
docker-compose exec typespec npm run typespec:compile
```

#### 生成ファイルが見つからない
```bash
# OpenAPI仕様ファイルの存在確認
ls -la temp/openapi/openapi.yaml

# コンテナ状態を確認
docker-compose ps
```

#### DDLでエンティティ以外のテーブルが生成される
CSVファイル（`database/csv/table_definitions.csv`）を確認し、不要なテーブル定義が含まれていないかチェックしてください。エンティティフィルタリングにより、ResponseやRequest型は自動的に除外されます。

## 成果物の削除

生成されたファイルのみを削除するためのクリーンアップコマンドです。

### 一括削除

```bash
# すべての生成ファイルを削除
npm run clean:all
```

### 個別削除

```bash
# 一時ファイル（OpenAPI仕様書）のみ削除
npm run clean:temp

# CSVファイルのみ削除  
npm run clean:csv

# DDLファイルのみ削除
npm run clean:ddl

# Spring Boot生成ファイルのみ削除
npm run clean:backend

# Angular生成ファイルのみ削除
npm run clean:frontend
```

### 手動削除（参考）

npmスクリプトを使わない場合は、以下のコマンドで個別削除できます：

```bash
# 一時ファイル削除
rm -rf temp/openapi/*

# CSVファイル削除
rm -rf database/csv/*

# DDLファイル削除  
rm -f database/ddl/*.sql

# Spring Boot生成ファイル削除
rm -rf backend/src/main/java/com/example/userapi/controller/
rm -rf backend/src/main/java/com/example/userapi/dto/
rm -rf backend/src/main/java/com/example/userapi/entity/
rm -rf backend/src/main/java/com/example/userapi/repository/
rm -rf backend/src/main/java/com/example/userapi/service/

# Angular生成ファイル削除
rm -rf frontend/src/app/models/
rm -rf frontend/src/app/services/
```

### 注意事項

- 削除コマンドは**生成ファイルのみ**を対象とします
- ソースファイル（TypeSpec定義、設定ファイル、テンプレートなど）は削除されません
- 削除前に重要なカスタマイズが含まれていないか確認してください
- Git管理下のファイルは`.gitignore`により除外されているため、通常は削除後に再生成できます
