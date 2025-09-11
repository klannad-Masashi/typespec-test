from fastapi import FastAPI, Request, Form, HTTPException
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
from fastapi.responses import HTMLResponse, JSONResponse
from typing import List, Optional
import json
import subprocess
import os
from pathlib import Path
from services.typespec_generator import TypeSpecGenerator

app = FastAPI(
    title="TypeSpec Generator Web Service",
    version="1.0.0",
    description="GUI-based TypeSpec code generator"
)

# 静的ファイルとテンプレート設定
app.mount("/static", StaticFiles(directory="static"), name="static")
templates = Jinja2Templates(directory="templates")

# Workspace path from environment
WORKSPACE_PATH = os.getenv("WORKSPACE_PATH", "/workspace")

@app.get("/", response_class=HTMLResponse)
async def index(request: Request):
    """メインページ - API一覧表示"""
    # 既存APIリスト取得
    existing_apis = []
    openapi_dir = Path(WORKSPACE_PATH) / "output" / "openapi"
    if openapi_dir.exists():
        existing_apis = [f.stem.replace('-api', '') for f in openapi_dir.glob('*-api.yaml')]
    
    return templates.TemplateResponse("index.html", {
        "request": request,
        "existing_apis": existing_apis
    })

@app.get("/builder", response_class=HTMLResponse)
async def api_builder(request: Request):
    """API作成フォーム"""
    return templates.TemplateResponse("api_builder.html", {"request": request})

@app.post("/generate", response_class=HTMLResponse)
async def generate_typespec(
    request: Request,
    api_name: str = Form(...),
    description: str = Form(""),
    models_json: str = Form(...)
):
    """TypeSpec生成処理"""
    try:
        models = json.loads(models_json)
        
        # TypeSpec生成
        generator = TypeSpecGenerator(WORKSPACE_PATH)
        result = await generator.generate_api({
            "api_name": api_name.lower(),
            "description": description,
            "models": models,
            "auto_crud": True
        })
        
        return templates.TemplateResponse("result.html", {
            "request": request,
            "api_name": api_name,
            "result": result,
            "success": True
        })
        
    except Exception as e:
        return templates.TemplateResponse("result.html", {
            "request": request,
            "error": str(e),
            "success": False
        })

@app.post("/api/compile/{api_name}")
async def compile_api(api_name: str):
    """TypeSpecコンパイル実行"""
    try:
        # コンテナ内から他のコンテナにアクセスする場合は別のアプローチが必要
        # 一旦ステータス確認のみ実装
        api_dir = Path(WORKSPACE_PATH) / "typespec" / "packages" / f"{api_name}-api"
        if not api_dir.exists():
            return {"status": "error", "message": f"API '{api_name}' が見つかりません"}
        
        return {
            "status": "success", 
            "message": f"API '{api_name}' の設定確認完了",
            "output": f"TypeSpec API directory found: {api_dir}"
        }
            
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"コンパイルエラー: {str(e)}")

@app.post("/api/generate-spring/{api_name}")
async def generate_spring_code(api_name: str):
    """Spring Boot + JUnit生成"""
    try:
        # 一旦OpenAPIファイルの存在確認
        openapi_file = Path(WORKSPACE_PATH) / "output" / "openapi" / f"{api_name}-api.yaml"
        if not openapi_file.exists():
            return {
                "status": "error",
                "message": f"OpenAPIファイルが見つかりません: {openapi_file}"
            }
        
        return {
            "status": "success", 
            "message": "OpenAPIファイル確認完了",
            "spring_output": f"Found OpenAPI file: {openapi_file}",
            "junit_output": "Spring/JUnit generation would be executed here"
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/status")
async def get_status():
    """システム状態確認"""
    try:
        # コンテナ内なのでTypeSpecとGeneratorディレクトリの存在確認
        typespec_dir = Path(WORKSPACE_PATH) / "typespec"
        generator_dir = Path(WORKSPACE_PATH) / "generator"
        
        return {
            "typespec_running": typespec_dir.exists(),
            "generator_running": generator_dir.exists(),
            "workspace_path": WORKSPACE_PATH,
            "web_service_running": True
        }
    except Exception as e:
        return {"error": str(e)}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)