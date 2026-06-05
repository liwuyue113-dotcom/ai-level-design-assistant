"""
DeepSeek API 客户端 —— 使用 OpenAI 兼容接口
"""

import httpx
from openai import OpenAI
from config import DEEPSEEK_API_KEY, DEEPSEEK_BASE_URL, DEEPSEEK_MODEL


def get_client():
    """
    创建 DeepSeek API 客户端（OpenAI 兼容模式）

    使用 httpx.Client 并禁用代理，避免梯子/VPN 导致连接失败。
    DeepSeek 是国内服务，不需要走代理。
    """
    if not DEEPSEEK_API_KEY:
        return None
    http_client = httpx.Client(proxy=None, timeout=httpx.Timeout(120.0, connect=30.0))
    return OpenAI(
        api_key=DEEPSEEK_API_KEY,
        base_url=DEEPSEEK_BASE_URL,
        http_client=http_client,
    )


def call_ai_stream(system_prompt: str, user_prompt: str, temperature: float = 0.7):
    """
    流式调用 DeepSeek API，逐块返回生成内容

    参数:
        system_prompt: 系统提示词
        user_prompt: 用户提示词
        temperature: 温度参数（0-2）

    Yields:
        str: 逐块文本内容

    异常:
        ValueError: API Key 未配置
        RuntimeError: API 调用失败
    """
    client = get_client()
    if client is None:
        raise ValueError("DeepSeek API Key 未配置，请在 .env 文件中设置 DEEPSEEK_API_KEY")

    try:
        stream = client.chat.completions.create(
            model=DEEPSEEK_MODEL,
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt},
            ],
            temperature=temperature,
            max_tokens=8192,
            stream=True,
        )
        for chunk in stream:
            if chunk.choices[0].delta.content:
                yield chunk.choices[0].delta.content
    except Exception as e:
        raise RuntimeError(f"DeepSeek API 调用失败: {str(e)}")


def call_ai(system_prompt: str, user_prompt: str, temperature: float = 0.7) -> str:
    """
    调用 DeepSeek API 生成内容

    参数:
        system_prompt: 系统提示词
        user_prompt: 用户提示词
        temperature: 温度参数（0-2），控制输出随机性

    返回:
        AI 生成的文本内容

    异常:
        ValueError: API Key 未配置
        RuntimeError: API 调用失败
    """
    client = get_client()
    if client is None:
        raise ValueError("DeepSeek API Key 未配置，请在 .env 文件中设置 DEEPSEEK_API_KEY")

    try:
        response = client.chat.completions.create(
            model=DEEPSEEK_MODEL,
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt},
            ],
            temperature=temperature,
            max_tokens=8192,
        )
        return response.choices[0].message.content
    except Exception as e:
        raise RuntimeError(f"DeepSeek API 调用失败: {str(e)}")
