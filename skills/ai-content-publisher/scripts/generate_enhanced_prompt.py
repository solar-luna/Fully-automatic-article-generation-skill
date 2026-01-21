#!/usr/bin/env python3
"""
增强版写作提示词生成器
根据话题和类型生成详细的AI写作指导，大幅提升文章质量
"""

import os
import sys
import yaml
import json
from pathlib import Path


class EnhancedPromptGenerator:
    """增强提示词生成器"""

    def __init__(self, config_path=None):
        """初始化生成器"""
        if config_path is None:
            script_dir = Path(__file__).parent
            config_path = script_dir.parent / 'config' / 'writing_templates.yaml'

        with open(config_path, 'r', encoding='utf-8') as f:
            self.config = yaml.safe_load(f)

    def generate_prompt(self, topic, content_type, target_audience="AI开发者"):
        """
        生成增强版写作提示词

        Args:
            topic: 话题信息（dict或string）
            content_type: 内容类型（new_tool/tutorial/industry_news）
            target_audience: 目标受众

        Returns:
            增强的提示词字符串
        """
        # 解析topic
        if isinstance(topic, dict):
            topic_title = topic.get('title', '')
            topic_url = topic.get('url', '')
            topic_summary = topic.get('summary', '')
        else:
            topic_title = str(topic)
            topic_url = ''
            topic_summary = ''

        # 获取受众信息
        audience_info = self.config['audiences'].get(target_audience, self.config['audiences']['AI开发者'])

        # 获取内容类型指南
        type_guide = self.config['content_types'].get(content_type, self.config['content_types']['new_tool'])

        # 获取质量要求
        quality = self.config['quality_requirements']

        # 获取写作风格
        style = self.config['writing_style']

        # 构建提示词
        prompt = f"""你是一位专业的AI技术内容创作者，正在为"{target_audience}"撰写关于以下主题的文章：

【主题】
{topic_title}

【参考链接】
{topic_url if topic_url else '（无）'}

【简要信息】
{topic_summary if topic_summary else '（无）'}

---

## 📋 写作任务

**内容类型**：{type_guide['name']}

**目标受众**：{audience_info['description']}

**内容重点**：{audience_info['focus']}

**写作语气**：{audience_info['tone']}

---

## 📝 文章结构要求

总字数：2500-3000字

"""

        # 添加结构指南
        for section in type_guide['structure']:
            prompt += f"\n### {section['section']}（{section['length']}）\n"
            if isinstance(section['content'], str):
                for line in section['content'].strip().split('\n'):
                    if line.strip():
                        prompt += f"{line}\n"
            else:
                prompt += f"{section['content']}\n"

            if 'avoid' in section:
                prompt += f"\n⚠️ {section['avoid']}\n"

        prompt += "\n---\n\n## ✅ 质量要求\n\n### 必须包含：\n"
        for item in quality['must_have']:
            prompt += f"- {item}\n"

        prompt += "\n### 必须避免：\n"
        for item in quality['must_avoid']:
            prompt += f"- {item}\n"

        prompt += "\n### 最佳实践：\n"
        for item in quality['best_practices']:
            prompt += f"- {item}\n"

        prompt += f"\n---\n\n## 🎨 写作风格\n\n"
        prompt += f"**整体语气**：{style['tone']}\n\n"

        prompt += "**推荐用法**：\n"
        for item in style['prefer']:
            prompt += f"- {item}\n"

        prompt += "\n**句子结构**：\n"
        for item in style['sentence_structure']:
            prompt += f"- {item}\n"

        prompt += "\n**段落结构**：\n"
        for item in style['paragraph_structure']:
            prompt += f"- {item}\n"

        prompt += "\n---\n\n## 🚫 严格禁止\n\n"
        prompt += """1. **不得编造信息**
   - 所有技术细节必须准确
   - 不确定的信息标注"据报道"或"根据官方"
   - 代码必须可运行

2. **不得空洞无物**
   - 每个段落必须有实质内容
   - 避免"众所周知"、"显而易见"等废话
   - 多用具体例子而非抽象概念

3. **不得过度营销**
   - 客观评价，说明优缺点
   - 不用"震惊"、"必看"等标题党词汇

---

## 📌 特别强调

"""

        # 根据内容类型添加特别强调
        type_emphasis = {
            # AI工具实战类
            'tool_deep_dive': """- 必须有实际的使用步骤，不能只介绍功能
- 必须提供安装命令（bash代码块）
- 必须提供基本使用命令（代码块）
- 如果有配置文件，必须提供配置示例（代码块）
- 代码块必须指定语言（bash、python、json等）
- 必须对比同类工具，说明优势
- 如果是付费工具，必须说明价格
- 必须有效果对比数据
- 避免说"附上代码"但不实际提供代码""",

            'tool_workflow': """- 必须展示完整的工作流程
- 每个工具的作用要说清楚
- 工具之间如何衔接要详细说明
- 每个步骤如果涉及命令，必须提供代码块
- 代码块要简洁实用（≤20行），优先展示核心命令和参数
- 代码块必须指定语言（bash、python、json等）
- 必须有效率提升的量化数据
- 避免说"附上代码"但不实际提供代码""",

            # 创业方法论类
            'startup_knowledge': """- 必须有真实案例支撑
- 避免空洞的理论
- 提供可执行的行动步骤
- 说明常见错误和避坑方法""",

            'startup_pitfalls': """- 必须基于真实经历
- 保持真诚和谦逊的态度
- 深入分析错误的根本原因
- 提供具体的避免策略""",

            # 效率提升类
            'workflow_optimization': """- 必须有优化前后的对比数据
- 提供完整的SOP流程
- 说明实施步骤和注意事项
- 方法要适合一人公司场景""",

            'time_management': """- 必须有具体的时间分配示例
- 方法要实用可行
- 避免过于理想化
- 提供个性化调整建议""",

            # 个人成长类
            'skill_development': """- 提供清晰的能力提升路径
- 推荐具体学习资源
- 分享真实经历和经验
- 设定可达成的目标""",

            'mindset_adjustment': """- 保持真诚，不要说教
- 避免空洞的鸡汤
- 提供实用的心理调节方法
- 分享真实的脆弱时刻""",

            # 案例分析类
            'success_case': """- 案例必须真实
- 数据要可信
- 分析要深入，不要流于表面
- 区分可复制和不可复制的部分""",

            'failure_analysis': """- 保持客观，不要指责
- 分析要深入到本质
- 提供建设性的建议
- 说明如何提前识别问题""",

            # 资源整合类
            'tool_collection': """- 推荐的工具必须自己用过
- 客观评价，不要只说好话
- 提供多种价位选择
- 说明适用场景和局限性""",

            'template_sharing': """- 模板必须实用可用
- 提供完整内容，不要藏着掖着
- 支持读者根据自己情况调整
- 提供填写示例和使用说明""",

            # 兼容旧类型
            'new_tool': """- 必须有实际的使用步骤，不能只介绍功能
- 必须说明如何获取/安装
- 必须对比同类工具，说明优势
- 如果是付费工具，必须说明价格""",

            'tutorial': """- 代码必须完整可运行，不能省略关键部分
- 每个步骤都要说明"为什么这样做"
- 必须提供完整的代码仓库链接或Gist
- 遇到的坑和解决方法也要写出来""",

            'industry_news': """- 不只报道事件，要分析影响
- 必须说明对读者的实际意义
- 提供具体的行动建议
- 避免纯新闻搬运，要有自己的分析"""
        }

        if content_type in type_emphasis:
            prompt += type_emphasis[content_type] + "\n"

        prompt += "\n---\n\n## 📦 内容格式化指南（必须遵守）\n\n"
        prompt += """**⚠️ 重要：文章中必须包含3-5个引用块！**

在以下场景使用引用块强调关键信息：

1. **💡 提示** - 易错步骤、重要配置、关键操作前的提醒
   示例：`> **💡 提示**: 安装时务必使用Python 3.8+版本，旧版本可能有兼容性问题`

2. **⚠️ 警告** - 安全风险、性能问题、兼容性警告
   示例：`> **⚠️ 警告**: 此配置会影响生产环境，请在测试环境先验证`

3. **📌 要点** - 重要段落后的核心总结、关键信息提炼
   示例：`> **📌 要点**: 这个功能的核心是通过异步处理提升30%的性能`

4. **✅ 建议** - 最佳实践、优化技巧、专业建议、行动指南
   示例：`> **✅ 建议**: 对于大文件处理，建议使用流式读取以节省内存`

**格式要求**：
- 每篇文章必须包含3-5个引用块（根据2500-3000字的文章长度）
- 每个引用块控制在1-2行，保持简洁
- 不要在每个段落都加，只在关键位置使用
- 优先在：易错步骤、重要警告、最佳实践、核心要点处使用

**如何判断该用引用块**：
- 这个信息是否特别重要，需要读者注意？
- 这是否是易错的地方或常见坑点？
- 这是否是核心要点的总结？
- 这是否是给读者的关键建议？

"""

        prompt += "\n---\n\n## 🎯 开始创作\n\n"
        prompt += "现在请基于以上要求，创作一篇高质量的AI技术文章。\n\n"
        prompt += "⚠️ 请直接输出文章内容，使用Markdown格式，不要有任何额外的解释或元信息。\n"

        return prompt


def main():
    """主函数"""
    if len(sys.argv) < 3:
        print("用法: generate_enhanced_prompt.py <topic_json> <content_type> [target_audience]")
        print("示例: generate_enhanced_prompt.py topic.json new_tool 'AI开发者'")
        sys.exit(1)

    topic_file = sys.argv[1]
    content_type = sys.argv[2]
    target_audience = sys.argv[3] if len(sys.argv) > 3 else "AI开发者"

    # 读取话题
    with open(topic_file, 'r', encoding='utf-8') as f:
        topic = json.load(f)

    # 生成提示词
    generator = EnhancedPromptGenerator()
    prompt = generator.generate_prompt(topic, content_type, target_audience)

    # 输出
    print(prompt)


if __name__ == '__main__':
    main()
