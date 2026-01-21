#!/usr/bin/env python3
"""
选题策略脚本（优化版）
根据时间段选择最佳选题，每次只选1篇
"""

import json
import os
import sys
import re
import time
import yaml
from datetime import datetime

# Add scripts directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from title_generator import get_time_slot_type, TIME_SLOT_CONTENT


# 排除关键词黑名单
EXCLUDE_KEYWORDS = [
    # 融资类
    '融资', '融资轮', 'A轮', 'B轮', 'C轮', 'IPO', '上市', '估值', '市值',
    '投资', '募资', '资金', '投资人',
    # 企业动态
    '裁员', '人事变动', '高管离职', '财报', '季度收入', '营收',
    # 纯商业新闻
    '战略合作', '收购', '并购',
    # 非AI相关（新增）
    'dietary', 'diet', 'food', 'nutrition', 'health', 'vaccine', 'medical',
    '饮食', '膳食', '食品', '营养', '健康', '疫苗', '医疗',
]

# AI相关关键词（必须包含至少一个）
AI_KEYWORDS = [
    # 英文
    'ai', 'artificial intelligence', 'machine learning', 'ml', 'deep learning',
    'neural network', 'llm', 'large language model', 'gpt', 'claude', 'chatgpt',
    'generative ai', 'gen ai', 'transformer', 'diffusion', 'stable diffusion',
    'openai', 'anthropic', 'deepmind', 'hugging face', 'langchain',
    'prompt', 'embedding', 'vector', 'rag', 'fine-tuning', 'training',
    'inference', 'model', 'algorithm', 'computer vision', 'nlp',
    'natural language processing', 'reinforcement learning', 'agent',
    # 中文
    '人工智能', '机器学习', '深度学习', '神经网络', '大模型', '语言模型',
    '生成式', 'AI', '智能', '算法', '模型训练', '微调', '推理',
    '提示词', '向量', '嵌入', '计算机视觉', '自然语言', '强化学习', '智能体',
]

# 内容类型识别规则
CONTENT_TYPE_RULES = {
    'new_tool': {
        'keywords': ['发布', '推出', '开源', '新工具', '新模型', 'new model', 'release', 'launch'],
        'sources': ['github.com', 'huggingface.co', 'openai.com', 'anthropic.com'],
        'priority': 'high'
    },
    'tutorial': {
        'keywords': ['教程', '技巧', '如何', '实战', '指南', '入门', 'tutorial', 'guide', 'how to'],
        'sources': ['medium.com', 'dev.to'],
        'priority': 'medium'
    },
    'industry_news': {
        'keywords': ['报告', '研究', '分析', '趋势', 'report', 'research', 'analysis'],
        'sources': ['theverge.com', 'techcrunch.com', 'venturebeat.com'],
        'priority': 'low'
    }
}


def load_content_types():
    """加载内容类型配置"""
    script_dir = os.path.dirname(os.path.abspath(__file__))
    config_path = os.path.join(os.path.dirname(script_dir), 'config', 'content_types.yaml')

    try:
        with open(config_path, 'r', encoding='utf-8') as f:
            return yaml.safe_load(f)
    except FileNotFoundError:
        print(f"内容类型配置文件不存在: {config_path}")
        return {}


def load_hotspots(cache_path=None):
    """加载热点缓存"""
    if cache_path is None:
        script_dir = os.path.dirname(os.path.abspath(__file__))
        cache_dir = os.path.join(os.path.dirname(script_dir), 'cache')
        cache_path = os.path.join(cache_dir, 'hotspots.json')

    try:
        with open(cache_path, 'r', encoding='utf-8') as f:
            return json.load(f)
    except FileNotFoundError:
        print(f"热点缓存文件不存在: {cache_path}")
        print("请先运行 fetch_hotspots.py 获取热点")
        sys.exit(1)


