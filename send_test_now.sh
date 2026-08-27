#!/bin/bash
# 立即发送测试消息

echo "发送测试消息到微信..."
echo ""

python3 << 'PYTHON_EOF'
import requests
import json
from datetime import datetime

token = "c8747e8205a4467baf6970a1333da336"
url = "http://www.pushplus.plus/send"

now = datetime.now().strftime('%Y-%m-%d %H:%M:%S')

content = f"""📊 股票监控测试消息

发送时间: {now}

✅ PushPlus配置成功！

明天开始将在工作日的以下时间推送：
• 09:30 - 早盘播报
• 10:00 - 早盘播报  
• 14:30 - A股收盘分析

监控内容：
【外盘市场】
• 美股：道琼斯、标普500、纳斯达克
• 韩国：KOSPI指数
• 日本：日经225指数

【A股市场】
• 上证指数、深证成指、创业板指、科创50
• 板块强度分析
• 涨停数量统计
• 成交量分析（放量/缩量）

如果你收到这条消息，说明配置成功！🎉"""

data = {
    "token": token,
    "title": "📊 股票监控测试",
    "content": content,
    "template": "txt"
}

try:
    response = requests.post(url, json=data, timeout=10)
    result = response.json()
    
    if result.get('code') == 200:
        print("✅ 测试消息发送成功！请检查微信。")
    else:
        print(f"❌ 发送失败: {result}")
except Exception as e:
    print(f"❌ 请求异常: {e}")
PYTHON_EOF

echo ""
