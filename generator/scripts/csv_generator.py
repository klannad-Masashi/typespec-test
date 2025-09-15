#!/usr/bin/env python3
"""
CSV Generator - TypeSpecモデルからCSV形式のテーブル定義を生成
OpenAPI仕様からテーブル定義をCSV形式で出力し、DDL生成の中間ファイルとして使用
"""

import os
import yaml
import csv
import logging
from datetime import datetime
from pathlib import Path

logger = logging.getLogger(__name__)


class CSVGenerator:
    """CSV生成クラス - マルチAPI対応"""
    
    def __init__(self, openapi_files, config_path=None):
        """
        Args:
            openapi_files: dict または str
                dict: {api_name: file_path} の形式（マルチAPIモード）
                str: 単一ファイルパス（レガシーモード）
        """
        if isinstance(openapi_files, str):
            # レガシーモード：単一ファイル
            api_name = Path(openapi_files).stem
            if api_name == 'openapi':
                api_name = 'main'
            self.openapi_files = {api_name: openapi_files}
        else:
            # マルチAPIモード
            self.openapi_files = openapi_files
            
        self.config_path = config_path
        self.project_root = Path(__file__).parent.parent.parent
        self.output_dir = self.project_root / "output" / "csv"
        
    def load_multiple_openapi_specs(self):
        """複数のOpenAPI仕様ファイルを読み込み"""
        specs = {}
        for api_name, file_path in self.openapi_files.items():
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    specs[api_name] = yaml.safe_load(f)
                    logger.info(f"{api_name} API仕様を読み込みました: {file_path}")
            except Exception as e:
                logger.error(f"{api_name} API仕様ファイルの読み込みに失敗: {e}")
                raise
        return specs
            
    def load_config(self):
        """設定ファイルを読み込み"""
        if not self.config_path or not os.path.exists(self.config_path):
            return self.get_default_config()
            
        try:
            with open(self.config_path, 'r', encoding='utf-8') as f:
                return yaml.safe_load(f)
        except Exception as e:
            logger.warning(f"設定ファイルの読み込みに失敗、デフォルト設定を使用: {e}")
            return self.get_default_config()
            
    def get_default_config(self):
        """デフォルト設定を返す"""
        return {
            'csv': {
                'output_dir': 'output/csv',
                'table_definition_file': 'table_definitions.csv',
                'encoding': 'utf-8'
            }
        }
        
    def is_entity_model(self, schema_name, schema_def):
        """エンティティモデルかどうかを判定（Request/Response型を除外）"""
        # Request/Response/Error系の型名パターンを除外
        exclude_patterns = [
            'Request', 'Response', 'Error', 'List'
        ]
        
        for pattern in exclude_patterns:
            if pattern in schema_name:
                return False
                
        # プロパティにidフィールドがあるかチェック（エンティティの特徴）
        properties = schema_def.get('properties', {})
        has_id = 'id' in properties
        
        # createdAt, updatedAtがあるかチェック（エンティティの特徴）
        has_timestamps = 'createdAt' in properties and 'updatedAt' in properties
        
        # idがあるか、timestampsがある場合をエンティティとみなす
        return has_id or has_timestamps
        
    def model_name_to_table_name(self, model_name):
        """モデル名をテーブル名に変換（例: User -> users）"""
        # 簡単な複数形変換
        if model_name.lower() == 'user':
            return 'users'
        elif model_name.endswith('y'):
            return model_name[:-1].lower() + 'ies'
        elif model_name.endswith(('s', 'sh', 'ch', 'x', 'z')):
            return model_name.lower() + 'es'
        else:
            return model_name.lower() + 's'
            
    def openapi_type_to_sql_type(self, prop_def):
        """OpenAPIの型をSQL型に変換"""
        prop_type = prop_def.get('type', 'string')
        prop_format = prop_def.get('format')
        
        # TypeScriptの型からPostgreSQLの型へのマッピング
        type_mapping = {
            'string': 'VARCHAR(255)',
            'integer': 'INTEGER', 
            'number': 'DECIMAL',
            'boolean': 'BOOLEAN',
            'array': 'JSONB',
            'object': 'JSONB'
        }
        
        # フォーマットによる詳細な型指定
        if prop_type == 'string':
            if prop_format == 'email':
                return 'VARCHAR(255)'
            elif prop_format == 'date-time':
                return 'TIMESTAMP WITH TIME ZONE'
            elif prop_format == 'uuid':
                return 'UUID'
            else:
                max_length = prop_def.get('maxLength', 255)
                return f'VARCHAR({max_length})'
        elif prop_type == 'integer':
            # Primary Keyの場合はSERIALに
            return 'SERIAL' if prop_def.get('primary_key', False) else 'INTEGER'
        else:
            return type_mapping.get(prop_type, 'VARCHAR(255)')
            
    def extract_table_definitions_to_csv(self, openapi_specs):
        """複数のOpenAPI仕様からテーブル定義を抽出してCSV行のリストを作成"""
        csv_rows = []
        processed_tables = set()  # 重複テーブル名の管理
        
        # CSVヘッダー
        csv_rows.append([
            'api_name', 'table_name', 'column_name', 'data_type', 'nullable', 
            'primary_key', 'unique', 'default_value', 'description'
        ])
        
        # 各API仕様を処理
        for api_name, openapi_spec in openapi_specs.items():
            logger.info(f"{api_name} APIからテーブル定義を抽出中...")
            
            # OpenAPIのcomponentsセクションからスキーマを取得
            schemas = openapi_spec.get('components', {}).get('schemas', {})
            
            for schema_name, schema_def in schemas.items():
                # エンティティかどうかを判定
                if not self.is_entity_model(schema_name, schema_def):
                    continue
                    
                # モデル名からテーブル名を生成
                table_name = self.model_name_to_table_name(schema_name)
                
                # 重複テーブル名の処理
                full_table_name = f"{api_name}_{table_name}"
                if table_name in processed_tables:
                    logger.warning(f"重複するテーブル名を検出: {table_name} (API: {api_name})")
                    table_name = full_table_name
                else:
                    processed_tables.add(table_name)
                
                # プロパティからカラム定義を生成
                properties = schema_def.get('properties', {})
                required_fields = schema_def.get('required', [])
                
                for prop_name, prop_def in properties.items():
                    # Primary Keyの判定
                    is_primary = prop_name.lower() == 'id'
                    
                    # データ型の決定
                    if is_primary and prop_def.get('type') == 'integer':
                        data_type = 'SERIAL PRIMARY KEY'
                    else:
                        data_type = self.openapi_type_to_sql_type(prop_def)
                    
                    # Nullable判定
                    nullable = prop_name not in required_fields and not is_primary
                    
                    # Unique判定
                    unique = prop_name in ['username', 'email'] and not is_primary
                    
                    # デフォルト値
                    default_value = prop_def.get('default', '')
                    if default_value is True:
                        default_value = 'true'
                    elif default_value is False:
                        default_value = 'false'
                    elif default_value and prop_name in ['created_at', 'updated_at']:
                        default_value = 'CURRENT_TIMESTAMP'
                        
                    # 説明
                    description = prop_def.get('description', '')
                    
                    csv_rows.append([
                        api_name,
                        table_name,
                        prop_name, 
                        data_type,
                        'true' if nullable else 'false',
                        'true' if is_primary else 'false',
                        'true' if unique else 'false',
                        str(default_value),
                        description
                    ])
                    
                # 共通カラムの追加（TypeSpecで定義されていない場合）
                if 'createdAt' not in properties:
                    csv_rows.append([
                        api_name, table_name, 'created_at', 'TIMESTAMP WITH TIME ZONE',
                        'false', 'false', 'false', 'CURRENT_TIMESTAMP', 'レコード作成日時'
                    ])
                    
                if 'updatedAt' not in properties:
                    csv_rows.append([
                        api_name, table_name, 'updated_at', 'TIMESTAMP WITH TIME ZONE', 
                        'false', 'false', 'false', 'CURRENT_TIMESTAMP', 'レコード更新日時'
                    ])
                    
        return csv_rows
        
    def generate(self):
        """CSV生成のメイン処理 - マルチAPI対応"""
        try:
            # 複数OpenAPI仕様とコンフィグを読み込み
            openapi_specs = self.load_multiple_openapi_specs()
            config = self.load_config()
            
            # テーブル定義をCSV形式で抽出
            csv_rows = self.extract_table_definitions_to_csv(openapi_specs)
            
            if len(csv_rows) <= 1:  # ヘッダーのみの場合
                logger.warning("テーブル定義が見つかりませんでした")
                return
                
            # 出力ディレクトリを作成
            self.output_dir.mkdir(parents=True, exist_ok=True)
            
            # CSVファイル出力
            output_file = self.output_dir / config['csv']['table_definition_file']
            with open(output_file, 'w', encoding='utf-8', newline='') as f:
                writer = csv.writer(f)
                writer.writerows(csv_rows)
                
            logger.info(f"マルチAPIテーブル定義CSVを生成しました: {output_file}")
            
            # バックアップファイルも作成
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            backup_file = self.output_dir / f"table_definitions_{timestamp}.csv"
            with open(backup_file, 'w', encoding='utf-8', newline='') as f:
                writer = csv.writer(f)
                writer.writerows(csv_rows)
                
            logger.info(f"バックアップCSVも作成しました: {backup_file}")
            
            # API別統計をログ出力
            api_stats = {}
            for row in csv_rows[1:]:  # ヘッダー除外
                api_name = row[0]
                table_name = row[1]
                if api_name not in api_stats:
                    api_stats[api_name] = set()
                api_stats[api_name].add(table_name)
            
            for api_name, tables in api_stats.items():
                logger.info(f"{api_name} API: {len(tables)}テーブル ({', '.join(tables)})")
            
            total_tables = sum(len(tables) for tables in api_stats.values())
            logger.info(f"生成されたテーブル数: {total_tables}")
            
        except Exception as e:
            logger.error(f"CSV生成中にエラーが発生しました: {e}")
            raise


if __name__ == "__main__":
    generator = CSVGenerator("output/openapi/openapi.yaml")
    generator.generate()