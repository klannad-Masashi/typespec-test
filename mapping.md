# TypeSpec → Java コントローラー マッピング表

このドキュメントは、TypeSpecファイルの要素がJavaコントローラーファイルのどの部分にマッピングされるかを示しています。

## 1. 基本構造マッピング

| TypeSpec要素 | 値/例 | Java要素 | 値/例 | 備考 |
|-------------|------|----------|------|------|
| `namespace` | `Example` | `class名` | `ExampleController` | namespace名 + "Controller" |
| `@service` | `title: "Example"` | `class コメント` | `/** Example */` | サービスタイトルがコメントに |
| `@route("/api/v1/example")` | `/api/v1/example` | `@PostMapping` | `"api/v1/example"` | パス情報がアノテーションに |
| `op exampleV1` | `exampleV1` | `method名` | `exampleV1` | オペレーション名をそのまま使用 |

## 2. モデルマッピング

| TypeSpec要素 | 例 | Java要素 | 例 | 変換規則 |
|-------------|---|----------|---|---------|
| `model` | `V1InDto` | `record` | `public record V1InDto` | モデル名をそのまま使用 |
| `field: type` | `name: string` | `Type fieldName` | `String name` | 型変換 + フィールド名保持 |
| `field?` | `nullableValue?: string` | `Type fieldName` | `String nullableValue` | オプショナルマーク除去 |
| `/** コメント */` | `/** 名前 */` | `// コメント` | 生成されない | JSDocコメントは変換されない |

## 3. 型マッピング

| TypeSpec型 | Java型 | 例 |
|-----------|-------|-----|
| `string` | `String` | `name: string` → `String name` |
| `int64` | `Long` | `innerLong: int64` → `Long innerLong` |
| `utcDateTime` | `Instant` | `instantValue: utcDateTime` → `Instant instantValue` |
| `model[]` | `List<Model>` | `V1InDtoArrayObject[]` → `List<V1InDtoArrayObject>` |
| `enum` | `enum` | `ExampleEnum` → `ExampleEnum` |

## 4. バリデーションマッピング

| TypeSpec デコレーター | Java アノテーション | 例 |
|-------------------|------------------|-----|
| `@unitCheckString("jisX0213withAlphaNumericSymbol")` | `@UnitCheckString(pattern = UnitCheckString.Type.jisX0213withAlphaNumericSymbol)` | 文字種制限 |
| `@unitCheckString()` | `@UnitCheckString(pattern = UnitCheckString.Type.all)` | 汎用文字列 |
| `@maxLength(20)` | `@UnitCheckString(maxLength = 20)` | 最大長制限 |
| `@minValue(5) @maxValue(10)` | `@UnitCheckNumber(minLength = 5, maxLength = 10)` | 数値範囲 |
| `@minItems(2) @maxItems(10)` | `@UnitCheckArray(minLength = 2, maxLength = 10)` | 配列サイズ |
| `@unitCheckObject` | `@UnitCheckObject` | オブジェクト検証 |
| `@unitCheckInstant` | `@UnitCheckInstant` | 日時検証 |
| `@unitCheckEnum` | `@UnitCheckEnum` | 列挙型検証 |

## 5. 列挙型マッピング

| TypeSpec要素 | 例 | Java要素 | 例 |
|-------------|---|----------|---|
| `enum EnumName` | `enum ExampleEnum` | `public enum EnumName` | `public enum ExampleEnum` |
| `VALUE: "code"` | `VALUE1: "value1"` | `VALUE("code")` | `VALUE1("value1")` |

## 6. オペレーションマッピング

| TypeSpec要素 | 例 | Java要素 | 例 |
|-------------|---|----------|---|
| `@post` | `@post` | `@PostMapping` | `@PostMapping("api/v1/example")` |
| `@body request: Type` | `@body request: V1InDto` | `@RequestBody Type param` | `@RequestBody V1InDto v1InDto` |
| `: ReturnType` | `: V1OutDto` | `public ReturnType method()` | `public V1OutDto exampleV1()` |

## 7. 具体例

