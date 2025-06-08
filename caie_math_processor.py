#!/usr/bin/env python3
"""
CAIE A-Level Mathematics Paper Processing System
处理2001-2022年所有CAIE数学试卷，提取题目和答案
"""

import os
import re
import json
import PyPDF2
# import fitz  # PyMuPDF - 暂时注释，使用PyPDF2替代
from pathlib import Path
from dataclasses import dataclass
from typing import List, Dict, Optional
import pandas as pd

@dataclass
class PaperInfo:
    """试卷信息结构"""
    file_path: str
    year: str
    season: str
    paper_type: str  # 'qp' or 'ms'
    paper_code: str  # e.g., '11', '12', '22'
    subject_code: str = "9709"
    
@dataclass
class Question:
    """题目信息结构"""
    question_id: str
    content: str
    image_path: Optional[str] = None
    paper_info: Optional[PaperInfo] = None
    mark_scheme: Optional[str] = None

class CAIEMathProcessor:
    def __init__(self, base_path: str):
        self.base_path = Path(base_path)
        self.papers: List[PaperInfo] = []
        self.questions: List[Question] = []
        
    def scan_papers(self) -> List[PaperInfo]:
        """扫描2020年CAIE数学试卷文件（测试版）"""
        print("🔍 扫描CAIE数学试卷文件（仅2020年测试数据）...")
        
        math_path = self.base_path / "CAIE" / "Alevel" / "Mathematics (9709)"
        
        for year_dir in sorted(math_path.iterdir()):
            if not year_dir.is_dir():
                continue
                
            year = year_dir.name
            # 只处理2020年数据
            if year != "2020":
                continue
                
            print(f"📅 处理年份: {year} (测试模式)")
            
            for season_dir in year_dir.iterdir():
                if not season_dir.is_dir():
                    continue
                    
                season = season_dir.name.lower()
                
                # 扫描Question Paper
                qp_dir = season_dir / "Question_Paper" if (season_dir / "Question_Paper").exists() else season_dir / "Question Paper"
                if qp_dir.exists():
                    for pdf_file in qp_dir.glob("*.pdf"):
                        paper_info = self._parse_filename(str(pdf_file), year, season, "qp")
                        if paper_info:
                            self.papers.append(paper_info)
                
                # 扫描Mark Scheme
                ms_dir = season_dir / "Mark_Scheme" if (season_dir / "Mark_Scheme").exists() else season_dir / "Mark Scheme"
                if ms_dir.exists():
                    for pdf_file in ms_dir.glob("*.pdf"):
                        paper_info = self._parse_filename(str(pdf_file), year, season, "ms")
                        if paper_info:
                            self.papers.append(paper_info)
        
        print(f"✅ 总共找到 {len(self.papers)} 个试卷文件")
        return self.papers
    
    def _parse_filename(self, file_path: str, year: str, season: str, paper_type: str) -> Optional[PaperInfo]:
        """解析文件名提取试卷信息"""
        filename = Path(file_path).name
        
        # 匹配文件名模式: 9709_s22_qp_12.pdf
        pattern = r"9709_([smw])(\d+)_(qp|ms)_(\w+)\.pdf"
        match = re.search(pattern, filename)
        
        if match:
            season_code, year_code, type_code, paper_code = match.groups()
            return PaperInfo(
                file_path=file_path,
                year=year,
                season=season,
                paper_type=type_code,
                paper_code=paper_code
            )
        
        return None
    
    def extract_questions_from_pdf(self, paper_info: PaperInfo) -> List[Question]:
        """从PDF中提取题目 (使用PyPDF2替代PyMuPDF)"""
        print(f"📖 处理文件: {Path(paper_info.file_path).name}")
        
        try:
            with open(paper_info.file_path, 'rb') as file:
                pdf_reader = PyPDF2.PdfReader(file)
                questions = []
                
                for page_num in range(len(pdf_reader.pages)):
                    page = pdf_reader.pages[page_num]
                    text = page.extract_text()
                    
                    # 检测题目编号 (1., 2., 3., 等)
                    question_patterns = [
                        r"^\s*(\d+)\.\s*(.+)",  # 1. 题目内容
                        r"^\s*(\d+)\s+(.+)",    # 1 题目内容
                    ]
                    
                    for pattern in question_patterns:
                        matches = re.findall(pattern, text, re.MULTILINE | re.DOTALL)
                        for match in matches:
                            question_num, content = match
                            
                            # 清理内容
                            content = content.strip()
                            if len(content) > 50:  # 过滤太短的内容
                                question = Question(
                                    question_id=f"{paper_info.year}_{paper_info.season}_{paper_info.paper_code}_{question_num}",
                                    content=content[:500],  # 限制长度
                                    paper_info=paper_info
                                )
                                questions.append(question)
                
                return questions
            
        except Exception as e:
            print(f"❌ 处理文件出错 {paper_info.file_path}: {e}")
            return []
    
    def match_questions_with_answers(self):
        """匹配题目与答案"""
        print("🔗 匹配题目与Mark Scheme...")
        
        # 按试卷分组
        qp_papers = [p for p in self.papers if p.paper_type == "qp"]
        ms_papers = [p for p in self.papers if p.paper_type == "ms"]
        
        # 为每个Question Paper找到对应的Mark Scheme
        for qp in qp_papers:
            # 查找对应的Mark Scheme
            matching_ms = [ms for ms in ms_papers 
                          if ms.year == qp.year 
                          and ms.season == qp.season 
                          and ms.paper_code == qp.paper_code]
            
            if matching_ms:
                print(f"✅ 找到匹配: {Path(qp.file_path).name} <-> {Path(matching_ms[0].file_path).name}")
                
                # 提取题目
                questions = self.extract_questions_from_pdf(qp)
                
                # 提取对应答案（简化版）
                for question in questions:
                    question.mark_scheme = f"Mark Scheme: {matching_ms[0].file_path}"
                
                self.questions.extend(questions)
    
    def export_to_json(self, output_file: str):
        """导出为JSON格式"""
        print(f"💾 导出数据到 {output_file}")
        
        data = []
        for question in self.questions:
            data.append({
                "id": question.question_id,
                "content": question.content,
                "year": question.paper_info.year,
                "season": question.paper_info.season,
                "paper_code": question.paper_info.paper_code,
                "mark_scheme": question.mark_scheme,
                "file_path": question.paper_info.file_path
            })
        
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
        
        print(f"✅ 成功导出 {len(data)} 个题目")
    
    def create_elasticsearch_index(self):
        """创建Elasticsearch索引结构"""
        index_mapping = {
            "mappings": {
                "properties": {
                    "question_id": {"type": "keyword"},
                    "content": {
                        "type": "text",
                        "analyzer": "standard",
                        "fields": {
                            "keyword": {"type": "keyword"}
                        }
                    },
                    "year": {"type": "keyword"},
                    "season": {"type": "keyword"},
                    "paper_code": {"type": "keyword"},
                    "subject": {"type": "keyword"},
                    "mark_scheme": {"type": "text"},
                    "file_path": {"type": "keyword"}
                }
            },
            "settings": {
                "number_of_shards": 1,
                "number_of_replicas": 0,
                "analysis": {
                    "analyzer": {
                        "math_analyzer": {
                            "tokenizer": "standard",
                            "filter": ["lowercase", "stop"]
                        }
                    }
                }
            }
        }
        
        with open("elasticsearch_mapping.json", 'w') as f:
            json.dump(index_mapping, f, indent=2)
        
        print("✅ Elasticsearch映射配置已生成")

def main():
    """主函数"""
    print("🚀 CAIE A-Level数学试卷处理器启动")
    
    # 设置基础路径
    base_path = "/Users/patrick/Desktop/Container"
    processor = CAIEMathProcessor(base_path)
    
    # 扫描所有试卷
    papers = processor.scan_papers()
    
    # 统计信息
    qp_count = len([p for p in papers if p.paper_type == "qp"])
    ms_count = len([p for p in papers if p.paper_type == "ms"])
    
    print(f"📊 统计信息:")
    print(f"   Question Papers: {qp_count}")
    print(f"   Mark Schemes: {ms_count}")
    print(f"   年份范围: {min(p.year for p in papers)} - {max(p.year for p in papers)}")
    
    # 匹配题目和答案
    processor.match_questions_with_answers()
    
    # 导出数据
    processor.export_to_json("caie_math_questions.json")
    
    # 生成Elasticsearch配置
    processor.create_elasticsearch_index()
    
    print("🎉 处理完成！")

if __name__ == "__main__":
    main()