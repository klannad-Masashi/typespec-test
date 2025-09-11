import "@typespec/http";
import "@typespec/rest";
import "@typespec/openapi3";
import "@typespec-gen/common";
import "@typespec-gen/decorators";

using TypeSpec.Http;
using TypeSpec.Rest;
using TypeSpecGen.DDL;

namespace ExampleModels {

  @doc("Example入力DTO")
  model InDto {
    @doc("名前 (必須)")
    name: string;

    @doc("Nullable値")
    nullableValue?: string;

    @doc("Nullable かつ NotEmpty")
    @minLength(1)
    notEmpty?: string;

    @doc("Nullable かつ MaxLength(10)")
    @maxLength(10)
    maxLength?: string;

    @doc("Nullable かつ英数字パターン")
    @pattern("^[A-Za-z0-9]*$")
    alphanumeric?: string;

    @doc("Nullable かつ Min(1) Max(10)")
    @minValue(1)
    @maxValue(10)
    minmax?: int32;
  }

  @doc("Example出力DTO")
  model OutDto {
    @doc("メッセージ")
    message: string;

    @doc("ユーザーID")
    userId: int64;

    @doc("Exampleリスト")
    examples: ExampleDto[];
  }

  @doc("Example詳細DTO")
  model ExampleDto {
    @doc("ExampleID")
    exampleId: int64;

    @doc("名前")
    name: string;

    @doc("作成日時")
    createdAt: utcDateTime;

    @doc("更新日時")
    updatedAt: utcDateTime;
  }
}