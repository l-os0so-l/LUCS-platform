import logging
import os
import sys
import threading
import time
import types
import uuid
from datetime import datetime
from typing import Optional

# ─── numpy 2.x 兼容性补丁 ───
# 模型文件在 numpy 2.x 环境下保存（引用 numpy._core），
# Python 3.8 最高支持 numpy 1.24.x（使用 numpy.core）。
# 将 numpy._core 及其子模块映射到 numpy.core 对应模块，使 torch.load 能反序列化。
import numpy as np
if not hasattr(np, '_core'):
    import numpy.core as _nc
    _np_core = types.ModuleType('numpy._core')
    _np_core.__path__ = []
    _np_core.__package__ = 'numpy._core'
    for _n in dir(_nc):
        if not _n.startswith('__'):
            setattr(_np_core, _n, getattr(_nc, _n))
    sys.modules['numpy._core'] = _np_core
    np._core = _np_core

    # numpy._core.multiarray
    import numpy.core.multiarray as _ncma
    _np_core_ma = types.ModuleType('numpy._core.multiarray')
    _np_core_ma.__path__ = []
    _np_core_ma.__package__ = 'numpy._core.multiarray'
    for _n in dir(_ncma):
        if not _n.startswith('__'):
            setattr(_np_core_ma, _n, getattr(_ncma, _n))
    sys.modules['numpy._core.multiarray'] = _np_core_ma

    # numpy._core._multiarray_umath
    import numpy.core._multiarray_umath as _ncumu
    _np_core_um = types.ModuleType('numpy._core._multiarray_umath')
    _np_core_um.__path__ = []
    _np_core_um.__package__ = 'numpy._core._multiarray_umath'
    for _n in dir(_ncumu):
        if not _n.startswith('__'):
            setattr(_np_core_um, _n, getattr(_ncumu, _n))
    sys.modules['numpy._core._multiarray_umath'] = _np_core_um

import base64
import io

import torch
from PIL import Image

from app.config import settings
from app.core.paths import paths
from app.models.schemas import ClassStat, SegmentationResult, RealtimeSegmentationResult
from app.utils.file_utils import get_file_url

logger = logging.getLogger(__name__)

DEVICE = torch.device("cuda" if torch.cuda.is_available() else "cpu")

# ─── 7 类土地分类定义 ───
LAND_CLASSES = {
    0: {"name": "背景",   "english": "background",  "color": [0, 0, 0]},
    1: {"name": "荒地",   "english": "barren",      "color": [139, 69, 19]},
    2: {"name": "建筑",   "english": "building",    "color": [255, 0, 0]},
    3: {"name": "道路",   "english": "road",        "color": [255, 255, 0]},
    4: {"name": "水域",   "english": "water",       "color": [0, 0, 255]},
    5: {"name": "耕地",   "english": "agriculture", "color": [0, 255, 0]},
    6: {"name": "森林",   "english": "forest",      "color": [0, 128, 0]},
}

NUM_CLASSES = 7  # 0-6

# 预计算调色板 (用于快速生成伪彩色图)
PALETTE = np.zeros((NUM_CLASSES, 3), dtype=np.uint8)
for cid, info in LAND_CLASSES.items():
    PALETTE[cid] = info["color"]


def _hex_color(rgb):
    """RGB tuple -> HEX string"""
    return "#{:02x}{:02x}{:02x}".format(int(rgb[0]), int(rgb[1]), int(rgb[2]))


def _load_deeplabv3_model():
    """加载 DeepLabV3+ / ResNet50 语义分割模型"""
    import segmentation_models_pytorch as smp

    model_path = settings.SEGMENTATION_MODEL_PATH
    if not os.path.exists(model_path):
        raise FileNotFoundError(f"Segmentation model not found: {model_path}")

    logger.info("Loading DeepLabV3+ model from %s", model_path)

    # 创建与训练时一致的模型结构
    model = smp.DeepLabV3Plus(
        encoder_name="resnet50",
        encoder_weights=None,       # 不加载预训练 encoder，用本地权重
        classes=NUM_CLASSES,
    )

    # 加载训练好的权重（weights_only=False 以兼容 pickle 格式）
    checkpoint = torch.load(model_path, map_location=DEVICE, weights_only=False)

    # 兼容不同保存格式
    if isinstance(checkpoint, dict):
        if "model_state_dict" in checkpoint:
            state_dict = checkpoint["model_state_dict"]
        elif "state_dict" in checkpoint:
            state_dict = checkpoint["state_dict"]
        else:
            state_dict = checkpoint
    else:
        state_dict = checkpoint

    model.load_state_dict(state_dict)
    model.to(DEVICE)
    model.eval()

    logger.info("DeepLabV3+ model loaded on %s", DEVICE)
    return model


