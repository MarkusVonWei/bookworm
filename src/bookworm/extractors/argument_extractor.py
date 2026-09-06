import json
import logging
from typing import List, Optional
from dataclasses import dataclass

from ..utils import get_llm_client

logger = logging.getLogger("bookworm")


@dataclass
class Argument:
    """观点/论点数据类"""
    claim: str  # 主张
    premises: List[str]  # 前提/论据
    conclusion: str  # 结论
    strength: float  # 论证强度 (0-1)
    context: str  # 上下文
    supporting_evidence: List[str]  # 支持证据


class ArgumentExtractor:
    """核心观点提取器"""

    def __init__(self, llm=None):
        self.llm = llm or get_llm_client()
        self.extraction_prompt = """
        你是一个专业的书籍分析专家。请从以下文本中提取作者的核心观点和论证结构。

        要求：
        1. 识别作者的主要论点（claim）
        2. 找出支撑这些论点的前提和论据（premises）
        3. 提取论证的结论（conclusion）
        4. 评估论证的强度（0-1之间）
        5. 记录相关的支持证据

        文本内容：
        {text}

        请以JSON格式返回结果，格式如下：
        {{
            "arguments": [
                {{
                    "claim": "作者的主要主张",
                    "premises": ["前提1", "前提2"],
                    "conclusion": "论证结论",
                    "strength": 0.8,
                    "context": "论证的上下文",
                    "supporting_evidence": ["证据1", "证据2"]
                }}
            ]
        }}

        只返回JSON，不要有其他内容。
        """

    def extract(self, text: str, max_arguments: int = 10) -> List[Argument]:
        """从文本中提取核心观点"""
        # 如果文本太长，分块处理
        if len(text) > 4000:
            return self._extract_from_long_text(text, max_arguments)
        
        prompt = self.extraction_prompt.format(text=text)
        
        try:
            logger.debug(f"开始观点提取, 文本长度: {len(text)}")
            response = self.llm.complete(prompt)
            result = json.loads(response.text)
            
            arguments = []
            for item in result.get("arguments", [])[:max_arguments]:
                arguments.append(Argument(
                    claim=item["claim"],
                    premises=item.get("premises", []),
                    conclusion=item.get("conclusion", ""),
                    strength=item.get("strength", 0.5),
                    context=item.get("context", ""),
                    supporting_evidence=item.get("supporting_evidence", [])
                ))
            
            logger.info(f"观点提取成功, 提取到 {len(arguments)} 个观点")
            return arguments
        except Exception as e:
            logger.error(f"观点提取失败: {e}", exc_info=True)
            return []

    def _extract_from_long_text(self, text: str, max_arguments: int) -> List[Argument]:
        """从长文本中提取观点"""
        # 将文本分成多个块
        chunk_size = 3000
        chunks = [text[i:i+chunk_size] for i in range(0, len(text), chunk_size)]
        
        all_arguments = []
        seen_claims = set()
        
        for chunk in chunks:
            arguments = self.extract(chunk, max_arguments=max_arguments)
            for arg in arguments:
                if arg.claim not in seen_claims:
                    all_arguments.append(arg)
                    seen_claims.add(arg.claim)
        
        # 按强度排序
        all_arguments.sort(key=lambda x: x.strength, reverse=True)
        
        return all_arguments[:max_arguments]

    def extract_from_chapters(self, chapters: List[dict]) -> List[Argument]:
        """从多个章节中提取观点"""
        all_arguments = []
        seen_claims = set()
        
        for chapter in chapters:
            text = chapter.get("content", "")
            arguments = self.extract(text)
            
            for arg in arguments:
                if arg.claim not in seen_claims:
                    all_arguments.append(arg)
                    seen_claims.add(arg.claim)
        
        # 按强度排序
        all_arguments.sort(key=lambda x: x.strength, reverse=True)
        
        return all_arguments

    def analyze_argument_structure(self, argument: Argument) -> dict:
        """分析论证结构"""
        return {
            "claim": argument.claim,
            "premises_count": len(argument.premises),
            "evidence_count": len(argument.supporting_evidence),
            "strength": argument.strength,
            "has_conclusion": bool(argument.conclusion),
            "argument_type": self._classify_argument(argument)
        }

    def _classify_argument(self, argument: Argument) -> str:
        """分类论证类型"""
        # 简单的启发式分类
        if "因为" in argument.claim or "由于" in argument.claim:
            return "因果论证"
        elif "研究显示" in argument.context or "数据表明" in argument.context:
            return "实证论证"
        elif "逻辑上" in argument.context or "推理" in argument.context:
            return "逻辑论证"
        else:
            return "一般论证"
