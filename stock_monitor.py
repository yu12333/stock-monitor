#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
股票市场监控脚本 - 使用 akshare 获取A股数据
盘面总览格式直接复制自 daily_stock_analysis
"""

import requests
import json
import os
from datetime import datetime
import pytz

# 导入数据获取模块
try:
    from akshare_data_fetcher import (
        get_a_stock_index,
        get_market_stats,
        get_limit_stats,
        get_sectors,
        get_first_limit_ups
    )
    USE_AKSHARE = True
except ImportError as e:
    print(f"警告：无法导入 akshare_data_fetcher 模块: {e}")
    USE_AKSHARE = False

PUSHPLUS_TOKEN = os.environ.get("PUSHPLUS_TOKEN", "")


def get_api_time():
    """获取API调用时间"""
    beijing_tz = pytz.timezone('Asia/Shanghai')
    return datetime.now(beijing_tz).strftime('%Y-%m-%d %H:%M:%S')


def get_us_stock_data():
    """获取美股三大指数"""
    try:
        url = "https://push2.eastmoney.com/api/qt/ulist.np/get"
        params = {
            'fltt': 2,
            'fields': 'f2,f3,f4,f12,f14',
            'secids': '100.DJIA,100.SPX,100.NDX'
        }
        response = requests.get(url, params=params, headers={'User-Agent': 'Mozilla/5.0'}, timeout=10)
        data = response.json()
        
        stocks = []
        names = ['道琼斯', '标普500', '纳斯达克']
        if 'data' in data and 'diff' in data['data']:
            for i, item in enumerate(data['data']['diff']):
                stocks.append({
                    'name': names[i],
                    'price': item.get('f2', 0),
                    'change_pct': item.get('f3', 0)
                })
        return stocks if stocks else [{'name': n, 'price': 0, 'change_pct': 0} for n in names]
    except Exception as e:
        print(f"获取美股失败: {e}")
        return [{'name': n, 'price': 0, 'change_pct': 0} for n in ['道琼斯', '标普500', '纳斯达克']]


def get_korea_japan_data():
    """获取韩国和日本指数"""
    try:
        url = "https://push2.eastmoney.com/api/qt/ulist.np/get"
        params = {
            'fltt': 2,
            'fields': 'f2,f3,f4,f12,f14',
            'secids': '100.KS11,100.N225'
        }
        response = requests.get(url, params=params, headers={'User-Agent': 'Mozilla/5.0'}, timeout=10)
        data = response.json()
        
        stocks = []
        names = ['韩国KOSPI', '日经225']
        if 'data' in data and 'diff' in data['data']:
            for i, item in enumerate(data['data']['diff']):
                stocks.append({
                    'name': names[i],
                    'price': item.get('f2', 0),
                    'change_pct': item.get('f3', 0)
                })
        return stocks if stocks else [{'name': n, 'price': 0, 'change_pct': 0} for n in names]
    except Exception as e:
        print(f"获取韩国日本失败: {e}")
        return [{'name': n, 'price': 0, 'change_pct': 0} for n in ['韩国KOSPI', '日经225']]


def _describe_turnover(total_amount: float) -> str:
    """
    描述成交额活跃度
    直接复制自 daily_stock_analysis/src/market_analyzer.py
    """
    if total_amount >= 15000:
        return "高活跃度"
    if total_amount >= 9000:
        return "中等活跃"
    if total_amount > 0:
        return "缩量观望"
    return "暂无数据"


def build_stats_block(market_stats: Dict) -> str:
    """
    构建盘面总览表格
    直接复制自 daily_stock_analysis/src/market_analyzer.py._build_stats_block
    """
    up_count = market_stats.get('up_count', 0)
    down_count = market_stats.get('down_count', 0)
    flat_count = market_stats.get('flat_count', 0)
    limit_up_count = market_stats.get('limit_up_count', 0)
    limit_down_count = market_stats.get('limit_down_count', 0)
    total_amount = market_stats.get('total_amount', 0.0)
    
    has_stats = up_count or down_count or total_amount
    if not has_stats:
        return ""
    
    participation = up_count + down_count
    up_ratio = up_count / participation if participation else 0.0
    limit_spread = limit_up_count - limit_down_count
    
    lines = [
        "| 指标 | 数值 | 观察 |",
        "|------|------|------|",
        f"| 上涨/下跌/平盘 | {up_count} / {down_count} / {flat_count} | 上涨占比(不含平盘) {up_ratio:.1%} |",
        f"| 涨停/跌停 | {limit_up_count} / {limit_down_count} | 涨跌停差 {limit_spread:+d} |",
        f"| 两市成交额 | {total_amount:.0f} 亿 | {_describe_turnover(total_amount)} |",
    ]
    
    return "\n".join(lines)


def format_message(api_time, us_data, kj_data, a_data, sectors, market_stats, first_limit_ups, analysis_type):
    """格式化消息"""
    titles = {
        "morning": "📊 早盘市场播报",
        "morning_close": "📊 上午收盘播报",
        "noon": "📊 午盘播报",
        "afternoon": "📊 A股收盘分析"
    }
    title = titles.get(analysis_type, "📊 市场播报")
    
    # 标题加上API时间
    message = f"{title}\n⏰ 数据时间: {api_time}\n\n"
    
    # 外盘
    message += "【外盘市场】\n"
    for stock in us_data + kj_data:
        if stock['price'] > 0:
            arrow = "↑" if stock['change_pct'] >= 0 else "↓"
            message += f"{stock['name']}: {stock['price']:.2f} {arrow}{abs(stock['change_pct']):.2f}%\n"
        else:
            message += f"{stock['name']}: 暂无数据\n"
    
    # A股指数
    message += "\n【A股指数】\n"
    for stock in a_data:
        if stock['price'] > 0:
            arrow = "↑" if stock['change_pct'] >= 0 else "↓"
            message += f"{stock['name']}: {stock['price']:.2f} {arrow}{abs(stock['change_pct']):.2f}% 成交量:{stock['volume']:.0f}亿\n"
        else:
            message += f"{stock['name']}: 暂无数据\n"
    
    # 盘面总览表格（直接复制自 daily_stock_analysis）
    stats_block = build_stats_block(market_stats)
    if stats_block:
        message += "\n【盘面总览】\n"
        message += stats_block + "\n"
    
    # 板块
    if sectors:
        message += "\n【强势板块】\n"
        for i, s in enumerate(sectors[:6], 1):
            arrow = "↑" if s['change_pct'] >= 0 else "↓"
            message += f"{i}. {s['name']}: {arrow}{abs(s['change_pct']):.2f}%\n"
    
    # 率先涨停
    if first_limit_ups:
        message += "\n【率先涨停】\n"
        for stock in first_limit_ups[:3]:
            message += f"• {stock['name']}\n"
    
    return message


def send_to_wechat(message):
    """推送到微信"""
    if not PUSHPLUS_TOKEN:
        print("未配置PUSHPLUS_TOKEN")
        return False
    
    try:
        resp = requests.post("http://www.pushplus.plus/send", json={
            "token": PUSHPLUS_TOKEN,
            "title": "📊 股票监控",
            "content": message,
            "template": "txt"
        }, timeout=10)
        result = resp.json()
        print(f"推送结果: {result}")
        return result.get('code') == 200
    except Exception as e:
        print(f"推送失败: {e}")
        return False


def main(analysis_type="morning"):
    """主函数"""
    print(f"开始收集数据... ({analysis_type})")
    print(f"使用 akshare 数据源: {USE_AKSHARE}")
    
    api_time = get_api_time()
    us_data = get_us_stock_data()
    kj_data = get_korea_japan_data()
    a_data = get_a_stock_index()
    sectors = get_sectors()
    market_stats = get_market_stats()
    first_limit_ups = get_first_limit_ups()
    
    message = format_message(
        api_time, us_data, kj_data, a_data, 
        sectors, market_stats, first_limit_ups, analysis_type
    )
    
    send_to_wechat(message)
    
    print("\n" + "="*50)
    print(message)
    print("="*50)


if __name__ == "__main__":
    import sys
    analysis_type = sys.argv[1] if len(sys.argv) > 1 else "morning"
    main(analysis_type)