def is_excluded(topic):
    """检查是否应该排除该话题"""
    title = topic['title'].lower()
    summary = topic.get('summary', '').lower()
    combined = title + ' ' + summary

    # 检查排除关键词
    for keyword in EXCLUDE_KEYWORDS:
        if keyword.lower() in combined:
            return True

    return False


def is_ai_related(topic):
    """检查话题是否与AI相关（必须包含AI关键词）"""
    title = topic['title'].lower()
    summary = topic.get('summary', '').lower()
    url = topic['url'].lower()
    combined = title + ' ' + summary + ' ' + url

    # 必须包含至少一个AI关键词
    for keyword in AI_KEYWORDS:
        if keyword.lower() in combined:
            return True

    return False


def score_topic_by_type(topic, target_type):
    """
    根据目标类型对话题进行评分

    Args:
        topic: 话题字典
        target_type: 目标内容类型 (new_tool/tutorial/industry_news)

    Returns:
        (score, reasons)
    """
    score = 0
    reasons = []

    title = topic['title'].lower()
    summary = topic.get('summary', '').lower()
    url = topic['url'].lower()
    combined = title + ' ' + summary

    # 1. 类型匹配度 (30分)
    type_keywords = {
        'new_tool': ['发布', '推出', '开源', 'new', 'release', 'launch', 'announce'],
        'tutorial': ['教程', '技巧', '如何', '实战', 'guide', 'tutorial', 'how to', 'step'],
        'industry_news': ['报告', '研究', '分析', '趋势', 'report', 'research', 'analysis']
    }

    for kw in type_keywords.get(target_type, []):
        if kw in combined:
            score += 30
            reasons.append(f"匹配{target_type}类型")
            break

    # 2. 技术深度 (25分)
    if any(kw in combined for kw in ['代码', 'code', 'api', '示例', 'example']):
        score += 25
        reasons.append("有技术内容")
    elif any(kw in combined for kw in ['技术', 'technical', '算法', 'algorithm', '模型', 'model']):
        score += 18
        reasons.append("有技术细节")

    # 3. 新颖性 (20分)
    for kw in ['发布', '推出', '开源', 'new', 'release', 'launch']:
        if kw in title:
            score += 20
            reasons.append("最新发布")
            break

    # 4. 基础实用性 (15分)
    if any(kw in combined for kw in ['应用', 'application', '案例', 'use case', '如何', 'how']):
        score += 15
        reasons.append("有应用场景")
    elif any(kw in combined for kw in ['工具', 'tool', '框架', 'framework', '库', 'library']):
        score += 10
        reasons.append("实用工具")

    # 5. 来源权威性 (10分)
    authoritative_sources = [
        'openai.com', 'anthropic.com', 'deepmind.com', 'ai.meta.com',
        'huggingface.co', 'arxiv.org', 'github.com'
    ]
    for source in authoritative_sources:
        if source in url:
            score += 10
            reasons.append(f"权威来源")
            break

    # 6. 实用性加分 (新增，最多+20分)
    practicality_score, prac_reasons = score_practicality(topic)
    score += practicality_score
    reasons.extend(prac_reasons)

    return score, reasons


def score_practicality(topic):
    """
    评估话题的实用性（读者能直接用）

    Returns:
        (score, reasons) - 分数和原因列表
    """
    score = 0
    reasons = []

    title = topic['title'].lower()
    summary = topic.get('summary', '').lower()
    url = topic['url'].lower()
    combined = title + ' ' + summary

    # 优先：开源工具/代码库（+15分）
    if 'github.com' in url:
        score += 15
        reasons.append("开源可用")

        # GitHub stars加分
        stars = topic.get('stars', 0)
        if stars > 1000:
            score += 5
            reasons.append(f"高人气({stars}+ stars)")

    # 优先：有教程/示例（+10分）
    if any(kw in combined for kw in ['tutorial', 'guide', 'how to', '教程', '实战', '示例']):
        score += 10
        reasons.append("有教程")

    # 优先：免费工具（+5分）
    if any(kw in combined for kw in ['free', 'open source', '免费', '开源']):
        score += 5
        reasons.append("免费")

    # 降低：纯理论/研究（-10分）
    if any(kw in combined for kw in ['research', 'paper', 'study', '研究', '论文']) and \
       not any(kw in combined for kw in ['code', 'implementation', '实现', '代码']):
        score -= 10
        reasons.append("纯理论(降低)")

    # 降低：企业内部工具（-15分）
    if any(kw in combined for kw in ['internal', 'enterprise only', '企业内部', '仅限企业']):
        score -= 15
        reasons.append("不可公开使用(降低)")

    return score, reasons


