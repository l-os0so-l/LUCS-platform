import os
from typing import Optional

from fastapi import APIRouter, UploadFile, File, Form, HTTPException, Query
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
)
from app.services.detection_service import detection_service
from app.services.history_service import history_service
from app.utils.file_utils import save_upload_file, ensure_directories

router = APIRouter(prefix="/detection", tags=["detection"])

ensure_directories()


@router.post("/single", response_model=SingleDetectionResponse)
async def detect_single_image(
    file: UploadFile = File(...),
    model_name: str = Form("land-seg-v1")
):
    try:
        original_filename = file.filename or "unknown.jpg"
        filename = await save_upload_file(file)
        image_path = str(paths.uploads / filename)

        result = detection_service.detect_single_image(image_path, model_name)

        # 自动保存历史记录
        record_dict = result.dict()
        record_dict["filename"] = original_filename
        history_service.add_record(record_dict)

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
):
    """分页获取检测历史记录"""
    records, total = history_service.get_records(
        page=page,
        page_size=page_size,
        search=search,
        filter_model=model_name,
    )
    # 将 dict 列表转换为 HistoryRecord
    parsed = []
    for r in records:
        try:
            parsed.append(HistoryRecord(**r))
        except Exception as exc:
            import logging
            logging.getLogger(__name__).warning("Skipping malformed record: %s", exc)
    return HistoryListResponse(
        success=True,
        message="获取成功",
        data=parsed,
        total=total,
        page=page,
        page_size=page_size,
    )


@router.get("/history/{detection_id}", response_model=HistoryDetailResponse)
async def get_history_detail(detection_id: str):
    """获取单条历史记录详情"""
    record = history_service.get_record_by_id(detection_id)
    if record is None:
        raise HTTPException(status_code=404, detail="记录不存在")
    try:
        parsed = HistoryRecord(**record)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"数据解析错误: {str(e)}")
    return HistoryDetailResponse(success=True, message="获取成功", data=parsed)


@router.delete("/history/{detection_id}", response_model=DeleteResponse)
async def delete_history(detection_id: str):
    """删除指定历史记录（不删除对应图片文件）"""
    ok = history_service.delete_record(detection_id)
    if not ok:
        raise HTTPException(status_code=404, detail="记录不存在")
    return DeleteResponse(success=True, message="删除成功")


# ── 目标类型接口 ──────────────────────────────────────────────────────────────

@router.get("/targets/list", response_model=TargetListResponse)
async def get_target_list():
    targets = [
        TargetItem(id=0, name="background", chinese_name="背景", description="非目标区域"),
        TargetItem(id=1, name="building", chinese_name="建筑", description="房屋、楼宇等人工建筑"),
        TargetItem(id=2, name="road", chinese_name="道路", description="公路、街道等交通道路"),
        TargetItem(id=3, name="water", chinese_name="水域", description="河流、湖泊、水库等水体"),
        TargetItem(id=4, name="barren", chinese_name="裸地", description="未利用土地、荒漠等"),
        TargetItem(id=5, name="forest", chinese_name="林地", description="森林、灌木等植被覆盖区"),
        TargetItem(id=6, name="agriculture", chinese_name="耕地", description="农田、种植用地等"),
    ]
    return TargetListResponse(
        success=True,
        message="获取成功",
        data=targets
    )
