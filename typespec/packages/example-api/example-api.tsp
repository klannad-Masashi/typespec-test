import "@typespec/http";
import "@typespec/rest";
import "@typespec/openapi3";
import "@typespec/versioning";
import "@typespec-gen/common";
import "@typespec-gen/decorators";
import "@typespec-gen/enums";
import "@typespec-gen/models";

using TypeSpec.Http;
using TypeSpec.Rest;
using TypeSpec.Versioning;
using TypeSpecGen.DDL;
using TypeSpecGen.Enums;
using ExampleModels;

@service(#{
  title: "Example Service"
})
@server("http://localhost:8080", "Development server")
namespace ExampleAPI;

// モデルは@typespec-gen/modelsパッケージから参照

// API エンドポイント定義
@tag("Example")
@route("/api/v1/example")
namespace Example {
  @doc("Example list operation")
  @post
  @route("/list")
  op list(
    @doc("リクエストデータ")
    @body body: InDto
  ): OutDto | ErrorResponse;
}