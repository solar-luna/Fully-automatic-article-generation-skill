#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
微信公众号文章格式化工具 v3.0 - 专业排版增强版
将 Markdown 转换为适配微信公众号的精美 HTML
"""

import markdown
from bs4 import BeautifulSoup, NavigableString
import sys
import argparse
import re


def detect_alert_type(blockquote):
    """
    检测blockquote是否为特殊警告框
    支持的关键词：
    - Info: 💡, 提示, Info, TIP, NOTE
    - Warning: ⚠️, 警告, Warning, WARN, CAUTION
    - Success: ✅, 成功, Success, DONE
    - Danger: ❌, 危险, Danger, ERROR, CRITICAL
    """
    first_strong = blockquote.find('strong')
    if first_strong:
        text = first_strong.get_text().strip()
        text_lower = text.lower()
        if any(kw in text for kw in ['💡', '提示']) or any(kw in text_lower for kw in ['info', 'tip', 'note']):
            return 'info'
        elif any(kw in text for kw in ['⚠️', '警告']) or any(kw in text_lower for kw in ['warning', 'warn', 'caution']):
            return 'warning'
        elif any(kw in text for kw in ['✅', '成功']) or any(kw in text_lower for kw in ['success', 'done']):
            return 'success'
        elif any(kw in text for kw in ['❌', '危险']) or any(kw in text_lower for kw in ['danger', 'error', 'critical']):
            return 'danger'
    return None


def is_intro_paragraph(p, index):
    """判断是否为导语段落（前2段）"""
    return index < 2


def is_scenario_paragraph(p):
    """判断段落是否为场景描述（包含"场景"、"示例"、"案例"等关键词）"""
    text = p.get_text()
    keywords = ['场景一', '场景二', '场景三', '场景四', '场景五',
                '示例', '案例', '亮点', '特点', '优势']
    return any(kw in text for kw in keywords)


def has_numbered_list_pattern(p):
    """检测段落是否包含编号模式（如：1. xxx）"""
    text = p.get_text()
    return bool(re.match(r'^\d+[.、]', text.strip()))


def apply_syntax_highlighting(code_element):
    """为代码块应用Atom One Dark语法高亮"""
    syntax_colors = {
        'k': '#c678dd', 'kn': '#c678dd', 'kd': '#c678dd', 'kt': '#c678dd',
        'o': '#abb2bf',
        's': '#98c379', 's1': '#98c379', 's2': '#98c379',
        'mi': '#d19a66', 'mf': '#d19a66',
        'nf': '#61afef',
        'nc': '#e5c07b',
        'nn': '#abb2bf',
        'na': '#d19a66',
        'nb': '#e5c07b',
        'c': '#5c6370', 'c1': '#5c6370', 'cm': '#5c6370',
    }

    for span in code_element.find_all('span'):
        if 'class' in span.attrs:
            for cls in span['class']:
                if cls in syntax_colors:
                    span['style'] = f'color: {syntax_colors[cls]};'
                    break


def apply_inline_styles(html_content):
    """应用内联CSS样式 - v3.0 专业排版版"""
    soup = BeautifulSoup(html_content, 'html.parser')

    # ==================== H2 标题增强（大幅美化 - 淡紫色背景） ====================
    for h2 in soup.find_all('h2'):
        h2['style'] = (
            'font-size: 22px; '
            'font-weight: bold; '
            'color: #1f2937; '
            'margin-top: 45px; '
            'margin-bottom: 25px; '
            'padding: 15px 20px; '
            'background: #faf5ff; '  # 淡紫色（微信不支持渐变）
            'border-left: 5px solid #7c3aed; '  # 紫色边框（微信不支持border-image）
            'border-radius: 0 8px 8px 0; '
            'box-shadow: 0 2px 8px rgba(124, 58, 237, 0.1);'
        )

    # ==================== H3 标题美化（蓝色系） ====================
    for h3 in soup.find_all('h3'):
        h3['style'] = (
            'font-size: 19px; '
            'font-weight: 600; '
            'color: #1f2937; '
            'margin-top: 30px; '
            'margin-bottom: 18px; '
            'padding-left: 15px; '
            'border-left: 4px solid #3b82f6; '  # 蓝色边框
            'position: relative;'
        )

    # ==================== 段落增强处理 ====================
    paragraphs = soup.find_all('p')
    for idx, p in enumerate(paragraphs):
        # 基础样式
        base_style = (
            'font-size: 16px; '
            'line-height: 1.9; '  # 增加行高
            'color: #374151; '
            'margin: 20px 0; '  # 加大间距
        )

        # 导语段落（前2段）- 特殊样式（淡蓝色系）
        if is_intro_paragraph(p, idx):
            p['style'] = base_style + (
                'background: #eff6ff; '  # 淡蓝色（微信不支持渐变）
                'padding: 20px; '
                'border-left: 4px solid #3b82f6; '  # 蓝色边框
                'border-radius: 0 8px 8px 0; '
                'font-size: 17px; '
                'line-height: 2.0; '
                'color: #1f2937; '
                'margin-bottom: 25px; '
                'box-shadow: 0 2px 6px rgba(59, 130, 246, 0.1);'  # 蓝色阴影
            )
        # 场景/案例段落 - 卡片样式（青色系）
        elif is_scenario_paragraph(p):
            p['style'] = base_style + (
                'background: #ecfeff; '  # 淡青背景
                'padding: 18px 20px; '
                'border-left: 4px solid #06b6d4; '  # 青色边框
                'border-radius: 0 6px 6px 0; '
                'margin: 25px 0; '
                'box-shadow: 0 1px 4px rgba(6, 182, 212, 0.1);'  # 青色阴影
            )
        # 包含编号的段落 - 突出显示（绿色系）
        elif has_numbered_list_pattern(p):
            p['style'] = base_style + (
                'padding-left: 25px; '
                'border-left: 3px solid #10b981; '  # 绿色边框
                'margin: 18px 0;'
            )
        # 普通段落
        else:
            p['style'] = base_style + (
                'text-align: justify; '
                'text-indent: 0;'  # 首行不缩进（微信编辑器会自动处理）
            )

    # ==================== 列表大幅美化 ====================
    for ul in soup.find_all('ul'):
        ul['style'] = (
            'margin: 25px 0; '
            'padding-left: 0; '
            'list-style: none;'
        )

    for li in soup.find_all('li'):
        if li.parent.name == 'ul':
            li['style'] = (
                'font-size: 16px; '
                'line-height: 1.9; '
                'color: #374151; '
                'margin: 15px 0; '
                'padding: 12px 12px 12px 35px; '
                'background: #fafafa; '  # 浅灰背景
                'border-radius: 6px; '
                'position: relative;'
            )
            # 蓝紫渐变圆点
            bullet = soup.new_tag('span')
            bullet['style'] = (
                'position: absolute; '
                'left: 12px; '
                'top: 12px; '
                'color: #8b5cf6; '  # 稍浅的紫色
                'font-weight: bold; '
                'font-size: 18px;'
            )
            bullet.string = '●'
            li.insert(0, bullet)
            if li.contents and len(li.contents) > 1:
                li.insert(1, ' ')
        else:
            # 有序列表
            li['style'] = (
                'font-size: 16px; '
                'line-height: 1.9; '
                'color: #374151; '
                'margin: 12px 0; '
                'padding-left: 8px;'
            )

    # 有序列表容器
    for ol in soup.find_all('ol'):
        ol['style'] = (
            'margin: 25px 0; '
            'padding-left: 30px; '
            'counter-reset: li;'
        )

    # ==================== 代码块增强 ====================
    for pre in soup.find_all('pre'):
        pre['style'] = (
            'background: #282c34; '
            'color: #abb2bf; '
            'padding: 16px; '
            'border-radius: 8px; '
            'overflow-x: auto; '
            'margin: 20px 0; '
            'font-family: "SFMono-Regular", Consolas, "Liberation Mono", Menlo, Courier, monospace; '
            'font-size: 14px; '
            'line-height: 1.6;'
        )
        for code in pre.find_all('code'):
            code['style'] = (
                'background-color: transparent; '
                'color: #abb2bf; '
                'padding: 0; '
                'font-family: inherit;'
            )
            apply_syntax_highlighting(code)

    # 行内代码（浅灰色系）
    for code in soup.find_all('code'):
        if code.parent.name != 'pre':
            code['style'] = (
                'background: #f5f5f5; '
                'color: #e83e8c; '
                'padding: 2px 6px; '
                'border-radius: 4px; '
                'font-family: "SFMono-Regular", Consolas, "Liberation Mono", Menlo, Courier, monospace; '
                'font-size: 0.9em; '
                'font-weight: 500;'
            )

    # ==================== 强调文本增强 ====================
    for strong in soup.find_all('strong'):
        strong['style'] = (
            'color: #3b82f6; '  # 蓝色（从紫色改为蓝色）
            'font-weight: 600; '
            'background: #eff6ff; '  # 淡蓝色（微信不支持渐变）
            'padding: 2px 6px; '
            'border-radius: 3px;'
        )

    # ==================== 引用块大幅增强 ====================
    for blockquote in soup.find_all('blockquote'):
        alert_type = detect_alert_type(blockquote)

        if alert_type == 'info':
            blockquote['style'] = (
                'border-left: 5px solid #6366f1; '
                'background: #eef2ff; '  # 淡紫蓝色（微信不支持渐变）
                'padding: 20px 24px; '
                'margin: 30px 0; '
                'border-radius: 0 10px 10px 0; '
                'color: #3730a3; '
                'font-style: normal; '
                'box-shadow: 0 2px 8px rgba(99, 102, 241, 0.1);'
            )
        elif alert_type == 'warning':
            blockquote['style'] = (
                'border-left: 5px solid #f59e0b; '
                'background: #fffbeb; '  # 淡黄色（微信不支持渐变）
                'padding: 20px 24px; '
                'margin: 30px 0; '
                'border-radius: 0 10px 10px 0; '
                'color: #92400e; '
                'font-style: normal; '
                'box-shadow: 0 2px 8px rgba(245, 158, 11, 0.1);'
            )
        elif alert_type == 'success':
            blockquote['style'] = (
                'border-left: 5px solid #10b981; '
                'background: #ecfdf5; '  # 淡绿色（微信不支持渐变）
                'padding: 20px 24px; '
                'margin: 30px 0; '
                'border-radius: 0 10px 10px 0; '
                'color: #065f46; '
                'font-style: normal; '
                'box-shadow: 0 2px 8px rgba(16, 185, 129, 0.1);'
            )
        elif alert_type == 'danger':
            blockquote['style'] = (
                'border-left: 5px solid #ef4444; '
                'background: #fef2f2; '  # 淡红色（微信不支持渐变）
                'padding: 20px 24px; '
                'margin: 30px 0; '
                'border-radius: 0 10px 10px 0; '
                'color: #991b1b; '
                'font-style: normal; '
                'box-shadow: 0 2px 8px rgba(239, 68, 68, 0.1);'
            )
        else:
            # 默认引用块 - 更醒目
            blockquote['style'] = (
                'border-left: 5px solid #a78bfa; '
                'background: #faf5ff; '  # 淡紫色（微信不支持渐变）
                'padding: 20px 24px; '
                'margin: 30px 0; '
                'color: #4b5563; '
                'font-style: italic; '
                'border-radius: 0 10px 10px 0; '
                'box-shadow: 0 2px 6px rgba(167, 139, 250, 0.1);'
            )

    # ==================== 表格大幅美化 ====================
    for table in soup.find_all('table'):
        table['style'] = (
            'border-collapse: collapse; '
            'width: 100%; '
            'margin: 20px 0; '
            'font-size: 15px; '
            'overflow-x: auto; '
            'display: block;'
        )

    for th in soup.find_all('th'):
        th['style'] = (
            'background: #7c3aed; '  # 纯色紫色背景（微信不支持渐变）
            'color: white; '
            'padding: 12px 16px; '
            'text-align: left; '
            'font-weight: 600; '
            'border: 1px solid #dee2e6; '
            'font-size: 15px; '
            'letter-spacing: 0.3px;'
        )

    # 表格行条纹 + hover效果模拟
    for tbody in soup.find_all('tbody'):
        rows = tbody.find_all('tr')
        for idx, tr in enumerate(rows):
            cells = tr.find_all('td')
            for td in cells:
                base_style = (
                    'padding: 12px 16px; '
                    'border: 1px solid #dee2e6; '
                    'color: #374151; '
                    'font-size: 14px; '
                    'line-height: 1.7;'
                )
                if idx % 2 == 0:
                    td['style'] = base_style + 'background: #f8f9fa;'
                else:
                    td['style'] = base_style + 'background: white;'

    # ==================== 分隔线美化 ====================
    for hr in soup.find_all('hr'):
        hr['style'] = (
            'border: none; '
            'height: 3px; '
            'background: #7c3aed; '  # 紫色（微信不支持渐变）
            'margin: 50px auto; '
            'width: 70%; '
            'opacity: 0.5; '
            'border-radius: 2px;'
        )

    # ==================== 链接美化 ====================
    for a in soup.find_all('a'):
        a['style'] = (
            'color: #3b82f6; '  # 蓝色（从紫色改为蓝色）
            'text-decoration: none; '
            'border-bottom: 2px solid #dbeafe; '  # 浅蓝下划线
            'padding-bottom: 2px; '
            'font-weight: 500;'
        )

    return str(soup)


def markdown_to_html(input_file, skip_h1=True):
    """将 Markdown 转换为 HTML"""

    # 读取 Markdown 文件
    with open(input_file, 'r', encoding='utf-8') as f:
        md_content = f.read()

    # 如果需要跳过 H1 标题
    if skip_h1:
        lines = md_content.split('\n')
        filtered_lines = []
        skip_next_empty = False

        for line in lines:
            if line.startswith('# ') and not line.startswith('## '):
                skip_next_empty = True
                continue
            if skip_next_empty and line.strip() == '':
                skip_next_empty = False
                continue
            skip_next_empty = False
            filtered_lines.append(line)

        md_content = '\n'.join(filtered_lines)

    # 转换为 HTML - 增强配置
    html = markdown.markdown(
        md_content,
        extensions=[
            'markdown.extensions.extra',
            'markdown.extensions.codehilite',
            'markdown.extensions.tables',
            'markdown.extensions.toc',
            'markdown.extensions.nl2br',
            'markdown.extensions.fenced_code',
        ],
        extension_configs={
            'markdown.extensions.codehilite': {
                'css_class': 'highlight',
                'linenums': False,
                'use_pygments': True,
                'noclasses': True,
                'pygments_style': 'monokai',
            }
        }
    )

    # 应用内联样式
    styled_html = apply_inline_styles(html)

    # 创建完整的 HTML 文档 - 更大的内边距
    full_html = f"""<!-- ⚠️ 标题请在微信公众号编辑器中单独填写 -->
