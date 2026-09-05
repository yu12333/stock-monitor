#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
A股数据获取模块
直接复制自 daily_stock_analysis 的数据获取逻辑
支持多个数据源：TickFlow、Tushare、Akshare、Efinance
"""

import akshare as ak
import pandas as pd
import numpy as np
import math
import time
import random
import requests
import os
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


def _enforce_rate_limit():
    time.sleep(random.uniform(0.3, 0.8))


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


# ==================== 数据源1: TickFlow ====================

def _fetch_by_tickflow() -> Optional[Dict[str, Any]]:
    """使用 TickFlow 获取数据（需要 API Key）"""
    api_key = os.environ.get('TICKFLOW_API_KEY', '').strip()
    if not api_key:
        logger.info("[TickFlow] 未配置 API Key，跳过")
        return None
    
    try:
        _enforce_rate_limit()
        logger.info("[TickFlow] 尝试获取数据...")
        
        # TickFlow API 调用
        # 这里需要根据 TickFlow 的实际 API 实现
        # 暂时返回 None，让其他数据源处理
        logger.info("[TickFlow] 暂未实现，跳过")
        return None
    except Exception as e:
        logger.warning(f"[TickFlow] 失败: {e}")
        return None


# ==================== 数据源2: Tushare ====================

def _fetch_by_tushare() -> Optional[Dict[str, Any]]:
    """使用 Tushare 获取数据（需要 Token）"""
    token = os.environ.get('TUSHARE_TOKEN', '').strip()
    if not token:
        logger.info("[Tushare] 未配置 Token，跳过")
        return None
    
    try:
        _enforce_rate_limit()
        logger.info("[Tushare] 尝试获取数据...")
        
        import tushare as ts
        pro = ts.pro_api(token)
        
        # 获取每日指标
        today = datetime.now().strftime('%Y%m%d')
        df = pro.daily_basic(ts_code='', trade_date=today, 
                            fields='ts_code,close,pre_close,turnover_rate,pct_chg')
        
        if df is None or df.empty:
            logger.warning("[Tushare] 返回空数据")
            return None
        
        logger.info(f"[Tushare] 获取到 {len(df)} 条数据")
        
        # 计算涨跌统计
        up_count = 0
        down_count = 0
        flat_count = 0
        limit_up_count = 0
        limit_down_count = 0
        
        for _, row in df.iterrows():
            code = str(row.get('ts_code', ''))
            pct_chg = safe_float(row.get('pct_chg'))
            close = safe_float(row.get('close'))
            pre_close = safe_float(row.get('pre_close'))
            
            if close == 0 or pre_close == 0:
                continue
            
            pure_code = normalize_stock_code(code)
            
            # 确定涨跌幅比例
            if is_bse_code(pure_code):
                ratio = 0.30
            elif is_kc_cy_stock(pure_code):
                ratio = 0.20
            else:
                ratio = 0.10
            
            # 计算涨跌停价
            limit_up_price = np.floor(pre_close * (1 + ratio) * 100 + 0.5) / 100.0
            limit_down_price = np.floor(pre_close * (1 - ratio) * 100 + 0.5) / 100.0
            
            limit_up_tolerance = round(abs(pre_close * (1 + ratio) - limit_up_price), 10)
            limit_down_tolerance = round(abs(pre_close * (1 - ratio) - limit_down_price), 10)
            
            if abs(close - limit_up_price) <= limit_up_tolerance:
                limit_up_count += 1
            if abs(close - limit_down_price) <= limit_down_tolerance:
                limit_down_count += 1
            
            if pct_chg > 0:
                up_count += 1
            elif pct_chg < 0:
                down_count += 1
            else:
                flat_count += 1
        
        result = {
            'up_count': up_count,
            'down_count': down_count,
            'flat_count': flat_count,
            'limit_up_count': limit_up_count,
            'limit_down_count': limit_down_count,
            'total_amount': 0.0,  # Tushare 需要额外接口获取成交额
        }
        logger.info(f"[Tushare] 计算完成: 上涨{up_count} 下跌{down_count} 涨停{limit_up_count} 跌停{limit_down_count}")
        return result
    except Exception as e:
        logger.warning(f"[Tushare] 失败: {e}")
        return None


# ==================== 数据源3: Efinance ====================

def _fetch_by_efinance() -> Optional[Dict[str, Any]]:
    """使用 Efinance 获取数据"""
    try:
        _enforce_rate_limit()
        logger.info("[Efinance] 尝试获取数据...")
        
        import efinance as ef
        df = ef.stock.get_realtime_quotes()
        
        if df is None or df.empty:
            logger.warning("[Efinance] 返回空数据")
            return None
        
        logger.info(f"[Efinance] 获取到 {len(df)} 条数据")
        
        # 提取列名
        code_col = next((c for c in ['股票代码', '代码', 'code'] if c in df.columns), None)
        name_col = next((c for c in ['股票名称', '名称', 'name'] if c in df.columns), None)
        close_col = next((c for c in ['最新价', 'close', 'lastPrice'] if c in df.columns), None)
        pre_close_col = next((c for c in ['昨收', '昨收盘', 'pre_close'] if c in df.columns), None)
        amount_col = next((c for c in ['成交额', 'amount'] if c in df.columns), None)
        
        if not all([code_col, name_col, close_col, pre_close_col]):
            logger.error(f"[Efinance] 缺少必要列: {df.columns.tolist()}")
            return None
        
        up_count = 0
        down_count = 0
        flat_count = 0
        limit_up_count = 0
        limit_down_count = 0
        total_amount = 0.0
        
        for _, row in df.iterrows():
            code = str(row[code_col])
            name = str(row[name_col])
            current_price = row[close_col]
            pre_close = row[pre_close_col]
            
            if pd.isna(current_price) or pd.isna(pre_close) or current_price in ['-'] or pre_close in ['-']:
                continue
            
            amount = 0
            if amount_col and amount_col in df.columns:
                try:
                    amount = float(row[amount_col])
                except:
                    amount = 0
            
            if amount == 0:
                continue
            
            total_amount += amount
            current_price = float(current_price)
            pre_close = float(pre_close)
            
            pure_code = normalize_stock_code(code)
            
            if is_bse_code(pure_code):
                ratio = 0.30
            elif is_kc_cy_stock(pure_code):
                ratio = 0.20
            elif is_st_stock(name):
                ratio = 0.05
            else:
                ratio = 0.10
            
            limit_up_price = np.floor(pre_close * (1 + ratio) * 100 + 0.5) / 100.0
            limit_down_price = np.floor(pre_close * (1 - ratio) * 100 + 0.5) / 100.0
            
            limit_up_tolerance = round(abs(pre_close * (1 + ratio) - limit_up_price), 10)
            limit_down_tolerance = round(abs(pre_close * (1 - ratio) - limit_down_price), 10)
            
            if current_price > 0:
                if abs(current_price - limit_up_price) <= limit_up_tolerance:
                    limit_up_count += 1
                if abs(current_price - limit_down_price) <= limit_down_tolerance:
                    limit_down_count += 1
                
                if current_price > pre_close:
                    up_count += 1
                elif current_price < pre_close:
                    down_count += 1
                else:
                    flat_count += 1
        
        result = {
            'up_count': up_count,
            'down_count': down_count,
            'flat_count': flat_count,
            'limit_up_count': limit_up_count,
            'limit_down_count': limit_down_count,
            'total_amount': total_amount / 1e8,
        }
        logger.info(f"[Efinance] 计算完成: 上涨{up_count} 下跌{down_count} 涨停{limit_up_count} 跌停{limit_down_count}")
        return result
    except Exception as e:
        logger.warning(f"[Efinance] 失败: {e}")
        return None


# ==================== 数据源4: Akshare ====================

def _fetch_by_akshare() -> Optional[Dict[str, Any]]:
    """使用 Akshare 获取数据"""
    try:
        _enforce_rate_limit()
        logger.info("[Akshare] 尝试获取数据...")
        
        import akshare as ak
        df = ak.stock_zh_a_spot_em()
        
        if df is None or df.empty:
            logger.warning("[Akshare] 返回空数据")
            return None
        
        logger.info(f"[Akshare] 获取到 {len(df)} 条数据")
        
        code_col = next((c for c in ['代码', '股票代码'] if c in df.columns), None)
        name_col = next((c for c in ['名称', '股票名称'] if c in df.columns), None)
        close_col = next((c for c in ['最新价', 'close'] if c in df.columns), None)
        pre_close_col = next((c for c in ['昨收', 'pre_close'] if c in df.columns), None)
        amount_col = next((c for c in ['成交额', 'amount'] if c in df.columns), None)
        
        if not all([code_col, name_col, close_col, pre_close_col]):
            logger.error(f"[Akshare] 缺少必要列")
            return None
        
        up_count = 0
        down_count = 0
        flat_count = 0
        limit_up_count = 0
        limit_down_count = 0
        total_amount = 0.0
        
        for _, row in df.iterrows():
            code = str(row[code_col])
            name = str(row[name_col])
            current_price = row[close_col]
            pre_close = row[pre_close_col]
            
            if pd.isna(current_price) or pd.isna(pre_close) or current_price in ['-'] or pre_close in ['-']:
                continue
            
            amount = 0
            if amount_col and amount_col in df.columns:
                try:
                    amount = float(row[amount_col])
                except:
                    amount = 0
            
            if amount == 0:
                continue
            
            total_amount += amount
            current_price = float(current_price)
            pre_close = float(pre_close)
            
            pure_code = normalize_stock_code(code)
            
            if is_bse_code(pure_code):
                ratio = 0.30
            elif is_kc_cy_stock(pure_code):
                ratio = 0.20
            elif is_st_stock(name):
                ratio = 0.05
            else:
                ratio = 0.10
            
            limit_up_price = np.floor(pre_close * (1 + ratio) * 100 + 0.5) / 100.0
            limit_down_price = np.floor(pre_close * (1 - ratio) * 100 + 0.5) / 100.0
            
            limit_up_tolerance = round(abs(pre_close * (1 + ratio) - limit_up_price), 10)
            limit_down_tolerance = round(abs(pre_close * (1 - ratio) - limit_down_price), 10)
            
            if current_price > 0:
                if abs(current_price - limit_up_price) <= limit_up_tolerance:
                    limit_up_count += 1
                if abs(current_price - limit_down_price) <= limit_down_tolerance:
                    limit_down_count += 1
                
                if current_price > pre_close:
                    up_count += 1
                elif current_price < pre_close:
                    down_count += 1
                else:
                    flat_count += 1
        
        result = {
            'up_count': up_count,
            'down_count': down_count,
            'flat_count': flat_count,
            'limit_up_count': limit_up_count,
            'limit_down_count': limit_down_count,
            'total_amount': total_amount / 1e8,
        }
        logger.info(f"[Akshare] 计算完成: 上涨{up_count} 下跌{down_count} 涨停{limit_up_count} 跌停{limit_down_count}")
        return result
    except Exception as e:
        logger.warning(f"[Akshare] 失败: {e}")
        return None


# ==================== 主函数：多数据源自动切换 ====================

def get_market_stats() -> Dict[str, Any]:
    """
    获取市场涨跌统计
    直接复制自 daily_stock_analysis 的 DataManager.get_market_stats 逻辑
    数据源优先级：TickFlow -> Tushare -> Efinance -> Akshare
    """
    default_result = {
        'up_count': 0, 'down_count': 0, 'flat_count': 0,
        'limit_up_count': 0, 'limit_down_count': 0, 'total_amount': 0.0
    }
    
    # 尝试数据源1: TickFlow
    result = _fetch_by_tickflow()
    if result and (result['up_count'] > 0 or result['down_count'] > 0):
        return result
    
    # 尝试数据源2: Tushare
    result = _fetch_by_tushare()
    if result and (result['up_count'] > 0 or result['down_count'] > 0):
        return result
    
    # 尝试数据源3: Efinance
    result = _fetch_by_efinance()
    if result and (result['up_count'] > 0 or result['down_count'] > 0):
        return result
    
    # 尝试数据源4: Akshare
    result = _fetch_by_akshare()
    if result and (result['up_count'] > 0 or result['down_count'] > 0):
        return result
    
    logger.error("所有数据源都失败，返回默认值")
    return default_result


def get_a_stock_index() -> List[Dict[str, Any]]:
    """获取A股主要指数"""
    try:
        _enforce_rate_limit()
        import akshare as ak
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
        import akshare as ak
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
        import akshare as ak
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
    print("测试市场涨跌统计（多数据源）")
    print("=" * 50)
    
    stats = get_market_stats()
    print(f"\n上涨: {stats['up_count']} 家")
    print(f"下跌: {stats['down_count']} 家")
    print(f"平盘: {stats['flat_count']} 家")
    print(f"涨停: {stats['limit_up_count']} 家")
    print(f"跌停: {stats['limit_down_count']} 家")
    print(f"两市成交额: {stats['total_amount']:.0f} 亿")
