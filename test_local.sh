#!/bin/bash
# 本地测试脚本 - 在用户环境中运行

echo "股票监控系统 - 本地测试"
echo "================================"
echo ""

# 检查Python
if ! command -v python3 &> /dev/null; then
    echo "❌ Python3 未安装"
    echo "请先安装Python3: https://www.python.org/downloads/"
    exit 1
fi

echo "✓ Python3 已安装"

# 检查依赖
echo ""
echo "检查Python依赖..."
python3 -c "import requests; import pytz" 2>/dev/null
if [ $? -ne 0 ]; then
    echo "⚠️  依赖未安装，正在安装..."
    pip3 install requests pytz
else
    echo "✓ 依赖已安装"
fi

# 测试PushPlus
echo ""
echo "测试PushPlus推送..."
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
    "content": "这是一条测试消息\n\n发送时间: " + __import__('datetime').datetime.now().strftime('%Y-%m-%d %H:%M:%S') + "\n\n如果你收到这条消息，说明PushPlus配置成功！",
    "template": "txt"
}

try:
    response = requests.post(url, json=data, timeout=10)
    result = response.json()
    
    if result.get('code') == 200:
        print("✅ 推送成功！请检查微信消息。")
        print(f"响应: {result}")
    else:
        print(f"❌ 推送失败: {result}")
except Exception as e:
    print(f"❌ 请求异常: {e}")
PYTHON_EOF

echo ""
echo "================================"
echo ""
echo "如果推送失败，请检查:"
echo "1. 网络连接是否正常"
echo "2. Token是否正确"
echo "3. 访问 http://www.pushplus.plus/ 检查服务状态"
echo ""
echo "如果推送成功，继续运行:"
echo "./setup_cron.sh"
echo ""
