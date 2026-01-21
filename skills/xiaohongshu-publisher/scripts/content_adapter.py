#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
小红书内容适配器
将微信公众号内容转换为小红书格式
"""

import re
import html
from typing import Dict, List, Tuple


class XiaohongshuContentAdapter:
    """小红书内容适配器"""

    # 小红书限制
    MAX_TITLE_CHARS = 20
    MAX_CONTENT_CHARS = 800  # 包含emoji
    SAFE_CONTENT_CHARS = 700  # 留出emoji空间

    def __init__(self):
        """初始化适配器"""
        self.emoji_list = [
            "🔥", "💡", "✅", "⚡", "🚀", "💪", "🎯", "📌", "✨", "💎",
            "🌟", "👍", "🤔", "😎", "🔧", "📊", "📈", "💻", "🎨", "🔮"
        ]

    def adapt_title(self, title: str) -> str:
        """
        适配标题到小红书格式（最多20字）

        Args:
            title: 原始标题

        Returns:
            适配后的标题
        """
        # 去除HTML标签
        title = re.sub(r'<[^>]+>', '', title)
        title = html.unescape(title)
        title = title.strip()

        # 截断到最大长度
        if len(title) > self.MAX_TITLE_CHARS:
            title = title[:self.MAX_TITLE_CHARS - 1] + "…"
            print(f"  ⚠ 标题超长，已截断到 {self.MAX_TITLE_CHARS} 字")

        return title

    def extract_key_points(self, content: str) -> List[str]:
        """
        从内容中提取关键要点

        Args:
            content: HTML内容

        Returns:
            关键要点列表
        """
        # 去除HTML标签
        text = re.sub(r'<[^>]+>', ' ', content)
        text = html.unescape(text)
        text = re.sub(r'\s+', ' ', text).strip()

        # 按句子分割
        sentences = re.split(r'[。！？；\n]', text)
        sentences = [s.strip() for s in sentences if s.strip() and len(s.strip()) > 5]

        # 提取带数字、特殊标记的句子（通常是要点）
        key_points = []
        patterns = [
            r'^\d+[、.]\s*(.+)',  # "1. xxx"
            r'^[•·-]\s*(.+)',      # "• xxx"
            r'^（.*?）\s*(.+)',     # "（核心）xxx"
        ]

        for sent in sentences:
            matched = False
            for pattern in patterns:
                m = re.match(pattern, sent)
                if m:
                    point = m.group(1).strip()
                    if len(point) > 5:
                        key_points.append(point)
                        matched = True
                        break
            if not matched and len(key_points) < 3:
                # 如果要点不够，取一些较长的句子
                if len(sent) > 10 and len(sent) < 50:
                    key_points.append(sent)

        return key_points[:5]  # 最多5个要点

    def adapt_content(self, content: str, title: str = "") -> Dict[str, any]:
        """
        适配内容到小红书格式

        Args:
            content: HTML内容
            title: 标题

        Returns:
            包含适配后内容的字典
        """
        # 去除HTML标签
        text = re.sub(r'<[^>]+>', ' ', content)
        text = html.unescape(text)
        text = re.sub(r'\s+', ' ', text).strip()

        # 提取关键要点
        key_points = self.extract_key_points(content)

        # 构建小红书风格内容
        xhs_content_parts = []

        # 1. 引入句（如果有标题的话）
        if title:
            xhs_content_parts.append(f"{title}\n")

        # 2. 核心要点（带emoji）
        if key_points:
            xhs_content_parts.append("核心亮点：")
            for i, point in enumerate(key_points[:4], 1):
                emoji = self.emoji_list[i % len(self.emoji_list)]
                # 压缩要点长度
                if len(point) > 30:
                    point = point[:28] + ".."
                xhs_content_parts.append(f"{emoji} {point}")

        # 3. 总结/行动建议
        xhs_content_parts.append("\n💬 怎么样？你觉得这个如何？")

        # 合并内容
        xhs_content = "\n".join(xhs_content_parts)

        # 检查长度
        total_chars = len(xhs_content)
        if total_chars > self.MAX_CONTENT_CHARS:
            # 需要压缩
            print(f"  ⚠ 内容过长 ({total_chars} 字)，正在压缩...")
            xhs_content = self._compress_content(xhs_content)
            print(f"  ✓ 压缩后: {len(xhs_content)} 字")
        else:
            print(f"  ✓ 内容长度: {len(xhs_content)} 字")

        return {
            "content": xhs_content,
            "original_length": len(text),
            "adapted_length": len(xhs_content),
            "key_points": key_points
        }

    def _compress_content(self, content: str) -> str:
        """
        压缩内容到安全长度

        Args:
            content: 内容

        Returns:
            压缩后的内容
        """
        lines = content.split("\n")
        compressed = []

        for line in lines:
            if not line.strip():
                continue

            # 跳过一些不重要的行
            if any(keyword in line for keyword in ["💬 怎么样", "总结", "要点"]):
                if len("\n".join(compressed)) < self.SAFE_CONTENT_CHARS - 50:
                    compressed.append(line)
                continue

            # 截断长行
            if len(line) > 40:
                line = line[:38] + ".."

            # 检查总长度
            current_length = len("\n".join(compressed)) + len(line) + 1
            if current_length > self.SAFE_CONTENT_CHARS:
                break

            compressed.append(line)

        result = "\n".join(compressed)

        # 确保不超过最大长度
        if len(result) > self.MAX_CONTENT_CHARS:
            result = result[:self.MAX_CONTENT_CHARS - 1] + "…"

        return result

    def generate_tags(self, title: str, content: str) -> List[str]:
        """
        根据内容生成话题标签

        Args:
            title: 标题
            content: 内容

        Returns:
            标签列表
        """
        # 常见AI/技术相关标签
        common_tags = {
            "AI": ["#AI", "#人工智能", "#AIGC"],
            "模型": ["#大模型", "#AI模型", "#LLM"],
            "工具": ["#AI工具", "#效率工具", "#生产力工具"],
            "编程": ["#编程", "#代码", "#开发者"],
            "ChatGPT": ["#ChatGPT", "#OpenAI"],
            "Claude": ["#Claude", "#Anthropic"],
            "GPT": ["#GPT", "#OpenAI"],
            "Python": ["#Python", "#编程"],
            "数据": ["#数据分析", "#大数据"],
            "学习": ["#学习", "#知识分享"],
            "科技": ["#科技", "#黑科技"],
            "教程": ["#教程", "#入门教程"],
        }

        text = (title + " " + content).lower()
        found_tags = []

        # 匹配关键词
        for keyword, tags in common_tags.items():
            if keyword.lower() in text:
                found_tags.extend(tags)
                if len(found_tags) >= 5:
                    break

        # 默认标签
        if not found_tags:
            found_tags = ["#AI", "#科技"]

        return found_tags[:5]  # 最多5个标签


def main():
    """测试函数"""
    adapter = XiaohongshuContentAdapter()

    # 测试标题
    long_title = "OpenAI发布全新o4模型：推理能力提升3倍，数学准确率达到94.5%"
    print("原标题:", long_title)
    print("适配后:", adapter.adapt_title(long_title))
    print()

    # 测试内容
    test_content = """
    <h1>OpenAI o4模型重磅发布</h1>
    <p>OpenAI今日正式发布了备受期待的o4模型，该模型在推理能力上实现了重大突破。</p>
    <p>经过多项基准测试，o4在数学问题解决上准确率达到94.5%，相比o3提升45%。</p>
    <p>核心亮点：</p>
    <ul>
    <li>数学准确率94.5%，提升45%</li>
    <li>编程效率提升3倍</li>
    <li>支持更长上下文（128K→200K）</li>
    </ul>
    """

    result = adapter.adapt_content(test_content, "OpenAI o4发布")
    print("适配后内容:")
    print(result["content"])
    print()
    print("标签:", adapter.generate_tags("OpenAI o4发布", test_content))


if __name__ == "__main__":
    main()