<section style="font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, 'Helvetica Neue', Arial, 'PingFang SC', 'Microsoft YaHei', sans-serif; font-size: 16px; color: #374151; line-height: 1.8; padding: 30px 24px; background: #ffffff;">
{styled_html}
</section>"""

    return full_html


def main():
    parser = argparse.ArgumentParser(description='微信公众号文章格式化工具 v3.0')
    parser.add_argument('input', help='输入的 Markdown 文件路径')
    parser.add_argument('-o', '--output', help='输出的 HTML 文件路径')
    parser.add_argument('--keep-h1', action='store_true', help='保留 H1 标题')

    args = parser.parse_args()

    # 确定输出文件路径
    if args.output:
        output_file = args.output
    else:
        output_file = args.input.rsplit('.', 1)[0] + '_wechat.html'

    # 转换
    html = markdown_to_html(args.input, skip_h1=not args.keep_h1)

    # 保存
    with open(output_file, 'w', encoding='utf-8') as f:
        f.write(html)

    print(f"✅ 转换成功！（v3.0 专业排版版）")
    print(f"📄 输出文件：{output_file}")
    print(f"\n📋 发布步骤：")
    print(f"1. 在浏览器中打开：file://{output_file}")
    print(f"2. 按 Ctrl+A 全选，Ctrl+C 复制")
    print(f"3. 在微信公众号编辑器中粘贴")
    print(f"4. 在标题栏填写文章标题")
    print(f"5. 检查格式后发布")


if __name__ == '__main__':
    main()
