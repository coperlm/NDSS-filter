import requests
from bs4 import BeautifulSoup
import json
import os
import time  # 添加时间模块用于延时

# --- 配置 ---
# 包含论文列表的本地 HTML 文件路径
# 请确保这个路径是正确的
LOCAL_HTML_FILE = '.\\NDSS Symposium 2025 Accepted Papers - NDSS Symposium.html'

# 保存提取数据的文件名
OUTPUT_FILE = 'ndss_papers_2025.json'

def get_paper_links(html_file_path):
    """解析本地 HTML 文件以查找所有论文详情页面的 URL。"""
    paper_links = []
    try:
        with open(html_file_path, 'r', encoding='utf-8') as f:
            soup = BeautifulSoup(f, 'html.parser')
        
        # 查找所有 class 为 'paper-link-abs' 的 'a' 标签
        links = soup.find_all('a', class_='paper-link-abs')
        for link in links:
            url = link.get('href')
            if url:
                paper_links.append(url)
        
        print(f"找到了 {len(paper_links)} 个论文链接。")
        return paper_links
    except FileNotFoundError:
        print(f"错误: 文件 '{html_file_path}' 未找到。")
        return []
    except Exception as e:
        print(f"解析 HTML 文件时出错: {e}")
        return []

def fetch_and_parse_paper_details(url):
    """获取论文详情页面并提取标题和摘要。"""
    try:
        print(f"正在获取: {url}")
        # 使用 User-Agent 伪装成浏览器
        headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'}
        response = requests.get(url, headers=headers, timeout=30)
        response.raise_for_status()  # 如果请求失败则抛出异常
        
        soup = BeautifulSoup(response.content, 'html.parser')
        
        # 调试：保存第一个页面的HTML到文件
        if "a-key-driven-framework" in url:
            with open('debug_page.html', 'w', encoding='utf-8') as f:
                f.write(soup.prettify())
            print("已保存调试页面到 debug_page.html")
        
        # --- 尝试多种选择器来查找标题 ---
        title = "未找到标题"
        # 尝试不同的标题选择器
        title_selectors = [
            ('h1', {'class': 'entry-title'}),
            ('h1', {'class': 'wp-block-heading'}),
            ('h1', {}),
            ('title', {}),
            ('.entry-title', {}),
            ('.page-title', {}),
            ('.post-title', {})
        ]
        
        for tag, attrs in title_selectors:
            if attrs:
                title_element = soup.find(tag, attrs)
            else:
                title_element = soup.find(tag)
            if title_element:
                title = title_element.get_text(strip=True)
                print(f"  找到标题使用选择器 {tag} {attrs}: {title[:50]}...")
                break
        
        # --- 查找作者信息 ---
        authors = "未找到作者"
        paper_data_div = soup.find('div', class_='paper-data')
        if paper_data_div:
            # 第一个 p 标签通常是作者信息
            p_tags = paper_data_div.find_all('p')
            if len(p_tags) >= 1:
                first_p = p_tags[0]
                authors = first_p.get_text(strip=True)
                print(f"  找到作者: {authors[:50]}...")
        
        # --- 查找摘要 ---
        abstract = "未找到摘要"
        
        # 方法1: 查找 paper-data div 下的段落
        if paper_data_div:
            # 查找第二个 p 标签（第一个通常是作者信息）
            p_tags = paper_data_div.find_all('p')
            if len(p_tags) >= 2:
                # 获取第二个 p 标签下的第一个 p 标签内容
                second_p = p_tags[1]
                inner_p = second_p.find('p')
                if inner_p:
                    abstract = inner_p.get_text(strip=True)
                    print(f"  找到摘要在 paper-data div: {abstract[:50]}...")
        
        # 方法2: 如果方法1失败，尝试在 entry-content 中查找较长的段落
        if abstract == "未找到摘要":
            entry_content = soup.find('div', class_='entry-content')
            if entry_content:
                # 查找所有 p 标签，选择最长的作为摘要
                all_paragraphs = entry_content.find_all('p')
                longest_text = ""
                for p in all_paragraphs:
                    text = p.get_text(strip=True)
                    # 跳过作者信息（通常包含大学名称或简短）
                    if (len(text) > len(longest_text) and 
                        len(text) > 200 and  # 摘要通常比较长
                        'University' not in text[:100] and  # 作者信息通常包含University
                        not any(name in text for name in ['Institute', 'College', 'Ltd', 'Inc', 'Corp'])):
                        longest_text = text
                if longest_text:
                    abstract = longest_text
                    print(f"  找到摘要在 entry-content (最长段落): {abstract[:50]}...")
        
        # 方法3: 如果还没找到，尝试查找包含 "Abstract" 文本的标题
        if abstract == "未找到摘要":
            abstract_patterns = ['abstract', 'Abstract', 'ABSTRACT']
            for pattern in abstract_patterns:
                abstract_heading = soup.find(['h2', 'h3', 'h4', 'strong', 'b'], string=lambda text: text and pattern in text)
                if abstract_heading:
                    # 查找紧随其后的段落
                    next_element = abstract_heading.find_next_sibling(['p', 'div'])
                    if next_element:
                        abstract = next_element.get_text(strip=True)
                        print(f"  找到摘要使用模式 '{pattern}': {abstract[:50]}...")
                        break
                    # 如果没有兄弟元素，尝试父元素的下一个兄弟
                    parent = abstract_heading.parent
                    if parent:
                        next_element = parent.find_next_sibling(['p', 'div'])
                        if next_element:
                            abstract = next_element.get_text(strip=True)
                            print(f"  找到摘要使用父元素方法: {abstract[:50]}...")
                            break

        return {'title': title, 'authors': authors, 'abstract': abstract, 'url': url}
        
    except requests.exceptions.RequestException as e:
        print(f"获取 {url} 时出错: {e}")
        return None
    except Exception as e:
        print(f"解析 {url} 时出错: {e}")
        return None

