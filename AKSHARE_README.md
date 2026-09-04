# Akshare 数据源替换说明

## 概述

已将 stock-monitor 项目中的A股数据获取代码从直接使用东方财富API替换为使用 akshare 库，基于 daily_stock_analysis 项目的实现。

## 主要变更

### 1. 新增文件
- `akshare_data_fetcher.py`: 使用 akshare 获取A股数据的模块
- `test_akshare.py`: akshare 数据获取模块的测试脚本
- `test_mock.py`: 模拟测试脚本

### 2. 修改文件
- `stock_monitor.py`: 更新为使用新的 akshare 数据获取模块
- `requirements.txt`: 添加 akshare 依赖

## 功能说明

### 数据获取函数

1. **`get_a_stock_index()`**: 获取A股主要指数数据
   - 上证指数、深证成指、创业板指、科创50
   - 返回：价格、涨跌幅、成交量（亿）

2. **`get_market_stats()`**: 获取市场涨跌统计
   - 上涨家数、下跌家数、平盘家数
   - 涨停家数、跌停家数

3. **`get_limit_stats()`**: 获取涨跌停统计
   - 涨停家数、跌停家数

4. **`get_sectors()`**: 获取板块涨幅排名
   - 涨幅前8的行业板块

5. **`get_first_limit_ups()`**: 获取率先涨停的股票
   - 按首次封板时间排序的前5只股票

## 数据源优先级

1. **主要数据源**: akshare (基于新浪财经、东方财富等接口)
2. **备用数据源**: 东方财富API (当 akshare 失败时自动切换)

## 安装依赖

```bash
pip install -r requirements.txt
```

主要依赖：
- akshare>=1.10.0
- pandas>=1.5.0
- numpy>=1.21.0
- requests>=2.28.0
- pytz>=2023.3

## 使用方法

### 直接运行测试
```bash
python3 test_akshare.py
```

### 运行模拟测试
```bash
python3 test_mock.py
```

### 运行股票监控
```bash
python3 stock_monitor.py morning
python3 stock_monitor.py afternoon
```

## 优势

1. **数据更全面**: akshare 提供更丰富的A股数据
2. **更稳定**: 多数据源自动切换，避免单一API故障
3. **防封禁**: 内置速率限制和随机User-Agent
4. **易于维护**: 代码结构清晰，便于后续扩展

## 注意事项

1. 网络连接需要能够访问外部API
2. 首次运行可能需要较长时间下载数据
3. 建议在非交易时间测试，避免API限流
4. 如果遇到网络问题，会自动回退到东方财富API

## 故障排除

### 网络连接问题
如果遇到网络连接错误，请检查：
- 网络连接是否正常
- 防火墙设置
- DNS解析是否正常

### 依赖安装问题
```bash
# 使用国内镜像源
pip install -r requirements.txt -i https://pypi.tuna.tsinghua.edu.cn/simple
```

## 更新日志

- 2026-09-04: 初始版本，基于 daily_stock_analysis 项目实现
