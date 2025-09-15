# typespec-gen

TypeSpecを真の情報源とする、マルチAPI対応フルスタックWeb開発コード生成ツールです。

## 概要

このプロジェクトは、TypeSpec定義ファイルから以下のコンポーネントを自動生成します：

- **DDL（Data Definition Language）**: PostgreSQL用のデータベーススキーマ
- **Spring Boot Controller**: API別に分離されたRESTコントローラー
- **Spring Boot DTO**: バリデーション付きデータ転送オブジェクト
- **Angular TypeScript型定義**: インターフェースとモデル
- **Angular APIサービス**: HTTP通信用サービスクラス
- **CSV テーブル定義**: データベース設計の中間ファイル

## 🚀 現在の実装：Example API

現在は **Example API** を基盤とした実装となっています：

- `example-api` → サンプル実装とテンプレート
- カスタムデコレーター対応（バリデーション、DDL生成用）
- 将来的なマルチAPI対応への拡張が可能な設計

**注意**: `user-api`, `product-api`, `auth-api` は将来的な拡張例として、現在は `example-api` のみ実装されています。

## 技術スタック

- **API定義**: TypeSpec (.tsp files)
- **フロントエンド**: Angular with TypeScript
- **バックエンド**: Spring Boot (Java)
- **データベース**: PostgreSQL
- **生成ツール**: Python 3.12.3
- **開発環境**: Docker Compose

## プロジェクト構造

```
typespec-gen/
├── typespec/              # TypeSpec関連
│   ├── Dockerfile        # TypeSpec開発環境用イメージ
│   ├── package.json      # TypeSpec依存関係（Workspace Root）
│   ├── packages/         # TypeSpec Workspaceパッケージ
│   │   ├── models/       # 📦 モデル定義パッケージ
│   │   │   ├── example-models.tsp  # 現在実装されている例示用モデル
│   │   │   ├── user-models.tsp     # （将来拡張用）
│   │   │   ├── product-models.tsp  # （将来拡張用）
│   │   │   ├── auth-models.tsp     # （将来拡張用）
│   │   │   └── lib.tsp
│   │   ├── common/       # 📦 共通型定義
│   │   │   └── base-types.tsp
│   │   ├── decorators/   # 📦 カスタムデコレーター
│   │   │   ├── lib.tsp
│   │   │   └── lib.ts
│   │   ├── enums/        # 📦 列挙型定義
│   │   │   └── lib.tsp
│   │   └── api/          # 📦 API定義パッケージ
│   │       └── example/  # 🚀 Example API（実装済み）
│   │           ├── main.tsp        # メインAPI定義
│   │           ├── tspconfig.yaml  # TypeSpec設定
│   │           └── tsp-output/     # コンパイル出力
├── generator/             # Python生成ツール
│   ├── Dockerfile        # Python生成環境用イメージ
│   ├── requirements.txt  # Python依存関係
│   ├── main.py           # メイン生成スクリプト
│   ├── scripts/          # 各生成スクリプト
│   │   ├── csv_generator.py      # CSV生成
│   │   ├── ddl_generator.py      # DDL生成
│   │   ├── spring_generator.py   # Spring Boot生成
│   │   └── angular_generator.py  # Angular生成
│   └── templates/        # Jinja2テンプレート
│       ├── angular/      # Angular用テンプレート
│       ├── spring/       # Spring Boot用テンプレート
│       └── ddl/          # DDL用テンプレート
├── output/                # 生成ファイル出力先（gitignore対象）
│   ├── openapi/          # OpenAPI仕様書
│   │   └── example.yaml  # Example API仕様書
│   ├── csv/              # テーブル定義CSV
│   ├── ddl/              # PostgreSQL DDLファイル
│   ├── backend/          # Spring Boot生成ファイル
│   └── frontend/         # Angular生成ファイル
├── config/                # 生成設定
│   └── generator_config.yaml # ジェネレーター設定ファイル
├── web-service/           # TypeSpec Webサービス
├── web-db/               # データベース初期化
└── docker-compose.yml     # Docker環境設定
```

## 開発環境の起動

このプロジェクトは、すべての開発作業をDockerコンテナ上で実施することを前提としています。

### 1. Docker環境の起動

```bash
# Docker Composeでコンテナを起動
docker compose up -d

# TypeSpec開発コンテナに接続
docker compose exec typespec /bin/sh
```

### 2. TypeSpec依存関係の初期化