def calculate_type_match_score(topic, target_type, content_types_config):
    """
    计算内容类型匹配度（30分）

    Args:
        topic: 话题字典
        target_type: 目标内容类型
        content_types_config: 内容类型配置

    Returns:
        (score, reasons)
    """
    score = 0
    reasons = []

    title = topic['title'].lower()
    summary = topic.get('summary', '').lower()
    combined = title + ' ' + summary

    # 获取目标类型的关键词
    if target_type in content_types_config:
        keywords = content_types_config[target_type].get('keywords', [])

        # 计算匹配的关键词数量
        matched_keywords = sum(1 for kw in keywords if kw.lower() in combined)

        if matched_keywords >= 3:
            score = 30
            reasons.append(f"高度匹配{target_type}类型({matched_keywords}个关键词)")
        elif matched_keywords >= 2:
            score = 20
            reasons.append(f"匹配{target_type}类型({matched_keywords}个关键词)")
        elif matched_keywords >= 1:
            score = 10
            reasons.append(f"部分匹配{target_type}类型")
        else:
            # 即使没有匹配关键词，也给基础分（AI相关内容）
            score = 8
            reasons.append(f"AI相关内容（基础分）")

    return score, reasons


def calculate_timeliness_score(topic):
    """
    计算时效性分（20分）
    发布时间越近分数越高

    Args:
        topic: 话题字典

    Returns:
        (score, reasons)
    """
    score = 0
    reasons = []

    published_date = topic.get('published_date')
    if not published_date:
        # 提高无时间戳内容的默认分（从10分提高到12分）
        return 12, ["无发布时间(默认12分)"]

    try:
        # 计算距离现在的小时数
        from datetime import datetime
        pub_time = datetime.fromisoformat(published_date.replace('Z', '+00:00'))
        now = datetime.now(pub_time.tzinfo)
        hours_ago = (now - pub_time).total_seconds() / 3600

        if hours_ago <= 24:
            score = 20
            reasons.append("24小时内发布")
        elif hours_ago <= 48:
            score = 15
            reasons.append("48小时内发布")
        elif hours_ago <= 72:
            score = 10
            reasons.append("72小时内发布")
        else:
            score = 5
            reasons.append("超过72小时")
    except:
        score = 12
        reasons.append("时间解析失败(默认12分)")

    return score, reasons


def calculate_quality_score(topic):
    """
    计算基础质量分（30分）
    标题完整性、描述清晰度、来源可靠性

    Args:
        topic: 话题字典

    Returns:
        (score, reasons)
    """
    score = 0
    reasons = []

    title = topic.get('title', '')
    summary = topic.get('summary', '')
    url = topic.get('url', '')

    # 1. 标题完整性（10分）
    if len(title) >= 20 and len(title) <= 200:
        score += 10
        reasons.append("标题长度适中")
    elif len(title) >= 10:
        score += 5
        reasons.append("标题较短")

    # 2. 描述清晰度（10分）
    if len(summary) >= 50:
        score += 10
        reasons.append("描述详细")
    elif len(summary) >= 20:
        score += 5
        reasons.append("描述简短")

    # 3. 来源可靠性（10分）
    authoritative_sources = [
        'openai.com', 'anthropic.com', 'deepmind.com', 'ai.meta.com',
        'huggingface.co', 'arxiv.org', 'github.com', 'microsoft.com',
        'google.com', 'nvidia.com'
    ]
    for source in authoritative_sources:
        if source in url.lower():
            score += 10
            reasons.append("权威来源")
            break
    else:
        score += 5
        reasons.append("一般来源")

    return score, reasons


