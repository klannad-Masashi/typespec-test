# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## プロジェクト概要

TypeSpecを使用したフルスタックWeb開発プロジェクトです。TypeSpecのAPI定義からAngularフロントエンド、Spring Bootバックエンド、データベースコンポーネントを自動生成します。

## アーキテクチャ

このプロジェクトはTypeSpecを真の情報源とするコード生成アプローチに従います：

```
TypeSpec定義 (.tspファイル)
├── OpenAPI仕様書の生成
├── Spring Bootコントローラーとドメインオブジェクトの生成
├── Angular TypeScript型定義とAPIクライアントの生成
└── データベースDDLスキーマの生成
```

### 技術スタック
- **API定義**: TypeSpec (.tspファイル)
- **フロントエンド**: Angular with TypeScript
- **バックエンド**: Spring Boot (Java/Kotlin)
- **データベース**: リレーショナルデータベース（DDL自動生成）

## 開発ワークフロー

このプロジェクトはTypeSpecによるコード生成を使用するため、一般的な開発フローは以下の通りです：

1. TypeSpec (.tsp) ファイルでAPI仕様を定義または修正
2. 各レイヤー（フロントエンド、バックエンド、データベース）のコード成果物を生成
3. 生成されたコンポーネントをビルドしてテスト
4. 統合アプリケーションをデプロイ

## TypeSpecコード生成

プロジェクトはTypeSpec定義から以下を生成します：

- **DDL**: データベーススキーマ、テーブル、制約、インデックス
- **Spring Boot**: ルーティングとハンドラーメソッドを含むREST APIコントローラー
- **DTO**: バリデーションルール付きのData Transfer Object
- **Angular**: TypeScript型定義、APIクライアントサービス、フォームバリデーション

## プロジェクト構造（想定）

```
typespec-test/
├── typespec/           # TypeSpec API定義 (.tspファイル)
├── generated/
│   ├── backend/        # 生成されたSpring Bootコード
│   ├── frontend/       # 生成されたAngularコンポーネント
│   └── database/       # 生成されたDDLスクリプト
├── backend/           # Spring Bootアプリケーション
├── frontend/          # Angularアプリケーション
└── database/          # データベース設定とマイグレーション
```

## 開発環境

### Docker環境での実行
このプロジェクトでは、すべてのコマンド（ビルド、テスト、実行など）は基本的にDocker環境で実施してください。

- ローカル環境で実行が必要な場合は、必ず事前に確認してください
- 開発、ビルド、テスト、デプロイはすべてDockerコンテナ内で実行することを前提としています

### ソースコードのコメント
- ソースコードには分かりやすい日本語コメントを記載してください
- 特に複雑な処理やビジネスロジックには必ず説明コメントを追加してください
- 自動生成されたコードであっても、カスタマイズ部分には適切なコメントを記載してください

## 重要な考慮事項

- TypeSpec定義はAPIコントラクトの単一情報源である必要があります
- 生成されたコードは手動編集せず、TypeSpecファイルで変更を行う必要があります
- ビルドプロセスはTypeSpec定義からすべての成果物を再生成する必要があります
- 統合テストは生成されたフロントエンドとバックエンドコード間の整合性を検証する必要があります