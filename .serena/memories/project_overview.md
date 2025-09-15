# プロジェクト概要

## プロジェクトの目的
TypeSpecを真の情報源とするマルチAPI対応フルスタックWeb開発コード生成ツールです。1API = 1TypeSpecファイルアーキテクチャを採用し、スケーラブルな開発を実現します。

## 主な特徴
- TypeSpec定義からOpenAPI仕様書、Spring Boot、Angular、DDLを自動生成
- マルチAPI対応（user-api.tsp、product-api.tsp、auth-api.tsp など）
- モデル分離アーキテクチャ（共有モデル + API別エンドポイント）
- Docker環境での統合開発

## アーキテクチャ
```
TypeSpec定義 (.tspファイル)
├── OpenAPI仕様書の生成
├── Spring Bootコントローラーとドメインオブジェクトの生成
├── Angular TypeScript型定義とAPIクライアントの生成
└── データベースDDLスキーマの生成
```

## プロジェクト構造
- `typespec/`: TypeSpec定義とワークスペース
- `generator/`: Python生成ツール
- `output/`: 生成されたコード類
- `config/`: 生成設定ファイル
- `web-service/`: TypeSpec Webサービス
- `web-db/`: PostgreSQL データベース

## 技術スタック
- **API定義**: TypeSpec (.tsp files)
- **フロントエンド**: Angular with TypeScript  
- **バックエンド**: Spring Boot (Java)
- **データベース**: PostgreSQL
- **生成ツール**: Python 3.12.3
- **開発環境**: Docker Compose