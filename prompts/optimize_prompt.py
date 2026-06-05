"""
关卡优化 Prompt —— 根据评审结果优化原方案
"""

from prompts.base_prompt import BASE_LEVEL_STRUCTURE


def build_optimize_prompt(level_type: str, original_design: str, review_result: str) -> str:
    """根据原方案和评审结果构建优化 Prompt"""

    level_type_names = {
        "stealth": "2D 潜入关卡",
        "platformer": "2D 平台跳跃关卡",
        "puzzle": "2D 解谜关卡",
        "combat": "2D 动作战斗关卡",
        "exploration": "2D 探索冒险关卡",
    }
    type_name = level_type_names.get(level_type, "2D 关卡")

    return f"""你是一名资深 {type_name} 策划，你的任务是优化一份已有的关卡设计方案。

## 原始关卡方案

{original_design}

## AI 评审结果

{review_result}

## 优化要求

请根据评审中指出的问题，生成一份优化后的完整关卡方案。优化时需要重点关注：

1. **针对每个评审问题的响应**：评审中指出的每个问题都必须有对应的改进。
2. **不降低原有优点**：原方案中评审认可的亮点要保留甚至强化。
3. **数据具体化**：把模糊的描述变成具体的数据（如敌人数量、巡逻范围、平台间距等）。
4. **可执行性**：优化后的方案应该更接近可直接实现的策划文档。

请按照以下结构输出：

## 一、优化后的关卡方案
（完整的关卡方案，结构与原方案一致）

{BASE_LEVEL_STRUCTURE}

## 二、修改说明
逐条说明你修改了哪些地方。

## 三、优化理由
逐条说明为什么这样优化，与评审意见的对应关系。

## 四、预期评分提升
预估优化后各维度分数能提升多少，给出优化前后的评分对比表格。

请直接输出完整内容，不要额外解释。"""
