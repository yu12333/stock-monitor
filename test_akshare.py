#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
测试 akshare 数据获取模块
"""

import sys
import os

# 添加当前目录到 Python 路径
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def test_akshare_data_fetcher():
    """测试 akshare_data_fetcher 模块"""
    print("=" * 50)
    print("测试 akshare_data_fetcher 模块")
    print("=" * 50)
    
    try:
        import akshare_data_fetcher as akf
        print("✓ 模块导入成功")
        
        # 测试各个函数
        print("\n1. 测试 get_a_stock_index:")
        try:
            result = akf.get_a_stock_index()
            print(f"   获取到 {len(result)} 个指数")
            for item in result:
                print(f"   - {item['name']}: {item['price']} ({item['change_pct']:.2f}%)")
        except Exception as e:
            print(f"   ✗ 失败: {e}")
        
        print("\n2. 测试 get_market_stats:")
        try:
            result = akf.get_market_stats()
            print(f"   上涨: {result['up']}, 下跌: {result['down']}, 平盘: {result['flat']}")
            print(f"   涨停: {result['limit_up']}, 跌停: {result['limit_down']}")
        except Exception as e:
            print(f"   ✗ 失败: {e}")
        
        print("\n3. 测试 get_sectors:")
        try:
            result = akf.get_sectors()
            print(f"   获取到 {len(result)} 个板块")
            for i, item in enumerate(result[:3], 1):
                print(f"   {i}. {item['name']}: {item['change_pct']:.2f}%")
        except Exception as e:
            print(f"   ✗ 失败: {e}")
        
        print("\n4. 测试 get_limit_stats:")
        try:
            result = akf.get_limit_stats()
            print(f"   涨停: {result['limit_up']}, 跌停: {result['limit_down']}")
        except Exception as e:
            print(f"   ✗ 失败: {e}")
        
        print("\n5. 测试 get_first_limit_ups:")
        try:
            result = akf.get_first_limit_ups()
            print(f"   获取到 {len(result)} 只率先涨停股票")
            for item in result:
                print(f"   - {item['name']}")
        except Exception as e:
            print(f"   ✗ 失败: {e}")
        
        print("\n" + "=" * 50)
        print("测试完成")
        print("=" * 50)
        
    except ImportError as e:
        print(f"✗ 模块导入失败: {e}")
    except Exception as e:
        print(f"✗ 测试失败: {e}")

if __name__ == "__main__":
    test_akshare_data_fetcher()
