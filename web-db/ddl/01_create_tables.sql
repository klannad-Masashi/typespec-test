-- TypeSpec Generator Database Schema
-- 作成日: 2025-09-11

-- APIプロジェクト管理テーブル
CREATE TABLE IF NOT EXISTS apis (
    id SERIAL PRIMARY KEY,
    name VARCHAR(100) NOT NULL UNIQUE,
    display_name VARCHAR(200),
    description TEXT,
    namespace VARCHAR(100),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    is_active BOOLEAN DEFAULT true
);

-- コメント追加
COMMENT ON TABLE apis IS 'API プロジェクト基本情報';
COMMENT ON COLUMN apis.name IS 'API識別名（英小文字、ハイフン可）';
COMMENT ON COLUMN apis.display_name IS '表示用API名';
COMMENT ON COLUMN apis.namespace IS 'TypeSpec名前空間';

-- モデル定義テーブル
CREATE TABLE IF NOT EXISTS models (
    id SERIAL PRIMARY KEY,
    api_id INTEGER REFERENCES apis(id) ON DELETE CASCADE,
    name VARCHAR(100) NOT NULL,
    description TEXT,
    is_common BOOLEAN DEFAULT false,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    is_active BOOLEAN DEFAULT true,
    UNIQUE(api_id, name),  -- 同一API内でモデル名は重複不可
    CONSTRAINT check_common_model CHECK (
        (is_common = true AND api_id IS NULL) OR 
        (is_common = false AND api_id IS NOT NULL)
    )
);

-- コメント追加
COMMENT ON TABLE models IS 'モデル定義（API固有または共通）';
COMMENT ON COLUMN models.api_id IS 'API ID（共通モデルの場合はNULL）';
COMMENT ON COLUMN models.is_common IS '共通モデルフラグ';
COMMENT ON COLUMN models.is_active IS 'アクティブ状態フラグ（論理削除用）';

-- モデル値定義テーブル
CREATE TABLE IF NOT EXISTS model_values (
    id SERIAL PRIMARY KEY,
    model_id INTEGER NOT NULL REFERENCES models(id) ON DELETE CASCADE,
    name VARCHAR(100) NOT NULL,
    field_type VARCHAR(50) NOT NULL,
    description TEXT,
    is_required BOOLEAN DEFAULT true,
    sort_order INTEGER DEFAULT 0,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(model_id, name)  -- 同一モデル内でフィールド名は重複不可
);

-- コメント追加
COMMENT ON TABLE model_values IS 'モデル値定義';
COMMENT ON COLUMN model_values.field_type IS 'フィールド型（string, integer, boolean等）';
COMMENT ON COLUMN model_values.sort_order IS 'フィールド表示順序';

