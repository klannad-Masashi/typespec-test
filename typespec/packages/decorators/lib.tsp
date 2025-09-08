// lib.tsp
// デコレーターの「宣言」ファイル。
// ここでは型や対象を定義するだけで、実装は lib.ts 側にある。

namespace TypeSpecGen.DDL;

// ===== モデル（テーブル）向け =====
extern dec makeDDL(target: Model);
/** テーブル名を明示指定 */
extern dec tableName(target: Model, name: valueof string);

// ===== プロパティ（カラム）向け =====
/** 主キー */
// extern dec pk(target: ModelProperty);
/** ユニーク制約 */
// extern dec unique(target: ModelProperty);
/** DDLに含めない */
extern dec notAddForDDL(target: ModelProperty);

/** 参照テーブル（マスタ用） */
extern dec lookupTable(target: ModelProperty, table: valueof string);
extern dec lookupColumn(target: ModelProperty, column: valueof string);

/** CHECK制約候補 */
extern dec checkIn(target: ModelProperty, values: valueof string[]);
/** DB ENUM 候補 */
extern dec dbEnum(target: ModelProperty, values: valueof string[]);

/** 型ヒント */
extern dec length(target: ModelProperty, len: valueof numeric);
extern dec precisionScale(target: ModelProperty, precision: valueof numeric, scale: valueof numeric);

namespace TypeSpecGen.Java;

/** Java Enum生成マーカー */
extern dec makeEnumJava(target: Enum);