def calculate_audience_relevance_score(topic):
    """
    计算受众相关性（20分）
    与目标受众痛点的相关性

    Args:
        topic: 话题字典

    Returns:
        (score, reasons)
    """
    score = 0
    reasons = []

    title = topic['title'].lower()
    summary = topic.get('summary', '').lower()
    combined = title + ' ' + summary

    # 受众痛点关键词
    pain_point_keywords = {
        '效率': ['efficiency', 'productivity', 'fast', 'quick', '效率', '快速', '提速'],
        '成本': ['free', 'cost', 'cheap', '免费', '低成本', '省钱'],
        '易用': ['easy', 'simple', 'beginner', '简单', '入门', '新手'],
        '实用': ['practical', 'useful', 'application', '实用', '应用', '落地'],
    }

    matched_pain_points = []
    for pain_point, keywords in pain_point_keywords.items():
        if any(kw in combined for kw in keywords):
            matched_pain_points.append(pain_point)

    if len(matched_pain_points) >= 2:
        score = 20
        reasons.append(f"高度相关({','.join(matched_pain_points)})")
    elif len(matched_pain_points) >= 1:
        score = 15
        reasons.append(f"相关({','.join(matched_pain_points)})")
    else:
        score = 10
        reasons.append("一般相关")

    return score, reasons


def score_with_time_slot_keywords(topic, time_slot_keywords):
    """
    根据时间段关键词打分（新增20分维度）

    Args:
        topic: 话题字典
        time_slot_keywords: 当前时间段的关键词列表

    Returns:
        (score, reasons)
    """
    score = 0
    reasons = []

    title = topic['title'].lower()
    summary = topic.get('summary', '').lower()
    combined = title + ' ' + summary

    # 计算匹配的关键词数量
    matched_count = sum(1 for kw in time_slot_keywords if kw.lower() in combined)

    if matched_count >= 5:
        score = 20
        reasons.append(f"高度匹配时间段({matched_count}个关键词)")
    elif matched_count >= 3:
        score = 15
        reasons.append(f"匹配时间段({matched_count}个关键词)")
    elif matched_count >= 1:
        score = 10
        reasons.append(f"部分匹配时间段")
    else:
        score = 0
        reasons.append("不匹配时间段")

    return score, reasons


def score_topic_enhanced(topic, target_type, content_types_config):
    """
    增强版话题评分（4维度评分系统）

    评分维度：
    1. 基础质量分（30分）：标题完整性、描述清晰度、来源可靠性
    2. 时效性分（20分）：发布时间越近分数越高
    3. 内容类型匹配度（30分）：与当前时间段目标类型的匹配程度
    4. 受众相关性（20分）：与目标受众痛点的相关性

    额外加分：
    - 权威来源（OpenAI/Anthropic/DeepMind等）：+5分

    Args:
        topic: 话题字典
        target_type: 目标内容类型
        content_types_config: 内容类型配置

    Returns:
        (total_score, detailed_reasons)
    """
    total_score = 0
    all_reasons = []

    # 1. 基础质量分（30分）
    quality_score, quality_reasons = calculate_quality_score(topic)
    total_score += quality_score
    all_reasons.append(f"基础质量: {quality_score}/30 - {', '.join(quality_reasons)}")

    # 2. 时效性分（20分）
    time_score, time_reasons = calculate_timeliness_score(topic)
    total_score += time_score
    all_reasons.append(f"时效性: {time_score}/20 - {', '.join(time_reasons)}")

    # 3. 内容类型匹配度（30分）
    type_score, type_reasons = calculate_type_match_score(topic, target_type, content_types_config)
    total_score += type_score
    all_reasons.append(f"类型匹配: {type_score}/30 - {', '.join(type_reasons)}")

    # 4. 受众相关性（20分）
    audience_score, audience_reasons = calculate_audience_relevance_score(topic)
    total_score += audience_score
    all_reasons.append(f"受众相关: {audience_score}/20 - {', '.join(audience_reasons)}")

    # 额外加分：顶级权威来源（+5分）
    url = topic.get('url', '').lower()
    top_sources = ['openai.com', 'anthropic.com', 'deepmind.com', 'ai.meta.com']
    if any(source in url for source in top_sources):
        total_score += 5
        all_reasons.append("额外加分: +5 - 顶级权威来源")

    return total_score, all_reasons


