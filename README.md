# typespec-test

TypeSpecを真の情報源とする、マルチAPI対応フルスタックWeb開発コード生成ツールです。

## 概要

このプロジェクトは、TypeSpec定義ファイルから以下のコンポーネントを自動生成します：

- **DDL（Data Definition Language）**: PostgreSQL用のデータベーススキーマ
- **Spring Boot Controller**: API別に分離されたRESTコントローラー
- **Spring Boot DTO**: バリデーション付きデータ転送オブジェクト
- **Angular TypeScript型定義**: インターフェースとモデル
- **Angular APIサービス**: HTTP通信用サービスクラス
- **CSV テーブル定義**: データベース設計の中間ファイル

## 🚀 新機能：マルチAPI対応

**1API = 1TypeSpecファイル**アーキテクチャをサポート。以下の構造でAPIを分離管理できます：

- `user-api.tsp` → User管理API
- `product-api.tsp` → 商品管理API  
- `auth-api.tsp` → 認証API

各APIは独立したパッケージ・モジュール構造で生成され、スケーラブルな開発が可能です。

## 技術スタック

- **API定義**: TypeSpec (.tsp files)
- **フロントエンド**: Angular with TypeScript
- **バックエンド**: Spring Boot (Java)
- **データベース**: PostgreSQL
- **生成ツール**: Python 3.12.3
- **開発環境**: Docker Compose

## プロジェクト構造

```
typespec-test/
├── typespec/              # TypeSpec関連
│   ├── Dockerfile        # TypeSpec開発環境用イメージ
│   ├── package.json      # TypeSpec依存関係（Workspace Root）
│   ├── packages/         # TypeSpec Workspaceパッケージ
│   │   ├── models/       # 📦 モデル定義パッケージ
│   │   │   ├── user-models.tsp
│   │   │   ├── product-models.tsp
│   │   │   ├── auth-models.tsp
│   │   │   └── lib.tsp
│   │   ├── common/       # 📦 共通型定義
│   │   │   └── base-types.tsp
│   │   ├── decorators/   # 📦 カスタムデコレーター
│   │   │   ├── lib.tsp
│   │   │   └── lib.ts
│   │   ├── enums/        # 📦 列挙型定義
│   │   │   └── lib.tsp
│   │   ├── user-api/     # 🚀 ユーザーAPI（エンドポイントのみ）
│   │   │   └── user-api.tsp
│   │   ├── product-api/  # 🚀 商品API（エンドポイントのみ）
│   │   │   └── product-api.tsp
│   │   └── auth-api/     # 🚀 認証API（エンドポイントのみ）
│   │       └── auth-api.tsp
├── generator/             # Python生成ツール（マルチAPI対応）
│   ├── Dockerfile        # Python生成環境用イメージ
│   ├── requirements.txt  # Python依存関係
│   ├── main.py           # メイン生成スクリプト（マルチ入力対応）
│   ├── scripts/          # 各生成スクリプト
│   │   ├── csv_generator.py      # マルチAPI対応済み
│   │   ├── ddl_generator.py      # DDL生成
│   │   ├── spring_generator.py   # マルチAPI対応済み
│   │   └── angular_generator.py  # マルチAPI対応済み
│   └── templates/        # Jinja2テンプレート
│       ├── angular/      # Angular用テンプレート
│       ├── spring/       # Spring Boot用テンプレート
│       └── ddl/          # DDL用テンプレート
├── output/                # 生成ファイル出力先
│   ├── openapi/          # OpenAPI仕様書（API別）
│   │   ├── user-api.yaml
│   │   ├── product-api.yaml
│   │   └── auth-api.yaml
│   ├── csv/              # テーブル定義CSV（API統合）
│   ├── ddl/              # PostgreSQL DDLファイル
│   ├── backend/          # Spring Boot生成ファイル（API別パッケージ）
│   │   └── main/java/com/example/
│   │       ├── userapi/
│   │       ├── productapi/
│   │       └── authapi/
│   └── frontend/         # Angular生成ファイル（API別モジュール）
│       └── app/
│           ├── user/
│           ├── product/
│           └── auth/
├── config/                # 生成設定
│   └── generator_config.yaml # ジェネレーター設定ファイル
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

# 全APIを一括コンパイル
docker compose exec typespec npm run typespec:compile-all
```

## TypeSpec Workspace - 使い方ガイド

### アーキテクチャ概要

このプロジェクトは**モデル分離アーキテクチャ**を採用しています：

- **📦 Modelsパッケージ**: 全APIで共有するデータモデル定義
- **🚀 APIパッケージ**: エンドポイント定義のみに特化
- **🔧 共通パッケージ**: 型定義、デコレーター、列挙型

### 開発ワークフロー

#### 1. モデルを修正する場合

```bash
# 対象ファイルを編集
docker compose exec typespec vi packages/models/user-models.tsp    # ユーザー関連モデル
docker compose exec typespec vi packages/models/product-models.tsp # 商品関連モデル
docker compose exec typespec vi packages/models/auth-models.tsp    # 認証関連モデル

# 影響する全APIを再コンパイル
docker compose exec typespec npm run typespec:compile-all
```

