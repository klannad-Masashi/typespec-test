import "@typespec/http";
import "@typespec/rest";
import "@typespec/openapi3";
import "@typespec/versioning";
import "@typespec-test/common";
import "@typespec-test/decorators";
import "@typespec-test/enums";
import "@typespec-test/models";

using TypeSpec.Http;
using TypeSpec.Rest;
using TypeSpec.Versioning;
using MyService.DDL;
using MyService.Enums;
using UserModels;

@service({
  title: "User Management API",
})
@server("http://localhost:8080", "Development server")
namespace UserManagementAPI;

// モデルは@typespec-test/modelsパッケージから参照

// API エンドポイント定義
@tag("Users")
@route("/api/users")
namespace Users {
  @doc("ユーザー一覧取得")
  @get
  op listUsers(...SearchQuery): UserListResponse | ErrorResponse;

  @doc("ユーザー詳細取得")
  @get
  op getUser(
    @doc("ユーザーID")
    @path userId: int32
  ): User | ErrorResponse;

  @doc("ユーザー作成")
  @post
  op createUser(
    @doc("ユーザー作成データ")
    @body user: CreateUserRequest
  ): UserCreateResponse | ErrorResponse;

  @doc("ユーザー更新")
  @put
  op updateUser(
    @doc("ユーザーID")
    @path userId: int32,
    
    @doc("ユーザー更新データ")
    @body user: UpdateUserRequest
  ): User | ErrorResponse;

  @doc("ユーザー削除")
  @delete
  op deleteUser(
    @doc("ユーザーID")
    @path userId: int32
  ): DeleteResponse | ErrorResponse;
}