def main():
    """主函数，用于编排抓取过程。"""
    # 检查本地 HTML 文件是否存在
    if not os.path.exists(LOCAL_HTML_FILE):
        print(f"未在以下路径找到输入文件: {LOCAL_HTML_FILE}")
        print("请确保文件路径正确。")
        return

    paper_urls = get_paper_links(LOCAL_HTML_FILE)
    
    if not paper_urls:
        print("没有找到论文链接，脚本退出。")
        return
        
    all_papers_data = []

    # 只处理前10篇论文进行调试
    # paper_urls = paper_urls[:10]

    for i, url in enumerate(paper_urls):
        print(f"正在处理第 {i+1}/{len(paper_urls)} 篇论文")
        paper_data = fetch_and_parse_paper_details(url)
        if paper_data:
            all_papers_data.append(paper_data)
            print(f"  -> 标题: {paper_data['title']}")
            print(f"  -> 作者: {paper_data['authors'][:50]}...")
            print(f"  -> 摘要: {paper_data['abstract'][:100]}...")
            print(f"  -> 链接: {paper_data['url']}")
            print("-" * 50)
        
        # 添加延时避免请求过快
        if i < len(paper_urls) - 1:  # 最后一次不需要延时
            time.sleep(2)  # 每次请求间隔2秒

    # 将数据保存到 JSON 文件
    with open(OUTPUT_FILE, 'w', encoding='utf-8') as f:
        json.dump(all_papers_data, f, indent=4, ensure_ascii=False)
        
    print(f"\n成功提取了 {len(all_papers_data)} 篇论文的数据。")
    print(f"结果已保存到 '{OUTPUT_FILE}'。")

if __name__ == '__main__':
    print("开始运行 NDSS 2025 论文抓取脚本。")
    print("本脚本将获取每篇论文的标题和摘要。")
    print("请确保您已安装所需库: pip install requests beautifulsoup4")
    print("-" * 30)
    main()
