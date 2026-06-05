"""
项目配置文件

支持两种配置方式：
  1. 本地开发：从 .env 文件读取（使用 python-dotenv）
  2. Streamlit Cloud 部署：从 st.secrets 读取

优先使用 st.secrets（Cloud），回退到 .env（本地）
"""

import os
from dotenv import load_dotenv

# 加载 .env 文件（本地开发时使用，Cloud 环境下此文件不存在也没关系）
load_dotenv()


def _get_config(key: str, default: str = "") -> str:
    """
    统一配置读取：
    先尝试 st.secrets（Streamlit Cloud），再回退到环境变量（本地 .env）
    """
    try:
        import streamlit as st

        # st.secrets 在本地没有配置时会抛出异常
        value = st.secrets.get(key, None)
        if value:
            return value
    except Exception:
        pass

    return os.getenv(key, default)


# DeepSeek API 配置
DEEPSEEK_API_KEY = _get_config("DEEPSEEK_API_KEY", "")
DEEPSEEK_BASE_URL = _get_config("DEEPSEEK_BASE_URL", "https://api.deepseek.com")
DEEPSEEK_MODEL = _get_config("DEEPSEEK_MODEL", "deepseek-chat")

# 历史记录文件路径（Cloud 环境用内存存储，此路径仅本地使用）
HISTORY_FILE = os.path.join(os.path.dirname(__file__), "data", "history.json")

# 支持的关卡类型
LEVEL_TYPES = {
    "stealth": "2D 潜入关卡",
    "platformer": "2D 平台跳跃关卡",
    "puzzle": "2D 解谜关卡",
    "combat": "2D 动作战斗关卡",
    "exploration": "2D 探索冒险关卡",
}
