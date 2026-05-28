"""
ORM 模型定义（借鉴 original 项目结构）
"""
import uuid
from datetime import datetime

from sqlalchemy import Column, String, Integer, Float, Boolean, DateTime, Text, ForeignKey, JSON
from sqlalchemy.orm import relationship

from app.database import Base


def generate_uuid():
    return str(uuid.uuid4())


class User(Base):
    """用户表"""
    __tablename__ = "users"

    id = Column(String(36), primary_key=True, default=generate_uuid)
    username = Column(String(50), unique=True, nullable=False, index=True)
    email = Column(String(100), unique=True, nullable=False, index=True)
    password_hash = Column(String(255), nullable=False)
    nickname = Column(String(50), default="")
    role = Column(String(20), default="user")  # user / admin
    avatar_url = Column(String(500), default="")
    location = Column(String(100), default="")
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.now)
    updated_at = Column(DateTime, default=datetime.now, onupdate=datetime.now)

    # 关系
    detection_records = relationship("DetectionRecord", back_populates="user", cascade="all, delete-orphan")


class DetectionRecord(Base):
    """检测记录表（替代 JSON 文件存储）"""
    __tablename__ = "detection_records"

    id = Column(String(36), primary_key=True, default=generate_uuid)
    user_id = Column(String(36), ForeignKey("users.id", ondelete="SET NULL"), nullable=True)
    filename = Column(String(255), default="")
    model_name = Column(String(50), default="land-seg-v1")
    type = Column(String(20), default="single")  # single / batch / video

    # 图片 URL（兼容现有静态文件路径）
    image_url = Column(String(500), default="")
    result_image_url = Column(String(500), default="")
    overlay_image_url = Column(String(500), default="")

    # 像素统计（JSON 存储 class_stats 列表）
    class_stats = Column(JSON, default=list)
    total_pixels = Column(Integer, default=0)
    inference_time = Column(Float, default=0.0)

    created_at = Column(DateTime, default=datetime.now)

    # 关系
    user = relationship("User", back_populates="detection_records")
