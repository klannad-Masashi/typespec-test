import "@typespec/http";
import "@typespec/rest";
import "@typespec/openapi3";
import "@typespec/versioning";

// 共通型定義をインポート
import "./common/base-types.tsp";

// 各API定義をインポート
import "./apis/user-api.tsp";
import "./apis/product-api.tsp";
import "./apis/auth-api.tsp";

using TypeSpec.Http;
using TypeSpec.Rest;
using TypeSpec.Versioning;

@service({
  title: "Full Stack API Suite",
  description: "User Management, Product Management, and Authentication APIs"
})
@server("http://localhost:8080", "Development server")
namespace FullStackAPI;

// このファイルはインポートハブとして機能します
// 新しいAPIを追加する場合は、apis/フォルダにAPIファイルを作成し、
// 上記のimport文に追加してください