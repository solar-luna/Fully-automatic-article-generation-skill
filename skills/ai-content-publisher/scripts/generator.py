#!/usr/bin/env python3
"""
内容生成脚本
调用 wechat-tech-writer skill 生成文章
"""

import json
import os
import sys
from datetime import datetime


def load_selected_topics(cache_path=None):
    """加载选中的话题"""
    if cache_path is None:
        script_dir = os.path.dirname(os.path.abspath(__file__))
        cache_dir = os.path.join(os.path.dirname(script_dir), 'cache')
        cache_path = os.path.join(cache_dir, 'selected_topics.json')

    try:
        with open(cache_path, 'r', encoding='utf-8') as f:
            return json.load(f)
    except FileNotFoundError:
        print(f"选题文件不存在: {cache_path}")
        print("请先运行 selector.py 选择选题")
        sys.exit(1)


def get_current_date_str():
    """获取当前日期字符串"""
    return datetime.now().strftime("%Y年%m月%d日")


def validate_date(topic_date):
    """验证话题日期是否在48小时内"""
    from datetime import timedelta
    now = datetime.now()
    try:
        pub_date = datetime.fromisoformat(topic_date.replace('Z', '+00:00'))
        if (now - pub_date.replace(tzinfo=None)) > timedelta(hours=48):
            return False
        return True
    except:
        return True


def get_type_prompt(content_type):
    """根据内容类型生成提示词"""
    type_prompts = {
        # AI工具实战类
        'tool_deep_dive': "这是一篇单工具深度解析文章。参考模板：wechat-tech-writer/templates/tool_deep_dive.md。重点：1. 痛点引入 2. 工具介绍 3. 实战演示（必须包含安装命令、使用命令的代码块） 4. 效果对比 5. 适用人群。代码块要求：使用```语言名称格式，必须提供安装命令（bash）、基本使用命令，代码要简洁实用（≤20行），避免说'附上代码'但不实际提供",
        'tool_workflow': "这是一篇工具组合工作流文章。参考模板：wechat-tech-writer/templates/tool_workflow.md。重点：1. 场景描述 2. 工具组合介绍 3. 完整流程演示（每个步骤如果涉及命令，必须提供代码块） 4. 效率提升分析。代码块要求：使用```语言名称格式，代码要简洁实用（≤20行），优先展示核心命令和参数，避免说'附上代码'但不实际提供",

        # 创业方法论类
        'startup_knowledge': "这是一篇创业必知必会文章。参考模板：wechat-tech-writer/templates/startup_knowledge.md。重点：1. 认知破题 2. 核心知识点 3. 案例分析 4. 实操建议",
        'startup_pitfalls': "这是一篇创业避坑指南文章。参考模板：wechat-tech-writer/templates/startup_pitfalls.md。重点：1. 个人故事引入 2. 错误分析 3. 避坑清单",

        # 效率提升类
        'workflow_optimization': "这是一篇工作流优化案例文章。参考模板：wechat-tech-writer/templates/workflow_optimization.md。重点：1. 效率现状对比 2. 核心方法论 3. 完整SOP展示 4. 实施指南",
        'time_management': "这是一篇时间管理方法文章。参考模板：wechat-tech-writer/templates/time_management.md。重点：1. 时间困境 2. 方法论介绍 3. 一日时间分配实例 4. 效果与调整",

        # 个人成长类
        'skill_development': "这是一篇能力提升路径文章。参考模板：wechat-tech-writer/templates/skill_development.md。重点：1. 能力框架 2. 能力提升方法 3. 个人经验 4. 行动清单",
        'mindset_adjustment': "这是一篇心态调整指南文章。参考模板：wechat-tech-writer/templates/mindset_adjustment.md。重点：1. 心理状态描述 2. 心态调整方法 3. 个人故事 4. 长期心态建设",

        # 案例分析类
        'success_case': "这是一篇成功案例拆解文章。参考模板：wechat-tech-writer/templates/success_case.md。重点：1. 案例背景 2. 关键成功因素 3. 可复制的经验 4. 关键启示",
        'failure_analysis': "这是一篇失败案例分析文章。参考模板：wechat-tech-writer/templates/failure_analysis.md。重点：1. 案例描述 2. 失败原因分析 3. 如何避免",

        # 资源整合类
        'tool_collection': "这是一篇工具/资源推荐合集文章。参考模板：wechat-tech-writer/templates/tool_collection.md。重点：1. 资源清单（8-10个工具） 2. 使用建议 3. 我的工具箱",
        'template_sharing': "这是一篇模板/清单分享文章。参考模板：wechat-tech-writer/templates/template_sharing.md。重点：1. 模板说明 2. 模板展示 3. 使用指南 4. 获取方式",

        # 兼容旧类型
        'new_tool': "这是一篇新工具/新模型介绍文章。重点介绍：1. 是什么（产品介绍）2. 核心特性 3. 对开发者的价值 4. 如何开始使用",
        'tutorial': "这是一篇实战教程文章。重点介绍：1. 核心原理 2. 实战步骤 3. 代码示例 4. 应用场景",
        'industry_news': "这是一篇行业动态分析文章。重点介绍：1. 事件概述 2. 技术层面的影响 3. 对开发者的建议"
    }
    return type_prompts.get(content_type, "重点介绍对AI开发者和产品经理有价值的信息")


