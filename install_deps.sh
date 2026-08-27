#!/bin/bash
echo "安装Python依赖..."
echo ""

pip3 install requests pytz

if [ $? -eq 0 ]; then
    echo ""
    echo "✅ 依赖安装成功！"
    echo ""
    echo "现在可以运行测试："
    echo "./send_test_now.sh"
else
    echo ""
    echo "❌ 安装失败，尝试使用国内镜像："
    echo ""
    pip3 install requests pytz -i https://pypi.tuna.tsinghua.edu.cn/simple
fi
