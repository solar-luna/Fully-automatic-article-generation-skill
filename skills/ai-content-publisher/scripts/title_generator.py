#!/usr/bin/env python3
"""
智能标题生成模块
根据文章类型和内容生成吸引人且符合实际的标题
"""

from datetime import datetime
import re


# 标题模板库（优化版 - 基于4个优化维度）
# 维度1：数字化 - 用具体数字增加可信度
# 维度2：对比化 - 制造反差和冲突
# 维度3：痛点化 - 直击受众痛点
# 维度4：好奇化 - 引发好奇

TITLE_TEMPLATES = {
    # 类型1：AI工具实战类 - 单工具深度解析
    'tool_deep_dive': [
        # 数字化
        "{tool_name}：{number}个功能让你{benefit}",
        "{number}步精通{tool_name}",
        # 对比化
        "我用{tool_name}{action}，只用了{time}",
        "从{pain_point}到{benefit}：{tool_name}实战",
        # 痛点化
        "别再{pain_point}了！{tool_name}来帮你",
        "{tool_name}：{pain_point}的终极解决方案",
        # 好奇化
        "{tool_name}背后的{number}个秘密",
    ],

    # 类型1：AI工具实战类 - 工具组合工作流
    'tool_workflow': [
        "{number}个工具打造AI工作流",
        "我的AI工作流：{number}个工具省{time}",
        "从手动到自动：{number}个工具组合",
    ],

    # 类型2：创业方法论类 - 创业必知必会
    'startup_knowledge': [
        "一人公司必知的{number}个AI技能",
        "创业第一课：{number}个关键概念",
        "为什么你的创业总是{pain_point}",
    ],

    # 类型2：创业方法论类 - 创业避坑指南
    'startup_pitfalls': [
        "创业避坑：{number}个致命错误",
        "我花{cost}买的{number}个教训",
        "别再犯这{number}个创业错误",
    ],

    # 类型3：效率提升类 - 工作流优化
    'workflow_optimization': [
        "我把{long_time}工作压缩到{short_time}",
        "{number}个方法让效率翻倍",
        "从每天{long_time}到{short_time}：我的方法",
    ],

    # 类型3：效率提升类 - 时间管理
    'time_management': [
        "一人公司时间管理：{number}个方法",
        "我用这个方法，{time}完成{long_time}的工作",
        "告别{pain_point}：时间管理{number}法则",
    ],

    # 类型4：个人成长类 - 能力提升
    'skill_development': [
        "一人公司必备的{number}项能力",
        "{number}个月掌握{skill}",
        "从{level_a}到{level_b}：{number}个方法",
    ],

    # 类型4：个人成长类 - 心态调整
    'mindset_adjustment': [
        "创业心态：{number}个关键转变",
        "一人公司的{number}个心理陷阱",
        "告别{pain_point}：{number}个心态调整",
    ],

    # 类型5：案例分析类 - 成功案例
    'success_case': [
        "他用{tool}实现月入{income}",
        "{number}个月从0到{achievement}",
        "从{state_a}到{state_b}：{number}个关键",
    ],

    # 类型5：案例分析类 - 失败分析
    'failure_analysis': [
        "为什么他的项目失败了：{number}个原因",
        "复盘：价值{cost}的{number}个教训",
        "别犯这{number}个致命错误",
    ],

    # 类型6：资源整合类 - 工具合集
    'tool_collection': [
        "一人公司工具箱：{number}个必备工具",
        "{number}个AI工具让你{benefit}",
        "告别{pain_point}：{number}个工具推荐",
    ],

    # 类型6：资源整合类 - 模板分享
    'template_sharing': [
        "{number}个模板让你{benefit}",
        "我的{type}模板（附下载）",
        "还在{pain_point}？用这{number}个模板",
    ],

    # 保留旧类型以兼容现有代码
    'new_tool': [
        "{tool_name}来了！{benefit}效率提升{number}倍",
        "这个AI工具让我{benefit}，强烈推荐",
        "{tool_name}：{pain_point}的终极解决方案",
        "告别{pain_point}！{tool_name}让{benefit}",
        "{company}发布{tool_name}，{number}个亮点不容错过",
        "{tool_name}：{time}上手的{benefit}神器",
        "推荐！{tool_name}帮你{benefit}",
    ],
    'tutorial': [
        "{number}步用{tool}实现{goal}（附代码）",
        "从零开始：{time}用{tool}搞定{goal}",
        "手把手教你用{tool}{action}，小白也能学会",
        "{tool}实战：我用{time}{action}的全过程",
        "这样用{tool}才对！{number}个实战技巧",
        "告别{pain_point}！用{tool}{action}的完整指南",
        "{action}最佳实践：用{tool}提升{benefit}",
    ],
    'industry_news': [
        "{event}来了！{target}必知的{number}件事",
        "{company}发布{event}，{impact}",
        "重磅！{event}发布，{target}如何抓住机会",
        "{event}深度解读：{number}个关键变化",
        "{event}背后：{industry}的{number}个发展趋势",
        "{event}：{target}需要知道的实用信息",
        "解读{event}：对{target}的{impact}",
    ],
}


