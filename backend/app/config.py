from pathlib import Path
from pydantic import BaseModel
from typing import Optional
import os

from app.core.paths import paths


class Settings(BaseModel):
    APP_NAME: str = "RSOD Detection Platform"
    APP_VERSION: str = "1.0.0"
    DEBUG: bool = True
    
    HOST: str = "0.0.0.0"
    PORT: int = 8000
    
    # Paths are now centrally managed by app.core.paths.
    STATIC_DIR: str = str(paths.static)
    UPLOAD_DIR: str = str(paths.uploads)
    RESULT_DIR: str = str(paths.results)
    
    # 语义分割模型路径 (DeepLabV3+ / ResNet50)
    SEGMENTATION_MODEL_PATH: str = str(paths.models / "land_seg_best.pth")
    
    CONFIDENCE_THRESHOLD: float = 0.5
    IOU_THRESHOLD: float = 0.45
    
    CORS_ORIGINS: list = ["http://localhost:5173", "http://localhost:3000"]


def get_settings() -> Settings:
    settings = Settings()
    
    env_file = ".env"
    if os.path.exists(env_file):
        with open(env_file, "r", encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith("#"):
                    key, value = line.split("=", 1)
                    if hasattr(settings, key):
                        try:
                            setattr(settings, key, type(getattr(settings, key))(value))
                        except ValueError:
                            pass
    
    return settings


settings = get_settings()
