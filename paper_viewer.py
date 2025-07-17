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
            # 处理摘要，如果太长则截断
            abstract = paper.get('abstract', '暂无摘要')
            if len(abstract) > 500:
                abstract = abstract[:500] + "..."
            
            paper_card = f"""
            <div class="paper-card">
                <div class="paper-rank">#{i}</div>
                <div class="paper-title">{paper.get('title', '未知标题')}</div>
                <div class="paper-authors">👥 {paper.get('authors', '未知作者')}</div>
                
                <div class="scores">
                    <div class="score-item">
                        <span class="score-label">语义相似度</span>
                        <span class="score-value">{paper.get('similarity_score', 0):.4f}</span>
                    </div>
                    <div class="score-item">
                        <span class="score-label">规则分数</span>
                        <span class="score-value">{paper.get('rule_score', 0):.2f}</span>
                    </div>
                    <div class="score-item">
                        <span class="score-label">综合分数</span>
                        <span class="score-value">{paper.get('final_score', 0):.4f}</span>
                    </div>
                </div>
                
                <div class="paper-abstract">
                    📝 <strong>摘要：</strong>{abstract}
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
    <style>
        * {
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }
        
        body {
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            line-height: 1.6;
            color: #333;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            min-height: 100vh;
            padding: 20px;
        }
        
        .container {
            max-width: 1200px;
            margin: 0 auto;
            background: white;
            border-radius: 15px;
            box-shadow: 0 20px 40px rgba(0,0,0,0.1);
            overflow: hidden;
        }
        
        .header {
            background: linear-gradient(135deg, #2c3e50 0%, #3498db 100%);
            color: white;
            padding: 30px;
            text-align: center;
        }
        
        .header h1 {
            font-size: 2.5em;
            margin-bottom: 10px;
            text-shadow: 2px 2px 4px rgba(0,0,0,0.3);
        }
        
        .header .subtitle {
            font-size: 1.2em;
            opacity: 0.9;
        }
        
        .stats {
            background: #f8f9fa;
            padding: 20px;
            display: flex;
            justify-content: space-around;
            border-bottom: 1px solid #e9ecef;
        }
        
        .stat-item {
            text-align: center;
        }
        
        .stat-number {
            font-size: 2em;
            font-weight: bold;
            color: #3498db;
        }
        
        .stat-label {
            color: #666;
            font-size: 0.9em;
        }
        
        .paper-list {
            padding: 30px;
        }
        
        .paper-card {
            background: white;
            border: 1px solid #e9ecef;
            border-radius: 10px;
            margin-bottom: 25px;
            padding: 25px;
            box-shadow: 0 5px 15px rgba(0,0,0,0.08);
            transition: transform 0.3s ease, box-shadow 0.3s ease;
            position: relative;
        }
        
        .paper-card:hover {
            transform: translateY(-2px);
            box-shadow: 0 10px 25px rgba(0,0,0,0.15);
        }
        
        .paper-rank {
            position: absolute;
            top: -10px;
            left: 20px;
            background: linear-gradient(135deg, #ff6b6b, #ee5a52);
            color: white;
            padding: 5px 15px;
            border-radius: 20px;
            font-weight: bold;
            font-size: 0.9em;
        }
        
        .paper-title {
            font-size: 1.4em;
            font-weight: bold;
            color: #2c3e50;
            margin: 15px 0 10px 0;
            line-height: 1.3;
        }
        
        .paper-authors {
            color: #666;
            margin-bottom: 15px;
            font-style: italic;
        }
        
        .scores {
            display: flex;
            gap: 20px;
            margin-bottom: 15px;
            flex-wrap: wrap;
        }
        
        .score-item {
            background: #f8f9fa;
            padding: 8px 12px;
            border-radius: 6px;
            border-left: 4px solid #3498db;
        }
        
        .score-label {
            font-size: 0.8em;
            color: #666;
            display: block;
        }
        
        .score-value {
            font-weight: bold;
            color: #2c3e50;
            font-size: 1.1em;
        }
        
        .paper-abstract {
            background: #f8f9fa;
            padding: 15px;
            border-radius: 6px;
            margin: 15px 0;
            line-height: 1.7;
            color: #444;
        }
        
        .paper-link {
            display: inline-block;
            background: linear-gradient(135deg, #3498db, #2980b9);
            color: white;
            padding: 10px 20px;
            text-decoration: none;
            border-radius: 6px;
            transition: all 0.3s ease;
            font-weight: 500;
        }
        
        .paper-link:hover {
            background: linear-gradient(135deg, #2980b9, #21618c);
            transform: translateY(-1px);
            box-shadow: 0 5px 15px rgba(52, 152, 219, 0.4);
        }
        
        .search-box {
            margin: 20px 0;
            padding: 0 30px;
        }
        
        .search-input {
            width: 100%;
            padding: 12px 20px;
            border: 2px solid #e9ecef;
            border-radius: 25px;
            font-size: 16px;
            outline: none;
            transition: border-color 0.3s ease;
        }
        
        .search-input:focus {
            border-color: #3498db;
        }
        
        @media (max-width: 768px) {
            .header h1 {
                font-size: 2em;
            }
            
            .stats {
                flex-direction: column;
                gap: 15px;
            }
            
            .scores {
                flex-direction: column;
            }
            
            .paper-list {
                padding: 20px;
            }
            
            .paper-card {
                padding: 20px;
            }
        }
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>🎯 NDSS 2025 论文筛选结果</h1>
            <div class="subtitle">基于AI语义分析的智能论文推荐系统</div>
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
            <input type="text" class="search-input" placeholder="🔍 搜索论文标题、作者或关键词..." onkeyup="filterPapers()">
        </div>
        
        <div class="paper-list">
            """ + paper_cards + """
        </div>
    </div>
    
    <script>
        function filterPapers() {
            const input = document.querySelector('.search-input');
            const filter = input.value.toLowerCase();
            const cards = document.querySelectorAll('.paper-card');
            
            cards.forEach(card => {
                const title = card.querySelector('.paper-title').textContent.toLowerCase();
                const authors = card.querySelector('.paper-authors').textContent.toLowerCase();
                const abstract = card.querySelector('.paper-abstract').textContent.toLowerCase();
                
                if (title.includes(filter) || authors.includes(filter) || abstract.includes(filter)) {
                    card.style.display = 'block';
                } else {
                    card.style.display = 'none';
                }
            });
        }
        
        // 添加复制链接功能
        document.querySelectorAll('.paper-link').forEach(link => {
            link.addEventListener('click', function(e) {
                e.preventDefault();
                window.open(this.href, '_blank');
            });
        });
    </script>
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
            background: linear-gradient(135deg, #ff6b6b 0%, #ee5a52 100%);
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
            border-radius: 15px;
            text-align: center;
            box-shadow: 0 20px 40px rgba(0,0,0,0.1);
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
            background: linear-gradient(135deg, #3498db, #2980b9);
            color: white;
            padding: 12px 30px;
            border: none;
            border-radius: 25px;
            font-size: 16px;
            cursor: pointer;
            transition: all 0.3s ease;
        }
        
        .retry-button:hover {
            transform: translateY(-2px);
            box-shadow: 0 5px 15px rgba(52, 152, 219, 0.4);
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
                server.shutdown()
                
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
