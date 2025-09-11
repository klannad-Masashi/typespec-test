from sqlalchemy import Column, Integer, String, Text, Boolean, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from generator.database import Base

class Api(Base):
    """API プロジェクト"""
    __tablename__ = "apis"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), unique=True, nullable=False, index=True)
    display_name = Column(String(200))
    description = Column(Text)
    namespace = Column(String(100))
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
    is_active = Column(Boolean, default=True)
    
    # リレーションシップ
    models = relationship("Model", back_populates="api", cascade="all, delete-orphan")
    endpoints = relationship("Endpoint", back_populates="api", cascade="all, delete-orphan")

class Model(Base):
    """モデル定義（API固有または共通）"""
    __tablename__ = "models"
    
    id = Column(Integer, primary_key=True, index=True)
    api_id = Column(Integer, ForeignKey("apis.id", ondelete="CASCADE"), nullable=True)
    name = Column(String(100), nullable=False)
    description = Column(Text)
    is_common = Column(Boolean, default=False, index=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
    is_active = Column(Boolean, default=True, index=True)
    
    # リレーションシップ
    api = relationship("Api", back_populates="models")
    model_values = relationship("ModelValue", back_populates="model", cascade="all, delete-orphan")
    
    # このモデルをリクエストとして使用するエンドポイント
    request_endpoints = relationship("Endpoint", foreign_keys="Endpoint.request_model_id", back_populates="request_model")
    # このモデルをレスポンスとして使用するエンドポイント
    response_endpoints = relationship("Endpoint", foreign_keys="Endpoint.response_model_id", back_populates="response_model")
    # このモデルをエラーレスポンスとして使用するエラーレスポンス
    error_responses = relationship("ErrorResponse", back_populates="response_model")

class ModelValue(Base):
    """モデル値定義"""
    __tablename__ = "model_values"
    
    id = Column(Integer, primary_key=True, index=True)
    model_id = Column(Integer, ForeignKey("models.id", ondelete="CASCADE"), nullable=False)
    name = Column(String(100), nullable=False)
    field_type = Column(String(50), nullable=False)
    description = Column(Text)
    is_required = Column(Boolean, default=True)
    sort_order = Column(Integer, default=0)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    # リレーションシップ
    model = relationship("Model", back_populates="model_values")
    validations = relationship("ModelValueValidation", back_populates="model_value", cascade="all, delete-orphan")

class ModelValueValidation(Base):
    """モデル値バリデーション制約"""
    __tablename__ = "model_value_validations"
    
    id = Column(Integer, primary_key=True, index=True)
    model_value_id = Column(Integer, ForeignKey("model_values.id", ondelete="CASCADE"), nullable=False)
    validation_type = Column(String(50), nullable=False)  # minLength, maxLength, minimum, maximum, pattern, format
    validation_value = Column(Text, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    # リレーションシップ
    model_value = relationship("ModelValue", back_populates="validations")

class Endpoint(Base):
    """API エンドポイント定義"""
    __tablename__ = "endpoints"
    
    id = Column(Integer, primary_key=True, index=True)
    api_id = Column(Integer, ForeignKey("apis.id", ondelete="CASCADE"), nullable=False)
    method = Column(String(10), nullable=False)  # GET, POST, PUT, DELETE, PATCH
    path = Column(String(500), nullable=False)
    operation_id = Column(String(100), nullable=False)
    description = Column(Text)
    request_model_id = Column(Integer, ForeignKey("models.id", ondelete="SET NULL"), nullable=True)
    response_model_id = Column(Integer, ForeignKey("models.id", ondelete="SET NULL"), nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
    
    # リレーションシップ
    api = relationship("Api", back_populates="endpoints")
    request_model = relationship("Model", foreign_keys=[request_model_id], back_populates="request_endpoints")
    response_model = relationship("Model", foreign_keys=[response_model_id], back_populates="response_endpoints")
    error_responses = relationship("ErrorResponse", back_populates="endpoint", cascade="all, delete-orphan")

class ErrorResponse(Base):
    """エンドポイントエラーレスポンス定義"""
    __tablename__ = "error_responses"
    
    id = Column(Integer, primary_key=True, index=True)
    endpoint_id = Column(Integer, ForeignKey("endpoints.id", ondelete="CASCADE"), nullable=False)
    status_code = Column(Integer, nullable=False)
    description = Column(Text)
    response_model_id = Column(Integer, ForeignKey("models.id", ondelete="SET NULL"), nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    # リレーションシップ
    endpoint = relationship("Endpoint", back_populates="error_responses")
    response_model = relationship("Model", back_populates="error_responses")