/**
 * UpdateUserRequest インターフェース
 * ユーザー更新リクエスト
 * TypeSpecから自動生成 - 2025-09-03T01:10:28.128367
 */
export interface UpdateUserRequest {

  /**
   * ユーザー名
   */
  username?: string;

  /**
   * メールアドレス
   */
  email?: string;

  /**
   * フルネーム
   */
  fullName?: string;

  /**
   * アクティブフラグ
   */
  isActive?: boolean;

}