```bash
# デコレーターとenumをビルド（初回必須）
docker compose exec typespec npm run build:all

# Example APIをコンパイル
docker compose exec typespec npm run compile:example-api

# 全APIを一括コンパイル（現在はExample APIのみ）
docker compose exec typespec npm run compile:all-apis
```

## TypeSpec Workspace - 使い方ガイド

### アーキテクチャ概要

このプロジェクトは**モデル分離アーキテクチャ**を採用しています：

- **📦 Modelsパッケージ**: 全APIで共有するデータモデル定義（現在はexample-models.tsp）
- **🚀 APIパッケージ**: エンドポイント定義のみに特化（現在はexample/main.tsp）
- **🔧 共通パッケージ**: 型定義、デコレーター、列挙型

### 開発ワークフロー

#### 1. モデルを修正する場合

```bash
# 対象ファイルを編集
docker compose exec typespec vi packages/models/example-models.tsp # 例示モデル
# 将来的には以下も拡張可能：
# docker compose exec typespec vi packages/models/user-models.tsp
# docker compose exec typespec vi packages/models/product-models.tsp
# docker compose exec typespec vi packages/models/auth-models.tsp

# 影響する全APIを再コンパイル
docker compose exec typespec npm run compile:all-apis
```

#### 2. 新しいエンドポイントを追加する場合

```bash
# APIファイルを編集
docker compose exec typespec vi packages/api/example/main.tsp # Example API

# 該当APIを再コンパイル
docker compose exec typespec npm run compile:example-api
```

#### 3. 個別APIのコンパイル

```bash
# Example APIのコンパイル（デコレーター未変更の場合）
docker compose exec typespec npm run compile:example-api

# 全体ビルドとコンパイル（デコレーター変更時）
docker compose exec typespec npm run all:build-compile
```

### カスタムデコレーター（DDL生成用）の使い方

#### 基本的なDDLデコレーター

```typescript
// packages/models/example-models.tsp の例（将来拡張用）
@doc("ユーザー情報")
@MyService.DDL.makeDDL                    // DDL生成対象
@MyService.DDL.tableName("app_users")     // テーブル名指定
model User {
  @key
  id: int32;

  @MyService.DDL.length(50)               // 文字列長制約
  username: string;

  @MyService.DDL.notAddForDDL             // DDL生成から除外
  internalField?: string;
  
  ...TimestampFields;                     // 共通のタイムスタンプ
}
```

#### 利用可能なデコレーター

- `@MyService.DDL.makeDDL` - DDL生成対象としてマーク
- `@MyService.DDL.tableName("table_name")` - テーブル名指定
- `@MyService.DDL.length(50)` - 文字列長制約
- `@MyService.DDL.notAddForDDL` - DDL生成から除外
- `@MyService.DDL.checkIn(["value1", "value2"])` - CHECK制約

## コード生成の実行

### マルチAPI対応の生成フロー

```bash
# 1. Example APIをTypeSpecコンパイル（OpenAPI仕様書生成）
docker compose exec typespec npm run compile:example-api

# 2. Example APIから全てのコンポーネントを生成
docker compose exec generator python generator/main.py --target all --input output/openapi

# または個別生成
docker compose exec generator python generator/main.py --target csv --input output/openapi
docker compose exec generator python generator/main.py --target spring --input output/openapi
docker compose exec generator python generator/main.py --target angular --input output/openapi
```

### 段階的生成

```bash
# 1. CSV生成（API統合テーブル定義）
docker compose exec generator python generator/main.py --target csv --input output/openapi

# 2. CSV内容を確認（API名列付き）
cat output/csv/table_definitions.csv

# 3. DDL生成（PostgreSQL DDL）
docker compose exec generator python generator/main.py --target ddl --input output/openapi

# 4. Spring Boot生成（API別パッケージ）
docker compose exec generator python generator/main.py --target spring --input output/openapi

# 5. Angular生成（API別モジュール）
docker compose exec generator python generator/main.py --target angular --input output/openapi
```

### レガシーモード生成

```bash
# 統合TypeSpecコンパイル（単一OpenAPI仕様書生成）
docker compose exec typespec npm run typespec:compile

# レガシーモードでコンポーネント生成
docker compose exec generator python generator/main.py --target all --legacy-mode
```

## 生成されるファイル

### OpenAPI仕様書
- **場所**: `output/openapi/example.yaml`
- **内容**: Example APIのOpenAPI 3.0仕様書

