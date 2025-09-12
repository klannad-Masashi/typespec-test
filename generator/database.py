"""
Generator用データベース接続設定
Web Serviceと同じデータベースに接続
"""

from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
import os

# データベース接続設定
DATABASE_URL = os.getenv(
    "DATABASE_URL", 
    "postgresql://postgres:postgres@web-db:5432/typespec-info"
)

# SQLAlchemy エンジン作成
engine = create_engine(DATABASE_URL)

# セッションファクトリー作成
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# ベースクラス作成
Base = declarative_base()

def get_db():
    """データベースセッション取得"""
    db = SessionLocal()
    try:
        return db
    finally:
        db.close()

def get_db_session():
    """データベースセッション取得（with文用）"""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()