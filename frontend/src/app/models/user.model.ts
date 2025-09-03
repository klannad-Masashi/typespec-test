/**
 * User インターフェース
 * ユーザー情報
 * TypeSpecから自動生成 - 2025-09-03T01:10:28.129733
 */
export interface User {

  /**
   * ユーザーID（自動生成）
   */
  id: number;

  /**
   * ユーザー名
   */
  username: string;

  /**
   * メールアドレス
   */
  email: string;

  /**
   * フルネーム
   */
  fullName: string;

  /**
   * 作成日時
   */
  createdAt: Date;

  /**
   * 更新日時
   */
  updatedAt: Date;

  /**
   * アクティブフラグ
   */
  isActive: boolean;

}