### Spring Bootファイル
- **場所**: `output/backend/src/main/java/com/example/api/`
- **内容**: ExampleController、DTO（バリデーション付き）

### Angularファイル
- **場所**: `output/frontend/app/` (models/, services/)
- **内容**: TypeScript型定義、HTTPサービス

### CSVファイル（テーブル定義）
- **場所**: `output/csv/table_definitions.csv`
- **内容**: テーブル定群（例：`example,example_table,id,SERIAL PRIMARY KEY...`）

### DDLファイル
- **場所**: `output/ddl/[テーブル名].sql`
- **内容**: PostgreSQL DDL、インデックス、トリガー、サンプルデータ

## 設定のカスタマイズ

生成動作は`config/generator_config.yaml`で設定できます：

```yaml
# グローバル設定
global:
  output_base: output/

# デフォルトSpring Boot設定
spring:
  base_package: com.example.userapi
  controller_package: controller
  dto_package: dto

# デフォルトAngular設定  
angular:
  api_base_url: http://localhost:8080/api
  models_dir: app/models
  services_dir: app/services

# API別設定（マルチAPI対応）
apis:
  user:
    input_file: user-api.yaml
    spring:
      base_package: com.example.user.userapi
    angular:
      module_name: user
      api_base_url: http://localhost:8080/api/user
      
  product:
    input_file: product-api.yaml
    spring:
      base_package: com.example.user.productapi
    angular:
      module_name: product
      api_base_url: http://localhost:8080/api/product
      
  auth:
    input_file: auth-api.yaml
    spring:
      base_package: com.example.user.authapi
    angular:
      module_name: auth
      api_base_url: http://localhost:8080/api/auth

# データベース設定
database:
  name: userdb
  extensions:
    - uuid-ossp
  create_indexes: true
  create_triggers: true
  insert_sample_data: true
```

## トラブルシューティング

### TypeSpecコンパイルエラー

```bash
# Example APIのコンパイルエラー確認
docker compose exec typespec npm run compile:example-api

# 全APIコンパイルエラー確認
docker compose exec typespec npm run compile:all-apis
```

### 生成ファイルが見つからない

```bash
# Example API：OpenAPI仕様ファイルの存在確認
ls -la output/openapi/
# → example.yaml があるか確認

# コンテナ状態を確認
docker compose ps

# 全ての出力ディレクトリを確認
ls -la output/
```

### マルチAPI生成エラー

```bash
# Example API生成でエラーが発生した場合
docker compose exec generator python generator/main.py --target csv --input output/openapi

# 単一ファイル指定で生成テスト
docker compose exec generator python generator/main.py --target spring --input output/openapi/example.yaml
```

### モデルが見つからない場合

- `packages/models/lib.tsp`に適切にモデルがimportされているか確認
- APIファイル（`packages/api/example/main.tsp`）でデコレーターがimportされているか確認
- 名前空間（`namespace Example`）が正しく宣言されているか確認

### 生成ファイルのクリーンアップ

```bash
# 生成されたファイルを削除
rm -rf output/openapi/*

# 再生成
docker compose exec typespec npm run compile:example-api
```

## 🗑️ 成果物の削除

### 一括削除

```bash
# すべての生成ファイルを削除（マルチAPI対応）
rm -rf output/*
```

### 個別削除

```bash
# OpenAPI仕様書のみ削除
rm -rf output/openapi/*.yaml

# CSVファイルのみ削除  
rm -rf output/csv/*

# DDLファイルのみ削除
rm -rf output/ddl/*

# Spring Boot生成ファイルのみ削除
rm -rf output/backend/*

# Angular生成ファイルのみ削除
rm -rf output/frontend/*
```

### Example API関連ファイルの削除

```bash
# Example APIの生成ファイルのみ削除
rm -f output/openapi/example.yaml
rm -rf output/backend/src/main/java/com/example/api/
rm -rf output/frontend/app/
```

## 🎯 まとめ

このツールにより、TypeSpecを真の情報源としたフルスタック開発が実現されます：

✅ **コード生成**: TypeSpec定義からSpring Boot/Angular/DDLを自動生成  
✅ **バリデーション対応**: カスタムデコレーターで高度なバリデーション  
✅ **Docker統合**: 開発環境からコード生成まで一元管理  
✅ **拡張性**: 将来的なマルチAPI対応への拡張が可能  
✅ **一貫性**: API定義からフロントエンドまでの一貫した型安全性

TypeSpecを真の情報源として、一貫性のあるフルスタックアプリケーションの開発を効率化できます。