def extract_tool_name(topic):
    """从话题中提取工具名称"""
    # 简单提取：取标题的核心部分
    title = topic['title']
    # 移除常见的前缀/后缀
    prefixes = ['New ', 'Introducing ', 'Announcing ', '发布：', '推出：']
    for prefix in prefixes:
        if prefix in title:
            title = title.replace(prefix, '')
    return title.split('|')[0].split('-')[0].strip()[:30]


def extract_benefit(topic):
    """提取具体收益（增强版）"""
    text = (topic.get('title', '') + ' ' + topic.get('summary', '')).lower()

    # 收益关键词映射（更具体）
    benefits = {
        '节省时间': ['save time', 'faster', 'quick', '节省', '快速', '提速'],
        '降低成本': ['free', 'cost', 'cheap', '免费', '低成本', '省钱'],
        '提高效率': ['efficient', 'productivity', 'boost', '效率', '生产力'],
        '简化流程': ['easy', 'simple', 'automate', '简单', '自动', '便捷'],
        '增强能力': ['powerful', 'advanced', 'smart', '强大', '智能', '高级'],
        '易于上手': ['beginner', 'user-friendly', '入门', '新手', '友好'],
    }

    for benefit, keywords in benefits.items():
        if any(kw in text for kw in keywords):
            return benefit

    return '提高效率'  # 默认收益


def extract_core_feature(topic):
    """从话题中提取核心特性"""
    summary = topic.get('summary', '')
    title = topic['title']

    # 查找技术关键词
    tech_keywords = ['API', 'LLM', 'Agent', '模型', '算法', '框架']
    for kw in tech_keywords:
        if kw in title or kw in summary:
            return kw

    return '新功能'


def extract_number(topic):
    """从话题中提取有意义的数字"""
    text = topic.get('title', '') + ' ' + topic.get('summary', '')

    # 1. 直接查找数字（优先级：3-10之间的数字）
    numbers = re.findall(r'\b([3-9]|10)\b', text)
    if numbers:
        return numbers[0]

    # 2. 根据内容特征推断合适的数字
    text_lower = text.lower()
    if any(kw in text_lower for kw in ['step', 'way', 'method', '步骤', '方法']):
        return '5'  # 教程类默认5步
    elif any(kw in text_lower for kw in ['tip', 'trick', '技巧', '要点']):
        return '7'  # 技巧类默认7个
    elif any(kw in text_lower for kw in ['thing', 'point', '件事', '要点']):
        return '3'  # 要点类默认3个
    else:
        return '3'  # 默认3


def extract_time(topic):
    """提取学习/使用时间"""
    text = topic.get('title', '') + ' ' + topic.get('summary', '')

    # 1. 查找已有的时间表述
    time_patterns = [
        (r'(\d+)\s*分钟', lambda m: f"{m.group(1)}分钟"),
        (r'(\d+)\s*min', lambda m: f"{m.group(1)}分钟"),
        (r'(\d+)\s*小时', lambda m: f"{m.group(1)}小时"),
        (r'(\d+)\s*hour', lambda m: f"{m.group(1)}小时"),
    ]

    for pattern, formatter in time_patterns:
        match = re.search(pattern, text, re.IGNORECASE)
        if match:
            return formatter(match)

    # 2. 根据内容类型推断
    text_lower = text.lower()
    content_type = topic.get('content_type', '')
    if 'tutorial' in content_type or 'guide' in text_lower:
        return '15分钟'  # 教程默认15分钟
    elif 'quick' in text_lower or '快速' in text:
        return '5分钟'
    else:
        return '10分钟'


