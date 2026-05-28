import logging
import os
from typing import Optional

from fastapi import APIRouter, UploadFile, File, Form, HTTPException, Query, Depends
from fastapi.responses import FileResponse

from app.config import settings
from app.core.paths import paths
from app.models.schemas import (
    SingleDetectionResponse,
    TargetListResponse,
    TargetItem,
    HistoryListResponse,
    HistoryDetailResponse,
    DeleteResponse,
    HistoryRecord,
    RealtimeSegmentationResponse,
)
from app.services.detection_service import detection_service
from app.services.history_service import history_service
from app.utils.file_utils import save_upload_file, ensure_directories
from app.database import get_db
from app.models.database import DetectionRecord, User
from app.utils.security import get_current_user
from sqlalchemy.orm import Session

router = APIRouter(prefix="/detection", tags=["detection"])

ensure_directories()


@router.post("/single", response_model=SingleDetectionResponse)
async def detect_single_image(
    file: UploadFile = File(...),
    model_name: str = Form("land-seg-v1"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    try:
        original_filename = file.filename or "unknown.jpg"
        filename = await save_upload_file(file)
        image_path = str(paths.uploads / filename)

        result = detection_service.detect_single_image(image_path, model_name)

        # 保存到 JSON（兼容旧版）
        record_dict = result.dict()
        record_dict["filename"] = original_filename
        history_service.add_record(record_dict)

        # 保存到数据库（绑定用户）
        db_record = DetectionRecord(
            id=result.detection_id,
            user_id=current_user.id if current_user else None,
            filename=original_filename,
            model_name=model_name,
            type="single",
            image_url=result.image_url,
            result_image_url=result.result_image_url,
            overlay_image_url=result.overlay_image_url,
            class_stats=[s.dict() for s in result.class_stats],
            total_pixels=result.total_pixels,
            inference_time=result.inference_time,
        )
        db.add(db_record)
        db.commit()

        return SingleDetectionResponse(
            success=True,
            message="分类成功",
            data=result
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"分类失败: {str(e)}")


# ── 历史记录接口 ──────────────────────────────────────────────────────────────

@router.get("/history", response_model=HistoryListResponse)
async def get_history(
    page: int = Query(1, ge=1, description="页码"),
    page_size: int = Query(10, ge=1, le=100, description="每页条数"),
    search: Optional[str] = Query(None, description="搜索文件名或ID"),
    model_name: Optional[str] = Query(None, description="按模型名称过滤"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """分页获取当前用户的检测历史记录"""
    from sqlalchemy import desc, or_

    if not current_user:
        raise HTTPException(status_code=401, detail="请先登录")

    query = db.query(DetectionRecord).filter(DetectionRecord.user_id == current_user.id)
    if search:
        query = query.filter(
            or_(
                DetectionRecord.filename.ilike(f"%{search}%"),
                DetectionRecord.id.ilike(f"%{search}%"),
            )
        )
    if model_name:
        query = query.filter(DetectionRecord.model_name == model_name)

    total = query.count()
    records = query.order_by(desc(DetectionRecord.created_at)).offset((page - 1) * page_size).limit(page_size).all()

    parsed = []
    for r in records:
        parsed.append(HistoryRecord(
            detection_id=r.id,
            filename=r.filename,
            image_url=r.image_url,
            result_image_url=r.result_image_url,
            overlay_image_url=r.overlay_image_url,
            class_stats=r.class_stats or [],
            total_pixels=r.total_pixels,
            inference_time=r.inference_time,
            model_name=r.model_name,
            created_at=r.created_at,
        ))

    return HistoryListResponse(
        success=True,
        message="获取成功",
        data=parsed,
        total=total,
        page=page,
        page_size=page_size,
    )


@router.get("/history/{detection_id}", response_model=HistoryDetailResponse)
async def get_history_detail(
    detection_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """获取单条历史记录详情（仅允许查看自己的记录）"""
    if not current_user:
        raise HTTPException(status_code=401, detail="请先登录")

    r = db.query(DetectionRecord).filter(
        DetectionRecord.id == detection_id,
        DetectionRecord.user_id == current_user.id,
    ).first()
    if r is None:
        # 数据库没有则回退到 JSON
        record = history_service.get_record_by_id(detection_id)
        if record is None:
            raise HTTPException(status_code=404, detail="记录不存在")
        try:
            parsed = HistoryRecord(**record)
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"数据解析错误: {str(e)}")
        return HistoryDetailResponse(success=True, message="获取成功", data=parsed)

    parsed = HistoryRecord(
        detection_id=r.id,
        filename=r.filename,
        image_url=r.image_url,
        result_image_url=r.result_image_url,
        overlay_image_url=r.overlay_image_url,
        class_stats=r.class_stats or [],
        total_pixels=r.total_pixels,
        inference_time=r.inference_time,
        model_name=r.model_name,
        created_at=r.created_at,
    )
    return HistoryDetailResponse(success=True, message="获取成功", data=parsed)


@router.delete("/history/{detection_id}", response_model=DeleteResponse)
async def delete_history(
    detection_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """删除指定历史记录（仅允许删除自己的记录）"""
    if not current_user:
        raise HTTPException(status_code=401, detail="请先登录")

    r = db.query(DetectionRecord).filter(
        DetectionRecord.id == detection_id,
        DetectionRecord.user_id == current_user.id,
    ).first()
    if r:
        db.delete(r)
        db.commit()
    # 同时清理 JSON 备份
    history_service.delete_record(detection_id)
    return DeleteResponse(success=True, message="删除成功")


# ── 目标类型接口 ──────────────────────────────────────────────────────────────

# ── 视频实时帧检测接口 ─────────────────────────────────────────────────────────

@router.post("/video-frame", response_model=RealtimeSegmentationResponse)
async def detect_video_frame(
    file: UploadFile = File(...),
    model_name: str = Form("land-seg-v1")
):
    """
    实时视频帧分割接口

    接收视频播放时的单帧图片，执行语义分割，
    返回分割结果（base64 编码图片 + 像素统计），不保存到数据库。
    """
    try:
        import numpy as np
        from PIL import Image
        import io

        contents = await file.read()
        pil_img = Image.open(io.BytesIO(contents)).convert("RGB")

        result = detection_service.detect_frame_realtime(pil_img, model_name)

        return RealtimeSegmentationResponse(
            success=True,
            message="帧分割成功",
            data=result
        )
    except Exception as e:
        import traceback
        logger = logging.getLogger(__name__)
        logger.error("[视频帧分割错误] %s", traceback.format_exc())
        raise HTTPException(status_code=500, detail=f"帧分割失败: {str(e)}")


# ── 目标类型接口 ──────────────────────────────────────────────────────────────

@router.get("/targets/list", response_model=TargetListResponse)
async def get_target_list():
    """获取模型实际训练的7类土地类型列表（含颜色与说明）"""
    targets = [
        TargetItem(id=0, name="background", chinese_name="背景", description="图像边缘或无意义区域"),
        TargetItem(id=1, name="building", chinese_name="建筑", description="房屋、厂房、大棚等"),
        TargetItem(id=2, name="road", chinese_name="道路", description="公路、乡村道路"),
        TargetItem(id=3, name="water", chinese_name="水域", description="河流、湖泊、池塘"),
        TargetItem(id=4, name="barren", chinese_name="裸地", description="未耕种土地、荒地"),
        TargetItem(id=5, name="forest", chinese_name="林地", description="森林、树木覆盖区"),
        TargetItem(id=6, name="agriculture", chinese_name="耕地", description="农田、种植区"),
    ]
    return TargetListResponse(
        success=True,
        message="获取成功",
        data=targets
    )
