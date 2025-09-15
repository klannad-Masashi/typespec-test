import "@typespec/http";
import "@typespec/rest";
import "@typespec/openapi";
import "@typespec-gen/decorators";

using TypeSpec.Http;
using TypeSpec.Rest;
using TypeSpec.OpenAPI;

@service(#{
  title: "Example"
})
namespace Example;

/**
 * 例示用の列挙型
 */
@makeEnumJava
enum ExampleEnum {
  VALUE1: "value1",
  VALUE2: "value2",
  VALUE3: "value3"
}

/**
 * 例示用の列挙型
 */
@makeEnumJava
enum SampleEnum {
  AAA: "01",
  BBB: "02",
  CCC: "03"
}

/**
 * 入力用DTO内部オブジェクト
 */
model V1InDtoInnerObject {
  /**
   * 内部名称
   */
  innerName: string;
  
  /**
   * 内部数値
   */
  innerLong: int64;
}

/**
 * 入力用DTO配列オブジェクト
 */
model V1InDtoArrayObject {
  /**
   * 配列名称
   */
  arrayName: string;
}

/**
 * API入力DTO
 */
model V1InDto {
  /**
   * 名前（JIS X 0213 + 英数記号）
   */
  @unitCheckString("jisX0213withAlphaNumericSymbol")
  @pattern("^[\\u3040-\\u309F\\u30A0-\\u30FF\\u4E00-\\u9FAF\\uF900-\\uFAFF\\u3400-\\u4DBFa-zA-Z0-9\\s!-/:-@\\[-`{-~]+$")
  name: string;
  
  /**
   * NULL許可値
   */
  @unitCheckString()
  nullableValue?: string;
  
  /**
   * 空文字不可値
   */
  @unitCheckString()
  notEmpty?: string;
  
  /**
   * 最大長制限値
   */
  @unitCheckString()
  @maxLength(20)
  maxLengthValue: string;
  
  /**
   * 英数字値
   */
  @unitCheckString("alphanumericPattern")
  @pattern("^[a-zA-Z0-9]+$")
  alphanumericValue: string;
  
  /**
   * 最小最大値
   */
  @unitCheckNumber
  @minValue(5)
  @maxValue(10)
  minMaxValue: int64;
  
  /**
   * 内部オブジェクト
   */
  @unitCheckObject
  inDtoInnerObject: V1InDtoInnerObject;
  
  /**
   * 配列オブジェクトリスト
   */
  @unitCheckArray
  @minItems(2)
  @maxItems(10)
  inDtoArrayObjectList: V1InDtoArrayObject[];
  
  /**
   * 日時値
   */
  @unitCheckInstant
  instantValue: utcDateTime;
  
  /**
   * 列挙型
   */
  @unitCheckEnum
  exampleEnum: ExampleEnum;
}

/**
 * 出力用DTO内部オブジェクト
 */
model V1OutDtoInnerObject {
  /**
   * 内部名称
   */
  innerName: string;
  
  /**
   * 内部数値（文字列化）
   */
  innerLong: string;
}

/**
 * 出力用DTO配列オブジェクト
 */
model V1OutDtoArrayObject {
  /**
   * 配列名称
   */
  arrayName: string;
}

/**
 * API出力DTO
 */
model V1OutDto {
  /**
   * 名前
   */
  name: string;
  
  /**
   * NULL許可値
   */
  nullableValue?: string;
  
  /**
   * 空文字不可値
   */
  notEmpty?: string;
  
  /**
   * 最大長制限値
   */
  maxLengthValue: string;
  
  /**
   * 英数字値
   */
  alphanumericValue: string;
  
  /**
   * 最小最大値（文字列化）
   */
  minMaxValue: string;
  
  /**
   * 内部オブジェクト
   */
  inDtoInnerObject: V1OutDtoInnerObject;
  
  /**
   * 配列オブジェクトリスト
   */
  inDtoArrayObjectList: V1OutDtoArrayObject[];
}

/**
 * Example API v1 エンドポイント
 */
@route("/api/v1/example")
@post 
op exampleV1(
  @body request: V1InDto
): V1OutDto;