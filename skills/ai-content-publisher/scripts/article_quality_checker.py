#!/usr/bin/env python3
"""
文章质量自动评分系统
根据多个维度评估文章质量，低分文章自动重新生成
"""

import os
import re
import yaml
from pathlib import Path


class ArticleQualityChecker:
    """文章质量检查器"""

    def __init__(self, config_path=None):
        """初始化检查器"""
        if config_path is None:
            script_dir = Path(__file__).parent
            config_path = script_dir.parent / 'config' / 'quality_rules.yaml'

        with open(config_path, 'r', encoding='utf-8') as f:
            self.config = yaml.safe_load(f)

        self.thresholds = self.config['thresholds']
        self.dimensions = self.config['dimensions']
        self.penalties = self.config['penalties']

    def check_article(self, article_path):
        """
        检查文章质量

        Args:
            article_path: 文章文件路径

        Returns:
            (score, details, passed)
        """
        # 读取文章
        with open(article_path, 'r', encoding='utf-8') as f:
            content = f.read()

        # 计算各维度得分
        scores = {}
        details = []

        # 1. 实用性评分
        prac_score, prac_details = self._check_practicality(content)
        scores['practicality'] = prac_score
        details.extend(prac_details)

        # 2. 深度分析评分
        depth_score, depth_details = self._check_depth(content)
        scores['depth'] = depth_score
        details.extend(depth_details)

        # 3. 结构完整性评分
        struct_score, struct_details = self._check_structure(content)
        scores['structure'] = struct_score
        details.extend(struct_details)

        # 4. 可读性评分
        read_score, read_details = self._check_readability(content)
        scores['readability'] = read_score
        details.extend(read_details)

        # 5. 原创性评分
        orig_score, orig_details = self._check_originality(content)
        scores['originality'] = orig_score
        details.extend(orig_details)

        # 6. 扣分项
        penalty_score, penalty_details = self._check_penalties(content)
        details.extend(penalty_details)

        # 总分
        total_score = sum(scores.values()) + penalty_score
        total_score = max(0, min(100, total_score))  # 限制在0-100之间

        # 判断是否通过
        passed = total_score >= self.thresholds['poor']

        return total_score, details, passed

    def _check_practicality(self, content):
        """检查实用性"""
        score = 0
        details = []
        rules = self.dimensions['practicality']['rules']

        for rule in rules:
            if self._contains_keywords(content, rule['keywords']):
                score += rule['score']
                details.append(f"✅ {rule['name']} (+{rule['score']}分)")
            else:
                details.append(f"❌ {rule['name']} (0分)")

        return score, details

    def _check_depth(self, content):
        """检查深度"""
        score = 0
        details = []
        rules = self.dimensions['depth']['rules']

        # 字数检查
        word_count = len(content)
        if word_count >= rules[0]['min_words']:
            score += rules[0]['score']
            details.append(f"✅ {rules[0]['name']} ({word_count}字, +{rules[0]['score']}分)")
        else:
            details.append(f"❌ {rules[0]['name']} ({word_count}字 < {rules[0]['min_words']}字, 0分)")

        # 技术细节检查
        if self._contains_keywords(content, rules[1]['keywords']):
            score += rules[1]['score']
            details.append(f"✅ {rules[1]['name']} (+{rules[1]['score']}分)")
        else:
            details.append(f"❌ {rules[1]['name']} (0分)")

        # 对比分析检查
        if self._contains_keywords(content, rules[2]['keywords']):
            score += rules[2]['score']
            details.append(f"✅ {rules[2]['name']} (+{rules[2]['score']}分)")
        else:
            details.append(f"❌ {rules[2]['name']} (0分)")

        return score, details

    def _check_structure(self, content):
        """检查结构"""
        score = 0
        details = []
        rules = self.dimensions['structure']['rules']

        # 引言检查
        lines = content.split('\n')
        first_para = []
        for line in lines:
            line = line.strip()
            if line and not line.startswith('#'):
                first_para.append(line)
                if len(' '.join(first_para)) >= rules[0]['min_length']:
                    break

        if len(' '.join(first_para)) >= rules[0]['min_length']:
            score += rules[0]['score']
            details.append(f"✅ {rules[0]['name']} (+{rules[0]['score']}分)")
        else:
            details.append(f"❌ {rules[0]['name']} (0分)")

        # 小标题检查
        heading_count = content.count('##')
        if heading_count >= rules[1]['min_count']:
            score += rules[1]['score']
            details.append(f"✅ {rules[1]['name']} ({heading_count}个, +{rules[1]['score']}分)")
        else:
            details.append(f"❌ {rules[1]['name']} ({heading_count}个 < {rules[1]['min_count']}个, 0分)")

        # 总结检查
        if self._contains_keywords(content, rules[2]['keywords']):
            score += rules[2]['score']
            details.append(f"✅ {rules[2]['name']} (+{rules[2]['score']}分)")
        else:
            details.append(f"❌ {rules[2]['name']} (0分)")

        return score, details

    def _check_readability(self, content):
        """检查可读性"""
        score = 0
        details = []
        rules = self.dimensions['readability']['rules']

        # 段落长度检查
        paragraphs = [p.strip() for p in content.split('\n\n') if p.strip() and not p.strip().startswith('#')]
        if paragraphs:
            avg_length = sum(len(p) for p in paragraphs) / len(paragraphs)
            if avg_length <= rules[0]['max_length']:
                score += rules[0]['score']
                details.append(f"✅ {rules[0]['name']} (平均{int(avg_length)}字, +{rules[0]['score']}分)")
            else:
                details.append(f"⚠️  {rules[0]['name']} (平均{int(avg_length)}字 > {rules[0]['max_length']}字, 0分)")

        # 列表/表格检查
        if self._contains_keywords(content, rules[1]['keywords']):
            score += rules[1]['score']
            details.append(f"✅ {rules[1]['name']} (+{rules[1]['score']}分)")
        else:
            details.append(f"❌ {rules[1]['name']} (0分)")

        return score, details

    def _check_originality(self, content):
        """检查原创性"""
        score = 0
        details = []
        rules = self.dimensions['originality']['rules']

        # 非简单翻译
        if not self._contains_keywords(content, rules[0]['avoid_keywords']):
            score += rules[0]['score']
            details.append(f"✅ {rules[0]['name']} (+{rules[0]['score']}分)")
        else:
            details.append(f"❌ {rules[0]['name']} (0分)")

        # 独特见解
        if self._contains_keywords(content, rules[1]['keywords']):
            score += rules[1]['score']
            details.append(f"✅ {rules[1]['name']} (+{rules[1]['score']}分)")
        else:
            details.append(f"❌ {rules[1]['name']} (0分)")

        return score, details

    def _check_penalties(self, content):
        """检查扣分项"""
        penalty = 0
        details = []

        for rule in self.penalties:
            if rule['name'] == "大量空话":
                count = sum(1 for kw in rule['keywords'] if kw in content)
                if count > rule.get('max_occurrences', 2):
                    penalty += rule['penalty']
                    details.append(f"⚠️  {rule['name']} ({count}处, {rule['penalty']}分)")

        return penalty, details

    def _contains_keywords(self, text, keywords):
        """检查是否包含关键词"""
        text_lower = text.lower()
        return any(kw.lower() in text_lower for kw in keywords)


def main():
    """主函数"""
    import sys

    if len(sys.argv) < 2:
        print("用法: article_quality_checker.py <文章路径>")
        sys.exit(1)

    article_path = sys.argv[1]

    if not os.path.exists(article_path):
        print(f"❌ 文章文件不存在: {article_path}")
        sys.exit(1)

    # 创建检查器
    checker = ArticleQualityChecker()

    # 检查文章
    print(f"\n📝 正在检查文章质量: {os.path.basename(article_path)}")
    print("=" * 60)

    score, details, passed = checker.check_article(article_path)

    # 输出详细结果
    print("\n📊 评分详情：\n")
    for detail in details:
        print(f"   {detail}")

    print("\n" + "=" * 60)
    print(f"\n🎯 总分：{score}/100")

    if score >= 85:
        print("✅ 质量评级：优秀")
    elif score >= 70:
        print("✅ 质量评级：合格")
    else:
        print("❌ 质量评级：不合格（需要重新生成）")

    print("=" * 60 + "\n")

    # 返回状态码
    sys.exit(0 if passed else 1)


if __name__ == '__main__':
    main()
