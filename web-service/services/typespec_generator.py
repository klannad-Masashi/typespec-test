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
            package_dir = self.typespec_path / "packages" / f"{api_name}-api"
            package_dir.mkdir(parents=True, exist_ok=True)
            
            # モデルディレクトリ確認・作成
            models_dir = self.typespec_path / "packages" / "models"
            models_dir.mkdir(parents=True, exist_ok=True)
            
            # TypeSpecファイル生成
            results = {}
            
            # 1. モデル定義生成
            if api_data.get("models"):
                models_content = await self._generate_models(api_name, api_data["models"])
                models_file = models_dir / f"{api_name}-models.tsp"
                models_file.write_text(models_content, encoding="utf-8")
                results["models_file"] = str(models_file)
                logger.info(f"Generated models file: {models_file}")
            
            # 2. API定義生成
            api_content = await self._generate_api_definition(api_data)
            api_file = package_dir / f"{api_name}-api.tsp"
            api_file.write_text(api_content, encoding="utf-8")
            results["api_file"] = str(api_file)
            logger.info(f"Generated API file: {api_file}")
            
            # 3. package.json生成
            package_json = await self._generate_package_json(api_name)
            package_file = package_dir / "package.json"
            package_file.write_text(package_json, encoding="utf-8")
            results["package_file"] = str(package_file)
            
            # 4. tspconfig.yaml生成
            tspconfig = await self._generate_tspconfig(api_name)
            config_file = package_dir / "tspconfig.yaml"
            config_file.write_text(tspconfig, encoding="utf-8")
            results["config_file"] = str(config_file)
            
            # 5. メインpackage.jsonの更新
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
        auto_crud = api_data.get("auto_crud", True)
        
        # CRUD操作生成
        operations = []
        if auto_crud and models:
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
                        "method": "get", 
                        "path": f"/{model_name.lower()}s/{{id}}",
                        "operation": f"get{model_name}",
                        "description": f"Get {model_name.lower()} by ID",
                        "response": model_name
                    },
                    {
                        "method": "post",
                        "path": f"/{model_name.lower()}s",
                        "operation": f"create{model_name}",
                        "description": f"Create new {model_name.lower()}",
                        "request": model_name,
                        "response": model_name
                    },
                    {
                        "method": "put",
                        "path": f"/{model_name.lower()}s/{{id}}",
                        "operation": f"update{model_name}",
                        "description": f"Update {model_name.lower()}",
                        "request": model_name,
                        "response": model_name
                    },
                    {
                        "method": "delete",
                        "path": f"/{model_name.lower()}s/{{id}}",
                        "operation": f"delete{model_name}",
                        "description": f"Delete {model_name.lower()}",
                        "response": "void"
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
            package_name=f"@typespec-gen/{api_name}-api"
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
        
        if validations.get("minLength"):
            decorators.append(f"@minLength({validations['minLength']})")
        if validations.get("maxLength"):
            decorators.append(f"@maxLength({validations['maxLength']})")
        if validations.get("pattern"):
            decorators.append(f"@pattern(\"{validations['pattern']}\")")
        if validations.get("minimum"):
            decorators.append(f"@minValue({validations['minimum']})")
        if validations.get("maximum"):
            decorators.append(f"@maxValue({validations['maximum']})")
        if validations.get("format") == "email":
            decorators.append("@format(\"email\")")
        
        return decorators