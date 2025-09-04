import "@typespec/http";
import "@typespec/rest";
import "@typespec/openapi3";
import "@typespec/versioning";
import "../common/base-types.tsp";

using TypeSpec.Http;
using TypeSpec.Rest;
using TypeSpec.Versioning;

@service({
  title: "Product Management API",
})
@server("http://localhost:8080", "Development server")
namespace ProductManagementAPI;

// 商品カテゴリ列挙型
@doc("商品カテゴリ")
enum ProductCategory {
  @doc("家電")
  Electronics: "electronics",
  
  @doc("衣服")
  Clothing: "clothing",
  
  @doc("書籍")
  Books: "books",
  
  @doc("スポーツ")
  Sports: "sports",
  
  @doc("その他")
  Other: "other"
}

// 商品ステータス
@doc("商品ステータス")
enum ProductStatus {
  @doc("利用可能")
  Available: "available",
  
  @doc("在庫切れ")
  OutOfStock: "out_of_stock",
  
  @doc("生産中止")
  Discontinued: "discontinued"
}

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

// API エンドポイント定義
@tag("Products")
@route("/api/products")
namespace Products {
  @doc("商品一覧取得")
  @get
  op listProducts(...ProductSearchQuery): ProductListResponse | ErrorResponse;

  @doc("商品詳細取得")
  @get
  op getProduct(
    @doc("商品ID")
    @path productId: int32
  ): Product | ErrorResponse;

  @doc("商品作成")
  @post
  op createProduct(
    @doc("商品作成データ")
    @body product: CreateProductRequest
  ): ProductCreateResponse | ErrorResponse;

  @doc("商品更新")
  @put
  op updateProduct(
    @doc("商品ID")
    @path productId: int32,
    
    @doc("商品更新データ")
    @body product: UpdateProductRequest
  ): Product | ErrorResponse;

  @doc("在庫更新")
  @patch
  op updateStock(
    @doc("商品ID")
    @path productId: int32,
    
    @doc("在庫更新データ")
    @body stock: UpdateStockRequest
  ): Product | ErrorResponse;

  @doc("商品削除")
  @delete
  op deleteProduct(
    @doc("商品ID")
    @path productId: int32
  ): DeleteResponse | ErrorResponse;

  @doc("カテゴリ別商品取得")
  @get
  @route("/category/{category}")
  op getProductsByCategory(
    @doc("商品カテゴリ")
    @path category: ProductCategory,
    
    @doc("ページ番号")
    @query page?: int32 = 1,
    
    @doc("1ページあたりの件数")
    @query limit?: int32 = 10
  ): ProductListResponse | ErrorResponse;
}