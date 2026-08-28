#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
股票市场监控脚本 - 使用东方财富API
数据源：东方财富（国内最可靠的财经数据源之一）
"""

import requests
import json
import os
from datetime import datetime
import pytz

# PushPlus配置
PUSHPLUS_TOKEN = os.environ.get("PUSHPLUS_TOKEN", "c8747e8205a4467baf6970a1333da336")

def get_us_stock_data():
    """获取美股三大指数（东方财富API）"""
    try:
        # 东方财富外盘指数API
        url = "https://push2.eastmoney.com/api/qt/ulist.np/get"
        params = {
            'fltt': 2,
            'fields': 'f2,f3,f4,f12,f14',
            'secids': '100.DJIA,100.SPX,100.NDX'  # 道琼斯、标普500、纳斯达克
        }
        
        response = requests.get(url, params=params, headers={'User-Agent': 'Mozilla/5.0'}, timeout=10)
        data = response.json()
        
        stocks = []
        if 'data' in data and 'diff' in data['data']:
            names = ['道琼斯', '标普500', '纳斯达克']
            for i, item in enumerate(data['data']['diff']):
                stocks.append({
                    'name': names[i],
                    'price': item.get('f2', 0),
                    'change_pct': item.get('f3', 0)
                })
        
        return stocks if stocks else [
            {'name': '道琼斯', 'price': 0, 'change_pct': 0},
            {'name': '标普500', 'price': 0, 'change_pct': 0},
            {'name': '纳斯达克', 'price': 0, 'change_pct': 0}
        ]
    except Exception as e:
        print(f"获取美股失败: {e}")
        return [
            {'name': '道琼斯', 'price': 0, 'change_pct': 0},
            {'name': '标普500', 'price': 0, 'change_pct': 0},
            {'name': '纳斯达克', 'price': 0, 'change_pct': 0}
        ]

def get_korea_japan_data():
    """获取韩国和日本指数（东方财富API）"""
    try:
        url = "https://push2.eastmoney.com/api/qt/ulist.np/get"
        params = {
            'fltt': 2,
            'fields': 'f2,f3,f4,f12,f14',
            'secids': '100.KS11,100.N225'  # 韩国KOSPI、日经225
        }
        
        response = requests.get(url, params=params, headers={'User-Agent': 'Mozilla/5.0'}, timeout=10)
        data = response.json()
        
        stocks = []
        if 'data' in data and 'diff' in data['data']:
            names = ['韩国KOSPI', '日经225']
            for i, item in enumerate(data['data']['diff']):
                stocks.append({
                    'name': names[i],
                    'price': item.get('f2', 0),
                    'change_pct': item.get('f3', 0)
                })
        
        return stocks if stocks else [
            {'name': '韩国KOSPI', 'price': 0, 'change_pct': 0},
            {'name': '日经225', 'price': 0, 'change_pct': 0}
        ]
    except Exception as e:
        print(f"获取韩国日本失败: {e}")
        return [
            {'name': '韩国KOSPI', 'price': 0, 'change_pct': 0},
            {'name': '日经225', 'price': 0, 'change_pct': 0}
        ]

def get_a_stock_index():
    """获取A股主要指数（东方财富API）"""
    try:
        url = "https://push2.eastmoney.com/api/qt/ulist.np/get"
        params = {
            'fltt': 2,
            'fields': 'f2,f3,f4,f6,f12,f14',
            'secids': '1.000001,0.399001,0.399006,1.000688'  # 上证、深证、创业板、科创50
        }
        
        response = requests.get(url, params=params, headers={'User-Agent': 'Mozilla/5.0'}, timeout=10)
        data = response.json()
        
        stocks = []
        names = ['上证指数', '深证成指', '创业板指', '科创50']
        if 'data' in data and 'diff' in data['data']:
            for i, item in enumerate(data['data']['diff']):
                stocks.append({
                    'name': names[i],
                    'price': item.get('f2', 0),
                    'change_pct': item.get('f3', 0),
                    'volume': item.get('f6', 0) / 100000000  # 转换为亿
                })
        
        return stocks if stocks else [
            {'name': '上证指数', 'price': 0, 'change_pct': 0, 'volume': 0},
            {'name': '深证成指', 'price': 0, 'change_pct': 0, 'volume': 0},
            {'name': '创业板指', 'price': 0, 'change_pct': 0, 'volume': 0},
            {'name': '科创50', 'price': 0, 'change_pct': 0, 'volume': 0}
        ]
    except Exception as e:
        print(f"获取A股指数失败: {e}")
        return [
            {'name': '上证指数', 'price': 0, 'change_pct': 0, 'volume': 0},
            {'name': '深证成指', 'price': 0, 'change_pct': 0, 'volume': 0},
            {'name': '创业板指', 'price': 0, 'change_pct': 0, 'volume': 0},
            {'name': '科创50', 'price': 0, 'change_pct': 0, 'volume': 0}
        ]

def get_market_stats():
    """获取A股涨跌家数（东方财富API）"""
    try:
        url = "https://push2.eastmoney.com/api/qt/ulist.np/get"
        params = {
            'fltt': 2,
            'fields': 'f104,f105,f106',
            'secids': '1.000001'
        }
        
        response = requests.get(url, params=params, headers={'User-Agent': 'Mozilla/5.0'}, timeout=10)
        data = response.json()
        
        if 'data' in data and 'diff' in data['data']:
            item = data['data']['diff'][0]
            return {
                'up': item.get('f104', 0),
                'down': item.get('f105', 0),
                'flat': item.get('f106', 0)
            }
    except Exception as e:
        print(f"获取涨跌家数失败: {e}")
    
    return {'up': 0, 'down': 0, 'flat': 0}

def get_limit_stats():
    """获取涨跌停统计（东方财富API）"""
    try:
        # 涨停
        url_up = "https://push2ex.eastmoney.com/getTopicZTPool"
        params_up = {
            'ut': '7eea3edcaed734bea9cb3e58b20a59fa',
            'dpt': 'wz.ztzt',
            'Ession': 'ztlb',
            'date': datetime.now().strftime('%Y%m%d')
        }
        resp_up = requests.get(url_up, params=params_up, headers={'User-Agent': 'Mozilla/5.0'}, timeout=10)
        limit_up = len(resp_up.json().get('data', {}).get('pool', []))
        
        # 跌停
        url_down = "https://push2ex.eastmoney.com/getTopicDTPool"
        params_down = {
            'ut': '7eea3edcaed734bea9cb3e58b20a59fa',
            'dpt': 'wz.ztzt',
            'Ession': 'dtlb',
            'date': datetime.now().strftime('%Y%m%d')
        }
        resp_down = requests.get(url_down, params=params_down, headers={'User-Agent': 'Mozilla/5.0'}, timeout=10)
        limit_down = len(resp_down.json().get('data', {}).get('pool', []))
        
        return {'limit_up': limit_up, 'limit_down': limit_down}
    except Exception as e:
        print(f"获取涨跌停失败: {e}")
        return {'limit_up': 0, 'limit_down': 0}

def get_sectors():
    """获取板块涨幅排名（东方财富API）"""
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
            'fs': 'm:90+t:2',  # 行业板块
            'fields': 'f2,f3,f4,f12,f14'
        }
        
        response = requests.get(url, params=params, headers={'User-Agent': 'Mozilla/5.0'}, timeout=10)
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
        print(f"获取板块失败: {e}")
        return []

def get_first_limit_ups():
    """获取率先涨停的股票（东方财富API）"""
    try:
        url = "https://push2ex.eastmoney.com/getTopicZTPool"
        params = {
            'ut': '7eea3edcaed734bea9cb3e58b20a59fa',
            'dpt': 'wz.ztzt',
            'Ession': 'ztlb',
            'date': datetime.now().strftime('%Y%m%d')
        }
        
        response = requests.get(url, params=params, headers={'User-Agent': 'Mozilla/5.0'}, timeout=10)
        data = response.json()
        
        stocks = []
        if 'data' in data and 'pool' in data['data']:
            for item in data['data']['pool'][:5]:
                stocks.append({'name': item.get('n', '')})
        
        return stocks
    except Exception as e:
        print(f"获取涨停股票失败: {e}")
        return []

def format_message(us_data, kj_data, a_data, sectors, market_stats, limit_stats, first_limit_ups, analysis_type):
    """格式化消息"""
    beijing_tz = pytz.timezone('Asia/Shanghai')
    now = datetime.now(beijing_tz)
    
    titles = {
        "morning": "📊 早盘市场播报",
        "morning_close": "📊 上午收盘播报",
        "noon": "📊 午盘播报",
        "afternoon": "📊 A股收盘分析"
    }
    title = titles.get(analysis_type, "📊 市场播报")
    message = f"{title} - {now.strftime('%Y-%m-%d %H:%M')}\n\n"
    
    # 外盘
    message += "【外盘市场】\n"
    for stock in us_data + kj_data:
        arrow = "↑" if stock['change_pct'] >= 0 else "↓"
        message += f"{stock['name']}: {stock['price']:.2f} {arrow}{abs(stock['change_pct']):.2f}%\n"
    
    # A股指数
    message += "\n【A股指数】\n"
    for stock in a_data:
        arrow = "↑" if stock['change_pct'] >= 0 else "↓"
        message += f"{stock['name']}: {stock['price']:.2f} {arrow}{abs(stock['change_pct']):.2f}% 成交量:{stock['volume']:.0f}亿\n"
    
    # 涨跌家数
    if market_stats:
        message += f"\n【涨跌家数】\n上涨: {market_stats['up']}家 | 下跌: {market_stats['down']}家 | 平盘: {market_stats['flat']}家\n"
    
    # 涨跌停
    if limit_stats:
        message += f"\n【涨跌停统计】\n涨停: {limit_stats['limit_up']}家 | 跌停: {limit_stats['limit_down']}家\n"
    
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
    
    us_data = get_us_stock_data()
    kj_data = get_korea_japan_data()
    a_data = get_a_stock_index()
    sectors = get_sectors()
    market_stats = get_market_stats()
    limit_stats = get_limit_stats()
    first_limit_ups = get_first_limit_ups()
    
    message = format_message(us_data, kj_data, a_data, sectors, market_stats, limit_stats, first_limit_ups, analysis_type)
    
    send_to_wechat(message)
    
    print("\n" + "="*50)
    print(message)
    print("="*50)

if __name__ == "__main__":
    import sys
    analysis_type = sys.argv[1] if len(sys.argv) > 1 else "morning"
    main(analysis_type)
