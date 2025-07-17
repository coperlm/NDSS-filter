# 🎯 NDSS 2025 论文智能筛选系统

基于AI语义分析和规则的论文推荐系统，帮助研究人员快速筛选和发现感兴趣的学术论文。

## ✨ 功能特色

- 🤖 **AI语义分析**: 使用 SentenceTransformer 模型进行语义相似度计算
- 📊 **规则筛选**: 基于关键词权重的规则过滤系统  
- 🎨 **可视化界面**: 现代化的Web界面展示筛选结果
- 🔍 **实时搜索**: 支持论文标题、作者、摘要的实时搜索
- 📱 **响应式设计**: 支持桌面和移动设备访问
- 🌐 **本地部署**: 无需外部依赖，本地localhost运行

## 🚀 快速开始

### 1. 环境要求

- Python 3.8+
- pip 包管理器

### 2. 安装依赖

```bash
pip install sentence-transformers requests beautifulsoup4 torch
```

### 3. 运行系统

#### 步骤1: 提取论文数据
```bash
python scrape_papers.py
```
这将从NDSS 2025网站抓取论文信息并保存为 `ndss_papers_2025.json`

#### 步骤2: 执行智能筛选
```bash
python paper_filter.py
```
系统将：
- 自动加载论文数据
- 使用默认研究兴趣进行筛选
- 生成 `filtered_papers_10.json` 结果文件

#### 步骤3: 启动可视化界面
```bash
python paper_viewer.py
```
系统将：
- 启动本地Web服务器 (默认端口8080)
- 自动打开浏览器访问 `http://localhost:8080`
- 提供美观的论文筛选结果展示

## 📁 项目结构

```
papers/
├── README.md                    # 项目说明文档
├── scrape_papers.py            # 论文数据抓取工具
├── paper_filter.py             # AI智能筛选器
├── paper_viewer.py             # Web可视化工具
├── ndss_papers_2025.json       # 原始论文数据
├── filtered_papers_10.json     # 筛选结果数据
└── NDSS Symposium 2025...      # 原始HTML文件
```

## 🔧 配置说明

### 修改研究兴趣

编辑 `paper_filter.py` 文件中的 `default_research_interest` 变量：

```python
# 设置默认研究兴趣 - 您可以在这里修改为您感兴趣的领域
default_research_interest = "你的研究兴趣描述"
```

### 调整筛选参数

在 `paper_filter.py` 中可以调整：

- **返回论文数量**: 修改 `top_k=10` 参数
- **权重比例**: 修改 `semantic_weight=0.7` (语义相似度权重70%，规则权重30%)
- **关键词权重**: 在 `keyword_weights` 字典中调整关键词权重

### 修改服务器端口

在 `paper_viewer.py` 中修改默认端口：

```python
viewer.start_server(port=8080)  # 修改为其他端口
```

## 📊 系统架构

### 1. 数据抓取层 (`scrape_papers.py`)
- 从NDSS官网抓取论文标题和链接
- 访问每篇论文详情页面获取摘要和作者信息
- 容错处理和重试机制
- 输出JSON格式的结构化数据

### 2. 智能筛选层 (`paper_filter.py`)
```
语义分析 + 规则筛选 = 综合评分
    ↓
- SentenceTransformer模型计算语义相似度
- 关键词权重规则评分
- 加权综合排序
- 导出筛选结果
```

### 3. 可视化展示层 (`paper_viewer.py`)
- HTTP服务器动态生成HTML页面
- 响应式布局和现代化UI设计
- 实时搜索和筛选功能
- 论文详情展示和链接跳转

## 🎨 界面特色

- 🌈 **渐变背景**: 现代化的视觉效果
- 📋 **卡片布局**: 清晰的论文信息展示
- 🏆 **排名标识**: 醒目的筛选排名显示
- 📈 **统计信息**: 实时的筛选统计数据
- 🔍 **搜索框**: 便捷的实时搜索功能
- 📱 **移动适配**: 完美的移动设备体验

## 🔍 使用示例

### 预设研究兴趣选项
- 同态加密和安全计算
- 隐私保护机器学习和联邦学习  
- 侧信道攻击和对策
- 零知识证明和密码协议
- 恶意软件检测和分析

### 自定义研究兴趣
可以输入任何英文描述，如：
- "blockchain security and smart contracts"
- "IoT device authentication and privacy"
- "quantum cryptography and post-quantum security"

## 🛠️ 技术栈

- **Python 3.8+**: 核心开发语言
- **SentenceTransformers**: AI语义分析模型
- **BeautifulSoup4**: HTML解析和数据抓取
- **HTTP Server**: 内置Web服务器
- **JavaScript**: 前端交互功能
- **CSS3**: 现代化样式设计

## 📝 输出格式

### JSON数据结构
```json
{
  "title": "论文标题",
  "authors": "作者信息", 
  "abstract": "论文摘要",
  "url": "论文链接",
  "similarity_score": 0.8234,
  "rule_score": 1.5,
  "final_score": 0.7823
}
```

### Web界面展示
- 论文排名和综合评分
- 语义相似度、规则分数、综合分数
- 论文标题、作者、摘要预览
- 原文链接跳转

## 🚨 注意事项

1. **网络依赖**: 首次运行需要下载AI模型文件（约90MB）
2. **抓取频率**: 请适度使用数据抓取功能，避免对目标网站造成压力
3. **端口占用**: 如果8080端口被占用，系统会自动尝试8081等其他端口
4. **数据更新**: 论文数据需要手动重新抓取以获取最新信息

## 🤝 贡献指南

欢迎提交Issue和Pull Request来改进这个项目！

### 可能的改进方向
- 支持更多会议论文源
- 增加更多筛选维度
- 优化AI模型性能
- 添加论文收藏功能
- 支持PDF文档解析

## 📄 许可证

MIT License - 详见 LICENSE 文件

## 👨‍💻 作者

GitHub Copilot - AI驱动的智能编程助手

---

🎉 **开始使用吧！** 运行 `python paper_viewer.py` 即可体验智能论文筛选系统！
