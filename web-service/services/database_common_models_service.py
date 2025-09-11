from typing import List, Dict, Any
from sqlalchemy.orm import Session
from models.database_models import Model, ModelValue, ModelValueValidation
from database import get_db
import logging

logger = logging.getLogger(__name__)

class DatabaseCommonModelsService:
    """データベースベースの共通モデル管理サービス"""
    
    def __init__(self):
        pass
    
    async def get_existing_models(self, db: Session) -> List[Dict[str, Any]]:
        """既存の共通モデル一覧を取得"""
        try:
            models = db.query(Model).filter(Model.is_common == True, Model.is_active == True).order_by(Model.updated_at.desc()).all()
            
            model_list = []
            for model in models:
                model_list.append({
                    "id": model.id,
                    "name": model.name,
                    "description": model.description
                })
            
            return model_list
            
        except Exception as e:
            logger.error(f"Failed to get existing common models: {str(e)}")
            return []
    
    async def delete_model(self, model_id: int, db: Session) -> Dict[str, Any]:
        """共通モデルを論理削除"""
        try:
            # 共通モデルを検索
            model = db.query(Model).filter(
                Model.id == model_id,
                Model.is_common == True,
                Model.is_active == True
            ).first()
            
            if not model:
                return {
                    "success": False,
                    "error": "指定された共通modelが見つかりません"
                }
            
            # 論理削除（is_activeをFalseに設定）
            model.is_active = False
            db.commit()
            
            logger.info(f"Logically deleted common model: {model.name} (ID: {model_id})")
            return {
                "success": True,
                "message": f"共通model '{model.name}' を削除しました"
            }
            
        except Exception as e:
            db.rollback()
            logger.error(f"Failed to delete common model {model_id}: {str(e)}")
            return {
                "success": False,
                "error": f"削除処理中にエラーが発生しました: {str(e)}"
            }
    
    async def add_models(self, models_data: List[Dict[str, Any]], db: Session) -> Dict[str, Any]:
        """共通モデルを追加"""
        try:
            created_models = []
            
            for model_data in models_data:
                # 共通モデルを作成
                model = Model(
                    api_id=None,  # 共通モデルはapi_idがNULL
                    name=model_data["name"],
                    description=model_data.get("description", ""),
                    is_common=True
                )
                db.add(model)
                db.flush()  # IDを取得するため
                
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
                
                created_models.append(model.name)
            
            db.commit()
            
            logger.info(f"Created {len(created_models)} common models: {created_models}")
            return {
                "success": True,
                "message": f"{len(created_models)}個の共通modelを追加しました",
                "models": created_models
            }
            
        except Exception as e:
            db.rollback()
            logger.error(f"Failed to add common models: {str(e)}")
            return {"success": False, "error": str(e)}
    
    async def get_model_detail(self, model_id: int, db: Session) -> Dict[str, Any]:
        """共通モデルの詳細情報を取得"""
        try:
            model = db.query(Model).filter(
                Model.id == model_id, 
                Model.is_common == True,
                Model.is_active == True
            ).first()
            
            if not model:
                return {"success": False, "error": "共通modelが見つかりません"}
            
            # フィールド情報を取得
            fields = []
            for field in sorted(model.model_values, key=lambda f: f.sort_order):
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
            
            return {
                "success": True,
                "model": {
                    "id": model.id,
                    "name": model.name,
                    "description": model.description,
                    "fields": fields,
                    "created_at": model.created_at.isoformat(),
                    "updated_at": model.updated_at.isoformat()
                }
            }
            
        except Exception as e:
            logger.error(f"Failed to get model detail: {str(e)}")
            return {"success": False, "error": str(e)}
    
    async def update_model(self, model_id: int, model_data: Dict[str, Any], db: Session) -> Dict[str, Any]:
        """共通モデルを更新"""
        try:
            logger.info(f"Starting update for common model ID: {model_id}")
            logger.info(f"Update data: {model_data}")
            
            # 共通モデルを検索
            model = db.query(Model).filter(
                Model.id == model_id,
                Model.is_common == True,
                Model.is_active == True
            ).first()
            
            if not model:
                logger.warning(f"Common model not found: ID {model_id}")
                return {
                    "success": False,
                    "error": "指定された共通モデルが見つかりません"
                }
            
            logger.info(f"Found model: {model.name} (ID: {model.id})")
            
            # モデル基本情報を更新
            logger.info("Updating model basic info")
            model.name = model_data["name"]
            model.description = model_data.get("description", "")
            logger.info(f"Updated model name to: {model.name}")
            
            # 既存のフィールドをすべて削除（カスケード削除でバリデーションも削除）
            existing_fields_count = len(model.model_values)
            logger.info(f"Deleting {existing_fields_count} existing model values")
            
            try:
                for field in model.model_values:
                    logger.info(f"Deleting model value: {field.name} (ID: {field.id})")
                    db.delete(field)
                
                # 削除を確定してユニーク制約を解除
                db.flush()
                logger.info("Successfully deleted all existing model values and flushed transaction")
            except Exception as delete_error:
                logger.error(f"Error during field deletion: {str(delete_error)}")
                raise delete_error
            
            # 新しいフィールドを作成
            new_fields = model_data.get("fields", [])
            logger.info(f"Creating {len(new_fields)} new model values")
            
            for i, field_data in enumerate(new_fields):
                logger.info(f"Creating field {i+1}: {field_data}")
                
                try:
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
                    logger.info(f"Created model value: {model_value.name} (ID: {model_value.id})")
                    
                    # バリデーション制約を作成
                    validations = field_data.get("validations", {})
                    logger.info(f"Creating {len(validations)} validations for field: {model_value.name}")
                    
                    for validation_type, validation_value in validations.items():
                        logger.info(f"Creating validation: {validation_type} = {validation_value}")
                        model_value_validation = ModelValueValidation(
                            model_value_id=model_value.id,
                            validation_type=validation_type,
                            validation_value=str(validation_value)
                        )
                        db.add(model_value_validation)
                        
                except Exception as field_error:
                    logger.error(f"Error creating field {i+1} ({field_data.get('name', 'unknown')}): {str(field_error)}")
                    raise field_error
            
            logger.info("Attempting to commit transaction")
            db.commit()
            logger.info("Transaction committed successfully")
            
            logger.info(f"Updated common model: {model.name} (ID: {model_id})")
            return {
                "success": True,
                "message": f"共通モデル '{model.name}' を更新しました"
            }
            
        except Exception as e:
            logger.error(f"Exception occurred during update: {type(e).__name__}: {str(e)}")
            logger.error(f"Exception details: ", exc_info=True)
            db.rollback()
            logger.info("Transaction rolled back")
            return {
                "success": False,
                "error": f"更新処理中にエラーが発生しました: {str(e)}"
            }