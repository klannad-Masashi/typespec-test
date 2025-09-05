// lib.ts
// デコレーターの実装本体。
// 付与された情報を OpenAPI の拡張 (x-*) として埋め込む。

import {
  createTypeSpecLibrary,
  DecoratorContext,
  Model,
  ModelProperty,
} from "@typespec/compiler";
import { setExtension } from "@typespec/openapi";

export const $lib = createTypeSpecLibrary({
  name: "@typespec-test/decorators", // パッケージ名（package.json と対応させる）
  diagnostics: {},
});

// ===== モデル系 =====
export function $makeDDL(ctx: DecoratorContext, target: Model) {
  setExtension(ctx.program, target, "x-makeDDL", true);
}

export function $tableName(ctx: DecoratorContext, target: Model, name: string) {
  setExtension(ctx.program, target, "x-tableName", name);
}

// ===== プロパティ系 =====
// pk と unique は標準デコレータとの衝突のためコメントアウト
// export function $pk(ctx: DecoratorContext, target: ModelProperty) {
//   setExtension(ctx.program, target, "x-pk", true);
// }

// export function $unique(ctx: DecoratorContext, target: ModelProperty) {
//   setExtension(ctx.program, target, "x-unique", true);
// }

export function $notAddForDDL(ctx: DecoratorContext, target: ModelProperty) {
  setExtension(ctx.program, target, "x-notAddForDDL", true);
}

export function $lookupTable(ctx: DecoratorContext, target: ModelProperty, table: string) {
  setExtension(ctx.program, target, "x-lookupTable", table);
}

export function $lookupColumn(ctx: DecoratorContext, target: ModelProperty, column: string) {
  setExtension(ctx.program, target, "x-lookupColumn", column);
}

export function $checkIn(ctx: DecoratorContext, target: ModelProperty, values: string[]) {
  setExtension(ctx.program, target, "x-checkIn", values);
}

export function $dbEnum(ctx: DecoratorContext, target: ModelProperty, values: string[]) {
  setExtension(ctx.program, target, "x-dbEnum", values);
}

// ===== 型ヒント =====
export function $length(ctx: DecoratorContext, target: ModelProperty, len: number) {
  setExtension(ctx.program, target, "x-length", len);
}

export function $precisionScale(
  ctx: DecoratorContext,
  target: ModelProperty,
  precision: number,
  scale: number
) {
  setExtension(ctx.program, target, "x-precision", precision);
  setExtension(ctx.program, target, "x-scale", scale);
}

// IDE 用（任意）
export const $decorators = {
  "MyService.DDL": {
    makeDDL: $makeDDL,
    tableName: $tableName,
    // pk: $pk,           // コメントアウト（標準デコレータとの衝突回避）
    // unique: $unique,   // コメントアウト（標準デコレータとの衝突回避）
    notAddForDDL: $notAddForDDL,
    lookupTable: $lookupTable,
    lookupColumn: $lookupColumn,
    checkIn: $checkIn,
    dbEnum: $dbEnum,
    length: $length,
    precisionScale: $precisionScale,
  },
};