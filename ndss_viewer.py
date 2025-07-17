#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
NDSS 2025 Paper List Viewer
查看和展示NDSS 2025翻译后的论文列表
"""

import json
import html
from datetime import datetime

def generate_html_report(json_file: str, output_file: str = "ndss2025_papers_report.html"):
    """生成HTML格式的论文报告"""
    try:
        with open(json_file, 'r', encoding='utf-8') as f:
            data = json.load(f)
    except Exception as e:
        print(f"读取JSON文件失败: {e}")
        return False
    
    papers = data.get('papers', [])
    total_papers = data.get('total_papers', len(papers))
    
    # HTML模板
    html_content = f"""
<!DOCTYPE html>
<html lang="zh-CN">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>NDSS Symposium 2025 已录用论文列表</title>
    <style>
        body {{
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            line-height: 1.6;
            color: #333;
            max-width: 1200px;
            margin: 0 auto;
            padding: 20px;
            background-color: #f5f5f5;
        }}
        
        .header {{
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            padding: 30px;
            border-radius: 10px;
            text-align: center;
            margin-bottom: 30px;
            box-shadow: 0 4px 6px rgba(0,0,0,0.1);
        }}
        
        .header h1 {{
            margin: 0;
            font-size: 2.5em;
            font-weight: 300;
        }}
        
        .stats {{
            background: white;
            padding: 20px;
            border-radius: 8px;
            margin-bottom: 30px;
            box-shadow: 0 2px 4px rgba(0,0,0,0.1);
            display: flex;
            justify-content: space-around;
            text-align: center;
        }}
        
        .stat-item {{
            flex: 1;
        }}
        
        .stat-number {{
            font-size: 2em;
            font-weight: bold;
            color: #667eea;
        }}
        
        .paper-list {{
            background: white;
            border-radius: 8px;
            box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        }}
        
        .paper-item {{
            padding: 25px;
            border-bottom: 1px solid #eee;
            transition: background-color 0.3s ease;
        }}
        
        .paper-item:hover {{
            background-color: #f8f9fa;
        }}
        
        .paper-item:last-child {{
            border-bottom: none;
        }}
        
        .paper-number {{
            color: #666;
            font-weight: bold;
            margin-bottom: 10px;
        }}
        
        .paper-title-en {{
            font-size: 1.2em;
            font-weight: 600;
            color: #2c3e50;
            margin-bottom: 8px;
            line-height: 1.4;
        }}
        
        .paper-title-zh {{
            font-size: 1.1em;
            color: #e74c3c;
            margin-bottom: 12px;
            font-weight: 500;
        }}
        
        .paper-authors {{
            color: #666;
            margin-bottom: 8px;
            font-size: 0.95em;
        }}
        
        .paper-url {{
            margin-top: 10px;
        }}
        
        .paper-url a {{
            color: #3498db;
            text-decoration: none;
            font-size: 0.9em;
        }}
        
        .paper-url a:hover {{
            text-decoration: underline;
        }}
        
        .search-box {{
            background: white;
            padding: 20px;
            border-radius: 8px;
            margin-bottom: 20px;
            box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        }}
        
        .search-box input {{
            width: 100%;
            padding: 12px;
            border: 1px solid #ddd;
            border-radius: 5px;
            font-size: 16px;
        }}
        
        .no-results {{
            text-align: center;
            color: #666;
            padding: 40px;
            font-style: italic;
        }}
    </style>
</head>
<body>
    <div class="header">
        <h1>NDSS Symposium 2025</h1>
        <p>Network and Distributed System Security Symposium</p>
        <p>已录用论文列表 (中英文对照)</p>
    </div>
    
    <div class="stats">
        <div class="stat-item">
            <div class="stat-number">{total_papers}</div>
            <div>论文总数</div>
        </div>
        <div class="stat-item">
            <div class="stat-number">{sum(1 for p in papers if 'url' in p)}</div>
            <div>有链接的论文</div>
        </div>
        <div class="stat-item">
            <div class="stat-number">{sum(1 for p in papers if 'title_chinese' in p)}</div>
            <div>已翻译论文</div>
        </div>
    </div>
    
    <div class="search-box">
        <input type="text" id="searchInput" placeholder="搜索论文标题、作者或关键词..." onkeyup="searchPapers()">
    </div>
    
    <div class="paper-list" id="paperList">
