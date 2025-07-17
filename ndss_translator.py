#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
NDSS 2025 Paper List Translator
为NDSS 2025论文标题添加中文翻译
"""

import json
import time
import re
from typing import Dict, Any, List

try:
    from googletrans import Translator
    GOOGLETRANS_AVAILABLE = True
except ImportError:
    GOOGLETRANS_AVAILABLE = False
    print("googletrans库未安装，将尝试安装...")

def install_googletrans():
    """安装googletrans库"""
    import subprocess
    import sys
    
    try:
        subprocess.check_call([sys.executable, "-m", "pip", "install", "googletrans==4.0.0rc1"])
        print("googletrans库安装成功!")
        return True
    except subprocess.CalledProcessError:
        print("googletrans库安装失败，请手动安装: pip install googletrans==4.0.0rc1")
        return False

def clean_title_for_translation(title: str) -> str:
    """清理标题以便翻译"""
    # 移除末尾的省略号和不完整的标点
    title = re.sub(r'\.{3,}$', '', title)  # 移除省略号
    title = re.sub(r'\.\.\.$', '', title)  # 移除三个点
    title = re.sub(r'\s*with\s*$', '', title, flags=re.IGNORECASE)  # 移除末尾的"with"
    title = re.sub(r'\s*in\s*$', '', title, flags=re.IGNORECASE)  # 移除末尾的"in"
    title = re.sub(r'\s*for\s*$', '', title, flags=re.IGNORECASE)  # 移除末尾的"for"
    title = re.sub(r'\s*and\s*$', '', title, flags=re.IGNORECASE)  # 移除末尾的"and"
    title = re.sub(r'\s*of\s*$', '', title, flags=re.IGNORECASE)  # 移除末尾的"of"
    
    return title.strip()

def translate_text(text: str, translator: 'Translator') -> str:
    """翻译文本到中文"""
    try:
        # 清理文本
        cleaned_text = clean_title_for_translation(text)
        
        if not cleaned_text:
            return text
        
        # 翻译
        result = translator.translate(cleaned_text, src='en', dest='zh-cn')
        
        if result and result.text:
            return result.text
        else:
            return text
            
    except Exception as e:
        print(f"翻译失败 '{text[:50]}...': {e}")
        return text

def add_chinese_translations(json_file: str, output_file: str = None) -> bool:
    """为JSON文件中的论文标题添加中文翻译"""
    
    # 检查并安装googletrans
    global GOOGLETRANS_AVAILABLE
    if not GOOGLETRANS_AVAILABLE:
        if not install_googletrans():
            return False
        try:
            from googletrans import Translator
            GOOGLETRANS_AVAILABLE = True
        except ImportError:
            print("无法导入googletrans库")
            return False
    
    # 加载JSON文件
    try:
        with open(json_file, 'r', encoding='utf-8') as f:
            data = json.load(f)
    except Exception as e:
        print(f"读取JSON文件失败: {e}")
        return False
    
    # 初始化翻译器
    translator = Translator()
    
    # 翻译每个论文标题
    total_papers = len(data.get('papers', []))
    print(f"开始翻译 {total_papers} 篇论文标题...")
    
    for i, paper in enumerate(data.get('papers', []), 1):
        if 'title' in paper and paper['title']:
            original_title = paper['title']
            print(f"[{i}/{total_papers}] 翻译: {original_title[:60]}...")
            
            # 翻译标题
            chinese_title = translate_text(original_title, translator)
            paper['title_chinese'] = chinese_title
            
            # 添加延迟以避免API限制
            time.sleep(0.1)
            
            # 每10个请求显示进度
            if i % 10 == 0:
                print(f"进度: {i}/{total_papers} ({i/total_papers*100:.1f}%)")
    
    # 更新元数据
    data['description'] += " (with Chinese translations)"
    data['translation_date'] = "2025-07-17"
    
    # 保存结果
    output_file = output_file or json_file.replace('.json', '_translated.json')
    try:
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
        print(f"翻译完成! 结果保存到: {output_file}")
        return True
    except Exception as e:
        print(f"保存文件失败: {e}")
        return False

def display_sample_translations(json_file: str, count: int = 10):
    """显示翻译示例"""
    try:
        with open(json_file, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        papers = data.get('papers', [])
        print(f"\n前{count}篇论文标题翻译示例:")
        print("=" * 80)
        
        for i, paper in enumerate(papers[:count], 1):
            print(f"\n{i}. 英文: {paper.get('title', 'N/A')}")
            if 'title_chinese' in paper:
                print(f"   中文: {paper['title_chinese']}")
            if 'authors' in paper:
                authors = paper['authors'][:80] + "..." if len(paper['authors']) > 80 else paper['authors']
                print(f"   作者: {authors}")
            if 'url' in paper:
                print(f"   链接: {paper['url']}")
        
        print("=" * 80)
        print(f"总计: {len(papers)} 篇论文")
        translated_count = sum(1 for p in papers if 'title_chinese' in p)
        print(f"已翻译: {translated_count} 篇")
        
    except Exception as e:
        print(f"读取文件失败: {e}")

def main():
    """主函数"""
    input_file = "ndss2025_papers_clean.json"
    output_file = "ndss2025_papers_translated.json"
    
    print("NDSS 2025 论文标题翻译工具")
    print("=" * 50)
    
    # 执行翻译
    success = add_chinese_translations(input_file, output_file)
    
    if success:
        # 显示翻译示例
        display_sample_translations(output_file, 10)
    else:
        print("翻译过程中出现错误")

if __name__ == "__main__":
    main()
