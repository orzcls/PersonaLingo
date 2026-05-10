"""
统一 LLM 调用适配层
支持 OpenAI 和 Anthropic，通过 config.LLM_PROVIDER 切换
"""
from typing import AsyncGenerator, Optional
from app.config import get_settings


class LLMAdapter:
    """统一 LLM 调用接口

    注意：provider / api_key / base_url 在每次调用时动态从 settings 读取，
    以便 /api/settings 更新后即时生效；客户端按 (provider, api_key, base_url) 缓存。
    """

    def __init__(self, provider: Optional[str] = None):
        # 允许显式指定一个固定的 provider（例如测试场景）；None 表示跟随全局 settings
        self._forced_provider = provider
        # 按 (provider, api_key, base_url) 签名缓存客户端；配置变化时自动重建
        self._openai_client = None
        self._openai_sig = None
        self._anthropic_client = None
        self._anthropic_sig = None

    def _current_provider(self) -> str:
        if self._forced_provider:
            return self._forced_provider
        return get_settings().LLM_PROVIDER

    @property
    def provider(self) -> str:
        """向后兼容的 provider 属性（动态读取当前 provider）"""
        return self._current_provider()

    def _get_openai_client(self):
        from openai import AsyncOpenAI
        settings = get_settings()
        sig = (settings.OPENAI_API_KEY, settings.OPENAI_BASE_URL)
        if self._openai_client is None or self._openai_sig != sig:
            self._openai_client = AsyncOpenAI(
                api_key=settings.OPENAI_API_KEY,
                base_url=settings.OPENAI_BASE_URL
            )
            self._openai_sig = sig
        return self._openai_client

    def _get_anthropic_client(self):
        from anthropic import AsyncAnthropic
        settings = get_settings()
        base_url = (
            f"{settings.ANTHROPIC_BASE_URL.rstrip('/')}/v1"
            if settings.ANTHROPIC_BASE_URL and settings.ANTHROPIC_BASE_URL != "https://api.anthropic.com"
            else None
        )
        sig = (settings.ANTHROPIC_API_KEY, base_url)
        if self._anthropic_client is None or self._anthropic_sig != sig:
            self._anthropic_client = AsyncAnthropic(
                api_key=settings.ANTHROPIC_API_KEY,
                base_url=base_url
            )
            self._anthropic_sig = sig
        return self._anthropic_client

    async def chat(
        self,
        messages: list[dict],
        model: Optional[str] = None,
        temperature: float = 0.7,
        max_tokens: int = 4096
    ) -> str:
        """统一聊天接口，返回完整文本"""
        provider = self._current_provider()
        if provider == "openai":
            return await self._chat_openai(messages, model, temperature, max_tokens)
        elif provider == "anthropic":
            return await self._chat_anthropic(messages, model, temperature, max_tokens)
        else:
            raise ValueError(f"Unsupported provider: {provider}")

    async def chat_stream(
        self,
        messages: list[dict],
        model: Optional[str] = None,
        temperature: float = 0.7,
        max_tokens: int = 4096
    ) -> AsyncGenerator[str, None]:
        """统一流式聊天接口"""
        provider = self._current_provider()
        if provider == "openai":
            async for chunk in self._stream_openai(messages, model, temperature, max_tokens):
                yield chunk
        elif provider == "anthropic":
            async for chunk in self._stream_anthropic(messages, model, temperature, max_tokens):
                yield chunk
        else:
            raise ValueError(f"Unsupported provider: {provider}")

    async def _chat_openai(self, messages, model, temperature, max_tokens) -> str:
        client = self._get_openai_client()
        settings = get_settings()
        response = await client.chat.completions.create(
            model=model or settings.OPENAI_MODEL,
            messages=messages,
            temperature=temperature,
            max_tokens=max_tokens
        )
        return response.choices[0].message.content

    async def _chat_anthropic(self, messages, model, temperature, max_tokens) -> str:
        client = self._get_anthropic_client()
        settings = get_settings()
        # Anthropic 需要分离 system message
        system_msg = ""
        chat_messages = []
        for msg in messages:
            if msg["role"] == "system":
                system_msg = msg["content"]
            else:
                chat_messages.append(msg)

        response = await client.messages.create(
            model=model or settings.ANTHROPIC_MODEL,
            system=system_msg if system_msg else "You are a helpful assistant.",
            messages=chat_messages,
            temperature=temperature,
            max_tokens=max_tokens
        )
        return response.content[0].text

    async def _stream_openai(self, messages, model, temperature, max_tokens) -> AsyncGenerator[str, None]:
        client = self._get_openai_client()
        settings = get_settings()
        stream = await client.chat.completions.create(
            model=model or settings.OPENAI_MODEL,
            messages=messages,
            temperature=temperature,
            max_tokens=max_tokens,
            stream=True
        )
        async for chunk in stream:
            if chunk.choices[0].delta.content:
                yield chunk.choices[0].delta.content

    async def _stream_anthropic(self, messages, model, temperature, max_tokens) -> AsyncGenerator[str, None]:
        client = self._get_anthropic_client()
        settings = get_settings()
        system_msg = ""
        chat_messages = []
        for msg in messages:
            if msg["role"] == "system":
                system_msg = msg["content"]
            else:
                chat_messages.append(msg)

        async with client.messages.stream(
            model=model or settings.ANTHROPIC_MODEL,
            system=system_msg if system_msg else "You are a helpful assistant.",
            messages=chat_messages,
            temperature=temperature,
            max_tokens=max_tokens
        ) as stream:
            async for text in stream.text_stream:
                yield text

    def get_available_providers(self) -> list[dict]:
        """获取可用的LLM提供商列表"""
        settings = get_settings()
        providers = []
        if settings.OPENAI_API_KEY:
            providers.append({
                "id": "openai",
                "name": "OpenAI",
                "model": settings.OPENAI_MODEL,
                "available": True
            })
        if settings.ANTHROPIC_API_KEY:
            providers.append({
                "id": "anthropic",
                "name": "Anthropic",
                "model": settings.ANTHROPIC_MODEL,
                "available": True
            })
        return providers


def get_llm(provider: Optional[str] = None) -> LLMAdapter:
    """获取 LLM 适配器实例"""
    return LLMAdapter(provider=provider)
