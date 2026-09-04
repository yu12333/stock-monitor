#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
使用 akshare 获取A股数据的模块
基于 daily_stock_analysis 项目的实现 - 精确计算涨跌停版本
"""

import akshare as ak
import pandas as pd
import numpy as np
import math
import time
import random
import requests
from datetime import datetime
from typing import Optional, Dict, List, Any, Tuple
import logging

# 设置日志
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# User-Agent 池，用于随机轮换
USER_AGENTS = [
    'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
    'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
    'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:121.0) Gecko/20100101 Firefox/121.0',
    'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.2 Safari/605.1.15',
    'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
]


def _set_random_user_agent():
    """设置随机 User-Agent"""
    pass


def _enforce_rate_limit():
    """强制速率限制，避免请求过快"""
    time.sleep(random.uniform(0.5, 1.5))


def safe_float(value: Any) -> float:
    """安全的浮点数转换"""
    try:
        if pd.isna(value):
            return 0.0
        return float(value)
    except (TypeError, ValueError):
        return 0.0


def safe_int(value: Any) -> int:
    """安全的整数转换"""
    try:
        if pd.isna(value):
            return 0
        return int(float(value))
    except (TypeError, ValueError):
        return 0


def is_bse_code(code: str) -> bool:
    """
    检查是否为北交所股票代码
    北交所规则 (2026):
    - 新格式 (2024+): 92xxxx 主交易代码
    - 历史范围: 43xxxx, 83xxxx, 87xxxx, 88xxxx
    """
    c = (code or "").strip().split(".")[0]
    if len(c) != 6 or not c.isdigit():
        return False
    if c.startswith("900"):
        return False
    return c.startswith(("92", "43", "81", "82", "83", "87", "88"))


def is_st_stock(name: str) -> bool:
    """检查是否为ST股票"""
    n = (name or "").upper()
    return 'ST' in n


def is_kc_cy_stock(code: str) -> bool:
    """
    检查是否为科创板或创业板股票
    - 科创板: 688开头
    - 创业板: 300开头
    两者都有±20%的涨跌幅限制
    """
    c = (code or "").strip().split(".")[0]
    return c.startswith("688") or c.startswith("30")


def normalize_stock_code(code: str) -> str:
    """标准化股票代码，去除前缀"""
    if not code:
        return ""
    code = str(code).strip()
    for prefix in ['sh', 'sz', 'bj', 'SH', 'SZ', 'BJ']:
        if code.startswith(prefix):
            code = code[len(prefix):]
    return code


def get_limit_ratio(code: str, name: str) -> float:
    """
    获取涨跌幅限制比例
    - 北交所: 30%
    - 科创板/创业板: 20%
    - ST股票: 5%
    - 其他主板: 10%
    """
    pure_code = normalize_stock_code(code)
    if is_bse_code(pure_code):
        return 0.30
    if is_kc_cy_stock(pure_code):
        return 0.20
    if is_st_stock(name):
        return 0.05
    return 0.10


def round_limit_price(prev_close: float, ratio: float) -> float:
    """计算涨跌停价格（四舍五入保留2位小数）"""
    return math.floor(prev_close * (1 + ratio) * 100 + 0.5) / 100.0


def get_a_stock_index_eastmoney() -> List[Dict[str, Any]]:
    """使用东方财富API获取A股主要指数数据（备用方案）"""
    try:
        url = "https://push2.eastmoney.com/api/qt/ulist.np/get"
        params = {
            'fltt': 2,
            'fields': 'f2,f3,f4,f6,f12,f14',
            'secids': '1.000001,0.399001,0.399006,1.000688'
        }
        response = requests.get(url, params=params, headers={'User-Agent': random.choice(USER_AGENTS)}, timeout=10)
        data = response.json()
        
        stocks = []
        names = ['上证指数', '深证成指', '创业板指', '科创50']
        if 'data' in data and 'diff' in data['data']:
            for i, item in enumerate(data['data']['diff']):
                stocks.append({
                    'name': names[i],
                    'price': item.get('f2', 0),
                    'change_pct': item.get('f3', 0),
                    'volume': item.get('f6', 0) / 100000000
                })
        return stocks if stocks else [{'name': n, 'price': 0, 'change_pct': 0, 'volume': 0} for n in names]
    except Exception as e:
        logger.error(f"[API错误] 使用东方财富API获取A股指数失败: {e}")
        return [{'name': n, 'price': 0, 'change_pct': 0, 'volume': 0} for n in ['上证指数', '深证成指', '创业板指', '科创50']]


def get_a_stock_index() -> List[Dict[str, Any]]:
    """获取A股主要指数数据"""
    try:
        _set_random_user_agent()
        _enforce_rate_limit()
        
        logger.info("[API调用] ak.stock_zh_index_spot_sina() 获取指数行情...")
        df = ak.stock_zh_index_spot_sina()
        
        if df is None or df.empty:
            logger.warning("[API返回] 指数行情数据为空，尝试使用东方财富API")
            return get_a_stock_index_eastmoney()
        
        indices_map = {
            'sh000001': '上证指数',
            'sz399001': '深证成指',
            'sz399006': '创业板指',
            'sh000688': '科创50',
        }
        
        results = []
        for code, name in indices_map.items():
            row = df[df['代码'] == code]
            if row.empty:
                row = df[df['代码'].str.contains(code)]
            
            if not row.empty:
                row = row.iloc[0]
                price = safe_float(row.get('最新价', 0))
                change_pct = safe_float(row.get('涨跌幅', 0))
                volume = safe_float(row.get('成交额', 0)) / 100000000
                
                results.append({
                    'name': name,
                    'price': price,
                    'change_pct': change_pct,
                    'volume': volume
                })
            else:
                results.append({'name': name, 'price': 0, 'change_pct': 0, 'volume': 0})
        
        return results
        
    except Exception as e:
        logger.error(f"[API错误] 获取A股指数失败，尝试使用东方财富API: {e}")
        return get_a_stock_index_eastmoney()


def get_market_stats_eastmoney() -> Dict[str, int]:
    """使用东方财富API获取市场涨跌统计（备用方案）"""
    try:
        url = "https://push2.eastmoney.com/api/qt/clist/get"
        params = {
            'pn': 1,
            'pz': 1,
            'po': 1,
            'np': 1,
            'fltt': 2,
            'invt': 2,
            'fid': 'f3',
            'fs': 'm:0+t:6,m:0+t:80,m:1+t:2,m:1+t:23',
            'fields': 'f104,f105,f106'
        }
        response = requests.get(url, params=params, headers={'User-Agent': random.choice(USER_AGENTS)}, timeout=10)
        data = response.json()
        
        sh_url = "https://push2.eastmoney.com/api/qt/ulist.np/get"
        sh_params = {
            'fltt': 2,
            'fields': 'f104,f105,f106',
            'secids': '1.000001'
        }
        sh_resp = requests.get(sh_url, params=sh_params, headers={'User-Agent': random.choice(USER_AGENTS)}, timeout=10)
        sh_data = sh_resp.json()
        
        if 'data' in sh_data and 'diff' in sh_data['data'] and len(sh_data['data']['diff']) > 0:
            item = sh_data['data']['diff'][0]
            return {
                'up': item.get('f104', 0),
                'down': item.get('f105', 0),
                'flat': item.get('f106', 0),
                'limit_up': 0,
                'limit_down': 0
            }
    except Exception as e:
        logger.error(f"[API错误] 使用东方财富API获取涨跌家数失败: {e}")
    
    return {'up': 0, 'down': 0, 'flat': 0, 'limit_up': 0, 'limit_down': 0}


def get_market_stats() -> Dict[str, int]:
    """
    获取市场涨跌统计（精确计算版本）
    
    基于 daily_stock_analysis 的实现，精确计算涨跌停：
    - 考虑不同板块的涨跌幅限制（主板10%，创业板/科创板20%，北交所30%，ST股5%）
    - 计算精确的涨跌停价格（昨收 * (1 ± 比例)，四舍五入保留2位小数）
    - 使用容差比较来判断是否涨跌停
    """
    try:
        _set_random_user_agent()
        _enforce_rate_limit()
        
        logger.info("[API调用] ak.stock_zh_a_spot_em() 获取A股实时行情...")
        df = ak.stock_zh_a_spot_em()
        
        if df is None or df.empty:
            logger.warning("[API返回] A股实时行情数据为空，尝试使用东方财富API")
            return get_market_stats_eastmoney()
        
        # 计算涨跌统计
        up_count = 0
        down_count = 0
        flat_count = 0
        limit_up_count = 0
        limit_down_count = 0
        
        for _, row in df.iterrows():
            code = str(row.get('代码', ''))
            name = str(row.get('名称', ''))
            current_price = safe_float(row.get('最新价'))
            pre_close = safe_float(row.get('昨收'))
            
            # 跳过无效数据
            if current_price == 0 or pre_close == 0:
                continue
            
            # 获取涨跌幅限制比例
            ratio = get_limit_ratio(code, name)
            
            # 计算涨跌停价格
            limit_up_price = round_limit_price(pre_close, ratio)
            limit_down_price = math.floor(pre_close * (1 - ratio) * 100 + 0.5) / 100.0
            
            # 计算容差
            limit_up_tolerance = round(abs(pre_close * (1 + ratio) - limit_up_price), 10)
            limit_down_tolerance = round(abs(pre_close * (1 - ratio) - limit_down_price), 10)
            
            # 判断涨跌停（精确比较）
            is_limit_up = abs(current_price - limit_up_price) <= limit_up_tolerance
            is_limit_down = abs(current_price - limit_down_price) <= limit_down_tolerance
            
            if is_limit_up:
                limit_up_count += 1
            if is_limit_down:
                limit_down_count += 1
            
            # 计算涨跌
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
            'limit_down': limit_down_count
        }
        
    except Exception as e:
        logger.error(f"[API错误] 获取市场涨跌统计失败，尝试使用东方财富API: {e}")
        return get_market_stats_eastmoney()


def get_limit_stats_eastmoney() -> Dict[str, int]:
    """使用东方财富API获取涨跌停统计（备用方案）"""
    today = datetime.now().strftime('%Y%m%d')
    
    limit_up = 0
    try:
        url_up = "https://push2ex.eastmoney.com/getTopicZTPool"
        params_up = {
            'ut': '7eea3edcaed734bea9cb3e58b20a59fa',
            'dpt': 'wz.ztzt',
            'Ession': 'ztlb',
            'date': today
        }
        resp_up = requests.get(url_up, params=params_up, headers={'User-Agent': random.choice(USER_AGENTS)}, timeout=10)
        data_up = resp_up.json()
        if 'data' in data_up and 'pool' in data_up['data']:
            limit_up = len(data_up['data']['pool'])
    except Exception as e:
        logger.error(f"[API错误] 使用东方财富API获取涨停失败: {e}")
    
    limit_down = 0
    try:
        url_down = "https://push2ex.eastmoney.com/getTopicDTPool"
        params_down = {
            'ut': '7eea3edcaed734bea9cb3e58b20a59fa',
            'dpt': 'wz.ztzt',
            'Ession': 'dtlb',
            'date': today
        }
        resp_down = requests.get(url_down, params=params_down, headers={'User-Agent': random.choice(USER_AGENTS)}, timeout=10)
        data_down = resp_down.json()
        if 'data' in data_down and 'pool' in data_down['data']:
            limit_down = len(data_down['data']['pool'])
    except Exception as e:
        logger.error(f"[API错误] 使用东方财富API获取跌停失败: {e}")
    
    return {'limit_up': limit_up, 'limit_down': limit_down}


def get_limit_stats() -> Dict[str, int]:
    """
    获取涨跌停统计
    返回：{'limit_up': 50, 'limit_down': 10}
    """
    try:
        _set_random_user_agent()
        _enforce_rate_limit()
        
        today = datetime.now().strftime('%Y%m%d')
        
        logger.info(f"[API调用] ak.stock_zt_pool_em(date={today}) 获取涨停池...")
        df_up = ak.stock_zt_pool_em(date=today)
        limit_up = len(df_up) if df_up is not None and not df_up.empty else 0
        
        logger.info(f"[API调用] ak.stock_zt_pool_dtgc_em(date={today}) 获取跌停池...")
        df_down = ak.stock_zt_pool_dtgc_em(date=today)
        limit_down = len(df_down) if df_down is not None and not df_down.empty else 0
        
        # 如果akshare获取失败，使用从实时行情计算的结果
        if limit_up == 0 and limit_down == 0:
            logger.info("[API返回] 涨跌停池数据为空，从实时行情计算涨跌停统计")
            stats = get_market_stats()
            return {'limit_up': stats['limit_up'], 'limit_down': stats['limit_down']}
        
        return {'limit_up': limit_up, 'limit_down': limit_down}
        
    except Exception as e:
        logger.error(f"[API错误] 获取涨跌停统计失败: {e}")
        stats = get_market_stats()
        return {'limit_up': stats['limit_up'], 'limit_down': stats['limit_down']}


def get_sectors_eastmoney() -> List[Dict[str, Any]]:
    """使用东方财富API获取板块涨幅排名（备用方案）"""
    try:
        url = "https://push2.eastmoney.com/api/qt/clist/get"
        params = {
            'pn': 1,
            'pz': 10,
            'po': 1,
            'np': 1,
            'fltt': 2,
            'invt': 2,
            'fid': 'f3',
            'fs': 'm:90+t:2',
            'fields': 'f2,f3,f4,f12,f14'
        }
        response = requests.get(url, params=params, headers={'User-Agent': random.choice(USER_AGENTS)}, timeout=10)
        data = response.json()
        
        sectors = []
        if 'data' in data and 'diff' in data['data']:
            for item in data['data']['diff'][:8]:
                sectors.append({
                    'name': item.get('f14', ''),
                    'change_pct': item.get('f3', 0)
                })
        return sectors
    except Exception as e:
        logger.error(f"[API错误] 使用东方财富API获取板块失败: {e}")
        return []


def get_sectors() -> List[Dict[str, Any]]:
    """获取板块涨幅排名"""
    try:
        _set_random_user_agent()
        _enforce_rate_limit()
        
        logger.info("[API调用] ak.stock_board_industry_name_em() 获取行业板块排行...")
        df = ak.stock_board_industry_name_em()
        
        if df is None or df.empty:
            logger.warning("[API返回] 行业板块数据为空，尝试使用东方财富API")
            return get_sectors_eastmoney()
        
        df['涨跌幅'] = pd.to_numeric(df['涨跌幅'], errors='coerce')
        df = df.dropna(subset=['涨跌幅'])
        
        top_sectors = df.nlargest(8, '涨跌幅')
        
        sectors = []
        for _, row in top_sectors.iterrows():
            sectors.append({
                'name': row['板块名称'],
                'change_pct': safe_float(row['涨跌幅'])
            })
        
        return sectors
        
    except Exception as e:
        logger.error(f"[API错误] 获取板块排名失败，尝试使用东方财富API: {e}")
        return get_sectors_eastmoney()


def get_first_limit_ups_eastmoney() -> List[Dict[str, str]]:
    """使用东方财富API获取率先涨停的股票（备用方案）"""
    try:
        today = datetime.now().strftime('%Y%m%d')
        url = "https://push2ex.eastmoney.com/getTopicZTPool"
        params = {
            'ut': '7eea3edcaed734bea9cb3e58b20a59fa',
            'dpt': 'wz.ztzt',
            'Ession': 'ztlb',
            'date': today
        }
        response = requests.get(url, params=params, headers={'User-Agent': random.choice(USER_AGENTS)}, timeout=10)
        data = response.json()
        
        stocks = []
        if 'data' in data and 'pool' in data['data']:
            for item in data['data']['pool'][:5]:
                stocks.append({'name': item.get('n', '')})
        return stocks
    except Exception as e:
        logger.error(f"[API错误] 使用东方财富API获取涨停股票失败: {e}")
        return []


def get_first_limit_ups() -> List[Dict[str, str]]:
    """获取率先涨停的股票"""
    try:
        _set_random_user_agent()
        _enforce_rate_limit()
        
        today = datetime.now().strftime('%Y%m%d')
        
        logger.info(f"[API调用] ak.stock_zt_pool_em(date={today}) 获取涨停池...")
        df = ak.stock_zt_pool_em(date=today)
        
        if df is None or df.empty:
            logger.warning("[API返回] 涨停池数据为空，尝试使用东方财富API")
            return get_first_limit_ups_eastmoney()
        
        if '首次封板时间' in df.columns:
            df['首次封板时间'] = pd.to_numeric(df['首次封板时间'], errors='coerce')
            df = df.sort_values('首次封板时间')
        
        stocks = []
        for _, row in df.head(5).iterrows():
            name = row.get('名称', '')
            if name:
                stocks.append({'name': str(name)})
        
        return stocks
        
    except Exception as e:
        logger.error(f"[API错误] 获取率先涨停股票失败，尝试使用东方财富API: {e}")
        return get_first_limit_ups_eastmoney()


if __name__ == "__main__":
    print("测试A股指数获取:")
    print(get_a_stock_index())
    
    print("\n测试市场涨跌统计:")
    print(get_market_stats())
    
    print("\n测试涨跌停统计:")
    print(get_limit_stats())
    
    print("\n测试板块排名:")
    print(get_sectors())
    
    print("\n测试率先涨停股票:")
    print(get_first_limit_ups())
