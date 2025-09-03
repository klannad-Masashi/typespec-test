/**
 * ErrorResponse インターフェース
 * エラーレスポンス
 * TypeSpecから自動生成 - 2025-09-03T01:10:28.127067
 */
export interface ErrorResponse {

  /**
   * エラーコード
   */
  code: string;

  /**
   * エラーメッセージ
   */
  message: string;

  /**
   * 詳細情報
   */
  details?: string;

}