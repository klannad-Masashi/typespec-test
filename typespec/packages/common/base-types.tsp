import "@typespec/openapi3";
import "@typespec/http";
import "@typespec/rest";

using TypeSpec.Http;
using TypeSpec.Rest;

// 共通エラーレスポンス
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

// 共通の基本型
@doc("ページング情報")
model PaginationInfo {
  @doc("現在のページ")
  page: int32;

  @doc("1ページあたりの件数")
  limit: int32;

  @doc("総件数")
  total: int32;

  @doc("総ページ数")
  totalPages: int32;
}

// 共通のレスポンス型
@doc("削除成功レスポンス")
model DeleteResponse {
  @doc("削除成功メッセージ")
  message?: string;
}

@doc("作成成功レスポンス")
model CreateResponse {
  @doc("作成されたリソースID")
  id: int32;

  @doc("作成成功メッセージ")
  message?: string;
}

// 共通のクエリパラメータ
@doc("検索クエリ")
model SearchQuery {
  @doc("検索キーワード")
  @query search?: string;

  @doc("ページ番号（1から開始）")
  @query page?: int32 = 1;

  @doc("1ページあたりの件数")
  @query limit?: int32 = 10;

  @doc("ソート順序（asc/desc）")
  @query sort?: "asc" | "desc" = "asc";

  @doc("ソートフィールド")
  @query sortBy?: string;
}

// 共通のタイムスタンプ
@doc("作成・更新タイムスタンプ")
model TimestampFields {
  @doc("作成日時")
  @visibility(Lifecycle.Read)
  createdAt: utcDateTime;

  @doc("更新日時")
  @visibility(Lifecycle.Read)
  updatedAt: utcDateTime;
}