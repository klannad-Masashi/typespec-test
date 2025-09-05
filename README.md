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

## TypeSpec Workspace - 使い方ガイド

### アーキテクチャ概要

このプロジェクトは**モデル分離アーキテクチャ**を採用しています：

- **📦 Modelsパッケージ**: 全APIで共有するデータモデル定義
- **🚀 APIパッケージ**: エンドポイント定義のみに特化
- **🔧 共通パッケージ**: 型定義、デコレーター、列挙型

### 基本的な使い方

#### 1. 環境起動
```bash
# Docker環境を起動
docker compose up -d

# TypeSpecコンテナに接続
docker compose exec typespec /bin/sh
```

#### 2. 全体ビルド
```bash
# デコレーターとenumをビルド（初回必須）
npm run build:all

# 全APIを一括コンパイル
npm run typespec:compile-all
```

#### 3. 個別APIのコンパイル
```bash
# 個別コンパイル（デコレーター未変更の場合）
npm run typespec:compile-user      # ユーザーAPI
npm run typespec:compile-product   # 商品API
npm run typespec:compile-auth      # 認証API
```

### 開発ワークフロー

#### モデルを修正する場合

1. **対象ファイルを編集**:
   ```bash
   vi packages/models/user-models.tsp    # ユーザー関連モデル
   vi packages/models/product-models.tsp # 商品関連モデル
   vi packages/models/auth-models.tsp    # 認証関連モデル
   ```

2. **影響する全APIを再コンパイル**:
   ```bash
   # 例：ユーザーモデルを変更した場合
   npm run typespec:compile-user
   
   # または全体を再コンパイル
   npm run typespec:compile-all
   ```

#### 新しいエンドポイントを追加する場合

1. **APIファイルを編集**:
   ```bash
   vi packages/user-api/user-api.tsp     # ユーザーAPI
   vi packages/product-api/product-api.tsp # 商品API
   vi packages/auth-api/auth-api.tsp      # 認証API
   ```

2. **該当APIを再コンパイル**:
   ```bash
   npm run typespec:compile-user  # 編集したAPIのみ
   ```

#### 新しいモデルを追加する場合

1. **適切なモデルファイルに追加**:
   ```typescript
   // packages/models/user-models.tsp の例
   @doc("新しいユーザー関連モデル")
   model NewUserModel {
     @key
     id: int32;
     
     @doc("説明")
     description: string;
   }
   ```

2. **APIファイルでモデルを使用**:
   ```typescript
   // packages/user-api/user-api.tsp の例
   @doc("新エンドポイント")
   @get
   op getNewUserData(): NewUserModel | ErrorResponse;
   ```

3. **再コンパイル**:
   ```bash
   npm run typespec:compile-user
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

### ビルド要件について

**重要**: `npm run build:all`の実行タイミング

```bash
# ✅ 効率的な実行方法
npm run typespec:compile-all  # build:all → 全API（推奨）

# ✅ デコレーター変更後の個別実行
npm run build:decorators && npm run typespec:compile-user

# ❌ 非効率な実行（decoratorsが重複ビルドされる）
npm run typespec:compile-user   # build実行
npm run typespec:compile-product # build実行（重複）
npm run typespec:compile-auth    # build実行（重複）
```

### 生成されるファイル

#### OpenAPI仕様書
```bash
ls output/openapi/
# user-api.yaml     - ユーザー管理API仕様書
# product-api.yaml  - 商品管理API仕様書  
# auth-api.yaml     - 認証API仕様書
```

#### 名前空間による参照
生成されたOpenAPI仕様書では、モデルは名前空間付きで参照されます：
- `UserModels.User`
- `UserModels.CreateUserRequest`
- `ProductModels.Product`
- `AuthModels.LoginRequest`

### トラブルシューティング

#### コンパイルエラーが発生した場合
```bash
# 1. 依存関係をビルド
npm run build:all

