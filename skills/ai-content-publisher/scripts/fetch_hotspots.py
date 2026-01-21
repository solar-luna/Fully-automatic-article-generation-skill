#!/usr/bin/env python3
"""
热点获取脚本
从RSS源和GitHub获取最新的AI热点
"""

import feedparser
import requests
from datetime import datetime, timedelta
import json
import os
import sys


def load_config(config_path="config/sources.yaml"):
    """加载配置文件"""
    try:
        import yaml
        with open(config_path, 'r', encoding='utf-8') as f:
            return yaml.safe_load(f)
    except ImportError:
        print("请安装 pyyaml: pip install pyyaml")
        sys.exit(1)


def fetch_rss_feed(url, max_age_hours=48, max_results=10):
    """抓取单个RSS源（带超时控制）"""
    try:
        # 使用requests获取RSS内容，添加超时控制
        response = requests.get(url, timeout=15, headers={
            'User-Agent': 'Mozilla/5.0 (compatible; AI-Content-Publisher/1.0)'
        })
        response.raise_for_status()

        # 解析RSS
        feed = feedparser.parse(response.content)
        hotspots = []
        cutoff_time = datetime.now() - timedelta(hours=max_age_hours)

        for entry in feed.entries[:max_results]:
            # 解析发布时间
            published = entry.get('published_parsed')
            if published:
                pub_time = datetime(*published[:6])
            else:
                pub_time = datetime.now()

            # 只保留48小时内的内容
            if pub_time < cutoff_time:
                continue

            hotspots.append({
                'title': entry.get('title', ''),
                'url': entry.get('link', ''),
                'summary': entry.get('summary', '')[:200],
                'published': pub_time.isoformat(),
                'source': feed.feed.get('title', url),
                'type': 'rss'
            })

        return hotspots
    except requests.exceptions.Timeout:
        print(f"抓取RSS超时 {url}")
        return []
    except requests.exceptions.RequestException as e:
        print(f"抓取RSS失败 {url}: {e}")
        return []
    except Exception as e:
        print(f"解析RSS失败 {url}: {e}")
        return []


def fetch_github_trending(config):
    """获取GitHub Trending AI/ML项目"""
    if not config.get('github', {}).get('enabled', False):
        return []

    try:
        # 使用GitHub搜索API获取最近的热门AI/ML项目
        api_url = "https://api.github.com/search/repositories"
        github_config = config['github']

        # 构建查询
        languages = ' '.join([f"language:{lang}" for lang in github_config.get('languages', ['python'])])
        topics = ' '.join([f"topic:{topic}" for topic in github_config.get('topics', ['machine-learning'])])
        min_stars = github_config.get('min_stars', 10)

        query = f"{languages} {topics} stars:>={min_stars}"
        params = {
            'q': query,
            'sort': 'stars',
            'order': 'desc',
            'per_page': github_config.get('max_results', 20)
        }

        response = requests.get(api_url, params=params, timeout=30)
        response.raise_for_status()
        data = response.json()

        hotspots = []
        cutoff_time = datetime.now() - timedelta(hours=config.get('max_age_hours', 48))

        for repo in data.get('items', []):
            # 检查更新时间
            updated = datetime.strptime(repo['updated_at'], '%Y-%m-%dT%H:%M:%SZ')
            if updated < cutoff_time:
                continue

            hotspots.append({
                'title': repo['name'],
                'url': repo['html_url'],
                'summary': repo.get('description', '')[:200],
                'published': updated.isoformat(),
                'source': 'GitHub Trending',
                'type': 'github',
                'stars': repo['stargazers_count'],
                'language': repo.get('language', '')
            })

        return hotspots

    except Exception as e:
        print(f"获取GitHub Trending失败: {e}")
        return []


def deduplicate_hotspots(hotspots):
    """去重热点（基于URL）"""
    seen_urls = set()
    unique_hotspots = []

    for hotspot in hotspots:
        url = hotspot['url']
        if url not in seen_urls:
            seen_urls.add(url)
            unique_hotspots.append(hotspot)

    return unique_hotspots


def fetch_all_hotspots(config_path=None):
    """获取所有热点"""
    if config_path is None:
        # 默认配置路径
        script_dir = os.path.dirname(os.path.abspath(__file__))
        config_path = os.path.join(os.path.dirname(script_dir), 'config/sources.yaml')

    config = load_config(config_path)
    all_hotspots = []
    max_age = config.get('max_age_hours', 48)
    max_per_source = config.get('max_hotspots_per_source', 10)

    # 获取RSS热点
    for category in ['ai_companies', 'tech_media', 'tutorial_communities']:
        for source in config.get(category, []):
            if not source.get('enabled', True):
                continue

            print(f"抓取 {source['name']}...")
            hotspots = fetch_rss_feed(
                source['url'],
                max_age_hours=max_age,
                max_results=max_per_source
            )
            all_hotspots.extend(hotspots)

    # 获取GitHub热点
    print("抓取 GitHub Trending...")
    github_hotspots = fetch_github_trending(config)
    all_hotspots.extend(github_hotspots)

    # 去重
    all_hotspots = deduplicate_hotspots(all_hotspots)

    # 按发布时间排序
    all_hotspots.sort(key=lambda x: x['published'], reverse=True)

    print(f"共获取 {len(all_hotspots)} 个热点")
    return all_hotspots


def save_hotspots(hotspots, output_path=None):
    """保存热点到JSON文件"""
    if output_path is None:
        script_dir = os.path.dirname(os.path.abspath(__file__))
        output_dir = os.path.join(os.path.dirname(script_dir), 'cache')
        os.makedirs(output_dir, exist_ok=True)
        output_path = os.path.join(output_dir, 'hotspots.json')

    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(hotspots, f, ensure_ascii=False, indent=2)

    print(f"热点已保存到: {output_path}")
    return output_path


if __name__ == '__main__':
    # 获取所有热点
    hotspots = fetch_all_hotspots()

    # 保存到文件
    save_hotspots(hotspots)

    # 输出预览
    print("\n=== 热点预览 ===")
    for i, h in enumerate(hotspots[:10], 1):
        print(f"{i}. {h['title']}")
        print(f"   来源: {h['source']} | 时间: {h['published'][:10]}")
