#!/usr/bin/env python3
"""
DDL Generator - PostgreSQL DDL生成スクリプト
OpenAPI仕様からPostgreSQLのテーブル定義を生成
"""

import os
import yaml
import logging
from datetime import datetime
from pathlib import Path
from jinja2 import Environment, FileSystemLoader

logger = logging.getLogger(__name__)


class DDLGenerator:
    """PostgreSQL DDL生成クラス"""
    
    def __init__(self, openapi_path, config_path=None):
        self.openapi_path = openapi_path
        self.config_path = config_path
        self.project_root = Path(__file__).parent.parent.parent
        self.output_dir = self.project_root / "database" / "ddl"
        
        # Jinja2環境の初期化
        template_dir = self.project_root / "templates" / "ddl"
        self.jinja_env = Environment(
            loader=FileSystemLoader(str(template_dir)),
            trim_blocks=True,
            lstrip_blocks=True
        )
        
    def load_openapi_spec(self):
        """OpenAPI仕様ファイルを読み込み"""
        try:
            with open(self.openapi_path, 'r', encoding='utf-8') as f:
                return yaml.safe_load(f)
        except Exception as e:
            logger.error(f"OpenAPI仕様ファイルの読み込みに失敗: {e}")
            raise
            
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
            'database': {
                'name': 'userdb',
                'extensions': ['uuid-ossp'],
                'create_indexes': True,
                'create_triggers': True,
                'insert_sample_data': True
            },
            'tables': {
                'users': {
                    'primary_key': 'id',
                    'indexes': ['username', 'email', 'is_active'],
                    'timestamps': True
                }
            }
        }
        
    def extract_table_definitions(self, openapi_spec):
        """OpenAPI仕様からテーブル定義を抽出"""
        tables = {}
        
        # OpenAPIのcomponentsセクションからスキーマを取得
        schemas = openapi_spec.get('components', {}).get('schemas', {})
        
        for schema_name, schema_def in schemas.items():
            # モデル名からテーブル名を生成（例: User -> users）
            table_name = self.model_name_to_table_name(schema_name)
            
            # プロパティからカラム定義を生成
            columns = self.extract_columns(schema_def.get('properties', {}))
            
            tables[table_name] = {
                'name': table_name,
                'columns': columns,
                'model_name': schema_name
            }
            
        return tables
        
    def model_name_to_table_name(self, model_name):
        """モデル名をテーブル名に変換（例: User -> users）"""
        # 簡単な複数形変換（実際はより複雑な変換が必要な場合がある）
        if model_name.lower() == 'user':
            return 'users'
        elif model_name.endswith('y'):
            return model_name[:-1].lower() + 'ies'
        elif model_name.endswith(('s', 'sh', 'ch', 'x', 'z')):
            return model_name.lower() + 'es'
        else:
            return model_name.lower() + 's'
            
    def extract_columns(self, properties):
        """プロパティからカラム定義を抽出"""
        columns = []
        
        for prop_name, prop_def in properties.items():
            column = self.property_to_column(prop_name, prop_def)
            columns.append(column)
            
        # 共通カラムの追加
        columns.extend([
            {
                'name': 'created_at',
                'type': 'TIMESTAMP WITH TIME ZONE',
                'nullable': False,
                'default': 'CURRENT_TIMESTAMP'
            },
            {
                'name': 'updated_at', 
                'type': 'TIMESTAMP WITH TIME ZONE',
                'nullable': False,
                'default': 'CURRENT_TIMESTAMP'
            }
        ])
        
        return columns
        
    def property_to_column(self, prop_name, prop_def):
        """プロパティをカラム定義に変換"""
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
                sql_type = 'VARCHAR(255)'
            elif prop_format == 'date-time':
                sql_type = 'TIMESTAMP WITH TIME ZONE'
            elif prop_format == 'uuid':
                sql_type = 'UUID'
            else:
                max_length = prop_def.get('maxLength', 255)
                sql_type = f'VARCHAR({max_length})'
        else:
            sql_type = type_mapping.get(prop_type, 'VARCHAR(255)')
            
        # Primary Keyの判定
        is_primary = prop_name.lower() == 'id'
        if is_primary:
            sql_type = 'SERIAL PRIMARY KEY' if prop_type == 'integer' else 'UUID PRIMARY KEY DEFAULT uuid_generate_v4()'
            
        return {
            'name': prop_name,
            'type': sql_type,
            'nullable': not prop_def.get('required', False) and not is_primary,
            'unique': prop_name in ['username', 'email'],
            'default': prop_def.get('default'),
            'primary_key': is_primary
        }
        
    def generate_ddl(self, tables, config):
        """DDLを生成"""
        try:
            template = self.jinja_env.get_template('schema.sql.j2')
        except Exception:
            # テンプレートファイルが存在しない場合はデフォルトのDDLを生成
            return self.generate_default_ddl(tables, config)
            
        return template.render(
            tables=tables,
            config=config,
            generated_at=datetime.now().isoformat(),
            database_name=config['database']['name']
        )
        
    def generate_default_ddl(self, tables, config):
        """デフォルトのDDL生成（テンプレートファイルがない場合）"""
        ddl_parts = []
        
        # ヘッダー
        ddl_parts.append(f"""-- TypeSpecから自動生成されたPostgreSQL DDL
-- 生成日時: {datetime.now().isoformat()}

-- データベース作成（必要に応じてコメントアウト）
-- CREATE DATABASE {config['database']['name']};
-- \\c {config['database']['name']};

-- 拡張機能の有効化""")
        
        for ext in config['database']['extensions']:
            ddl_parts.append(f'CREATE EXTENSION IF NOT EXISTS "{ext}";')
            
        ddl_parts.append("")
        
        # テーブル作成
        for table_name, table_def in tables.items():
            ddl_parts.append(f"-- {table_name}テーブル")
            ddl_parts.append(f"CREATE TABLE {table_name} (")
            
            column_defs = []
            for column in table_def['columns']:
                column_def = f"    {column['name']} {column['type']}"
                if not column['nullable']:
                    column_def += " NOT NULL"
                if column.get('unique'):
                    column_def += " UNIQUE"
                if column.get('default'):
                    column_def += f" DEFAULT {column['default']}"
                column_defs.append(column_def)
                
            ddl_parts.append(",\n".join(column_defs))
            ddl_parts.append(");")
            ddl_parts.append("")
            
        return "\n".join(ddl_parts)
        
    def generate(self):
        """DDL生成のメイン処理"""
        try:
            # OpenAPI仕様とコンフィグを読み込み
            openapi_spec = self.load_openapi_spec()
            config = self.load_config()
            
            # テーブル定義を抽出
            tables = self.extract_table_definitions(openapi_spec)
            
            if not tables:
                logger.warning("テーブル定義が見つかりませんでした")
                tables = self.get_default_tables()
                
            # DDLを生成
            ddl_content = self.generate_ddl(tables, config)
            
            # 出力ディレクトリを作成
            self.output_dir.mkdir(parents=True, exist_ok=True)
            
            # ファイル出力
            output_file = self.output_dir / "schema.sql"
            with open(output_file, 'w', encoding='utf-8') as f:
                f.write(ddl_content)
                
            logger.info(f"PostgreSQL DDLを生成しました: {output_file}")
            
            # バックアップファイルも作成
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            backup_file = self.output_dir / f"schema_{timestamp}.sql"
            with open(backup_file, 'w', encoding='utf-8') as f:
                f.write(ddl_content)
                
            logger.info(f"バックアップも作成しました: {backup_file}")
            
        except Exception as e:
            logger.error(f"DDL生成中にエラーが発生しました: {e}")
            raise
            
    def get_default_tables(self):
        """デフォルトのテーブル定義"""
        return {
            'users': {
                'name': 'users',
                'columns': [
                    {
                        'name': 'id',
                        'type': 'SERIAL PRIMARY KEY',
                        'nullable': False,
                        'primary_key': True
                    },
                    {
                        'name': 'username',
                        'type': 'VARCHAR(50)',
                        'nullable': False,
                        'unique': True
                    },
                    {
                        'name': 'email', 
                        'type': 'VARCHAR(255)',
                        'nullable': False,
                        'unique': True
                    },
                    {
                        'name': 'full_name',
                        'type': 'VARCHAR(100)',
                        'nullable': True
                    },
                    {
                        'name': 'is_active',
                        'type': 'BOOLEAN',
                        'nullable': False,
                        'default': 'true'
                    },
                    {
                        'name': 'created_at',
                        'type': 'TIMESTAMP WITH TIME ZONE',
                        'nullable': False,
                        'default': 'CURRENT_TIMESTAMP'
                    },
                    {
                        'name': 'updated_at',
                        'type': 'TIMESTAMP WITH TIME ZONE', 
                        'nullable': False,
                        'default': 'CURRENT_TIMESTAMP'
                    }
                ],
                'model_name': 'User'
            }
        }


if __name__ == "__main__":
    generator = DDLGenerator("temp/openapi/openapi.yaml")
    generator.generate()