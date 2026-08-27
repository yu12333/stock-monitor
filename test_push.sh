#!/bin/bash
# 测试PushPlus推送功能

TOKEN="c8747e8205a4467baf6970a1333da336"
TITLE="股票监控测试"
CONTENT="这是一条测试消息，用于验证PushPlus推送功能是否正常工作。\n\n发送时间: $(date '+%Y-%m-%d %H:%M:%S')\n\n如果你收到这条消息，说明配置成功！"

echo "测试PushPlus推送..."
echo "Token: ${TOKEN:0:8}..."
echo ""

# 使用curl发送测试消息
response=$(curl -s -X POST "http://www.pushplus.plus/send" \
  -H "Content-Type: application/json" \
  -d "{
    \"token\": \"$TOKEN\",
    \"title\": \"$TITLE\",
    \"content\": \"$CONTENT\",
    \"template\": \"txt\"
  }" 2>&1)

if [ $? -eq 0 ]; then
    echo "✓ 请求已发送"
    echo "响应: $response"
    
    # 检查响应
    if echo "$response" | grep -q '"code":200'; then
        echo ""
        echo "✓✓✓ 推送成功！请检查微信消息。"
    else
        echo ""
        echo "✗ 推送可能失败，请检查Token和网络连接。"
    fi
else
    echo "✗ 请求发送失败"
    echo "错误: $response"
    echo ""
    echo "可能原因:"
    echo "1. 网络连接问题"
    echo "2. 无法访问 pushplus.plus"
    echo "3. 需要配置代理"
fi

echo ""
echo "================================"
echo "如需手动测试，可以访问:"
echo "http://www.pushplus.plus/send"
echo "使用Token: $TOKEN"
echo ""
