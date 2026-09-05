#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
A股数据获取模块 - 多数据源备用方案
直接复制自 daily_stock_analysis 的实现逻辑
"""

import akshare as ak
import pandas as pd
import numpy as np
import math
import time
import random
import requests
from datetime import datetime
from typing import Dict, List, Any, Optional
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


# ==================== 辅助函数（复制自 daily_stock_analysis/data_provider/base.py）====================

def normalize_stock_code(code: str) -> str:
    """标准化股票代码，去除前缀"""
    if not code:
        return ""
    code = str(code).strip()
    for prefix in ['sh', 'sz', 'bj', 'SH', 'SZ', 'BJ']:
        if code.startswith(prefix):
            code = code[len(prefix):]
    return code


def is_bse_code(code: str) -> bool:
    """检查是否为北交所股票代码"""
    c = (code or "").strip().split(".")[0]
    if len(c) != 6 or not c.isdigit():
        return False
    if c.startswith("900"):
        return False
    return c.startswith(("92", "43", "81", "82", "83", "87", "88"))


def is_st_stock(name: str) -> bool:
    """检查是否为ST股票"""
    return 'ST' in (name or "").upper()


def is_kc_cy_stock(code: str) -> bool:
    """检查是否为科创板或创业板股票"""
    c = (code or "").strip().split(".")[0]
    return c.startswith("688") or c.startswith("30")


def safe_float(value: Any) -> float:
    """安全的浮点数转换"""
    try:
        if pd.isna(value):
            return 0.0
        return float(value)
    except (TypeError, ValueError):
        return 0.0


def _enforce_rate_limit():
    """强制速率限制"""
    time.sleep(random.uniform(0.3, 0.8))


# ==================== 核心计算函数（直接复制自 efinance_fetcher._calc_market_stats）====================

def _calc_market_stats(df: pd.DataFrame) -> Optional[Dict[str, Any]]:
    """
    从行情 DataFrame 计算涨跌统计
    直接复制自 daily_stock_analysis/data_provider/efinance_fetcher.py
    """
    df = df.copy()
    
    # 提取基础比对数据：最新价、昨收
    code_col = next((c for c in ['代码', '股票代码', 'ts_code', 'stock_code'] if c in df.columns), None)
    name_col = next((c for c in ['名称', '股票名称', 'name'] if c in df.columns), None)
    close_col = next((c for c in ['最新价', 'close', 'lastPrice'] if c in df.columns), None)
    pre_close_col = next((c for c in ['昨收', '昨日收盘', 'pre_close', 'lastClose'] if c in df.columns), None)
    amount_col = next((c for c in ['成交额', 'amount'] if c in df.columns), None)
    
    if not all([code_col, name_col, close_col, pre_close_col]):
        logger.error(f"缺少必要列: code={code_col}, name={name_col}, close={close_col}, pre_close={pre_close_col}")
        return None
    
    limit_up_count = 0
    limit_down_count = 0
    up_count = 0
    down_count = 0
    flat_count = 0
    total_amount = 0.0

    for idx, row in df.iterrows():
        code = row[code_col]
        name = row[name_col]
        current_price = row[close_col]
        pre_close = row[pre_close_col]
        
        # 停牌过滤
        if pd.isna(current_price) or pd.isna(pre_close) or current_price in ['-'] or pre_close in ['-']:
            continue
        
        # 获取成交额
        amount = 0
        if amount_col and amount_col in df.columns:
            try:
                amount = float(row[amount_col])
            except:
                amount = 0
        
        if amount == 0:
            continue
        
        total_amount += amount
        
        # 转换为float
        current_price = float(current_price)
        pre_close = float(pre_close)
        
        # 获取去除前缀的纯数字代码
        pure_code = normalize_stock_code(str(code))

        # 确定每只股票的涨跌幅比例
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

        limit_up_price_Tolerance = round(abs(pre_close * (1 + ratio) - limit_up_price), 10)
        limit_down_price_Tolerance = round(abs(pre_close * (1 - ratio) - limit_down_price), 10)

        # 精确比对
        if current_price > 0:
            is_limit_up = abs(current_price - limit_up_price) <= limit_up_price_Tolerance
            is_limit_down = abs(current_price - limit_down_price) <= limit_down_price_Tolerance

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
        'up_count': up_count,
        'down_count': down_count,
        'flat_count': flat_count,
        'limit_up_count': limit_up_count,
        'limit_down_count': limit_down_count,
        'total_amount': total_amount / 1e8,
    }


# ==================== 数据源1：akshare（东方财富）====================

def _fetch_by_akshare() -> Optional[Dict[str, Any]]:
    """使用 akshare 获取数据"""
    try:
        _enforce_rate_limit()
        logger.info("[数据源1] 尝试 ak.stock_zh_a_spot_em()...")
        df = ak.stock_zh_a_spot_em()
        if df is not None and not df.empty:
            result = _calc_market_stats(df)
            if result and (result['up_count'] > 0 or result['down_count'] > 0):
                logger.info(f"[数据源1] akshare 成功: 上涨{result['up_count']} 下跌{result['down_count']}")
                return result
    except Exception as e:
        logger.warning(f"[数据源1] akshare 失败: {e}")
    return None


# ==================== 数据源2：东方财富直接API====================

def _fetch_by_eastmoney_api() -> Optional[Dict[str, Any]]:
    """使用东方财富API直接获取"""
    try:
        import requests
        _enforce_rate_limit()
        logger.info("[数据源2] 尝试东方财富API...")
        
        # 获取涨跌家数
        url = "https://push2.eastmoney.com/api/qt/ulist.np/get"
        params = {
            'fltt': 2,
            'fields': 'f104,f105,f106',
            'secids': '1.000001'
        }
        response = requests.get(url, params=params, headers={'User-Agent': 'Mozilla/5.0'}, timeout=10)
        data = response.json()
        
        if 'data' in data and 'diff' in data['data'] and len(data['data']['diff']) > 0:
            item = data['data']['diff'][0]
            up_count = item.get('f104', 0)
            down_count = item.get('f105', 0)
            flat_count = item.get('f106', 0)
            
            # 获取成交额
            url2 = "https://push2.eastmoney.com/api/qt/ulist.np/get"
            params2 = {
                'fltt': 2,
                'fields': 'f6',
                'secids': '1.000001,0.399001,0.399006,1.000688'
            }
            response2 = requests.get(url2, params=params2, headers={'User-Agent': 'Mozilla/5.0'}, timeout=10)
            data2 = response2.json()
            
            total_amount = 0
            if 'data' in data2 and 'diff' in data2['data']:
                for item2 in data2['data']['diff']:
                    total_amount += item2.get('f6', 0)
            
            result = {
                'up_count': up_count,
                'down_count': down_count,
                'flat_count': flat_count,
                'limit_up_count': 0,  # 这个API不提供涨跌停数据
                'limit_down_count': 0,
                'total_amount': total_amount / 1e8,
            }
            logger.info(f"[数据源2] 东方财富API 成功: 上涨{up_count} 下跌{down_count}")
            return result
    except Exception as e:
        logger.warning(f"[数据源2] 东方财富API 失败: {e}")
    return None


# ==================== 数据源3：新浪财经====================

def _fetch_by_sina() -> Optional[Dict[str, Any]]:
    """使用新浪财经获取涨跌家数"""
    try:
        import requests
        _enforce_rate_limit()
        logger.info("[数据源3] 尝试新浪财经...")
        
        url = "https://vip.stock.finance.sina.com.cn/quotes_service/api/json_v2.php/Market_Center.getHQNodeStockCount?node=hs_a"
        response = requests.get(url, headers={'User-Agent': 'Mozilla/5.0'}, timeout=10)
        
        # 新浪返回的是股票总数，不是涨跌家数，这个方案不太可行
        # 改用另一个接口
        url2 = "https://hq.sinajs.cn/list=sh000001"
        response2 = requests.get(url2, headers={'User-Agent': 'Mozilla/5.0', 'Referer': 'https://finance.sina.com.cn'}, timeout=10)
        
        if response2.status_code == 200:
            # 解析上证指数数据
            content = response2.text
            if 'var hq_str_sh000001' in content:
                parts = content.split('"')[1].split(',')
                if len(parts) > 3:
                    # 新浪接口只能获取指数数据，无法获取涨跌家数
                    pass
        
        logger.warning("[数据源3] 新浪接口不支持涨跌家数查询")
    except Exception as e:
        logger.warning(f"[数据源3] 新浪 失败: {e}")
    return None


# ==================== 主函数：多数据源自动切换====================

def get_market_stats() -> Dict[str, Any]:
    """
    获取市场涨跌统计
    模仿 daily_stock_analysis 的 DataManager，自动切换数据源
    """
    default_result = {
        'up_count': 0, 'down_count': 0, 'flat_count': 0,
        'limit_up_count': 0, 'limit_down_count': 0, 'total_amount': 0.0
    }
    
    # 尝试数据源1: akshare
    result = _fetch_by_akshare()
    if result:
        return result
    
    # 尝试数据源2: 东方财富API
    result = _fetch_by_eastmoney_api()
    if result:
        # 这个API没有涨跌停数据，尝试用akshare补充
        try:
            _enforce_rate_limit()
            df = ak.stock_zt_pool_em(date=datetime.now().strftime('%Y%m%d'))
            if df is not None and not df.empty:
                result['limit_up_count'] = len(df)
        except:
            pass
        
        try:
            _enforce_rate_limit()
            df = ak.stock_zt_pool_dtgc_em(date=datetime.now().strftime('%Y%m%d'))
            if df is not None and not df.empty:
                result['limit_down_count'] = len(df)
        except:
            pass
        
        return result
    
    # 尝试数据源3: 新浪
    result = _fetch_by_sina()
    if result:
        return result
    
    # 所有数据源都失败
    logger.error("所有数据源都失败，返回默认值")
    return default_result


def get_a_stock_index() -> List[Dict[str, Any]]:
    """获取A股主要指数"""
    try:
        _enforce_rate_limit()
        df = ak.stock_zh_index_spot_sina()
        if df is None or df.empty:
            return [{'name': n, 'price': 0, 'change_pct': 0, 'volume': 0} 
                    for n in ['上证指数', '深证成指', '创业板指', '科创50']]
        
        indices_map = {
            'sh000001': '上证指数', 
            'sz399001': '深证成指', 
            'sz399006': '创业板指', 
            'sh000688': '科创50'
        }
        results = []
        for code, name in indices_map.items():
            row = df[df['代码'] == code]
            if not row.empty:
                row = row.iloc[0]
                results.append({
                    'name': name,
                    'price': safe_float(row.get('最新价', 0)),
                    'change_pct': safe_float(row.get('涨跌幅', 0)),
                    'volume': safe_float(row.get('成交额', 0)) / 100000000
                })
            else:
                results.append({'name': name, 'price': 0, 'change_pct': 0, 'volume': 0})
        return results
    except Exception as e:
        logger.error(f"获取A股指数失败: {e}")
        return [{'name': n, 'price': 0, 'change_pct': 0, 'volume': 0} 
                for n in ['上证指数', '深证成指', '创业板指', '科创50']]


def get_limit_stats() -> Dict[str, int]:
    """获取涨跌停统计"""
    stats = get_market_stats()
    return {
        'limit_up': stats['limit_up_count'], 
        'limit_down': stats['limit_down_count']
    }


def get_sectors() -> List[Dict[str, Any]]:
    """获取板块涨幅排名"""
    try:
        _enforce_rate_limit()
        df = ak.stock_board_industry_name_em()
        if df is None or df.empty:
            return []
        df['涨跌幅'] = pd.to_numeric(df['涨跌幅'], errors='coerce')
        df = df.dropna(subset=['涨跌幅'])
        top_sectors = df.nlargest(8, '涨跌幅')
        return [{'name': row['板块名称'], 'change_pct': safe_float(row['涨跌幅'])} 
                for _, row in top_sectors.iterrows()]
    except Exception as e:
        logger.error(f"获取板块排名失败: {e}")
        return []


def get_first_limit_ups() -> List[Dict[str, str]]:
    """获取率先涨停的股票"""
    try:
        _enforce_rate_limit()
        today = datetime.now().strftime('%Y%m%d')
        df = ak.stock_zt_pool_em(date=today)
        if df is None or df.empty:
            return []
        if '首次封板时间' in df.columns:
            df['首次封板时间'] = pd.to_numeric(df['首次封板时间'], errors='coerce')
            df = df.sort_values('首次封板时间')
        return [{'name': str(row.get('名称', ''))} 
                for _, row in df.head(5).iterrows() if row.get('名称')]
    except Exception as e:
        logger.error(f"获取率先涨停股票失败: {e}")
        return []


# ==================== 测试 ====================

if __name__ == "__main__":
    print("=" * 50)
    print("测试市场涨跌统计（多数据源备用）")
    print("=" * 50)
    
    stats = get_market_stats()
    print(f"\n上涨: {stats['up_count']} 家")
    print(f"下跌: {stats['down_count']} 家")
    print(f"平盘: {stats['flat_count']} 家")
    print(f"涨停: {stats['limit_up_count']} 家")
    print(f"跌停: {stats['limit_down_count']} 家")
    print(f"两市成交额: {stats['total_amount']:.0f} 亿")