def enforce_diversity(sorted_topics, history):
    """
    确保内容类型多样化
    避免连续多天发布同一类型内容

    Args:
        sorted_topics: 已排序的话题列表
        history: 历史发布记录

    Returns:
        调整后的话题列表
    """
    if not history or len(history) < 3:
        return sorted_topics

    # 统计最近9条记录的内容类型（假设每天3篇）
    recent_types = [r.get('content_type', '') for r in history[-9:]]

    # 计数每种类型出现次数
    type_counts = {}
    for t in recent_types:
        if t:
            type_counts[t] = type_counts.get(t, 0) + 1

    # 如果某个类型出现>5次，降低该类型的优先级
    adjusted = False
    for topic in sorted_topics:
        topic_type = topic.get('content_type', '')
        if type_counts.get(topic_type, 0) >= 5:
            topic['score'] -= 20
            adjusted = True
            print(f"⚖️  '{topic_type}'最近发布过多（{type_counts[topic_type]}次），降低优先级")

    if adjusted:
        # 重新排序
        sorted_topics.sort(key=lambda x: x['score'], reverse=True)
        print("📊 已调整排序以增加内容多样性")

    return sorted_topics


def extract_keywords(topic):
    """从话题中提取关键词集合"""
    text = (topic.get('title', '') + ' ' + topic.get('summary', '')).lower()

    # 移除停用词
    stopwords = {'the', 'a', 'an', 'and', 'or', 'but', 'in', 'on', 'at', 'to', 'for',
                 'of', 'with', 'by', 'from', 'is', 'are', 'was', 'were',
                 '的', '了', '和', '与', '或', '但是', '在', '为', '用'}

    # 分词（简单的空格分割 + 标点符号处理）
    words = re.findall(r'\b\w+\b', text)

    # 过滤停用词和短词
    keywords = {w for w in words if len(w) > 2 and w not in stopwords}

    return keywords


def calculate_similarity(topic1, topic2):
    """
    计算两个话题的相似度（0-1之间）
    使用Jaccard相似度算法
    """
    # 1. 提取关键词集合
    keywords1 = extract_keywords(topic1)
    keywords2 = extract_keywords(topic2)

    # 2. Jaccard相似度 = 交集 / 并集
    intersection = keywords1 & keywords2
    union = keywords1 | keywords2

    if not union:
        return 0.0

    similarity = len(intersection) / len(union)

    # 3. 如果URL完全相同，直接返回1.0
    if topic1.get('url') == topic2.get('url'):
        return 1.0

    return similarity


def load_publish_history(hours=48):
    """
    加载发布历史记录

    Args:
        hours: 加载最近N小时内的记录（默认48小时）

    Returns:
        历史记录列表
    """
    script_dir = os.path.dirname(os.path.abspath(__file__))
    cache_dir = os.path.join(os.path.dirname(script_dir), 'cache')
    history_file = os.path.join(cache_dir, 'publish_history.json')

    if not os.path.exists(history_file):
        print(f"📝 历史记录文件不存在，将创建新文件")
        return []

    try:
        with open(history_file, 'r', encoding='utf-8') as f:
            data = json.load(f)

        if 'records' not in data:
            print(f"⚠️  历史记录格式错误，返回空列表")
            return []

        # 过滤出最近N小时内的记录
        cutoff = time.time() - (hours * 3600)
        recent_records = [
            r for r in data['records']
            if r.get('timestamp', 0) > cutoff
        ]

        print(f"📊 加载了 {len(recent_records)} 条历史记录（最近{hours}小时）")
        return recent_records

    except json.JSONDecodeError as e:
        print(f"⚠️  历史记录JSON解析失败: {e}")
        return []
    except Exception as e:
        print(f"⚠️  加载历史记录失败: {e}")
        return []


