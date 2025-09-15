# 開発環境とツール情報

## Docker環境構成
- **typespec**: TypeSpec開発専用コンテナ（Node.js環境）
- **generator**: Python生成ツール専用コンテナ（Python 3.12.3）
- **web-service**: TypeSpec Webサービス（ポート8000）
- **web-db**: PostgreSQL データベース（ポート5432）

## TypeSpec環境
- **バージョン**: @typespec/compiler ^0.66.0
- **ワークスペース**: packages/* 構造
- **ビルドツール**: npm scripts
- **出力先**: output/openapi/

## Python生成環境
- **バージョン**: Python 3.12.3
- **主要ライブラリ**:
  - PyYAML==6.0.2 (YAML処理)
  - Jinja2==3.1.4 (テンプレート)
  - click==8.1.7 (CLI)
  - black==24.8.0 (フォーマッター)
  - flake8==7.1.1 (リンター)
  - pytest==8.3.2 (テスト)

## ポート割り当て
- **8000**: web-service (TypeSpec API)
- **5432**: web-db (PostgreSQL)
- **8080**: Spring Boot API（将来的）
- **4200**: Angular フロントエンド（将来的）

## ファイルシステム構成
```
プロジェクトルート/
├── typespec/          # TypeSpec Workspace
├── generator/         # Python生成ツール
├── output/           # 生成されたファイル
├── config/           # 設定ファイル
├── web-service/      # Webサービス
├── web-db/          # DB初期化スクリプト
└── docker-compose.yml
```

## Darwin（macOS）固有コマンド
- **find**: BSD版find（GNU findとは異なる）
- **grep**: BSD版grep（ripgrepの`rg`を推奨）
- **git**: バージョン管理
- **ls**: BSD版ls
- **cd**: 基本的なディレクトリ操作

## エディタ・IDE推奨設定
- **TypeScript/TypeSpec**: VS Code + TypeSpec拡張
- **Python**: PyCharm または VS Code + Python拡張
- **Java**: IntelliJ IDEA または Eclipse
- **文字エンコーディング**: UTF-8必須