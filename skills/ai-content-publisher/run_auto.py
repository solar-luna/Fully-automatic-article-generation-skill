#!/usr/bin/env python3
"""
AI内容自动发布主脚本
串联所有步骤：获取热点 → 选择选题 → 生成标题 → 生成文章 → 格式化 → 发布
"""

import os
import sys
import json
import subprocess
from datetime import datetime

# 添加技能路径
script_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.append(os.path.join(script_dir, 'scripts'))
from title_generator import generate_title, get_time_slot_type, TIME_SLOT_CONTENT


def run_step(description, command):
    """运行一个步骤并处理错误"""
    print(f"\n{'='*60}")
    print(f"【{description}】")
    print(f"{'='*60}")

    try:
        result = subprocess.run(
            command,
            shell=True,
            capture_output=True,
            text=True,
            timeout=300  # 5分钟超时
        )

        if result.returncode != 0:
            print(f"❌ 失败: {result.stderr}")
            return False

        print(f"✅ 成功")
        if result.stdout:
            print(result.stdout[:500])  # 只显示前500字符
        return True

    except subprocess.TimeoutExpired:
        print("❌ 超时（5分钟）")
        return False
    except Exception as e:
        print(f"❌ 错误: {e}")
        return False


def main():
    """主流程"""
    print("="*60)
    print("AI内容自动发布系统")
    print("="*60)

    # 获取当前时间和目标类型
    target_type, time_slot = get_time_slot_type()
    time_info = TIME_SLOT_CONTENT[time_slot]

    print(f"\n📅 当前时间: {datetime.now().strftime('%Y-%m-%d %H:%M')}")
    print(f"⏰ 时段: {time_slot}")
    print(f"📝 内容类型: {time_info['description']}")
    print(f"🎯 目标读者: {time_info['target_audience']}")

    script_dir = os.path.dirname(os.path.abspath(__file__))
    cache_dir = os.path.join(script_dir, 'cache')
    os.makedirs(cache_dir, exist_ok=True)

    # 步骤1: 获取热点
    if not run_step("步骤1: 获取热点", f"cd {script_dir} && python3 scripts/fetch_hotspots.py"):
        return False

    # 步骤2: 选择选题
    if not run_step("步骤2: 智能选题", f"cd {script_dir} && python3 scripts/selector.py"):
        return False

    # 读取选中的话题
    topic_file = os.path.join(cache_dir, 'selected_topic.json')
    if not os.path.exists(topic_file):
        print(f"❌ 选题文件不存在: {topic_file}")
        return False

    with open(topic_file, 'r') as f:
        topic = json.load(f)

    print(f"\n📌 选定话题: {topic['title']}")
    print(f"🔗 来源: {topic['source']}")

    # 生成标题
    generated_title = generate_title(topic, target_type)
    print(f"\n📰 生成标题: {generated_title}")

    # 保存标题到话题中
    topic['generated_title'] = generated_title

    # 步骤3-6: 文章生成、格式化、发布
    # 注意：这些步骤需要实际的实现
    # 当前我们只有框架，实际的AI内容生成需要Claude参与

    print(f"\n{'='*60}")
    print("⚠️ 注意事项")
    print(f"{'='*60}")
    print("当前脚本完成了热点获取和选题。")
    print("实际的AI内容生成需要调用Claude，")
    print("建议手动触发: claude skill ai-content-publisher")
    print("或者等待完整的自动化脚本实现。")

    return True


if __name__ == '__main__':
    success = main()
    sys.exit(0 if success else 1)
