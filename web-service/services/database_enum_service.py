from typing import List, Dict, Any, Optional
from sqlalchemy.orm import Session
from models.database_models import Enum, EnumValue
from database import get_db
import logging

logger = logging.getLogger(__name__)

class DatabaseEnumService:
    """データベースベースのEnum管理サービス"""
    
    def __init__(self):
        pass
    
    async def create_enums(self, enums_data: List[Dict[str, Any]], db: Session) -> Dict[str, Any]:
        """新しいEnumを作成"""
        try:
            created_enums = []
            
            for enum_data in enums_data:
                enum_name = enum_data["name"]
                description = enum_data.get("description", "")
                values = enum_data.get("values", [])
                
                # Enumを作成
                enum = Enum(
                    name=enum_name,
                    description=description
                )
                db.add(enum)
                db.flush()  # IDを取得するため
                
                # Enum値を作成
                for i, value_data in enumerate(values):
                    enum_value = EnumValue(
                        enum_id=enum.id,
                        name=value_data["name"],
                        description=value_data.get("description", ""),
                        sort_order=i + 1
                    )
                    db.add(enum_value)
                
                created_enums.append({
                    "id": enum.id,
                    "name": enum.name,
                    "description": enum.description
                })
            
            db.commit()
            
            logger.info(f"{len(created_enums)} Enums created")
            return {
                "success": True,
                "message": f"{len(created_enums)}個のEnumを作成しました",
                "enums": created_enums
            }
            
        except Exception as e:
            db.rollback()
            logger.error(f"Failed to create Enums: {str(e)}")
            return {"success": False, "error": str(e)}
    
    async def get_enum_list(self, db: Session) -> List[Dict[str, Any]]:
        """Enum一覧を取得"""
        try:
            enums = db.query(Enum).filter(Enum.is_active == True).order_by(Enum.updated_at.desc()).all()
            
            enum_list = []
            for enum in enums:
                values = []
                for enum_value in sorted(enum.enum_values, key=lambda v: v.sort_order):
                    values.append({
                        "name": enum_value.name,
                        "description": enum_value.description
                    })
                
                enum_list.append({
                    "id": enum.id,
                    "name": enum.name,
                    "description": enum.description,
                    "values": values,
                    "created_at": enum.created_at.isoformat(),
                    "updated_at": enum.updated_at.isoformat()
                })
            
            return enum_list
            
        except Exception as e:
            logger.error(f"Failed to get Enum list: {str(e)}")
            return []
    
    async def get_enum_detail(self, enum_id: int, db: Session) -> Optional[Dict[str, Any]]:
        """Enum詳細情報を取得"""
        try:
            enum = db.query(Enum).filter(Enum.id == enum_id, Enum.is_active == True).first()
            if not enum:
                return None
            
            values = []
            for enum_value in sorted(enum.enum_values, key=lambda v: v.sort_order):
                values.append({
                    "name": enum_value.name,
                    "description": enum_value.description
                })
            
            return {
                "id": enum.id,
                "name": enum.name,
                "description": enum.description,
                "values": values,
                "created_at": enum.created_at.isoformat(),
                "updated_at": enum.updated_at.isoformat()
            }
            
        except Exception as e:
            logger.error(f"Failed to get Enum detail: {str(e)}")
            return None
    
    async def update_enum(self, enum_id: int, enum_data: Dict[str, Any], db: Session) -> Dict[str, Any]:
        """Enumを更新"""
        try:
            logger.info(f"Starting update for Enum ID: {enum_id}")
            logger.info(f"Update data: {enum_data}")
            
            enum = db.query(Enum).filter(Enum.id == enum_id, Enum.is_active == True).first()
            if not enum:
                logger.warning(f"Enum not found: ID {enum_id}")
                return {"success": False, "error": "Enumが見つかりません"}
            
            logger.info(f"Found enum: {enum.name} (ID: {enum.id})")
            
            # Enum基本情報を更新
            logger.info("Updating enum basic info")
            enum.name = enum_data.get("name", enum.name)
            enum.description = enum_data.get("description", enum.description)
            logger.info(f"Updated enum name to: {enum.name}")
            
            # 既存のEnum値をすべて削除
            existing_values_count = len(enum.enum_values)
            logger.info(f"Deleting {existing_values_count} existing enum values")
            
            try:
                for enum_value in enum.enum_values:
                    logger.info(f"Deleting enum value: {enum_value.name} (ID: {enum_value.id})")
                    db.delete(enum_value)
                
                # 削除を確定してユニーク制約を解除
                db.flush()
                logger.info("Successfully deleted all existing enum values and flushed transaction")
            except Exception as delete_error:
                logger.error(f"Error during enum value deletion: {str(delete_error)}")
                raise delete_error
            
            # 新しいEnum値を追加
            values = enum_data.get("values", [])
            logger.info(f"Creating {len(values)} new enum values")
            
            for i, value_data in enumerate(values):
                logger.info(f"Creating enum value {i+1}: {value_data}")
                
                try:
                    enum_value = EnumValue(
                        enum_id=enum.id,
                        name=value_data["name"],
                        description=value_data.get("description", ""),
                        sort_order=i + 1
                    )
                    db.add(enum_value)
                    db.flush()
                    logger.info(f"Created enum value: {enum_value.name} (ID: {enum_value.id})")
                    
                except Exception as value_error:
                    logger.error(f"Error creating enum value {i+1} ({value_data.get('name', 'unknown')}): {str(value_error)}")
                    raise value_error
            
            logger.info("Attempting to commit transaction")
            db.commit()
            logger.info("Transaction committed successfully")
            
            logger.info(f"Enum '{enum.name}' updated")
            return {
                "success": True,
                "message": f"Enum '{enum.name}' を更新しました",
                "enum_id": enum.id
            }
            
        except Exception as e:
            logger.error(f"Exception occurred during enum update: {type(e).__name__}: {str(e)}")
            logger.error(f"Exception details: ", exc_info=True)
            db.rollback()
            logger.info("Transaction rolled back")
            return {"success": False, "error": str(e)}
    
    async def delete_enum(self, enum_id: int, db: Session) -> Dict[str, Any]:
        """Enumを削除（論理削除）"""
        try:
            enum = db.query(Enum).filter(Enum.id == enum_id, Enum.is_active == True).first()
            if not enum:
                return {"success": False, "error": "Enumが見つかりません"}
            
            # 論理削除
            enum.is_active = False
            db.commit()
            
            logger.info(f"Enum '{enum.name}' deleted")
            return {
                "success": True,
                "message": f"Enum '{enum.name}' を削除しました"
            }
            
        except Exception as e:
            db.rollback()
            logger.error(f"Failed to delete Enum: {str(e)}")
            return {"success": False, "error": str(e)}