def extract_pain_point(topic):
    """识别用户痛点"""
    text = (topic.get('title', '') + ' ' + topic.get('summary', '')).lower()

    # 痛点关键词映射
    pain_points = {
        '效率低': ['slow', 'inefficient', '缓慢', '效率', '速度'],
        '成本高': ['expensive', 'cost', '昂贵', '价格', '付费'],
        '难度大': ['difficult', 'complex', 'hard', '困难', '复杂'],
        '手动操作': ['manual', 'tedious', '手动', '重复'],
        '配置繁琐': ['setup', 'configuration', '配置', '安装'],
    }

    for pain, keywords in pain_points.items():
        if any(kw in text for kw in keywords):
            return pain

    return '效率低'  # 默认痛点


def extract_target_audience(topic):
    """提取目标受众"""
    text = (topic.get('title', '') + ' ' + topic.get('summary', '')).lower()

    audiences = {
        'AI开发者': ['developer', 'engineer', '开发', '工程师'],
        'AI产品经理': ['product', 'pm', '产品'],
        'AI初学者': ['beginner', 'starter', '入门', '新手', '初学'],
        '企业用户': ['enterprise', 'business', '企业', '商业'],
        'AI从业者': ['professional', 'practitioner', '从业', '专业'],
    }

    for audience, keywords in audiences.items():
        if any(kw in text for kw in keywords):
            return audience

    return 'AI开发者'  # 默认受众


def extract_impact(topic):
    """提取影响描述"""
    text = (topic.get('title', '') + ' ' + topic.get('summary', '')).lower()

    if any(kw in text for kw in ['game changer', 'revolution', '革命', '颠覆']):
        return '彻底改变'
    elif any(kw in text for kw in ['improve', 'enhance', '改进', '提升']):
        return '大幅提升'
    elif any(kw in text for kw in ['new', 'launch', '发布', '推出']):
        return '带来新机会'
    else:
        return '产生重要影响'


def extract_company(topic):
    """提取公司名"""
    url = topic.get('url', '').lower()
    title = topic.get('title', '').lower()

    companies = {
        'OpenAI': ['openai'],
        'Anthropic': ['anthropic', 'claude'],
        'Google': ['google', 'deepmind'],
        'Meta': ['meta', 'facebook'],
        'Microsoft': ['microsoft'],
        '智谱AI': ['zhipu'],
        '百度': ['baidu'],
    }

    for company, keywords in companies.items():
        if any(kw in url or kw in title for kw in keywords):
            return company

    return 'AI公司'


def get_time_slot_type():
    """根据当前时间返回文章类型（扩展版 - 支持12种类型）"""
    import random
    hour = datetime.now().hour

    if 6 <= hour < 11:
        # 早上6-11点：AI工具实战类 + 资源整合类
        types = TIME_SLOT_CONTENT['morning']['types']
        selected_type = random.choice(types)
        return selected_type, 'morning'
    elif 11 <= hour < 16:
        # 中午11-16点：效率提升类 + 个人成长类
        types = TIME_SLOT_CONTENT['afternoon']['types']
        selected_type = random.choice(types)
        return selected_type, 'afternoon'
    else:
        # 晚上16点以后：创业方法论类 + 案例分析类
        types = TIME_SLOT_CONTENT['evening']['types']
        selected_type = random.choice(types)
        return selected_type, 'evening'


