// lib.ts
// デコレーターの実装本体。
// 付与された情報を OpenAPI の拡張 (x-*) として埋め込む。

import {
  createTypeSpecLibrary,
  DecoratorContext,
  Enum,
  Model,
  ModelProperty,
} from "@typespec/compiler";
import { setExtension } from "@typespec/openapi";

export const $lib = createTypeSpecLibrary({
  name: "@typespec-gen/decorators", // パッケージ名（package.json と対応させる）
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

// ===== Enum系 =====
export function $makeEnumJava(ctx: DecoratorContext, target: Enum) {
  setExtension(ctx.program, target, "x-makeEnumJava", true);
}

// ===== バリデーション系 =====
export function $unitCheckString(ctx: DecoratorContext, target: ModelProperty, pattern?: string) {
  setExtension(ctx.program, target, "x-unitCheckString", pattern || "all");
}

export function $unitCheckNumber(ctx: DecoratorContext, target: ModelProperty) {
  setExtension(ctx.program, target, "x-unitCheckNumber", true);
}

export function $unitCheckObject(ctx: DecoratorContext, target: ModelProperty) {
  setExtension(ctx.program, target, "x-unitCheckObject", true);
}

export function $unitCheckArray(ctx: DecoratorContext, target: ModelProperty) {
  setExtension(ctx.program, target, "x-unitCheckArray", true);
}

export function $unitCheckInstant(ctx: DecoratorContext, target: ModelProperty) {
  setExtension(ctx.program, target, "x-unitCheckInstant", true);
}

export function $unitCheckEnum(ctx: DecoratorContext, target: ModelProperty) {
  setExtension(ctx.program, target, "x-unitCheckEnum", true);
}
