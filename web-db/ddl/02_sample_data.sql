-- サンプルデータ挿入
-- 作成日: 2025-09-11

-- 共通モデルの例
INSERT INTO models (name, description, is_common, is_active, api_id) VALUES
    ('BaseEntity', '共通基底エンティティ', true, true, NULL),
    ('ErrorResponse', '標準エラーレスポンス', true, true, NULL),
    ('PaginationInfo', 'ページネーション情報', true, true, NULL)
ON CONFLICT DO NOTHING;

-- BaseEntityのフィールド
WITH base_model AS (SELECT id FROM models WHERE name = 'BaseEntity' AND is_common = true)
INSERT INTO model_values (model_id, name, field_type, description, is_required, sort_order)
SELECT 
    base_model.id,
    field_data.name,
    field_data.field_type,
    field_data.description,
    field_data.is_required,
    field_data.sort_order
FROM base_model, (VALUES
    ('id', 'string', 'エンティティID', true, 1),
    ('createdAt', 'datetime', '作成日時', true, 2),
    ('updatedAt', 'datetime', '更新日時', true, 3)
) AS field_data(name, field_type, description, is_required, sort_order);

-- ErrorResponseのフィールド  
WITH error_model AS (SELECT id FROM models WHERE name = 'ErrorResponse' AND is_common = true)
INSERT INTO model_values (model_id, name, field_type, description, is_required, sort_order)
SELECT 
    error_model.id,
    field_data.name,
    field_data.field_type,
    field_data.description,
    field_data.is_required,
    field_data.sort_order
FROM error_model, (VALUES
    ('code', 'string', 'エラーコード', true, 1),
    ('message', 'string', 'エラーメッセージ', true, 2),
    ('details', 'string', 'エラー詳細', false, 3)
) AS field_data(name, field_type, description, is_required, sort_order);

-- PaginationInfoのフィールド
WITH pagination_model AS (SELECT id FROM models WHERE name = 'PaginationInfo' AND is_common = true)
INSERT INTO model_values (model_id, name, field_type, description, is_required, sort_order)
SELECT 
    pagination_model.id,
    field_data.name,
    field_data.field_type,
    field_data.description,
    field_data.is_required,
    field_data.sort_order
FROM pagination_model, (VALUES
    ('page', 'integer', 'ページ番号', true, 1),
    ('size', 'integer', 'ページサイズ', true, 2),
    ('total', 'integer', '総件数', true, 3),
    ('totalPages', 'integer', '総ページ数', true, 4)
) AS field_data(name, field_type, description, is_required, sort_order);

-- バリデーション制約の例
WITH page_field AS (
    SELECT mv.id FROM model_values mv
    JOIN models m ON mv.model_id = m.id
    WHERE m.name = 'PaginationInfo' AND mv.name = 'page'
)
INSERT INTO model_value_validations (model_value_id, validation_type, validation_value)
SELECT page_field.id, 'minimum', '1' FROM page_field;

WITH size_field AS (
    SELECT mv.id FROM model_values mv
    JOIN models m ON mv.model_id = m.id
    WHERE m.name = 'PaginationInfo' AND mv.name = 'size'
)
INSERT INTO model_value_validations (model_value_id, validation_type, validation_value)
SELECT size_field.id, validation_type, validation_value
FROM size_field, (VALUES
    ('minimum', '1'),
    ('maximum', '100')
) AS validation_data(validation_type, validation_value);