# タスク完了時のチェックリスト

## 開発フローの基本原則
1. **TypeSpec定義の変更**: TypeSpecファイル(.tsp)でAPI仕様を修正
2. **コンパイル**: TypeSpecからOpenAPI仕様書を生成
3. **コード生成**: 各レイヤー（フロントエンド、バックエンド、DDL）のコード生成
4. **検証**: 生成されたコンポーネントの整合性確認

## タスク完了時に実行すべきコマンド

### 1. TypeSpecコンパイル確認
```bash
# 全APIコンパイル
docker compose exec typespec npm run typespec:compile-all

# コンパイルエラーがないことを確認
ls -la output/openapi/
```

### 2. コード生成確認
```bash
# 全コンポーネント再生成
docker compose exec generator python generator/main.py --target all --input output/openapi

# 生成されたファイルの確認
ls -la output/backend/
ls -la output/frontend/
ls -la output/ddl/
```

### 3. Python コード品質チェック
```bash
# フォーマットチェック
docker compose exec generator black --check generator/

# リントチェック
docker compose exec generator flake8 generator/

# テスト実行（テストファイルが存在する場合）
docker compose exec generator pytest generator/
```

### 4. 生成ファイルの整合性確認
- [ ] OpenAPI仕様書が全API分生成されている
- [ ] Spring BootのController/DTOが正しく生成されている  
- [ ] Angular の型定義/サービスが正しく生成されている
- [ ] DDLファイルが適切に生成されている
- [ ] バリデーションルールが適切に反映されている

### 5. Docker環境の状態確認
```bash
# コンテナの状態確認
docker compose ps

# ログ確認（エラーがないか）
docker compose logs typespec
docker compose logs generator
```

## 注意事項
- **生成ファイルは手動編集禁止**: 全ての変更はTypeSpecで行う
- **統合テスト**: 可能であればフロントエンドとバックエンド間の整合性を検証
- **データベース**: DDL実行前にスキーマ変更の影響を確認