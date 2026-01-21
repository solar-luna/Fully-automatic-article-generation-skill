#!/usr/bin/env python3
"""
微信技术文章生成脚本
支持标准模式和深度模式
"""

import argparse
import json
import os
import subprocess
import sys
from datetime import datetime
from anthropic import Anthropic


def generate_prompt(topic, url, content_type, mode):
    """
    生成 Claude 提示词

    Args:
        topic: 话题标题
        url: 参考链接
        content_type: 内容类型 (new_tool/tutorial/industry_news)
        mode: 模式 (standard/deep)
    """

    # 根据模式设定字数要求
    if mode == 'deep':
        word_count = "5000字"
        depth = "深度分析文章"
        research_rounds = "5-8轮"
    else:
        word_count = "2000-3000字"
        depth = "科普文章"
        research_rounds = "3-5轮"

    # 根据内容类型设定写作重点
    type_guidance = {
        'new_tool': '''
重点介绍：
1. 功能特性（核心能力是什么）
2. 使用场景（解决什么问题）
3. 如何开始（安装/使用步骤）
4. 与竞品对比（优势在哪里）
''',
        'tutorial': '''
重点讲解：
1. 核心原理（是什么、为什么）
2. 实战步骤（具体怎么做）
3. 代码示例（可运行的例子）
4. 应用场景（什么时候用）
''',
        'industry_news': '''
重点分析：
1. 事件概述（发生了什么）
2. 影响分析（对开发者的影响）
3. 实用建议（如何应对）
4. 行业趋势（未来发展方向）
'''
    }

    guidance = type_guidance.get(content_type, type_guidance['new_tool'])

    prompt = f"""生成一篇关于"{topic}"的微信公众号文章。

## ⚠️ 重要提醒

**语言要求：全文必须是简体中文！**
- 文章标题必须是中文
- 正文内容必须是中文
- 只有专有名词（如公司名、产品名、技术术语）可以保留英文
- 代码、命令、URL等可以保留英文

**网络工具使用限制：**
- 如果 WebSearch 或 WebFetch 工具不可用，请基于你的知识库生成内容
- 不要因为无法访问网络而拒绝生成文章
- 可以使用参考链接中的信息作为基础

## 文章要求

### 基本信息
- 话题：{topic}
- 参考链接：{url}
- 内容类型：{content_type}
- 字数：{word_count}
- 文章类型：{depth}

### 写作指导
{guidance}

### 写作风格（严格遵守）

1. **文章结构**
   - 开头用100-200字吸引读者（问题/场景/数据引入）
   - 主体部分按小标题展开
   - 结尾总结要点 + 行动号召
   - ❌ 不要添加"参考资料"、"优缺点说明"等额外章节

2. **语言风格（⚠️ 重要：必须用中文写作）**
   - 标题必须是中文
   - 正文必须是简体中文
   - 面向普通用户，避免过度技术化
   - 多用短句（15-20字）
   - 使用类比和比喻帮助理解
   - 多用"你"、"我们"，创造对话感
   - ❌ 不要直接照搬英文原文，必须用中文重新表达

3. **链接格式**
   - 所有URL使用纯文本格式
   - ❌ 错误：`[官网](https://example.com/)`
   - ✅ 正确：`官方网站：https://example.com/`

4. **参考来源链接**
   - 文章末尾必须附上参考来源链接
   - 格式：`参考来源：TechCrunch: https://techcrunch.com/xxx`
   - 每个来源都要有可点击的链接

5. **配图**
   - 无需生成封面图（使用预定义封面库）
   - 根据内容需要决定是否生成额外配图（0-2张）

5. **搜索策略（如果网络工具可用）**
   - 第1轮：官方信息和文档
   - 第2轮：技术解析和详细介绍
   - 第3轮：对比评测和使用场景
   - 第4轮：补充验证（{research_rounds}）

### 输出要求

1. 生成2000-3000字的原创内容
2. 只输出正文，不要添加"参考资料"等额外章节
3. 链接使用纯文本格式
4. **文章末尾必须附上参考来源链接，格式如下（每个来源两行）**：

```
参考来源：

TechCrunch
{url}

（如果搜索到其他来源，也按相同格式添加）
```

**重要**：必须使用上面提供的参考链接 "{url}"，格式为：
- 第1行：来源名称（从URL提取，如TechCrunch、OpenAI Blog等）
- 第2行：完整的 HTTPS 链接
- 来源之间空一行

现在开始生成文章。
"""

    return prompt


