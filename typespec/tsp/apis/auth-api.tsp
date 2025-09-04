import "@typespec/http";
import "@typespec/rest";
import "@typespec/openapi3";
import "@typespec/versioning";
import "../common/base-types.tsp";

using TypeSpec.Http;
using TypeSpec.Rest;
using TypeSpec.Versioning;

@service({
  title: "Authentication API",
})
@server("http://localhost:8080", "Development server")
namespace AuthenticationAPI;

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

// 認証ユーザー情報
@doc("認証ユーザー情報")
model AuthUser {
  @doc("ユーザーID")
  @key
  id: int32;

  @doc("ユーザー名")
  username: string;

  @doc("メールアドレス")
  email: string;

  @doc("フルネーム")
  fullName: string;

  @doc("ユーザーロール")
  role: UserRole;

  @doc("最終ログイン日時")
  lastLoginAt?: utcDateTime;

  @doc("アカウント有効フラグ")
  isActive: boolean = true;

  // 共通のタイムスタンプを継承
  ...TimestampFields;
}

// ログインリクエスト
@doc("ログインリクエスト")
model LoginRequest {
  @doc("ユーザー名またはメールアドレス")
  @minLength(1)
  identifier: string;

  @doc("パスワード")
  @minLength(8)
  @maxLength(128)
  password: string;

  @doc("ログイン状態を記憶するか")
  rememberMe?: boolean = false;
}

// パスワードリセットリクエスト
@doc("パスワードリセットリクエスト")
model PasswordResetRequest {
  @doc("メールアドレス")
  @format("email")
  email: string;
}

// パスワード変更リクエスト
@doc("パスワード変更リクエスト")
model ChangePasswordRequest {
  @doc("現在のパスワード")
  @minLength(8)
  @maxLength(128)
  currentPassword: string;

  @doc("新しいパスワード")
  @minLength(8)
  @maxLength(128)
  newPassword: string;

  @doc("新しいパスワード（確認）")
  @minLength(8)
  @maxLength(128)
  confirmPassword: string;
}

// ユーザー登録リクエスト
@doc("ユーザー登録リクエスト")
model RegisterRequest {
  @doc("ユーザー名")
  @minLength(3)
  @maxLength(50)
  username: string;

  @doc("メールアドレス")
  @format("email")
  email: string;

  @doc("パスワード")
  @minLength(8)
  @maxLength(128)
  password: string;

  @doc("フルネーム")
  @maxLength(100)
  fullName: string;
}

// トークンリフレッシュリクエスト
@doc("トークンリフレッシュリクエスト")
model RefreshTokenRequest {
  @doc("リフレッシュトークン")
  refreshToken: string;
}

// レスポンス型定義
@doc("ログインレスポンス")
model LoginResponse {
  @doc("アクセストークン")
  accessToken: string;

  @doc("リフレッシュトークン")
  refreshToken: string;

  @doc("トークンタイプ（通常はBearer）")
  tokenType: "Bearer";

  @doc("トークン有効期限（秒）")
  expiresIn: int32;

  @doc("認証ユーザー情報")
  user: AuthUser;

  @doc("ログイン試行結果")
  result: LoginResult;
}

@doc("トークンリフレッシュレスポンス")
model RefreshTokenResponse {
  @doc("新しいアクセストークン")
  accessToken: string;

  @doc("新しいリフレッシュトークン")
  refreshToken?: string;

  @doc("トークンタイプ（通常はBearer）")
  tokenType: "Bearer";

  @doc("トークン有効期限（秒）")
  expiresIn: int32;
}

@doc("ユーザー登録レスポンス")
model RegisterResponse {
  @doc("登録されたユーザー情報")
  user: AuthUser;

  @doc("確認メール送信済みフラグ")
  emailVerificationSent: boolean;
}

@doc("パスワードリセットレスポンス")
model PasswordResetResponse {
  @doc("リセットメール送信済みフラグ")
  emailSent: boolean;

  @doc("メッセージ")
  message: string;
}

@doc("パスワード変更レスポンス")
model ChangePasswordResponse {
  @doc("変更成功フラグ")
  success: boolean;

  @doc("メッセージ")
  message: string;
}

@doc("ユーザー情報レスポンス")
model UserProfileResponse {
  @doc("ユーザー情報")
  user: AuthUser;
}

// API エンドポイント定義
@tag("Authentication")
@route("/api/auth")
namespace Auth {
  @doc("ユーザーログイン")
  @post
  @route("/login")
  op login(
    @doc("ログイン認証データ")
    @body loginData: LoginRequest
  ): LoginResponse | ErrorResponse;

  @doc("ユーザー登録")
  @post
  @route("/register")
  op register(
    @doc("ユーザー登録データ")
    @body registerData: RegisterRequest
  ): RegisterResponse | ErrorResponse;

  @doc("ログアウト")
  @post
  @route("/logout")
  op logout(): DeleteResponse | ErrorResponse;

  @doc("トークンリフレッシュ")
  @post
  @route("/refresh")
  op refreshToken(
    @doc("リフレッシュトークンデータ")
    @body refreshData: RefreshTokenRequest
  ): RefreshTokenResponse | ErrorResponse;

  @doc("パスワードリセット要求")
  @post
  @route("/password/reset")
  op requestPasswordReset(
    @doc("パスワードリセット要求データ")
    @body resetData: PasswordResetRequest
  ): PasswordResetResponse | ErrorResponse;

  @doc("パスワード変更")
  @put
  @route("/password/change")
  op changePassword(
    @doc("パスワード変更データ")
    @body passwordData: ChangePasswordRequest
  ): ChangePasswordResponse | ErrorResponse;

  @doc("現在のユーザー情報取得")
  @get
  @route("/me")
  op getCurrentUser(): UserProfileResponse | ErrorResponse;

  @doc("トークン検証")
  @post
  @route("/verify")
  op verifyToken(): UserProfileResponse | ErrorResponse;
}