### TypeSpec側 (main.tsp)
```typescript
namespace Example;

enum ExampleEnum {
  VALUE1: "value1",
  VALUE2: "value2"
}

model V1InDto {
  @unitCheckString("jisX0213withAlphaNumericSymbol")
  name: string;

  @unitCheckString()
  nullableValue?: string;

  @unitCheckNumber
  @minValue(5)
  @maxValue(10)
  minMaxValue: int64;
}

model V1OutDto {
  name: string;
  nullableValue?: string;
  minMaxValue: string;
}

@route("/api/v1/example")
@post
op exampleV1(
  @body request: V1InDto
): V1OutDto;
```

### Java側 (ExampleController.java)
```java
@RestController
public class ExampleController {

    @PostMapping("api/v1/example")
    public V1OutDto exampleV1(@RequestBody V1InDto v1InDto) {
        // 実装
    }

    public record V1InDto(
        @UnitCheckString(
            pattern = UnitCheckString.Type.jisX0213withAlphaNumericSymbol
        )
        String name,

        @UnitCheckString(
            isRequired = false,
            pattern = UnitCheckString.Type.all
        )
        String nullableValue,

        @UnitCheckNumber(
            minLength = 5,
            maxLength = 10
        )
        Long minMaxValue
    ) {
    }

    public record V1OutDto(
        String name,
        String nullableValue,
        String minMaxValue
    ) {
    }

    public enum ExampleEnum {
        VALUE1("value1"),
        VALUE2("value2");

        private final String code;

        ExampleEnum(String code) {
            this.code = code;
        }

        public String getCode() {
            return code;
        }
    }
}
```

## 8. 生成処理の流れ

1. **TypeSpec → OpenAPI**: TypeSpecファイルがOpenAPI仕様に変換
2. **OpenAPI → Java**: Spring Generator (`generator/scripts/spring_generator.py`) がJavaコードを生成
3. **テンプレート適用**: Jinja2テンプレート (`generator/templates/spring/controller.java.j2`) を使用
4. **カスタムアノテーション変換**: `x_extension_parser.py`によってTypeSpecの独自デコレーターがJavaのバリデーションアノテーションに変換

## 9. 複数エンドポイント時の動作

TypeSpecで複数のエンドポイントが定義された場合、各エンドポイントごとに個別のJavaメソッドが生成されます。

### メソッド名生成ルール

| 条件 | 生成されるメソッド名 | 例 |
|------|------------------|-----|
| TypeSpecで `op 操作名` が指定されている | `操作名` をそのまま使用 | `op getUserById` → `getUserById()` |
| 操作名が指定されていない | `{HTTPメソッド}_{パス}` 形式で自動生成 | POST `/api/users` → `post_api_users()` |

### 複数エンドポイントの例

```typescript
// TypeSpec例
@route("/api/v1/example")
@post
op exampleV1(@body request: V1InDto): V1OutDto;

@route("/api/v1/example/{id}")
@get
op getExampleById(@path id: string): V1OutDto;

@route("/api/v1/example")
@get
op getAllExamples(): V1OutDto[];
```

```java
// 生成されるJava例
@RestController
public class ExampleController {

    @PostMapping("api/v1/example")
    public V1OutDto exampleV1(@RequestBody V1InDto v1InDto) {
        // 実装
    }

    @GetMapping("api/v1/example/{id}")
    public V1OutDto getExampleById(@PathVariable String id) {
        // 実装
    }

    @GetMapping("api/v1/example")
    public List<V1OutDto> getAllExamples() {
        // 実装
    }
}
```

## 10. 注意事項

- TypeSpecのモデル名はそのままJavaのrecord名として使用されます
- TypeSpecのフィールド名はcamelCaseに変換されます
- オプショナルフィールド（`?`）は Java側でも同様に扱われますが、バリデーションアノテーションで `isRequired = false` として表現されます
- TypeSpecのコメント（`/** */`）は現在のところJava側には反映されません
- メソッド名は `operation_id` に基づいて生成されるため、複数エンドポイントでも重複しません