def check_network():
    """检查网络连接是否可用"""
    import subprocess
    try:
        # 测试DNS解析（使用国内网站）
        result = subprocess.run(
            ['nslookup', 'baidu.com'],
            capture_output=True,
            timeout=5
        )
        if result.returncode != 0:
            return False

        # 测试HTTP连接（使用国内可访问的网站）
        result = subprocess.run(
            ['curl', '-s', '--connect-timeout', '5', '--max-time', '10', 'https://www.baidu.com'],
            capture_output=True,
            timeout=15
        )
        return result.returncode == 0
    except Exception:
        return False


def map_content_type(content_type):
    """
    将 ai-content-publisher 的内容类型映射到 wechat-tech-writer 支持的类型

    ai-content-publisher 支持更多类型（10+种），但 wechat-tech-writer 只支持3种基本类型
    这个函数负责将扩展类型映射到基本类型
    """
    type_mapping = {
        # AI工具实战类 -> new_tool
        'tool_deep_dive': 'new_tool',
        'tool_workflow': 'new_tool',

        # 创业方法论类 -> tutorial
        'startup_knowledge': 'tutorial',
        'startup_pitfalls': 'tutorial',

        # 效率提升类 -> tutorial
        'workflow_optimization': 'tutorial',
        'time_management': 'tutorial',

        # 个人成长类 -> tutorial
        'skill_development': 'tutorial',
        'mindset_adjustment': 'tutorial',

        # 案例分析类 -> industry_news
        'success_case': 'industry_news',
        'failure_analysis': 'industry_news',

        # 资源整合类 -> new_tool
        'tool_collection': 'new_tool',
        'template_sharing': 'new_tool',
    }

    # 如果是已知的扩展类型，映射它；否则保持原样（可能已经是基本类型）
    return type_mapping.get(content_type, content_type)


