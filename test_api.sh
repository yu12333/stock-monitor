#!/bin/bash
echo "测试API连接..."

echo "1. 测试Yahoo Finance API..."
curl -s "https://query1.finance.yahoo.com/v8/finance/chart/^DJI?interval=1d&range=1d" | head -100

echo -e "\n\n2. 测试新浪财经API..."
curl -s "https://hq.sinajs.cn/list=sh000001" | head -100

echo -e "\n\n3. 测试PushPlus API..."
curl -s "http://www.pushplus.plus/" | head -50

echo -e "\n\n测试完成!"
