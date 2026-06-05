"""
历史记录服务 —— 本地 JSON 文件存储
"""

import json
import os
from datetime import datetime
from config import HISTORY_FILE


def _ensure_data_dir():
    """确保 data 目录存在"""
    os.makedirs(os.path.dirname(HISTORY_FILE), exist_ok=True)


def _load_history() -> list:
    """加载历史记录"""
    _ensure_data_dir()
    if not os.path.exists(HISTORY_FILE):
        return []
    try:
        with open(HISTORY_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    except (json.JSONDecodeError, FileNotFoundError):
        return []


def _save_history(history: list):
    """保存历史记录"""
    _ensure_data_dir()
    with open(HISTORY_FILE, "w", encoding="utf-8") as f:
        json.dump(history, f, ensure_ascii=False, indent=2)


def save_record(
    level_type: str,
    user_input: dict,
    level_design: str,
    review_result: str = "",
    optimized_design: str = "",
) -> dict:
    """
    保存一条关卡设计记录

    返回:
        保存的记录对象
    """
    history = _load_history()

    record = {
        "id": datetime.now().strftime("%Y%m%d%H%M%S%f"),
        "created_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "level_type": level_type,
        "user_input": user_input,
        "level_design": level_design,
        "review_result": review_result,
        "optimized_design": optimized_design,
    }

    # 新记录插入到列表开头（最新的在前面）
    history.insert(0, record)

    # 最多保留 50 条记录
    if len(history) > 50:
        history = history[:50]

    _save_history(history)
    return record


def update_review(record_id: str, review_result: str):
    """更新某条记录的评审结果"""
    history = _load_history()
    for record in history:
        if record["id"] == record_id:
            record["review_result"] = review_result
            break
    _save_history(history)


def update_optimized(record_id: str, optimized_design: str):
    """更新某条记录的优化方案"""
    history = _load_history()
    for record in history:
        if record["id"] == record_id:
            record["optimized_design"] = optimized_design
            break
    _save_history(history)


def get_all_records() -> list:
    """获取所有历史记录（按时间倒序）"""
    return _load_history()


def get_record_by_id(record_id: str) -> dict | None:
    """根据 ID 获取单条记录"""
    history = _load_history()
    for record in history:
        if record["id"] == record_id:
            return record
    return None


def delete_record(record_id: str):
    """删除一条记录"""
    history = _load_history()
    history = [r for r in history if r["id"] != record_id]
    _save_history(history)
