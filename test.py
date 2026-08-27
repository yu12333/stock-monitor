#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
测试脚本 - 验证股票监控功能
"""

from stock_monitor import *

def test_data_fetch():
    """测试数据获取功能"""
    print("测试美股数据获取...")
    us_data = get_us_stock_data()
    print(f"获取到 {len(us_data)} 条美股数据")
    for stock in us_data:
        print(f"  {stock['name']}: {stock['price']:.2f} ({stock['change_percent']:+.2f}%)")
    
    print("\n测试韩国/日本数据获取...")
    kj_data = get_korea_japan_data()
    print(f"获取到 {len(kj_data)} 条韩国/日本数据")
    for stock in kj_data:
        print(f"  {stock['name']}: {stock['price']:.2f} ({stock['change_percent']:+.2f}%)")
    
    print("\n测试A股数据获取...")
    a_data = get_a_stock_data()
    print(f"获取到 {len(a_data)} 条A股数据")
    for stock in a_data:
        volume_str = f"成交量:{stock['volume']:.0f}亿" if 'volume' in stock else ""
        print(f"  {stock['name']}: {stock['price']:.2f} ({stock['change_percent']:+.2f}%) {volume_str}")
    
    return us_data, kj_data, a_data

def test_message_format():
    """测试消息格式化"""
    print("\n测试消息格式化...")
    us_data = [
        {'name': '道琼斯', 'price': 35234.56, 'change': 156.78, 'change_percent': 0.45},
        {'name': '标普500', 'price': 4456.78, 'change': 14.56, 'change_percent': 0.32},
        {'name': '纳斯达克', 'price': 14678.90, 'change': 82.34, 'change_percent': 0.56}
    ]
    
    kj_data = [
        {'name': '韩国KOSPI', 'price': 2567.89, 'change': -5.67, 'change_percent': -0.23},
        {'name': '日经225', 'price': 32456.78, 'change': 38.90, 'change_percent': 0.12}
    ]
    
    a_data = [
        {'name': '上证指数', 'price': 3234.56, 'change': 10.89, 'change_percent': 0.34, 'volume': 3456},
        {'name': '深证成指', 'price': 10678.90, 'change': 47.56, 'change_percent': 0.45, 'volume': 4567},
        {'name': '创业板指', 'price': 2156.78, 'change': 14.34, 'change_percent': 0.67, 'volume': 2345},
        {'name': '科创50', 'price': 987.65, 'change': 8.67, 'change_percent': 0.89, 'volume': 567}
    ]
    
    message = format_message(us_data, kj_data, a_data, analysis_type="morning")
    print("生成的消息:")
    print("-" * 50)
    print(message)
    print("-" * 50)

if __name__ == "__main__":
    print("股票监控系统测试")
    print("=" * 50)
    
    # 测试数据获取
    us_data, kj_data, a_data = test_data_fetch()
    
    # 测试消息格式化
    test_message_format()
    
    print("\n测试完成!")
    print("=" * 50)
    print("\n下一步:")
    print("1. 编辑 config.py 填入你的PushPlus Token")
    print("2. 运行 python stock_monitor.py morning 测试推送")
    print("3. 设置定时任务（参考 README.md）")
