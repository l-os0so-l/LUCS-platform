from pydantic import BaseModel
from typing import List, Optional
from datetime import datetime


# ─── 语义分割 Schema ───

class ClassStat(BaseModel):
    """单类别的像素统计信息"""
    class_id: int
    class_name: str
    pixel_count: int
    pixel_ratio: float          # 占比，0~1
    color_hex: str              # 可视化颜色，如 "#FF0000"


class SegmentationResult(BaseModel):
    """语义分割推理结果"""
    detection_id: str
    image_url: str              # 原始图片 URL
    result_image_url: str       # 伪彩色分割图 URL
    overlay_image_url: str      # 叠加图 URL（原图 + 伪彩色半透明叠加）
    class_stats: List[ClassStat]  # 各类别像素统计
    total_pixels: int
    inference_time: float
    model_name: str
    created_at: datetime


class SingleDetectionResponse(BaseModel):
    success: bool
    message: str
    data: Optional[SegmentationResult] = None


class HistoryRecord(BaseModel):
    """历史记录单条数据（完整字段，与 SegmentationResult 对应）"""
    detection_id: str
    filename: str                       # 原始文件名
    image_url: str
    result_image_url: str
    overlay_image_url: str
    class_stats: List[ClassStat]
    total_pixels: int
    inference_time: float
    model_name: str
    created_at: datetime


class HistoryListResponse(BaseModel):
    success: bool
    message: str
    data: List[HistoryRecord]
    total: int
    page: int
    page_size: int


class HistoryDetailResponse(BaseModel):
    success: bool
    message: str
    data: Optional[HistoryRecord] = None


class DeleteResponse(BaseModel):
    success: bool
    message: str


# ─── 视频实时分割 Schema ───

class RealtimeSegmentationResult(BaseModel):
    """视频实时帧分割结果（不保存到数据库/文件系统）"""
    class_stats: List[ClassStat]       # 各类别像素统计
    total_pixels: int
    inference_time: float              # 推理耗时（秒）
    model_name: str
    image_width: int
    image_height: int
    mask_base64: Optional[str] = None   # 伪彩色分割图 base64
    overlay_base64: Optional[str] = None  # 叠加图 base64


class RealtimeSegmentationResponse(BaseModel):
    success: bool
    message: str
    data: Optional[RealtimeSegmentationResult] = None


class TargetItem(BaseModel):
    id: int
    name: str
    chinese_name: str
    description: Optional[str] = None


class TargetListResponse(BaseModel):
    success: bool
    message: str
    data: List[TargetItem]