# 2. 個別にコンパイルしてエラーを特定
npm run typespec:compile-user
npm run typespec:compile-product
npm run typespec:compile-auth
```

#### モデルが見つからない場合
- `packages/models/lib.tsp`に適切にimportされているか確認
- APIファイルで`import "@typespec-test/models"`されているか確認
- `using UserModels;`（または適切な名前空間）が宣言されているか確認

#### 生成ファイルのクリーンアップ
```bash
# 生成されたファイルを削除
rm -rf output/openapi/*

# 再生成
npm run typespec:compile-all
```

### 拡張方法

#### 新しいAPIパッケージを追加
1. `packages/new-api/`ディレクトリ作成
2. `package.json`と`new-api.tsp`作成
3. ルートの`package.json`にコンパイルスクリプト追加
4. 必要に応じて`packages/models/`に新しいモデルファイル追加

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

#### 🆕 マルチAPIモード（推奨）

```bash
# 1. 各API別にTypeSpecコンパイル（個別OpenAPI仕様書生成）
docker compose exec typespec npm run typespec:compile-separate

# 2. マルチAPIから全てのコンポーネントを生成
docker compose exec generator python generator/main.py --target all --input output/openapi

# 個別生成も可能
docker compose exec generator python generator/main.py --target csv --input output/openapi
docker compose exec generator python generator/main.py --target spring --input output/openapi
docker compose exec generator python generator/main.py --target angular --input output/openapi
```

#### 📋 レガシーモード（単一API）

```bash
# 1. 統合TypeSpecコンパイル（単一OpenAPI仕様書生成）
docker compose exec typespec npm run typespec:compile

# 2. レガシーモードでコンポーネント生成
docker compose exec generator python generator/main.py --target all --legacy-mode
```

### 4. 生成されたファイルの確認

```bash
# 全ての出力ファイル
ls -la output/

# マルチAPI対応：各API別OpenAPI仕様書
ls -la output/openapi/
# → user-api.yaml, product-api.yaml, auth-api.yaml

# CSVファイル（API統合テーブル定義）
ls -la output/csv/
# → API名付きテーブル定義CSV

# Spring Bootファイル（API別パッケージ）
find output/backend -name "*.java"
# → userapi/, productapi/, authapi/ 別パッケージ

# Angularファイル（API別モジュール）
find output/frontend -name "*.ts"
# → user/, product/, auth/ 別モジュール
```

## 🔧 使い方

### 1. マルチAPI TypeSpec定義の作成・編集

各APIを独立したファイルで定義します：

```bash
# TypeSpec専用コンテナに接続
docker compose exec typespec /bin/sh

# API別TypeSpecファイルを編集
vi typespec/tsp/apis/user-api.tsp      # ユーザー管理API
vi typespec/tsp/apis/product-api.tsp   # 商品管理API  
vi typespec/tsp/apis/auth-api.tsp      # 認証API

# 共通型定義を編集
vi typespec/tsp/common/base-types.tsp  # エラー型、ページネーション等
```

### 2. TypeSpecのコンパイル

#### マルチAPIコンパイル（推奨）

```bash
# 各API別に個別コンパイル
docker compose exec typespec npm run typespec:compile-separate
```

#### 統合コンパイル（従来方式）

```bash
# 全API統合で単一OpenAPI仕様書生成
docker compose exec typespec npm run typespec:compile
```

### 3. コード生成の実行

#### 3.1 マルチAPI 全コンポーネントの一括生成（推奨）

```bash
# マルチAPIモードで全コンポーネント生成
docker compose exec generator python generator/main.py --target all --input output/openapi
```

#### 3.2 マルチAPI 段階的生成

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

#### 3.3 レガシーモード生成

```bash
# 従来の単一API生成
docker compose exec generator python generator/main.py --target all --legacy-mode

# または個別指定
docker compose exec generator python generator/main.py --target spring --input output/openapi/openapi.yaml
```

### 4. 生成フローの詳細

#### 🆕 マルチAPI生成フロー（推奨）

```
TypeSpec定義 (.tsp)
├── apis/user-api.tsp
├── apis/product-api.tsp  
└── apis/auth-api.tsp
    ↓
TypeSpecコンパイル（各API別）
    ↓
OpenAPI仕様 (API別)
├── output/openapi/user-api.yaml
├── output/openapi/product-api.yaml
└── output/openapi/auth-api.yaml
    ↓
マルチAPI対応生成（generatorコンテナ）
    ↓
├── CSV生成 (API統合テーブル定義)
├── DDL生成 (output/ddl/[テーブル名].sql)  
├── Spring Boot生成 (API別パッケージ)
│   ├── userapi/
│   ├── productapi/
│   └── authapi/
└── Angular生成 (API別モジュール)
    ├── user/
    ├── product/
    └── auth/
```

#### 📋 レガシー生成フロー

```
TypeSpec定義 (main.tsp) → OpenAPI仕様 (単一) → 各種コード生成
```

### コンテナ構成
- **typespecコンテナ**: TypeSpec → OpenAPI変換専用（Node.js 24-slim環境）
- **generatorコンテナ**: OpenAPI → 各種コード生成専用（Python 3.12.3-slim環境）
- **postgresコンテナ**: データベース環境（PostgreSQL 15-alpine）

### 5. 生成されるファイル

#### 🆕 マルチAPI対応の生成ファイル

#### OpenAPI仕様書（API別）
- **場所**: 
  - `output/openapi/user-api.yaml`
  - `output/openapi/product-api.yaml` 
  - `output/openapi/auth-api.yaml`
- **内容**: 各APIに特化したOpenAPI 3.0仕様書

#### Spring Bootファイル（API別パッケージ）
- **場所**: 
  - `output/backend/main/java/com/example/user/userapi/`
  - `output/backend/main/java/com/example/user/productapi/`
  - `output/backend/main/java/com/example/user/authapi/`
- **内容**: API別Controller、DTO（バリデーション付き）

#### Angularファイル（API別モジュール）
- **場所**:
  - `output/frontend/app/user/` (models/, services/)
  - `output/frontend/app/product/` (models/, services/)
  - `output/frontend/app/auth/` (models/, services/)
- **内容**: API別TypeScript型定義、HTTPサービス

#### CSVファイル（API統合テーブル定義）
- **場所**: `output/csv/table_definitions.csv`
- **内容**: API名列付きテーブル定義（例：`user,users,id,SERIAL PRIMARY KEY...`）

#### DDLファイル
- **場所**: `output/ddl/[テーブル名].sql`
- **内容**: PostgreSQL DDL、インデックス、トリガー、サンプルデータ

#### 📊 生成統計例
- **User API**: 7モデル, 5エンドポイント
- **Product API**: 10モデル, 7エンドポイント
- **Auth API**: 16モデル, 8エンドポイント
- **データベース**: 3テーブル（users, products, authusers）

### 6. 設定のカスタマイズ

#### 🆕 マルチAPI対応設定

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

# 🆕 API別設定（マルチAPI対応）
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

### 7. トラブルシューティング

#### TypeSpecコンパイルエラー

```bash
# マルチAPI構文エラーを確認
docker compose exec typespec npm run typespec:compile-separate

# 個別APIのコンパイルエラー確認
docker compose exec typespec npm run typespec:compile-user
docker compose exec typespec npm run typespec:compile-product  
docker compose exec typespec npm run typespec:compile-auth

# 統合コンパイルエラー確認
docker compose exec typespec npm run typespec:compile
```

#### 生成ファイルが見つからない

```bash
# マルチAPI：各OpenAPI仕様ファイルの存在確認
ls -la output/openapi/
# → user-api.yaml, product-api.yaml, auth-api.yaml があるか確認

# レガシー：単一OpenAPI仕様ファイルの存在確認  
ls -la output/openapi/openapi.yaml

# コンテナ状態を確認
docker compose ps

# 全ての出力ディレクトリを確認
ls -la output/
```

#### マルチAPI生成エラー

```bash
# マルチAPI生成でエラーが発生した場合
docker compose exec generator python generator/main.py --target csv --input output/openapi

# 個別API生成テスト
docker compose exec generator python generator/main.py --target spring --input output/openapi/user-api.yaml
```

#### パッケージ・モジュール構造の問題

マルチAPI生成では、各APIが独立したパッケージ・モジュールに生成されます：
- **Spring Boot**: `com.example.user.userapi`, `com.example.user.productapi`など
- **Angular**: `app/user/`, `app/product/`など

想定と異なる構造の場合は、設定ファイル（`config/generator_config.yaml`）の`apis`セクションを確認してください。

## 🗑️ 成果物の削除

マルチAPI対応後の生成ファイルを削除するためのクリーンアップコマンドです。

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

### 段階的削除（バックアップ保持）

```bash
# バックアップファイルを保持してメインファイルのみ削除
find output/ -name "*_[0-9]*" -prune -o -type f -delete
```

### 注意事項

- 削除コマンドは**output/ディレクトリ内の生成ファイルのみ**を対象とします
- ソースファイル（TypeSpec定義、設定ファイル、テンプレートなど）は削除されません
- マルチAPI対応により、API別に生成されたファイルが複数ディレクトリに分散しています
- 削除前に重要なカスタマイズが含まれていないか確認してください
- 生成ファイルは`.gitignore`により除外されているため、通常は削除後に再生成できます
- バックアップファイル（タイムスタンプ付き）は自動生成されるため、履歴確認に使用できます

---

## 🎯 まとめ

このツールにより、**1API = 1TypeSpecファイル**アーキテクチャに基づいた、スケーラブルなフルスタック開発が実現されます：

✅ **API分離**: 各APIを独立したTypeSpecファイルで定義  
✅ **パッケージ分離**: Spring BootでAPI別パッケージ構造  
✅ **モジュール分離**: AngularでAPI別モジュール構造  
✅ **データベース統合**: 複数APIのテーブル定義を統合管理  
✅ **レガシー互換**: 従来の単一API方式もサポート

TypeSpecを真の情報源として、一貫性のあるフルスタックアプリケーションの開発を効率化できます。
