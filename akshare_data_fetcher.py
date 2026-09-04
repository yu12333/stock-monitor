#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
使用 akshare 获取A股数据的模块
基于 daily_stock_analysis 项目的精确计算实现
"""

import akshare as ak
import pandas as pd
import numpy as np
import math
import time
import random
from datetime import datetime
from typing import Dict, List, Any
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def _enforce_rate_limit():
    time.sleep(random.uniform(0.3, 0.8))

def safe_float(value: Any) -> float:
    try:
        if pd.isna(value):
            return 0.0
        return float(value)
    except (TypeError, ValueError):
        return 0.0

def is_bse_code(code: str) -> bool:
    c = (code or "").strip().split(".")[0]
    if len(c) != 6 or not c.isdigit():
        return False
    if c.startswith("900"):
        return False
    return c.startswith(("92", "43", "81", "82", "83", "87", "88"))

def is_st_stock(name: str) -> bool:
    return 'ST' in (name or "").upper()

def is_kc_cy_stock(code: str) -> bool:
    c = (code or "").strip().split(".")[0]
    return c.startswith("688") or c.startswith("30")

def normalize_stock_code(code: str) -> str:
    if not code:
        return ""
    code = str(code).strip()
    for prefix in ['sh', 'sz', 'bj', 'SH', 'SZ', 'BJ']:
        if code.startswith(prefix):
            code = code[len(prefix):]
    return code

def get_a_stock_index() -> List[Dict[str, Any]]:
    try:
        _enforce_rate_limit()
        df = ak.stock_zh_index_spot_sina()
        if df is None or df.empty:
            return [{'name': n, 'price': 0, 'change_pct': 0, 'volume': 0} for n in ['上证指数', '深证成指', '创业板指', '科创50']]
        indices_map = {'sh000001': '上证指数', 'sz399001': '深证成指', 'sz399006': '创业板指', 'sh000688': '科创50'}
        results = []
        for code, name in indices_map.items():
            row = df[df['代码'] == code]
            if not row.empty:
                row = row.iloc[0]
                results.append({'name': name, 'price': safe_float(row.get('最新价', 0)), 'change_pct': safe_float(row.get('涨跌幅', 0)), 'volume': safe_float(row.get('成交额', 0)) / 100000000})
            else:
                results.append({'name': name, 'price': 0, 'change_pct': 0, 'volume': 0})
        return results
    except Exception as e:
        logger.error(f"获取A股指数失败: {e}")
        return [{'name': n, 'price': 0, 'change_pct': 0, 'volume': 0} for n in ['上证指数', '深证成指', '创业板指', '科创50']]

def get_market_stats() -> Dict[str, Any]:
    """
    获取市场涨跌统计（精确计算版本）
    基于 daily_stock_analysis 的实现
    """
    try:
        _enforce_rate_limit()
        logger.info("[API调用] ak.stock_zh_a_spot_em() 获取A股实时行情...")
        df = ak.stock_zh_a_spot_em()
        
        if df is None or df.empty:
            logger.warning("[API返回] A股实时行情数据为空")
            return {'up': 0, 'down': 0, 'flat': 0, 'limit_up': 0, 'limit_down': 0, 'total_amount': 0.0}
        
        up_count = down_count = flat_count = limit_up_count = limit_down_count = 0
        total_amount = 0.0
        
        for _, row in df.iterrows():
            code = str(row.get('代码', ''))
            name = str(row.get('名称', ''))
            current_price = safe_float(row.get('最新价'))
            pre_close = safe_float(row.get('昨收'))
            amount = safe_float(row.get('成交额'))
            
            # 停牌过滤
            if current_price == 0 or pre_close == 0 or amount == 0:
                continue
            
            # 累计成交额
            total_amount += amount
            
            # 获取涨跌幅限制比例
            pure_code = normalize_stock_code(code)
            if is_bse_code(pure_code):
                ratio = 0.30
            elif is_kc_cy_stock(pure_code):
                ratio = 0.20
            elif is_st_stock(name):
                ratio = 0.05
            else:
                ratio = 0.10
            
            # 严格按照 A 股规则计算涨跌停价：昨收 * (1 ± 比例) -> 四舍五入保留2位小数
            limit_up_price = np.floor(pre_close * (1 + ratio) * 100 + 0.5) / 100.0
            limit_down_price = np.floor(pre_close * (1 - ratio) * 100 + 0.5) / 100.0
            
            limit_up_tolerance = round(abs(pre_close * (1 + ratio) - limit_up_price), 10)
            limit_down_tolerance = round(abs(pre_close * (1 - ratio) - limit_down_price), 10)
            
            # 精确比对
            is_limit_up = abs(current_price - limit_up_price) <= limit_up_tolerance
            is_limit_down = abs(current_price - limit_down_price) <= limit_down_tolerance
            
            if is_limit_up:
                limit_up_count += 1
            if is_limit_down:
                limit_down_count += 1
            
            if current_price > pre_close:
                up_count += 1
            elif current_price < pre_close:
                down_count += 1
            else:
                flat_count += 1
        
        return {
            'up': up_count,
            'down': down_count,
            'flat': flat_count,
            'limit_up': limit_up_count,
            'limit_down': limit_down_count,
            'total_amount': total_amount / 1e8  # 转换为亿元
        }
    except Exception as e:
        logger.error(f"获取市场涨跌统计失败: {e}")
        return {'up': 0, 'down': 0, 'flat': 0, 'limit_up': 0, 'limit_down': 0, 'total_amount': 0.0}

def get_limit_stats() -> Dict[str, int]:
    stats = get_market_stats()
    return {'limit_up': stats['limit_up'], 'limit_down': stats['limit_down']}

def get_sectors() -> List[Dict[str, Any]]:
    try:
        _enforce_rate_limit()
        df = ak.stock_board_industry_name_em()
        if df is None or df.empty:
            return []
        df['涨跌幅'] = pd.to_numeric(df['涨跌幅'], errors='coerce')
        df = df.dropna(subset=['涨跌幅'])
        top_sectors = df.nlargest(8, '涨跌幅')
        return [{'name': row['板块名称'], 'change_pct': safe_float(row['涨跌幅'])} for _, row in top_sectors.iterrows()]
    except Exception as e:
        logger.error(f"获取板块排名失败: {e}")
        return []

def get_first_limit_ups() -> List[Dict[str, str]]:
    try:
        _enforce_rate_limit()
        today = datetime.now().strftime('%Y%m%d')
        df = ak.stock_zt_pool_em(date=today)
        if df is None or df.empty:
            return []
        if '首次封板时间' in df.columns:
            df['首次封板时间'] = pd.to_numeric(df['首次封板时间'], errors='coerce')
            df = df.sort_values('首次封板时间')
        return [{'name': str(row.get('名称', ''))} for _, row in df.head(5).iterrows() if row.get('名称')]
    except Exception as e:
        logger.error(f"获取率先涨停股票失败: {e}")
        return []

if __name__ == "__main__":
    print("测试市场涨跌统计:")
    stats = get_market_stats()
    print(f"上涨: {stats['up']} | 下跌: {stats['down']} | 平盘: {stats['flat']}")
    print(f"涨停: {stats['limit_up']} | 跌停: {stats['limit_down']}")
    print(f"两市成交额: {stats['total_amount']:.0f} 亿")
