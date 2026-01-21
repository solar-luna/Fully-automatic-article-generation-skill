#!/usr/bin/env python3
"""
更新发布历史记录脚本
将本次生成的文章信息写入历史数据库，并自动清理过期记录
"""

import json
import os
import sys
import time
import re
from datetime import datetime


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


def update_history(topic, title, published=True):
    """
    更新发布历史

    Args:
        topic: 选中的话题字典
        title: 生成的标题
        published: 是否已发布
    """
    # 获取脚本所在目录
    script_dir = os.path.dirname(os.path.abspath(__file__))
    cache_dir = os.path.join(os.path.dirname(script_dir), 'cache')
    history_file = os.path.join(cache_dir, 'publish_history.json')

    # 确保cache目录存在
    os.makedirs(cache_dir, exist_ok=True)

    # 初始化或加载历史文件
    if not os.path.exists(history_file):
        data = {'records': []}
        print(f"✅ 创建新的历史记录文件: {history_file}")
    else:
        try:
            with open(history_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
            if 'records' not in data:
                data = {'records': []}
        except (json.JSONDecodeError, Exception) as e:
            print(f"⚠️  历史记录文件损坏，重新初始化: {e}")
            data = {'records': []}

    # 提取关键词
    keywords = list(extract_keywords(topic))

    # 创建新记录
    record = {
        'date': datetime.now().strftime('%Y-%m-%d'),
        'time': datetime.now().strftime('%H:%M'),
        'timestamp': int(time.time()),
        'title': title,
        'url': topic.get('url', ''),
        'summary': topic.get('summary', ''),
        'content_type': topic.get('content_type', 'unknown'),
        'keywords': keywords,
        'published': published
    }

    # 添加记录
    data['records'].append(record)
    print(f"✅ 添加记录: {title}")

    # 自动清理7天前的记录
    cutoff = time.time() - (7 * 24 * 3600)
    original_count = len(data['records'])
    data['records'] = [r for r in data['records'] if r.get('timestamp', 0) > cutoff]
    cleaned_count = original_count - len(data['records'])

    if cleaned_count > 0:
        print(f"🧹 清理了 {cleaned_count} 条过期记录（>7天）")

    # 保存
    try:
        with open(history_file, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
        print(f"✅ 历史记录已更新: {history_file}")
        print(f"📊 当前历史记录总数: {len(data['records'])}")
    except Exception as e:
        print(f"❌ 保存历史记录失败: {e}")
        sys.exit(1)


def main():
    """主函数"""
    # 检查命令行参数
    if len(sys.argv) < 3:
        print("用法: update_history.py <selected_topic.json> <生成的标题>")
        print("示例: update_history.py cache/selected_topic.json 'Claude 3.5来了！提高效率效率提升3倍'")
        sys.exit(1)

    topic_file = sys.argv[1]
    title = sys.argv[2]

    # 检查topic文件是否存在
    if not os.path.exists(topic_file):
        print(f"❌ 话题文件不存在: {topic_file}")
        sys.exit(1)

    # 读取话题
    try:
        with open(topic_file, 'r', encoding='utf-8') as f:
            topic = json.load(f)
    except Exception as e:
        print(f"❌ 读取话题文件失败: {e}")
        sys.exit(1)

    # 更新历史
    update_history(topic, title)


if __name__ == '__main__':
    main()
