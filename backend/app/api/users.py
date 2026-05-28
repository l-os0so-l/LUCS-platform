"""
用户接口：个人信息 / 统计 / 设置更新
"""
from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy.orm import Session
from sqlalchemy import func

from app.database import get_db
from app.models.database import User, DetectionRecord
from app.utils.security import get_current_user_required

router = APIRouter(prefix="/users", tags=["users"])


class UserProfileResponse(BaseModel):
    success: bool
    message: str
    data: dict = None


class UpdateProfileRequest(BaseModel):
    nickname: str = None
    email: str = None
    location: str = None
    avatar_url: str = None


class UserStatsResponse(BaseModel):
    success: bool
    message: str
    data: dict = None


@router.get("/profile", response_model=UserProfileResponse)
def get_profile(
    user: User = Depends(get_current_user_required),
):
    return UserProfileResponse(
        success=True,
        message="获取成功",
        data={
            "id": user.id,
            "username": user.username,
            "email": user.email,
            "nickname": user.nickname,
            "role": user.role,
            "avatar_url": user.avatar_url,
            "location": user.location,
            "created_at": user.created_at.isoformat() if user.created_at else "",
        },
    )


@router.put("/profile", response_model=UserProfileResponse)
def update_profile(
    req: UpdateProfileRequest,
    user: User = Depends(get_current_user_required),
    db: Session = Depends(get_db),
):
    if req.nickname is not None:
        user.nickname = req.nickname
    if req.email is not None:
        user.email = req.email
    if req.location is not None:
        user.location = req.location
    if req.avatar_url is not None:
        user.avatar_url = req.avatar_url

    db.commit()
    db.refresh(user)

    return UserProfileResponse(
        success=True,
        message="更新成功",
        data={
            "id": user.id,
            "username": user.username,
            "email": user.email,
            "nickname": user.nickname,
            "role": user.role,
            "avatar_url": user.avatar_url,
            "location": user.location,
        },
    )


@router.get("/stats", response_model=UserStatsResponse)
def get_user_stats(
    user: User = Depends(get_current_user_required),
    db: Session = Depends(get_db),
):
    """获取用户个人统计（用于个人中心）"""
    total_count = db.query(DetectionRecord).filter(DetectionRecord.user_id == user.id).count()

    total_types = db.query(DetectionRecord.model_name).filter(DetectionRecord.user_id == user.id).distinct().count()

    avg_time_result = db.query(func.avg(DetectionRecord.inference_time)).filter(DetectionRecord.user_id == user.id).scalar()
    avg_time = round(avg_time_result or 0, 2)

    # 使用天数（从注册到今天）
    from datetime import datetime
    days = (datetime.now() - user.created_at).days if user.created_at else 0
    days = max(days, 1)

    return UserStatsResponse(
        success=True,
        message="获取成功",
        data={
            "total_classifications": total_count,
            "total_model_types": total_types or 1,
            "avg_inference_time": avg_time,
            "usage_days": days,
        },
    )
