#!/usr/bin/env python3
"""
小红书内容改写脚本（优化版）
生成真正有用、接地气的小红书内容
核心原则：必须对读者有实际帮助，不能空洞无物
"""

import os
import re
import sys


class XiaohongshuAdapter:
    """小红书内容适配器（优化版）"""

    def __init__(self):
        self.max_length = 1000  # 小红书正文最大1000字

    def adapt(self, markdown_path, output_path=None):
        """
        将markdown文章改写为小红书风格

        Args:
            markdown_path: 原始markdown文件路径
            output_path: 输出文件路径（如果为None，自动生成）

        Returns:
            改写后的标题和内容
        """
        # 读取原文
        with open(markdown_path, 'r', encoding='utf-8') as f:
            content = f.read()

        # 提取核心信息
        tool_info = self._extract_tool_info(content)
        value_points = self._extract_value_points(content)
        how_to_use = self._extract_how_to_use(content)

        # 生成小红书标题（≤20字）
        xhs_title = self._generate_xhs_title(tool_info)

        # 生成小红书正文
        xhs_content = self._generate_xhs_content(tool_info, value_points, how_to_use)

        # 输出
        if output_path:
            with open(output_path, 'w', encoding='utf-8') as f:
                f.write(f"# {xhs_title}\n\n{xhs_content}")

        return xhs_title, xhs_content

    def _extract_tool_info(self, content):
        """提取工具核心信息"""
        lines = content.split('\n')

        # 提取标题（第一个#标题）
        title = ""
        for line in lines:
            if line.strip().startswith('# '):
                title = line.strip()[2:].strip()
                break

        # 提取工具名（从标题中）
        tool_name = self._extract_tool_name_from_title(title)

        # 识别文章类型
        article_type = self._identify_article_type(content)

        # 提取核心功能/特点
        core_feature = self._extract_core_feature(content)

        return {
            'name': tool_name,
            'type': article_type,
            'feature': core_feature,
            'title': title
        }

    def _extract_tool_name_from_title(self, title):
        """从标题中提取工具名"""
        # 常见分隔符
        for sep in ['：', ':', '｜', '|', '——', '-']:
            if sep in title:
                parts = title.split(sep)
                # 取第一部分，通常是工具名
                name = parts[0].strip()
                # 去除常见前缀
                prefixes = ['新工具', '推荐', '分享', '介绍']
                for prefix in prefixes:
                    name = name.replace(prefix, '')
                return name.strip()

        # 如果没有分隔符，取前20个字符
        return title[:20].strip()

    def _identify_article_type(self, content):
        """识别文章类型"""
        content_lower = content.lower()

        if any(kw in content_lower for kw in ['教程', '步骤', 'tutorial', 'how to', '如何']):
            return 'tutorial'
        elif any(kw in content_lower for kw in ['工具', 'tool', '模型', 'model', '框架', 'framework']):
            return 'tool'
        else:
            return 'news'

    def _extract_core_feature(self, content):
        """提取核心功能/特点"""
        # 查找关键特性描述
        patterns = [
            r'核心功能[:：](.{20,100})',
            r'主要特点[:：](.{20,100})',
            r'能够(.{10,80})',
            r'可以(.{10,80})',
            r'帮助你(.{10,80})',
        ]

        for pattern in patterns:
            match = re.search(pattern, content)
            if match:
                feature = match.group(1).strip()
                # 清理
                feature = re.sub(r'\n', ' ', feature)
                feature = re.sub(r'\s+', ' ', feature)
                return feature[:60]  # 限制长度

        return "提升AI开发效率"  # 默认

    def _extract_value_points(self, content):
        """提取有价值的要点（必须对读者有实际帮助）"""
        valuable_points = []

        # 1. 查找具体的使用方法
        usage_patterns = [
            r'##\s*使用方法\s*\n([\s\S]{100,500}?)(?=\n##|\Z)',
            r'##\s*快速开始\s*\n([\s\S]{100,500}?)(?=\n##|\Z)',
            r'##\s*安装\s*\n([\s\S]{100,300}?)(?=\n##|\Z)',
        ]

        for pattern in usage_patterns:
            match = re.search(pattern, content)
            if match:
                usage_text = match.group(1).strip()
                # 提取具体步骤
                steps = self._extract_steps(usage_text)
                if steps:
                    valuable_points.append({
                        'type': 'usage',
                        'content': f"使用方法：{steps}"
                    })
                    break

        # 2. 查找实际效果/收益
        benefit_keywords = ['提升', '节省', '降低', '提高', '减少', '优化']
        for line in content.split('\n'):
            if any(kw in line for kw in benefit_keywords) and 20 < len(line) < 100:
                # 去除markdown格式
                clean_line = re.sub(r'[#*`\[\]()]', '', line).strip()
                if clean_line and '评论' not in clean_line:
                    valuable_points.append({
                        'type': 'benefit',
                        'content': clean_line
                    })
                    if len(valuable_points) >= 3:
                        break

        # 3. 查找实际案例
        case_pattern = r'案例[:：](.{50,200})'
        match = re.search(case_pattern, content)
        if match:
            valuable_points.append({
                'type': 'case',
                'content': f"实际案例：{match.group(1).strip()}"
            })

        return valuable_points[:4]  # 最多4个要点

    def _extract_steps(self, text):
        """从文本中提取步骤"""
        # 查找数字步骤
        step_pattern = r'[1-9][\.\、](.{10,80})'
        steps = re.findall(step_pattern, text)

        if steps:
            # 只取前3步
            steps = steps[:3]
            return ' → '.join([s.strip() for s in steps])

        # 如果没有数字步骤，查找关键操作
        if 'pip install' in text or 'npm install' in text:
            return "安装工具 → 配置环境 → 开始使用"

        return None

    def _extract_how_to_use(self, content):
        """提取如何获取/使用信息"""
        how_to = {}

        # 查找GitHub链接
        github_match = re.search(r'(https?://github\.com/[\w\-]+/[\w\-]+)', content)
        if github_match:
            how_to['github'] = github_match.group(1)

        # 查找官网链接
        website_match = re.search(r'官网[:：]?\s*(https?://[\w\.\-/]+)', content)
        if website_match:
            how_to['website'] = website_match.group(1)

        # 查找安装命令
        install_match = re.search(r'```[\w]*\n(pip install|npm install|git clone).+?\n```', content, re.DOTALL)
        if install_match:
            how_to['install'] = install_match.group(1).strip()

        return how_to

    def _generate_xhs_title(self, tool_info):
        """
        生成小红书风格标题（≤20字）
        必须清晰说明是什么、能干嘛
        """
        name = tool_info['name']
        article_type = tool_info['type']

        # 根据类型生成不同风格的标题
        if article_type == 'tool':
            # 工具类：说清楚能干嘛
            if '模型' in name or 'AI' in name.upper():
                title = f"{name}！AI开发神器"
            else:
                title = f"{name}：必试的AI工具"
        elif article_type == 'tutorial':
            # 教程类：强调学会后能做什么
            title = f"手把手教你用{name}"
        else:
            # 新闻类：说重点
            title = f"{name}来了"

        # 截断到20字
        if len(title) > 20:
            title = title[:19] + '！'

        return title

    def _generate_xhs_content(self, tool_info, value_points, how_to_use):
        """生成小红书正文内容（必须有实际帮助）"""
        parts = []

        # 1. 开场：清晰说明是什么、能干嘛（不用模板，直接说）
        name = tool_info['name']
        feature = tool_info['feature']
        article_type = tool_info['type']

        if article_type == 'tool':
            intro = f"🔥 {name}是个AI工具，{feature}。"
        elif article_type == 'tutorial':
            intro = f"💡 今天教大家用{name}，{feature}。"
        else:
            intro = f"✨ {name}，{feature}。"

        parts.append(intro + "\n")

        # 2. 核心价值点（每个都必须有实际意义）
        if value_points:
            parts.append("\n")
            for i, point in enumerate(value_points, 1):
                content = point['content']
                # 口语化
                content = self._make_casual(content)
                # 确保不太长
                if len(content) > 100:
                    content = content[:97] + '...'

                # 根据类型选emoji
                if point['type'] == 'usage':
                    emoji = '📝'
                elif point['type'] == 'benefit':
                    emoji = '⚡️'
                elif point['type'] == 'case':
                    emoji = '✅'
                else:
                    emoji = '💡'

                parts.append(f"{emoji} {content}\n")

        # 3. 如何获取（必须有，否则无法使用）
        parts.append("\n")
        if how_to_use:
            if 'github' in how_to_use:
                parts.append(f"🔗 GitHub搜索：{name}\n")
            elif 'website' in how_to_use:
                parts.append(f"🔗 官网搜索：{name}\n")
            else:
                parts.append(f"🔗 搜索：{name}\n")
        else:
            # 如果没有链接，至少告诉如何搜索
            parts.append(f"🔗 百度/谷歌搜索：{name}\n")

        # 4. 行动建议（告诉读者下一步做什么）
        if article_type == 'tool':
            action = "\n💬 建议：先去GitHub看看star数，确认是否活跃维护"
        elif article_type == 'tutorial':
            action = "\n💬 建议：跟着教程自己试一遍，遇到问题评论区问"
        else:
            action = "\n💬 建议：关注这个工具的更新动态"

        parts.append(action)

        # 5. 互动引导
        parts.append("\n\n👍 觉得有用记得点赞收藏！")

        # 组合内容
        content = ''.join(parts)

        # 确保不超过1000字
        if len(content) > 1000:
            content = content[:950] + '\n\n👍 觉得有用记得点赞收藏！'

        return content

    def _make_casual(self, text):
        """将文本口语化"""
        # 替换正式用语
        replacements = {
            '您': '你',
            '我们可以': '可以',
            '需要注意的是': '注意',
            '值得一提的是': '',
            '通过...可以': '用...能',
            '能够': '能',
            '进行': '',
            '实现': '做到',
            '因此': '所以',
            '此外': '还有',
            '综上所述': '总的来说',
            '显著': '明显',
            '有效': '好用',
            '优化': '改进',
            '提升性能': '跑得更快',
            '降低成本': '省钱',
        }

        for old, new in replacements.items():
            text = text.replace(old, new)

        return text


def main():
    """主函数"""
    if len(sys.argv) < 2:
        print("用法: adapt_for_xiaohongshu.py <markdown文件路径> [输出路径]")
        sys.exit(1)

    markdown_path = sys.argv[1]
    output_path = sys.argv[2] if len(sys.argv) > 2 else None

    if not os.path.exists(markdown_path):
        print(f"❌ 文件不存在: {markdown_path}")
        sys.exit(1)

    # 创建适配器
    adapter = XiaohongshuAdapter()

    # 改写内容
    print(f"\n📝 正在将文章改写为小红书风格...")
    xhs_title, xhs_content = adapter.adapt(markdown_path, output_path)

    print(f"\n✅ 改写完成！")
    print(f"📊 小红书标题: {xhs_title}")
    print(f"📊 小红书内容长度: {len(xhs_content)}字")

    if output_path:
        print(f"💾 已保存到: {output_path}")
    else:
        print(f"\n{xhs_content}")


if __name__ == '__main__':
    main()