"""
    
    # 添加每篇论文
    for i, paper in enumerate(papers, 1):
        title_en = html.escape(paper.get('title', 'N/A'))
        title_zh = html.escape(paper.get('title_chinese', ''))
        authors = html.escape(paper.get('authors', 'N/A'))
        
        # 清理作者信息，移除残留的特殊字符
        authors = authors.replace('ï', '').replace('ç', '').replace('å', '').strip()
        if len(authors) > 150:
            authors = authors[:150] + "..."
        
        html_content += f"""
        <div class="paper-item" data-search="{title_en.lower()} {title_zh.lower()} {authors.lower()}">
            <div class="paper-number">#{i}</div>
            <div class="paper-title-en">{title_en}</div>
            {f'<div class="paper-title-zh">{title_zh}</div>' if title_zh else ''}
            <div class="paper-authors"><strong>作者:</strong> {authors}</div>
            {f'<div class="paper-url"><a href="{paper["url"]}" target="_blank">查看详情</a></div>' if 'url' in paper else ''}
        </div>
"""
    
    # 结束HTML
    html_content += f"""
    </div>
    
    <div class="no-results" id="noResults" style="display: none;">
        没有找到匹配的论文
    </div>
    
    <script>
        function searchPapers() {{
            const input = document.getElementById('searchInput');
            const filter = input.value.toLowerCase();
            const paperList = document.getElementById('paperList');
            const papers = paperList.getElementsByClassName('paper-item');
            const noResults = document.getElementById('noResults');
            
            let visibleCount = 0;
            
            for (let i = 0; i < papers.length; i++) {{
                const searchData = papers[i].getAttribute('data-search');
                if (searchData.indexOf(filter) > -1) {{
                    papers[i].style.display = '';
                    visibleCount++;
                }} else {{
                    papers[i].style.display = 'none';
                }}
            }}
            
            if (visibleCount === 0 && filter !== '') {{
                noResults.style.display = 'block';
                paperList.style.display = 'none';
            }} else {{
                noResults.style.display = 'none';
                paperList.style.display = 'block';
            }}
        }}
    </script>
    
    <footer style="text-align: center; margin-top: 40px; color: #666; font-size: 0.9em;">
        <p>数据提取时间: {data.get('extraction_date', 'N/A')} | 翻译时间: {data.get('translation_date', 'N/A')}</p>
        <p>数据来源: NDSS Symposium 官网</p>
    </footer>
</body>
</html>
"""
    
    # 保存HTML文件
    try:
        with open(output_file, 'w', encoding='utf-8') as f:
            f.write(html_content)
        print(f"HTML报告已生成: {output_file}")
        return True
    except Exception as e:
        print(f"保存HTML文件失败: {e}")
        return False

def main():
    """主函数"""
    json_file = "ndss2025_papers_translated.json"
    html_file = "ndss2025_papers_report.html"
    
    print("生成NDSS 2025论文HTML报告...")
    
    if generate_html_report(json_file, html_file):
        print("报告生成成功!")
        print(f"请打开 {html_file} 查看完整的论文列表")
        
        # 显示一些统计信息
        try:
            with open(json_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            papers = data.get('papers', [])
            print(f"\n统计信息:")
            print(f"- 论文总数: {len(papers)}")
            print(f"- 有中文翻译: {sum(1 for p in papers if 'title_chinese' in p)}")
            print(f"- 有链接: {sum(1 for p in papers if 'url' in p)}")
            print(f"- 有作者信息: {sum(1 for p in papers if 'authors' in p)}")
            
        except Exception as e:
            print(f"读取统计信息失败: {e}")
    else:
        print("报告生成失败")

if __name__ == "__main__":
    main()