-- モデル値バリデーション制約テーブル
CREATE TABLE IF NOT EXISTS model_value_validations (
    id SERIAL PRIMARY KEY,
    model_value_id INTEGER NOT NULL REFERENCES model_values(id) ON DELETE CASCADE,
    validation_type VARCHAR(50) NOT NULL,  -- minLength, maxLength, minimum, maximum, pattern, format
    validation_value TEXT NOT NULL,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- コメント追加
COMMENT ON TABLE model_value_validations IS 'モデル値バリデーション制約';
COMMENT ON COLUMN model_value_validations.validation_type IS 'バリデーション種類（minLength, maxLength等）';
COMMENT ON COLUMN model_value_validations.validation_value IS 'バリデーション値';

-- エンドポイント定義テーブル
CREATE TABLE IF NOT EXISTS endpoints (
    id SERIAL PRIMARY KEY,
    api_id INTEGER NOT NULL REFERENCES apis(id) ON DELETE CASCADE,
    method VARCHAR(10) NOT NULL,  -- GET, POST, PUT, DELETE, PATCH
    path VARCHAR(500) NOT NULL,
    operation_id VARCHAR(100) NOT NULL,
    description TEXT,
    request_model_id INTEGER REFERENCES models(id) ON DELETE SET NULL,
    response_model_id INTEGER REFERENCES models(id) ON DELETE SET NULL,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(api_id, method, path)  -- 同一API内で同一メソッド＋パスは重複不可
);

-- コメント追加
COMMENT ON TABLE endpoints IS 'API エンドポイント定義';
COMMENT ON COLUMN endpoints.method IS 'HTTPメソッド';
COMMENT ON COLUMN endpoints.operation_id IS 'TypeSpec操作ID';

-- エラーレスポンス定義テーブル
CREATE TABLE IF NOT EXISTS error_responses (
    id SERIAL PRIMARY KEY,
    endpoint_id INTEGER NOT NULL REFERENCES endpoints(id) ON DELETE CASCADE,
    status_code INTEGER NOT NULL,
    description TEXT,
    response_model_id INTEGER REFERENCES models(id) ON DELETE SET NULL,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(endpoint_id, status_code)  -- 同一エンドポイントで同一ステータスコードは重複不可
);

-- コメント追加
COMMENT ON TABLE error_responses IS 'エンドポイントエラーレスポンス定義';
COMMENT ON COLUMN error_responses.status_code IS 'HTTPステータスコード（400, 404等）';

-- Enum定義テーブル
CREATE TABLE IF NOT EXISTS enums (
    id SERIAL PRIMARY KEY,
    name VARCHAR(100) NOT NULL UNIQUE,
    description TEXT,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    is_active BOOLEAN DEFAULT true
);

-- コメント追加
COMMENT ON TABLE enums IS 'Enum定義';
COMMENT ON COLUMN enums.name IS 'Enum名（英大文字、アンダースコア可）';

-- Enum値定義テーブル
CREATE TABLE IF NOT EXISTS enum_values (
    id SERIAL PRIMARY KEY,
    enum_id INTEGER NOT NULL REFERENCES enums(id) ON DELETE CASCADE,
    name VARCHAR(100) NOT NULL,
    description TEXT,
    sort_order INTEGER DEFAULT 0,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(enum_id, name)  -- 同一Enum内で値名は重複不可
);

-- コメント追加
COMMENT ON TABLE enum_values IS 'Enum値定義';
COMMENT ON COLUMN enum_values.name IS 'Enum値名';
COMMENT ON COLUMN enum_values.sort_order IS 'Enum値表示順序';

-- インデックス作成
CREATE INDEX IF NOT EXISTS idx_apis_name ON apis(name);
CREATE INDEX IF NOT EXISTS idx_models_api_id ON models(api_id);
CREATE INDEX IF NOT EXISTS idx_models_is_common ON models(is_common);
CREATE INDEX IF NOT EXISTS idx_models_is_active ON models(is_active);
CREATE INDEX IF NOT EXISTS idx_model_values_model_id ON model_values(model_id);
CREATE INDEX IF NOT EXISTS idx_endpoints_api_id ON endpoints(api_id);
CREATE INDEX IF NOT EXISTS idx_error_responses_endpoint_id ON error_responses(endpoint_id);
CREATE INDEX IF NOT EXISTS idx_enums_name ON enums(name);
CREATE INDEX IF NOT EXISTS idx_enum_values_enum_id ON enum_values(enum_id);

-- 更新時刻自動更新のためのトリガー関数
CREATE OR REPLACE FUNCTION update_updated_at()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = CURRENT_TIMESTAMP;
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

-- 更新時刻自動更新トリガー
CREATE TRIGGER trigger_apis_updated_at
    BEFORE UPDATE ON apis
    FOR EACH ROW
    EXECUTE FUNCTION update_updated_at();

CREATE TRIGGER trigger_models_updated_at
    BEFORE UPDATE ON models
    FOR EACH ROW
    EXECUTE FUNCTION update_updated_at();

CREATE TRIGGER trigger_endpoints_updated_at
    BEFORE UPDATE ON endpoints
    FOR EACH ROW
    EXECUTE FUNCTION update_updated_at();

CREATE TRIGGER trigger_enums_updated_at
    BEFORE UPDATE ON enums
    FOR EACH ROW
    EXECUTE FUNCTION update_updated_at();