# TypeSpec Workspace 概要

## TypeSpec Workspaceとは

TypeSpecにおける「workspace」は、複数のTypeSpecパッケージやプロジェクトを統合的に管理するための仕組みです。一つのワークスペース内で関連する複数のAPIパッケージを管理し、型定義やデコレーターなどの共通リソースを効率的に共有できます。

## TypeSpec Workspaceの主な機能

### 1. マルチパッケージ管理
- 複数の関連するTypeSpecパッケージを一つのワークスペース内で管理
- 各パッケージは独立して開発・保守が可能
- 統一されたビルドプロセスとツールチェーンを使用

### 2. 依存関係の解決
- パッケージ間の依存関係を自動で解決
- `import`文を使用して他のパッケージの型定義やデコレーターを参照
- 循環依存の検出と防止

### 3. 共通設定とリソース共有
- ワークスペース全体で共通の設定やコンパイル設定を使用
- 型定義、デコレーター、列挙型などの再利用
- 一貫性のあるAPI設計の実現

## 現在のプロジェクト構造

```
project-root/
├── typespec/
│   ├── packages/                 # TypeSpec Workspaceのパッケージディレクトリ
│   │   ├── common/              # 共通型定義パッケージ
│   │   │   └── base-types.tsp   # 基本型定義（TimestampFields, PaginationInfoなど）
│   │   ├── decorators/          # カスタムデコレーターパッケージ
│   │   │   ├── lib.tsp         # デコレーター宣言
│   │   │   └── lib.ts          # デコレーター実装
│   │   ├── enums/               # 列挙型定義パッケージ
│   │   │   └── lib.tsp         # システム全体で使用する列挙型
│   │   ├── user-api/            # ユーザーAPIパッケージ
│   │   │   └── user-api.tsp    # ユーザー管理API定義
│   │   ├── product-api/         # 商品APIパッケージ
│   │   │   └── product-api.tsp # 商品管理API定義
│   │   └── auth-api/            # 認証APIパッケージ
│   │       └── auth-api.tsp    # 認証API定義
│   ├── node_modules/            # TypeSpec関連の依存パッケージ
│   └── package.json             # ワークスペース設定
└── typespec_workspace.md        # このドキュメント
```

## パッケージの役割と依存関係

### 共通パッケージ（Foundation Layer）

#### 1. `@typespec-gen/common`
- **役割**: システム全体で共通利用される基本型定義
- **提供するもの**:
  - `TimestampFields`: 作成日時・更新日時フィールド
  - `PaginationInfo`: ページング情報
  - `SearchQuery`: 検索クエリパラメータ
  - `ErrorResponse`: エラーレスポンス型
  - `DeleteResponse`: 削除レスポンス型

#### 2. `@typespec-gen/decorators`
- **役割**: DDL生成用のカスタムデコレーター
- **提供するもの**:
  - `@makeDDL`: モデルをDDL生成対象としてマーク
  - `@tableName`: テーブル名の明示指定
  - `@notAddForDDL`: DDL生成から除外
  - `@length`: 文字列長制約
  - その他データベース関連のメタデータ

#### 3. `@typespec-gen/enums`
- **役割**: システム全体で使用する列挙型定義
- **提供するもの**: 各種ステータス、カテゴリなどの列挙型

### APIパッケージ（Application Layer）

#### 1. `user-api`
- **機能**: ユーザー管理API
- **依存関係**: `@typespec-gen/common`, `@typespec-gen/decorators`, `@typespec-gen/enums`
- **提供するAPI**: ユーザーCRUD操作

#### 2. `product-api`
- **機能**: 商品管理API
- **依存関係**: `@typespec-gen/common`, `@typespec-gen/decorators`, `@typespec-gen/enums`
- **提供するAPI**: 商品CRUD操作

#### 3. `auth-api`
- **機能**: 認証・認可API
- **依存関係**: `@typespec-gen/common`, `@typespec-gen/decorators`, `@typespec-gen/enums`
- **提供するAPI**: ログイン、トークン管理など

## パッケージの使用方法

### importの書き方
```typescript
// 共通型定義のimport
import "@typespec-gen/common";

// カスタムデコレーターのimport
import "@typespec-gen/decorators";

// 列挙型のimport
import "@typespec-gen/enums";

// 名前空間の使用宣言
using MyService.DDL;          // デコレーター用
using MyService.Enums;        // 列挙型用
```

### 実際の使用例
```typescript
// user-api.tsp での使用例
@doc("ユーザー情報")
@MyService.DDL.makeDDL              // カスタムデコレーター
@MyService.DDL.tableName("app_users") // テーブル名指定
model User {
  @key
  id: int32;
  
  @MyService.DDL.length(50)         // 長さ制約
  username: string;
  
  // 共通のタイムスタンプフィールドを継承
  ...TimestampFields;
}
```

## TypeSpec Workspaceの利点

### 1. コードの再利用性
- 共通の型定義やデコレーターを複数のAPIで共有
- DRY原則に従った開発が可能

### 2. 一貫性の保持
- 全APIで統一されたエラーハンドリング
- 共通のレスポンス形式
- 統一されたネーミング規則

### 3. 保守性の向上
- 変更時の影響範囲が明確
- 共通部分の修正が全体に反映
- パッケージ単位での独立した開発

### 4. スケーラビリティ
- 新しいAPIの追加が容易
- 既存APIとの整合性を自動で保持
- 大規模プロジェクトでの管理が効率的

## 開発ワークフロー

1. **共通部分の設計**: `common`, `decorators`, `enums`の設計・実装
2. **APIパッケージの開発**: 各API固有の定義を実装
3. **コンパイル**: ワークスペース全体を一括コンパイル
4. **コード生成**: OpenAPI仕様書、フロントエンド・バックエンドコードの生成
5. **統合テスト**: 生成されたコード間の整合性確認

この構造により、TypeSpecプロジェクトの管理性と拡張性を大幅に向上させています。