from typing import List, Dict, Any, Optional
from sqlalchemy.orm import Session
from models.database_models import Api, Model, ModelValue, ModelValueValidation, Endpoint, ErrorResponse
from database import get_db
import logging

logger = logging.getLogger(__name__)

class DatabaseApiService:
    """データベースベースのAPI管理サービス"""
    
    def __init__(self):
        pass
    
    async def create_api(self, api_data: Dict[str, Any], db: Session) -> Dict[str, Any]:
        """新しいAPIプロジェクトを作成"""
        try:
            api_name = api_data["api_name"]
            description = api_data.get("description", "")
            models = api_data.get("models", [])
            endpoints = api_data.get("endpoints", [])
            
            # APIプロジェクトを作成
            api = Api(
                name=api_name,
                display_name=api_name.title(),
                description=description,
                namespace=f"{api_name.title()}Service"
            )
            db.add(api)
            db.flush()  # IDを取得するため
            
            # モデルを作成
            model_map = {}  # モデル名 -> Model ID のマッピング
            for model_data in models:
                model = Model(
                    api_id=api.id,
                    name=model_data["name"],
                    description=model_data.get("description", ""),
                    is_common=False
                )
                db.add(model)
                db.flush()
                model_map[model_data["name"]] = model.id
                
                # フィールドを作成
                for i, field_data in enumerate(model_data.get("fields", [])):
                    model_value = ModelValue(
                        model_id=model.id,
                        name=field_data["name"],
                        field_type=field_data["type"],
                        description=field_data.get("description", ""),
                        is_required=field_data.get("required", True),
                        sort_order=i + 1
                    )
                    db.add(model_value)
                    db.flush()
                    
                    # バリデーション制約を作成
                    validations = field_data.get("validations", {})
                    for validation_type, validation_value in validations.items():
                        model_value_validation = ModelValueValidation(
                            model_value_id=model_value.id,
                            validation_type=validation_type,
                            validation_value=str(validation_value)
                        )
                        db.add(model_value_validation)
            
            # エンドポイントを作成
            for endpoint_data in endpoints:
                # リクエスト・レスポンスモデルIDを取得
                request_model_id = model_map.get(endpoint_data.get("requestModel"))
                response_model_id = model_map.get(endpoint_data.get("responseModel"))
                
                endpoint = Endpoint(
                    api_id=api.id,
                    method=endpoint_data["method"],
                    path=endpoint_data["path"],
                    operation_id=endpoint_data["operationId"],
                    description=endpoint_data.get("description", ""),
                    request_model_id=request_model_id,
                    response_model_id=response_model_id
                )
                db.add(endpoint)
                db.flush()
                
                # エラーレスポンスを作成
                error_responses = endpoint_data.get("errorResponses", [])
                for error_data in error_responses:
                    error_model_id = model_map.get(error_data.get("model"))
                    
                    error_response = ErrorResponse(
                        endpoint_id=endpoint.id,
                        status_code=int(error_data["statusCode"]),
                        description=error_data.get("description", ""),
                        response_model_id=error_model_id
                    )
                    db.add(error_response)
            
            db.commit()
            
            logger.info(f"API '{api_name}' created with ID {api.id}")
            return {
                "success": True,
                "message": f"API '{api_name}' を作成しました",
                "api_id": api.id
            }
            
        except Exception as e:
            db.rollback()
            logger.error(f"Failed to create API: {str(e)}")
            return {"success": False, "error": str(e)}
    
    async def get_api_list(self, db: Session) -> List[Dict[str, Any]]:
        """API一覧を取得"""
        try:
            apis = db.query(Api).filter(Api.is_active == True).order_by(Api.updated_at.desc()).all()
            
            api_list = []
            for api in apis:
                api_list.append({
                    "id": api.id,
                    "name": api.name,
                    "display_name": api.display_name,
                    "description": api.description,
                    "created_at": api.created_at.isoformat(),
                    "updated_at": api.updated_at.isoformat()
                })
            
            return api_list
            
        except Exception as e:
            logger.error(f"Failed to get API list: {str(e)}")
            return []
    
    async def get_api_detail(self, api_id: int, db: Session) -> Optional[Dict[str, Any]]:
        """API詳細情報を取得"""
        try:
            api = db.query(Api).filter(Api.id == api_id, Api.is_active == True).first()
            if not api:
                return None
            
            # モデル情報を取得
            models = []
            for model in api.models:
                fields = []
                for field in sorted(model.fields, key=lambda f: f.sort_order):
                    validations = {}
                    for validation in field.validations:
                        validations[validation.validation_type] = validation.validation_value
                    
                    fields.append({
                        "name": field.name,
                        "type": field.field_type,
                        "description": field.description,
                        "required": field.is_required,
                        "validations": validations
                    })
                
                models.append({
                    "name": model.name,
                    "description": model.description,
                    "fields": fields
                })
            
            # エンドポイント情報を取得
            endpoints = []
            for endpoint in api.endpoints:
                error_responses = []
                for error in endpoint.error_responses:
                    error_responses.append({
                        "statusCode": str(error.status_code),
                        "description": error.description,
                        "model": error.response_model.name if error.response_model else None
                    })
                
                endpoints.append({
                    "method": endpoint.method,
                    "path": endpoint.path,
                    "operationId": endpoint.operation_id,
                    "description": endpoint.description,
                    "requestModel": endpoint.request_model.name if endpoint.request_model else None,
                    "responseModel": endpoint.response_model.name if endpoint.response_model else None,
                    "errorResponses": error_responses
                })
            
            return {
                "id": api.id,
                "name": api.name,
                "display_name": api.display_name,
                "description": api.description,
                "namespace": api.namespace,
                "models": models,
                "endpoints": endpoints,
                "created_at": api.created_at.isoformat(),
                "updated_at": api.updated_at.isoformat()
            }
            
        except Exception as e:
            logger.error(f"Failed to get API detail: {str(e)}")
            return None