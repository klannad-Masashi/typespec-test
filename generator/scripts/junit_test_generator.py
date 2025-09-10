#!/usr/bin/env python3
"""
JUnit Test Generator - JUnit 5テストコード生成スクリプト
Spring Generatorで生成されたメタデータからJUnit 5テストコードを生成
"""

import os
import json
import yaml
import logging
from datetime import datetime
from pathlib import Path
from jinja2 import Environment, FileSystemLoader

logger = logging.getLogger(__name__)


class JunitTestGenerator:
    """JUnit 5テスト生成クラス"""
    
    def __init__(self, config_path=None):
        self.config_path = config_path
        self.project_root = Path(__file__).parent.parent.parent
        
        # Jinja2環境の初期化
        template_dir = Path(__file__).parent.parent / "templates" / "junit"
        self.jinja_env = Environment(
            loader=FileSystemLoader(str(template_dir)),
            trim_blocks=True,
            lstrip_blocks=True
        )
        
    def load_config(self):
        """設定ファイルを読み込み"""
        if not self.config_path or not os.path.exists(self.config_path):
            return self.get_default_config()
            
        try:
            with open(self.config_path, 'r', encoding='utf-8') as f:
                config = yaml.safe_load(f)
                return config
        except Exception as e:
            logger.warning(f"設定ファイルの読み込みに失敗、デフォルト設定を使用: {e}")
            return self.get_default_config()
            
    def get_default_config(self):
        """デフォルト設定を返す"""
        return {
            'junit': {
                'base_package': 'com.example.api',
                'output_dir': 'output/backend/src/test/java',
                'include_integration_tests': True,
                'mock_external_dependencies': True
            }
        }
        
    def load_spring_metadata(self):
        """Spring生成メタデータを読み込み"""
        metadata_file = self.project_root / "output" / "metadata" / "spring_metadata.json"
        
        if not metadata_file.exists():
            raise FileNotFoundError(f"Spring メタデータファイルが見つかりません: {metadata_file}")
            
        with open(metadata_file, 'r', encoding='utf-8') as f:
            return json.load(f)
            
    def generate_controller_test(self, controller_info, config):
        """Controller テストクラスを生成"""
        template = self.jinja_env.get_template('controller_test.java.j2')
        
        # エンドポイント情報を解析
        endpoints = self.parse_endpoints(controller_info.get('endpoints', {}))
        
        template_vars = {
            'controller_info': controller_info,
            'endpoints': endpoints,
            'config': config,
            'generated_at': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
            'package_name': controller_info['package']
        }
        
        return template.render(**template_vars)
        
    def generate_dto_validation_test(self, dto_info, config):
        """DTO バリデーションテストクラスを生成"""
        template = self.jinja_env.get_template('dto_validation_test.java.j2')
        
        template_vars = {
            'dto_info': dto_info,
            'config': config,
            'generated_at': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
            'package_name': dto_info['package']
        }
        
        return template.render(**template_vars)
        
    def parse_endpoints(self, endpoints_data):
        """エンドポイント情報を解析してテスト生成用に整形"""
        parsed_endpoints = []
        
        for endpoint_key, endpoint_info in endpoints_data.items():
            parsed_endpoint = {
                'key': endpoint_key,
                'method': endpoint_info.get('method', 'GET'),
                'path': endpoint_info.get('path', '/'),
                'operation_id': endpoint_info.get('operation_id', ''),
                'description': endpoint_info.get('description', ''),
                'parameters': self.parse_parameters(endpoint_info.get('parameters', [])),
                'request_body': endpoint_info.get('request_body'),
                'responses': endpoint_info.get('responses', {})
            }
            parsed_endpoints.append(parsed_endpoint)
            
        return parsed_endpoints
        
    def parse_parameters(self, parameters):
        """パラメータ情報を解析"""
        parsed_params = []
        
        for param in parameters:
            if isinstance(param, dict) and '$ref' in param:
                # $ref は簡略化して処理
                ref_name = param['$ref'].split('/')[-1]
                parsed_params.append({
                    'name': ref_name,
                    'type': 'String',
                    'location': 'query',
                    'required': False
                })
            else:
                # 直接定義されたパラメータ
                parsed_params.append({
                    'name': param.get('name', 'unknown'),
                    'type': self.java_type_from_schema(param.get('schema', {})),
                    'location': param.get('in', 'query'),
                    'required': param.get('required', False)
                })
                
        return parsed_params
        
    def java_type_from_schema(self, schema):
        """OpenAPIスキーマからJavaの型を推定"""
        if not schema:
            return 'String'
            
        schema_type = schema.get('type', 'string')
        schema_format = schema.get('format')
        
        type_mapping = {
            'string': 'String',
            'integer': 'Integer',
            'number': 'Double',
            'boolean': 'Boolean',
            'array': 'List<String>'
        }
        
        java_type = type_mapping.get(schema_type, 'String')
        
        # format による細分化
        if schema_type == 'integer' and schema_format == 'int64':
            java_type = 'Long'
        elif schema_type == 'integer' and schema_format == 'int32':
            java_type = 'Integer'
            
        return java_type
        
    def write_test_files(self, controllers, dtos, config):
        """テストファイルを出力"""
        output_base = config.get('junit', {}).get('output_dir', 'output/backend/src/test/java')
        base_path = Path(output_base)
        
        generated_files = []
        
        # Controller テストを生成
        for controller_info in controllers:
            test_content = self.generate_controller_test(controller_info, config)
            
            # パッケージパスを生成
            package_parts = controller_info['package'].split('.')
            # .controllerをそのまま使用
            package_path = base_path / '/'.join(package_parts)
            package_path.mkdir(parents=True, exist_ok=True)
            
            # ファイル名生成
            test_file_name = f"{controller_info['class_name']}Test.java"
            test_file_path = package_path / test_file_name
            
            # ファイル書き出し
            with open(test_file_path, 'w', encoding='utf-8') as f:
                f.write(test_content)
                
            generated_files.append(str(test_file_path))
            logger.info(f"Controller テストを生成: {test_file_path}")
            
        # DTO テストを生成
        for dto_info in dtos:
            # バリデーションがあるDTOのみテスト生成
            if not any(field.get('validations') for field in dto_info.get('fields', [])):
                continue
                
            test_content = self.generate_dto_validation_test(dto_info, config)
            
            # パッケージパスを生成
            package_parts = dto_info['package'].split('.')
            # .dtoをそのまま使用
            package_path = base_path / '/'.join(package_parts)
            package_path.mkdir(parents=True, exist_ok=True)
            
            # ファイル名生成
            test_file_name = f"{dto_info['class_name']}Test.java"
            test_file_path = package_path / test_file_name
            
            # ファイル書き出し
            with open(test_file_path, 'w', encoding='utf-8') as f:
                f.write(test_content)
                
            generated_files.append(str(test_file_path))
            logger.info(f"DTO テストを生成: {test_file_path}")
            
        return generated_files
        
    def generate(self):
        """JUnit テスト生成のメイン処理"""
        logger.info("JUnit テスト生成を開始...")
        
        try:
            # 設定とメタデータを読み込み
            config = self.load_config()
            metadata = self.load_spring_metadata()
            
            controllers = metadata.get('controllers', [])
            dtos = metadata.get('dtos', [])
            
            if not controllers and not dtos:
                logger.warning("テスト生成対象が見つかりませんでした")
                return []
                
            logger.info(f"テスト生成対象: Controller {len(controllers)}個, DTO {len(dtos)}個")
            
            # テストファイルを生成・出力
            generated_files = self.write_test_files(controllers, dtos, config)
            
            logger.info(f"JUnit テスト生成完了: {len(generated_files)}ファイル")
            return generated_files
            
        except Exception as e:
            logger.error(f"JUnit テスト生成中にエラーが発生: {e}")
            raise


if __name__ == "__main__":
    # テスト実行
    logging.basicConfig(level=logging.INFO, format='%(levelname)s - %(message)s')
    
    generator = JunitTestGenerator()
    generator.generate()