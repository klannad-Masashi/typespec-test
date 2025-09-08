#!/usr/bin/env python3
"""
Java Enum Generator - Java Enumクラス生成スクリプト
OpenAPI仕様からx-makeEnumJava=trueが付与されたenum定義を抽出してJava Enumクラスを生成
"""

import os
import yaml
import logging
import re
from datetime import datetime
from pathlib import Path
from jinja2 import Environment, FileSystemLoader

logger = logging.getLogger(__name__)


class JavaEnumGenerator:
    """Java Enum生成クラス"""
    
    def __init__(self, openapi_files, config_path=None):
        """
        Args:
            openapi_files: dict または str
                dict: {api_name: file_path} の形式（マルチAPIモード）
                str: 単一ファイルパス（レガシーモード）
        """
        if isinstance(openapi_files, str):
            # レガシーモード：単一ファイル
            api_name = Path(openapi_files).stem.replace('-api', '')
            if api_name == 'openapi':
                api_name = 'main'
            self.openapi_files = {api_name: openapi_files}
        else:
            # マルチAPIモード
            self.openapi_files = openapi_files
            
        self.config_path = config_path
        self.project_root = Path(__file__).parent.parent.parent
        
        # Jinja2環境の初期化
        template_dir = Path(__file__).parent.parent / "templates" / "java"
        self.jinja_env = Environment(
            loader=FileSystemLoader(str(template_dir)),
            trim_blocks=True,
            lstrip_blocks=True
        )
        
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
            'global': {
                'output_base': 'output/'
            },
            'java_enum': {
                'base_package': 'com.example.api',
                'output_dir': 'output/backend/src/main/java',
                'enum_package': 'enums'
            }
        }
        
    def extract_java_enums(self, specs):
        """x-makeEnumJava=trueが付与されたenum定義を抽出"""
        java_enums = []
        
        for api_name, spec in specs.items():
            if 'components' not in spec or 'schemas' not in spec['components']:
                continue
                
            schemas = spec['components']['schemas']
            for schema_name, schema_def in schemas.items():
                # enumかつx-makeEnumJava=trueの場合
                if (isinstance(schema_def, dict) and 
                    schema_def.get('type') == 'string' and
                    'enum' in schema_def and
                    schema_def.get('x-makeEnumJava') == True):
                    
                    enum_info = self.parse_enum_definition(schema_name, schema_def)
                    enum_info['api_name'] = api_name
                    java_enums.append(enum_info)
                    logger.info(f"Java Enum対象を検出: {schema_name} (API: {api_name})")
                    
        return java_enums
        
    def parse_enum_definition(self, schema_name, schema_def):
        """enum定義を解析してJava生成用の情報を抽出"""
        # クラス名を生成（TypeSpecGen.Enums.ProductCategory -> ProductCategory）
        class_name = schema_name.split('.')[-1] if '.' in schema_name else schema_name
        
        # enum値を解析
        enum_values = []
        for value in schema_def['enum']:
            # 値からJava定数名を生成
            # available -> AVAILABLE, out_of_stock -> OUT_OF_STOCK
            constant_name = self.to_java_constant_name(value)
            enum_values.append({
                'name': constant_name,
                'value': value
            })
            
        return {
            'original_name': schema_name,
            'class_name': class_name,
            'description': schema_def.get('description', f'{class_name} enum'),
            'enum_values': enum_values
        }
        
    def to_java_constant_name(self, value):
        """文字列値をJava定数名に変換"""
        # snake_case や kebab-case を UPPER_CASE に変換
        constant = re.sub(r'[-\s]', '_', value)
        constant = re.sub(r'([a-z0-9])([A-Z])', r'\1_\2', constant)
        return constant.upper()
        
    def generate_enum_file(self, enum_info, config):
        """Java Enumファイルを生成"""
        template = self.jinja_env.get_template('enum.java.j2')
        
        # パッケージ名を生成
        base_package = config.get('java_enum', {}).get('base_package', 'com.example.api')
        enum_package = config.get('java_enum', {}).get('enum_package', 'enums')
        package_name = f"{base_package}.{enum_package}"
        
        # テンプレート変数
        template_vars = {
            'package_name': package_name,
            'class_name': enum_info['class_name'],
            'description': enum_info['description'],
            'enum_values': enum_info['enum_values'],
            'original_name': enum_info['original_name'],
            'generated_at': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
            'api_name': enum_info.get('api_name', 'unknown')
        }
        
        return template.render(**template_vars)
        
    def write_enum_files(self, java_enums, config):
        """Java Enumファイルを出力"""
        output_base = config.get('java_enum', {}).get('output_dir', 'output/backend/src/main/java')
        base_package = config.get('java_enum', {}).get('base_package', 'com.example.api')
        enum_package = config.get('java_enum', {}).get('enum_package', 'enums')
        
        # パッケージディレクトリを作成
        package_path = Path(output_base) / base_package.replace('.', '/') / enum_package
        package_path.mkdir(parents=True, exist_ok=True)
        
        generated_files = []
        
        for enum_info in java_enums:
            # Java ファイル内容を生成
            java_content = self.generate_enum_file(enum_info, config)
            
            # ファイルパスを生成
            file_name = f"{enum_info['class_name']}.java"
            file_path = package_path / file_name
            
            # ファイルを書き出し
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(java_content)
                
            generated_files.append(str(file_path))
            logger.info(f"Java Enumファイルを生成: {file_path}")
            
        return generated_files
        
    def generate(self):
        """Java Enum生成のメイン処理"""
        logger.info("Java Enum生成を開始...")
        
        try:
            # 設定を読み込み
            config = self.load_config()
            
            # OpenAPI仕様を読み込み
            specs = self.load_multiple_openapi_specs()
            
            # Java Enum対象を抽出
            java_enums = self.extract_java_enums(specs)
            
            if not java_enums:
                logger.warning("x-makeEnumJava=trueが付与されたenum定義が見つかりませんでした")
                return []
                
            logger.info(f"{len(java_enums)}個のJava Enum定義を検出しました")
            
            # Java Enumファイルを生成・出力
            generated_files = self.write_enum_files(java_enums, config)
            
            logger.info(f"Java Enum生成完了: {len(generated_files)}ファイル")
            return generated_files
            
        except Exception as e:
            logger.error(f"Java Enum生成中にエラーが発生: {e}")
            raise


if __name__ == "__main__":
    # テスト実行
    logging.basicConfig(level=logging.INFO, format='%(levelname)s - %(message)s')
    
    # テスト用のOpenAPIファイル
    openapi_files = {
        'product': 'output/openapi/product-api.yaml',
        'auth': 'output/openapi/auth-api.yaml'
    }
    
    generator = JavaEnumGenerator(openapi_files)
    generator.generate()