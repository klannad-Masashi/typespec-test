"""
TypeSpec Generator - データベースからTypeSpecファイルを生成

データベース（APIs, Models, Endpoints等）からTypeSpec定義ファイルを生成します。
出力先: /output/typespec/{api_name}/
"""

from pathlib import Path
from typing import Dict, Any, List, Optional
import logging
from jinja2 import Environment, FileSystemLoader
from sqlalchemy.orm import Session

from generator.database import get_db
from generator.models.database_models import Api, Model, Field, FieldValidation, Endpoint, ErrorResponse

logger = logging.getLogger(__name__)

class TypeSpecGenerator:
    """データベースからTypeSpecファイルを生成"""
    
    def __init__(self, config_path: str = None):
        self.config_path = config_path
        self.project_root = Path(__file__).parent.parent.parent
        self.output_path = self.project_root / "output" / "typespec"
        self.templates_path = Path(__file__).parent.parent / "templates" / "typespec"
        
        # テンプレートディレクトリが存在しない場合は作成
        self.templates_path.mkdir(parents=True, exist_ok=True)
        
        # Jinja2環境設定
        self.jinja_env = Environment(
            loader=FileSystemLoader(str(self.templates_path)),
            trim_blocks=True,
            lstrip_blocks=True
        )
    
    def generate_api(self, api_name: str) -> Dict[str, Any]:
        """指定されたAPIのTypeSpecファイルを生成"""
        db = get_db()
        try:
            # APIを取得
            api = db.query(Api).filter(Api.name == api_name, Api.is_active == True).first()
            if not api:
                return {
                    "success": False,
                    "error": f"API '{api_name}' が見つかりません"
                }
            
            logger.info(f"Generating TypeSpec for API: {api_name}")
            
            # API詳細データを取得
            api_data = self._get_api_data(api, db)
            
            # 出力ディレクトリを作成
            api_output_path = self.output_path / api_name
            api_output_path.mkdir(parents=True, exist_ok=True)
            
            # TypeSpecファイルを生成
            result = self._generate_typespec_files(api_data, api_output_path)
            
            logger.info(f"TypeSpec generation completed for {api_name}")
            return {
                "success": True,
                "message": f"TypeSpec for '{api_name}' generated successfully",
                "output_path": str(api_output_path),
                "files": result
            }
            
        except Exception as e:
            logger.error(f"Failed to generate TypeSpec for {api_name}: {str(e)}")
            return {
                "success": False,
                "error": str(e)
            }
        finally:
            db.close()
    
    def generate_all_apis(self) -> Dict[str, Any]:
        """全APIのTypeSpecファイルを生成"""
        db = get_db()
        try:
            # アクティブなAPI一覧を取得
            apis = db.query(Api).filter(Api.is_active == True).all()
            
            results = {}
            total_success = 0
            
            for api in apis:
                result = self.generate_api(api.name)
                results[api.name] = result
                if result["success"]:
                    total_success += 1
            
            return {
                "success": True,
                "message": f"Generated TypeSpec for {total_success}/{len(apis)} APIs",
                "results": results
            }
            
        except Exception as e:
            logger.error(f"Failed to generate all APIs: {str(e)}")
            return {
                "success": False,
                "error": str(e)
            }
        finally:
            db.close()
    
    def _get_api_data(self, api: Api, db: Session) -> Dict[str, Any]:
        """APIの完全なデータを取得"""
        # 基本情報
        api_data = {
            "id": api.id,
            "name": api.name,
            "display_name": api.display_name,
            "description": api.description,
            "namespace": api.namespace or f"{api.name.title()}Service"
        }
        
        # API固有モデル
        api_models = []
        for model in api.models:
            model_data = self._get_model_data(model, db)
            api_models.append(model_data)
        
        # 共通モデル
        common_models = []
        common_model_query = db.query(Model).filter(Model.is_common == True)
        for model in common_model_query:
            model_data = self._get_model_data(model, db)
            common_models.append(model_data)
        
        # エンドポイント
        endpoints = []
        for endpoint in api.endpoints:
            endpoint_data = self._get_endpoint_data(endpoint, db)
            endpoints.append(endpoint_data)
        
        api_data.update({
            "models": api_models,
            "common_models": common_models,
            "endpoints": endpoints
        })
        
        return api_data
    
    def _get_model_data(self, model: Model, db: Session) -> Dict[str, Any]:
        """モデルデータを取得"""
        # フィールド
        fields = []
        for field in sorted(model.fields, key=lambda f: f.sort_order):
            validations = {}
            for validation in field.validations:
                validations[validation.validation_type] = validation.validation_value
            
            field_data = {
                "name": field.name,
                "type": field.field_type,
                "description": field.description,
                "required": field.is_required,
                "validations": validations
            }
            fields.append(field_data)
        
        return {
            "name": model.name,
            "description": model.description,
            "is_common": model.is_common,
            "fields": fields
        }
    
    def _get_endpoint_data(self, endpoint: Endpoint, db: Session) -> Dict[str, Any]:
        """エンドポイントデータを取得"""
        # エラーレスポンス
        error_responses = []
        for error in endpoint.error_responses:
            error_data = {
                "statusCode": str(error.status_code),
                "description": error.description,
                "model": error.response_model.name if error.response_model else None
            }
            error_responses.append(error_data)
        
        return {
            "method": endpoint.method,
            "path": endpoint.path,
            "operationId": endpoint.operation_id,
            "description": endpoint.description,
            "requestModel": endpoint.request_model.name if endpoint.request_model else None,
            "responseModel": endpoint.response_model.name if endpoint.response_model else None,
            "errorResponses": error_responses
        }
    
    def _generate_typespec_files(self, api_data: Dict[str, Any], output_path: Path) -> Dict[str, str]:
        """TypeSpecファイル一式を生成"""
        files = {}
        
        try:
            # main.tsp生成
            main_content = self._generate_main_typespec(api_data)
            main_file = output_path / "main.tsp"
            main_file.write_text(main_content, encoding="utf-8")
            files["main.tsp"] = str(main_file)
            
            # package.json生成
            package_content = self._generate_package_json(api_data)
            package_file = output_path / "package.json"
            package_file.write_text(package_content, encoding="utf-8")
            files["package.json"] = str(package_file)
            
            # tspconfig.yaml生成
            config_content = self._generate_tspconfig(api_data)
            config_file = output_path / "tspconfig.yaml"
            config_file.write_text(config_content, encoding="utf-8")
            files["tspconfig.yaml"] = str(config_file)
            
            return files
            
        except Exception as e:
            logger.error(f"Failed to generate TypeSpec files: {str(e)}")
            raise
    
    def _generate_main_typespec(self, api_data: Dict[str, Any]) -> str:
        """main.tsp生成"""
        template = self.jinja_env.get_template("main.tsp.j2")
        
        # モデル処理（型マッピング含む）
        processed_models = []
        for model_data in api_data.get("models", []) + api_data.get("common_models", []):
            processed_model = {
                "name": model_data["name"],
                "description": model_data.get("description", ""),
                "fields": []
            }
            
            for field in model_data.get("fields", []):
                processed_field = {
                    "name": field["name"],
                    "type": self._map_field_type(field["type"]),
                    "description": field.get("description", ""),
                    "required": field.get("required", True),
                    "validations": self._convert_validations(field.get("validations", {}))
                }
                processed_model["fields"].append(processed_field)
            
            processed_models.append(processed_model)
        
        # エンドポイント操作生成
        operations = []
        for endpoint_data in api_data.get("endpoints", []):
            operation = {
                "method": endpoint_data["method"].lower(),
                "path": endpoint_data["path"],
                "operation": endpoint_data["operationId"],
                "description": endpoint_data.get("description", f"{endpoint_data['operationId']} operation"),
                "response": endpoint_data.get("responseModel") or "string"
            }
            
            # リクエストモデル
            if endpoint_data.get("requestModel"):
                operation["request"] = endpoint_data["requestModel"]
            
            # エラーレスポンス
            if endpoint_data.get("errorResponses"):
                error_responses = []
                for error in endpoint_data["errorResponses"]:
                    error_responses.append({
                        "status_code": error["statusCode"],
                        "description": error.get("description", ""),
                        "model": error.get("model") or "string"
                    })
                operation["error_responses"] = error_responses
            
            operations.append(operation)
        
        return template.render(
            api_name=api_data["name"],
            description=api_data["description"],
            namespace=api_data["namespace"],
            models=processed_models,
            operations=operations
        )
    
    def _generate_package_json(self, api_data: Dict[str, Any]) -> str:
        """package.json生成"""
        template = self.jinja_env.get_template("package.json.j2")
        return template.render(
            api_name=api_data["name"],
            package_name=f"@typespec-gen/{api_data['name']}"
        )
    
    def _generate_tspconfig(self, api_data: Dict[str, Any]) -> str:
        """tspconfig.yaml生成"""
        template = self.jinja_env.get_template("tspconfig.yaml.j2")
        return template.render(api_name=api_data["name"])
    
    def _map_field_type(self, field_type: str) -> str:
        """フィールドタイプをTypeSpec型にマッピング"""
        type_mapping = {
            "string": "string",
            "text": "string", 
            "integer": "int32",
            "number": "float64",
            "boolean": "boolean",
            "date": "plainDate",
            "datetime": "utcDateTime",
            "email": "string",
            "url": "string", 
            "uuid": "string"
        }
        return type_mapping.get(field_type.lower(), "string")
    
    def _convert_validations(self, validations: Dict[str, Any]) -> List[str]:
        """バリデーション制約をTypeSpecデコレータに変換"""
        decorators = []
        for validation_type, value in validations.items():
            if validation_type == "minLength":
                decorators.append(f"@minLength({value})")
            elif validation_type == "maxLength":
                decorators.append(f"@maxLength({value})")
            elif validation_type == "minimum":
                decorators.append(f"@minValue({value})")
            elif validation_type == "maximum":
                decorators.append(f"@maxValue({value})")
            elif validation_type == "pattern":
                decorators.append(f"@pattern(\"{value}\")")
            elif validation_type == "format" and value == "email":
                decorators.append("@format(\"email\")")
            elif validation_type == "format" and value == "uri":
                decorators.append("@format(\"uri\")")
        
        return decorators