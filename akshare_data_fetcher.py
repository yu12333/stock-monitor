#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
A股数据获取模块
直接复制自 daily_stock_analysis 的 EfinanceFetcher 实现
使用 efinance 一次性获取全量数据
"""

import akshare as ak
import pandas as pd
import numpy as np
import time
import random
from datetime import datetime
from typing import Dict, List, Any, Optional
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def safe_float(value: Any) -> float:
    try:
        if pd.isna(value):
            return 0.0
        return float(value)
    except (TypeError, ValueError):
        return 0.0


def normalize_stock_code(code: str) -> str:
    if not code:
        return ""
    code = str(code).strip()
    for prefix in ['sh', 'sz', 'bj', 'SH', 'SZ', 'BJ']:
        if code.startswith(prefix):
            code = code[len(prefix):]
    return code


def is_bse_code(code: str) -> bool:
    c = normalize_stock_code(code)
    if len(c) != 6 or not c.isdigit():
        return False
    if c.startswith("900"):
        return False
    return c.startswith(("92", "43", "81", "82", "83", "87", "88"))


def is_st_stock(name: str) -> bool:
    return 'ST' in (name or "").upper()


def is_kc_cy_stock(code: str) -> bool:
    c = normalize_stock_code(code)
    return c.startswith("688") or c.startswith("30")


def _calc_market_stats(df: pd.DataFrame) -> Optional[Dict[str, Any]]:
    """
    从行情 DataFrame 计算涨跌统计
    直接复制自 daily_stock_analysis/data_provider/efinance_fetcher.py
    """
    df = df.copy()
    
    # 提取列名（兼容不同接口）
    code_col = next((c for c in ['代码', '股票代码', 'ts_code', 'stock_code'] if c in df.columns), None)
    name_col = next((c for c in ['名称', '股票名称', 'name'] if c in df.columns), None)
    close_col = next((c for c in ['最新价', 'close', 'lastPrice'] if c in df.columns), None)
    pre_close_col = next((c for c in ['昨收', '昨日收盘', 'pre_close', 'lastClose'] if c in df.columns), None)
    amount_col = next((c for c in ['成交额', 'amount'] if c in df.columns), None)
    
    if not all([code_col, name_col, close_col, pre_close_col]):
        logger.error(f"缺少必要列: {df.columns.tolist()}")
        return None
    
    limit_up_count = 0
    limit_down_count = 0
    up_count = 0
    down_count = 0
    flat_count = 0
    total_amount = 0.0

    for code, name, current_price, pre_close, amount in zip(
        df[code_col], df[name_col], df[close_col], df[pre_close_col], df[amount_col]
    ):
        # 停牌过滤
        if pd.isna(current_price) or pd.isna(pre_close) or current_price in ['-'] or pre_close in ['-'] or amount == 0:
            continue
        
        current_price = float(current_price)
        pre_close = float(pre_close)
        total_amount += float(amount)
        
        pure_code = normalize_stock_code(str(code))

        # 确定涨跌幅比例
        if is_bse_code(pure_code):
            ratio = 0.30
        elif is_kc_cy_stock(pure_code):
            ratio = 0.20
        elif is_st_stock(name):
            ratio = 0.05
        else:
            ratio = 0.10

        # 计算涨跌停价
        limit_up_price = np.floor(pre_close * (1 + ratio) * 100 + 0.5) / 100.0
        limit_down_price = np.floor(pre_close * (1 - ratio) * 100 + 0.5) / 100.0

        limit_up_tolerance = round(abs(pre_close * (1 + ratio) - limit_up_price), 10)
        limit_down_tolerance = round(abs(pre_close * (1 - ratio) - limit_down_price), 10)

        # 精确比对
        if current_price > 0:
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
        'up_count': up_count,
        'down_count': down_count,
        'flat_count': flat_count,
        'limit_up_count': limit_up_count,
        'limit_down_count': limit_down_count,
        'total_amount': total_amount / 1e8,
    }


def get_market_stats() -> Dict[str, Any]:
    """
    获取市场涨跌统计
    直接复制自 daily_stock_analysis 的 EfinanceFetcher
    使用 efinance 一次性获取全量数据
    """
    default_result = {
        'up_count': 0, 'down_count': 0, 'flat_count': 0,
        'limit_up_count': 0, 'limit_down_count': 0, 'total_amount': 0.0
    }
    
    try:
        import efinance as ef
        
        logger.info("[Efinance] 获取全市场实时行情...")
        df = ef.stock.get_realtime_quotes()
        
        if df is None or df.empty:
            logger.warning("[Efinance] 返回空数据")
            return default_result
        
        logger.info(f"[Efinance] 获取到 {len(df)} 只股票")
        
        result = _calc_market_stats(df)
        if result:
            logger.info(f"[Efinance] 上涨:{result['up_count']} 下跌:{result['down_count']} "
                       f"涨停:{result['limit_up_count']} 跌停:{result['limit_down_count']} "
                       f"成交额:{result['total_amount']:.0f}亿")
            return result
        
    except ImportError:
        logger.warning("[Efinance] 未安装 efinance 库，尝试 akshare...")
    except Exception as e:
        logger.warning(f"[Efinance] 失败: {e}，尝试 akshare...")
    
    # 备用方案：akshare
    try:
        import akshare as ak
        
        logger.info("[Akshare] 获取全市场实时行情...")
        df = ak.stock_zh_a_spot_em()
        
        if df is None or df.empty:
            logger.warning("[Akshare] 返回空数据")
            return default_result
        
        logger.info(f"[Akshare] 获取到 {len(df)} 只股票")
        
        result = _calc_market_stats(df)
        if result:
            logger.info(f"[Akshare] 上涨:{result['up_count']} 下跌:{result['down_count']} "
                       f"涨停:{result['limit_up_count']} 跌停:{result['limit_down_count']} "
                       f"成交额:{result['total_amount']:.0f}亿")
            return result
        
    except Exception as e:
        logger.error(f"[Akshare] 失败: {e}")
    
    return default_result


def get_a_stock_index() -> List[Dict[str, Any]]:
    """获取A股主要指数"""
    try:
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


if __name__ == "__main__":
    print("=" * 50)
    print("测试市场涨跌统计")
    print("=" * 50)
    
    stats = get_market_stats()
    print(f"\n上涨: {stats['up_count']} 家")
    print(f"下跌: {stats['down_count']} 家")
    print(f"平盘: {stats['flat_count']} 家")
    print(f"涨停: {stats['limit_up_count']} 家")
    print(f"跌停: {stats['limit_down_count']} 家")
    print(f"两市成交额: {stats['total_amount']:.0f} 亿")
