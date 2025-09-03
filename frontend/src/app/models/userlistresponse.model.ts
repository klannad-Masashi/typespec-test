/**
 * UserListResponse インターフェース
 * ユーザー一覧レスポンス
 * TypeSpecから自動生成 - 2025-09-03T01:10:28.132274
 */
export interface UserListResponse {

  /**
   * ユーザーリスト
   */
  users: any[];

  /**
   * 総件数
   */
  total: number;

  /**
   * 現在のページ
   */
  page: number;

  /**
   * 1ページあたりの件数
   */
  limit: number;

}