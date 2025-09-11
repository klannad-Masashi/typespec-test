from pathlib import Path
from typing import Dict, Any, List
import json
import asyncio
from jinja2 import Environment, FileSystemLoader
import logging

# ログ設定
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class TypeSpecGenerator:
    """TypeSpec生成サービス - フォーム入力からTypeSpecファイルを生成"""
    
    def __init__(self, workspace_path: str):
        self.workspace_path = Path(workspace_path)
        self.typespec_path = self.workspace_path / "typespec"
        self.templates_path = Path(__file__).parent.parent / "templates" / "typespec"
        
        # Jinja2環境設定
        self.jinja_env = Environment(
            loader=FileSystemLoader(str(self.templates_path)),
            trim_blocks=True,
            lstrip_blocks=True
        )
    
    async def generate_api(self, api_data: Dict[str, Any]) -> Dict[str, Any]:
        """APIデータからTypeSpecファイルを生成"""
        try:
            api_name = api_data["api_name"]
            logger.info(f"Generating TypeSpec for API: {api_name}")
            
            # パッケージディレクトリ作成
            package_dir = self.typespec_path / "packages" / "api" / api_name
            package_dir.mkdir(parents=True, exist_ok=True)
            
            # TypeSpecファイル生成
            results = {}
            
            # 1. 統合TypeSpecファイル生成（main.tsp）
            main_content = await self._generate_main_typespec(api_data)
            main_file = package_dir / "main.tsp"
            main_file.write_text(main_content, encoding="utf-8")
            results["main_file"] = str(main_file)
            logger.info(f"Generated main TypeSpec file: {main_file}")
            
            # 2. package.json生成
            package_json = await self._generate_package_json(api_name)
            package_file = package_dir / "package.json"
            package_file.write_text(package_json, encoding="utf-8")
            results["package_file"] = str(package_file)
            
            # 3. tspconfig.yaml生成
            tspconfig = await self._generate_tspconfig(api_name)
            config_file = package_dir / "tspconfig.yaml"
            config_file.write_text(tspconfig, encoding="utf-8")
            results["config_file"] = str(config_file)
            
            # 4. メインpackage.jsonの更新
            await self._update_main_package_json(api_name)
            
            results["success"] = True
            results["message"] = f"TypeSpec API '{api_name}' generated successfully"
            logger.info(f"TypeSpec generation completed for {api_name}")
            
            return results
            
        except Exception as e:
            logger.error(f"TypeSpec generation failed: {str(e)}")
            return {
                "success": False,
                "error": str(e),
                "message": f"TypeSpec generation failed: {str(e)}"
            }
    
    async def _generate_main_typespec(self, api_data: Dict[str, Any]) -> str:
        """統合TypeSpecファイル（main.tsp）生成"""
        template = self.jinja_env.get_template("main.tsp.j2")
        
        api_name = api_data["api_name"]
        description = api_data.get("description", f"{api_name.title()} API")
        models = api_data.get("models", [])
        endpoints = api_data.get("endpoints", [])
        auto_crud = api_data.get("auto_crud", True)
        
        # モデル処理
        processed_models = []
        if models:
            for model in models:
                processed_model = {
                    "name": model["name"],
                    "description": model.get("description", ""),
                    "fields": []
                }
                
                for field in model.get("fields", []):
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
        
        # フォームから受け取ったエンドポイントを使用
        if endpoints:
            for endpoint in endpoints:
                operation = {
                    "method": endpoint["method"].lower(),
                    "path": endpoint["path"],
                    "operation": endpoint["operationId"],
                    "description": endpoint.get("description", f"{endpoint['operationId']} operation"),
                    "response": endpoint.get("responseModel") or "string"
                }
                
                # リクエストモデルがある場合は追加
                if endpoint.get("requestModel"):
                    operation["request"] = endpoint["requestModel"]
                
                # エラーレスポンスがある場合は追加
                if endpoint.get("errorResponses"):
                    error_responses = []
                    for error in endpoint["errorResponses"]:
                        error_responses.append({
                            "status_code": error["statusCode"],
                            "description": error.get("description", ""),
                            "model": error.get("model") or "string"
                        })
                    operation["error_responses"] = error_responses
                
                operations.append(operation)
        
        # フォームエンドポイントがない場合はCRUD自動生成
        elif auto_crud and models:
            for model in models:
                model_name = model["name"]
                operations.extend([
                    {
                        "method": "get",
                        "path": f"/{model_name.lower()}s",
                        "operation": f"list{model_name}s", 
                        "description": f"Get all {model_name.lower()}s",
                        "response": f"{model_name}[]"
                    },
                    {
                        "method": "post",
                        "path": f"/{model_name.lower()}s",
                        "operation": f"create{model_name}",
                        "description": f"Create new {model_name.lower()}",
                        "request": model_name,
                        "response": model_name
                    }
                ])
        
        return template.render(
            api_name=api_name,
            description=description,
            namespace=f"{api_name.title()}Service",
            models=processed_models,
            operations=operations
        )

    async def _generate_models(self, api_name: str, models: List[Dict[str, Any]]) -> str:
        """モデル定義のTypeSpecコード生成"""
        template = self.jinja_env.get_template("models.tsp.j2")
        
        # バリデーションルール変換
        processed_models = []
        for model in models:
            processed_model = {
                "name": model["name"],
                "description": model.get("description", ""),
                "fields": []
            }
            
            for field in model.get("fields", []):
                processed_field = {
                    "name": field["name"],
                    "type": self._map_field_type(field["type"]),
                    "description": field.get("description", ""),
                    "required": field.get("required", True),
                    "validations": self._convert_validations(field.get("validations", {}))
                }
                processed_model["fields"].append(processed_field)
            
            processed_models.append(processed_model)
        
        return template.render(
            api_name=api_name,
            models=processed_models,
            namespace=f"{api_name.title()}Models"
        )
    
    async def _generate_api_definition(self, api_data: Dict[str, Any]) -> str:
        """API定義のTypeSpecコード生成"""
        template = self.jinja_env.get_template("api.tsp.j2")
        
        api_name = api_data["api_name"]
        description = api_data.get("description", f"{api_name.title()} API")
        models = api_data.get("models", [])
        endpoints = api_data.get("endpoints", [])
        auto_crud = api_data.get("auto_crud", True)
        
        # エンドポイント操作生成
        operations = []
        
        # フォームから受け取ったエンドポイントを使用
        if endpoints:
            for endpoint in endpoints:
                operation = {
                    "method": endpoint["method"].lower(),
                    "path": endpoint["path"],
                    "operation": endpoint["operationId"],
                    "description": endpoint.get("description", f"{endpoint['operationId']} operation"),
                    "response": endpoint.get("responseModel") or "string"
                }
                
                # リクエストモデルがある場合は追加
                if endpoint.get("requestModel"):
                    operation["request"] = endpoint["requestModel"]
                
                operations.append(operation)
        
        # フォームエンドポイントがない場合はCRUD自動生成
        elif auto_crud and models:
            for model in models:
                model_name = model["name"]
                operations.extend([
                    {
                        "method": "get",
                        "path": f"/{model_name.lower()}s",
                        "operation": f"list{model_name}s", 
                        "description": f"Get all {model_name.lower()}s",
                        "response": f"{model_name}[]"
                    },
                    {
                        "method": "post",
                        "path": f"/{model_name.lower()}s",
                        "operation": f"create{model_name}",
                        "description": f"Create new {model_name.lower()}",
                        "request": model_name,
                        "response": model_name
                    }
                ])
        
        return template.render(
            api_name=api_name,
            description=description,
            namespace=f"{api_name.title()}Service", 
            operations=operations,
            has_models=len(models) > 0
        )
    
    async def _generate_package_json(self, api_name: str) -> str:
        """package.json生成"""
        template = self.jinja_env.get_template("package.json.j2")
        return template.render(
            api_name=api_name,
            package_name=f"@typespec-gen/{api_name}"
        )
    
    async def _generate_tspconfig(self, api_name: str) -> str:
        """tspconfig.yaml生成"""
        template = self.jinja_env.get_template("tspconfig.yaml.j2")
        return template.render(api_name=api_name)
    
    async def _update_main_package_json(self, api_name: str):
        """メインpackage.jsonにコンパイルスクリプト追加"""
        package_file = self.typespec_path / "package.json"
        
        if package_file.exists():
            with open(package_file, 'r', encoding='utf-8') as f:
                package_data = json.load(f)
            
            # スクリプト追加
            if "scripts" not in package_data:
                package_data["scripts"] = {}
            
            compile_script = f"typespec:compile-{api_name}"
            if compile_script not in package_data["scripts"]:
                package_data["scripts"][compile_script] = f"npm run compile --workspace=@typespec-gen/{api_name}-api"
            
            # compile-all更新
            if "typespec:compile-all-apis" in package_data["scripts"]:
                current_script = package_data["scripts"]["typespec:compile-all-apis"]
                new_compile_cmd = f"npm run typespec:compile-{api_name}"
                if new_compile_cmd not in current_script:
                    package_data["scripts"]["typespec:compile-all-apis"] += f" && {new_compile_cmd}"
            
            with open(package_file, 'w', encoding='utf-8') as f:
                json.dump(package_data, f, indent=2, ensure_ascii=False)
    
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
        """バリデーションルールをTypeSpecデコレーターに変換"""
        decorators = []
        
        # 文字列長制限
        if validations.get("minLength"):
            decorators.append(f"@minLength({validations['minLength']})")
        if validations.get("maxLength"):
            decorators.append(f"@maxLength({validations['maxLength']})")
        
        # パターン制限
        if validations.get("pattern"):
            decorators.append(f"@pattern(\"{validations['pattern']}\")")
        
        # 数値制限（ユーザー入力値を含む）
        if validations.get("minimum") is not None:
            decorators.append(f"@minValue({validations['minimum']})")
        if validations.get("maximum") is not None:
            decorators.append(f"@maxValue({validations['maximum']})")
        
        # フォーマット制限
        if validations.get("format") == "email":
            decorators.append("@format(\"email\")")
        elif validations.get("format") == "uri":
            decorators.append("@format(\"uri\")")
        
        return decorators