from pathlib import Path
from typing import Dict, Any, List
import json
import logging
from jinja2 import Environment, FileSystemLoader

# ログ設定
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class CommonModelsService:
    """共通モデル管理サービス"""
    
    def __init__(self, workspace_path: str):
        self.workspace_path = Path(workspace_path)
        self.common_path = self.workspace_path / "typespec" / "packages" / "common"
        self.base_types_file = self.common_path / "base-types.tsp"
        self.templates_path = Path(__file__).parent.parent / "templates" / "typespec"
        
        # Jinja2環境設定
        self.jinja_env = Environment(
            loader=FileSystemLoader(str(self.templates_path)),
            trim_blocks=True,
            lstrip_blocks=True
        )
    
    async def initialize_common_directory(self):
        """共通ディレクトリとファイルの初期化"""
        try:
            # ディレクトリ作成
            self.common_path.mkdir(parents=True, exist_ok=True)
            
            # base-types.tspが存在しない場合は初期化
            if not self.base_types_file.exists():
                await self._create_initial_base_types()
                logger.info(f"Initialized base-types.tsp: {self.base_types_file}")
            
            # package.jsonが存在しない場合は作成
            package_json_file = self.common_path / "package.json"
            if not package_json_file.exists():
                await self._create_common_package_json()
                logger.info(f"Created common package.json: {package_json_file}")
            
            return {"success": True, "message": "共通ディレクトリを初期化しました"}
            
        except Exception as e:
            logger.error(f"Common directory initialization failed: {str(e)}")
            return {"success": False, "error": str(e)}
    
    async def _create_initial_base_types(self):
        """初期base-types.tspファイルの作成"""
        initial_content = '''import "@typespec/http";
import "@typespec/rest";

using TypeSpec.Http;
using TypeSpec.Rest;

namespace CommonModels;

// 共通モデル定義
// このファイルにはプロジェクト全体で使用する共通の型定義を記述します

'''
        self.base_types_file.write_text(initial_content, encoding="utf-8")
    
    async def _create_common_package_json(self):
        """共通パッケージのpackage.json作成"""
        package_content = {
            "name": "@typespec-gen/common",
            "version": "1.0.0",
            "description": "Common TypeSpec models and types",
            "main": "base-types.tsp",
            "dependencies": {
                "@typespec/compiler": "^0.66.0",
                "@typespec/http": "^0.66.0",
                "@typespec/rest": "^0.66.0"
            }
        }
        
        package_file = self.common_path / "package.json"
        package_file.write_text(json.dumps(package_content, indent=2, ensure_ascii=False), encoding="utf-8")
    
    async def get_existing_models(self) -> List[Dict[str, Any]]:
        """既存の共通モデル一覧を取得"""
        try:
            if not self.base_types_file.exists():
                return []
            
            # 簡単なパース（実装を簡素化）
            content = self.base_types_file.read_text(encoding="utf-8")
            models = self._parse_models_from_content(content)
            return models
            
        except Exception as e:
            logger.error(f"Failed to get existing models: {str(e)}")
            return []
    
    def _parse_models_from_content(self, content: str) -> List[Dict[str, Any]]:
        """TypeSpecコンテンツからモデル定義を抽出（簡易版）"""
        models = []
        lines = content.split('\n')
        
        i = 0
        while i < len(lines):
            line = lines[i].strip()
            
            # model定義の開始を検出
            if line.startswith('model ') and '{' in line:
                model_name = line.split('model ')[1].split(' {')[0].strip()
                
                # モデルの説明を取得（前の行のコメントから）
                description = ""
                if i > 0 and lines[i-1].strip().startswith('*'):
                    description = lines[i-1].strip().replace('*', '').strip()
                
                models.append({
                    "name": model_name,
                    "description": description
                })
            
            i += 1
        
        return models
    
    async def add_models(self, models: List[Dict[str, Any]]) -> Dict[str, Any]:
        """共通モデルをbase-types.tspに追記"""
        try:
            # 初期化確認
            await self.initialize_common_directory()
            
            # 既存コンテンツ読み取り
            current_content = ""
            if self.base_types_file.exists():
                current_content = self.base_types_file.read_text(encoding="utf-8")
            
            # 新しいモデル定義を生成
            new_models_content = self._generate_models_content(models)
            
            # コンテンツを追記
            updated_content = current_content.rstrip() + "\n\n" + new_models_content
            
            # ファイル保存
            self.base_types_file.write_text(updated_content, encoding="utf-8")
            
            logger.info(f"Added {len(models)} models to base-types.tsp")
            return {
                "success": True,
                "message": f"{len(models)}個の共通モデルを追加しました",
                "file_path": str(self.base_types_file)
            }
            
        except Exception as e:
            logger.error(f"Failed to add models: {str(e)}")
            return {"success": False, "error": str(e)}
    
    def _generate_models_content(self, models: List[Dict[str, Any]]) -> str:
        """モデル定義のTypeSpecコンテンツ生成"""
        # フィールドの型をマッピング
        for model in models:
            for field in model.get("fields", []):
                field["type_mapped"] = self._map_field_type(field["type"])
        
        # Jinja2テンプレートで生成
        template = self.jinja_env.get_template("base-types.tsp.j2")
        content = template.render(models=models)
        
        return content
    
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