def _preprocess_image(pil_img, target_size=512):
    """
    预处理图片用于 DeepLabV3+ 推理
    - Resize 到 target_size 的倍数（保持长宽比，短边对齐）
    - 归一化到 [0,1]，ImageNet 标准化
    - 返回 tensor 和原始尺寸
    """
    orig_w, orig_h = pil_img.size

    # 计算缩放尺寸（短边对齐 target_size，保持长宽比）
    scale = target_size / min(orig_w, orig_h)
    new_w = int(orig_w * scale)
    new_h = int(orig_h * scale)
    # 确保是 32 的倍数（DeepLabV3+ 下采样 16/32 倍）
    new_w = ((new_w + 31) // 32) * 32
    new_h = ((new_h + 31) // 32) * 32

    resized = pil_img.resize((new_w, new_h), Image.BILINEAR)
    img_np = np.array(resized, dtype=np.float32) / 255.0

    # ImageNet 标准化
    mean = np.array([0.485, 0.456, 0.406], dtype=np.float32)
    std = np.array([0.229, 0.224, 0.225], dtype=np.float32)
    img_np = (img_np - mean) / std

    # HWC -> CHW
    img_np = img_np.transpose(2, 0, 1)
    tensor = torch.from_numpy(img_np).unsqueeze(0).to(DEVICE)

    return tensor, (orig_h, orig_w), (new_h, new_w)


def _predict(model, pil_img):
    """
    运行推理，返回与原图同尺寸的分割 mask (H, W)，值为类别 id 0-6
    """
    tensor, (orig_h, orig_w), (new_h, new_w) = _preprocess_image(pil_img)

    with torch.no_grad():
        logits = model(tensor)  # (1, NUM_CLASSES, new_h, new_w)

    # 取 argmax 得到每个像素的类别
    pred = logits.argmax(dim=1).squeeze(0).cpu().numpy()  # (new_h, new_w)

    # Resize 回原图尺寸
    pred_pil = Image.fromarray(pred.astype(np.uint8))
    pred_resized = pred_pil.resize((orig_w, orig_h), Image.NEAREST)
    mask = np.array(pred_resized)

    return mask


def _compute_class_stats(mask):
    """根据分割 mask 计算各类别像素统计"""
    total = mask.size
    stats = []

    for cid in range(NUM_CLASSES):
        count = int(np.sum(mask == cid))
        info = LAND_CLASSES[cid]
        stats.append(ClassStat(
            class_id=cid,
            class_name=info["name"],
            pixel_count=count,
            pixel_ratio=round(count / total, 4) if total > 0 else 0.0,
            color_hex=_hex_color(info["color"]),
        ))

    return stats, total


def _save_visualizations(orig_img, mask, result_dir, result_id):
    """
    保存伪彩色分割图和叠加图
    - mask.png: 伪彩色分割图
    - overlay.png: 原图 + 伪彩色半透明叠加
    """
    h, w = mask.shape

    # 伪彩色分割图
    color_mask = PALETTE[mask]  # (H, W, 3) 快速查表

    # 叠加图 (60% 原图 + 40% 分割色)
    overlay = (orig_img * 0.6 + color_mask * 0.4).astype(np.uint8)

    # 保存
    mask_path = result_dir / f"{result_id}_mask.png"
    Image.fromarray(color_mask).save(mask_path)

    overlay_path = result_dir / f"{result_id}_overlay.png"
    Image.fromarray(overlay).save(overlay_path)

    return mask_path.name, overlay_path.name


class DetectionService:
    """语义分割服务（DeepLabV3+ / ResNet50, 7类土地分类）"""

    def __init__(self):
        self.model = None
        self._lock = threading.Lock()
        self._load_model()

    def _load_model(self):
        try:
            self.model = _load_deeplabv3_model()
            logger.info("DeepLabV3+ model ready. %d classes: %s",
                        NUM_CLASSES, [LAND_CLASSES[i]["name"] for i in range(NUM_CLASSES)])
        except FileNotFoundError as e:
            logger.warning("Model file not found, detection will be unavailable: %s", e)
            self.model = None
        except Exception as e:
            logger.error("Failed to load segmentation model: %s", e)
            self.model = None

    def detect_single_image(self, image_path, model_name="land-seg-v1"):
        if self.model is None:
            raise RuntimeError(
                "分割模型未加载，请将 land_seg_best.pth 放入 backend/models/ 目录后重启服务"
            )

        start_time = time.time()
        detection_id = str(uuid.uuid4())
        image_name = os.path.basename(image_path)

        logger.info("Starting segmentation: id=%s image=%s", detection_id, image_name)

        # 读取原图
        orig_pil = Image.open(image_path).convert("RGB")
        orig_img = np.array(orig_pil)

        # 推理（加锁，PyTorch 模型非线程安全）
        with self._lock:
            mask = _predict(self.model, orig_pil)

        # 统计
        class_stats, total_pixels = _compute_class_stats(mask)

        # 保存可视化
        result_dir = paths.ensure_dir(paths.results)
        mask_filename, overlay_filename = _save_visualizations(
            orig_img, mask, result_dir, detection_id
        )

        inference_time = time.time() - start_time
        logger.info(
            "Segmentation complete: id=%s time=%.3fs classes_found=%d",
            detection_id, inference_time,
            len([s for s in class_stats if s.pixel_count > 0 and s.class_id > 0]),
        )

        return SegmentationResult(
            detection_id=detection_id,
            image_url=get_file_url(image_name, settings.UPLOAD_DIR),
            result_image_url=get_file_url(mask_filename, settings.RESULT_DIR),
            overlay_image_url=get_file_url(overlay_filename, settings.RESULT_DIR),
            class_stats=class_stats,
            total_pixels=total_pixels,
            inference_time=round(inference_time, 3),
            model_name=model_name,
            created_at=datetime.now(),
        )

    def detect_frame_realtime(self, pil_img, model_name="land-seg-v1"):
        """
        实时视频帧分割（不保存到数据库和文件系统）

        参数:
            pil_img: PIL Image 对象 (RGB)
            model_name: 模型名称

        返回:
            RealtimeSegmentationResult: 包含 base64 图片和像素统计
        """
        if self.model is None:
            raise RuntimeError(
                "分割模型未加载，请将 land_seg_best.pth 放入 backend/models/ 目录后重启服务"
            )

        start_time = time.time()
        orig_img = np.array(pil_img)

        # 推理（加锁，PyTorch 模型非线程安全）
        with self._lock:
            mask = _predict(self.model, pil_img)

        # 统计
        class_stats, total_pixels = _compute_class_stats(mask)

        # 生成伪彩色分割图和叠加图
        h, w = mask.shape
        color_mask = PALETTE[mask]
        overlay = (orig_img * 0.6 + color_mask * 0.4).astype(np.uint8)

        # 编码为 base64（PNG 格式，无损）
        def _img_to_base64(img_arr):
            buf = io.BytesIO()
            Image.fromarray(img_arr).save(buf, format="PNG")
            return base64.b64encode(buf.getvalue()).decode("utf-8")

        mask_base64 = _img_to_base64(color_mask)
        overlay_base64 = _img_to_base64(overlay)

        inference_time = time.time() - start_time
        logger.info(
            "Realtime segmentation: time=%.3fs classes_found=%d",
            inference_time,
            len([s for s in class_stats if s.pixel_count > 0 and s.class_id > 0]),
        )

        return RealtimeSegmentationResult(
            class_stats=class_stats,
            total_pixels=total_pixels,
            inference_time=round(inference_time, 3),
            model_name=model_name,
            image_width=w,
            image_height=h,
            mask_base64=mask_base64,
            overlay_base64=overlay_base64,
        )


detection_service = DetectionService()
