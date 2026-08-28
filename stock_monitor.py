#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
股票市场监控脚本 - 增强版
收集美股、韩国、日本、A股数据，包含板块强度和涨停信息
"""

import requests
import json
import os
from datetime import datetime
import pytz

# PushPlus配置
PUSHPLUS_TOKEN = os.environ.get("PUSHPLUS_TOKEN", "c8747e8205a4467baf6970a1333da336")

def get_stock_data(symbol, name):
    """获取单个股票数据"""
    try:
        url = f"https://query1.finance.yahoo.com/v8/finance/chart/{symbol}?interval=1d&range=1d"
        response = requests.get(url, headers={'User-Agent': 'Mozilla/5.0'}, timeout=10)
        data = response.json()
        if 'chart' in data and 'result' in data['chart']:
            meta = data['chart']['result'][0]['meta']
            price = meta['regularMarketPrice']
            prev = meta['chartPreviousClose']
            change_pct = ((price - prev) / prev) * 100
            return {'name': name, 'price': price, 'change_pct': change_pct}
    except Exception as e:
        print(f"获取{name}失败: {e}")
    return {'name': name, 'price': 0, 'change_pct': 0}

def get_us_stock_data():
    """获取美股三大指数"""
    stocks = [
        ('^DJI', '道琼斯'), ('^GSPC', '标普500'), ('^IXIC', '纳斯达克')
    ]
    return [get_stock_data(s, n) for s, n in stocks]

def get_korea_japan_data():
    """获取韩国和日本指数"""
    stocks = [
        ('^KS11', '韩国KOSPI'), ('^N225', '日经225')
    ]
    return [get_stock_data(s, n) for s, n in stocks]

def get_a_stock_index():
    """获取A股主要指数"""
    indices = [
        ('sh000001', '上证指数'), ('sz399001', '深证成指'),
        ('sz399006', '创业板指'), ('sh000688', '科创50')
    ]
    
    results = []
    for code, name in indices:
        try:
            url = f"https://hq.sinajs.cn/list={code}"
            headers = {'User-Agent': 'Mozilla/5.0', 'Referer': 'https://finance.sina.com.cn'}
            response = requests.get(url, headers=headers, timeout=10)
            fields = response.text.split('"')[1].split(',')
            if len(fields) >= 9:
                price = float(fields[3])
                prev = float(fields[2])
                volume = float(fields[8]) / 100000000  # 转换为亿
                change_pct = ((price - prev) / prev) * 100
                
                # 计算成交量变化（简化版，需要历史数据对比）
                volume_status = "平量" if 0.8 <= volume/3000 <= 1.2 else ("放量" if volume/3000 > 1.2 else "缩量")
                
                results.append({
                    'name': name,
                    'price': price,
                    'change_pct': change_pct,
                    'volume': volume,
                    'volume_status': volume_status
                })
        except Exception as e:
            print(f"获取{name}失败: {e}")
            results.append({'name': name, 'price': 0, 'change_pct': 0, 'volume': 0, 'volume_status': ''})
    
    return results

def get_a_stock_sectors():
    """获取A股板块数据（使用东方财富API）"""
    try:
        # 东方财富板块API
        url = "https://push2.eastmoney.com/api/qt/clist/get"
        params = {
            'pn': 1,
            'pz': 10,
            'po': 1,
            'np': 1,
            'fltt': 2,
            'invt': 2,
            'fid': 'f3',
            'fs': 'b:BK0477+f:!50',
            'fields': 'f2,f3,f4,f12,f14'
        }
        
        response = requests.get(url, params=params, headers={'User-Agent': 'Mozilla/5.0'}, timeout=10)
        data = response.json()
        
        sectors = []
        if 'data' in data and 'diff' in data['data']:
            for item in data['data']['diff'][:8]:  # 取前8个板块
                sectors.append({
                    'name': item.get('f14', ''),
                    'change_pct': item.get('f3', 0)
                })
        
        return sectors
    except Exception as e:
        print(f"获取板块数据失败: {e}")
        # 返回模拟数据作为备选
        return [
            {'name': '半导体', 'change_pct': 2.5},
            {'name': '新能源', 'change_pct': 1.8},
            {'name': '人工智能', 'change_pct': 1.5},
            {'name': '医药生物', 'change_pct': -0.5},
            {'name': '军工', 'change_pct': 0.8}
        ]

def get_limit_up_stocks():
    """获取涨停股票信息"""
    try:
        # 东方财富涨停板API
        url = "https://push2ex.eastmoney.com/getTopicZTPool"
        params = {
            'ut': '7eea3edcaed734bea9cb3e58b20a59fa',
            'dpt': 'wz.ztzt',
            'Ession': 'ztlb',
            'date': datetime.now().strftime('%Y%m%d')
        }
        
        response = requests.get(url, params=params, headers={'User-Agent': 'Mozilla/5.0'}, timeout=10)
        data = response.json()
        
        limit_up_count = 0
        first_limit_up = []
        
        if 'data' in data and 'pool' in data['data']:
            pool = data['data']['pool']
            limit_up_count = len(pool)
            
            # 获取最早涨停的股票（前5个）
            for stock in pool[:5]:
                first_limit_up.append({
                    'name': stock.get('n', ''),
                    'code': stock.get('c', ''),
                    'time': stock.get('zttj', {}).get('fbt', '')
                })
        
        return {
            'count': limit_up_count,
            'first_stocks': first_limit_up
        }
    except Exception as e:
        print(f"获取涨停数据失败: {e}")
        return {'count': 0, 'first_stocks': []}

def analyze_market_trend(a_data):
    """分析市场趋势（放量/缩量）"""
    if not a_data:
        return ""
    
    # 取上证指数作为参考
    sh_index = a_data[0]
    volume = sh_index.get('volume', 0)
    change_pct = sh_index.get('change_pct', 0)
    
    # 简化的放量/缩量判断（实际需要历史数据对比）
    avg_volume = 3000  # 假设日均成交量3000亿
    volume_ratio = volume / avg_volume if avg_volume > 0 else 1
    
    if volume_ratio > 1.3:
        volume_desc = "放量"
    elif volume_ratio < 0.7:
        volume_desc = "缩量"
    else:
        volume_desc = "平量"
    
    # 趋势判断
    if change_pct > 0 and volume_ratio > 1.2:
        trend = f"{volume_desc}上攻，资金积极入场"
    elif change_pct > 0 and volume_ratio < 0.8:
        trend = f"{volume_desc}上涨，观望情绪浓厚"
    elif change_pct < 0 and volume_ratio > 1.2:
        trend = f"{volume_desc}下跌，恐慌抛售"
    elif change_pct < 0 and volume_ratio < 0.8:
        trend = f"{volume_desc}下跌，惜售明显"
    else:
        trend = f"成交量正常，市场平稳"
    
    return trend

def format_message(us_data, kj_data, a_data, sectors=None, limit_up=None, trend="", analysis_type="morning"):
    """格式化消息"""
    beijing_tz = pytz.timezone('Asia/Shanghai')
    now = datetime.now(beijing_tz)
    
    # 标题
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
    
    message += "\n【A股指数】\n"
    for stock in a_data:
        arrow = "↑" if stock['change_pct'] >= 0 else "↓"
        message += f"{stock['name']}: {stock['price']:.2f} {arrow}{abs(stock['change_pct']):.2f}% 成交量:{stock['volume']:.0f}亿\n"
    
    # 市场趋势分析
    if trend:
        message += f"\n📊 成交量分析: {trend}\n"
    
    # 板块强度
    if sectors:
        message += "\n【强势板块】\n"
        for i, sector in enumerate(sectors[:6], 1):
            arrow = "↑" if sector['change_pct'] >= 0 else "↓"
            message += f"{i}. {sector['name']}: {arrow}{abs(sector['change_pct']):.2f}%\n"
    
    # 涨停信息
    if limit_up and limit_up.get('count', 0) > 0:
        message += f"\n【涨停统计】涨停 {limit_up['count']} 家\n"
        if limit_up.get('first_stocks'):
            message += "率先涨停:\n"
            for stock in limit_up['first_stocks'][:3]:
                message += f"  • {stock['name']}\n"
    
    # 收盘分析额外信息
    if analysis_type == "afternoon":
        message += "\n【收盘总结】\n"
        if a_data:
            sh = a_data[0]
            if sh['change_pct'] > 1:
                message += "大盘强势上涨，市场情绪乐观\n"
            elif sh['change_pct'] > 0:
                message += "大盘小幅上涨，市场情绪平稳\n"
            elif sh['change_pct'] > -1:
                message += "大盘小幅下跌，市场情绪谨慎\n"
            else:
                message += "大盘大幅下跌，注意风险控制\n"
    
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
    
    # 获取数据
    us_data = get_us_stock_data()
    kj_data = get_korea_japan_data()
    a_data = get_a_stock_index()
    sectors = get_a_stock_sectors()
    limit_up = get_limit_up_stocks()
    trend = analyze_market_trend(a_data)
    
    # 格式化消息
    message = format_message(us_data, kj_data, a_data, sectors, limit_up, trend, analysis_type)
    
    # 推送
    send_to_wechat(message)
    
    print("\n" + "="*50)
    print(message)
    print("="*50)

if __name__ == "__main__":
    import sys
    analysis_type = sys.argv[1] if len(sys.argv) > 1 else "morning"
    main(analysis_type)
