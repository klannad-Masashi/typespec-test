from fastapi import FastAPI, Request, Form, HTTPException, Depends
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
from fastapi.responses import HTMLResponse, JSONResponse
from typing import List, Optional, Dict, Any
import json
import os
import logging
from sqlalchemy.orm import Session
from database import get_db
from services.database_api_service import DatabaseApiService
from services.database_common_models_service import DatabaseCommonModelsService
from services.database_enum_service import DatabaseEnumService

app = FastAPI(
    title="TypeSpec Generator Web Service",
    version="1.0.0",
    description="GUI-based TypeSpec code generator"
)

# 静的ファイルとテンプレート設定
app.mount("/static", StaticFiles(directory="static"), name="static")
templates = Jinja2Templates(directory="templates")

# ログ設定
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Workspace path from environment
WORKSPACE_PATH = os.getenv("WORKSPACE_PATH", "/workspace")


@app.get("/", response_class=HTMLResponse)
async def index(request: Request, db: Session = Depends(get_db)):
    """メインページ - API一覧表示"""
    # データベースから既存APIリスト取得
    db_api_service = DatabaseApiService()
    existing_apis = await db_api_service.get_api_list(db)
    
    return templates.TemplateResponse("index.html", {
        "request": request,
        "existing_apis": existing_apis
    })

@app.get("/builder", response_class=HTMLResponse)
async def api_builder(request: Request):
    """API作成フォーム"""
    return templates.TemplateResponse("api_builder.html", {"request": request})

@app.get("/common-models", response_class=HTMLResponse)
async def common_models_page(request: Request):
    """共通モデル定義ページ"""
    return templates.TemplateResponse("common_models.html", {"request": request})

@app.get("/enums", response_class=HTMLResponse)
async def enums_page(request: Request):
    """Enum定義ページ"""
    return templates.TemplateResponse("enums.html", {"request": request})

@app.post("/generate", response_class=HTMLResponse)
async def generate_typespec(
    request: Request,
    api_name: str = Form(...),
    description: str = Form(""),
    models_json: str = Form(...),
    endpoints_json: str = Form(...),
    db: Session = Depends(get_db)
):
    """TypeSpec生成処理"""
    try:
        models = json.loads(models_json)
        endpoints = json.loads(endpoints_json)
        
        api_data = {
            "api_name": api_name.lower(),
            "description": description,
            "models": models,
            "endpoints": endpoints,
            "auto_crud": True
        }
        
        # データベースに保存
        db_api_service = DatabaseApiService()
        db_result = await db_api_service.create_api(api_data, db)
        
        if not db_result["success"]:
            raise Exception(f"Database save failed: {db_result['error']}")
        
        return templates.TemplateResponse("result.html", {
            "request": request,
            "api_name": api_name,
            "result": {
                "success": True,
                "message": f"API '{api_name}' をデータベースに保存しました",
                "database": db_result
            },
            "success": True
        })
        
    except Exception as e:
        return templates.TemplateResponse("result.html", {
            "request": request,
            "error": str(e),
            "success": False
        })


@app.get("/api/status")
async def get_status():
    """システム状態確認"""
    try:
        return {
            "web_service_running": True,
            "workspace_path": WORKSPACE_PATH
        }
    except Exception as e:
        return {"error": str(e)}

@app.get("/api/common-models")
async def get_common_models(db: Session = Depends(get_db)):
    """既存の共通モデル一覧を取得"""
    try:
        db_service = DatabaseCommonModelsService()
        models = await db_service.get_existing_models(db)
        return models
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/common-models/add")
async def add_common_models(request: Request, db: Session = Depends(get_db)):
    """共通モデルを追加"""
    try:
        body = await request.json()
        models = body.get("models", [])
        
        if not models:
            raise HTTPException(status_code=400, detail="モデルデータが必要です")
        
        # データベースに保存
        db_service = DatabaseCommonModelsService()
        db_result = await db_service.add_models(models, db)
        
        return db_result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/edit-common-model/{model_id}", response_class=HTMLResponse)
async def edit_common_model_page(model_id: int, request: Request):
    """共通モデル編集画面"""
    return templates.TemplateResponse("edit_common_model.html", {
        "request": request,
        "model_id": model_id
    })

@app.get("/api/common-models/{model_id}")
async def get_common_model(model_id: int, db: Session = Depends(get_db)):
    """共通モデル詳細取得"""
    try:
        service = DatabaseCommonModelsService()
        result = await service.get_model_detail(model_id, db)
        
        if not result["success"]:
            raise HTTPException(status_code=404, detail=result["error"])
            
        return result
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.put("/api/common-models/{model_id}")
async def update_common_model(model_id: int, request: Request, db: Session = Depends(get_db)):
    """共通モデルを更新"""
    try:
        body = await request.json()
        
        service = DatabaseCommonModelsService()
        result = await service.update_model(model_id, body, db)
        
        if not result["success"]:
            raise HTTPException(status_code=404, detail=result["error"])
            
        return result
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.delete("/api/common-models/{model_id}")
async def delete_common_model(model_id: int, db: Session = Depends(get_db)):
    """共通モデルを削除"""
    try:
        service = DatabaseCommonModelsService()
        result = await service.delete_model(model_id, db)
        
        if not result["success"]:
            raise HTTPException(status_code=404, detail=result["error"])
            
        return result
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/enums")
async def get_enums(db: Session = Depends(get_db)):
    """既存のEnum一覧を取得"""
    try:
        db_service = DatabaseEnumService()
        enums = await db_service.get_enum_list(db)
        return enums
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/edit-enum/{enum_id}", response_class=HTMLResponse)
async def edit_enum_page(enum_id: int, request: Request):
    """Enum編集画面"""
    return templates.TemplateResponse("edit_enum.html", {
        "request": request,
        "enum_id": enum_id
    })

@app.get("/api/enums/{enum_id}")
async def get_enum(enum_id: int, db: Session = Depends(get_db)):
    """Enum詳細取得"""
    try:
        service = DatabaseEnumService()
        result = await service.get_enum_detail(enum_id, db)
        
        if result is None:
            raise HTTPException(status_code=404, detail="Enumが見つかりません")
            
        return {"success": True, "enum": result}
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/enums/add")
async def add_enums(request: Request, db: Session = Depends(get_db)):
    """Enumを追加"""
    try:
        body = await request.json()
        enums = body.get("enums", [])
        
        if not enums:
            raise HTTPException(status_code=400, detail="Enumデータが必要です")
        
        # データベースに保存
        db_service = DatabaseEnumService()
        db_result = await db_service.create_enums(enums, db)
        
        return db_result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.put("/api/enums/{enum_id}")
async def update_enum(enum_id: int, request: Request, db: Session = Depends(get_db)):
    """Enumを更新"""
    try:
        body = await request.json()
        
        # データベースで更新
        db_service = DatabaseEnumService()
        db_result = await db_service.update_enum(enum_id, body, db)
        
        return db_result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.delete("/api/enums/{enum_id}")
async def delete_enum(enum_id: int, db: Session = Depends(get_db)):
    """Enumを削除"""
    try:
        # データベースから削除
        db_service = DatabaseEnumService()
        db_result = await db_service.delete_enum(enum_id, db)
        
        return db_result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)