#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
NDSS 2025 Paper List Parser - 改进版
从MHTML文件中提取NDSS 2025已录用论文信息并转换为JSON格式
"""

import re
import json
import html
from typing import List, Dict, Any

def decode_quoted_printable(text: str) -> str:
    """解码quoted-printable编码的文本"""
    # 基本的quoted-printable解码
    text = re.sub(r'=([0-9A-F]{2})', lambda m: chr(int(m.group(1), 16)), text)
    text = text.replace('=\n', '')  # 移除软换行
    return text

def clean_html_text(text: str) -> str:
    """清理HTML标签和编码"""
    # 解码HTML实体
    text = html.unescape(text)
    # 移除HTML标签
    text = re.sub(r'<[^>]+>', '', text)
    # 清理多余的空白字符
    text = re.sub(r'\s+', ' ', text)
    return text.strip()

def extract_english_only(text: str) -> str:
    """只保留英文部分，移除中文翻译"""
    # 按换行符分割，通常英文在前，中文翻译在后
    parts = text.split('\n')
    if parts:
        english_part = parts[0].strip()
        # 移除箭头符号和重复内容
        english_part = re.sub(r'\s*-->\s*.*', '', english_part)
        
        # 使用更严格的方法：寻找第一个中文字符的位置，然后截断
        # 匹配任何非ASCII或扩展拉丁字符
        chinese_match = re.search(r'[^\x00-\x7F\u00C0-\u017F\u0100-\u024F\u1E00-\u1EFF]', english_part)
        if chinese_match:
            # 如果找到中文字符，截断到中文字符之前
            english_part = english_part[:chinese_match.start()]
        
        # 清理末尾的标点符号和空白字符
        english_part = re.sub(r'[,\.\s]+$', '', english_part)
        
        # 清理多余的空白字符
        english_part = re.sub(r'\s+', ' ', english_part)
        
        return english_part.strip()
    return text

def clean_url(url: str) -> str:
    """清理URL中的换行符"""
    return url.replace('\n', '').replace(' ', '')

def extract_paper_info_improved(mhtml_content: str) -> List[Dict[str, Any]]:
    """从MHTML内容中提取论文信息 - 改进版"""
    papers = []
    
    # 查找论文列表区域 - 使用更精确的模式
    paper_pattern = r'<div class=3D"tag-box rel-paper">(.*?)</div>\s*</div>\s*=20'
    paper_matches = re.findall(paper_pattern, mhtml_content, re.DOTALL)
    
    for paper_html in paper_matches:
        paper_info = {}
        
        # 提取论文标题
        title_pattern = r'<h3 class=3D"blog-post-title"[^>]*>(.*?)</h3>'
        title_match = re.search(title_pattern, paper_html, re.DOTALL)
        if title_match:
            title_raw = clean_html_text(decode_quoted_printable(title_match.group(1)))
            title = extract_english_only(title_raw)
            if title:
                paper_info['title'] = title
        
        # 提取作者信息
        author_pattern = r'<p[^>]*>(.*?)</p>'
        author_match = re.search(author_pattern, paper_html, re.DOTALL)
        if author_match:
            authors_raw = clean_html_text(decode_quoted_printable(author_match.group(1)))
            authors = extract_english_only(authors_raw)
            if authors:
                paper_info['authors'] = authors
        
        # 提取论文链接
        link_pattern = r'href=3D"([^"]+)"[^>]*><span>More Details'
        link_match = re.search(link_pattern, paper_html)
        if link_match:
            link = clean_url(link_match.group(1).replace('=', ''))
            if link:
                paper_info['url'] = link
        
        # 只添加有标题的论文
        if 'title' in paper_info and paper_info['title']:
            papers.append(paper_info)
    
    return papers

def parse_ndss_mhtml_improved(file_path: str) -> Dict[str, Any]:
    """解析NDSS MHTML文件 - 改进版"""
    try:
        with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
            content = f.read()
        
        # 提取论文信息
        papers = extract_paper_info_improved(content)
        
        # 构建结果
        result = {
            "conference": "NDSS Symposium 2025",
            "description": "Network and Distributed System Security Symposium 2025 Accepted Papers",
            "total_papers": len(papers),
            "extraction_date": "2025-07-17",
            "papers": papers
        }
        
        return result
        
    except Exception as e:
        print(f"解析文件时出错: {e}")
        return {}

def main():
    """主函数"""
    mhtml_file = "NDSS Symposium 2025 已录用论文 - NDSS Symposium --- NDSS Symposium 2025 Accepted Papers - NDSS Symposium.mhtml"
    
    print("正在解析NDSS 2025论文列表...")
    result = parse_ndss_mhtml_improved(mhtml_file)
    
    if result:
        # 保存为JSON文件
        output_file = "ndss2025_papers_clean.json"
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(result, f, ensure_ascii=False, indent=2)
        
        print(f"解析完成！")
        print(f"总共提取了 {result['total_papers']} 篇论文")
        print(f"结果已保存到: {output_file}")
        
        # 显示前几篇论文作为示例
        if result['papers']:
            print("\n前10篇论文示例:")
            for i, paper in enumerate(result['papers'][:10], 1):
                print(f"\n{i}. {paper.get('title', 'N/A')}")
                authors = paper.get('authors', 'N/A')
                if len(authors) > 80:
                    authors = authors[:80] + "..."
                print(f"   作者: {authors}")
                if 'url' in paper:
                    print(f"   链接: {paper['url']}")
    else:
        print("解析失败，请检查文件路径和格式。")

if __name__ == "__main__":
    main()
