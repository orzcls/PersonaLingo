"""
Token 管理器
参考 Claude Code 的 autoCompact 机制
- 计数 token 使用量
- 阈值预警
- 自动压缩历史对话
"""
from typing import Optional
from app.services.llm_adapter import get_llm


class TokenManager:
    """管理对话 token 预算"""
    
    # 默认阈值（基于 GPT-4o 的 128K 上下文）
    MAX_CONTEXT = 128000
    WARN_THRESHOLD = 100000       # 78% - 发出警告
    COMPACT_THRESHOLD = 115000    # 90% - 自动压缩
    BLOCK_THRESHOLD = 125000      # 98% - 阻止新消息
    
    def __init__(self, max_context: int = None):
        if max_context:
            self.MAX_CONTEXT = max_context
            self.WARN_THRESHOLD = int(max_context * 0.78)
            self.COMPACT_THRESHOLD = int(max_context * 0.90)
            self.BLOCK_THRESHOLD = int(max_context * 0.98)
    
    def count_tokens(self, messages: list[dict]) -> int:
        """
        估算消息列表的 token 数
        使用简单的字符数/3 估算（避免依赖 tiktoken 在所有环境都可用）
        """
        total = 0
        for msg in messages:
            content = msg.get("content", "")
            # 粗略估计：英文约4字符/token，中文约2字符/token
            # 取一个保守的平均值
            total += len(content) // 3 + 4  # +4 for role/formatting overhead
        return total
    
    def check_status(self, messages: list[dict]) -> dict:
        """
        检查当前 token 状态
        返回: {"count": int, "status": "ok"|"warning"|"critical"|"blocked", "usage_pct": float}
        """
        count = self.count_tokens(messages)
        usage_pct = count / self.MAX_CONTEXT
        
        if count >= self.BLOCK_THRESHOLD:
            status = "blocked"
        elif count >= self.COMPACT_THRESHOLD:
            status = "critical"
        elif count >= self.WARN_THRESHOLD:
            status = "warning"
        else:
            status = "ok"
        
        return {
            "count": count,
            "max": self.MAX_CONTEXT,
            "status": status,
            "usage_pct": round(usage_pct * 100, 1)
        }
    
    async def compact_if_needed(self, messages: list[dict]) -> tuple[list[dict], bool]:
        """
        检查并在需要时压缩历史
        返回: (可能压缩后的messages, 是否进行了压缩)
        """
        status = self.check_status(messages)
        
        if status["status"] in ("critical", "blocked"):
            compacted = await self.compress_history(messages)
            return compacted, True
        
        return messages, False
    
    async def compress_history(self, messages: list[dict], keep_recent: int = 10) -> list[dict]:
        """
        压缩历史消息
        策略：保留最近 N 条 + 将更早的内容摘要为一条 system 消息
        """
        if len(messages) <= keep_recent:
            return messages
        
        # 分割：旧消息 vs 最近消息
        older = messages[:-keep_recent]
        recent = messages[-keep_recent:]
        
        # 找到原始 system 消息（如果有）
        system_msg = None
        non_system_older = []
        for msg in older:
            if msg["role"] == "system":
                system_msg = msg
            else:
                non_system_older.append(msg)
        
        # 生成摘要
        if non_system_older:
            summary = self._quick_summary(non_system_older)
        else:
            summary = ""
        
        # 重建消息列表
        result = []
        if system_msg:
            result.append(system_msg)
        
        if summary:
            result.append({
                "role": "system",
                "content": f"[Earlier conversation summary]: {summary}"
            })
        
        result.extend(recent)
        return result
    
    def _quick_summary(self, messages: list[dict]) -> str:
        """快速本地摘要（不调用LLM，基于规则提取关键内容）"""
        key_points = []
        for msg in messages:
            content = msg.get("content", "")
            role = msg.get("role", "")
            # 提取前100字符作为要点
            if len(content) > 100:
                key_points.append(f"{role}: {content[:100]}...")
            else:
                key_points.append(f"{role}: {content}")
        
        # 限制总长度
        summary_parts = key_points[-5:]  # 保留最后5条的摘要
        return " | ".join(summary_parts)


# 全局单例
_token_manager = None

def get_token_manager() -> TokenManager:
    global _token_manager
    if _token_manager is None:
        _token_manager = TokenManager()
    return _token_manager
