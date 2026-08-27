# 配置文件

# PushPlus配置
# 1. 访问 http://www.pushplus.plus/
# 2. 注册并登录
# 3. 获取token并填入下方
PUSHPLUS_TOKEN = "c8747e8205a4467baf6970a1333da336"

# 市场时间配置（北京时间）
MARKET_TIMES = {
    'morning_1': '09:30',  # 早盘第一次播报
    'morning_2': '10:00',  # 早盘第二次播报
    'afternoon': '14:30'   # A股收盘播报
}

# 股票代码配置
US_STOCKS = {
    '^DJI': '道琼斯',
    '^GSPC': '标普500',
    '^IXIC': '纳斯达克'
}

KOREA_JAPAN_STOCKS = {
    '^KS11': '韩国KOSPI',
    '^N225': '日经225'
}

A_STOCK_INDICES = {
    'sh000001': '上证指数',
    'sz399001': '深证成指',
    'sz399006': '创业板指',
    'sh000688': '科创50'
}