def main():
    parser = argparse.ArgumentParser(description='微信技术文章生成脚本')
    parser.add_argument('--topic', required=True, help='话题标题')
    parser.add_argument('--url', required=True, help='参考链接')
    parser.add_argument('--type', default='new_tool',
                       help='内容类型（支持 ai-content-publisher 的所有类型，会自动映射）')
    parser.add_argument('--mode', default='standard',
                       choices=['standard', 'deep'],
                       help='文章模式：standard=2000-3000字, deep=5000字')
    parser.add_argument('--output', required=True, help='输出目录')
    parser.add_argument('--author', default='阳桃AI干货', help='作者名称')

    args = parser.parse_args()

    # 映射内容类型
    original_type = args.type
    mapped_type = map_content_type(original_type)

    # 验证映射后的类型
    valid_types = ['new_tool', 'tutorial', 'industry_news']
    if mapped_type not in valid_types:
        print(f"❌ 错误：未知的内容类型 '{original_type}'")
        print(f"   支持的类型：{', '.join(valid_types)}")
        print(f"   或 ai-content-publisher 配置文件中的任何类型")
        sys.exit(1)

    if original_type != mapped_type:
        print(f"📝 内容类型映射: {original_type} -> {mapped_type}")

    # 使用映射后的类型
    args.type = mapped_type

    # 创建输出目录
    output_dir = os.path.abspath(args.output)
    os.makedirs(output_dir, exist_ok=True)

    # 切换到输出目录（这样Claude生成的文件会保存在这里）
    original_dir = os.getcwd()
    os.chdir(output_dir)

    # 生成提示词
    prompt = generate_prompt(args.topic, args.url, args.type, args.mode)

    # 检查网络连接
    network_available = check_network()
    if not network_available:
        print("⚠️  警告：网络连接不可用")
        print("   Claude API 需要网络连接才能工作")
        print("   建议检查云平台安全组规则，确保允许出站HTTPS流量")
        print()

    print("=" * 60)
    print("微信技术文章生成器")
    print("=" * 60)
    print(f"话题：{args.topic}")
    print(f"链接：{args.url}")
    print(f"类型：{args.type}")
    print(f"模式：{args.mode}")
    print(f"输出：{output_dir}")
    print(f"网络：{'✅ 可用' if network_available else '❌ 不可用'}")
    print("=" * 60)
    print()

    # 调用 Claude CLI 生成文章
    try:
        print("🤖 正在调用 Claude 生成文章...")
        print()

        # 修改提示词，明确要求输出markdown格式
        enhanced_prompt = f"""{prompt}

**重要输出要求**：
1. 直接输出完整的 markdown 格式文章，不要有任何额外说明
2. 文章开头就是标题（# 标题），不要有其他内容
3. 不要使用代码块包裹文章内容
4. 文章结束后不要有任何额外说明或总结

请立即开始输出文章：
"""

        # 将提示词保存到临时文件
        import tempfile
        with tempfile.NamedTemporaryFile(mode='w', suffix='.txt', delete=False, encoding='utf-8') as f:
            f.write(enhanced_prompt)
            prompt_file = f.name

        try:
            # 使用 Anthropic API 生成文章
            print("🤖 正在调用 Claude API 生成文章...")
            print()

            # 初始化 API 客户端（会自动从环境变量读取配置）
            client = Anthropic()

            # 调用 API 生成文章
            response = client.messages.create(
                model="claude-sonnet-4-5-20250929",
                max_tokens=8000,
                temperature=0.7,
                messages=[{
                    "role": "user",
                    "content": enhanced_prompt
                }]
            )

            # 提取文章内容
            article_content = ""
            for block in response.content:
                if hasattr(block, 'text'):
                    article_content += block.text

            if not article_content or len(article_content) < 100:
                print(f"❌ 文章内容太短或为空（{len(article_content)} 字符）")
                sys.exit(1)

            # 清理内容
            lines = article_content.split('\n')

            # 跳过开头的说明性文字，找到实际的文章开始（markdown标题）
            start_idx = 0
            for i, line in enumerate(lines):
                stripped = line.strip()
                if stripped.startswith('#') and not stripped.startswith('#!'):
                    start_idx = i
                    break

            article_content = '\n'.join(lines[start_idx:]).strip()

            # 移除可能的 markdown 代码块标记
            if article_content.startswith('```markdown'):
                article_content = article_content[len('```markdown'):].strip()
            if article_content.startswith('```'):
                article_content = article_content[3:].strip()
            if article_content.endswith('```'):
                article_content = article_content[:-3].strip()

            # 二次检查内容长度
            if len(article_content) < 500:
                print(f"❌ 文章内容过短（{len(article_content)} 字符）")
                print(f"内容预览：{article_content[:300]}")
                sys.exit(1)

            # 保存文章到文件
            article_file = 'article.md'
            article_path = os.path.join(output_dir, article_file)

            with open(article_path, 'w', encoding='utf-8') as f:
                f.write(article_content)

            print("=" * 60)
            print("✅ 文章生成完成")
            print("=" * 60)
            print(f"📄 文章：{article_path}")
            print(f"📊 字数：约 {len(article_content)} 字符")
            print()

            # ⚠️ 封面图由 auto_publish.sh 中的 select_cover.py 统一处理
            # 此处不再生成或选择封面，确保所有封面都从封面库选择

        except Exception as e:
            print(f"❌ API 调用失败：{e}")
            import traceback
            traceback.print_exc()
            sys.exit(1)

        finally:
            # 删除临时文件
            try:
                os.unlink(prompt_file)
            except:
                pass

    except subprocess.TimeoutExpired:
        print("❌ 生成超时（10分钟）")
        print("💡 可能原因：")
        print("   1. 网络连接不稳定")
        print("   2. 文章主题过于复杂")
        print("   3. Claude 服务响应慢")
        sys.exit(1)
    except Exception as e:
        print(f"❌ 错误：{e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
    finally:
        # 恢复原来的工作目录
        os.chdir(original_dir)


if __name__ == '__main__':
    main()
