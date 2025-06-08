#!/usr/bin/env python3
"""
CAIE搜题系统 API服务器
支持拍照搜题、文本搜索、OCR识别
"""

import os
import json
import uuid
import asyncio
from typing import List, Dict, Optional
from pathlib import Path

import uvicorn
from fastapi import FastAPI, File, UploadFile, HTTPException, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import redis
from elasticsearch import Elasticsearch
import cv2
import numpy as np
from PIL import Image
import io

from ocr_service import OCRService  # 重新启用
from search_service import SearchService
from math_search_optimizer import MathSearchOptimizer
from models import SearchResult, OCRResult, SearchRequest

# 初始化FastAPI应用
app = FastAPI(
    title="CAIE搜题系统API",
    description="支持拍照搜题、OCR识别、智能搜索",
    version="1.0.0"
)

# 跨域设置
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 全局服务实例
ocr_service = None
search_service = None
math_optimizer = None
redis_client = None

@app.on_event("startup")
async def startup_event():
    """应用启动时初始化服务"""
    global ocr_service, search_service, math_optimizer, redis_client
    
    print("🚀 启动CAIE搜题系统...")
    
    # 初始化Redis
    try:
        redis_url = os.getenv("REDIS_URL", "redis://localhost:6379")
        redis_client = redis.from_url(redis_url)
        redis_client.ping()
        print("✅ Redis连接成功")
    except Exception as e:
        print(f"❌ Redis连接失败: {e}")
    
    # 初始化OCR服务
    try:
        ocr_service = OCRService()
        print("✅ OCR服务初始化成功")
    except Exception as e:
        print(f"❌ OCR服务初始化失败: {e}")
    
    # 初始化搜索服务
    try:
        es_url = os.getenv("ELASTICSEARCH_URL", "http://localhost:9200")
        search_service = SearchService(es_url)
        await search_service.initialize()
        print("✅ 搜索服务初始化成功")
        
        # 初始化数学搜索优化器
        math_optimizer = MathSearchOptimizer(search_service)
        print("✅ 数学搜索优化器初始化成功")
    except Exception as e:
        print(f"❌ 搜索服务初始化失败: {e}")

@app.get("/")
async def root():
    """健康检查"""
    return {
        "message": "CAIE搜题系统API - 搜索功能测试版", 
        "version": "1.0.0-search-only",
        "status": "running",
        "note": "OCR功能暂时禁用，专注测试搜索功能"
    }

@app.get("/health")
async def health_check():
    """系统健康状态"""
    status = {
        "elasticsearch": False,
        "redis": False,
        "ocr": False
    }
    
    # 检查Elasticsearch
    try:
        if search_service and search_service.es.ping():
            status["elasticsearch"] = True
    except:
        pass
    
    # 检查Redis
    try:
        if redis_client:
            redis_client.ping()
            status["redis"] = True
    except:
        pass
    
    # 检查OCR
    if ocr_service:
        status["ocr"] = True
    
    return {"status": status, "healthy": all(status.values())}

@app.post("/ocr", response_model=OCRResult)
async def extract_text(file: UploadFile = File(...)):
    """OCR文字识别接口 - 支持数学公式"""
    if not ocr_service:
        raise HTTPException(status_code=503, detail="OCR服务未启动")
    
    try:
        # 读取图片
        contents = await file.read()
        image = Image.open(io.BytesIO(contents))
        
        # OCR识别
        result = await ocr_service.extract_text(image)
        
        return OCRResult(
            text=result["text"],
            confidence=result["confidence"],
            boxes=result["boxes"]
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"OCR处理失败: {str(e)}")

@app.post("/search/text", response_model=List[SearchResult])
async def search_by_text(request: SearchRequest):
    """文本搜索接口"""
    if not search_service:
        raise HTTPException(status_code=503, detail="搜索服务未启动")
    
    try:
        results = await search_service.search_by_text(
            query=request.query,
            limit=request.limit,
            filters=request.filters
        )
        return results
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"搜索失败: {str(e)}")

@app.post("/search/image", response_model=List[SearchResult])
async def search_by_image(
    file: UploadFile = File(...),
    limit: int = 10
):
    """拍照搜题接口 - 支持数学公式识别优化"""
    if not ocr_service or not search_service or not math_optimizer:
        raise HTTPException(status_code=503, detail="服务未完全启动")
    
    try:
        # 1. OCR识别图片文字（增强版）
        contents = await file.read()
        image = Image.open(io.BytesIO(contents))
        
        ocr_result = await ocr_service.extract_text(image)
        
        if not ocr_result.get("original_text", "").strip():
            raise HTTPException(status_code=400, detail="未识别到文字内容")
        
        # 2. 使用数学搜索优化器进行智能匹配
        optimized_results = await math_optimizer.optimize_ocr_search(ocr_result)
        
        # 3. 转换为标准SearchResult格式
        search_results = []
        for item in optimized_results[:limit]:
            result = item['result']
            result.confidence = item['confidence']  # 使用优化后的置信度
            search_results.append(result)
        
        return search_results
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"拍照搜题失败: {str(e)}")

@app.post("/search/image/analysis")
async def search_by_image_with_analysis(
    file: UploadFile = File(...),
    limit: int = 10
):
    """拍照搜题接口 - 带详细分析结果"""
    if not ocr_service or not search_service or not math_optimizer:
        raise HTTPException(status_code=503, detail="服务未完全启动")
    
    try:
        # OCR识别
        contents = await file.read()
        image = Image.open(io.BytesIO(contents))
        ocr_result = await ocr_service.extract_text(image)
        
        if not ocr_result.get("original_text", "").strip():
            raise HTTPException(status_code=400, detail="未识别到文字内容")
        
        # 优化搜索
        optimized_results = await math_optimizer.optimize_ocr_search(ocr_result)
        
        # 分析匹配质量
        detailed_results = []
        for item in optimized_results[:limit]:
            quality_analysis = math_optimizer.analyze_match_quality(ocr_result, item)
            detailed_results.append({
                "result": item['result'],
                "confidence": item['confidence'],
                "method_scores": item.get('method_scores', {}),
                "method_count": item.get('method_count', 0),
                "quality_analysis": quality_analysis
            })
        
        return {
            "ocr_result": ocr_result,
            "search_results": detailed_results,
            "total_found": len(optimized_results)
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"拍照搜题失败: {str(e)}")

@app.post("/admin/index")
async def create_index(background_tasks: BackgroundTasks):
    """管理接口：创建搜索索引"""
    if not search_service:
        raise HTTPException(status_code=503, detail="搜索服务未启动")
    
    # 后台任务执行索引创建
    background_tasks.add_task(search_service.build_index)
    
    return {"message": "索引创建任务已启动", "status": "started"}

@app.get("/admin/stats")
async def get_stats():
    """管理接口：获取系统统计"""
    if not search_service:
        raise HTTPException(status_code=503, detail="搜索服务未启动")
    
    try:
        stats = await search_service.get_index_stats()
        return stats
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"获取统计失败: {str(e)}")

if __name__ == "__main__":
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info"
    )