def select_non_duplicate_topic(sorted_topics, history, similarity_threshold=0.7):
    """
    从排序后的话题列表中选择第一个不重复的话题

    Args:
        sorted_topics: 按评分降序排列的话题列表
        history: 最近的发布历史
        similarity_threshold: 相似度阈值（默认0.7）

    Returns:
        选中的话题，如果全部重复则返回None
    """
    print(f"\n=== 去重检查 ===")
    print(f"候选话题数: {len(sorted_topics)}")
    print(f"历史记录数: {len(history)}")
    print(f"相似度阈值: {similarity_threshold}")

    if not history:
        print("✅ 无历史记录，直接选择第一个话题")
        return sorted_topics[0] if sorted_topics else None

    for i, topic in enumerate(sorted_topics):
        # 检查是否与历史记录重复
        is_duplicate = False
        max_similarity = 0.0
        duplicate_with = None

        for historical in history:
            similarity = calculate_similarity(topic, historical)

            if similarity > max_similarity:
                max_similarity = similarity
                duplicate_with = historical.get('title', 'Unknown')

            if similarity >= similarity_threshold:
                is_duplicate = True
                break

        if not is_duplicate:
            print(f"✅ 选中第 {i+1} 个话题（最高相似度: {max_similarity:.2f}）")
            print(f"   标题: {topic['title'][:50]}...")
            return topic
        else:
            print(f"⚠️  第 {i+1} 个话题重复")
            print(f"   标题: {topic['title'][:50]}...")
            print(f"   与 '{duplicate_with[:30]}...' 相似度: {max_similarity:.2f}")

    # 所有话题都重复
    print(f"❌ 前 {len(sorted_topics)} 个话题全部重复，本次放弃发布")
    return None


def select_single_topic(hotspots):
    """
    选择单个最佳选题

    根据当前时间段确定目标类型，然后选择最匹配的高分话题
    """
    # 加载内容类型配置
    content_types_config = load_content_types()

    # 获取当前时间段和目标类型
    target_type, time_slot = get_time_slot_type()
    time_info = TIME_SLOT_CONTENT[time_slot]
    time_keywords = time_info.get('keywords', [])  # 新增：获取时间段关键词

    print(f"\n=== 时间段策略 ===")
    print(f"当前时间: {datetime.now().strftime('%H:%M')}")
    print(f"时段: {time_slot}")
    print(f"目标类型: {time_info['description']}")
    print(f"内容重点: {time_info['focus']}")
    print(f"目标读者: {time_info['target_audience']}")
    print(f"匹配关键词数: {len(time_keywords)}")

    # 过滤排除的话题和非AI相关话题
    filtered = []
    excluded_count = 0
    non_ai_count = 0
    for topic in hotspots:
        if is_excluded(topic):
            excluded_count += 1
            continue
        if not is_ai_related(topic):
            non_ai_count += 1
            continue
        filtered.append(topic)

    print(f"\n过滤了 {excluded_count} 个无用话题")
    print(f"过滤了 {non_ai_count} 个非AI相关话题")
    print(f"剩余候选: {len(filtered)} 个")

    if not filtered:
        print("❌ 没有可用的话题")
        return None

    # 评分并排序（使用增强版4维度评分系统 + 时间段关键词匹配）
    for topic in filtered:
        # 原有的4维度评分
        base_score, base_reasons = score_topic_enhanced(topic, target_type, content_types_config)

        # 新增：时间段关键词匹配（20分）
        time_score, time_reasons = score_with_time_slot_keywords(topic, time_keywords)

        topic['score'] = base_score + time_score
        topic['score_reasons'] = base_reasons + time_reasons
        topic['content_type'] = target_type

    # 按分数排序
    filtered.sort(key=lambda x: x['score'], reverse=True)

    # 加载历史记录并检查重复
    history = load_publish_history(hours=48)

    # 强制多样性（如果某类型最近发布过多，降低其优先级）
    filtered = enforce_diversity(filtered, history)

    # 选择第一个不重复的话题（检查前10个）
    selected = select_non_duplicate_topic(filtered[:10], history, similarity_threshold=0.7)

    if selected is None:
        print("\n❌ 所有候选话题均与近期发布重复，放弃本次发布")
        return None

    print(f"\n=== 选定选题 ===")
    print(f"标题: {selected['title']}")
    print(f"来源: {selected['source']}")
    print(f"评分: {selected['score']}")
    print(f"原因: {', '.join(selected['score_reasons'])}")
    print(f"URL: {selected['url']}")

    return selected


