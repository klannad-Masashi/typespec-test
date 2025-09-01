# typespec-test
TypeSpecを使用したWeb開発プロジェクト

## TypeSpecとは

TypeSpecは、Microsoft が開発したAPI定義のための宣言型言語です。REST API、OpenAPI、JSON Schema等を統一された構文で定義でき、複数の形式への出力を自動生成できます。

### TypeSpecの特徴
- **統一された構文**: 一つの定義から複数の出力形式を生成
- **型安全性**: 強力な型システムによる安全なAPI設計
- **再利用性**: 共通のモデルやパターンの効率的な再利用
- **拡張性**: プラグインによる柔軟な拡張機能

## アーキテクチャ構成

本プロジェクトは以下の技術スタックで構成されたWebアプリケーションです：

### フロントエンド
- **Angular**: TypeScriptベースのSPAフレームワーク
- TypeSpecから自動生成されるTypeScript型定義とAPIクライアントを使用

### バックエンド
- **Spring Boot**: Java/Kotlinベースのマイクロサービスフレームワーク
- TypeSpecから自動生成されるAPIコントローラーとDTOを使用

### データベース
- **PostgreSQL**: 高性能なオープンソースリレーショナルデータベース
- TypeSpecから自動生成されるDDL（Data Definition Language）を使用
- JSON型サポートによる柔軟なデータ構造対応

## TypeSpecからの自動生成機能

このプロジェクトでは、TypeSpec定義から以下のコンポーネントを自動生成します：

### 1. DDL（Data Definition Language）
- データベーススキーマの自動生成
- テーブル定義、制約、インデックスの作成

### 2. Spring Boot APIコントローラー
- REST APIエンドポイントの自動生成
- ルーティング設定とハンドラーメソッドの作成

### 3. DTO（Data Transfer Object）
- API間でのデータ転送オブジェクトの自動生成
- バリデーション設定の組み込み

### 4. Angular フロントエンド部品
- TypeScript型定義の自動生成
- APIクライアントサービスの自動生成
- フォームバリデーションの自動設定