def generate_title(topic, content_type=None):
    """
    为话题生成标题（优化版 - 使用评分机制）

    Args:
        topic: 话题字典
        content_type: 内容类型

    Returns:
        生成的标题
    """
    if content_type is None:
        content_type, _ = get_time_slot_type()

    # 提取所有可能的信息（扩展版 - 支持新模板变量）
    time_ranges = extract_time_range(topic)
    level_ranges = extract_level_range(topic)
    state_ranges = extract_state_range(topic)

    info = {
        'tool_name': extract_tool_name(topic)[:15],  # 限制长度
        'benefit': extract_benefit(topic),
        'pain_point': extract_pain_point(topic),
        'number': extract_number(topic),
        'time': extract_time(topic),
        'action': get_action_keyword(topic),
        'goal': get_goal_keyword(topic),
        'tool': extract_tool_name(topic).split()[0] if extract_tool_name(topic) else 'AI',
        'event': extract_tool_name(topic),
        'target': extract_target_audience(topic),
        'impact': extract_impact(topic),
        'company': extract_company(topic),
        'industry': 'AI',
        # 新增变量（用于扩展模板）
        'cost': extract_cost(topic),
        'income': extract_income(topic),
        'achievement': extract_achievement(topic),
        'skill': get_skill_keyword(topic),
        'percent': extract_percent(topic),
        'concept': extract_concept(topic),
        'type': extract_template_type(topic),
        'long_time': time_ranges['long_time'],
        'short_time': time_ranges['short_time'],
        'level_a': level_ranges['level_a'],
        'level_b': level_ranges['level_b'],
        'state_a': state_ranges['state_a'],
        'state_b': state_ranges['state_b'],
    }

    # 选择模板
    templates = TITLE_TEMPLATES.get(content_type, TITLE_TEMPLATES['new_tool'])

    # 尝试填充每个模板，选择最合适的
    best_title = None
    best_score = 0

    for template in templates:
        try:
            title = template.format(**info)
            title = clean_title(title)

            # 评估标题质量
            score = evaluate_title_quality(title, info)

            if score > best_score:
                best_score = score
                best_title = title

        except (KeyError, IndexError):
            # 模板缺少某个变量，跳过
            continue

    # 如果所有模板都失败，返回后备标题
    if best_title is None:
        best_title = f"{info['tool_name']}：{info['benefit']}"

    return best_title


def evaluate_title_quality(title, info):
    """
    评估标题质量（简化版）

    Args:
        title: 生成的标题
        info: 提取的信息字典

    Returns:
        质量分数（0-100）
    """
    score = 50  # 基础分

    # 包含数字 +10
    if any(char.isdigit() for char in title):
        score += 10

    # 长度适中（15-30字）+10
    if 15 <= len(title) <= 30:
        score += 10
    elif len(title) < 15:
        score -= 5  # 太短扣分
    elif len(title) > 40:
        score -= 10  # 太长扣分

    # 包含具体工具名 +10
    if info.get('tool_name') and len(info['tool_name']) > 2:
        score += 10

    # 包含收益词 +10
    if any(kw in title for kw in ['效率', '节省', '简化', '提升', '增强', '降低']):
        score += 10

    # 包含行动词 +5
    if any(kw in title for kw in ['用', '实现', '搞定', '学会', '提升', '抓住']):
        score += 5

    return score


def get_action_keyword(topic):
    """提取动作关键词"""
    title = topic['title'].lower()
    if any(kw in title for kw in ['build', 'create', 'make', '搭建', '创建', '构建']):
        return '搭建AI应用'
    elif any(kw in title for kw in ['use', 'apply', '使用', '应用']):
        return '使用AI工具'
    elif any(kw in title for kw in ['deploy', '部署', 'deploy']):
        return '部署AI服务'
    else:
        return '实践AI开发'


def get_goal_keyword(topic):
    """提取目标关键词"""
    summary = topic.get('summary', '').lower()
    if any(kw in summary for kw in ['chatbot', 'assistant', '助手', '机器人']):
        return '智能助手'
    elif any(kw in summary for kw in ['agent', '代理']):
        return 'AI Agent'
    elif any(kw in summary for kw in ['automation', ' automate', '自动化']):
        return '工作流自动化'
    else:
        return 'AI项目'


def get_skill_keyword(topic):
    """提取技能关键词"""
    title = topic['title'].lower()
    if 'prompt' in title:
        return 'Prompt工程'
    elif 'llm' in title or 'language model' in title:
        return 'LLM开发'
    elif 'agent' in title:
        return 'AI Agent'
    else:
        return 'AI开发'


