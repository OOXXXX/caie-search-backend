#!/usr/bin/env python3
"""
数据模型定义
"""

from typing import List, Dict, Optional, Any
from pydantic import BaseModel, Field

class OCRResult(BaseModel):
    """OCR识别结果"""
    text: str = Field(description="识别的文字内容")
    confidence: float = Field(description="识别置信度")
    boxes: List[List[int]] = Field(description="文字位置框", default=[])

class SearchRequest(BaseModel):
    """搜索请求"""
    query: str = Field(description="搜索关键词")
    limit: int = Field(default=10, description="返回结果数量")
    filters: Optional[Dict[str, Any]] = Field(default=None, description="搜索过滤条件")

class SearchResult(BaseModel):
    """搜索结果"""
    id: str = Field(description="题目ID")
    title: str = Field(description="题目标题")
    content: str = Field(description="题目内容")
    year: str = Field(description="年份")
    season: str = Field(description="考试季节")
    paper_code: str = Field(description="试卷代码")
    mark_scheme: Optional[str] = Field(description="答案内容")
    confidence: float = Field(description="匹配置信度")
    file_path: Optional[str] = Field(description="文件路径")

class QuestionData(BaseModel):
    """题目数据结构"""
    question_id: str
    content: str
    year: str
    season: str
    paper_code: str
    subject_code: str = "9709"
    mark_scheme: Optional[str] = None
    file_path: Optional[str] = None
    image_path: Optional[str] = None

class IndexStats(BaseModel):
    """索引统计信息"""
    total_documents: int
    index_size: str
    last_updated: Optional[str] = None