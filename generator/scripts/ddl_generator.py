#!/usr/bin/env python3
"""
DDL Generator - PostgreSQL DDL生成スクリプト
CSV形式のテーブル定義からPostgreSQLのDDLを生成
"""

import os
import csv
import yaml
import logging
from datetime import datetime
from pathlib import Path
from jinja2 import Environment, FileSystemLoader

logger = logging.getLogger(__name__)


class DDLGenerator:
    """PostgreSQL DDL生成クラス"""
    
    def __init__(self, csv_path=None, config_path=None):
        self.config_path = config_path
        self.project_root = Path(__file__).parent.parent.parent
        self.csv_dir = self.project_root / "output" / "csv"
        self.output_dir = self.project_root / "output" / "ddl"
        
        # CSVファイルパスの決定
        if csv_path:
            self.csv_path = csv_path
        else:
            self.csv_path = self.csv_dir / "table_definitions.csv"
        
        # Jinja2環境の初期化
        template_dir = Path(__file__).parent.parent / "templates" / "ddl"
        self.jinja_env = Environment(
            loader=FileSystemLoader(str(template_dir)),
            trim_blocks=True,
            lstrip_blocks=True
        )
        
    def load_csv_definitions(self):
        """CSVファイルからテーブル定義を読み込み"""
        try:
            tables = {}
            with open(self.csv_path, 'r', encoding='utf-8') as f:
                reader = csv.DictReader(f)
                
                for row in reader:
                    table_name = row['table_name']
                    
                    # テーブルが未登録の場合は初期化
                    if table_name not in tables:
                        tables[table_name] = {
                            'name': table_name,
                            'columns': []
                        }
                    
                    # カラム情報を追加
                    column = {
                        'name': row['column_name'],
                        'type': row['data_type'],
                        'nullable': row['nullable'].lower() == 'true',
                        'primary_key': row['primary_key'].lower() == 'true',
                        'unique': row['unique'].lower() == 'true',
                        'default': row['default_value'] if row['default_value'] else None,
                        'description': row.get('description', '')
                    }
                    
                    tables[table_name]['columns'].append(column)
                    
            return tables
            
        except Exception as e:
            logger.error(f"CSVファイルの読み込みに失敗: {e}")
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
            # CSVファイルとコンフィグを読み込み
            config = self.load_config()
            
            # CSVファイルの存在チェック
            if not os.path.exists(self.csv_path):
                logger.error(f"CSVファイルが見つかりません: {self.csv_path}")
                logger.info("先にCSV生成を実行してください")
                return
            
            # CSVからテーブル定義を読み込み
            tables = self.load_csv_definitions()
            
            if not tables:
                logger.warning("テーブル定義が見つかりませんでした")
                tables = self.get_default_tables()
                
            # DDLを生成
            ddl_content = self.generate_ddl(tables, config)
            
            # 出力ディレクトリを作成
            self.output_dir.mkdir(parents=True, exist_ok=True)
            
            # テーブル名からファイル名を生成（複数テーブルがある場合は最初のテーブル名を使用）
            table_names = list(tables.keys())
            if table_names:
                primary_table = table_names[0]  # 最初のテーブル名を使用
            else:
                primary_table = "schema"  # フォールバック
                
            # ファイル出力
            output_file = self.output_dir / f"{primary_table}.sql"
            with open(output_file, 'w', encoding='utf-8') as f:
                f.write(ddl_content)
                
            logger.info(f"PostgreSQL DDLを生成しました: {output_file}")
            
            # バックアップファイルも作成
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            backup_file = self.output_dir / f"{primary_table}_{timestamp}.sql"
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
    generator = DDLGenerator()
    generator.generate()