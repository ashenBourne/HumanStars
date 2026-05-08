#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""诊断数据提取问题"""

import re
from pathlib import Path

BASE_DIR = "C:/Users/Administrator/.claude/skills/mao-ze-dong-perspective/references/sources/books"

def debug_first_article():
    md_file = Path(BASE_DIR) / "000-中国社会各阶级的分析.md"

    with open(md_file, 'r', encoding='utf-8') as f:
        content = f.read()

    print("=== 原始文件前500字 ===")
    print(content[:500])
    print("\n=== 提取日期 ===")

    # 方法1：提取括号内日期
    date_match = re.search(r'（(.+?)）', content[:200])
    if date_match:
        print(f"日期（括号内）：{date_match.group(1)}")
    else:
        print("未找到日期")

    # 方法2：提取年份
    year_match = re.search(r'([一二三四五六七八九零〇]{4})年', content[:500])
    if year_match:
        print(f"年份：{year_match.group(1)}")
    else:
        print("未找到中文年份")

    year_match2 = re.search(r'(\d{4})年', content[:500])
    if year_match2:
        print(f"阿拉伯年份：{year_match2.group(1)}")

    print("\n=== 正文提取测试 ===")
    # 测试正文提取
    main_text = content
    separator = re.search(r'\n\s*-{5,}', content)
    if separator:
        main_text = content[:separator.start()]

    lines = main_text.split('\n')
    cleaned_lines = []
    for line in lines:
        line = line.strip()
        if not line:
            continue
        if re.match(r'^#\s+', line):
            continue
        if line.startswith('>'):
            continue
        if re.match(r'^\s*-\s*$', line):
            continue
        cleaned_lines.append(line)

    main_text = ' '.join(cleaned_lines)

    print(f"正文长度：{len(main_text)} 字符")
    print(f"前500字：\n{main_text[:500]}")

    print("\n=== 搜索'我们' ===")
    we_count = len(re.findall(r'\b我们\b', main_text))
    print(f"'我们'出现次数：{we_count}")

    # 简单验证：检查是不是正文中真的有"我们"
    we_occurrences = re.findall(r'[^。]*\b我们\b[^。]*。', main_text[:2000])
    print(f"前2000字中的例子（最多5个）：")
    for i, occ in enumerate(we_occurrences[:5], 1):
        print(f"{i}. {occ}")

if __name__ == '__main__':
    debug_first_article()
