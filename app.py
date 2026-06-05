"""
AI 关卡设计助手 —— 主应用入口
面向 2D 游戏的关卡方案生成、评分与优化工具

运行方式: streamlit run app.py
"""

import streamlit as st
import sys
from pathlib import Path
from datetime import datetime

sys.path.insert(0, str(Path(__file__).parent))

from config import LEVEL_TYPES
from services.ai_client import call_ai_stream
from services.export_service import export_to_markdown

from prompts.stealth_prompt import build_stealth_prompt
from prompts.platformer_prompt import build_platformer_prompt
from prompts.puzzle_prompt import build_puzzle_prompt
from prompts.combat_prompt import build_combat_prompt
from prompts.exploration_prompt import build_exploration_prompt
from prompts.review_prompt import build_review_prompt
from prompts.optimize_prompt import build_optimize_prompt

PROMPT_BUILDERS = {
    "stealth": build_stealth_prompt,
    "platformer": build_platformer_prompt,
    "puzzle": build_puzzle_prompt,
    "combat": build_combat_prompt,
    "exploration": build_exploration_prompt,
}

st.set_page_config(
    page_title="AI 关卡设计助手",
    page_icon="",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ================================================================
#  CUSTOM CSS — 像素游戏锻造台
#  16-bit 像素风 + 暗黑工坊 + 网格画布 + RPG 数值卡
# ================================================================
st.markdown("""
<style>
/* === FONTS === */
@import url('https://fonts.googleapis.com/css2?family=Ma+Shan+Zheng&family=Noto+Serif+SC:wght@400;500;600;700&family=IBM+Plex+Mono:wght@400;500&family=Press+Start+2P&display=swap');

/* === VARIABLES === */
:root {
    --bg-deep:    #0d0b09;
    --bg-canvas:  #13110f;
    --card:       #1e1b17;
    --card-lit:   #27231e;
    --side-bg:    #100e0c;
    --text:       #e8e0d4;
    --text-soft:  #b0a898;
    --text-dim:   #6e6860;
    --gold:       #d4a84b;
    --gold-lit:   #e8c46c;
    --gold-dim:   rgba(212, 168, 75, 0.1);
    --pix-green:  #5fa36b;
    --pix-blue:   #5896b8;
    --pix-red:    #c86058;
    --pix-purple: #8b6fb0;
    --border:     #2e2a24;
    --border-lit: #3e3830;
    --grid-color: rgba(255,255,255,0.018);
    --radius:     4px;
    --radius-lg:  8px;
    --ease:       180ms ease;
}

/* === GLOBAL — 网格画布背景 === */
.stApp {
    background: var(--bg-deep);
    background-image:
        linear-gradient(var(--grid-color) 1px, transparent 1px),
        linear-gradient(90deg, var(--grid-color) 1px, transparent 1px),
        radial-gradient(ellipse at 50% 0%, rgba(212,168,75,0.05) 0%, transparent 60%),
        radial-gradient(ellipse at 85% 90%, rgba(88,150,184,0.03) 0%, transparent 50%);
    background-size: 24px 24px, 24px 24px, 100% 100%, 100% 100%;
}

#MainMenu, footer { visibility: hidden; }
[data-testid="stHeader"] { background: transparent; }
[data-testid="stToolbar"] { right: 0.5rem; }
.main .block-container { padding-top: 1rem; padding-bottom: 2rem; max-width: 1100px; }

/* === SCROLLBAR === */
::-webkit-scrollbar { width: 5px; height: 5px; }
::-webkit-scrollbar-track { background: var(--bg-deep); }
::-webkit-scrollbar-thumb { background: var(--border-lit); border-radius: 2px; }
::-webkit-scrollbar-thumb:hover { background: #524c44; }

/* ============================================
   SIDEBAR — 暗黑装备栏
   ============================================ */
[data-testid="stSidebar"] {
    background: linear-gradient(170deg, #14110e 0%, #0f0d0b 100%);
    border-right: 1px solid var(--border);
}
[data-testid="stSidebar"] .block-container { padding: 1.8rem 1.2rem; }
[data-testid="stSidebar"] h1, [data-testid="stSidebar"] h2, [data-testid="stSidebar"] h3 {
    font-family: 'Press Start 2P', 'Noto Serif SC', monospace;
    font-size: 0.7rem;
    color: var(--gold);
    text-transform: uppercase;
    letter-spacing: 0.04em;
}
[data-testid="stSidebar"] label {
    font-family: 'Noto Serif SC', 'Press Start 2P', sans-serif;
    font-size: 0.72rem;
    font-weight: 600;
    color: var(--text-soft);
    text-transform: uppercase;
    letter-spacing: 0.04em;
    line-height: 1.5;
    padding-bottom: 2px;
}
/* selectbox — 白边 + 垂直居中 + 不裁切 */
.stSelectbox [data-baseweb="select"] {
    min-height: 52px !important;
    height: 52px !important;
    display: flex !important;
    align-items: center !important;
    overflow: visible !important;
    border: 1px solid #ffffff !important;
    border-radius: 8px !important;
    background: #171410 !important;
    box-shadow: none !important;
}
.stSelectbox [data-baseweb="select"] > div {
    min-height: 52px !important;
    height: 52px !important;
    display: flex !important;
    align-items: center !important;
    overflow: visible !important;
    border: 1px solid #ffffff !important;
    border-radius: 8px !important;
    background: #171410 !important;
    box-shadow: none !important;
}
.stSelectbox div[role="combobox"] {
    min-height: 52px !important;
    height: 52px !important;
    display: flex !important;
    align-items: center !important;
    padding-top: 0 !important;
    padding-bottom: 0 !important;
    line-height: 1.4 !important;
    border: none !important;
}
.stSelectbox div[role="combobox"] > div {
    border: none !important;
    background: transparent !important;
}
.stSelectbox input {
    line-height: 1.4 !important;
    padding-top: 0 !important;
    padding-bottom: 0 !important;
    border: none !important;
    color: #e8e0d4 !important;
}
.stSelectbox [data-baseweb="select"]:hover,
.stSelectbox [data-baseweb="select"] > div:hover {
    border-color: #ffffff !important;
    box-shadow: none !important;
}
.stSelectbox [data-baseweb="select"]:focus-within,
.stSelectbox [data-baseweb="select"] > div:focus-within {
    border-color: var(--gold) !important;
    box-shadow: 0 0 0 2px var(--gold-dim) !important;
}
.stSelectbox [data-baseweb="select"] span,
.stSelectbox [data-baseweb="select"] div {
    color: #e8e0d4 !important;
}
.stSelectbox svg {
    fill: #b0a898 !important;
    color: #b0a898 !important;
}

/* 侧边栏输入框 & selectbox 容器 */
[data-testid="stSidebar"] .stTextInput input,
[data-testid="stSidebar"] .stSelectbox > div > div {
    background: #1a1713;
    border: 2px solid var(--border);
    border-radius: var(--radius);
    color: var(--text);
    font-family: 'IBM Plex Mono', monospace;
    font-size: 0.82rem;
    line-height: 1.4;
    min-height: 52px;
    padding: 0 0.65rem;
    image-rendering: pixelated;
    display: flex;
    align-items: center;
}

/* 主内容区输入框 */
.stTextInput input,
.stTextArea textarea {
    line-height: 1.4 !important;
    padding-top: 12px !important;
    padding-bottom: 12px !important;
}

/* 下拉菜单修复 */
[data-testid="stSidebar"] .stSelectbox [data-baseweb="select"] [role="option"] div,
[data-testid="stSidebar"] .stSelectbox [data-baseweb="select"] [role="option"] span {
    color: #e8e0d4 !important;
    font-size: 0.82rem;
    line-height: 1.4;
}
div[data-baseweb="popover"],
div[data-baseweb="menu"] {
    background: #1e1b17 !important;
    border: 2px solid var(--border);
}
div[data-baseweb="menu"] li,
[role="listbox"] li,
[role="option"] {
    background: #1e1b17 !important;
    color: #e8e0d4 !important;
    font-family: 'IBM Plex Mono', monospace;
    font-size: 0.82rem;
    padding: 8px 12px;
}
div[data-baseweb="menu"] li:hover,
[role="listbox"] li:hover,
[role="option"]:hover {
    background: #27231e !important;
    color: #e8c46c !important;
}

/* 聚焦样式 */
[data-testid="stSidebar"] .stTextInput input:focus,
[data-testid="stSidebar"] .stSelectbox > div > div:focus-within {
    border-color: var(--gold);
    box-shadow: 0 0 0 3px var(--gold-dim), inset 0 0 0 1px rgba(212,168,75,0.1);
    outline: none;
}
[data-testid="stSidebar"] .stTextInput input::placeholder {
    color: #4a4540;
    font-style: italic;
}
[data-testid="stSidebar"] hr { border-color: var(--border); margin: 1rem 0; }

/* ============================================
   TYPOGRAPHY
   ============================================ */
h1, h2, h3 {
    font-family: 'Ma Shan Zheng', 'Noto Serif SC', serif;
    color: var(--text);
    font-weight: 400;
}
h1 { font-size: 2.6rem; letter-spacing: 0.05em; }
h2 { font-size: 1.55rem; border-bottom: none; }
h3 { font-size: 1.18rem; color: var(--gold-lit); }
p, li, span, div { font-family: 'Noto Serif SC', serif; color: var(--text-soft); }
code {
    font-family: 'IBM Plex Mono', monospace;
    background: rgba(212,168,75,0.08);
    color: var(--gold-lit);
    padding: 0.1em 0.4em;
    border-radius: 2px;
    font-size: 0.84em;
}
pre { background: var(--card); border: 1px solid var(--border); border-radius: var(--radius); padding: 1rem; }

/* ============================================
   BUTTONS — 像素边框按钮
   ============================================ */
.stButton > button {
    font-family: 'Press Start 2P', 'Noto Serif SC', monospace;
    font-size: 0.58rem;
    text-transform: uppercase;
    letter-spacing: 0.04em;
    border-radius: var(--radius);
    padding: 0.65rem 1.2rem;
    transition: all var(--ease);
    cursor: pointer;
    image-rendering: pixelated;
    position: relative;
}
.stButton > button[kind="primary"] {
    background: linear-gradient(180deg, #c8963e 0%, #a07828 100%);
    color: #1a1408;
    border: none;
    border-bottom: 3px solid #7a5c20;
    box-shadow: 0 2px 0 #7a5c20, 0 4px 12px rgba(200,150,62,0.2);
}
.stButton > button[kind="primary"]:hover {
    background: linear-gradient(180deg, #d4a84b 0%, #b88830 100%);
    transform: translateY(-1px);
    box-shadow: 0 2px 0 #7a5c20, 0 6px 20px rgba(200,150,62,0.3);
}
.stButton > button[kind="primary"]:active { transform: translateY(1px); box-shadow: 0 1px 0 #7a5c20; }

.stButton > button[kind="secondary"] {
    background: transparent;
    color: var(--gold-lit);
    border: 2px solid var(--gold);
}
.stButton > button[kind="secondary"]:hover {
    background: var(--gold-dim);
    border-color: var(--gold-lit);
}
.stButton > button:disabled { opacity: 0.25; cursor: not-allowed; }
[data-testid="stSidebar"] .stButton > button[kind="primary"] {
    font-size: 0.62rem;
    padding: 0.75rem 1.2rem;
}

/* ============================================
   INPUTS
   ============================================ */
.stTextInput input {
    background: #1a1713;
    border: 2px solid var(--border);
    border-radius: var(--radius);
    color: var(--text);
    font-family: 'Noto Serif SC', serif;
    padding: 0.5rem 0.65rem;
}
.stTextInput input:focus {
    border-color: var(--gold);
    box-shadow: 0 0 0 3px var(--gold-dim);
}
.stTextInput label, .stSelectbox label { color: var(--text-soft) !important; }

/* ============================================
   EXPANDERS — 像素边框面板
   ============================================ */
.streamlit-expanderHeader {
    font-family: 'Press Start 2P', monospace;
    font-size: 0.55rem;
    text-transform: uppercase;
    color: var(--gold) !important;
    background: var(--card);
    border: 2px solid var(--border);
    border-radius: var(--radius);
    padding: 0.75rem 1rem !important;
    letter-spacing: 0.06em;
    image-rendering: pixelated;
}
.streamlit-expanderHeader:hover {
    background: var(--card-lit);
    border-color: var(--gold);
}
.streamlit-expanderHeader svg { color: var(--gold); }
.streamlit-expanderContent {
    background: var(--card);
    border: 2px solid var(--border);
    border-top: none;
    border-radius: 0 0 var(--radius) var(--radius);
    padding: 1rem 1.2rem;
}
[data-testid="stExpander"] { margin-bottom: 0.5rem; }

/* ============================================
   ALERTS
   ============================================ */
div.stAlert[kind="success"] {
    background: rgba(95,163,107,0.06);
    border: 2px solid rgba(95,163,107,0.3);
    border-radius: var(--radius);
}
div.stAlert[kind="info"] {
    background: rgba(212,168,75,0.05);
    border: 2px solid rgba(212,168,75,0.2);
    border-radius: var(--radius);
}
div.stAlert[kind="error"] {
    background: rgba(200,96,88,0.06);
    border: 2px solid rgba(200,96,88,0.25);
    border-radius: var(--radius);
}

/* ============================================
   SPINNER
   ============================================ */
.stSpinner > div { border-color: var(--gold) transparent transparent transparent !important; }

/* ============================================
   DOWNLOAD — 像素边框
   ============================================ */
.stDownloadButton > button {
    font-family: 'Press Start 2P', monospace;
    font-size: 0.48rem;
    text-transform: uppercase;
    border-radius: var(--radius);
    background: transparent;
    color: var(--pix-green);
    border: 2px solid rgba(95,163,107,0.4);
    padding: 0.5rem 1rem;
    image-rendering: pixelated;
}
.stDownloadButton > button:hover {
    background: rgba(95,163,107,0.06);
    border-color: var(--pix-green);
}

/* ============================================
   TABS
   ============================================ */
.stTabs [data-baseweb="tab-list"] { border-bottom: 2px solid var(--border); background: transparent; gap: 0; }
.stTabs [data-baseweb="tab"] {
    font-family: 'Press Start 2P', monospace;
    font-size: 0.5rem;
    text-transform: uppercase;
    color: var(--text-dim);
    background: transparent;
    border: none;
    border-bottom: 3px solid transparent;
    padding: 0.55rem 0.9rem;
    margin-right: 0;
    image-rendering: pixelated;
}
.stTabs [data-baseweb="tab"]:hover { color: var(--text-soft); }
.stTabs [data-baseweb="tab"][aria-selected="true"] {
    color: var(--gold-lit);
    border-bottom-color: var(--gold);
}
.stTabs [data-baseweb="tab-panel"] { padding-top: 0.8rem; }

/* ============================================
   DIVIDER
   ============================================ */
hr { border: none; border-top: 2px solid var(--border); margin: 1.8rem 0; }

/* ============================================
   CUSTOM
   ============================================ */
.empty-state {
    text-align: center;
    padding: 3rem 2rem;
    background: var(--card);
    border: 2px dashed var(--border);
    border-radius: var(--radius-lg);
}

/* ============================================
   PIXEL CORNER DECORATIONS
   ============================================ */
.pixel-card {
    position: relative;
    background: linear-gradient(160deg, #1e1b17 0%, #181510 100%);
    border: 2px solid var(--border);
    border-radius: var(--radius-lg);
    padding: 1.4rem 1.6rem;
    box-shadow: 0 2px 12px rgba(0,0,0,.3);
    overflow: hidden;
}
.pixel-card::before {
    content: "";
    position: absolute;
    top: -2px; left: -2px;
    width: 12px; height: 12px;
    background: var(--gold);
    clip-path: polygon(0 0, 100% 0, 0 100%);
    opacity: 0.6;
    image-rendering: pixelated;
}
.pixel-card::after {
    content: "";
    position: absolute;
    bottom: -2px; right: -2px;
    width: 12px; height: 12px;
    background: var(--gold);
    clip-path: polygon(100% 100%, 0 100%, 100% 0);
    opacity: 0.6;
    image-rendering: pixelated;
}

/* ============================================
   PIXEL SPRITE — 小型像素图标（纯 CSS）
   ============================================ */
.sprite-diamond {
    display: inline-block;
    width: 8px; height: 8px;
    background: var(--gold-lit);
    clip-path: polygon(50% 0, 100% 50%, 50% 100%, 0 50%);
    image-rendering: pixelated;
}
.sprite-heart {
    display: inline-block;
    width: 10px; height: 10px;
    background: var(--pix-red);
    clip-path: polygon(50% 15%, 61% 5%, 80% 5%, 95% 20%, 95% 45%, 50% 90%, 5% 45%, 5% 20%, 20% 5%, 39% 5%);
    image-rendering: pixelated;
}

/* ============================================
   STAT-BAR — RPG 属性条
   ============================================ */
.stat-bar-bg {
    display: inline-block;
    width: 100%;
    height: 8px;
    background: #1a1713;
    border: 1px solid var(--border);
    border-radius: 0;
    image-rendering: pixelated;
    overflow: hidden;
}
.stat-bar-fill {
    height: 100%;
    image-rendering: pixelated;
}

/* ============================================
   KEYFRAMES
   ============================================ */
@keyframes fadeIn { from { opacity: 0; transform: translateY(8px); } to { opacity: 1; transform: translateY(0); } }
@keyframes pixelGlow {
    0%, 100% { box-shadow: 0 0 4px rgba(212,168,75,0.05); }
    50%      { box-shadow: 0 0 14px rgba(212,168,75,0.12); }
}
@keyframes scanline {
    0% { background-position: 0 0; }
    100% { background-position: 0 4px; }
}
.animate-in  { animation: fadeIn 0.4s ease forwards; }
.animate-glow { animation: pixelGlow 3s ease-in-out infinite; }
</style>
""", unsafe_allow_html=True)

# --- 初始化 Session State ---
DEFAULT_STATE = {
    "level_design": "",
    "review_result": "",
    "optimized_design": "",
    "current_record_id": None,
    "is_generating": False,
    "is_reviewing": False,
    "is_optimizing": False,
    "history_records": [],
}
for key, val in DEFAULT_STATE.items():
    if key not in st.session_state:
        st.session_state[key] = val

LEVEL_DEFAULTS = {
    "stealth": {
        "form_game_type": "2D 潜入",
        "form_scene": "中世纪城堡",
        "form_goal": "营救囚犯",
        "form_difficulty": "中等",
        "form_enemy_types": "巡逻兵、弓箭手、守卫队长",
        "form_core_mechanics": "敌人巡逻、钥匙开门、隐藏路线、警报系统",
        "form_art_style": "像素风、暗色调",
        "form_play_time": "3-5 分钟",
    },
    "platformer": {
        "form_game_type": "2D 平台跳跃",
        "form_scene": "森林遗迹",
        "form_goal": "到达终点",
        "form_difficulty": "中等",
        "form_enemy_types": "移动平台、尖刺陷阱、落石",
        "form_core_mechanics": "二段跳、冲刺、移动平台",
        "form_art_style": "像素风、明亮色调",
        "form_play_time": "2-4 分钟",
    },
    "puzzle": {
        "form_game_type": "2D 解谜",
        "form_scene": "古代神殿",
        "form_goal": "解开封印、打开密室",
        "form_difficulty": "中等",
        "form_enemy_types": "压力板、可移动方块、光束机关",
        "form_core_mechanics": "推箱子、钥匙开门、机关连锁",
        "form_art_style": "像素风、神秘色调",
        "form_play_time": "5-8 分钟",
    },
    "combat": {
        "form_game_type": "2D 动作战斗",
        "form_scene": "黑暗要塞",
        "form_goal": "击败守关 Boss",
        "form_difficulty": "中等",
        "form_enemy_types": "近战兵、远程射手、重装精英、Boss",
        "form_core_mechanics": "连击系统、闪避、技能释放",
        "form_art_style": "像素风、暗色调",
        "form_play_time": "3-5 分钟",
    },
    "exploration": {
        "form_game_type": "2D 探索冒险",
        "form_scene": "废弃古城",
        "form_goal": "探索古城、收集遗物",
        "form_difficulty": "中等",
        "form_enemy_types": "野生动物、石像守卫、环境陷阱",
        "form_core_mechanics": "地图解锁、能力获取、区域连接",
        "form_art_style": "像素风、暖色调",
        "form_play_time": "5-10 分钟",
    },
}

FORM_KEYS = [
    "form_game_type", "form_scene", "form_goal", "form_difficulty",
    "form_enemy_types", "form_core_mechanics", "form_art_style", "form_play_time",
]


def on_level_type_change():
    new_display = st.session_state.form_level_type
    new_key = {v: k for k, v in LEVEL_TYPES.items()}[new_display]
    defaults = LEVEL_DEFAULTS[new_key]
    for k, v in defaults.items():
        st.session_state[k] = v


if "form_level_type" not in st.session_state:
    st.session_state.form_level_type = list(LEVEL_TYPES.values())[0]
    on_level_type_change()


# --- 辅助函数 ---
def get_prompt_builder(level_type_key: str):
    return PROMPT_BUILDERS.get(level_type_key, build_stealth_prompt)


def get_enemy_label(level_type_key: str) -> str:
    labels = {
        "stealth": "敌人类型",
        "platformer": "障碍 / 陷阱类型",
        "puzzle": "机关 / 障碍类型",
        "combat": "敌人类型",
        "exploration": "敌人 / 障碍类型",
    }
    return labels.get(level_type_key, "敌人 / 障碍类型")


def get_enemy_placeholder(level_type_key: str) -> str:
    placeholders = {
        "stealth": "例如：巡逻兵、弓箭手、守卫队长",
        "platformer": "例如：移动平台、尖刺陷阱、落石",
        "puzzle": "例如：压力板、可移动方块、光束机关",
        "combat": "例如：近战兵、远程射手、精英敌人、Boss",
        "exploration": "例如：野生动物、古代守卫、环境陷阱",
    }
    return placeholders.get(level_type_key, "")


def get_mechanics_placeholder(level_type_key: str) -> str:
    placeholders = {
        "stealth": "例如：敌人巡逻、钥匙开门、隐藏路线、警报系统",
        "platformer": "例如：二段跳、冲刺、蹬墙跳",
        "puzzle": "例如：推箱子、钥匙开门、机关连锁",
        "combat": "例如：连击系统、闪避、技能释放",
        "exploration": "例如：地图解锁、能力获取、多区域连接",
    }
    return placeholders.get(level_type_key, "")


def get_goal_placeholder(level_type_key: str) -> str:
    placeholders = {
        "stealth": "例如：营救囚犯、偷取情报、暗杀目标",
        "platformer": "例如：到达终点、收集全部金币",
        "puzzle": "例如：解开封印、打开密室大门",
        "combat": "例如：击败所有敌人、击败 Boss",
        "exploration": "例如：探索古城、收集遗物、揭开秘密",
    }
    return placeholders.get(level_type_key, "")


def get_system_prompt_for_type(level_type_key: str) -> str:
    prompts = {
        "stealth": "你是一名资深 2D 潜入类游戏策划，擅长设计敌人巡逻路线、玩家潜入路线和风险收益平衡。请用专业策划文档的语言风格输出。",
        "platformer": "你是一名资深 2D 平台跳跃类游戏策划，擅长设计跳跃节奏、平台布局和难度曲线。请用专业策划文档的语言风格输出。",
        "puzzle": "你是一名资深 2D 解谜类游戏策划，擅长设计谜题逻辑、机关连锁和信息提示系统。请用专业策划文档的语言风格输出。",
        "combat": "你是一名资深 2D 动作战斗类游戏策划，擅长设计敌人组合、战斗节奏和补给平衡。请用专业策划文档的语言风格输出。",
        "exploration": "你是一名资深 2D 探索冒险类游戏策划，擅长设计区域连接、环境叙事和探索回报机制。请用专业策划文档的语言风格输出。",
    }
    return prompts.get(level_type_key, prompts["stealth"])


# --- Session 历史记录 ---
def history_save(level_type_key: str, user_input: dict, level_design: str) -> dict:
    record = {
        "id": datetime.now().strftime("%Y%m%d%H%M%S%f"),
        "created_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "level_type": level_type_key,
        "user_input": user_input,
        "level_design": level_design,
        "review_result": "",
        "optimized_design": "",
    }
    st.session_state.history_records.insert(0, record)
    if len(st.session_state.history_records) > 50:
        st.session_state.history_records = st.session_state.history_records[:50]
    return record


def history_update_review(record_id: str, review_result: str):
    for r in st.session_state.history_records:
        if r["id"] == record_id:
            r["review_result"] = review_result
            break


def history_update_optimized(record_id: str, optimized_design: str):
    for r in st.session_state.history_records:
        if r["id"] == record_id:
            r["optimized_design"] = optimized_design
            break


# ================================================================
#  PAGE HEADER — 像素游戏标题
# ================================================================
st.markdown("""
<div style="text-align: center; padding: 0.8rem 0 1.6rem 0;">
    <div style="display: inline-flex; align-items: center; gap: 0.5rem; margin-bottom: 0.6rem;">
        <span style="font-family: 'Press Start 2P', monospace; font-size: 0.5rem; color: #6e6860; letter-spacing: 0.1em;">[ TOOL ]</span>
        <span style="font-family: 'Press Start 2P', monospace; font-size: 0.5rem; color: #b0a898; letter-spacing: 0.1em;">LEVEL DESIGN</span>
        <span style="font-family: 'Press Start 2P', monospace; font-size: 0.5rem; color: #6e6860; letter-spacing: 0.1em;">v1.0</span>
    </div>
    <h1 style="font-family: 'Ma Shan Zheng', 'Noto Serif SC', serif; font-size: 3.2rem; font-weight: 400; color: #e8e0d4; margin: 0; letter-spacing: 0.06em; line-height: 1.15;">
        AI 关卡设计助手
    </h1>
    <div style="display: inline-flex; align-items: center; gap: 1rem; margin-top: 0.5rem; padding: 0.3rem 0;">
        <svg width="24" height="4" viewBox="0 0 24 4"><rect x="0" y="0" width="4" height="4" fill="#d4a84b"/><rect x="6" y="0" width="4" height="4" fill="#3e3830"/><rect x="12" y="0" width="4" height="4" fill="#d4a84b"/><rect x="18" y="0" width="4" height="4" fill="#3e3830"/></svg>
        <span style="font-family: 'Press Start 2P', monospace; font-size: 0.46rem; color: #d4a84b; letter-spacing: 0.12em;">GENERATE &middot; REVIEW &middot; OPTIMIZE</span>
        <svg width="24" height="4" viewBox="0 0 24 4"><rect x="0" y="0" width="4" height="4" fill="#3e3830"/><rect x="6" y="0" width="4" height="4" fill="#d4a84b"/><rect x="12" y="0" width="4" height="4" fill="#3e3830"/><rect x="18" y="0" width="4" height="4" fill="#d4a84b"/></svg>
    </div>
</div>
""", unsafe_allow_html=True)

# 介绍 + RPG 数值卡
col_intro, col_stats = st.columns([3, 2])
with col_intro:
    st.markdown("""
    <div class="pixel-card">
        <div style="display: flex; align-items: center; gap: 0.4rem; margin-bottom: 0.8rem;">
            <span class="sprite-diamond"></span>
            <span style="font-family: 'Press Start 2P', monospace; font-size: 0.5rem; color: #d4a84b; text-transform: uppercase; letter-spacing: 0.08em;">Quest Log</span>
        </div>
        <p style="font-family: 'Noto Serif SC', serif; font-size: 0.92rem; color: #b0a898; line-height: 1.8; margin: 0;">
            面向<strong style="color: #e8e0d4;">游戏策划</strong>的 AI 辅助设计工具。
            输入关卡需求，AI 以专业策划文档格式，生成路线设计、敌人配置、
            奖励分布和体验节奏的完整方案。支持
            <strong style="color: #e8c46c;">5 种</strong> 2D 关卡类型。
        </p>
    </div>
    """, unsafe_allow_html=True)
with col_stats:
    # RPG 数值卡 — 像素风格属性面板
    st.markdown("""
    <div class="pixel-card" style="padding: 1.2rem 1.4rem;">
        <div style="display: flex; align-items: center; gap: 0.4rem; margin-bottom: 0.7rem;">
            <span class="sprite-diamond"></span>
            <span style="font-family: 'Press Start 2P', monospace; font-size: 0.5rem; color: #d4a84b; text-transform: uppercase; letter-spacing: 0.08em;">Stats</span>
        </div>
        <div style="display: flex; flex-direction: column; gap: 0.55rem;">
            <div>
                <div style="display: flex; justify-content: space-between; align-items: baseline; margin-bottom: 0.2rem;">
                    <span style="font-family: 'Press Start 2P', monospace; font-size: 0.45rem; color: #b0a898;">关卡类型</span>
                    <span style="font-family: 'IBM Plex Mono', monospace; font-size: 0.8rem; color: #e8c46c; font-weight: 600;">Lv.5</span>
                </div>
                <div class="stat-bar-bg"><div class="stat-bar-fill" style="width:100%; background: linear-gradient(90deg, #d4a84b, #e8c46c);"></div></div>
            </div>
            <div>
                <div style="display: flex; justify-content: space-between; align-items: baseline; margin-bottom: 0.2rem;">
                    <span style="font-family: 'Press Start 2P', monospace; font-size: 0.45rem; color: #b0a898;">分制评分</span>
                    <span style="font-family: 'IBM Plex Mono', monospace; font-size: 0.8rem; color: #e8c46c; font-weight: 600;">100/100</span>
                </div>
                <div class="stat-bar-bg"><div class="stat-bar-fill" style="width:100%; background: linear-gradient(90deg, #d4a84b, #e8c46c);"></div></div>
            </div>
            <div>
                <div style="display: flex; justify-content: space-between; align-items: baseline; margin-bottom: 0.2rem;">
                    <span style="font-family: 'Press Start 2P', monospace; font-size: 0.45rem; color: #b0a898;">AI Prompt</span>
                    <span style="font-family: 'IBM Plex Mono', monospace; font-size: 0.8rem; color: #5fa36b; font-weight: 600;">x8</span>
                </div>
                <div class="stat-bar-bg"><div class="stat-bar-fill" style="width:80%; background: linear-gradient(90deg, #5fa36b, #7ec48a);"></div></div>
            </div>
            <div>
                <div style="display: flex; justify-content: space-between; align-items: baseline; margin-bottom: 0.2rem;">
                    <span style="font-family: 'Press Start 2P', monospace; font-size: 0.45rem; color: #b0a898;">文档导出</span>
                    <span style="font-family: 'IBM Plex Mono', monospace; font-size: 0.8rem; color: #5896b8; font-weight: 600;">MD</span>
                </div>
                <div class="stat-bar-bg"><div class="stat-bar-fill" style="width:75%; background: linear-gradient(90deg, #5896b8, #7ab8d8);"></div></div>
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)

st.markdown("<hr>", unsafe_allow_html=True)

# --- 侧边栏 ---
with st.sidebar:
    st.markdown("""
    <div style="display: flex; align-items: center; gap: 0.4rem; margin-bottom: 1.2rem;">
        <span style="font-family: 'Press Start 2P', monospace; font-size: 0.55rem; color: #d4a84b; text-transform: uppercase; letter-spacing: 0.08em;">Level Config</span>
    </div>
    """, unsafe_allow_html=True)

    level_type_display = st.selectbox(
        "关卡类型",
        options=list(LEVEL_TYPES.values()),
        key="form_level_type",
        on_change=on_level_type_change,
        help="选择你要设计的关卡类型",
    )
    level_type_key = {v: k for k, v in LEVEL_TYPES.items()}[level_type_display]

    st.markdown("---")

    game_type = st.text_input("游戏类型", key="form_game_type")
    scene = st.text_input("关卡场景", key="form_scene")
    goal = st.text_input("玩家目标", key="form_goal", placeholder=get_goal_placeholder(level_type_key))
    difficulty = st.selectbox("关卡难度", options=["简单", "中等", "困难"], key="form_difficulty")
    enemy_types = st.text_input(get_enemy_label(level_type_key), key="form_enemy_types", placeholder=get_enemy_placeholder(level_type_key))
    core_mechanics = st.text_input("核心机制", key="form_core_mechanics", placeholder=get_mechanics_placeholder(level_type_key))
    art_style = st.text_input("美术风格", key="form_art_style")
    play_time = st.text_input("预计游玩时长", key="form_play_time")

    st.markdown("---")

    btn_generate = st.button(
        "[ 生成关卡方案 ]",
        type="primary",
        use_container_width=True,
        disabled=st.session_state.is_generating,
    )


# --- 主内容区 ---
if btn_generate:
    st.session_state.is_generating = True
    st.session_state.level_design = ""
    st.session_state.review_result = ""
    st.session_state.optimized_design = ""
    st.session_state.current_record_id = None
    st.rerun()

if st.session_state.is_generating:
    try:
        user_input = {
            "game_type": game_type,
            "scene": scene,
            "goal": goal,
            "difficulty": difficulty,
            "enemy_types": enemy_types,
            "core_mechanics": core_mechanics,
            "art_style": art_style,
            "play_time": play_time,
        }
        system_prompt = get_system_prompt_for_type(level_type_key)
        user_prompt = get_prompt_builder(level_type_key)(user_input)

        with st.spinner("AI 正在生成关卡方案..."):
            chunks = []
            def stream_gen():
                for chunk in call_ai_stream(system_prompt, user_prompt, temperature=0.7):
                    chunks.append(chunk)
                    yield chunk
            st.write_stream(stream_gen())

        full_text = "".join(chunks)
        st.session_state.level_design = full_text
        record = history_save(level_type_key, user_input, full_text)
        st.session_state.current_record_id = record["id"]
        st.success("关卡方案生成完成！")
        st.session_state.is_generating = False
        st.session_state.is_reviewing = True
        st.rerun()

    except ValueError as e:
        st.error(f"配置错误：{e}")
        st.info("请在项目根目录创建 `.env` 文件并配置 `DEEPSEEK_API_KEY`，参考 `.env.example`")
        st.session_state.is_generating = False
    except RuntimeError as e:
        st.error(f"API 调用失败：{e}")
        st.session_state.is_generating = False

if st.session_state.is_reviewing and st.session_state.level_design:
    try:
        review_prompt = build_review_prompt(level_type_key, st.session_state.level_design)
        system_review = "你是一位资深游戏关卡评审专家，专门评审 2D 游戏关卡设计方案。请给出严厉但建设性的评审意见。"

        with st.spinner("正在评审关卡方案..."):
            chunks = []
            def stream_gen():
                for chunk in call_ai_stream(system_review, review_prompt, temperature=0.3):
                    chunks.append(chunk)
                    yield chunk
            st.write_stream(stream_gen())

        full_text = "".join(chunks)
        st.session_state.review_result = full_text
        if st.session_state.current_record_id:
            history_update_review(st.session_state.current_record_id, full_text)
        st.success("评审完成！")
    except RuntimeError as e:
        st.error(f"评审失败：{e}")
        st.session_state.review_result = "（评审生成失败，请稍后重试）"
    finally:
        st.session_state.is_reviewing = False
        st.rerun()

if st.session_state.level_design:
    st.markdown("<hr>", unsafe_allow_html=True)
    st.markdown("""
    <div style="display: flex; align-items: center; gap: 0.5rem; margin-bottom: 0.3rem;">
        <span class="sprite-diamond"></span>
        <span style="font-family: 'Press Start 2P', monospace; font-size: 0.5rem; color: #d4a84b; text-transform: uppercase; letter-spacing: 0.08em;">Design Document</span>
    </div>
    """, unsafe_allow_html=True)
    with st.expander("VIEW  >>  查看完整关卡方案", expanded=True):
        st.markdown(st.session_state.level_design)

if st.session_state.review_result:
    st.markdown("<hr>", unsafe_allow_html=True)
    st.markdown("""
    <div style="display: flex; align-items: center; gap: 0.5rem; margin-bottom: 0.3rem;">
        <span style="display: inline-block; width: 8px; height: 8px; background: #5fa36b; clip-path: polygon(50% 0, 100% 50%, 50% 100%, 0 50%); image-rendering: pixelated;"></span>
        <span style="font-family: 'Press Start 2P', monospace; font-size: 0.5rem; color: #5fa36b; text-transform: uppercase; letter-spacing: 0.08em;">Review Report</span>
    </div>
    """, unsafe_allow_html=True)
    with st.expander("VIEW  >>  查看详细评审", expanded=True):
        st.markdown(st.session_state.review_result)

    st.markdown("---")
    col_opt, col_export = st.columns([1, 1])
    with col_opt:
        st.button(
            "[ 一键优化关卡方案 ]",
            type="secondary",
            use_container_width=True,
            disabled=st.session_state.is_optimizing,
            key="btn_optimize",
        )
    with col_export:
        if st.session_state.level_design:
            user_input = {
                "game_type": game_type, "scene": scene, "goal": goal,
                "difficulty": difficulty, "enemy_types": enemy_types,
                "core_mechanics": core_mechanics, "art_style": art_style,
                "play_time": play_time,
            }
            markdown_content = export_to_markdown(
                level_type_key, user_input,
                st.session_state.level_design, st.session_state.review_result,
                st.session_state.optimized_design,
            )
            st.download_button(
                label="[ 导出 Markdown ]",
                data=markdown_content,
                file_name=f"AI关卡设计方案_{level_type_key}.md",
                mime="text/markdown",
                use_container_width=True,
            )

if st.session_state.is_optimizing:
    try:
        optimize_prompt = build_optimize_prompt(
            level_type_key, st.session_state.level_design, st.session_state.review_result,
        )
        system_optimize = "你是一名资深游戏关卡策划，专门优化改进关卡设计方案。请给出具体、可执行的优化方案。"

        with st.spinner("AI 正在优化关卡方案..."):
            chunks = []
            def stream_gen():
                for chunk in call_ai_stream(system_optimize, optimize_prompt, temperature=0.6):
                    chunks.append(chunk)
                    yield chunk
            st.write_stream(stream_gen())

        full_text = "".join(chunks)
        st.session_state.optimized_design = full_text
        if st.session_state.current_record_id:
            history_update_optimized(st.session_state.current_record_id, full_text)
        st.success("优化完成！")
    except RuntimeError as e:
        st.error(f"优化失败：{e}")
    finally:
        st.session_state.is_optimizing = False
        st.rerun()

if st.session_state.get("btn_optimize", False):
    st.session_state.is_optimizing = True
    st.session_state.btn_optimize = False
    st.rerun()

if st.session_state.optimized_design:
    st.markdown("<hr>", unsafe_allow_html=True)
    st.markdown("""
    <div style="display: flex; align-items: center; gap: 0.5rem; margin-bottom: 0.3rem;">
        <span class="sprite-diamond"></span>
        <span style="font-family: 'Press Start 2P', monospace; font-size: 0.5rem; color: #e8c46c; text-transform: uppercase; letter-spacing: 0.08em;">Optimized Design</span>
    </div>
    """, unsafe_allow_html=True)
    with st.expander("VIEW  >>  查看优化方案", expanded=True):
        st.markdown(st.session_state.optimized_design)

    user_input = {
        "game_type": game_type, "scene": scene, "goal": goal,
        "difficulty": difficulty, "enemy_types": enemy_types,
        "core_mechanics": core_mechanics, "art_style": art_style,
        "play_time": play_time,
    }
    markdown_content_v2 = export_to_markdown(
        level_type_key, user_input,
        st.session_state.level_design, st.session_state.review_result,
        st.session_state.optimized_design,
    )
    st.download_button(
        label="[ 下载优化版 Markdown ]",
        data=markdown_content_v2,
        file_name=f"AI关卡设计方案_{level_type_key}_优化版.md",
        mime="text/markdown",
    )

# ================================================================
#  历史记录
# ================================================================
st.markdown("<hr>", unsafe_allow_html=True)
st.markdown("""
<div style="display: flex; align-items: center; gap: 0.5rem; margin-bottom: 0.3rem;">
    <span class="sprite-diamond"></span>
    <span style="font-family: 'Press Start 2P', monospace; font-size: 0.5rem; color: #d4a84b; text-transform: uppercase; letter-spacing: 0.08em;">History</span>
</div>
""", unsafe_allow_html=True)

records = st.session_state.history_records
if not records:
    st.markdown("""
    <div class="empty-state">
        <p style="font-family: 'Press Start 2P', monospace; font-size: 0.5rem; color: #6e6860; text-transform: uppercase; letter-spacing: 0.08em; margin: 0;">No Records</p>
        <p style="color: #4a4540; font-size: .83rem; margin-top: .4rem;">在左侧配置参数后点击生成按钮开始使用</p>
    </div>
    """, unsafe_allow_html=True)
else:
    st.markdown(f"""
    <span style="font-family: 'Press Start 2P', monospace; font-size: 0.48rem; color: #6e6860; letter-spacing: 0.06em;">
        [ {len(records)} / 50 ] RECORDS
    </span>
    """, unsafe_allow_html=True)

    for record in records:
        type_name = LEVEL_TYPES.get(record.get("level_type", ""), "未知类型")
        created = record.get("created_at", "")
        goal_text = record.get("user_input", {}).get("goal", "")

        with st.expander(f"[ {type_name} ] {goal_text}  --  {created}"):
            col1, col2 = st.columns([3, 1])
            with col1:
                st.markdown(f"**关卡类型**：{type_name}")
                st.markdown(f"**创建时间**：{created}")
                if record.get("user_input"):
                    ui = record["user_input"]
                    st.markdown(f"**场景**：{ui.get('scene', '--')} | **难度**：{ui.get('difficulty', '--')} | **时长**：{ui.get('play_time', '--')}")
                    st.markdown(f"**敌人/障碍**：{ui.get('enemy_types', '--')}")
                    st.markdown(f"**核心机制**：{ui.get('core_mechanics', '--')}")
            with col2:
                if record.get("level_design"):
                    md_content = export_to_markdown(
                        record.get("level_type", ""),
                        record.get("user_input", {}),
                        record.get("level_design", ""),
                        record.get("review_result", ""),
                        record.get("optimized_design", ""),
                    )
                    st.download_button(
                        label="[ 导出 ]",
                        data=md_content,
                        file_name=f"AI关卡设计_{record['id']}.md",
                        mime="text/markdown",
                        key=f"export_{record['id']}",
                    )

            if record.get("level_design"):
                tab1, tab2, tab3 = st.tabs([
                    "[ 关卡方案 ]", "[ 评审结果 ]", "[ 优化方案 ]"
                ])
                with tab1:
                    st.markdown(record["level_design"])
                with tab2:
                    if record.get("review_result"):
                        st.markdown(record["review_result"])
                    else:
                        st.info("暂无评审结果")
                with tab3:
                    if record.get("optimized_design"):
                        st.markdown(record["optimized_design"])
                    else:
                        st.info("暂无优化方案")

# ================================================================
#  FOOTER
# ================================================================
st.markdown("<hr>", unsafe_allow_html=True)
st.markdown("""
<div style="text-align: center; padding: .5rem 0 .2rem 0;">
    <span style="font-family: 'Press Start 2P', monospace; font-size: 0.42rem; color: #4a4540; letter-spacing: 0.08em;">
        AI Level Design Tool &middot; DeepSeek + Streamlit
    </span>
</div>
""", unsafe_allow_html=True)