def classify_topic(topic):
    """识别话题类型"""
    title = topic['title'].lower()
    url = topic['url'].lower()

    scores = {}
    for type_name, rules in CONTENT_TYPE_RULES.items():
        score = 0

        # 关键词匹配
        for kw in rules['keywords']:
            if kw.lower() in title:
                score += 1

        # 来源匹配
        for source in rules['sources']:
            if source in url:
                score += 2

        scores[type_name] = score

    # 返回得分最高的类型
    if max(scores.values()) == 0:
        return 'industry_news'  # 默认类型

    return max(scores, key=scores.get)


def score_topic(topic):
    """对话题进行实用性评分"""
    score = 0
    reasons = []

    # 1. 技术深度 (30分)
    summary = topic.get('summary', '').lower()
    title = topic['title'].lower()

    if any(kw in title + summary for kw in ['代码', 'code', 'api', '教程', 'tutorial']):
        score += 30
        reasons.append("包含技术内容")
    elif any(kw in title + summary for kw in ['技术', 'technical', '算法', 'algorithm']):
        score += 20
        reasons.append("包含技术细节")
    else:
        score += 10

    # 2. 新颖性 (25分)
    found_new = False
    for kw in ['发布', '推出', '开源', 'new', 'release', 'launch']:
        if kw in title:
            score += 25
            reasons.append("新发布/开源")
            found_new = True
            break

    if not found_new and any(kw in title for kw in ['更新', 'update', '升级', 'upgrade']):
        score += 18
        reasons.append("重要更新")

    # 3. 实用性 (25分)
    if any(kw in title + summary for kw in ['应用', 'application', '案例', 'example', '如何', 'how to']):
        score += 25
        reasons.append("有应用案例")
    elif any(kw in title + summary for kw in ['工具', 'tool', '框架', 'framework', '库', 'library']):
        score += 20
        reasons.append("实用工具")

    # 4. 热度 (20分)
    if topic.get('type') == 'github':
        stars = topic.get('stars', 0)
        if stars > 1000:
            score += 20
            reasons.append(f"GitHub {stars}+ stars")
        elif stars > 100:
            score += 14
            reasons.append(f"GitHub {stars}+ stars")
    else:
        score += 10

    return score, reasons



def save_selected_topic(topic, output_path=None):
    """保存选中的话题"""
    if topic is None:
        return None

    if output_path is None:
        script_dir = os.path.dirname(os.path.abspath(__file__))
        cache_dir = os.path.join(os.path.dirname(script_dir), 'cache')
        os.makedirs(cache_dir, exist_ok=True)
        output_path = os.path.join(cache_dir, 'selected_topic.json')

    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(topic, f, ensure_ascii=False, indent=2)

    print(f"\n✅ 选题已保存: {output_path}")
    return output_path


if __name__ == '__main__':
    # 加载热点
    hotspots = load_hotspots()

    # 选择单个选题（根据时间段自动判断类型）
    selected = select_single_topic(hotspots)

    # 保存
    if selected:
        save_selected_topic(selected)
