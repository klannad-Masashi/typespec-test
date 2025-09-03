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

logger = logging.getLogger(__name__)


class AngularGenerator:
    """Angular生成クラス"""
    
    def __init__(self, openapi_path, config_path=None):
        self.openapi_path = openapi_path
        self.config_path = config_path
        self.project_root = Path(__file__).parent.parent.parent
        self.output_dir = self.project_root / "frontend" / "src"
        
        # Jinja2環境の初期化
        template_dir = self.project_root / "templates" / "angular"
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
            }
        }
        
    def extract_models_and_services(self, openapi_spec):
        """OpenAPI仕様からモデルとサービスを抽出"""
        # スキーマからTypeScript interfaceを生成
        models = {}
        schemas = openapi_spec.get('components', {}).get('schemas', {})
        
        for schema_name, schema_def in schemas.items():
            models[schema_name] = self.convert_schema_to_interface(schema_name, schema_def)
            
        # パスからAPIサービスを生成
        services = {}
        paths = openapi_spec.get('paths', {})
        
        for path, path_def in paths.items():
            for method, method_def in path_def.items():
                if method.upper() in ['GET', 'POST', 'PUT', 'DELETE', 'PATCH']:
                    service_name = self.extract_service_name_from_path(path)
                    if service_name not in services:
                        services[service_name] = {
                            'name': service_name,
                            'methods': []
                        }
                    
                    service_method = self.convert_path_to_service_method(path, method, method_def)
                    services[service_name]['methods'].append(service_method)
                    
        return models, services
        
    def convert_schema_to_interface(self, schema_name, schema_def):
        """OpenAPIスキーマをTypeScriptインターフェースに変換"""
        properties = schema_def.get('properties', {})
        required = schema_def.get('required', [])
        
        fields = []
        for prop_name, prop_def in properties.items():
            field = {
                'name': prop_name,
                'type': self.openapi_type_to_typescript_type(prop_def),
                'optional': prop_name not in required,
                'description': prop_def.get('description', '')
            }
            fields.append(field)
            
        return {
            'name': schema_name,
            'fields': fields,
            'description': schema_def.get('description', '')
        }
        
    def extract_service_name_from_path(self, path):
        """パスからサービス名を抽出（例: /users -> UserService）"""
        # パスの最初のセグメントをサービス名として使用
        segments = path.strip('/').split('/')
        if segments:
            resource = segments[0]
            # 複数形を単数形に変換（簡単な実装）
            if resource.endswith('s'):
                resource = resource[:-1]
            return f"{resource.capitalize()}Service"
        return "ApiService"
        
    def convert_path_to_service_method(self, path, method, method_def):
        """OpenAPIパスをAngularサービスメソッドに変換"""
        operation_id = method_def.get('operationId', f"{method}_{path.replace('/', '_')}")
        
        # パラメータを抽出
        parameters = []
        path_params = []
        query_params = []
        
        for param in method_def.get('parameters', []):
            param_info = {
                'name': param['name'],
                'type': self.openapi_type_to_typescript_type(param.get('schema', {})),
                'required': param.get('required', False),
                'description': param.get('description', '')
            }
            
            if param['in'] == 'path':
                path_params.append(param_info)
            elif param['in'] == 'query':
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
        
    def generate_service(self, service_name, service, models, config):
        """Angularサービスを生成"""
        service_template = """import { Injectable } from '@angular/core';
import { HttpClient, HttpParams } from '@angular/common/http';
import { Observable } from 'rxjs';
import { environment } from '../../environments/environment';

{% for model_name in models.keys() %}
import { {{ model_name }} } from '../models/{{ model_name.lower() }}.model';
{% endfor %}

/**
 * {{ service_name }}
 * TypeSpecから自動生成されたAPIサービス
 * 生成日時: {{ generated_at }}
 */
@Injectable({
  providedIn: 'root'
})
export class {{ service_name }} {

  private readonly baseUrl = '{{ config.angular.api_base_url }}';

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
    url = url.replace('{{{ path_param.name }}}', {{ path_param.name }}.toString());
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
            config=config,
            generated_at=datetime.now().isoformat()
        )
        
    def generate(self):
        """Angular生成のメイン処理"""
        try:
            # OpenAPI仕様とコンフィグを読み込み
            openapi_spec = self.load_openapi_spec()
            config = self.load_config()
            
            # モデルとサービスを抽出
            models, services = self.extract_models_and_services(openapi_spec)
            
            if not models:
                logger.warning("モデル定義が見つかりませんでした")
                models = self.get_default_models()
                
            if not services:
                logger.warning("API定義が見つかりませんでした")
                services = self.get_default_services()
                
            # 出力ディレクトリを作成
            self.output_dir.mkdir(parents=True, exist_ok=True)
            
            # モデルディレクトリを作成
            models_dir = self.output_dir / config['angular']['models_dir']
            models_dir.mkdir(parents=True, exist_ok=True)
            
            # TypeScriptインターフェースを生成
            for model_name, model in models.items():
                interface_content = self.generate_interface(model_name, model)
                interface_file = models_dir / f"{model_name.lower()}.model.ts"
                
                with open(interface_file, 'w', encoding='utf-8') as f:
                    f.write(interface_content)
                logger.info(f"TypeScriptインターフェースを生成しました: {interface_file}")
                
            # サービスディレクトリを作成
            services_dir = self.output_dir / config['angular']['services_dir']
            services_dir.mkdir(parents=True, exist_ok=True)
            
            # Angularサービスを生成
            for service_name, service in services.items():
                service_content = self.generate_service(service_name, service, models, config)
                service_file = services_dir / f"{service_name.lower().replace('service', '')}.service.ts"
                
                with open(service_file, 'w', encoding='utf-8') as f:
                    f.write(service_content)
                logger.info(f"Angularサービスを生成しました: {service_file}")
                
        except Exception as e:
            logger.error(f"Angular生成中にエラーが発生しました: {e}")
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
    generator = AngularGenerator("temp/openapi/openapi.yaml")
    generator.generate()