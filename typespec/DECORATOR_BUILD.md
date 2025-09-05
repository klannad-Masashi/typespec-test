# カスタムデコレータビルドガイド

## 概要

このプロジェクトでは、TypeSpec用のカスタムデコレータ `@ABCDEF/tsp-ext-dec` を使用しています。
デコレータを変更した場合は、以下の手順でビルドが必要です。

## ビルド手順

### 1. デコレータビルド（必要時のみ）

```bash
npm run decorator:build
```

このコマンドは以下を実行します：
- TypeScriptファイル (`tsp/decorator/lib.ts`) をコンパイル
- 生成された JavaScript ファイルを `node_modules/@ABCDEF/tsp-ext-dec/` にコピー

### 2. TypeSpec コンパイル

```bash
npm run typespec:compile-separate
```

## デコレータビルドが必要なタイミング

以下のファイルを変更した場合は `npm run decorator:build` を実行してください：

- `tsp/decorator/lib.ts` - デコレータの実装
- `tsp/decorator/lib.tsp` - デコレータの宣言
- `tsp/decorator/package.json` - パッケージ設定
- `tsp/decorator/tsconfig.json` - TypeScript設定

## 効率的な開発ワークフロー

1. **初回セットアップ**: `npm run decorator:build`
2. **TypeSpec API定義の変更**: `npm run typespec:compile-separate` のみ
3. **デコレータの変更**: `npm run decorator:build` → `npm run typespec:compile-separate`

## トラブルシューティング

### `Unknown identifier MyService` エラー
- デコレータビルドが実行されていない可能性があります
- `npm run decorator:build` を実行してください

### `Library "@ABCDEF/tsp-ext-dec" is invalid` エラー
- JavaScriptファイルが生成されていない可能性があります
- `npm run decorator:clean && npm run decorator:build` を実行してください

## クリーンアップ

```bash
npm run decorator:clean
```

生成されたファイルをすべて削除します。