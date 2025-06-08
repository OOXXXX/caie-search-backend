#!/usr/bin/env python3
"""
搜索服务
基于Elasticsearch的智能搜索引擎
"""

import json
import asyncio
from typing import List, Dict, Any, Optional
from pathlib import Path
import logging

from elasticsearch import Elasticsearch, AsyncElasticsearch
from elasticsearch.exceptions import NotFoundError, RequestError
import numpy as np
from sentence_transformers import SentenceTransformer

from models import SearchResult, QuestionData, IndexStats
from caie_math_processor import CAIEMathProcessor
from math_formula_processor import MathFormulaProcessor

class SearchService:
    def __init__(self, elasticsearch_url: str):
        """初始化搜索服务"""
        self.logger = logging.getLogger(__name__)
        self.es_url = elasticsearch_url
        
        # 同步和异步Elasticsearch客户端
        self.es = Elasticsearch([elasticsearch_url])
        self.async_es = AsyncElasticsearch([elasticsearch_url])
        
        self.index_name = "caie_math_questions"
        
        # 初始化数学公式处理器
        self.math_processor = MathFormulaProcessor()
        
        # 初始化向量模型（用于语义搜索）
        try:
            self.embedding_model = SentenceTransformer('all-MiniLM-L6-v2')
            self.logger.info("✅ 向量模型加载成功")
        except Exception as e:
            self.logger.warning(f"⚠️  向量模型加载失败: {e}")
            self.embedding_model = None
    
    async def initialize(self):
        """初始化搜索服务"""
        try:
            # 检查连接
            if not self.es.ping():
                raise ConnectionError("无法连接到Elasticsearch")
            
            # 创建索引
            await self.create_index()
            
            self.logger.info("✅ 搜索服务初始化完成")
            
        except Exception as e:
            self.logger.error(f"❌ 搜索服务初始化失败: {e}")
            raise
    
    async def create_index(self):
        """创建Elasticsearch索引"""
        index_mapping = {
            "mappings": {
                "properties": {
                    "question_id": {"type": "keyword"},
                    "content": {
                        "type": "text",
                        "analyzer": "standard",
                        "search_analyzer": "standard",
                        "fields": {
                            "keyword": {"type": "keyword"},
                            "english": {
                                "type": "text",
                                "analyzer": "english"
                            }
                        }
                    },
                    "title": {
                        "type": "text",
                        "analyzer": "standard"
                    },
                    "year": {"type": "keyword"},
                    "season": {"type": "keyword"},
                    "paper_code": {"type": "keyword"},
                    "subject_code": {"type": "keyword"},
                    "mark_scheme": {
                        "type": "text",
                        "analyzer": "standard"
                    },
                    "file_path": {"type": "keyword"},
                    "embedding": {
                        "type": "dense_vector",
                        "dims": 384  # all-MiniLM-L6-v2的向量维度
                    },
                    "created_at": {"type": "date"}
                }
            },
            "settings": {
                "number_of_shards": 1,
                "number_of_replicas": 0,
                "analysis": {
                    "analyzer": {
                        "math_analyzer": {
                            "tokenizer": "standard",
                            "filter": [
                                "lowercase",
                                "stop",
                                "math_synonyms"
                            ]
                        }
                    },
                    "filter": {
                        "math_synonyms": {
                            "type": "synonym",
                            "synonyms": [
                                "differentiate,derivative,diff",
                                "integrate,integration,integral",
                                "solve,find,calculate,determine",
                                "function,equation,formula",
                                "graph,plot,curve,line"
                            ]
                        }
                    }
                }
            }
        }
        
        try:
            # 检查索引是否存在
            if self.es.indices.exists(index=self.index_name):
                self.logger.info(f"索引 {self.index_name} 已存在")
                return
            
            # 创建索引
            self.es.indices.create(
                index=self.index_name,
                body=index_mapping
            )
            self.logger.info(f"✅ 创建索引 {self.index_name} 成功")
            
        except RequestError as e:
            if "already exists" in str(e):
                self.logger.info(f"索引 {self.index_name} 已存在")
            else:
                self.logger.error(f"❌ 创建索引失败: {e}")
                raise
    
    async def build_index(self):
        """构建搜索索引"""
        self.logger.info("🔨 开始构建搜索索引...")
        
        try:
            # 使用CAIE数学处理器提取数据
            processor = CAIEMathProcessor("/Users/patrick/Desktop/Container")
            
            # 扫描试卷
            papers = processor.scan_papers()
            self.logger.info(f"找到 {len(papers)} 个试卷文件")
            
            # 匹配题目和答案
            processor.match_questions_with_answers()
            questions = processor.questions
            
            self.logger.info(f"提取到 {len(questions)} 个题目")
            
            # 批量索引
            await self._bulk_index_questions(questions)
            
            self.logger.info("✅ 搜索索引构建完成")
            
        except Exception as e:
            self.logger.error(f"❌ 构建索引失败: {e}")
            raise
    
    async def _bulk_index_questions(self, questions: List, batch_size: int = 100):
        """批量索引题目"""
        for i in range(0, len(questions), batch_size):
            batch = questions[i:i + batch_size]
            actions = []
            
            for question in batch:
                # 生成文档ID
                doc_id = question.question_id
                
                # 增强数学内容处理
                enhanced_content = self.math_processor.process_pdf_text(question.content)
                math_features = self.math_processor.extract_formula_features(question.content)
                formula_tokens = self.math_processor.tokenize_formula(question.content)
                
                # 准备文档数据
                doc = {
                    "question_id": question.question_id,
                    "content": enhanced_content,
                    "math_features": " ".join(math_features),
                    "formula_tokens": formula_tokens,
                    "title": f"Question {question.question_id}",
                    "year": question.paper_info.year,
                    "season": question.paper_info.season,
                    "paper_code": question.paper_info.paper_code,
                    "subject_code": "9709",
                    "mark_scheme": question.mark_scheme or "",
                    "file_path": question.paper_info.file_path,
                    "created_at": "2024-01-01T00:00:00"
                }
                
                # 生成向量嵌入
                if self.embedding_model:
                    try:
                        embedding = self.embedding_model.encode(question.content)
                        doc["embedding"] = embedding.tolist()
                    except Exception as e:
                        self.logger.warning(f"生成嵌入向量失败: {e}")
                
                # 添加到批次
                actions.append({
                    "_index": self.index_name,
                    "_id": doc_id,
                    "_source": doc
                })
            
            # 执行批量索引 - 修复格式
            try:
                # 构建正确的bulk格式
                bulk_data = []
                for action in actions:
                    bulk_data.append({"index": {"_index": action["_index"], "_id": action["_id"]}})
                    bulk_data.append(action["_source"])
                
                response = self.es.bulk(body=bulk_data)
                if response.get("errors"):
                    self.logger.warning(f"批量索引有错误: {response}")
                else:
                    self.logger.info(f"成功索引 {len(actions)} 个文档")
            except Exception as e:
                self.logger.error(f"批量索引失败: {e}")
    
    async def search_by_text(
        self, 
        query: str, 
        limit: int = 10,
        filters: Optional[Dict] = None
    ) -> List[SearchResult]:
        """文本搜索 - 支持数学公式增强"""
        try:
            # 使用数学公式处理器增强查询
            enhanced_queries = self.math_processor.enhance_search_query(query)
            
            # 构建增强的搜索查询
            search_body = {
                "query": {
                    "bool": {
                        "should": [
                            # 数学公式token精确匹配 - 最高权重
                            {
                                "terms": {
                                    "formula_tokens": self.math_processor.tokenize_formula(query),
                                    "boost": 5.0
                                }
                            },
                            # 数学特征匹配
                            {
                                "multi_match": {
                                    "query": " ".join(self.math_processor.extract_formula_features(query)),
                                    "fields": ["math_features^3"],
                                    "type": "best_fields",
                                    "boost": 4.0
                                }
                            },
                            # 数学符号字段精确匹配
                            {
                                "match": {
                                    "content.math_symbols": {
                                        "query": enhanced_queries.get('normalized', query),
                                        "boost": 3.5
                                    }
                                }
                            },
                            # 数学概念匹配
                            {
                                "match": {
                                    "content.math_concepts": {
                                        "query": enhanced_queries.get('expanded', query),
                                        "boost": 3.0
                                    }
                                }
                            },
                            # 原始查询 - 精确短语匹配
                            {
                                "match_phrase": {
                                    "content": {
                                        "query": enhanced_queries.get('original', query),
                                        "boost": 2.5
                                    }
                                }
                            },
                            # 标准化查询 - 数学符号处理
                            {
                                "multi_match": {
                                    "query": enhanced_queries.get('normalized', query),
                                    "fields": ["content^2", "title", "mark_scheme"],
                                    "type": "best_fields",
                                    "fuzziness": "AUTO",
                                    "boost": 2.0
                                }
                            },
                            # 扩展查询 - 概念同义词
                            {
                                "multi_match": {
                                    "query": enhanced_queries.get('expanded', query),
                                    "fields": ["content^1.5", "title", "mark_scheme"],
                                    "type": "best_fields",
                                    "fuzziness": "AUTO",
                                    "boost": 1.5
                                }
                            },
                            # 模糊匹配 - 兜底搜索
                            {
                                "multi_match": {
                                    "query": query,
                                    "fields": ["content", "title", "mark_scheme"],
                                    "type": "best_fields",
                                    "fuzziness": "AUTO",
                                    "boost": 1.0
                                }
                            },
                        ],
                        "minimum_should_match": 1
                    }
                },
                "size": limit,
                "highlight": {
                    "fields": {
                        "content": {"fragment_size": 200},
                        "math_features": {"fragment_size": 100}
                    }
                }
            }
            
            # 添加向量搜索 - 提高权重用于数学公式语义匹配
            if self.embedding_model:
                query_embedding = self.embedding_model.encode(query).tolist()
                search_body["query"]["bool"]["should"].append({
                    "script_score": {
                        "query": {"match_all": {}},
                        "script": {
                            "source": "cosineSimilarity(params.query_vector, 'embedding') + 1.0",
                            "params": {"query_vector": query_embedding}
                        },
                        "boost": 3.5  # 提高向量搜索权重
                    }
                })
            
            # 添加过滤条件
            if filters:
                filter_clauses = []
                for field, value in filters.items():
                    filter_clauses.append({"term": {field: value}})
                
                if filter_clauses:
                    search_body["query"]["bool"]["filter"] = filter_clauses
            
            # 执行搜索
            response = self.es.search(
                index=self.index_name,
                body=search_body
            )
            
            # 解析结果
            results = []
            for hit in response["hits"]["hits"]:
                source = hit["_source"]
                
                # 获取高亮文本
                highlight = hit.get("highlight", {})
                content = highlight.get("content", [source["content"]])[0]
                
                result = SearchResult(
                    id=source["question_id"],
                    title=source["title"],
                    content=content,
                    year=source["year"],
                    season=source["season"],
                    paper_code=source["paper_code"],
                    mark_scheme=source.get("mark_scheme"),
                    confidence=hit["_score"] / 10.0,  # 归一化分数
                    file_path=source.get("file_path")
                )
                results.append(result)
            
            return results
            
        except Exception as e:
            self.logger.error(f"文本搜索失败: {e}")
            return []
    
    async def search_by_image_similarity(
        self, 
        image_embedding: List[float], 
        limit: int = 5
    ) -> List[SearchResult]:
        """基于图像向量的相似度搜索"""
        try:
            search_body = {
                "query": {
                    "script_score": {
                        "query": {"match_all": {}},
                        "script": {
                            "source": "cosineSimilarity(params.query_vector, 'embedding') + 1.0",
                            "params": {"query_vector": image_embedding}
                        }
                    }
                },
                "size": limit
            }
            
            response = self.es.search(
                index=self.index_name,
                body=search_body
            )
            
            results = []
            for hit in response["hits"]["hits"]:
                source = hit["_source"]
                result = SearchResult(
                    id=source["question_id"],
                    title=source["title"],
                    content=source["content"],
                    year=source["year"],
                    season=source["season"],
                    paper_code=source["paper_code"],
                    mark_scheme=source.get("mark_scheme"),
                    confidence=hit["_score"] / 10.0,
                    file_path=source.get("file_path")
                )
                results.append(result)
            
            return results
            
        except Exception as e:
            self.logger.error(f"向量搜索失败: {e}")
            return []
    
    async def get_index_stats(self) -> IndexStats:
        """获取索引统计信息"""
        try:
            stats = self.es.indices.stats(index=self.index_name)
            count = self.es.count(index=self.index_name)
            
            return IndexStats(
                total_documents=count["count"],
                index_size=f"{stats['indices'][self.index_name]['total']['store']['size_in_bytes'] / 1024 / 1024:.2f} MB"
            )
            
        except Exception as e:
            self.logger.error(f"获取统计信息失败: {e}")
            return IndexStats(total_documents=0, index_size="0 MB")
    
    async def close(self):
        """关闭连接"""
        await self.async_es.close()
        self.es.close()