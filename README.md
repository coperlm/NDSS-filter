# NDSS 2025 论文提取与翻译工具

![NDSS 2025](https://img.shields.io/badge/NDSS-2025-blue.svg) ![Python](https://img.shields.io/badge/Python-3.7+-green.svg) ![License](https://img.shields.io/badge/License-MIT-yellow.svg)

## 📖 项目简介

这是一个专门用于提取和处理 NDSS Symposium 2025 已录用论文信息的工具集。该项目能够从官网的MHTML文件中提取论文信息，自动翻译标题为中文，并生成美观的可视化报告。

**NDSS (Network and Distributed System Security Symposium)** 是网络与分布式系统安全领域的顶级学术会议之一。

## ✨ 功能特性

- 🔍 **智能解析**: 从MHTML网页文件中准确提取论文信息
- 🌐 **自动翻译**: 使用Google翻译API将英文标题翻译为中文
- 📊 **数据清理**: 自动清理HTML编码和混杂的翻译内容
- 📋 **多格式输出**: 支持JSON和HTML两种输出格式
- 🔎 **搜索功能**: 支持中英文关键词实时搜索
- 📱 **响应式设计**: HTML报告适配各种设备
- 📈 **统计分析**: 提供详细的数据统计信息

## 📁 项目结构

```
NDSS filter/
├── ndss_parser_improved.py          # 论文信息提取脚本（改进版）
├── ndss_translator.py               # 论文标题翻译脚本
├── ndss_viewer.py                   # HTML报告生成脚本
├── ndss2025_papers_translated.json  # 翻译后的论文数据（JSON格式）
├── ndss2025_papers_report.html      # 可视化论文报告（HTML格式）
├── NDSS Symposium 2025 *.mhtml      # 原始网页文件
└── README.md                        # 项目说明文档
```

## 🚀 快速开始

### 环境要求

- Python 3.7+
- 互联网连接（用于翻译功能）

### 安装依赖

```bash
pip install googletrans==4.0.0rc1
```

### 使用步骤

#### 1. 提取论文信息

```bash
python ndss_parser_improved.py
```

**功能**: 从MHTML文件中提取论文标题、作者和链接信息，并清理编码问题。

**输出**: `ndss2025_papers_clean.json`

#### 2. 翻译论文标题

```bash
python ndss_translator.py
```

**功能**: 为所有论文标题添加中文翻译。

**输出**: `ndss2025_papers_translated.json`

#### 3. 生成可视化报告

```bash
python ndss_viewer.py
```

**功能**: 生成美观的HTML报告，支持搜索和筛选。

**输出**: `ndss2025_papers_report.html`

## 📊 数据格式

### JSON数据结构

```json
{
  "conference": "NDSS Symposium 2025",
  "description": "Network and Distributed System Security Symposium 2025 Accepted Papers (with Chinese translations)",
  "total_papers": 207,
  "extraction_date": "2025-07-17",
  "translation_date": "2025-07-17",
  "papers": [
    {
      "title": "A Key-Driven Framework for Identity-Preserving Face Anonymization",
      "title_chinese": "一个密钥驱动的框架，用于保持身份的人脸匿名化",
      "authors": "Miaomiao Wang (Shanghai University), Guang Hua (Singapore Institute of Technology), Sheng Li (Fudan University)",
      "url": "https://www.ndss-symposium.org/ndss-paper/..."
    }
  ]
}
```

### 字段说明

| 字段 | 描述 |
|------|------|
| `title` | 论文英文标题 |
| `title_chinese` | 论文中文标题（自动翻译） |
| `authors` | 作者信息 |
| `url` | 论文详情链接（如果可用） |

## 📈 统计信息

### NDSS 2025 论文统计

- **论文总数**: 207篇
- **已翻译论文**: 207篇 (100%)
- **有链接论文**: 154篇 (74%)
- **有作者信息**: 207篇 (100%)

### 研究领域分布

NDSS 2025涵盖的主要研究领域包括：

- 🔐 密码学与隐私保护
- 🛡️ 网络安全与防护
- 🤖 机器学习安全
- 📱 移动设备安全
- 🌐 Web安全
- ⚙️ 系统安全
- 🔗 区块链安全
- 🧠 AI安全

## 🛠️ 技术实现

### 核心技术栈

- **Python 3.7+**: 主要开发语言
- **googletrans**: Google翻译API接口
- **正则表达式**: 文本解析和清理
- **JSON**: 数据存储格式
- **HTML/CSS/JavaScript**: 可视化报告

### 关键算法

1. **MHTML解析**: 使用正则表达式解析quoted-printable编码的HTML内容
2. **文本清理**: 多层过滤机制移除中文翻译插件的干扰内容
3. **智能翻译**: 自动清理不完整标题并进行翻译
4. **搜索优化**: 支持中英文混合搜索的实时过滤

## 🎨 HTML报告特性

### 界面特点

- 🎨 **现代化设计**: 采用渐变背景和卡片式布局
- 📱 **响应式布局**: 自适应各种屏幕尺寸
- 🔍 **实时搜索**: 支持标题、作者、关键词搜索
- 📊 **统计面板**: 实时显示论文数量统计
- 🔗 **直达链接**: 一键跳转到论文详情页

### 搜索功能

- 支持英文标题搜索
- 支持中文标题搜索
- 支持作者姓名搜索
- 支持关键词模糊匹配
- 实时搜索结果高亮

## 🔧 自定义配置

### 修改翻译设置

在 `ndss_translator.py` 中可以调整：

```python
# 翻译延迟（避免API限制）
time.sleep(0.1)  # 可调整为更大值

# 翻译语言设置
result = translator.translate(cleaned_text, src='en', dest='zh-cn')
```

### 修改HTML样式

在 `ndss_viewer.py` 中的CSS部分可以自定义：

- 颜色主题
- 字体设置
- 布局样式
- 动画效果

## 📋 使用场景

### 学术研究

- 📚 **文献调研**: 快速浏览NDSS 2025所有论文
- 🔍 **主题筛选**: 通过关键词搜索相关研究
- 📊 **趋势分析**: 了解网络安全领域最新研究方向

### 教学应用

- 👨‍🏫 **课程设计**: 为网络安全课程准备教学材料
- 📖 **作业参考**: 为学生提供高质量论文参考
- 🎓 **研究指导**: 帮助学生了解顶级会议研究水平

### 产业应用

- 💼 **技术跟踪**: 跟踪学术界最新安全技术发展
- 🚀 **创新灵感**: 为产品安全设计提供学术参考
- 📈 **市场分析**: 了解安全技术发展趋势

## 🚨 注意事项

### 使用限制

1. **翻译API**: Google翻译可能有请求频率限制
2. **网络要求**: 翻译功能需要稳定的互联网连接
3. **数据更新**: 原始MHTML文件需要从官网获取最新版本

### 常见问题

**Q: 翻译失败怎么办？**
A: 检查网络连接，可能需要科学上网工具，或者增加翻译延迟时间。

**Q: 部分论文没有链接？**
A: 这是正常现象，部分论文的详情页可能还未发布。

**Q: 如何更新论文数据？**
A: 从NDSS官网下载最新的MHTML文件，替换原文件后重新运行脚本。

## 📄 许可证

本项目采用 MIT 许可证 - 详情请查看 [LICENSE](LICENSE) 文件。

## 🤝 贡献

欢迎提交 Issue 和 Pull Request！

### 贡献指南

1. Fork 本项目
2. 创建特性分支 (`git checkout -b feature/AmazingFeature`)
3. 提交更改 (`git commit -m 'Add some AmazingFeature'`)
4. 推送到分支 (`git push origin feature/AmazingFeature`)
5. 开启 Pull Request

## 📞 联系方式

如有问题或建议，欢迎通过以下方式联系：

- 📧 邮箱: [your-email@example.com]
- 🐛 问题反馈: [GitHub Issues](https://github.com/your-username/ndss-2025-papers/issues)

## 📚 相关资源

- [NDSS Symposium 官网](https://www.ndss-symposium.org/)
- [NDSS 2025 论文列表](https://www.ndss-symposium.org/ndss2025/accepted-papers/)
- [Google翻译API文档](https://py-googletrans.readthedocs.io/)

---

⭐ 如果这个项目对您有帮助，请给我们一个星标！

📈 **最后更新**: 2025年7月17日