def extract_cost(topic):
    """提取成本/代价（用于避坑类标题）"""
    text = topic.get('title', '') + ' ' + topic.get('summary', '')
    # 查找金额
    import re
    amounts = re.findall(r'(\d+)万', text)
    if amounts:
        return f"{amounts[0]}万"
    return "10万"  # 默认值


def extract_income(topic):
    """提取收入（用于成功案例）"""
    return "5万"  # 默认值，可以根据实际情况调整


def extract_achievement(topic):
    """提取成就（用于成功案例）"""
    text = (topic.get('title', '') + ' ' + topic.get('summary', '')).lower()
    if any(kw in text for kw in ['user', 'subscriber', '用户', '订阅']):
        return "10万用户"
    elif any(kw in text for kw in ['revenue', 'income', '收入', '营收']):
        return "月入10万"
    else:
        return "盈利"


def extract_percent(topic):
    """提取百分比（用于好奇化标题）"""
    import re
    text = topic.get('title', '') + ' ' + topic.get('summary', '')
    # 查找百分比
    percents = re.findall(r'(\d+)%', text)
    if percents:
        return f"{percents[0]}%"
    # 默认使用常见的百分比
    return "90%"


def extract_concept(topic):
    """提取概念（用于好奇化标题）"""
    title = topic.get('title', '')
    # 提取核心概念
    if 'AI' in title or 'ai' in title.lower():
        return "AI应用"
    elif any(kw in title.lower() for kw in ['startup', 'business', '创业', '商业']):
        return "创业"
    else:
        return "这个概念"


def extract_time_range(topic):
    """提取时间范围（用于对比化标题）"""
    return {
        'long_time': '8小时',
        'short_time': '2小时',
        'time': '10分钟'
    }


def extract_level_range(topic):
    """提取能力等级范围（用于对比化标题）"""
    return {
        'level_a': '新手',
        'level_b': '高手'
    }


def extract_state_range(topic):
    """提取状态范围（用于对比化标题）"""
    text = (topic.get('title', '') + ' ' + topic.get('summary', '')).lower()
    if any(kw in text for kw in ['manual', 'hand', '手动']):
        return {'state_a': '手动操作', 'state_b': '自动化'}
    elif any(kw in text for kw in ['slow', 'inefficient', '缓慢', '低效']):
        return {'state_a': '低效', 'state_b': '高效'}
    else:
        return {'state_a': '0', 'state_b': '1'}


def extract_template_type(topic):
    """提取模板类型（用于模板分享类标题）"""
    text = (topic.get('title', '') + ' ' + topic.get('summary', '')).lower()
    if any(kw in text for kw in ['content', 'article', '内容', '文章']):
        return "内容创作"
    elif any(kw in text for kw in ['project', 'manage', '项目', '管理']):
        return "项目管理"
    elif any(kw in text for kw in ['workflow', '工作流']):
        return "工作流"
    else:
        return "AI开发"


def clean_title(title):
    """清理标题，确保符合规范"""
    # 移除多余空格
    title = re.sub(r'\s+', ' ', title)

    # 确保不超过长度限制（微信公众号64字节，约20个汉字）
    max_length = 30  # 留些余量
    if len(title.encode('utf-8')) > 64:
        # 按字节截断
        title = title.encode('utf-8')[:max_length].decode('utf-8', errors='ignore')
        title = title[:-1] + '…'

    # 移除标题党词汇
    clickbait_words = ['震惊！', '必看！', '惊呆了！', '不看后悔！']
    for word in clickbait_words:
        title = title.replace(word, '')

    return title.strip()


def validate_title(title):
    """验证标题质量"""
    issues = []

    # 检查长度
    if len(title.encode('utf-8')) > 64:
        issues.append("标题过长（超过64字节）")

    # 检查是否为空
    if not title:
        issues.append("标题为空")

    # 检查是否有实际内容
    if len(title) < 5:
        issues.append("标题过短")

    # 检查是否全是符号
    if not re.search(r'[\u4e00-\u9fa5a-zA-Z0-9]', title):
        issues.append("标题缺少实质内容")

    return len(issues) == 0, issues


