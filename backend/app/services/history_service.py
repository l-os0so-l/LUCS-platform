"""历史记录服务 — 基于 JSON 文件的轻量持久化存储。

设计原则：
- 无需数据库依赖，使用单个 JSON 文件存储所有记录
- 线程安全读写（文件级锁）
- 记录按时间倒序返回
"""

from __future__ import annotations

import json
import logging
import threading
from datetime import datetime
from pathlib import Path
from typing import List, Optional

from app.core.paths import paths

logger = logging.getLogger(__name__)

_HISTORY_FILE_NAME = "detection_history.json"


class HistoryService:
    """历史记录管理服务（文件存储）"""

    def __init__(self) -> None:
        self._lock = threading.Lock()
        self._history_file: Path = paths.data / _HISTORY_FILE_NAME
        paths.ensure_dir(paths.data)
        # 初始化文件
        if not self._history_file.exists():
            self._write_records([])

    # ── 私有工具 ──────────────────────────────────────────────────────────

    def _read_records(self) -> List[dict]:
        try:
            with open(self._history_file, "r", encoding="utf-8") as f:
                return json.load(f)
        except (json.JSONDecodeError, OSError) as e:
            logger.warning("Failed to read history file: %s", e)
            return []

    def _write_records(self, records: List[dict]) -> None:
        with open(self._history_file, "w", encoding="utf-8") as f:
            json.dump(records, f, ensure_ascii=False, indent=2, default=str)

    # ── 公开接口 ──────────────────────────────────────────────────────────

    def add_record(self, record: dict) -> None:
        """追加一条新记录"""
        with self._lock:
            records = self._read_records()
            records.insert(0, record)          # 新记录插到头部
            self._write_records(records)
        logger.info("History record saved: %s", record.get("detection_id"))

    def get_records(
        self,
        page: int = 1,
        page_size: int = 10,
        search: Optional[str] = None,
        filter_model: Optional[str] = None,
    ) -> tuple[List[dict], int]:
        """分页查询记录，返回 (records, total)"""
        with self._lock:
            all_records = self._read_records()

        # 过滤
        if search:
            all_records = [
                r for r in all_records
                if search.lower() in r.get("filename", "").lower()
                or search.lower() in r.get("detection_id", "").lower()
            ]
        if filter_model:
            all_records = [
                r for r in all_records
                if r.get("model_name") == filter_model
            ]

        total = len(all_records)
        start = (page - 1) * page_size
        end = start + page_size
        return all_records[start:end], total

    def get_record_by_id(self, detection_id: str) -> Optional[dict]:
        """按 detection_id 查询单条记录"""
        with self._lock:
            records = self._read_records()
        for r in records:
            if r.get("detection_id") == detection_id:
                return r
        return None

    def delete_record(self, detection_id: str) -> bool:
        """删除指定记录，返回是否成功"""
        with self._lock:
            records = self._read_records()
            before = len(records)
            records = [r for r in records if r.get("detection_id") != detection_id]
            if len(records) == before:
                return False
            self._write_records(records)
        logger.info("History record deleted: %s", detection_id)
        return True


# 全局单例
history_service = HistoryService()
