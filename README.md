# 股票市场监控系统

## 功能介绍

本系统用于监控全球主要股票市场数据，并定时推送到微信：

- **美股三大指数**：道琼斯、标普500、纳斯达克
- **亚太市场**：韩国KOSPI、日经225
- **A股市场**：上证指数、深证成指、创业板指、科创50

## 推送时间

- 每天早上 09:30（北京时间）- 早盘播报
- 每天早上 10:00（北京时间）- 早盘播报
- 每天下午 14:30（北京时间）- A股收盘分析

## 安装步骤

### 1. 安装依赖

```bash
pip install requests pytz
```

### 2. 配置PushPlus

1. 访问 [PushPlus官网](http://www.pushplus.plus/)
2. 注册并登录
3. 在"个人中心"获取你的Token
4. 编辑 `config.py`，将 `YOUR_PUSHPLUS_TOKEN` 替换为你的Token

```python
PUSHPLUS_TOKEN = "你的PushPlus Token"
```

### 3. 测试运行

```bash
# 测试早盘播报
python stock_monitor.py morning

# 测试收盘播报
python stock_monitor.py afternoon
```

## 定时任务配置

### macOS/Linux (使用crontab)

```bash
# 编辑crontab
crontab -e

# 添加以下内容（注意修改脚本路径）
30 9 * * 1-5 cd /path/to/stock-monitor && python stock_monitor.py morning
0 10 * * 1-5 cd /path/to/stock-monitor && python stock_monitor.py morning
30 14 * * 1-5 cd /path/to/stock-monitor && python stock_monitor.py afternoon
```

### Windows (使用任务计划程序)

1. 打开"任务计划程序"
2. 创建基本任务
3. 设置触发器为每天 09:30、10:00、14:30
4. 操作选择"启动程序"
5. 程序填写 `python`
6. 参数填写 `stock_monitor.py morning` 或 `afternoon`
7. 起始于填写脚本所在目录

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

【板块强度】
半导体: ↑+2.50%
新能源: ↑+1.80%
人工智能: ↑+1.50%
医药生物: ↓-0.50%

涨停数量: 45家
```

## 注意事项

1. 本脚本使用Yahoo Finance和新浪财经API，可能需要科学上网或API变更
2. 成交量分析需要历史数据对比，当前为简化版本
3. PushPlus免费版每天可推送200条消息，足够使用
4. 定时任务仅在工作日运行（周一至周五）

## 故障排查

### 推送失败

1. 检查PushPlus Token是否正确
2. 确认网络连接正常
3. 查看PushPlus官网是否正常服务

### 数据获取失败

1. 检查网络连接
2. 确认Yahoo Finance API可访问
3. 检查新浪财经API是否变更

## 扩展功能

如需更详细的数据分析，可以考虑：

1. 接入tushare获取A股历史数据
2. 添加成交量对比分析
3. 增加更多技术指标
4. 添加自选股监控
