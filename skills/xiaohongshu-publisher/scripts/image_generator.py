#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
小红书封面图生成器
使用Pillow库自动生成文字封面图
"""

import os
import re
from typing import List, Tuple


class XiaohongshuImageGenerator:
    """小红书封面图生成器"""

    # 小红书推荐图片尺寸
    RECOMMENDED_SIZE = (1080, 1440)  # 3:4 比例
    MIN_SIZE = (720, 960)

    # 渐变背景配色方案
    COLOR_SCHEMES = [
        # (背景色, 文字色, 强调色, 名称)
        ("#1a1a2e", "#ffffff", "#e94560", "深蓝红"),  # 深蓝背景+红色强调
        ("#0f3460", "#ffffff", "#e94560", "午夜蓝"),
        ("#16213e", "#ffffff", "#0f3460", "深空蓝"),
        ("#1a1a2e", "#ffffff", "#ffd700", "黑金"),    # 深蓝背景+金色强调
        ("#2d132c", "#ffffff", "#801336", "深紫红"),
        ("#4a0e4e", "#ffffff", "#81007f", "深紫色"),
        ("#0c0032", "#ffffff", "#5b189a", "星空紫"),
        ("#190028", "#ffffff", "#7b2cbf", "暗夜紫"),
        ("#000000", "#ffffff", "#ff6b6b", "经典黑"),
        ("#1e3a5f", "#ffffff", "#4fc3f7", "冰蓝色"),
    ]

    def __init__(self, output_dir: str = None):
        """
        初始化图片生成器

        Args:
            output_dir: 输出目录，默认为 ~/.xiaohongshu-publisher/images
        """
        if output_dir is None:
            output_dir = os.path.expanduser("~/.xiaohongshu-publisher/images")
        self.output_dir = output_dir
        os.makedirs(self.output_dir, exist_ok=True)

    def _parse_color(self, color: str) -> Tuple[int, int, int]:
        """
        解析十六进制颜色为RGB元组

        Args:
            color: 十六进制颜色 (如 "#ff0000")

        Returns:
            RGB元组
        """
        color = color.lstrip("#")
        return tuple(int(color[i:i+2], 16) for i in (0, 2, 4))

    def _generate_gradient(self, width: int, height: int,
                           start_color: Tuple[int, int, int],
                           end_color: Tuple[int, int, int]) -> List[List[Tuple[int, int, int]]]:
        """
        生成渐变色像素数组

        Args:
            width: 宽度
            height: 高度
            start_color: 起始颜色
            end_color: 结束颜色

        Returns:
            像素数组
        """
        pixels = []
        for y in range(height):
            row = []
            for x in range(width):
                # 垂直渐变
                ratio = y / height
                r = int(start_color[0] * (1 - ratio) + end_color[0] * ratio)
                g = int(start_color[1] * (1 - ratio) + end_color[1] * ratio)
                b = int(start_color[2] * (1 - ratio) + end_color[2] * ratio)
                row.append((r, g, b))
            pixels.append(row)
        return pixels

    def _draw_text_centered(self, draw, text: str, y: int, font,
                           color: Tuple[int, int, int],
                           max_width: int) -> None:
        """
        在画布上居中绘制文本

        Args:
            draw: PIL ImageDraw对象
            text: 文本内容
            y: Y坐标
            font: 字体
            color: 文字颜色
            max_width: 最大宽度
        """
        try:
            from PIL import Image, ImageDraw, ImageFont
        except ImportError:
            raise ImportError("需要安装 Pillow 库: pip install Pillow")

        # 获取文本边界框
        bbox = draw.textbbox((0, 0), text, font=font)
        text_width = bbox[2] - bbox[0]

        # 如果文本过宽，需要换行
        if text_width > max_width:
            words = list(text)
            lines = []
            current_line = ""
            for word in words:
                test_line = current_line + word
                bbox = draw.textbbox((0, 0), test_line, font=font)
                if bbox[2] - bbox[0] <= max_width:
                    current_line = test_line
                else:
                    if current_line:
                        lines.append(current_line)
                    current_line = word
            if current_line:
                lines.append(current_line)

            # 绘制多行文本
            total_height = len(lines) * (font.size + 10)
            start_y = y - total_height // 2
            for i, line in enumerate(lines):
                bbox = draw.textbbox((0, 0), line, font=font)
                line_width = bbox[2] - bbox[0]
                x = (max_width - line_width) // 2
                draw.text((x, start_y + i * (font.size + 10)), line, font=font, fill=color)
        else:
            # 单行文本居中
            x = (max_width - text_width) // 2
            draw.text((x, y), text, font=font, fill=color)

    def generate_cover(self, title: str, key_points: List[str] = None,
                      output_filename: str = None,
                      color_scheme: int = 0) -> str:
        """
        生成封面图

        Args:
            title: 标题（主标题）
            key_points: 关键要点列表（副标题）
            output_filename: 输出文件名，默认为自动生成
            color_scheme: 配色方案索引

        Returns:
            生成的图片路径
        """
        try:
            from PIL import Image, ImageDraw, ImageFont
        except ImportError:
            raise ImportError("需要安装 Pillow 库: pip install Pillow")

        # 图片尺寸
        width, height = self.RECOMMENDED_SIZE

        # 选择配色方案
        scheme = self.COLOR_SCHEMES[color_scheme % len(self.COLOR_SCHEMES)]
        bg_color_hex, text_color_hex, accent_color_hex, scheme_name = scheme
        bg_color = self._parse_color(bg_color_hex)
        text_color = self._parse_color(text_color_hex)
        accent_color = self._parse_color(accent_color_hex)

        print(f"  → 使用配色方案: {scheme_name}")

        # 创建图像
        img = Image.new("RGB", (width, height))
        draw = ImageDraw.Draw(img)

        # 绘制渐变背景
        start_color = tuple(max(0, c - 30) for c in bg_color)
        pixels = self._generate_gradient(width, height, start_color, bg_color)
        for y, row in enumerate(pixels):
            for x, pixel in enumerate(row):
                img.putpixel((x, y), pixel)

        # 尝试加载字体
        font_paths = [
            "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf",
            "/usr/share/fonts/truetype/liberation/LiberationSans-Bold.ttf",
            "/System/Library/Fonts/PingFang.ttc",  # macOS
            "C:/Windows/Fonts/msyhbd.ttc",  # Windows
            "/usr/share/fonts/truetype/noto/NotoSansCJK-Bold.ttc",
        ]

        title_font = None
        body_font = None

        for font_path in font_paths:
            if os.path.exists(font_path):
                try:
                    title_font = ImageFont.truetype(font_path, 80)
                    body_font = ImageFont.truetype(font_path, 40)
                    break
                except:
                    continue

        if title_font is None:
            # 使用默认字体
            title_font = ImageFont.load_default()
            body_font = ImageFont.load_default()
            print("  ⚠ 未找到合适的字体，使用默认字体")

        # 绘制顶部装饰条
        draw.rectangle([(0, 0), (width, 15)], fill=accent_color)

        # 绘制标题
        self._draw_text_centered(draw, title, height // 3, title_font, text_color, width - 100)

        # 绘制要点
        if key_points:
            start_y = height // 2
            for i, point in enumerate(key_points[:3]):
                y_pos = start_y + i * 70
                # 绘制序号圆圈
                circle_x = 100
                circle_y = y_pos
                draw.ellipse([circle_x - 25, circle_y - 25, circle_x + 25, circle_y + 25],
                            fill=accent_color)

                # 绘制序号
                number_text = str(i + 1)
                bbox = draw.textbbox((0, 0), number_text, font=title_font)
                number_width = bbox[2] - bbox[0]
                draw.text((circle_x - number_width // 2, circle_y - 40), number_text,
                         font=title_font, fill=(255, 255, 255))

                # 绘制要点文字
                point_text = point[:30] + "…" if len(point) > 30 else point
                draw.text((150, y_pos - 20), point_text, font=body_font, fill=text_color)

        # 绘制底部装饰条
        draw.rectangle([(0, height - 15), (width, height)], fill=accent_color)

        # 添加底部小字
        footer_text = "阳桃AI干货"
        bbox = draw.textbbox((0, 0), footer_text, font=body_font)
        footer_width = bbox[2] - bbox[0]
        draw.text(((width - footer_width) // 2, height - 60), footer_text,
                 font=body_font, fill=tuple(max(0, c - 100) for c in text_color))

        # 保存图片
        if output_filename is None:
            import hashlib
            title_hash = hashlib.md5(title.encode()).hexdigest()[:8]
            output_filename = f"xhs_cover_{title_hash}.jpg"

        output_path = os.path.join(self.output_dir, output_filename)
        img.save(output_path, "JPEG", quality=95)
        print(f"  ✓ 封面图已保存: {output_path}")

        return output_path


def main():
    """测试函数"""
    generator = XiaohongshuImageGenerator()

    # 测试生成封面
    title = "OpenAI o4重磅发布"
    key_points = ["数学准确率94.5%", "编程效率提升3倍", "支持200K上下文"]

    output_path = generator.generate_cover(title, key_points)
    print(f"\n生成的封面图: {output_path}")


if __name__ == "__main__":
    main()
