#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
模拟测试 akshare 数据获取模块
"""

import sys
import os
import unittest
from unittest.mock import patch, MagicMock
import pandas as pd

# 添加当前目录到 Python 路径
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

class TestAkshareDataFetcher(unittest.TestCase):
    """测试 akshare_data_fetcher 模块"""
    
    @patch('akshare_data_fetcher.ak')
    def test_get_a_stock_index(self, mock_ak):
        """测试 get_a_stock_index 函数"""
        # 模拟 akshare 返回的数据
        mock_df = pd.DataFrame({
            '代码': ['sh000001', 'sz399001', 'sz399006', 'sh000688'],
            '名称': ['上证指数', '深证成指', '创业板指', '科创50'],
            '最新价': [3200.50, 12000.75, 2500.25, 1000.50],
            '涨跌幅': [1.25, -0.50, 2.10, -1.30],
            '成交额': [250000000000, 180000000000, 150000000000, 50000000000]
        })
        mock_ak.stock_zh_index_spot_sina.return_value = mock_df
        
        # 导入模块
        import akshare_data_fetcher as akf
        
        # 测试函数
        result = akf.get_a_stock_index()
        
        # 验证结果
        self.assertEqual(len(result), 4)
        self.assertEqual(result[0]['name'], '上证指数')
        self.assertAlmostEqual(result[0]['price'], 3200.50)
        self.assertAlmostEqual(result[0]['change_pct'], 1.25)
        self.assertAlmostEqual(result[0]['volume'], 2500.0)  # 转换为亿
    
    @patch('akshare_data_fetcher.ak')
    def test_get_market_stats(self, mock_ak):
        """测试 get_market_stats 函数"""
        # 模拟 akshare 返回的数据
        mock_df = pd.DataFrame({
            '最新价': [10.50, 20.75, 30.25, 5.50, 15.00],
            '昨收': [10.00, 21.00, 30.00, 6.00, 15.00]
        })
        mock_ak.stock_zh_a_spot_em.return_value = mock_df
        
        # 导入模块
        import akshare_data_fetcher as akf
        
        # 测试函数
        result = akf.get_market_stats()
        
        # 验证结果
        self.assertEqual(result['up'], 2)  # 10.50 > 10.00, 30.25 > 30.00
        self.assertEqual(result['down'], 2)  # 20.75 < 21.00, 5.50 < 6.00
        self.assertEqual(result['flat'], 1)  # 15.00 == 15.00
    
    @patch('akshare_data_fetcher.ak')
    def test_get_sectors(self, mock_ak):
        """测试 get_sectors 函数"""
        # 模拟 akshare 返回的数据
        mock_df = pd.DataFrame({
            '板块名称': ['半导体', '新能源', '医药', '金融', '消费'],
            '涨跌幅': [3.5, 2.8, 1.5, -0.5, -1.2]
        })
        mock_ak.stock_board_industry_name_em.return_value = mock_df
        
        # 导入模块
        import akshare_data_fetcher as akf
        
        # 测试函数
        result = akf.get_sectors()
        
        # 验证结果
        self.assertEqual(len(result), 5)
        self.assertEqual(result[0]['name'], '半导体')
        self.assertAlmostEqual(result[0]['change_pct'], 3.5)
    
    @patch('akshare_data_fetcher.ak')
    def test_get_limit_stats(self, mock_ak):
        """测试 get_limit_stats 函数"""
        # 模拟 akshare 返回的数据
        mock_df_up = pd.DataFrame({'名称': ['股票1', '股票2', '股票3']})
        mock_df_down = pd.DataFrame({'名称': ['股票4', '股票5']})
        mock_ak.stock_zt_pool_em.return_value = mock_df_up
        mock_ak.stock_zt_pool_dtgc_em.return_value = mock_df_down
        
        # 导入模块
        import akshare_data_fetcher as akf
        
        # 测试函数
        result = akf.get_limit_stats()
        
        # 验证结果
        self.assertEqual(result['limit_up'], 3)
        self.assertEqual(result['limit_down'], 2)
    
    @patch('akshare_data_fetcher.ak')
    def test_get_first_limit_ups(self, mock_ak):
        """测试 get_first_limit_ups 函数"""
        # 模拟 akshare 返回的数据
        mock_df = pd.DataFrame({
            '名称': ['股票A', '股票B', '股票C', '股票D', '股票E'],
            '首次封板时间': [93000, 93100, 93200, 93300, 93400]
        })
        mock_ak.stock_zt_pool_em.return_value = mock_df
        
        # 导入模块
        import akshare_data_fetcher as akf
        
        # 测试函数
        result = akf.get_first_limit_ups()
        
        # 验证结果
        self.assertEqual(len(result), 5)
        self.assertEqual(result[0]['name'], '股票A')

if __name__ == "__main__":
    unittest.main()