# 针对不同时间段的内容类型建议（扩展版 - 按受众群体区分）
TIME_SLOT_CONTENT = {
    'morning': {  # 8:00 - AI小白/初学者
        'types': ['tutorial', 'new_tool'],
        'description': 'AI入门教程和工具介绍',
        'focus': '零基础入门，简单易懂的教程',
        'target_audience': 'AI小白、初学者',
        'keywords': [
            # 入门相关
            'beginner', 'tutorial', 'introduction', 'getting started',
            'basics', 'fundamentals', 'guide', 'learn',
            '入门', '教程', '基础', '新手', '小白', '学习', '指南',
            # 简单工具
            'easy', 'simple', 'quick', 'step-by-step',
            '简单', '快速', '一步步', '零基础',
            # 概念解释
            'what is', 'how to', 'explained', 'understanding',
            '什么是', '如何', '理解', '解释'
        ]
    },
    'afternoon': {  # 12:00 - 传统程序员/AI开发者
        'types': ['tutorial', 'new_tool'],
        'description': '技术实战和开发工具',
        'focus': '代码示例、API使用、实战案例',
        'target_audience': '传统程序员、AI开发者',
        'keywords': [
            # 技术实战
            'code', 'api', 'implementation', 'development', 'programming',
            'deploy', 'build', 'integrate', 'example',
            '代码', '实现', '开发', '部署', '集成', '示例',
            # 工具框架
            'framework', 'library', 'sdk', 'tool', 'platform',
            '框架', '库', '工具', '平台', 'SDK',
            # 技术栈
            'python', 'javascript', 'react', 'node', 'docker',
            'langchain', 'huggingface', 'openai', 'pytorch', 'tensorflow',
            # 实战类
            'hands-on', 'practice', 'project', 'demo',
            '实战', '项目', '演示', '实践'
        ]
    },
    'evening': {  # 18:00 - AI创业者/产品经理/一人公司
        'types': ['industry_news', 'tutorial'],
        'description': '商业案例和产品应用',
        'focus': '成功案例、商业模式、产品设计',
        'target_audience': 'AI创业者、产品经理、一人公司',
        'keywords': [
            # 商业相关
            'business', 'startup', 'revenue', 'monetize', 'product',
            'case study', 'success', 'growth', 'strategy',
            '商业', '创业', '产品', '案例', '成功', '增长', '策略',
            # 应用场景
            'application', 'use case', 'solution', 'workflow',
            '应用', '场景', '解决方案', '工作流',
            # 结果导向
            'result', 'impact', 'achievement', 'profit', 'income',
            '结果', '效果', '收益', '月入', '赚钱',
            # 创业相关
            'entrepreneur', 'solo', 'indie', 'maker',
            '创业者', '一人公司', '独立开发', '个人'
        ]
    }
}


if __name__ == '__main__':
    # 测试标题生成
    test_topic = {
        'title': 'OpenAI releases new o3 model with improved reasoning',
        'url': 'https://openai.com/blog/o3',
        'summary': 'The new model features advanced reasoning capabilities and better performance on complex tasks.',
        'source': 'OpenAI Blog'
    }

    # 测试不同类型的标题
    print("=== 标题生成测试 ===\n")

    for content_type in ['new_tool', 'tutorial', 'industry_news', 'tips']:
        title = generate_title(test_topic, content_type)
        valid, issues = validate_title(title)
        print(f"[{content_type}] {title}")
        print(f"  验证: {'✅ 通过' if valid else '❌ ' + ', '.join(issues)}")
        print(f"  长度: {len(title.encode('utf-8'))} 字节\n")

    # 测试时间段策略
    print("=== 时间段策略 ===\n")
    for hour in [8, 12, 18]:
        test_datetime = datetime.now().replace(hour=hour)
        print(f"{hour}:00 -> ", end="")
        # 模拟时间段判断
        if 6 <= hour < 11:
            print(f"早晨时段: 新工具介绍")
        elif 11 <= hour < 16:
            print(f"中午时段: 实战教程")
        else:
            print(f"晚上时段: 行业动态")
