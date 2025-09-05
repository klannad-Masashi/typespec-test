// lib.tsp
// 共通Enum定義

namespace MyService.Enums;

// ユーザーステータス
enum UserStatus {
  Active: "active",
  Inactive: "inactive",
  Suspended: "suspended"
}

// 商品カテゴリ
enum ProductCategory {
  Electronics: "electronics",
  Clothing: "clothing", 
  Books: "books",
  Home: "home"
}

// 注文ステータス
enum OrderStatus {
  Pending: "pending",
  Processing: "processing",
  Shipped: "shipped",
  Delivered: "delivered",
  Cancelled: "cancelled"
}