import "@typespec/http";
import "@typespec/rest";
import "@typespec/openapi3";
import "@typespec/versioning";
import "@typespec-test/common";
import "@typespec-test/decorators";
import "@typespec-test/enums";

using TypeSpec.Http;
using TypeSpec.Rest;
using TypeSpec.Versioning;
using MyService.DDL;
using MyService.Enums;

@service({
  title: "User Management API",
})
@server("http://localhost:8080", "Development server")
namespace UserManagementAPI;

// ユーザーモデル定義
@doc("ユーザー情報")
@MyService.DDL.makeDDL
@MyService.DDL.tableName("app_users")
model User {
  @doc("ユーザーID（自動生成）")
  @key
  id: int32;

  @doc("ユーザー名")
  @minLength(1)
  @maxLength(50)
  @MyService.DDL.length(50)
  username: string;

  @doc("メールアドレス")
  @format("email")
  email: string;

  @doc("フルネーム")
  @maxLength(100)
  @MyService.DDL.length(100)
  fullName: string;

  @doc("アクティブフラグ")
  isActive: boolean = true;

  @doc("内部フィールド（DDL生成除外）")
  @MyService.DDL.notAddForDDL
  internalField?: string;

  // 共通のタイムスタンプを継承
  ...TimestampFields;
}

// ユーザー作成時の入力データ
@doc("ユーザー作成リクエスト")
model CreateUserRequest {
  @doc("ユーザー名")
  @minLength(1)
  @maxLength(50)
  username: string;

  @doc("メールアドレス")
  @format("email")
  email: string;

  @doc("フルネーム")
  @maxLength(100)
  fullName: string;
}

// ユーザー更新時の入力データ
@doc("ユーザー更新リクエスト")
model UpdateUserRequest {
  @doc("ユーザー名")
  @minLength(1)
  @maxLength(50)
  username?: string;

  @doc("メールアドレス")
  @format("email")
  email?: string;

  @doc("フルネーム")
  @maxLength(100)
  fullName?: string;

  @doc("アクティブフラグ")
  isActive?: boolean;
}

// レスポンス型定義
@doc("ユーザー一覧レスポンス")
model UserListResponse {
  @doc("ユーザーリスト")
  users: User[];

  // 共通のページング情報を継承
  ...PaginationInfo;
}

@doc("ユーザー作成レスポンス")
model UserCreateResponse {
  @doc("作成されたユーザー")
  user: User;
}

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