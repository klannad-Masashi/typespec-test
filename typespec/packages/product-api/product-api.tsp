import "@typespec/http";
import "@typespec/rest";
import "@typespec/openapi3";
import "@typespec/versioning";
import "@typespec-gen/common";
import "@typespec-gen/models";
import "@typespec-gen/enums";

using TypeSpec.Http;
using TypeSpec.Rest;
using TypeSpec.Versioning;
using ProductModels;
using TypeSpecGen.Enums;

@service({
  title: "Product Management API",
})
@server("http://localhost:8080", "Development server")
namespace ProductManagementAPI;

// モデルは@typespec-gen/modelsパッケージから参照

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