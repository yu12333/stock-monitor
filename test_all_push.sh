#!/bin/bash
# 测试所有推送方式

echo "股票监控系统 - 推送测试"
echo "================================"
echo ""

# PushPlus测试
echo "1. 测试PushPlus..."
echo "Token: c8747e82..."
echo ""

python3 << 'PYTHON_EOF'
import requests
import json

token = "c8747e8205a4467baf6970a1333da336"
url = "http://www.pushplus.plus/send"

data = {
    "token": token,
    "title": "股票监控测试",
    "content": "这是一条测试消息\n\n如果你收到这条消息，说明PushPlus配置成功！",
    "template": "txt"
}

try:
    response = requests.post(url, json=data, timeout=10)
    result = response.json()
    
    if result.get('code') == 200:
        print("✅ PushPlus推送成功！")
    else:
        print(f"❌ PushPlus推送失败: {result}")
except Exception as e:
    print(f"❌ PushPlus请求异常: {e}")
PYTHON_EOF

echo ""
echo "================================"
echo ""
echo "测试完成！"
echo ""
echo "如果推送失败，可能原因:"
echo "1. 网络连接问题（需要能够访问pushplus.plus）"
echo "2. Token配置错误"
echo "3. PushPlus服务异常"
echo ""
echo "备选方案:"
echo "1. 使用企业微信机器人"
echo "2. 使用Server酱（ServerChan）"
echo "3. 使用钉钉机器人"
echo ""
echo "如需修改推送方式，请编辑 stock_monitor.py"
echo ""
