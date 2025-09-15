#!/usr/bin/env python3
"""
Angular Generator - Angular DTO/サービス生成スクリプト
OpenAPI仕様からAngularのTypeScript型定義とAPIサービスを生成
"""

import os
import yaml
import logging
from datetime import datetime
from pathlib import Path
from jinja2 import Environment, FileSystemLoader
from .x_extension_parser import XExtensionParser

logger = logging.getLogger(__name__)


class AngularGenerator:
    """Angular生成クラス - マルチAPI対応"""
    
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
        self.base_output_dir = self.project_root / "output" / "frontend"
        
        # Jinja2環境の初期化
        template_dir = Path(__file__).parent.parent / "templates" / "angular"
        self.jinja_env = Environment(
            loader=FileSystemLoader(str(template_dir)),
            trim_blocks=True,
            lstrip_blocks=True
        )
        
        # x-拡張フィールドパーサーの初期化
        self.x_parser = XExtensionParser()
        
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
            'angular': {
                'api_base_url': 'http://localhost:8080/api',
                'models_dir': 'app/models',
                'services_dir': 'app/services',
                'interceptors': True,
                'error_handling': True
            },
            'features': {
                'reactive_forms': True,
                'validation': True,
                'http_client': True
            },
            'apis': {}  # API別設定（マルチAPI対応）
        }
        
    def get_api_module_name(self, api_name):
        """API名からAngularモジュール名を取得"""
        return api_name.lower()
    
    def get_api_output_dirs(self, api_name):
        """API別の出力ディレクトリを取得"""
        module_name = self.get_api_module_name(api_name)
        base_dir = self.base_output_dir / "app" / module_name
        return {
            'models': base_dir / "models",
            'services': base_dir / "services"
        }
    
    def get_api_base_url(self, api_name, config):
        """API別のベースURLを取得"""
        # API別設定がある場合はそれを使用
        if 'apis' in config and api_name in config['apis']:
            api_config = config['apis'][api_name]
            if 'angular' in api_config and 'api_base_url' in api_config['angular']:
                return api_config['angular']['api_base_url']
        
        # デフォルトURLを生成
        base_url = config.get('angular', {}).get('api_base_url', 'http://localhost:8080/api')
        return f"{base_url}/{api_name}"
        
    def extract_models_and_services_for_api(self, api_name, openapi_spec):
        """API別にモデルとサービスを抽出"""
        # スキーマからTypeScript interfaceを生成
        models = {}
        schemas = openapi_spec.get('components', {}).get('schemas', {})
        
        for schema_name, schema_def in schemas.items():
            interface_data = self.convert_schema_to_interface(schema_name, schema_def)
            interface_data['api_name'] = api_name
            models[schema_name] = interface_data
            
        # パスからAPIサービスを生成
        services = {}
        paths = openapi_spec.get('paths', {})
        
        for path, path_def in paths.items():
            for method, method_def in path_def.items():
                if method.upper() in ['GET', 'POST', 'PUT', 'DELETE', 'PATCH']:
                    service_name = self.extract_service_name_from_path(path, api_name)
                    if service_name not in services:
                        services[service_name] = {
                            'name': service_name,
                            'api_name': api_name,
                            'methods': []
                        }
                    
                    service_method = self.convert_path_to_service_method(path, method, method_def)
                    services[service_name]['methods'].append(service_method)
                    
        return models, services
        
    def convert_schema_to_interface(self, schema_name, schema_def):
        """OpenAPIスキーマをTypeScriptインターフェースに変換（x-拡張フィールド対応版）"""
        properties = schema_def.get('properties', {})
        required = schema_def.get('required', [])
        
        fields = []
        all_validators = []
        validator_imports = set()
        
        for prop_name, prop_def in properties.items():
            # x-拡張フィールドからバリデーション情報を生成
            validation_rules = self.x_parser.parse_property_extensions(prop_def)
            angular_validators = self.x_parser.to_angular_validators(validation_rules)
            
            # バリデーター情報をフィールドに追加
            field_validators = []
            for validator in angular_validators:
                field_validators.append({
                    'name': validator.validator_name,
                    'function': validator.validator_function,
                    'error_message': validator.error_message
                })
                validator_imports.add(validator.import_statement)
            
            field = {
                'name': prop_name,
                'type': self.openapi_type_to_typescript_type(prop_def),
                'optional': prop_name not in required,
                'description': prop_def.get('description', ''),
                'validators': field_validators,
                'x_extensions': self._extract_x_extensions(prop_def)
            }
            fields.append(field)
            all_validators.extend(field_validators)
            
        return {
            'name': schema_name,
            'fields': fields,
            'description': schema_def.get('description', ''),
            'validators': all_validators,
            'validator_imports': list(validator_imports)
        }
    
    def _extract_x_extensions(self, prop_def):
        """プロパティからx-拡張フィールドを抽出"""
        extensions = {}
        for key, value in prop_def.items():
            if key.startswith('x-'):
                extensions[key] = value
        return extensions
        
    def extract_service_name_from_path(self, path, api_name=None):
        """パスからサービス名を抽出（例: /users -> UserService）"""
        # パスの最初のセグメントをサービス名として使用
        segments = path.strip('/').split('/')
        
        # /api/users のような場合、"api" を除去
        if segments and segments[0] == 'api':
            segments = segments[1:]
            
        if segments:
            resource = segments[0]
            # 複数形を単数形に変換（簡単な実装）
            if resource.endswith('s'):
                resource = resource[:-1]
            service_name = f"{resource.capitalize()}Service"
            
            # API名が指定されている場合はプレフィックスとして使用
            if api_name and api_name.lower() != resource.lower():
                service_name = f"{api_name.capitalize()}{service_name}"
                
            return service_name
        return f"{api_name.capitalize()}Service" if api_name else "ApiService"
        
    def convert_path_to_service_method(self, path, method, method_def):
        """OpenAPIパスをAngularサービスメソッドに変換"""
        operation_id = method_def.get('operationId', f"{method}_{path.replace('/', '_')}")
        
        # パラメータを抽出
        parameters = []
        path_params = []
        query_params = []
        
        for param in method_def.get('parameters', []):
            # $refパラメータの場合はスキップ（現時点では完全な参照解決は実装しない）
            if '$ref' in param:
                logger.debug(f"パラメータ参照をスキップ: {param.get('$ref')}")
                continue
                
            # nameが存在しない場合はスキップ
            if 'name' not in param:
                logger.warning(f"パラメータに'name'がありません: {param}")
                continue
                
            param_info = {
                'name': param['name'],
                'type': self.openapi_type_to_typescript_type(param.get('schema', {})),
                'required': param.get('required', False),
                'description': param.get('description', '')
            }
            
            param_in = param.get('in', 'query')
            if param_in == 'path':
                path_params.append(param_info)
            elif param_in == 'query':
                query_params.append(param_info)
                
            parameters.append(param_info)
            
        # リクエストボディを抽出
        request_body = None
        request_body_def = method_def.get('requestBody')
        if request_body_def:
            content = request_body_def.get('content', {})
            json_content = content.get('application/json')
            if json_content and json_content.get('schema'):
                schema_ref = json_content['schema'].get('$ref', '')
                if schema_ref:
                    model_name = schema_ref.split('/')[-1]
                    request_body = {
                        'type': model_name,
                        'required': request_body_def.get('required', False)
                    }
                    
        # レスポンスタイプを抽出
        response_type = 'any'
        responses = method_def.get('responses', {})
        success_response = responses.get('200') or responses.get('201')
        if success_response:
            content = success_response.get('content', {})
            json_content = content.get('application/json')
            if json_content and json_content.get('schema'):
                schema = json_content['schema']
                response_type = self.openapi_schema_to_typescript_type(schema)
                
        return {
            'name': self.generate_method_name(method, path),
            'operation_id': operation_id,
            'http_method': method.upper(),
            'path': path,
            'parameters': parameters,
            'path_params': path_params,
            'query_params': query_params,
            'request_body': request_body,
            'response_type': response_type,
            'description': method_def.get('summary', ''),
            'detailed_description': method_def.get('description', '')
        }
        
    def generate_method_name(self, method, path):
        """HTTPメソッドとパスからメソッド名を生成"""
        method_lower = method.lower()
        
        # パスからリソース名を抽出
        segments = [s for s in path.strip('/').split('/') if not s.startswith('{')]
        resource = segments[0] if segments else 'resource'
        
        # メソッド名のマッピング
        method_mapping = {
            'get': 'get' if '{' in path else 'getAll',
            'post': 'create',
            'put': 'update',
            'patch': 'update', 
            'delete': 'delete'
        }
        
        action = method_mapping.get(method_lower, method_lower)
        
        if action == 'getAll':
            return f"get{resource.capitalize()}s"
        elif action == 'get':
            return f"get{resource.capitalize()}"
        else:
            return f"{action}{resource.capitalize()}"
            
    def openapi_type_to_typescript_type(self, prop_def):
        """OpenAPIの型をTypeScriptの型に変換"""
        prop_type = prop_def.get('type')
        prop_format = prop_def.get('format')
        
        if prop_type == 'string':
            if prop_format in ['date', 'date-time']:
                return 'Date'
            else:
                return 'string'
        elif prop_type == 'integer':
            return 'number'
        elif prop_type == 'number':
            return 'number' 
        elif prop_type == 'boolean':
            return 'boolean'
        elif prop_type == 'array':
            item_type = self.openapi_type_to_typescript_type(prop_def.get('items', {}))
            return f"{item_type}[]"
        elif prop_type == 'object':
            return 'any'  # より具体的な型が必要な場合は拡張
        else:
            return 'any'  # デフォルト
            
    def openapi_schema_to_typescript_type(self, schema):
        """OpenAPIスキーマをTypeScriptの型に変換"""
        if '$ref' in schema:
            return schema['$ref'].split('/')[-1]
        elif schema.get('type') == 'array':
            item_schema = schema.get('items', {})
            item_type = self.openapi_schema_to_typescript_type(item_schema)
            return f"{item_type}[]"
        else:
            return self.openapi_type_to_typescript_type(schema)
            
    def generate_interface(self, model_name, model):
        """TypeScriptインターフェースを生成"""
        interface_template = """/**
 * {{ model_name }} インターフェース
 * {{ model.description }}
 * TypeSpecから自動生成 - {{ generated_at }}
 */
export interface {{ model_name }} {
{% for field in model.fields %}
  /**
   * {{ field.description if field.description else field.name }}
   */
  {{ field.name }}{{ '?' if field.optional else '' }}: {{ field.type }};
{% endfor %}
}"""

        from jinja2 import Template
        template = Template(interface_template)
        return template.render(
            model_name=model_name,
            model=model,
            generated_at=datetime.now().isoformat()
        )
        
    def generate_service(self, service_name, service, models, api_base_url):
        """Angularサービスを生成"""
        service_template = """import { Injectable } from '@angular/core';
import { HttpClient, HttpParams } from '@angular/common/http';
import { Observable } from 'rxjs';

{% for model_name in models.keys() %}
import { {{ model_name }} } from '../models/{{ model_name.lower() }}.model';
{% endfor %}

/**
 * {{ service_name }}
 * {{ service.api_name|title }} API用サービス
 * TypeSpecから自動生成されたAPIサービス
 * 生成日時: {{ generated_at }}
 */
@Injectable({
  providedIn: 'root'
})
export class {{ service_name }} {

  private readonly baseUrl = '{{ api_base_url }}';

  constructor(private http: HttpClient) {}

{% for method in service.methods %}
  /**
   * {{ method.description }}
   * {{ method.detailed_description }}
   */
  {{ method.name }}({% for param in method.parameters %}{{ param.name }}{{ '?' if not param.required else '' }}: {{ param.type }}{{ ', ' if not loop.last else '' }}{% endfor %}{% if method.request_body %}{{ ', ' if method.parameters else '' }}body{{ '?' if not method.request_body.required else '' }}: {{ method.request_body.type }}{% endif %}): Observable<{{ method.response_type }}> {
    {% if method.path_params %}
    let url = `${this.baseUrl}{{ method.path }}`;
    {% for path_param in method.path_params %}
    url = url.replace('{' + '{{ path_param.name }}' + '}', {{ path_param.name }}.toString());
    {% endfor %}
    {% else %}
    const url = `${this.baseUrl}{{ method.path }}`;
    {% endif %}

    {% if method.query_params %}
    let params = new HttpParams();
    {% for query_param in method.query_params %}
    if ({{ query_param.name }} !== undefined) {
      params = params.set('{{ query_param.name }}', {{ query_param.name }}.toString());
    }
    {% endfor %}
    {% endif %}

    {% if method.http_method == 'GET' %}
    return this.http.get<{{ method.response_type }}>(url{% if method.query_params %}, { params }{% endif %});
    {% elif method.http_method == 'POST' %}
    return this.http.post<{{ method.response_type }}>(url, {% if method.request_body %}body{% else %}{}{% endif %}{% if method.query_params %}, { params }{% endif %});
    {% elif method.http_method == 'PUT' %}
    return this.http.put<{{ method.response_type }}>(url, {% if method.request_body %}body{% else %}{}{% endif %}{% if method.query_params %}, { params }{% endif %});
    {% elif method.http_method == 'PATCH' %}
    return this.http.patch<{{ method.response_type }}>(url, {% if method.request_body %}body{% else %}{}{% endif %}{% if method.query_params %}, { params }{% endif %});
    {% elif method.http_method == 'DELETE' %}
    return this.http.delete<{{ method.response_type }}>(url{% if method.query_params %}, { params }{% endif %});
    {% endif %}
  }

{% endfor %}
}"""

        from jinja2 import Template
        template = Template(service_template)
        return template.render(
            service_name=service_name,
            service=service,
            models=models,
            api_base_url=api_base_url,
            generated_at=datetime.now().isoformat()
        )
        
    def generate(self):
        """Angular生成のメイン処理 - マルチAPI対応"""
        try:
            # 複数OpenAPI仕様とコンフィグを読み込み
            openapi_specs = self.load_multiple_openapi_specs()
            config = self.load_config()
            
            # 各APIごとに生成
            for api_name, openapi_spec in openapi_specs.items():
                logger.info(f"{api_name} APIのAngularコードを生成中...")
                
                # モデルとサービスを抽出
                models, services = self.extract_models_and_services_for_api(api_name, openapi_spec)
                
                if not models:
                    logger.warning(f"{api_name} API: モデル定義が見つかりませんでした")
                    models = {}
                    
                if not services:
                    logger.warning(f"{api_name} API: API定義が見つかりませんでした")
                    services = {}
                    
                # API別の出力ディレクトリを取得
                output_dirs = self.get_api_output_dirs(api_name)
                api_base_url = self.get_api_base_url(api_name, config)
                
                # モデルディレクトリを作成してインターフェース生成
                if models:
                    output_dirs['models'].mkdir(parents=True, exist_ok=True)
                    
                    for model_name, model in models.items():
                        interface_content = self.generate_interface(model_name, model)
                        interface_file = output_dirs['models'] / f"{model_name.lower()}.model.ts"
                        
                        with open(interface_file, 'w', encoding='utf-8') as f:
                            f.write(interface_content)
                        logger.info(f"TypeScriptインターフェースを生成しました: {interface_file}")
                        
                # サービスディレクトリを作成してサービス生成
                if services:
                    output_dirs['services'].mkdir(parents=True, exist_ok=True)
                    
                    for service_name, service in services.items():
                        service_content = self.generate_service(service_name, service, models, api_base_url)
                        # サービス名からファイル名を生成（例: UserService -> user.service.ts）
                        service_file_name = service_name.lower().replace('service', '') + '.service.ts'
                        service_file = output_dirs['services'] / service_file_name
                        
                        with open(service_file, 'w', encoding='utf-8') as f:
                            f.write(service_content)
                        logger.info(f"Angularサービスを生成しました: {service_file}")
                        
                logger.info(f"{api_name} API生成完了: {len(models)}モデル, {len(services)}サービス")
                
        except Exception as e:
            import traceback
            logger.error(f"Angular生成中にエラーが発生しました: {e}")
            logger.error(f"トレースバック: {traceback.format_exc()}")
            raise
            
    def get_default_models(self):
        """デフォルトのモデル定義"""
        return {
            'User': {
                'name': 'User',
                'fields': [
                    {
                        'name': 'id',
                        'type': 'number',
                        'optional': True,
                        'description': 'ユーザーID'
                    },
                    {
                        'name': 'username',
                        'type': 'string',
                        'optional': False,
                        'description': 'ユーザー名'
                    },
                    {
                        'name': 'email',
                        'type': 'string',
                        'optional': False,
                        'description': 'メールアドレス'
                    },
                    {
                        'name': 'fullName',
                        'type': 'string',
                        'optional': True,
                        'description': '氏名'
                    },
                    {
                        'name': 'isActive',
                        'type': 'boolean',
                        'optional': True,
                        'description': 'アクティブフラグ'
                    }
                ],
                'description': 'ユーザー情報'
            }
        }
        
    def get_default_services(self):
        """デフォルトのサービス定義"""
        return {
            'UserService': {
                'name': 'UserService',
                'methods': [
                    {
                        'name': 'getUsers',
                        'operation_id': 'getUsers',
                        'http_method': 'GET',
                        'path': '/users',
                        'parameters': [],
                        'path_params': [],
                        'query_params': [],
                        'request_body': None,
                        'response_type': 'User[]',
                        'description': 'ユーザー一覧取得'
                    },
                    {
                        'name': 'getUser',
                        'operation_id': 'getUserById',
                        'http_method': 'GET',
                        'path': '/users/{id}',
                        'parameters': [
                            {
                                'name': 'id',
                                'type': 'number',
                                'required': True,
                                'description': 'ユーザーID'
                            }
                        ],
                        'path_params': [
                            {
                                'name': 'id',
                                'type': 'number',
                                'required': True,
                                'description': 'ユーザーID'
                            }
                        ],
                        'query_params': [],
                        'request_body': None,
                        'response_type': 'User',
                        'description': 'ユーザー詳細取得'
                    }
                ]
            }
        }


if __name__ == "__main__":
    generator = AngularGenerator("output/openapi/openapi.yaml")
    generator.generate()