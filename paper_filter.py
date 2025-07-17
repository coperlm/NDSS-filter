#!/usr/bin/env python3
"""
AI+规则辅助筛选器 - NDSS 2025论文智能筛选工具
基于语义相似度和规则的论文推荐系统
"""

import json
import numpy as np
from typing import List, Dict, Tuple
import re
from dataclasses import dataclass
from sentence_transformers import SentenceTransformer, util
import torch

@dataclass
class Paper:
    """论文数据结构"""
    title: str
    authors: str
    abstract: str
    url: str
    similarity_score: float = 0.0
    rule_score: float = 0.0
    final_score: float = 0.0

class PaperFilter:
    """论文筛选器类"""
    
    def __init__(self, model_name: str = 'paraphrase-MiniLM-L6-v2'):
        """
        初始化筛选器
        
        Args:
            model_name: 使用的句子嵌入模型名称
        """
        print(f"正在加载语义嵌入模型: {model_name}")
        self.model = SentenceTransformer(model_name)
        print("模型加载完成!")
        
        # 定义关键词权重映射
        self.keyword_weights = {
            # 密码学相关 - 您感兴趣的领域
            'zero knowledge': 1.5,  # 零知识证明 - 高权重
            'chameleon hash': 1.5,  # 变色龙哈希 - 高权重
            'public key': 1.3,      # 公钥密码学
            'cryptography': 1.2, 
            'encryption': 1.2,
            'digital signature': 1.3,  # 数字签名
            'elliptic curve': 1.2,     # 椭圆曲线密码学
            'rsa': 1.1,                # RSA算法
            'bilinear pairing': 1.2,   # 双线性配对
            'lattice': 1.1,            # 格密码学
            'homomorphic': 1.0,        # 同态加密
            'commitment': 1.2,         # 承诺方案
            'proof system': 1.3,       # 证明系统
            'cryptographic protocol': 1.2,  # 密码协议
            'hash function': 1.1,      # 哈希函数
            'merkle tree': 1.0,        # 默克尔树
            'privacy': 0.8,            # 隐私相关但权重稍低
            'secure': 0.7,             # 安全相关但权重较低
            
            # 机器学习安全 - 不感兴趣
            'adversarial': 0.0,
            'neural network': 0.0,
            'deep learning': 0.0,
            'machine learning': 0.0,
            'federated learning': 0.0,
            'artificial intelligence': 0.0,
            
            # 系统安全 - 不感兴趣
            'vulnerability': 0.0,
            'attack': 0.0,
            'defense': 0.0,
            'malware': 0.0,
            'penetration': 0.0,
            'exploit': 0.0,
            
            # 区块链相关 - 中等兴趣（因为涉及密码学）
            'blockchain': 0.6,
            'bitcoin': 0.5,
            'cryptocurrency': 0.5,
            'smart contract': 0.4,
        }
    
    def load_papers_from_json(self, json_file: str) -> List[Paper]:
        """
        从JSON文件加载论文数据
        
        Args:
            json_file: JSON文件路径
            
        Returns:
            论文对象列表
        """
        try:
            with open(json_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            papers = []
            for item in data:
                paper = Paper(
                    title=item.get('title', ''),
                    authors=item.get('authors', ''),
                    abstract=item.get('abstract', ''),
                    url=item.get('url', '')
                )
                papers.append(paper)
            
            print(f"成功加载 {len(papers)} 篇论文")
            return papers
            
        except Exception as e:
            print(f"加载JSON文件时出错: {e}")
            return []
    
    def calculate_semantic_similarity(self, research_interest: str, papers: List[Paper]) -> List[Paper]:
        """
        计算语义相似度
        
        Args:
            research_interest: 研究兴趣描述
            papers: 论文列表
            
        Returns:
            更新了相似度分数的论文列表
        """
        print("正在计算语义相似度...")
        
        # 编码研究兴趣
        interest_embedding = self.model.encode(research_interest, convert_to_tensor=True)
        
        # 编码所有论文摘要
        abstracts = [paper.abstract for paper in papers]
        abstract_embeddings = self.model.encode(abstracts, convert_to_tensor=True)
        
        # 计算余弦相似度
        cos_scores = util.cos_sim(interest_embedding, abstract_embeddings)[0]
        
        # 更新论文的相似度分数
        for i, paper in enumerate(papers):
            paper.similarity_score = float(cos_scores[i])
        
        print("语义相似度计算完成!")
        return papers
    
    def apply_rule_based_filtering(self, papers: List[Paper]) -> List[Paper]:
        """
        应用基于规则的筛选
        
        Args:
            papers: 论文列表
            
        Returns:
            更新了规则分数的论文列表
        """
        print("正在应用规则筛选...")
        
        for paper in papers:
            rule_score = 0.0
            
            # 合并标题和摘要进行关键词匹配
            text = (paper.title + " " + paper.abstract).lower()
            
            # 根据关键词计算规则分数
            for keyword, weight in self.keyword_weights.items():
                if keyword in text:
                    rule_score += weight
                    
            # 标题中的关键词给予额外权重
            title_lower = paper.title.lower()
            for keyword, weight in self.keyword_weights.items():
                if keyword in title_lower and weight > 0:
                    rule_score += weight * 0.5  # 标题关键词额外加分
            
            paper.rule_score = rule_score
        
        print("规则筛选完成!")
        return papers
    
    def calculate_final_scores(self, papers: List[Paper], 
                             semantic_weight: float = 0.7, 
                             rule_weight: float = 0.3) -> List[Paper]:
        """
        计算最终综合分数
        
        Args:
            papers: 论文列表
            semantic_weight: 语义相似度权重
            rule_weight: 规则分数权重
            
        Returns:
            更新了最终分数的论文列表
        """
        print("正在计算最终综合分数...")
        
        # 归一化语义分数到0-1范围
        semantic_scores = [paper.similarity_score for paper in papers]
        if semantic_scores:
            min_sem = min(semantic_scores)
            max_sem = max(semantic_scores)
            sem_range = max_sem - min_sem if max_sem != min_sem else 1
        
        # 归一化规则分数到0-1范围
        rule_scores = [paper.rule_score for paper in papers]
        if rule_scores:
            min_rule = min(rule_scores)
            max_rule = max(rule_scores)
            rule_range = max_rule - min_rule if max_rule != min_rule else 1
        
        for paper in papers:
            # 归一化分数
            norm_semantic = (paper.similarity_score - min_sem) / sem_range if sem_range > 0 else 0
            norm_rule = (paper.rule_score - min_rule) / rule_range if rule_range > 0 else 0
            
            # 计算加权综合分数
            paper.final_score = semantic_weight * norm_semantic + rule_weight * norm_rule
        
        print("最终分数计算完成!")
        return papers
    
    def filter_and_rank(self, research_interest: str, papers: List[Paper], 
                       top_k: int = 10, semantic_weight: float = 0.7) -> List[Paper]:
        """
        完整的筛选和排序流程
        
        Args:
            research_interest: 研究兴趣描述
            papers: 论文列表
            top_k: 返回前k篇论文
            semantic_weight: 语义相似度权重
            
        Returns:
            排序后的前k篇论文
        """
        # 计算语义相似度
        papers = self.calculate_semantic_similarity(research_interest, papers)
        
        # 应用规则筛选
        papers = self.apply_rule_based_filtering(papers)
        
        # 计算最终分数
        papers = self.calculate_final_scores(papers, semantic_weight, 1 - semantic_weight)
        
        # 按最终分数排序
        papers.sort(key=lambda x: x.final_score, reverse=True)
        
        return papers[:top_k]
    
    def print_results(self, papers: List[Paper], show_scores: bool = True):
        """
        打印筛选结果
        
        Args:
            papers: 论文列表
            show_scores: 是否显示分数详情
        """
        print("\n" + "="*80)
        print("🎯 论文推荐结果")
        print("="*80)
        
        for i, paper in enumerate(papers, 1):
            print(f"\n📄 【第 {i} 名】")
            print(f"标题: {paper.title}")
            print(f"作者: {paper.authors}")
            
            if show_scores:
                print(f"语义相似度: {paper.similarity_score:.4f}")
                print(f"规则分数: {paper.rule_score:.2f}")
                print(f"综合分数: {paper.final_score:.4f}")
            
            # 显示摘要前200个字符
            abstract_preview = paper.abstract[:200] + "..." if len(paper.abstract) > 200 else paper.abstract
            print(f"摘要预览: {abstract_preview}")
            print(f"链接: {paper.url}")
            print("-" * 60)
    
    def export_results(self, papers: List[Paper], output_file: str):
        """
        导出结果到JSON文件
        
        Args:
            papers: 论文列表
            output_file: 输出文件路径
        """
        results = []
        for paper in papers:
            results.append({
                'title': paper.title,
                'authors': paper.authors,
                'abstract': paper.abstract,
                'url': paper.url,
                'similarity_score': paper.similarity_score,
                'rule_score': paper.rule_score,
                'final_score': paper.final_score
            })
        
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(results, f, indent=4, ensure_ascii=False)
        
        print(f"\n结果已导出到: {output_file}")


def main():
    """主函数 - 演示使用方法"""
    print("🚀 NDSS 2025 论文智能筛选器")
    print("="*50)
    
    # 初始化筛选器
    filter_system = PaperFilter()
    
    # 加载论文数据
    papers = filter_system.load_papers_from_json('ndss_papers_2025.json')
    
    if not papers:
        print("❌ 未能加载论文数据，请检查JSON文件")
        return
    
    # 设置默认研究兴趣 - 您可以在这里修改为您感兴趣的领域
    default_research_interest = "zero-knowledge proofs, chameleon hash functions, public key cryptography, digital signatures, and cryptographic protocols"
    
    # 可选的研究兴趣列表（仅供参考，程序会使用默认值）
    research_interests = [
        "zero-knowledge proofs and cryptographic protocols",
        "chameleon hash functions and commitment schemes",
        "public key cryptography and digital signatures", 
        "elliptic curve cryptography and bilinear pairings",
        "lattice-based cryptography and post-quantum security",
    ]
    
    # 使用默认研究兴趣
    research_interest = default_research_interest
    print(f"🎯 使用默认研究兴趣: {research_interest}")
    print("💡 如需修改研究兴趣，请编辑代码中的 default_research_interest 变量")
    print("🔐 当前偏好: 零知识证明、变色龙哈希、公钥密码学相关论文")
    
    try:
        
        # 执行筛选
        top_papers = filter_system.filter_and_rank(
            research_interest=research_interest,
            papers=papers,
            top_k=10,  # 返回前10篇
            semantic_weight=0.7  # 语义相似度权重70%，规则权重30%
        )
        
        # 显示结果
        filter_system.print_results(top_papers)
        
        # 导出结果
        output_file = f"filtered_papers_{len(top_papers)}.json"
        filter_system.export_results(top_papers, output_file)
        
        print(f"\n✅ 筛选完成! 从 {len(papers)} 篇论文中为您推荐了 {len(top_papers)} 篇最相关的论文。")
        
    except KeyboardInterrupt:
        print("\n\n👋 用户取消操作")
    except Exception as e:
        print(f"\n❌ 程序执行出错: {e}")


if __name__ == "__main__":
    main()
