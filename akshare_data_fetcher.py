#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
使用 akshare 获取A股数据的模块
基于 daily_stock_analysis 项目的实现
"""

import akshare as ak
import pandas as pd
import numpy as np
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
    requests_headers = {
        'User-Agent': random.choice(USER_AGENTS)
    }
    # 注意：akshare 底层使用 requests，这里设置全局 headers
    # 实际上 akshare 内部有自己的 headers 处理，这里主要是为了兼容
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


def get_a_stock_index_eastmoney() -> List[Dict[str, Any]]:
    """
    使用东方财富API获取A股主要指数数据（备用方案）
    
    返回：
    [
        {'name': '上证指数', 'price': 3200.50, 'change_pct': 1.25, 'volume': 2500.0},
        ...
    ]
    """
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
    """
    获取A股主要指数数据
    
    返回：
    [
        {'name': '上证指数', 'price': 3200.50, 'change_pct': 1.25, 'volume': 2500.0},
        ...
    ]
    """
    try:
        _set_random_user_agent()
        _enforce_rate_limit()
        
        # 使用 akshare 获取指数行情（新浪财经接口）
        logger.info("[API调用] ak.stock_zh_index_spot_sina() 获取指数行情...")
        df = ak.stock_zh_index_spot_sina()
        
        if df is None or df.empty:
            logger.warning("[API返回] 指数行情数据为空，尝试使用东方财富API")
            return get_a_stock_index_eastmoney()
        
        # 定义要获取的指数
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
                # 尝试带前缀查找
                row = df[df['代码'].str.contains(code)]
            
            if not row.empty:
                row = row.iloc[0]
                price = safe_float(row.get('最新价', 0))
                change_pct = safe_float(row.get('涨跌幅', 0))
                volume = safe_float(row.get('成交额', 0)) / 100000000  # 转换为亿
                
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
    """
    使用东方财富API获取市场涨跌统计（备用方案）
    
    返回：
    {'up': 1500, 'down': 800, 'flat': 200, 'limit_up': 50, 'limit_down': 10}
    """
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
            'fs': 'm:0+t:6,m:0+t:80,m:1+t:2,m:1+t:23',  # A股
            'fields': 'f104,f105,f106'
        }
        response = requests.get(url, params=params, headers={'User-Agent': random.choice(USER_AGENTS)}, timeout=10)
        data = response.json()
        
        if 'data' in data and 'total' in data['data']:
            # 通过总数计算
            total = data['data']['total']
            # 这个API不直接返回涨跌家数，需要用其他方式
            pass
        
        # 使用沪深两市分别获取
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
    获取市场涨跌统计
    
    返回：
    {'up': 1500, 'down': 800, 'flat': 200, 'limit_up': 50, 'limit_down': 10}
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
            current_price = safe_float(row.get('最新价'))
            pre_close = safe_float(row.get('昨收'))
            
            if current_price == 0 or pre_close == 0:
                continue
            
            # 计算涨跌幅
            change_pct = (current_price - pre_close) / pre_close * 100
            
            if change_pct > 0:
                up_count += 1
            elif change_pct < 0:
                down_count += 1
            else:
                flat_count += 1
            
            # 计算涨跌停（简化版，精确计算需要更复杂的逻辑）
            if abs(change_pct) >= 9.9:  # 接近10%涨跌幅
                if change_pct > 0:
                    limit_up_count += 1
                else:
                    limit_down_count += 1
        
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
    """
    使用东方财富API获取涨跌停统计（备用方案）
    
    返回：
    {'limit_up': 50, 'limit_down': 10}
    """
    today = datetime.now().strftime('%Y%m%d')
    
    # 涨停
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
    
    # 跌停
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
    
    返回：
    {'limit_up': 50, 'limit_down': 10}
    """
    try:
        _set_random_user_agent()
        _enforce_rate_limit()
        
        today = datetime.now().strftime('%Y%m%d')
        
        # 获取涨停池
        logger.info(f"[API调用] ak.stock_zt_pool_em(date={today}) 获取涨停池...")
        df_up = ak.stock_zt_pool_em(date=today)
        limit_up = len(df_up) if df_up is not None and not df_up.empty else 0
        
        # 获取跌停池
        logger.info(f"[API调用] ak.stock_zt_pool_dtgc_em(date={today}) 获取跌停池...")
        df_down = ak.stock_zt_pool_dtgc_em(date=today)
        limit_down = len(df_down) if df_down is not None and not df_down.empty else 0
        
        return {'limit_up': limit_up, 'limit_down': limit_down}
        
    except Exception as e:
        logger.error(f"[API错误] 获取涨跌停统计失败，尝试使用东方财富API: {e}")
        return get_limit_stats_eastmoney()


def get_sectors_eastmoney() -> List[Dict[str, Any]]:
    """
    使用东方财富API获取板块涨幅排名（备用方案）
    
    返回：
    [{'name': '半导体', 'change_pct': 3.5}, ...]
    """
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
    """
    获取板块涨幅排名
    
    返回：
    [{'name': '半导体', 'change_pct': 3.5}, ...]
    """
    try:
        _set_random_user_agent()
        _enforce_rate_limit()
        
        logger.info("[API调用] ak.stock_board_industry_name_em() 获取行业板块排行...")
        df = ak.stock_board_industry_name_em()
        
        if df is None or df.empty:
            logger.warning("[API返回] 行业板块数据为空，尝试使用东方财富API")
            return get_sectors_eastmoney()
        
        # 按涨跌幅排序
        df['涨跌幅'] = pd.to_numeric(df['涨跌幅'], errors='coerce')
        df = df.dropna(subset=['涨跌幅'])
        
        # 获取涨幅前8的板块
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
    """
    使用东方财富API获取率先涨停的股票（备用方案）
    
    返回：
    [{'name': '股票名称'}, ...]
    """
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
    """
    获取率先涨停的股票
    
    返回：
    [{'name': '股票名称'}, ...]
    """
    try:
        _set_random_user_agent()
        _enforce_rate_limit()
        
        today = datetime.now().strftime('%Y%m%d')
        
        logger.info(f"[API调用] ak.stock_zt_pool_em(date={today}) 获取涨停池...")
        df = ak.stock_zt_pool_em(date=today)
        
        if df is None or df.empty:
            logger.warning("[API返回] 涨停池数据为空，尝试使用东方财富API")
            return get_first_limit_ups_eastmoney()
        
        # 按首次封板时间排序
        if '首次封板时间' in df.columns:
            df['首次封板时间'] = pd.to_numeric(df['首次封板时间'], errors='coerce')
            df = df.sort_values('首次封板时间')
        
        # 获取前5只率先涨停的股票
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
    # 测试代码
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
