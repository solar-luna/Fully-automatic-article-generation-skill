#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
小红书REST API客户端
通过HTTP REST API调用xiaohongshu-mcp服务
"""

import json
import requests
from typing import Dict, Any, List, Optional


class XiaohongshuMCPClient:
    """小红书REST API客户端"""

    def __init__(self, api_url: str = "${XHS_API_URL:-http://localhost:18060}"):
        """
        初始化客户端

        Args:
            api_url: API服务地址
        """
        self.api_url = api_url
        self.publish_endpoint = f"{api_url}/api/v1/publish"

    def check_login_status(self) -> Dict[str, Any]:
        """
        检查登录状态（通过测试发布接口）

        Returns:
            登录状态信息
        """
        # 尝试简单的测试请求来验证服务可用性
        try:
            response = requests.get(self.api_url, timeout=5)
            return {"status": "ok", "service_running": True}
        except requests.exceptions.RequestException:
            raise Exception(f"小红书服务连接失败\n请确保xiaohongshu-mcp服务正在运行: docker ps | grep xiaohongshu-mcp")

    def publish_content(self, title: str, content: str,
                       images: List[str]) -> Dict[str, Any]:
        """
        发布图文内容

        Args:
            title: 标题
            content: 正文
            images: 图片路径列表（容器内路径，如 /app/images/xxx.png）

        Returns:
            发布结果
        """
        print(f"  → 正在发布到小红书...")

        payload = {
            "title": title,
            "content": content,
            "images": images,
            "tags": ["AI", "科技"]
        }

        try:
            response = requests.post(
                self.publish_endpoint,
                json=payload,
                headers={"Content-Type": "application/json"},
                timeout=60
            )
            response.raise_for_status()
            result = response.json()

            # 检查是否成功
            if not result.get("success"):
                raise Exception(f"发布失败: {result.get('message', '未知错误')}")

            return result

        except requests.exceptions.RequestException as e:
            raise Exception(f"发布请求失败: {e}")

    def publish_with_video(self, title: str, content: str,
                          video: str) -> Dict[str, Any]:
        """
        发布视频内容

        Args:
            title: 标题
            content: 正文
            video: 视频文件路径

        Returns:
            发布结果
        """
        print(f"  → 正在发布视频到小红书...")

        result = self._call("call_tool", {
            "name": "publish_with_video",
            "arguments": {
                "title": title,
                "content": content,
                "video": video
            }
        })

        return result

    def list_feeds(self) -> Dict[str, Any]:
        """
        获取推荐列表

        Returns:
            推荐内容列表
        """
        return self._call("call_tool", {
            "name": "list_feeds",
            "arguments": {}
        })

    def search_feeds(self, keyword: str) -> Dict[str, Any]:
        """
        搜索内容

        Args:
            keyword: 搜索关键词

        Returns:
            搜索结果
        """
        return self._call("call_tool", {
            "name": "search_feeds",
            "arguments": {
                "keyword": keyword
            }
        })


def main():
    """测试函数"""
    client = XiaohongshuMCPClient()

    # 测试连接
    print("测试MCP连接...")
    try:
        status = client.check_login_status()
        print("✓ MCP连接成功")
        print(f"登录状态: {json.dumps(status, ensure_ascii=False, indent=2)}")
    except Exception as e:
        print(f"✗ 连接失败: {e}")
        return

    # 测试发布
    print("\n测试发布功能...")
    try:
        result = client.publish_content(
            title="测试标题",
            content="这是一条测试内容",
            images=["/tmp/test.jpg"]
        )
        print("✓ 发布成功")
        print(f"结果: {json.dumps(result, ensure_ascii=False, indent=2)}")
    except Exception as e:
        print(f"✗ 发布失败: {e}")


if __name__ == "__main__":
    main()
