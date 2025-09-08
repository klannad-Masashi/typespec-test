// lib.tsp
// 共通Enum定義

namespace TypeSpecGen.Enums;

// ユーザーステータス
enum UserStatus {
  Active: "active",
  Inactive: "inactive",
  Suspended: "suspended"
}

// ユーザーロール
@doc("ユーザーロール")
enum UserRole {
  @doc("管理者")
  Admin: "admin",
  
  @doc("一般ユーザー")
  User: "user",
  
  @doc("ゲスト")
  Guest: "guest"
}

// ログイン試行結果
@doc("ログイン試行結果")
enum LoginResult {
  @doc("成功")
  Success: "success",
  
  @doc("認証情報が無効")
  InvalidCredentials: "invalid_credentials",
  
  @doc("アカウントがロック済み")
  AccountLocked: "account_locked",
  
  @doc("アカウントが非アクティブ")
  AccountInactive: "account_inactive"
}

// 商品カテゴリ
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

// 注文ステータス
enum OrderStatus {
  Pending: "pending",
  Processing: "processing",
  Shipped: "shipped",
  Delivered: "delivered",
  Cancelled: "cancelled"
}