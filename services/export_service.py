"""
Markdown 导出服务 —— 将关卡方案和评分导出为 Markdown 文档
"""

from config import LEVEL_TYPES


def export_to_markdown(
    level_type: str,
    user_input: dict,
    level_design: str,
    review_result: str = "",
    optimized_design: str = "",
) -> str:
    """
    生成完整的 Markdown 文档

    参数:
        level_type: 关卡类型 key（如 stealth, platformer）
        user_input: 用户输入参数字典
        level_design: AI 生成的关卡方案
        review_result: AI 评审结果
        optimized_design: 优化后的方案

    返回:
        Markdown 格式的文档内容
    """
    type_name = LEVEL_TYPES.get(level_type, "自定义关卡")

    md = f"""# AI 关卡设计方案

> 生成工具：AI 关卡设计助手
> 关卡类型：{type_name}

---

## 一、用户输入参数

| 参数 | 内容 |
|------|------|
| 游戏类型 | {user_input.get('game_type', '—')} |
| 关卡类型 | {type_name} |
| 关卡场景 | {user_input.get('scene', '—')} |
| 玩家目标 | {user_input.get('goal', '—')} |
| 关卡难度 | {user_input.get('difficulty', '—')} |
| 敌人/障碍类型 | {user_input.get('enemy_types', '—')} |
| 核心机制 | {user_input.get('core_mechanics', '—')} |
| 美术风格 | {user_input.get('art_style', '—')} |
| 预计游玩时长 | {user_input.get('play_time', '—')} |

---

## 二、关卡设计方案

{level_design}

---

"""
    if review_result:
        md += f"""## 三、AI 评审结果

{review_result}

---

"""

    if optimized_design:
        md += f"""## 四、优化方案

{optimized_design}

---

"""

    md += """## 附录

> 本文档由 AI 关卡设计助手自动生成。
> 项目定位：面向 2D 游戏的 AI 关卡设计辅助工具。
> 支持的关卡类型：2D 潜入、2D 平台跳跃、2D 解谜、2D 动作战斗、2D 探索冒险。
"""

    return md
