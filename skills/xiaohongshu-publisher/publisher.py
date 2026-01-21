#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
小红书自动发布工具
支持将微信公众号内容转换为小红书格式并发布
"""

import os
import sys
import json
import argparse
from pathlib import Path

# 添加scripts目录到路径
SCRIPT_DIR = Path(__file__).parent / "scripts"
sys.path.insert(0, str(SCRIPT_DIR))

from content_adapter import XiaohongshuContentAdapter
from image_generator import XiaohongshuImageGenerator
from xiaohongshu_client import XiaohongshuMCPClient


class XiaohongshuPublisher:
    """小红书自动发布器"""

    def __init__(self, api_url: str = "${XHS_API_URL:-http://localhost:18060}"):
        """
        初始化发布器

        Args:
            api_url: API服务地址
        """
        self.api_url = api_url
        self.adapter = XiaohongshuContentAdapter()
        self.image_generator = XiaohongshuImageGenerator()
        self.client = XiaohongshuMCPClient(api_url)

    def publish_from_wechat(self, title: str, content: str,
                           cover_image: str = None) -> dict:
        """
        从微信公众号内容发布到小红书

        Args:
            title: 文章标题
            content: 文章内容（HTML格式）
            cover_image: 封面图路径（可选，不提供则自动生成）

        Returns:
            发布结果
        """
        print(f"\n{'='*50}")
        print(f"小红书自动发布")
        print(f"{'='*50}\n")

        # 1. 检查登录状态
        print("1. 检查小红书登录状态...")
        try:
            status = self.client.check_login_status()
            print(f"  ✓ 已登录: {status.get('content', {}).get('text', 'OK')}")
        except Exception as e:
            print(f"  ✗ 登录检查失败: {e}")
            print("\n提示: 请确保xiaohongshu-mcp服务正在运行，且已完成登录")
            print("启动命令: cd ~/xiaohongshu-mcp && docker compose up -d")
            return {"success": False, "error": str(e)}

        # 2. 适配标题
        print("\n2. 适配标题格式...")
        xhs_title = self.adapter.adapt_title(title)
        print(f"  原标题: {title}")
        print(f"  适配后: {xhs_title}")

        # 3. 适配内容
        print("\n3. 适配内容格式...")
        adapted = self.adapter.adapt_content(content, xhs_title)
        xhs_content = adapted["content"]
        print(f"  原内容长度: {adapted['original_length']} 字")
        print(f"  适配后长度: {adapted['adapted_length']} 字")
        print(f"\n适配后内容预览:")
        print("-" * 40)
        print(xhs_content[:200] + "…" if len(xhs_content) > 200 else xhs_content)
        print("-" * 40)

        # 4. 使用封面图（强制要求：必须提供封面图，不生成）
        print("\n4. 处理封面图...")
        if cover_image and os.path.exists(cover_image):
            print(f"  使用指定封面: {cover_image}")
            cover_path = cover_image
        else:
            print(f"  ✗ 错误：未提供封面图！")
            print(f"  ⚠️  硬性要求：必须使用封面库的图片，不允许自动生成")
            print(f"  💡 解决方法：调用时使用 --cover 参数指定封面图路径")
            raise ValueError("必须提供封面图，不允许自动生成。请使用 --cover 参数指定从封面库选择的图片。")

        # 5. 发布到小红书
        print("\n5. 发布到小红书...")
        try:
            result = self.client.publish_content(
                title=xhs_title,
                content=xhs_content,
                images=[cover_path]
            )

            print(f"  ✓ 发布成功!")
            print(f"\n{'='*50}")
            print("✓ 内容已发布到小红书!")
            print(f"{'='*50}")

            return {
                "success": True,
                "title": xhs_title,
                "cover": cover_path,
                "result": result
            }

        except Exception as e:
            print(f"  ✗ 发布失败: {e}")
            return {
                "success": False,
                "error": str(e)
            }

    def publish_direct(self, title: str, content: str,
                      images: list = None) -> dict:
        """
        直接发布内容到小红书（不进行格式转换）

        Args:
            title: 标题
            content: 内容
            images: 图片路径列表

        Returns:
            发布结果
        """
        print(f"\n{'='*50}")
        print(f"小红书直接发布")
        print(f"{'='*50}\n")

        # 检查登录状态
        print("检查登录状态...")
        try:
            status = self.client.check_login_status()
            print(f"✓ 已登录")
        except Exception as e:
            print(f"✗ 登录检查失败: {e}")
            return {"success": False, "error": str(e)}

        # 发布
        print(f"发布内容...")
        try:
            result = self.client.publish_content(
                title=title,
                content=content,
                images=images or []
            )

            print(f"✓ 发布成功!")

            return {
                "success": True,
                "result": result
            }

        except Exception as e:
            print(f"✗ 发布失败: {e}")
            return {
                "success": False,
                "error": str(e)
            }


def load_html_file(file_path: str) -> str:
    """
    加载HTML文件

    Args:
        file_path: 文件路径

    Returns:
        文件内容
    """
    if not os.path.exists(file_path):
        raise FileNotFoundError(f"文件不存在: {file_path}")

    with open(file_path, 'r', encoding='utf-8') as f:
        return f.read()


def main():
    """主函数"""
    parser = argparse.ArgumentParser(
        description='小红书自动发布工具',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
使用示例:
  # 从微信公众号HTML发布（自动格式转换）
  %(prog)s --wechat --title "标题" --content article.html

  # 直接发布（不转换格式）
  %(prog)s --direct --title "标题" --content "内容文本" --images cover.jpg

  # 从JSON配置发布
  %(prog)s --config article.json
        """
    )

    parser.add_argument('--mode', choices=['wechat', 'direct'], default='wechat',
                       help='发布模式: wechat=从微信格式转换, direct=直接发布')
    parser.add_argument('-t', '--title', help='文章标题')
    parser.add_argument('-c', '--content', help='文章内容（HTML文件路径或直接文本）')
    parser.add_argument('--images', nargs='+', help='图片路径列表')
    parser.add_argument('--cover', help='封面图路径（仅wechat模式）')
    parser.add_argument('--config', help='JSON配置文件路径')
    parser.add_argument('--api-url', default='${XHS_API_URL:-http://localhost:18060}',
                       help='API服务地址')

    args = parser.parse_args()

    try:
        publisher = XiaohongshuPublisher(api_url=args.api_url)

        # 从配置文件读取
        if args.config:
            with open(args.config, 'r', encoding='utf-8') as f:
                config = json.load(f)

            title = config.get('title')
            content = config.get('content')
            images = config.get('images', [])
            mode = config.get('mode', 'wechat')

            if mode == 'wechat' and content and os.path.exists(content):
                result = publisher.publish_from_wechat(title, load_html_file(content))
            else:
                result = publisher.publish_direct(title, content, images)

        # 微信模式
        elif args.mode == 'wechat':
            if not args.title or not args.content:
                parser.print_help()
                print("\n错误: wechat模式需要 --title 和 --content 参数")
                sys.exit(1)

            content_text = load_html_file(args.content) if os.path.exists(args.content) else args.content
            result = publisher.publish_from_wechat(args.title, content_text, args.cover)

        # 直接模式
        else:
            if not args.title or not args.content:
                parser.print_help()
                print("\n错误: direct模式需要 --title 和 --content 参数")
                sys.exit(1)

            result = publisher.publish_direct(args.title, args.content, args.images)

        # 输出结果
        if result.get('success'):
            print(f"\n发布成功! 标题: {result.get('title', args.title)}")
            sys.exit(0)
        else:
            print(f"\n发布失败: {result.get('error')}")
            sys.exit(1)

    except KeyboardInterrupt:
        print("\n\n操作已取消")
        sys.exit(0)
    except Exception as e:
        print(f"\n错误: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == '__main__':
    main()
