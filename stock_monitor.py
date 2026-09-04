#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
股票市场监控脚本 - 使用 akshare 获取A股数据
数据源：akshare (基于东方财富、新浪财经等)
"""

import requests
import json
import os
from datetime import datetime
import pytz

# 导入新的 akshare 数据获取模块
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

def format_message(api_time, us_data, kj_data, a_data, sectors, market_stats, limit_stats, first_limit_ups, analysis_type):
    """格式化消息 - 使用类似盘面总览的表格格式"""
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
    
    # 盘面总览表格（类似 daily_stock_analysis 的格式）
    message += "\n【盘面总览】\n"
    message += "| 指标 | 数值 | 观察 |\n"
    message += "|------|------|------|\n"
    
    # 上涨/下跌/平盘
    up = market_stats.get('up', 0)
    down = market_stats.get('down', 0)
    flat = market_stats.get('flat', 0)
    total = up + down + flat
    up_ratio = up / total if total > 0 else 0
    message += f"| 上涨/下跌/平盘 | {up} / {down} / {flat} | 上涨占比(不含平盘) {up_ratio:.1%} |\n"
    
    # 涨停/跌停
    limit_up = limit_stats.get('limit_up', 0)
    limit_down = limit_stats.get('limit_down', 0)
    limit_spread = limit_up - limit_down
    message += f"| 涨停/跌停 | {limit_up} / {limit_down} | 涨跌停差 {limit_spread:+d} |\n"
    
    # 两市成交额
    total_amount = market_stats.get('total_amount', 0)
    if total_amount > 10000:
        turnover_desc = "成交活跃"
    elif total_amount > 8000:
        turnover_desc = "成交适中"
    else:
        turnover_desc = "成交清淡"
    message += f"| 两市成交额 | {total_amount:.0f} 亿 | {turnover_desc} |\n"
    
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
    limit_stats = get_limit_stats()
    first_limit_ups = get_first_limit_ups()
    
    message = format_message(api_time, us_data, kj_data, a_data, sectors, market_stats, limit_stats, first_limit_ups, analysis_type)
    
    send_to_wechat(message)
    
    print("\n" + "="*50)
    print(message)
    print("="*50)

if __name__ == "__main__":
    import sys
    analysis_type = sys.argv[1] if len(sys.argv) > 1 else "morning"
    main(analysis_type)
