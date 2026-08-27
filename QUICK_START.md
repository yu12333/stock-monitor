# 股票监控系统 - 快速开始

## 功能概述

监控全球主要股票市场，定时推送到微信：
- **美股**: 道琼斯、标普500、纳斯达克
- **亚太**: 韩国KOSPI、日经225
- **A股**: 上证指数、深证成指、创业板指、科创50

## 推送时间（北京时间）

- 09:30 - 早盘播报
- 10:00 - 早盘播报  
- 14:30 - A股收盘分析

## 三步快速启动

### 第1步: 配置PushPlus

1. 访问 http://www.pushplus.plus/
2. 微信扫码注册登录
3. 复制你的Token
4. 编辑 `config.py` (Python版) 或 `config.js` (Node.js版)
5. 替换 `YOUR_PUSHPLUS_TOKEN` 为你的Token

### 第2步: 测试运行

**Python版本** (推荐):
```bash
# 安装依赖
pip install requests pytz

# 测试运行
python stock_monitor.py morning
```

**Node.js版本**:
```bash
# 测试运行
node stock_monitor.js morning
```

**Bash版本** (基础功能):
```bash
./stock_monitor.sh
```

### 第3步: 设置定时任务

**macOS/Linux**:
```bash
# 编辑crontab
crontab -e

# 添加以下行（修改路径）
30 9 * * 1-5 cd /path/to/stock-monitor && python stock_monitor.py morning
0 10 * * 1-5 cd /path/to/stock-monitor && python stock_monitor.py morning
30 14 * * 1-5 cd /path/to/stock-monitor && python stock_monitor.py afternoon
```

**Windows**:
使用"任务计划程序"创建三个定时任务

## 消息格式示例

```
📊 早盘市场播报 - 2026-08-27 09:30

【外盘市场】
道琼斯: 35234.56 ↑+0.45%
标普500: 4456.78 ↑+0.32%
纳斯达克: 14678.90 ↑+0.56%
韩国KOSPI: 2567.89 ↓-0.23%
日经225: 32456.78 ↑+0.12%

【A股市场】
上证指数: 3234.56 ↑+0.34% 成交量:3456亿
深证成指: 10678.90 ↑+0.45% 成交量:4567亿
创业板指: 2156.78 ↑+0.67% 成交量:2345亿
科创50: 987.65 ↑+0.89% 成交量:567亿
```

## 常见问题

### Q: 推送失败怎么办？
A: 
1. 检查Token是否正确
2. 确认网络连接
3. 查看PushPlus官网状态

### Q: 数据获取失败？
A:
1. 检查网络连接
2. 部分API可能需要代理
3. 查看脚本错误信息

### Q: 如何修改推送时间？
A: 编辑crontab或任务计划程序中的时间设置

## 文件说明

- `stock_monitor.py` - Python主脚本（推荐）
- `stock_monitor.js` - Node.js版本
- `stock_monitor.sh` - Bash版本（基础功能）
- `config.py` / `config.js` - 配置文件
- `README.md` - 完整文档
- `QUICK_START.md` - 本文件

## 技术支持

如遇问题，请检查：
1. 依赖是否安装
2. Token是否配置
3. 网络是否正常
4. 查看脚本错误输出
