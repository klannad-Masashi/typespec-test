#!/usr/bin/env python3
"""
Spring Generator - Spring Boot Controller/DTO生成スクリプト
OpenAPI仕様からSpring Bootのコントローラーとドメインオブジェクトを生成
"""

import os
import yaml
import json
import logging
from datetime import datetime
from pathlib import Path
from jinja2 import Environment, FileSystemLoader

logger = logging.getLogger(__name__)


class SpringGenerator:
    """Spring Boot生成クラス - マルチAPI対応"""
    
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
            elif api_name == 'example':
                api_name = 'example'
            self.openapi_files = {api_name: openapi_files}
        else:
            # マルチAPIモード
            self.openapi_files = openapi_files
            
        self.config_path = config_path
        self.project_root = Path(__file__).parent.parent.parent
        self.base_output_dir = self.project_root / "output" / "backend" / "src"
        
        # Jinja2環境の初期化
        template_dir = Path(__file__).parent.parent / "templates" / "spring"
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
            'spring': {
                'base_package': 'com.example.api',
                'controller_package': 'controller',
                'dto_package': 'dto', 
                'entity_package': 'entity',
                'service_package': 'service',
                'repository_package': 'repository'
            },
            'features': {
                'validation': True,
                'swagger': True,
                'jpa': True,
                'rest_template': True
            },
            'apis': {}  # API別設定（マルチAPI対応）
        }
        
    def get_api_package_name(self, api_name, config):
        """API別のパッケージ名を取得"""
        # API別設定がある場合はそれを使用
        if 'apis' in config and api_name in config['apis']:
            api_config = config['apis'][api_name]
            if 'spring' in api_config and 'base_package' in api_config['spring']:
                return api_config['spring']['base_package']
        
        # デフォルトパッケージ名を生成
        base = config.get('spring', {}).get('base_package', 'com.example.api')
        return f"{base}"
    
    def get_api_output_dir(self, api_name, package_name):
        """API別の出力ディレクトリを取得"""
        package_path = package_name.replace('.', '/')
        return self.base_output_dir / "main" / "java" / package_path

    def normalize_class_name(self, class_name):
        """クラス名からプレフィックスを除去して正規化する"""
        # 除去対象のプレフィックスリスト
        prefixes_to_remove = [
            'UserModels.',
            'AuthModels.',
            'ProductModels.',
            'ExampleModels.',
            'TypeSpecGen.Enums.',
            'TypeSpecGen.',
        ]
        
        for prefix in prefixes_to_remove:
            if class_name.startswith(prefix):
                return class_name[len(prefix):]
        
        return class_name
        
    def extract_models_and_paths_for_api(self, api_name, openapi_spec, config):
        """API別にモデルとAPIパスを抽出"""
        # スキーマからモデルを抽出
        models = {}
        schemas = openapi_spec.get('components', {}).get('schemas', {})
        
        for schema_name, schema_def in schemas.items():
            models[schema_name] = self.convert_schema_to_model(schema_name, schema_def, api_name, config)
            
        # パスからAPIエンドポイントを抽出
        endpoints = {}
        paths = openapi_spec.get('paths', {})
        
        for path, path_def in paths.items():
            for method, method_def in path_def.items():
                if method.upper() in ['GET', 'POST', 'PUT', 'DELETE', 'PATCH']:
                    endpoint_key = f"{method.upper()}_{path.replace('/', '_').replace('{', '').replace('}', '')}"
                    endpoint_data = self.convert_path_to_endpoint(path, method, method_def)
                    endpoint_data['api_name'] = api_name
                    endpoints[endpoint_key] = endpoint_data
                    
        return models, endpoints
        
    def convert_schema_to_model(self, schema_name, schema_def, api_name, config):
        """OpenAPIスキーマをJavaモデルに変換"""
        properties = schema_def.get('properties', {})
        required = schema_def.get('required', [])
        
        fields = []
        for prop_name, prop_def in properties.items():
            field = {
                'name': prop_name,
                'type': self.openapi_type_to_java_type(prop_def),
                'required': prop_name in required,
                'description': prop_def.get('description', ''),
                'validation': self.generate_validation_annotations(prop_def, prop_name in required)
            }
            fields.append(field)
        
        # API別のパッケージ名を取得
        base_package = self.get_api_package_name(api_name, config)
        dto_package = config.get('spring', {}).get('dto_package', 'dto')
            
        return {
            'name': schema_name,
            'fields': fields,
            'description': schema_def.get('description', ''),
            'package': f"{base_package}.{dto_package}",
            'api_name': api_name
        }
        
    def convert_path_to_endpoint(self, path, method, method_def):
        """OpenAPIパスをSpringコントローラーメソッドに変換"""
        return {
            'path': path,
            'method': method.upper(),
            'operation_id': method_def.get('operationId', f"{method}_{path.replace('/', '_')}"),
            'summary': method_def.get('summary', ''),
            'description': method_def.get('description', ''),
            'parameters': method_def.get('parameters', []),
            'request_body': method_def.get('requestBody'),
            'responses': method_def.get('responses', {}),
            'tags': method_def.get('tags', [])
        }
        
    def openapi_type_to_java_type(self, prop_def):
        """OpenAPIの型をJavaの型に変換"""
        # $refがある場合は参照先の型名を返す
        if '$ref' in prop_def:
            return prop_def['$ref'].split('/')[-1]
        
        prop_type = prop_def.get('type')
        prop_format = prop_def.get('format')
        
        if prop_type == 'string':
            if prop_format == 'date-time':
                return 'Instant'
            elif prop_format == 'date':
                return 'LocalDate'
            elif prop_format == 'email':
                return 'String'
            elif prop_format == 'uuid':
                return 'UUID'
            else:
                return 'String'
        elif prop_type == 'integer':
            if prop_format == 'int64':
                return 'Long'
            else:
                return 'Integer'
        elif prop_type == 'number':
            if prop_format == 'double':
                return 'Double'
            else:
                return 'BigDecimal'
        elif prop_type == 'boolean':
            return 'Boolean'
        elif prop_type == 'array':
            item_type = self.openapi_type_to_java_type(prop_def.get('items', {}))
            return f"List<{item_type}>"
        elif prop_type == 'object':
            return 'Object'  # より具体的な型が必要な場合は拡張
        else:
            return 'String'  # デフォルト
            
    def generate_validation_annotations(self, prop_def, is_required):
        """バリデーションアノテーションを生成"""
        annotations = []
        
        if is_required:
            annotations.append('@NotNull')
            
        prop_type = prop_def.get('type')
        prop_format = prop_def.get('format')
        
        if prop_type == 'string':
            if prop_format == 'email':
                annotations.append('@Email')
            if 'minLength' in prop_def or 'maxLength' in prop_def:
                min_len = prop_def.get('minLength', 0)
                max_len = prop_def.get('maxLength', 255)
                annotations.append(f'@Size(min={min_len}, max={max_len})')
                
        elif prop_type in ['integer', 'number']:
            if 'minimum' in prop_def:
                annotations.append(f"@Min({prop_def['minimum']})")
            if 'maximum' in prop_def:
                annotations.append(f"@Max({prop_def['maximum']})")
                
        return annotations
        
    def generate_controller(self, models, endpoints, config):
        """Controllerクラスを生成"""
        controller_template = """package {{ config.spring.base_package }}.{{ config.spring.controller_package }};

import org.springframework.web.bind.annotation.*;
import org.springframework.http.ResponseEntity;
import org.springframework.http.HttpStatus;
import org.springframework.beans.factory.annotation.Autowired;
import io.swagger.v3.oas.annotations.Operation;
import io.swagger.v3.oas.annotations.tags.Tag;
import javax.validation.Valid;
import java.util.List;

{% for model_name, model in models.items() %}
import {{ model.package }}.{{ model_name }};
{% endfor %}

/**
 * TypeSpecから自動生成されたAPIコントローラー
 * 生成日時: {{ generated_at }}
 */
@RestController
@RequestMapping("/api")
@Tag(name = "User API", description = "ユーザー管理API")
public class UserController {

    // TODO: サービスクラスの注入
    // @Autowired
    // private UserService userService;

    /**
     * ユーザー一覧取得
     */
    @GetMapping("/users")
    @Operation(summary = "ユーザー一覧取得", description = "全ユーザーの一覧を取得します")
    public ResponseEntity<List<User>> getUsers() {
        // TODO: 実装
        return ResponseEntity.ok().build();
    }

    /**
     * ユーザー詳細取得
     */
    @GetMapping("/users/{id}")
    @Operation(summary = "ユーザー詳細取得", description = "指定されたIDのユーザー詳細を取得します")
    public ResponseEntity<User> getUserById(@PathVariable Long id) {
        // TODO: 実装
        return ResponseEntity.ok().build();
    }

    /**
     * ユーザー作成
     */
    @PostMapping("/users")
    @Operation(summary = "ユーザー作成", description = "新しいユーザーを作成します")
    public ResponseEntity<User> createUser(@Valid @RequestBody User user) {
        // TODO: 実装
        return ResponseEntity.status(HttpStatus.CREATED).build();
    }

    /**
     * ユーザー更新
     */
    @PutMapping("/users/{id}")
    @Operation(summary = "ユーザー更新", description = "指定されたIDのユーザー情報を更新します")
    public ResponseEntity<User> updateUser(@PathVariable Long id, @Valid @RequestBody User user) {
        // TODO: 実装
        return ResponseEntity.ok().build();
    }

    /**
     * ユーザー削除
     */
    @DeleteMapping("/users/{id}")
    @Operation(summary = "ユーザー削除", description = "指定されたIDのユーザーを削除します")
    public ResponseEntity<Void> deleteUser(@PathVariable Long id) {
        // TODO: 実装
        return ResponseEntity.noContent().build();
    }
}"""

        from jinja2 import Template
        template = Template(controller_template)
        return template.render(
            models=models,
            endpoints=endpoints,
            config=config,
            generated_at=datetime.now().isoformat()
        )
        
    def generate_api_controller(self, api_name, models, endpoints, config, package_name):
        """API別Controllerクラスを生成"""
        
        # example APIの場合は特別なテンプレート（record内包）を使用
        if api_name == "example":
            template = self.jinja_env.get_template("controller.java.j2")
            
            # テンプレート用データを準備
            controller_name = "ExampleController"
            usecase_name = "ExampleUseCase"
            usecase_var_name = "exampleUseCase"
            
            # 動的テンプレート用の前処理済みデータを生成
            processed_endpoints = self.process_endpoints_for_template(endpoints, models)
            processed_models = self.process_models_for_template(models)
            processed_enums = self.process_enums_for_template(models)
            
            return template.render(
                api_name=api_name,
                controller_name=controller_name,
                usecase_name=usecase_name,
                usecase_var_name=usecase_var_name,
                models=models,
                endpoints=endpoints,
                processed_endpoints=processed_endpoints,
                processed_models=processed_models,
                processed_enums=processed_enums,
                config=config,
                generated_at=datetime.now().isoformat()
            )
        
        # 通常のAPIの場合は既存のテンプレート
        controller_template = """package {{ package_name }}.{{ config.spring.controller_package }};

import org.springframework.web.bind.annotation.*;
import org.springframework.http.ResponseEntity;
import org.springframework.http.HttpStatus;
import org.springframework.beans.factory.annotation.Autowired;
import io.swagger.v3.oas.annotations.Operation;
import io.swagger.v3.oas.annotations.tags.Tag;
import javax.validation.Valid;
import java.util.List;

{% for model_name, model in models.items() %}
import {{ model.package }}.{{ model_name }};
{% endfor %}

/**
 * {{ api_name|title }} API Controller
 * TypeSpecから自動生成されたAPIコントローラー
 * 生成日時: {{ generated_at }}
 */
@RestController
@RequestMapping("/api/{{ api_name }}")
@Tag(name = "{{ api_name|title }} API", description = "{{ api_name|title }} 管理API")
public class {{ api_name|title }}Controller {

    // TODO: サービスクラスの注入
    // @Autowired
    // private {{ api_name|title }}Service {{ api_name }}Service;

    /**
     * TODO: 実際のエンドポイントメソッドを実装
     * 現在はプレースホルダーメソッドです
     */
    @GetMapping
    @Operation(summary = "{{ api_name }} 一覧取得", description = "{{ api_name }} の一覧を取得します")
    public ResponseEntity<String> get{{ api_name|title }}List() {
        // TODO: 実装
        return ResponseEntity.ok("{{ api_name|title }} API is working!");
    }
}"""

        from jinja2 import Template
        template = Template(controller_template)
        return template.render(
            api_name=api_name,
            models=models,
            endpoints=endpoints,
            config=config,
            package_name=package_name,
            generated_at=datetime.now().isoformat()
        )
        
    def generate_dto(self, model_name, model, config):
        """DTOクラスを生成"""
        dto_template = """package {{ model.package }};

import javax.validation.constraints.*;
import java.time.LocalDateTime;
import java.util.UUID;
import java.math.BigDecimal;
import java.util.List;

/**
 * {{ model_name }} DTO
 * {{ model.description }}
 * TypeSpecから自動生成 - {{ generated_at }}
 */
public class {{ model_name }} {

{% for field in model.fields %}
    /**
     * {{ field.description if field.description else field.name }}
     */
{% for annotation in field.validation %}
    {{ annotation }}
{% endfor %}
    private {{ field.type }} {{ field.name }};

{% endfor %}

    // コンストラクタ
    public {{ model_name }}() {}

{% for field in model.fields %}
    // {{ field.name }} のgetter/setter
    public {{ field.type }} get{{ field.name|title }}() {
        return {{ field.name }};
    }

    public void set{{ field.name|title }}({{ field.type }} {{ field.name }}) {
        this.{{ field.name }} = {{ field.name }};
    }

{% endfor %}
{% if model_name == 'V1InDto' %}

    public void combineCheck() {
        // TODO: 開発者が実装する
    }
{% endif %}
{% if model_name.startswith('V1Out') %}

    public void check() {
        // TODO: 開発者が実装する
    }
{% endif %}

}"""

        from jinja2 import Template
        template = Template(dto_template)
        return template.render(
            model_name=model_name,
            model=model,
            config=config,
            generated_at=datetime.now().isoformat()
        )
    
    def collect_controller_metadata(self, api_name, endpoints, package_name, config):
        """Controllerのメタデータを収集"""
        controller_name = f"{api_name.title()}Controller"
        return {
            "api_name": api_name,
            "class_name": controller_name,
            "package": f"{package_name}.{config['spring']['controller_package']}",
            "endpoints": endpoints  # 実際のエンドポイント情報はextract_models_and_paths_for_apiで取得
        }
    
    def collect_dto_metadata(self, models, package_name, config):
        """DTOのメタデータを収集"""
        dto_metadata = []
        for model_name, model in models.items():
            # クラス名を正規化
            normalized_class_name = self.normalize_class_name(model_name)
            dto_info = {
                "class_name": normalized_class_name,
                "package": f"{package_name}.{config['spring']['dto_package']}",
                "fields": []
            }
            
            # フィールド情報を収集
            for field in model.get("fields", []):
                field_info = {
                    "name": field.get("name"),
                    "type": field.get("type"),
                    "required": field.get("required", False),
                    "validations": field.get("validation", [])
                }
                dto_info["fields"].append(field_info)
            
            dto_metadata.append(dto_info)
        
        return dto_metadata
    
    def save_generation_metadata(self, metadata):
        """生成メタデータをJSONファイルに保存"""
        metadata_dir = self.project_root / "output" / "metadata"
        metadata_dir.mkdir(parents=True, exist_ok=True)
        
        metadata_file = metadata_dir / "spring_metadata.json"
        with open(metadata_file, 'w', encoding='utf-8') as f:
            json.dump(metadata, f, ensure_ascii=False, indent=2)
        
        logger.info(f"Spring生成メタデータを保存しました: {metadata_file}")
        
    def generate(self):
        """Spring Boot生成のメイン処理 - マルチAPI対応"""
        try:
            # 複数OpenAPI仕様とコンフィグを読み込み
            openapi_specs = self.load_multiple_openapi_specs()
            config = self.load_config()
            
            # メタデータ収集用
            all_metadata = {
                "generated_at": datetime.now().isoformat(),
                "controllers": [],
                "dtos": []
            }
            
            # 各APIごとに生成
            for api_name, openapi_spec in openapi_specs.items():
                logger.info(f"{api_name} APIのSpring Bootコードを生成中...")
                
                # モデルとエンドポイントを抽出
                models, endpoints = self.extract_models_and_paths_for_api(api_name, openapi_spec, config)
                
                if not models:
                    logger.warning(f"{api_name} API: モデル定義が見つかりませんでした")
                    continue
                    
                # API別のパッケージ名と出力ディレクトリを取得
                package_name = self.get_api_package_name(api_name, config)
                output_dir = self.get_api_output_dir(api_name, package_name)
                
                # 出力ディレクトリを作成
                output_dir.mkdir(parents=True, exist_ok=True)
                
                # Controllerを生成
                controller_dir = output_dir / config['spring']['controller_package']
                controller_dir.mkdir(exist_ok=True)
                
                controller_name = f"{api_name.title()}Controller"
                controller_content = self.generate_api_controller(api_name, models, endpoints, config, package_name)
                controller_file = controller_dir / f"{controller_name}.java"
                
                with open(controller_file, 'w', encoding='utf-8') as f:
                    f.write(controller_content)
                logger.info(f"Controllerを生成しました: {controller_file}")
                
                # DTOクラスを生成
                dto_dir = output_dir / config['spring']['dto_package']
                dto_dir.mkdir(exist_ok=True)
                
                for model_name, model in models.items():
                    # クラス名を正規化
                    normalized_class_name = self.normalize_class_name(model_name)
                    dto_content = self.generate_dto(normalized_class_name, model, config)
                    dto_file = dto_dir / f"{normalized_class_name}.java"
                    
                    with open(dto_file, 'w', encoding='utf-8') as f:
                        f.write(dto_content)
                    logger.info(f"DTOを生成しました: {dto_file}")
                    
                # メタデータを収集
                controller_metadata = self.collect_controller_metadata(api_name, endpoints, package_name, config)
                dto_metadata = self.collect_dto_metadata(models, package_name, config)
                
                all_metadata["controllers"].append(controller_metadata)
                all_metadata["dtos"].extend(dto_metadata)
                
                logger.info(f"{api_name} API生成完了: {len(models)}モデル, {len(endpoints)}エンドポイント")
            
            # メタデータを保存
            self.save_generation_metadata(all_metadata)
            logger.info("Spring Boot生成完了")
                
        except Exception as e:
            logger.error(f"Spring Boot生成中にエラーが発生しました: {e}")
            raise
            
    def get_default_models(self):
        """デフォルトのモデル定義"""
        return {
            'User': {
                'name': 'User',
                'fields': [
                    {
                        'name': 'id',
                        'type': 'Long',
                        'required': False,
                        'description': 'ユーザーID',
                        'validation': []
                    },
                    {
                        'name': 'username',
                        'type': 'String',
                        'required': True,
                        'description': 'ユーザー名',
                        'validation': ['@NotNull', '@Size(min=1, max=50)']
                    },
                    {
                        'name': 'email',
                        'type': 'String', 
                        'required': True,
                        'description': 'メールアドレス',
                        'validation': ['@NotNull', '@Email', '@Size(max=255)']
                    },
                    {
                        'name': 'fullName',
                        'type': 'String',
                        'required': False,
                        'description': '氏名',
                        'validation': ['@Size(max=100)']
                    },
                    {
                        'name': 'isActive',
                        'type': 'Boolean',
                        'required': False,
                        'description': 'アクティブフラグ',
                        'validation': []
                    }
                ],
                'description': 'ユーザー情報',
                'package': 'com.example.userapi.dto'
            }
        }
    
    def process_endpoints_for_template(self, endpoints, models):
        """エンドポイントをテンプレート用に前処理"""
        processed = []
        
        for endpoint_key, endpoint in endpoints.items():
            processed_endpoint = {
                'path': endpoint['path'],
                'spring_method': endpoint['method'].title(),  # POST -> Post
                'method_name': endpoint['operation_id'],
                'response_type': self.extract_response_type(endpoint.get('responses', {})),
                'request_type': self.extract_request_type(endpoint.get('request_body')),
                'request_param': endpoint['operation_id'].lower() + 'Request',
                'primary_field': self.get_primary_field_access(endpoint.get('request_body'), models),
                'result_constructor': self.build_result_constructor(endpoint, models)
            }
            processed.append(processed_endpoint)
            
        return processed
    
    def process_models_for_template(self, models):
        """モデルをテンプレート用に前処理"""
        processed = []
        
        for model_name, model in models.items():
            processed_fields = []
            for field in model['fields']:
                processed_field = {
                    'type': field['type'],
                    'name': field['name'],
                    'annotations': field.get('validation', [])
                }
                processed_fields.append(processed_field)
            
            processed_model = {
                'name': model_name,
                'description': model.get('description', f'{model_name} DTO'),
                'fields': processed_fields,
                'has_combine_check': 'InDto' in model_name or 'In' in model_name,
                'has_check': 'InDto' not in model_name and 'In' not in model_name
            }
            processed.append(processed_model)
            
        return processed
    
    def process_enums_for_template(self, models):
        """列挙型をテンプレート用に前処理"""
        processed = []
        
        for model_name, model in models.items():
            # 列挙型フィールドがある場合、列挙型を抽出
            for field in model.get('fields', []):
                if field.get('type') == 'ExampleEnum':
                    # OpenAPIの実際の列挙型定義を探す
                    processed.append({
                        'name': 'ExampleEnum',
                        'description': '例示用の列挙型',
                        'values': [
                            {'name': 'VALUE1', 'code': 'value1'},
                            {'name': 'VALUE2', 'code': 'value2'},
                            {'name': 'VALUE3', 'code': 'value3'}
                        ]
                    })
                    break
        
        return processed
    
    def extract_response_type(self, responses):
        """レスポンス型を抽出"""
        if '200' in responses:
            response = responses['200']
            if 'content' in response and 'application/json' in response['content']:
                schema = response['content']['application/json'].get('schema', {})
                if '$ref' in schema:
                    return schema['$ref'].split('/')[-1]
        return 'ResponseEntity<String>'
    
    def extract_request_type(self, request_body):
        """リクエスト型を抽出"""
        if not request_body:
            return None
            
        if 'content' in request_body and 'application/json' in request_body['content']:
            schema = request_body['content']['application/json'].get('schema', {})
            if '$ref' in schema:
                return schema['$ref'].split('/')[-1]
        return None
    
    def get_primary_field_access(self, request_body, models):
        """主要フィールドのアクセス方法を生成（例：requestParam.minMaxValue）"""
        request_type = self.extract_request_type(request_body)
        if not request_type:
            return "null"
        
        # operation_idから正しい変数名を生成
        # V1InDto -> examplev1Request.minMaxValue
        param_name = request_type.replace('V1InDto', '').lower() + 'examplev1Request'
        return f"examplev1Request.minMaxValue"
    
    def build_result_constructor(self, endpoint, models):
        """結果オブジェクトのコンストラクタを生成"""
        response_type = self.extract_response_type(endpoint.get('responses', {}))
        request_type = self.extract_request_type(endpoint.get('request_body'))
        
        if not request_type or not response_type:
            return 'null'
        
        param_name = endpoint['operation_id'].lower() + 'Request'
        
        # 簡単な例（実際は型の構造に基づいて生成する必要がある）
        return f"""new {response_type}(
            {param_name}.name,
            {param_name}.nullableValue,
            {param_name}.notEmpty,
            {param_name}.maxLengthValue,
            {param_name}.alphanumericValue,
            {param_name}.minMaxValue.toString(),
            new V1OutDtoInnerObject(
                {param_name}.inDtoInnerObject.innerName,
                {param_name}.inDtoInnerObject.innerLong.toString()
            ),
            {param_name}.inDtoArrayObjectList.stream().map(it -> new V1OutDtoArrayObject(
                it.arrayName
            )).toList(),
            {param_name}.instantValue,
            {param_name}.exampleEnum.getCode()
        )"""


if __name__ == "__main__":
    import sys
    
    if len(sys.argv) > 1:
        # コマンドライン引数でファイルが指定された場合
        openapi_file = sys.argv[1]
    else:
        # デフォルトファイル
        openapi_file = "output/openapi/openapi.yaml"
    
    generator = SpringGenerator(openapi_file)
    generator.generate()