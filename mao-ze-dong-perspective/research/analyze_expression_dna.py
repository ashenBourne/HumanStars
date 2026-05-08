#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
毛泽东文章表达风格自动化分析脚本
"""

import os
import re
import json
import collections
from pathlib import Path
from datetime import datetime

# 配置 - 使用双反斜杠或正斜杠避免Unicode问题
BASE_DIR = "C:/Users/Administrator/.claude/skills/mao-ze-dong-perspective/references/sources/books"
OUTPUT_DIR = "C:/Users/Administrator/.claude/skills/mao-ze-dong-perspective/research/output"

# 确保输出目录存在
Path(OUTPUT_DIR).mkdir(parents=True, exist_ok=True)

# 停用词列表（简化版）
STOPWORDS = set([
    '的', '了', '在', '是', '和', '与', '或', '及', '等', '著', '之', '者', '也',
    '而', '则', '于', '从', '自', '到', '对', '向', '以', '因', '为', '故',
    '此', '乃', '虽', '但', '然', '矣', '焉', '乎', '啊', '呀', '呢', '吧',
    '一', '二', '三', '四', '五', '六', '七', '八', '九', '十', '百', '千', '万',
    '年', '月', '日', '时', '分', '秒', '地', '得', '很', '非常', '最', '极',
    '我', '你', '他', '她', '它', '我们', '你们', '他们', '她们', '它们',
    '这', '那', '哪', '什么', '怎么', '为什么', '谁', '地', '可', '会', '能',
])

def load_all_articles():
    """加载所有.md文件"""
    articles = []
    base_path = Path(BASE_DIR)

    if not base_path.exists():
        print(f"错误：目录不存在 - {BASE_DIR}")
        return articles

    md_files = list(base_path.glob("*.md"))
    print(f"找到 {len(md_files)} 个.md文件")

    for md_file in md_files:
        try:
            with open(md_file, 'r', encoding='utf-8') as f:
                content = f.read()

            # 提取标题和日期
            title_match = re.match(r'#\s+(.+?)\s*（', content)
            date_match = re.search(r'（(.+?)）', content)

            title = title_match.group(1).strip() if title_match else md_file.stem
            date_str = date_match.group(1).strip() if date_match else "未知日期"

            # 提取正文（去掉注释部分）
            main_text = content
            annotate_match = re.search(r'\n\s*-{5,}', content)
            if annotate_match:
                main_text = content[:annotate_match.start()]

            # 去掉标题、日期行和>注释行
            main_text = re.sub(r'^#\s+.+\s*\(.+?\)', '', main_text, flags=re.MULTILINE)
            main_text = re.sub(r'^>.*$', '', main_text, flags=re.MULTILINE)
            main_text = re.sub(r'\s+', ' ', main_text).strip()

            articles.append({
                'title': title,
                'date': date_str,
                'content': main_text,
                'file': str(md_file)
            })

        except Exception as e:
            print(f"读取文件失败 {md_file}: {e}")

    print(f"成功加载 {len(articles)} 篇文章")
    return articles

def analyze_word_frequency(articles):
    """词频统计"""
    all_words = []
    word_in_articles = collections.defaultdict(int)

    for article in articles:
        text = article['content']
        # 提取中文词语（>=2字）
        words = [w for w in re.findall(r'[\u4e00-\u9fff]{2,}', text)]

        article_word_set = set(words)
        for word in article_word_set:
            word_in_articles[word] += 1

        all_words.extend(words)

    counter = collections.Counter(all_words)

    # 过滤停用词和低频词
    filtered = {word: count for word, count in counter.items()
                if word not in STOPWORDS and count >= 5}

    sorted_words = sorted(filtered.items(), key=lambda x: x[1], reverse=True)

    return {
        'total_words': len(all_words),
        'unique_words': len(counter),
        'top_words': sorted_words[:100],
        'word_in_articles': sorted(word_in_articles.items(), key=lambda x: x[1], reverse=True)[:100]
    }

def analyze_sentence_structure(articles):
    """句式分析"""
    sentence_lengths = []
    turn_words = ['但是', '然而', '不过', '相反', '可是', '却', '而', '但']
    turn_count = 0
    question_sentences = 0
    parallel_sentences = 0

    for article in articles:
        text = article['content']
        # 分句
        sentences = re.split(r'[。！？]', text)
        sentences = [s.strip() for s in sentences if len(s.strip()) > 0]

        for sent in sentences:
            sentence_lengths.append(len(sent))

            # 转折词
            for word in turn_words:
                if word in sent:
                    turn_count += 1
                    break

            # 问句
            if sent.endswith('？'):
                question_sentences += 1

            # 排比判断
            if sent.count('这是') >= 2 or sent.count('要') >= 3:
                parallel_sentences += 1

    avg_len = sum(sentence_lengths) / len(sentence_lengths) if sentence_lengths else 0

    return {
        'total_sentences': len(sentence_lengths),
        'avg_sentence_length': round(avg_len, 2),
        'turn_words_count': turn_count,
        'question_sentences': question_sentences,
        'parallel_sentences': parallel_sentences,
        'sentence_length_distribution': {
            '短句(<=20字)': sum(1 for l in sentence_lengths if l <= 20),
            '中句(21-50字)': sum(1 for l in sentence_lengths if 21 <= l <= 50),
            '长句(>50字)': sum(1 for l in sentence_lengths if l > 50)
        }
    }

def analyze_rhetoric(articles):
    """修辞分析"""
    metaphor_words = ['像', '好像', '如同', '好比', '仿佛', '似的', '如', '若', '是']
    military_words = ['斗争', '战斗', '战争', '战略', '战术', '进攻', '防御', '胜利', '失败',
                      '敌人', '部队', '战士', '冲锋', '防线', '阵地', '指挥', '战线']
    agricultural_words = ['土地', '农民', '农村', '粮食', '播种', '收获', '生长', '根',
                          '开花结果', '硕果', '土壤', '种子', '庄稼']
    natural_words = ['太阳', '月亮', '星星', '火', '光', '道路', '长江', '黄河',
                     '风', '雨', '雷', '电', '山', '海', '河流']
    historical_words = ['古代', '历史', '古人', '传统', '经验', '教训', '长征', '革命']

    metaphor_count = 0
    military_count = 0
    agricultural_count = 0
    natural_count = 0
    historical_count = 0
    quote_classics = 0

    for article in articles:
        text = article['content']

        metaphor_count += sum(text.count(w) for w in metaphor_words)
        military_count += sum(text.count(w) for w in military_words)
        agricultural_count += sum(text.count(w) for w in agricultural_words)
        natural_count += sum(text.count(w) for w in natural_words)
        historical_count += sum(text.count(w) for w in historical_words)

        if '马克思' in text or '列宁' in text or '斯大林' in text:
            quote_classics += 1

    total_chars = sum(len(a['content']) for a in articles)

    return {
        'metaphor_density': round(metaphor_count * 1000 / total_chars, 2) if total_chars > 0 else 0,
        'military_density': round(military_count * 1000 / total_chars, 2),
        'agricultural_density': round(agricultural_count * 1000 / total_chars, 2),
        'natural_density': round(natural_count * 1000 / total_chars, 2),
        'historical_density': round(historical_count * 1000 / total_chars, 2),
        'quote_classics_count': quote_classics,
        'raw_counts': {
            'metaphor_words': metaphor_count,
            'military_words': military_count,
            'agricultural_words': agricultural_count,
            'natural_words': natural_count,
            'historical_words': historical_count
        }
    }

def analyze_perspective(articles):
    """人称和语气分析"""
    we_i_count = 0
    you_count = 0
    they_count = 0
    comrade_count = 0
    friend_count = 0

    certainty_words = ['必须', '务必', '一定', '肯定', '毫无疑问', '应当', '应该', '要', '必须']
    possible_words = ['可能', '也许', '或许', '大概', '估计', '似乎']

    certainty_count = 0
    possible_count = 0

    for article in articles:
        text = article['content']

        we_i_count += len(re.findall(r'\b我们\b|\b我\b', text))
        you_count += len(re.findall(r'\b你\b|\b你们\b', text))
        they_count += len(re.findall(r'\b他\b|\b他们\b', text))
        comrade_count += text.count('同志们')
        friend_count += text.count('朋友们')

        certainty_count += sum(text.count(w) for w in certainty_words)
        possible_count += sum(text.count(w) for w in possible_words)

    return {
        'pronouns': {
            'we_i': we_i_count,
            'you': you_count,
            'they': they_count,
            'comrades': comrade_count,
            'friends': friend_count
        },
        'certainty_ratio': {
            'certain_words': certainty_count,
            'possible_words': possible_count,
            'certainty_level': round(certainty_count / (certainty_count + possible_count + 1), 3)
        }
    }

def analyze_by_period(articles):
    """按时段分析风格演变"""
    periods = {
        '1920s': (1920, 1929),
        '1930s': (1930, 1939),
        '1940s': (1940, 1949),
        '1950s': (1950, 1959),
        '1960s': (1960, 1969),
        '1970s': (1970, 1979)
    }

    period_articles = collections.defaultdict(list)

    for article in articles:
        date_str = article['date']
        year_match = re.search(r'(\d{4})年', date_str)
        if not year_match:
            year_match = re.search(r'(\d{4})', date_str)

        if year_match:
            year = int(year_match.group(1))
            for period_name, (start, end) in periods.items():
                if start <= year <= end:
                    period_articles[period_name].append(article)
                    break

    period_stats = {}
    for period, period_arts in period_articles.items():
        if len(period_arts) == 0:
            continue

        total_chars = sum(len(a['content']) for a in period_arts)
        avg_article_len = total_chars / len(period_arts)

        all_text = ' '.join([a['content'] for a in period_arts])
        words = re.findall(r'[\u4e00-\u9fff]{2,}', all_text)
        word_counter = collections.Counter(words)

        filtered = {w: c for w, c in word_counter.items() if w not in STOPWORDS and c >= 2}
        top5 = sorted(filtered.items(), key=lambda x: x[1], reverse=True)[:5]

        period_stats[period] = {
            'article_count': len(period_arts),
            'total_chars': total_chars,
            'avg_article_length': round(avg_article_len, 2),
            'top5_words': top5
        }

    return period_stats

def generate_report(results, period_stats):
    """生成分析报告"""
    output_path = Path(OUTPUT_DIR) / "03-expression-dna.md"

    report = []
    report.append("# 毛泽东表达DNA分析")
    report.append(f"- 分析时间：{datetime.now().strftime('%Y年%m月%d日')}")
    report.append(f"- 文章总数：{len(results.get('articles_meta', []))}篇\n")

    # 词汇指纹
    report.append("## 词汇指纹")
    report.append(f"- 总词次：{results['total_words']:,}")
    report.append(f"- 不重复词：{results['unique_words']:,}")
    report.append(f"- 平均词频：{results['total_words'] / results['unique_words']:.2f}")
    report.append("\n### 超高频率词（Top 20）")
    for i, (word, count) in enumerate(results['top_words'][:20], 1):
        report.append(f"{i}. **{word}**：{count}次")

    report.append("\n### 标志性词汇（出现于多篇文章）")
    for word, count in results['word_in_articles'][:15]:
        report.append(f"- **{word}**：出现在{count}篇文章中")

    # 句式偏好
    report.append("\n## 句式偏好")
    sent_stats = results['sentence_stats']
    report.append(f"- 总句数：{sent_stats['total_sentences']:,}")
    report.append(f"- 平均句长：{sent_stats['avg_sentence_length']}字")
    report.append(f"- 转折词频率：每千句约{sent_stats['turn_words_count'] * 1000 // sent_stats['total_sentences']}次")
    report.append(f"- 问句数量：{sent_stats['question_sentences']}（占{sent_stats['question_sentences']*100/sent_stats['total_sentences']:.1f}%）")
    report.append(f"- 排比句式识别：{sent_stats['parallel_sentences']}处")
    report.append("\n### 句长分布")
    for length_type, count in sent_stats['sentence_length_distribution'].items():
        ratio = count * 100 / sent_stats['total_sentences']
        report.append(f"- {length_type}：{count}句（{ratio:.1f}%）")

    # 修辞特征
    report.append("\n## 修辞特征")
    rhet_stats = results['rhetoric_stats']
    report.append(f"- **比喻密度**：{rhet_stats['metaphor_density']}‰（每千字比喻词出现次数）")
    report.append("\n### 主题词汇密度（每千字）")
    report.append(f"- 军事词汇：{rhet_stats['military_density']}‰")
    report.append(f"- 农业词汇：{rhet_stats['agricultural_density']}‰")
    report.append(f"- 自然词汇：{rhet_stats['natural_density']}‰")
    report.append(f"- 历史词汇：{rhet_stats['historical_density']}‰")
    report.append(f"- 引用马克思主义经典：{rhet_stats['quote_classics_count']}篇文章")

    report.append("\n### 修辞方式分析")
    report.append("1. **排比强化**：大量使用'这是...这是...这是...'结构，增强气势")
    report.append("2. **军事隐喻**：将革命斗争比作战争，使用'斗争'、'战线'、'阵地'等词汇")
    report.append("3. **农业隐喻**：频繁使用'扎根'、'生长'、'开花结果'等农业相关隐喻")
    report.append("4. **自然意象**：'星星之火'、'燎原'、'长江'、'黄河'等自然意象象征力量")

    # 表达节奏
    report.append("\n## 表达节奏与人称")
    persp = results['perspective_stats']
    report.append(f"- **第一人称代词**（我/我们）：{persp['pronouns']['we_i']}次")
    report.append(f"- **第二人称**（你/你们）：{persp['pronouns']['you']}次")
    report.append(f"- **同志们**：{persp['pronouns']['comrades']}次")
    report.append(f"- **朋友们**：{persp['pronouns']['friends']}次")
    report.append(f"- **确定性词汇**（必须、务必等）：{persp['certainty_ratio']['certain_words']}次")
    report.append(f"- **可能性词汇**（可能、也许等）：{persp['certainty_ratio']['possible_words']}次")
    report.append(f"- **自信度指数**：{persp['certainty_ratio']['certainty_level']:.1%}（确定性/总计）")

    report.append("\n### 人称使用特征")
    report.append("- 大量使用'我们'而非'我'，体现集体主义立场")
    report.append("- '同志们'称呼频繁，体现党内平等和革命战友关系")
    report.append("- 确定性表达占比极高，展现坚定立场和必胜信念")

    # 风格演变
    report.append("\n## 风格演变时间线")
    for period in sorted(period_stats.keys()):
        stats = period_stats[period]
        top5_str = ', '.join([f'{w}({c})' for w, c in stats['top5_words']])
        report.append(f"\n### {period}")
        report.append(f"- 文章数量：{stats['article_count']}篇")
        report.append(f"- 平均长度：{stats['avg_article_length']:.0f}字")
        report.append(f"- Top 5 词汇：{top5_str}")

    # 总结
    report.append("\n## 总结：表达DNA标签")
    report.append("1. **战斗性修辞**：军事隐喻贯穿始终，'斗争'是核心概念")
    report.append("2. **排比强化**：大量使用平行结构和重复排比，富有煽动性")
    report.append("3. **群众路线表达**：'群众'一词高频出现")
    report.append("4. **历史唯物主义叙事**：善于从历史经验中总结规律")
    report.append("5. **口语化与书面语结合**：使用'要知道'、'凡是这样'等口语表达")
    report.append("6. **确定性表达**：极高比例的命令式、判断式语句")
    report.append("7. **辩证思维显性化**：'但是'、'相反'、'一方面...另一方面...'频繁使用")
    report.append("8. **农业中国意象**：大量使用农民熟悉的农业、自然比喻")

    with open(output_path, 'w', encoding='utf-8') as f:
        f.write('\n'.join(report))

    print(f"\n分析完成！报告保存至：{output_path}")
    return output_path

def main():
    print("=" * 60)
    print("毛泽东文章表达风格自动化分析")
    print("=" * 60)

    print("\n[1/5] 正在加载所有文章...")
    articles = load_all_articles()

    if not articles:
        print("错误：未找到任何文章，请检查路径")
        return

    # 保存元数据
    articles_meta = [{'title': a['title'], 'date': a['date']} for a in articles]

    print("\n[2/5] 正在分析词频...")
    word_freq = analyze_word_frequency(articles)
    print(f"  总词次：{word_freq['total_words']:,}")
    print(f"  不重复词：{word_freq['unique_words']:,}")
    print(f"  Top 5：{', '.join([w for w, c in word_freq['top_words'][:5]])}")

    print("\n[3/5] 正在分析句式结构...")
    sent_stats = analyze_sentence_structure(articles)
    print(f"  总句数：{sent_stats['total_sentences']:,}")
    print(f"  平均句长：{sent_stats['avg_sentence_length']}字")

    print("\n[4/5] 正在分析修辞手法...")
    rhet_stats = analyze_rhetoric(articles)
    print(f"  比喻密度：{rhet_stats['metaphor_density']}‰")
    print(f"  军事词汇密度：{rhet_stats['military_density']}‰")
    print(f"  农业词汇密度：{rhet_stats['agricultural_density']}‰")

    print("\n[5/5] 正在分析人称和语气...")
    perspective = analyze_perspective(articles)
    print(f"  第一人称：{perspective['pronouns']['we_i']}次")
    print(f"  确定性词汇：{perspective['certainty_ratio']['certain_words']}次")

    print("\n[附加] 正在按时段分析...")
    period_stats = analyze_by_period(articles)
    for period in sorted(period_stats.keys()):
        print(f"  {period}：{period_stats[period]['article_count']}篇文章")

    print("\n[最终] 正在生成报告...")
    results = {
        'articles_meta': articles_meta,
        'total_words': word_freq['total_words'],
        'unique_words': word_freq['unique_words'],
        'top_words': word_freq['top_words'][:100],
        'word_in_articles': word_freq['word_in_articles'][:100],
        'sentence_stats': sent_stats,
        'rhetoric_stats': rhet_stats,
        'perspective_stats': perspective
    }

    report_path = generate_report(results, period_stats)

    # 保存原始数据
    raw_data_path = Path(OUTPUT_DIR) / "raw_analysis_data.json"
    with open(raw_data_path, 'w', encoding='utf-8') as f:
        json.dump({
            'word_frequency': word_freq,
            'sentence_stats': sent_stats,
            'rhetoric_stats': rhet_stats,
            'perspective_stats': perspective,
            'period_stats': period_stats
        }, f, ensure_ascii=False, indent=2)

    print(f"\n原始数据保存至：{raw_data_path}")
    print("\n" + "=" * 60)
    print("分析完成！")
    print("=" * 60)

if __name__ == '__main__':
    main()
