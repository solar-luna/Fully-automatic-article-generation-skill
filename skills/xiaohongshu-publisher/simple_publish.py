#!/usr/bin/env python3
"""简化的直接发布脚本 - 使用精美封面库"""
import requests
import json
import sys
import os
import random
import subprocess

COVER_DIR = "/home/ubuntu/.claude/skills/ai-content-publisher/assets/covers"
DOCKER_IMAGE_DIR = "${XHS_IMAGE_DIR}/docker/images"

def select_beautiful_cover():
    """从精美封面库中随机选择一张"""
    covers = [
        "tool_blue_ai.png",          # AI工具类 - 蓝色
        "tool_dark_coding.png",      # 编程工具类 - 深色
        "tool_orange_productivity.png",  # 效率工具类 - 橙色
        "tutorial_green_learning.png",   # 教程类 - 绿色
        "news_blue_data.png",        # 新闻数据类 - 蓝色
        "news_purple_analysis.png",  # 新闻分析类 - 紫色
    ]

    # 随机选择一张
    selected = random.choice(covers)
    return os.path.join(COVER_DIR, selected), selected

def publish_to_xiaohongshu(title, content, cover_path=None):
    """直接发布到小红书"""
    url = "${XHS_API_URL:-http://localhost:18060}/api/v1/publish"

    # 如果没有指定封面，从精美封面库选择
    if cover_path is None:
        source_cover, cover_name = select_beautiful_cover()
        print(f"📸 使用精美封面: {cover_name}")

        # 复制到Docker目录
        docker_cover = os.path.join(DOCKER_IMAGE_DIR, f"xhs_cover_{cover_name}")
        subprocess.run(["cp", source_cover, docker_cover], check=True)
        cover_path = f"/app/images/xhs_cover_{cover_name}"

    payload = {
        "title": title,
        "content": content,
        "images": [cover_path],
        "tags": ["AI", "科技"]
    }

    try:
        response = requests.post(url, json=payload, timeout=60)
        result = response.json()

        if result.get("success"):
            print(f"✅ 发布成功！")
            print(f"标题: {result['data']['title']}")
            return True
        else:
            print(f"❌ 发布失败: {result.get('message')}")
            return False
    except Exception as e:
        print(f"❌ 请求失败: {e}")
        return False

if __name__ == "__main__":
    if len(sys.argv) < 3:
        print("用法: python3 simple_publish.py <标题> <内容> [图片路径]")
        print("注意: 如果不指定图片路径，会自动从精美封面库选择")
        sys.exit(1)

    title = sys.argv[1]
    content = sys.argv[2]
    image = sys.argv[3] if len(sys.argv) > 3 else None

    publish_to_xiaohongshu(title, content, image)
