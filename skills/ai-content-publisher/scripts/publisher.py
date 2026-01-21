#!/usr/bin/env python3
"""
发布封装脚本
调用 wechat-article-formatter 和 wechat-draft-publisher 发布文章
"""

import os
import sys
import json
import subprocess
from datetime import datetime


def find_latest_articles():
    """查找最新生成的文章"""
    script_dir = os.path.dirname(os.path.abspath(__file__))
    base_dir = os.path.dirname(script_dir)
    output_dir = os.path.join(base_dir, 'output')

    # 找到最新的日期目录
    date_dirs = []
    if os.path.exists(output_dir):
        for d in os.listdir(output_dir):
            if os.path.isdir(os.path.join(output_dir, d)) and d.count('-') == 2:
                date_dirs.append(d)

    if not date_dirs:
        print("未找到生成的文章")
        return []

    date_dirs.sort(reverse=True)
    latest_date = date_dirs[0]
    latest_dir = os.path.join(output_dir, latest_date)

    # 查找文章目录
    articles = []
    for item in os.listdir(latest_dir):
        item_path = os.path.join(latest_dir, item)
        if os.path.isdir(item_path):
            md_file = os.path.join(item_path, 'article.md')
            if os.path.exists(md_file):
                articles.append({
                    'dir': item_path,
                    'md_file': md_file,
                    'index': item.replace('article_', '')
                })

    articles.sort(key=lambda x: x['index'])
    return articles


def format_article(md_file, theme='tech'):
    """调用 wechat-article-formatter 转换文章"""
    formatter_path = '/home/ubuntu/.claude/skills/wechat-article-formatter/convert.py'
    output_file = md_file.replace('.md', '_wechat.html')

    cmd = [
        'python3',
        formatter_path,
        '--input', md_file,
        '--theme', theme,
        '--output', output_file
    ]

    try:
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=120)
        if result.returncode == 0:
            print(f"✅ 格式化成功: {output_file}")
            return output_file
        else:
            print(f"❌ 格式化失败: {result.stderr}")
            return None
    except Exception as e:
        print(f"❌ 格式化出错: {e}")
        return None


def publish_to_wechat(html_file, title, cover_file):
    """调用 wechat-draft-publisher 发布文章"""
    publisher_path = '/home/ubuntu/.claude/skills/wechat-draft-publisher/publisher.py'

    cmd = [
        'python3',
        publisher_path,
        '--title', title,
        '--content', html_file,
        '--cover', cover_file,
        '--author', '阳桃AI干货'
    ]

    try:
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=60)
        if result.returncode == 0:
            print(f"✅ 发布成功: {title}")
            return True, result.stdout
        else:
            print(f"❌ 发布失败: {result.stderr}")
            return False, result.stderr
    except Exception as e:
        print(f"❌ 发布出错: {e}")
        return False, str(e)


def extract_title_from_md(md_file):
    """从Markdown文件提取标题"""
    with open(md_file, 'r', encoding='utf-8') as f:
        first_line = f.readline().strip()
        if first_line.startswith('# '):
            return first_line[2:].strip()
    return os.path.basename(os.path.dirname(md_file))


def publish_all_articles():
    """发布所有文章"""
    articles = find_latest_articles()

    if not articles:
        print("没有找到需要发布的文章")
        return

    print(f"找到 {len(articles)} 篇文章待发布")

    results = []

    for article in articles:
        print(f"\n=== 处理文章 {article['index']} ===")

        md_file = article['md_file']
        article_dir = article['dir']

        # 提取标题
        title = extract_title_from_md(md_file)
        print(f"标题: {title}")

        # 查找封面图
        cover_file = os.path.join(article_dir, 'cover.png')
        if not os.path.exists(cover_file):
            print(f"⚠️ 封面图不存在: {cover_file}")
            continue

        # 格式化文章
        html_file = format_article(md_file)
        if not html_file:
            continue

        # 发布到微信
        success, output = publish_to_wechat(html_file, title, cover_file)

        results.append({
            'title': title,
            'md_file': md_file,
            'html_file': html_file,
            'success': success,
            'output': output
        })

    # 保存发布结果
    save_publish_results(results)

    # 总结
    success_count = sum(1 for r in results if r['success'])
    print(f"\n=== 发布完成 ===")
    print(f"成功: {success_count}/{len(results)}")


def save_publish_results(results):
    """保存发布结果"""
    script_dir = os.path.dirname(os.path.abspath(__file__))
    cache_dir = os.path.join(os.path.dirname(script_dir), 'cache')
    os.makedirs(cache_dir, exist_ok=True)

    result_file = os.path.join(cache_dir, f'publish_results_{datetime.now().strftime("%Y%m%d_%H%M%S")}.json')

    with open(result_file, 'w', encoding='utf-8') as f:
        json.dump(results, f, ensure_ascii=False, indent=2)

    print(f"发布结果已保存: {result_file}")


if __name__ == '__main__':
    publish_all_articles()