def generate_article_prompt(topic, index):
    """生成文章提示词（用于调用 wechat-tech-writer）"""
    current_date = get_current_date_str()
    type_prompt = get_type_prompt(topic['content_type'])

    prompt = f"""
写一篇关于"{topic['title']}"的公众号文章。

⚠️ 重要约束：
- 今天是 {current_date}
- 只搜索48小时内的新内容
- 验证所有信息的发布时间

文章类型：{topic['content_type']}
{type_prompt}

参考资料：
- 标题：{topic['title']}
- 链接：{topic['url']}
- 简介：{topic.get('summary', '')}

要求：
1. 搜索最新信息（今天是{current_date}，确保内容是新的）
2. 生成2000-3000字的原创内容
3. 生成封面图
4. 标题控制在10个汉字以内
5. 只输出正文，不要添加"参考资料"等额外章节
6. 链接使用纯文本格式，不要用markdown超链接
"""

    return prompt


def quality_check(article_path):
    """简单的文章质量检查"""
    if not os.path.exists(article_path):
        return False, "文章文件不存在"

    with open(article_path, 'r', encoding='utf-8') as f:
        content = f.read()

    # 检查字数
    word_count = len(content)
    if word_count < 1500:
        return False, f"字数不足: {word_count} (建议≥2000)"

    # 检查是否包含封面图引用
    if 'cover.png' not in content and '封面' not in content:
        return False, "缺少封面图"

    # 检查是否有markdown超链接
    if '](' in content:
        return False, "包含markdown超链接，需要改为纯文本"

    return True, "OK"


def save_generation_result(topic, output_dir, article_index):
    """保存生成结果"""
    result = {
        'title': topic['title'],
        'url': topic['url'],
        'content_type': topic['content_type'],
        'score': topic.get('score', 0),
        'generated_at': datetime.now().isoformat(),
        'output_dir': output_dir,
        'article_index': article_index
    }

    script_dir = os.path.dirname(os.path.abspath(__file__))
    cache_dir = os.path.join(os.path.dirname(script_dir), 'cache')
    os.makedirs(cache_dir, exist_ok=True)

    result_path = os.path.join(cache_dir, f'generation_result_{article_index}.json')
    with open(result_path, 'w', encoding='utf-8') as f:
        json.dump(result, f, ensure_ascii=False, indent=2)

    return result_path


# 注意：这个脚本主要提供接口和辅助函数
# 实际的文章生成由 SKILL.md 中的 Claude 通过调用 wechat-tech-writer skill 完成
# 这里提供一个模拟生成结果的函数供测试


def mock_generate_article(topic, index):
    """模拟生成文章（用于测试）"""
    script_dir = os.path.dirname(os.path.abspath(__file__))
    base_dir = os.path.dirname(script_dir)

    # 创建输出目录
    today = datetime.now().strftime("%Y-%m-%d")
    output_dir = os.path.join(base_dir, 'output', today, f'article_{index}')
    os.makedirs(output_dir, exist_ok=True)

    # 生成模拟文章
    article_path = os.path.join(output_dir, 'article.md')
    with open(article_path, 'w', encoding='utf-8') as f:
        f.write(f"# {topic['title']}\n\n")
        f.write(f"![封面图](cover.png)\n\n")
        f.write(f"## 概述\n\n")
        f.write(f"这是一篇关于 {topic['title']} 的文章。\n\n")
        f.write(f"来源: {topic['url']}\n\n")
        f.write(f"类型: {topic['content_type']}\n\n")
        f.write(f"## 总结\n\n")
        f.write(f"（实际内容由 wechat-tech-writer skill 生成）\n")

    # 生成模拟封面图标记
    cover_path = os.path.join(output_dir, 'cover.png')
    with open(cover_path, 'w') as f:
        f.write("（实际封面图由 wechat-tech-writer skill 生成）")

    print(f"✅ 模拟生成文章 {index}: {topic['title']}")
    print(f"   输出目录: {output_dir}")

    # 保存结果
    save_generation_result(topic, output_dir, index)

    return {
        'article_path': article_path,
        'cover_path': cover_path,
        'output_dir': output_dir
    }


if __name__ == '__main__':
    # 加载选题
    topics = load_selected_topics()

    print(f"共 {len(topics)} 个选题待生成")

    # 为每个选题生成文章
    results = []
    for i, topic in enumerate(topics, 1):
        print(f"\n=== 生成文章 {i}/{len(topics)} ===")
        print(f"标题: {topic['title']}")
        print(f"类型: {topic['content_type']}")

        # 模拟生成（实际由 Claude 调用 skill 完成）
        result = mock_generate_article(topic, i)
        results.append({
            'topic': topic,
            'result': result
        })

    print(f"\n=== 生成完成 ===")
    print(f"共生成 {len(results)} 篇文章")

    # 输出生成的提示词供 Claude 使用
    print("\n=== 供 Claude 使用的提示词 ===")
    for i, topic in enumerate(topics, 1):
        print(f"\n【文章 {i}】")
        print(generate_article_prompt(topic, i))
