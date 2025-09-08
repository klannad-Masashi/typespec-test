import "@typespec/http";
import "@typespec/rest";
import "@typespec/openapi3";
import "@typespec-gen/common";
import "@typespec-gen/decorators";
import "@typespec-gen/enums";

using TypeSpec.Http;
using TypeSpec.Rest;
using TypeSpecGen.DDL;
using TypeSpecGen.Enums;

namespace ProductModels;

// 商品モデル定義
@doc("商品情報")
model Product {
  @doc("商品ID（自動生成）")
  @key
  id: int32;

  @doc("商品名")
  @minLength(1)
  @maxLength(100)
  name: string;

  @doc("商品説明")
  @maxLength(500)
  description?: string;

  @doc("価格（円）")
  price: decimal;

  @doc("在庫数")
  stockQuantity: int32;

  @doc("商品カテゴリ")
  category: ProductCategory;

  @doc("商品ステータス")
  status: ProductStatus = ProductStatus.Available;

  @doc("SKUコード")
  @minLength(1)
  @maxLength(50)
  sku: string;

  @doc("商品画像URL")
  imageUrl?: string;

  // 共通のタイムスタンプを継承
  ...TimestampFields;
}

// 商品作成時の入力データ
@doc("商品作成リクエスト")
model CreateProductRequest {
  @doc("商品名")
  @minLength(1)
  @maxLength(100)
  name: string;

  @doc("商品説明")
  @maxLength(500)
  description?: string;

  @doc("価格（円）")
  price: decimal;

  @doc("在庫数")
  stockQuantity: int32;

  @doc("商品カテゴリ")
  category: ProductCategory;

  @doc("SKUコード")
  @minLength(1)
  @maxLength(50)
  sku: string;

  @doc("商品画像URL")
  imageUrl?: string;
}

// 商品更新時の入力データ
@doc("商品更新リクエスト")
model UpdateProductRequest {
  @doc("商品名")
  @minLength(1)
  @maxLength(100)
  name?: string;

  @doc("商品説明")
  @maxLength(500)
  description?: string;

  @doc("価格（円）")
  price?: decimal;

  @doc("在庫数")
  stockQuantity?: int32;

  @doc("商品カテゴリ")
  category?: ProductCategory;

  @doc("商品ステータス")
  status?: ProductStatus;

  @doc("商品画像URL")
  imageUrl?: string;
}

// 在庫更新リクエスト
@doc("在庫更新リクエスト")
model UpdateStockRequest {
  @doc("新しい在庫数")
  stockQuantity: int32;
}

// レスポンス型定義
@doc("商品一覧レスポンス")
model ProductListResponse {
  @doc("商品リスト")
  products: Product[];

  // 共通のページング情報を継承
  ...PaginationInfo;
}

@doc("商品作成レスポンス")
model ProductCreateResponse {
  @doc("作成された商品")
  product: Product;
}

// カテゴリ別検索用クエリ
@doc("商品検索クエリ")
model ProductSearchQuery {
  // 基本の検索クエリを継承
  ...SearchQuery;

  @doc("カテゴリでフィルタ")
  @query category?: ProductCategory;

  @doc("ステータスでフィルタ")
  @query status?: ProductStatus;

  @doc("最低価格")
  @query minPrice?: decimal;

  @doc("最高価格")
  @query maxPrice?: decimal;
}