#!/usr/bin/env python3
"""
论文筛选结果可视化工具
将JSON格式的筛选结果转换为HTML并在本地浏览器中展示
"""

import json
import os
from http.server import HTTPServer, SimpleHTTPRequestHandler
import webbrowser
import threading
import time

class PaperViewer:
    """论文结果查看器"""
    
    def __init__(self, json_file: str = "filtered_papers_10.json"):
        """
        初始化查看器
        
        Args:
            json_file: JSON结果文件路径
        """
        self.json_file = json_file
        self.papers = []
        self.load_papers()
    
    def load_papers(self):
        """加载论文数据"""
        try:
            with open(self.json_file, 'r', encoding='utf-8') as f:
                self.papers = json.load(f)
            print(f"✅ 成功加载 {len(self.papers)} 篇论文数据")
        except FileNotFoundError:
            print(f"❌ 未找到文件: {self.json_file}")
            print("请先运行 paper_filter.py 生成筛选结果")
        except Exception as e:
            print(f"❌ 加载数据时出错: {e}")
    
    def generate_html(self) -> str:
        """生成HTML内容"""
        if not self.papers:
            return self.generate_error_html()
        
        # 生成论文卡片
        paper_cards = ""
        for i, paper in enumerate(self.papers, 1):
            title = paper.get('title', '未知标题')
            authors = paper.get('authors', '未知作者')
            
            # 处理摘要，如果太长则截断
            abstract = paper.get('abstract', '暂无摘要')
            if len(abstract) > 500:
                abstract = abstract[:500] + "..."
            
            # 获取各种分数
            similarity_score = paper.get('similarity_score', 0)
            rule_score = paper.get('rule_score', 0)
            final_score = paper.get('final_score', 0)
            
            # 计算进度条百分比（转换为0-100范围）
            similarity_percent = min(similarity_score * 100, 100)
            rule_percent = min(rule_score * 10, 100)  # rule_score通常在0-10范围
            final_percent = min(final_score * 100, 100)
            
            paper_card = f"""
            <div class="paper-card" data-search="{title.lower()} {authors.lower()} {abstract.lower()}">
                <div class="paper-rank">#{i}</div>
                <div class="paper-title">{title}</div>
                <div class="paper-authors"><strong>👥 作者:</strong> {authors}</div>
                
                <div class="scores">
                    <div class="score-item">
                        <span class="score-label">语义相似度</span>
                        <span class="score-value">{similarity_score:.4f}</span>
                    </div>
                    <div class="score-item">
                        <span class="score-label">规则分数</span>
                        <span class="score-value">{rule_score:.2f}</span>
                    </div>
                    <div class="score-item">
                        <span class="score-label">综合分数</span>
                        <span class="score-value">{final_score:.4f}</span>
                    </div>
                </div>
                
                <div class="progress-container">
                    <div class="progress-label">
                        <span>🎯 语义匹配度</span>
                        <span>{similarity_percent:.1f}%</span>
                    </div>
                    <div class="progress-bar">
                        <div class="progress-fill" style="width: {similarity_percent}%"></div>
                    </div>
                </div>
                
                <div class="progress-container">
                    <div class="progress-label">
                        <span>⚡ 规则匹配度</span>
                        <span>{rule_percent:.1f}%</span>
                    </div>
                    <div class="progress-bar">
                        <div class="progress-fill" style="width: {rule_percent}%"></div>
                    </div>
                </div>
                
                <div class="progress-container">
                    <div class="progress-label">
                        <span>🏆 综合匹配度</span>
                        <span>{final_percent:.1f}%</span>
                    </div>
                    <div class="progress-bar">
                        <div class="progress-fill" style="width: {final_percent}%"></div>
                    </div>
                </div>
                
                <div class="paper-abstract">
                    <strong>📝 摘要：</strong>{abstract}
                </div>
                
                <a href="{paper.get('url', '#')}" class="paper-link" target="_blank">
                    🔗 查看原文
                </a>
            </div>
            """
            paper_cards += paper_card
        
        # 计算统计信息
        total_papers = len(self.papers)
        avg_similarity = sum(paper.get('similarity_score', 0) for paper in self.papers) / total_papers if total_papers > 0 else 0
        max_score = max(paper.get('final_score', 0) for paper in self.papers) if self.papers else 0
        
        html_content = """<!DOCTYPE html>
<html lang="zh-CN">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>🎯 NDSS 2025 论文筛选结果</title>
    <link href="https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&family=JetBrains+Mono:wght@400;500&display=swap" rel="stylesheet">
    <style>
        * {
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }
        
        body {
            font-family: 'Inter', -apple-system, BlinkMacSystemFont, 'Segoe UI', 'Roboto', 'Helvetica Neue', Arial, sans-serif;
            line-height: 1.7;
            color: #1a202c;
            max-width: 1200px;
            margin: 0 auto;
            padding: 20px;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            min-height: 100vh;
            font-size: 16px;
        }
        
        .container {
            background: rgba(255, 255, 255, 0.95);
            backdrop-filter: blur(10px);
            border-radius: 20px;
            padding: 30px;
            box-shadow: 0 20px 40px rgba(0, 0, 0, 0.1);
        }
        
        .header {
            background: linear-gradient(135deg, #4f46e5 0%, #7c3aed 100%);
            color: white;
            padding: 40px 30px;
            border-radius: 16px;
            text-align: center;
            margin-bottom: 30px;
            box-shadow: 0 8px 32px rgba(79, 70, 229, 0.3);
            position: relative;
            overflow: hidden;
        }
        
        .header::before {
            content: '';
            position: absolute;
            top: 0;
            left: 0;
            right: 0;
            bottom: 0;
            background: url('data:image/svg+xml,<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 100 100"><defs><pattern id="grain" width="100" height="100" patternUnits="userSpaceOnUse"><circle cx="25" cy="25" r="1" fill="white" opacity="0.1"/><circle cx="75" cy="75" r="1" fill="white" opacity="0.1"/><circle cx="50" cy="10" r="0.5" fill="white" opacity="0.1"/><circle cx="10" cy="60" r="0.5" fill="white" opacity="0.1"/></pattern></defs><rect width="100" height="100" fill="url(%23grain)"/></svg>') repeat;
            pointer-events: none;
        }
        
        .header h1 {
            margin: 0;
            font-size: 3.2em;
            font-weight: 700;
            margin-bottom: 16px;
            position: relative;
            z-index: 1;
        }
        
        .header .subtitle {
            font-size: 1.5em;
            opacity: 0.95;
            font-weight: 400;
            position: relative;
            z-index: 1;
        }
        
        .stats {
            background: white;
            padding: 30px;
            border-radius: 16px;
            margin-bottom: 30px;
            box-shadow: 0 8px 32px rgba(0, 0, 0, 0.06);
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
            gap: 30px;
            text-align: center;
        }
        
        .stat-item {
            position: relative;
        }
        
        .stat-number {
            font-size: 2.8em;
            font-weight: 700;
            background: linear-gradient(135deg, #4f46e5 0%, #7c3aed 100%);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            background-clip: text;
            margin-bottom: 10px;
        }
        
        .stat-label {
            color: #374151;
            font-size: 1.1em;
            font-weight: 600;
            text-transform: uppercase;
            letter-spacing: 0.5px;
        }
        
        .search-box {
            background: white;
            padding: 25px;
            border-radius: 16px;
            margin-bottom: 25px;
            box-shadow: 0 8px 32px rgba(0, 0, 0, 0.06);
            position: relative;
        }
        
        .search-input {
            width: 100%;
            padding: 18px 22px 18px 55px;
            border: 2px solid #e2e8f0;
            border-radius: 12px;
            font-size: 18px;
            font-weight: 400;
            outline: none;
            transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
            background-color: #f8fafc;
            color: #1f2937;
        }
        
        .search-input:focus {
            border-color: #4f46e5;
            background-color: white;
            box-shadow: 0 0 0 3px rgba(79, 70, 229, 0.1);
        }
        
        .search-icon {
            position: absolute;
            left: 42px;
            top: 50%;
            transform: translateY(-50%);
            color: #374151;
            font-size: 20px;
        }
        
        .paper-list {
            background: white;
            border-radius: 16px;
            box-shadow: 0 8px 32px rgba(0, 0, 0, 0.06);
            overflow: hidden;
        }
        
        .paper-card {
            padding: 30px;
            border-bottom: 1px solid #f1f5f9;
            transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
            position: relative;
        }
        
        .paper-card:hover {
            background: linear-gradient(135deg, #f8fafc 0%, #f1f5f9 100%);
            transform: translateY(-2px);
        }
        
        .paper-card:last-child {
            border-bottom: none;
        }
        
        .paper-rank {
            display: inline-flex;
            align-items: center;
            justify-content: center;
            width: 50px;
            height: 50px;
            background: linear-gradient(135deg, #4f46e5 0%, #7c3aed 100%);
            color: white;
            border-radius: 50%;
            font-weight: 700;
            font-size: 1.1em;
            margin-bottom: 20px;
            box-shadow: 0 4px 16px rgba(79, 70, 229, 0.3);
        }
        
        .paper-title {
            font-size: 1.6em;
            font-weight: 600;
            color: #111827;
            margin-bottom: 15px;
            line-height: 1.4;
            letter-spacing: -0.01em;
        }
        
        .paper-authors {
            color: #374151;
            margin-bottom: 20px;
            font-size: 1.1em;
            font-weight: 500;
        }
        
        .scores {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(180px, 1fr));
            gap: 20px;
            margin-bottom: 25px;
        }
        
        .score-item {
            background: linear-gradient(135deg, #f8fafc 0%, #f1f5f9 100%);
            padding: 20px;
            border-radius: 12px;
            border: 1px solid #e2e8f0;
            text-align: center;
            transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
            position: relative;
            overflow: hidden;
        }
        
        .score-item:hover {
            transform: translateY(-2px);
            box-shadow: 0 8px 25px rgba(0, 0, 0, 0.1);
        }
        
        .score-label {
            font-size: 0.95em;
            color: #374151;
            display: block;
            margin-bottom: 10px;
            font-weight: 600;
            text-transform: uppercase;
            letter-spacing: 0.5px;
        }
        
        .score-value {
            font-weight: 700;
            color: #111827;
            font-size: 1.4em;
            font-family: 'JetBrains Mono', monospace;
        }
        
        .progress-container {
            margin: 20px 0;
            padding: 0;
        }
        
        .progress-label {
            display: flex;
            justify-content: space-between;
            align-items: center;
            margin-bottom: 10px;
            font-size: 1em;
            font-weight: 600;
            color: #374151;
        }
        
        .progress-bar {
            width: 100%;
            height: 10px;
            background-color: #e5e7eb;
            border-radius: 5px;
            overflow: hidden;
            position: relative;
        }
        
        .progress-fill {
            height: 100%;
            background: linear-gradient(90deg, #4f46e5 0%, #7c3aed 100%);
            border-radius: 5px;
            transition: width 1s cubic-bezier(0.4, 0, 0.2, 1);
            position: relative;
        }
        
        .progress-fill::after {
            content: '';
            position: absolute;
            top: 0;
            left: 0;
            bottom: 0;
            right: 0;
            background: linear-gradient(90deg, transparent 0%, rgba(255,255,255,0.3) 50%, transparent 100%);
            animation: shimmer 2s infinite;
        }
        
        @keyframes shimmer {
            0% {
                transform: translateX(-100%);
            }
            100% {
                transform: translateX(100%);
            }
        }
        
        .paper-abstract {
            background: linear-gradient(135deg, #f8fafc 0%, #f1f5f9 100%);
            padding: 22px;
            border-radius: 12px;
            margin: 20px 0;
            line-height: 1.8;
            color: #374151;
            border-left: 4px solid #4f46e5;
            font-size: 1.05em;
        }
        
        .paper-link {
            color: #4f46e5;
            text-decoration: none;
            font-size: 1.05em;
            font-weight: 600;
            display: inline-flex;
            align-items: center;
            gap: 10px;
            margin-top: 18px;
            padding: 14px 24px;
            border: 2px solid #4f46e5;
            border-radius: 8px;
            transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
        }
        
        .paper-link:hover {
            background: linear-gradient(135deg, #4f46e5 0%, #7c3aed 100%);
            color: white;
            text-decoration: none;
            transform: translateY(-2px);
            box-shadow: 0 8px 25px rgba(79, 70, 229, 0.3);
        }
        
        .no-results {
            text-align: center;
            color: #374151;
            padding: 60px 20px;
            font-style: italic;
            font-size: 1.2em;
        }
        
        @media (max-width: 768px) {
            body {
                padding: 15px;
            }
            
            .container {
                padding: 20px;
                border-radius: 16px;
            }
            
            .header h1 {
                font-size: 2.5em;
            }
            
            .stats {
                grid-template-columns: 1fr;
                gap: 20px;
                padding: 25px;
            }
            
            .scores {
                grid-template-columns: 1fr;
                gap: 15px;
            }
            
            .paper-card {
                padding: 25px 20px;
            }
            
            .search-input {
                padding: 16px 20px 16px 50px;
                font-size: 16px;
            }
            
            .search-icon {
                left: 38px;
            }
        }
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>🎯 NDSS 2025 论文筛选结果</h1>
            <div class="subtitle">基于密码学偏好的智能论文推荐系统</div>
        </div>
    
    <div class="stats">
        <div class="stat-item">
            <div class="stat-number">""" + str(total_papers) + """</div>
            <div class="stat-label">筛选论文数</div>
        </div>
        <div class="stat-item">
            <div class="stat-number">""" + f"{avg_similarity:.3f}" + """</div>
            <div class="stat-label">平均相似度</div>
        </div>
        <div class="stat-item">
            <div class="stat-number">""" + f"{max_score:.3f}" + """</div>
            <div class="stat-label">最高综合分数</div>
        </div>
    </div>
    
    <div class="search-box">
        <div class="search-icon">🔍</div>
        <input type="text" class="search-input" placeholder="搜索论文标题、作者或关键词..." onkeyup="filterPapers()">
    </div>
    
    <div class="paper-list" id="paperList">
        """ + paper_cards + """
    </div>
    
    <div class="no-results" id="noResults" style="display: none;">
        <div style="font-size: 3em; margin-bottom: 20px;">📭</div>
        <div>没有找到匹配的论文</div>
    </div>
    
    </div>
    
    <script>
        function filterPapers() {
            const input = document.querySelector('.search-input');
            const filter = input.value.toLowerCase();
            const paperList = document.getElementById('paperList');
            const papers = paperList.getElementsByClassName('paper-card');
            const noResults = document.getElementById('noResults');
            
            let visibleCount = 0;
            
            for (let i = 0; i < papers.length; i++) {
                const searchData = papers[i].getAttribute('data-search');
                if (searchData.indexOf(filter) > -1) {
                    papers[i].style.display = '';
                    visibleCount++;
                } else {
                    papers[i].style.display = 'none';
                }
            }
            
            if (visibleCount === 0 && filter !== '') {
                noResults.style.display = 'block';
                paperList.style.display = 'none';
            } else {
                noResults.style.display = 'none';
                paperList.style.display = 'block';
            }
        }
        
        // 添加论文链接点击事件
        document.querySelectorAll('.paper-link').forEach(link => {
            link.addEventListener('click', function(e) {
                e.preventDefault();
                window.open(this.href, '_blank');
            });
        });
        
        // 添加进度条动画
        window.addEventListener('load', function() {
            const progressBars = document.querySelectorAll('.progress-fill');
            progressBars.forEach((bar, index) => {
                setTimeout(() => {
                    bar.style.width = bar.style.width;
                }, index * 100);
            });
        });
    </script>
    
    <footer style="text-align: center; margin-top: 40px; padding: 30px; background: rgba(255,255,255,0.8); border-radius: 16px; backdrop-filter: blur(10px);">
        <p style="color: #374151; font-size: 1.05em; margin-bottom: 10px; font-weight: 500;">🔐 筛选偏好: 零知识证明、变色龙哈希、公钥密码学相关论文</p>
        <p style="color: #374151; font-size: 1em; font-weight: 500;">数据来源: NDSS Symposium 2025 官网</p>
    </footer>
</body>
</html>"""
        
        return html_content
    
    def generate_error_html(self) -> str:
        """生成错误页面HTML"""
        return """
<!DOCTYPE html>
<html lang="zh-CN">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>❌ 数据加载失败</title>
    <style>
        body {
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            background-color: #f5f5f5;
            min-height: 100vh;
            display: flex;
            align-items: center;
            justify-content: center;
            margin: 0;
            padding: 20px;
        }
        
        .error-container {
            background: white;
            padding: 50px;
            border-radius: 10px;
            text-align: center;
            box-shadow: 0 4px 6px rgba(0,0,0,0.1);
            max-width: 500px;
        }
        
        .error-icon {
            font-size: 4em;
            margin-bottom: 20px;
        }
        
        .error-title {
            font-size: 2em;
            color: #2c3e50;
            margin-bottom: 15px;
        }
        
        .error-message {
            color: #666;
            line-height: 1.6;
            margin-bottom: 30px;
        }
        
        .retry-button {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            padding: 12px 30px;
            border: none;
            border-radius: 5px;
            font-size: 16px;
            cursor: pointer;
            transition: all 0.3s ease;
        }
        
        .retry-button:hover {
            transform: translateY(-2px);
            box-shadow: 0 4px 8px rgba(102, 126, 234, 0.4);
        }
    </style>
</head>
<body>
    <div class="error-container">
        <div class="error-icon">😵</div>
        <h1 class="error-title">数据加载失败</h1>
        <p class="error-message">
            未找到论文筛选结果文件。<br>
            请先运行 <code>paper_filter.py</code> 生成筛选结果，<br>
            然后再使用此查看器。
        </p>
        <button class="retry-button" onclick="location.reload()">🔄 重新加载</button>
    </div>
</body>
</html>
        """
    
    def save_html(self, filename: str = "paper_results.html"):
        """保存HTML文件"""
        html_content = self.generate_html()
        with open(filename, 'w', encoding='utf-8') as f:
            f.write(html_content)
        print(f"✅ HTML文件已生成: {filename}")
        return filename
    
    def start_server(self, port: int = 8080):
        """启动本地服务器"""
        try:
            # 自定义HTTP处理器，直接提供动态HTML内容
            class PaperHandler(SimpleHTTPRequestHandler):
                def __init__(self, viewer, *args, **kwargs):
                    self.viewer = viewer
                    super().__init__(*args, **kwargs)
                
                def do_GET(self):
                    if self.path == '/' or self.path == '/index.html':
                        # 直接返回动态生成的HTML
                        html_content = self.viewer.generate_html()
                        self.send_response(200)
                        self.send_header('Content-type', 'text/html; charset=utf-8')
                        self.send_header('Content-length', len(html_content.encode('utf-8')))
                        self.end_headers()
                        self.wfile.write(html_content.encode('utf-8'))
                    else:
                        # 处理其他请求（如CSS, JS等静态文件）
                        super().do_GET()
                
                def log_message(self, format, *args):
                    pass  # 禁用日志输出
            
            # 创建处理器工厂函数
            def handler_factory(*args, **kwargs):
                return PaperHandler(self, *args, **kwargs)
            
            server = HTTPServer(('localhost', port), handler_factory)
            
            print(f"🌐 启动本地服务器: http://localhost:{port}")
            print(f"📄 访问页面: http://localhost:{port}/")
            print("⚡ 服务器正在运行... 按 Ctrl+C 停止")
            
            # 在后台启动服务器
            def run_server():
                server.serve_forever()
            
            server_thread = threading.Thread(target=run_server, daemon=True)
            server_thread.start()
            
            # 等待一秒后自动打开浏览器
            time.sleep(1)
            url = f"http://localhost:{port}/"
            print(f"🚀 正在打开浏览器...")
            webbrowser.open(url)
            
            try:
                # 保持主线程运行
                while True:
                    time.sleep(1)
            except KeyboardInterrupt:
                print("\n\n👋 服务器已停止")
                pass
                
        except OSError as e:
            if "Address already in use" in str(e):
                print(f"❌ 端口 {port} 已被占用，尝试使用端口 {port + 1}")
                self.start_server(port + 1)
            else:
                print(f"❌ 启动服务器失败: {e}")
        except Exception as e:
            print(f"❌ 发生错误: {e}")


def main():
    """主函数"""
    print("🎯 NDSS 2025 论文结果可视化工具")
    print("="*50)
    
    # 检查是否存在筛选结果文件
    json_files = [
        "filtered_papers_10.json",
        "filtered_papers_5.json", 
        "filtered_papers.json"
    ]
    
    json_file = None
    for file in json_files:
        if os.path.exists(file):
            json_file = file
            break
    
    if not json_file:
        print("❌ 未找到筛选结果文件")
        print("📝 请先运行 paper_filter.py 生成筛选结果")
        print("💡 或者将结果文件重命名为 filtered_papers_10.json")
        return
    
    print(f"📊 使用数据文件: {json_file}")
    
    # 创建查看器并启动服务器
    viewer = PaperViewer(json_file)
    if viewer.papers:
        print(f"📄 论文数据加载成功，共 {len(viewer.papers)} 篇论文")
        viewer.start_server()
    else:
        print("❌ 论文数据加载失败，无法启动服务器")


if __name__ == "__main__":
    main()
