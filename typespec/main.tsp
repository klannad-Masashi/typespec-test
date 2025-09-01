import "@typespec/http";
import "@typespec/rest";
import "@typespec/openapi3";

using TypeSpec.Http;
using TypeSpec.Rest;

@service({
  title: "User Management API",
  version: "1.0.0",
})
@server("http://localhost:8080", "Development server")
namespace UserManagement;

// ユーザーモデル定義
@doc("ユーザー情報")
model User {
  @doc("ユーザーID（自動生成）")
  @key
  id: int32;

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

  @doc("作成日時")
  @visibility("read")
  createdAt: utcDateTime;

  @doc("更新日時")
  @visibility("read")
  updatedAt: utcDateTime;

  @doc("アクティブフラグ")
  isActive: boolean = true;
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

// エラーレスポンス
@doc("エラーレスポンス")
@error
model ErrorResponse {
  @doc("エラーコード")
  code: string;

  @doc("エラーメッセージ")
  message: string;

  @doc("詳細情報")
  details?: string;
}

// API エンドポイント定義
@tag("Users")
@route("/users")
namespace Users {
  @doc("ユーザー一覧取得")
  @get
  op listUsers(
    @doc("ページ番号（1から開始）")
    @query page?: int32 = 1,
    
    @doc("1ページあたりの件数")
    @query limit?: int32 = 10,
    
    @doc("検索キーワード（ユーザー名またはメールアドレス）")
    @query search?: string
  ): {
    @doc("ユーザーリスト")
    @statusCode 200
    users: User[];

    @doc("総件数")
    total: int32;

    @doc("現在のページ")
    page: int32;

    @doc("1ページあたりの件数")
    limit: int32;
  } | ErrorResponse;

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
  ): {
    @doc("作成されたユーザー")
    @statusCode 201
    user: User;
  } | ErrorResponse;

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
  ): {
    @doc("削除成功")
    @statusCode 204
    _: void;
  } | ErrorResponse;
}