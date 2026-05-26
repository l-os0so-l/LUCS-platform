import logging
import shutil
from pathlib import Path
from typing import Optional, Union
from fastapi import UploadFile

from app.core.paths import paths

logger = logging.getLogger(__name__)


def ensure_directories():
    """确保必要的目录存在"""
    paths.init_all_dirs()
    logger.debug("All required directories ensured")


async def save_upload_file(file: UploadFile, upload_dir: Optional[Union[str, Path]] = None) -> str:
    """保存上传的文件

    Args:
        file: FastAPI UploadFile 对象
        upload_dir: 目标目录。默认使用 paths.uploads

    Returns:
        保存后的文件名（含时间戳前缀）
    """
    target_dir = Path(upload_dir) if upload_dir else paths.uploads
    paths.ensure_dir(target_dir)

    # 使用原始文件名，添加时间戳避免冲突
    import time
    timestamp = int(time.time())
    filename = f"{timestamp}_{file.filename}"
    file_path = target_dir / filename

    with open(file_path, "wb") as f:
        content = await file.read()
        f.write(content)

    logger.info(
        "Uploaded file saved: %s (size: %d bytes)",
        filename,
        len(content),
    )
    return filename


def get_file_url(filename: str, dir_path: Union[str, Path]) -> str:
    """获取文件的访问 URL

    基于 static 目录计算相对路径，确保无论传入绝对路径还是相对路径
    都能生成正确的 /static/... URL。
    """
    dir_path = Path(dir_path).resolve()
    static_dir = paths.static.resolve()

    try:
        # 计算 dir_path 相对于 static 目录的路径
        rel_path = dir_path.relative_to(static_dir)
        url_path = "/static"
        if rel_path.parts:
            url_path += "/" + "/".join(rel_path.parts)
    except ValueError:
        # 如果不在 static 目录下，fallback：直接用目录名拼接
        url_path = "/static/" + dir_path.name

    return f"{url_path}/{filename}"
