import "@typespec/http";
import "@typespec/rest";
import "@typespec/openapi";

using TypeSpec.Http;
using TypeSpec.Rest;
using TypeSpec.OpenAPI;

@service(#{
  title: "Test API",
  description: ""
})
namespace TestService;

// ===== モデル定義 =====

/**
 * ユーザー情報
 */
model User {
  /**
   * ユーザーID
   */
  @pattern("^[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}$")
  id: string;
  /**
   * ユーザー名
   */
  @maxLength(255)
  name: string;
  /**
   * メールアドレス
   */
  @maxLength(255)
  @format("email")
  email: string;
}

// ===== API操作定義 =====

/**
 * 
 */
@route("/api/v1/test/test1")
@get op get_test_1(): User;
