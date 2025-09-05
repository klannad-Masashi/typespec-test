import "@typespec/http";
import "@typespec/rest";
import "@typespec/openapi3";
import "@typespec/versioning";
import "@typespec-test/common";
import "@typespec-test/models";

using TypeSpec.Http;
using TypeSpec.Rest;
using TypeSpec.Versioning;
using AuthModels;

@service({
  title: "Authentication API",
})
@server("http://localhost:8080", "Development server")
namespace AuthenticationAPI;

// モデルは@typespec-test/modelsパッケージから参照

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