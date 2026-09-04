#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
使用示例：展示如何使用 akshare 数据获取模块
"""

import sys
import os

# 添加当前目录到 Python 路径
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def main():
    """主函数"""
    print("=" * 60)
    print("Akshare 数据获取模块使用示例")
    print("=" * 60)
    
    try:
        # 导入模块
        from akshare_data_fetcher import (
            get_a_stock_index,
            get_market_stats,
            get_limit_stats,
            get_sectors,
            get_first_limit_ups
        )
        
        print("\n1. 获取A股主要指数:")
        print("-" * 40)
        indices = get_a_stock_index()
        for idx in indices:
            print(f"{idx['name']}: {idx['price']:.2f} ({idx['change_pct']:.2f}%)")
        
        print("\n2. 获取市场涨跌统计:")
        print("-" * 40)
        stats = get_market_stats()
        print(f"上涨: {stats['up']}家")
        print(f"下跌: {stats['down']}家")
        print(f"平盘: {stats['flat']}家")
        print(f"涨停: {stats['limit_up']}家")
        print(f"跌停: {stats['limit_down']}家")
        
        print("\n3. 获取涨跌停统计:")
        print("-" * 40)
        limit_stats = get_limit_stats()
        print(f"涨停: {limit_stats['limit_up']}家")
        print(f"跌停: {limit_stats['limit_down']}家")
        
        print("\n4. 获取板块涨幅排名:")
        print("-" * 40)
        sectors = get_sectors()
        for i, sector in enumerate(sectors[:5], 1):
            print(f"{i}. {sector['name']}: {sector['change_pct']:.2f}%")
        
        print("\n5. 获取率先涨停股票:")
        print("-" * 40)
        limit_ups = get_first_limit_ups()
        for i, stock in enumerate(limit_ups[:3], 1):
            print(f"{i}. {stock['name']}")
        
        print("\n" + "=" * 60)
        print("示例完成")
        print("=" * 60)
        
    except ImportError as e:
        print(f"导入错误: {e}")
        print("请确保已安装所有依赖: pip install -r requirements.txt")
    except Exception as e:
        print(f"运行错误: {e}")

if __name__ == "__main__":
    main()