#### 2. 新しいエンドポイントを追加する場合

```bash
# APIファイルを編集
docker compose exec typespec vi packages/user-api/user-api.tsp     # ユーザーAPI
docker compose exec typespec vi packages/product-api/product-api.tsp # 商品API
docker compose exec typespec vi packages/auth-api/auth-api.tsp      # 認証API

# 該当APIを再コンパイル
docker compose exec typespec npm run typespec:compile-user  # 編集したAPIのみ
```

#### 3. 個別APIのコンパイル

```bash
# 個別コンパイル（デコレーター未変更の場合）
docker compose exec typespec npm run typespec:compile-user      # ユーザーAPI
docker compose exec typespec npm run typespec:compile-product   # 商品API
docker compose exec typespec npm run typespec:compile-auth      # 認証API
```

### カスタムデコレーター（DDL生成用）の使い方

#### 基本的なDDLデコレーター

```typescript
// packages/models/user-models.tsp の例
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
# 1. 各API別にTypeSpecコンパイル（個別OpenAPI仕様書生成）
docker compose exec typespec npm run typespec:compile-all

# 2. マルチAPIから全てのコンポーネントを生成
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

### OpenAPI仕様書（API別）
- **場所**: `output/openapi/user-api.yaml`, `output/openapi/product-api.yaml`, `output/openapi/auth-api.yaml`
- **内容**: 各APIに特化したOpenAPI 3.0仕様書

### Spring Bootファイル（API別パッケージ）
- **場所**: `output/backend/main/java/com/example/user/{userapi,productapi,authapi}/`
- **内容**: API別Controller、DTO（バリデーション付き）

### Angularファイル（API別モジュール）
- **場所**: `output/frontend/app/{user,product,auth}/` (models/, services/)
- **内容**: API別TypeScript型定義、HTTPサービス

### CSVファイル（API統合テーブル定義）
- **場所**: `output/csv/table_definitions.csv`
- **内容**: API名列付きテーブル定義（例：`user,users,id,SERIAL PRIMARY KEY...`）

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
# マルチAPI構文エラーを確認
docker compose exec typespec npm run typespec:compile-all

# 個別APIのコンパイルエラー確認
docker compose exec typespec npm run typespec:compile-user
docker compose exec typespec npm run typespec:compile-product  
docker compose exec typespec npm run typespec:compile-auth
```

### 生成ファイルが見つからない

```bash
# マルチAPI：各OpenAPI仕様ファイルの存在確認
ls -la output/openapi/
# → user-api.yaml, product-api.yaml, auth-api.yaml があるか確認

# コンテナ状態を確認
docker compose ps

# 全ての出力ディレクトリを確認
ls -la output/
```

### マルチAPI生成エラー

```bash
# マルチAPI生成でエラーが発生した場合
docker compose exec generator python generator/main.py --target csv --input output/openapi

# 個別API生成テスト
docker compose exec generator python generator/main.py --target spring --input output/openapi/user-api.yaml
```

### モデルが見つからない場合

- `packages/models/lib.tsp`に適切にimportされているか確認
- APIファイルで`import "@typespec-test/models"`されているか確認
- `using UserModels;`（または適切な名前空間）が宣言されているか確認

### 生成ファイルのクリーンアップ

```bash
# 生成されたファイルを削除
rm -rf output/openapi/*

# 再生成
docker compose exec typespec npm run typespec:compile-all
```

## 🗑️ 成果物の削除

### 一括削除

```bash
# すべての生成ファイルを削除（マルチAPI対応）
rm -rf output/*
```

### 個別削除

```bash
# マルチAPI OpenAPI仕様書のみ削除
rm -rf output/openapi/*.yaml

# API統合CSVファイルのみ削除  
rm -rf output/csv/*

# DDLファイルのみ削除
rm -rf output/ddl/*

# API別Spring Boot生成ファイルのみ削除
rm -rf output/backend/*

# API別Angular生成ファイルのみ削除
rm -rf output/frontend/app/user
rm -rf output/frontend/app/product  
rm -rf output/frontend/app/auth
```

### API別個別削除

```bash
# 特定APIの生成ファイルのみ削除
rm -f output/openapi/user-api.yaml
rm -rf output/backend/main/java/com/example/user/userapi
rm -rf output/frontend/app/user
```

## 🎯 まとめ

このツールにより、**1API = 1TypeSpecファイル**アーキテクチャに基づいた、スケーラブルなフルスタック開発が実現されます：

✅ **API分離**: 各APIを独立したTypeSpecファイルで定義  
✅ **パッケージ分離**: Spring BootでAPI別パッケージ構造  
✅ **モジュール分離**: AngularでAPI別モジュール構造  
✅ **データベース統合**: 複数APIのテーブル定義を統合管理  
✅ **レガシー互換**: 従来の単一API方式もサポート

TypeSpecを真の情報源として、一貫性のあるフルスタックアプリケーションの開発を効率化できます。