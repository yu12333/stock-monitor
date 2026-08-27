#!/bin/bash
# 设置工作日定时任务

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

echo "股票监控系统 - 工作日定时任务设置"
echo "========================================"
echo ""
echo "当前脚本目录: $SCRIPT_DIR"
echo ""

# 检查Python
if command -v python3 &> /dev/null; then
    PYTHON_CMD="python3"
elif command -v python &> /dev/null; then
    PYTHON_CMD="python"
else
    echo "❌ Python 未找到，请先安装Python"
    exit 1
fi

echo "✓ Python: $PYTHON_CMD"

# 检查依赖
echo ""
echo "检查Python依赖..."
$PYTHON_CMD -c "import requests; import pytz" 2>/dev/null
if [ $? -ne 0 ]; then
    echo "⚠️  依赖未安装，正在安装..."
    $PYTHON_CMD -m pip install requests pytz
else
    echo "✓ 依赖已安装"
fi

# 创建crontab条目（仅工作日）
echo ""
echo "准备添加定时任务（仅工作日：周一至周五）..."
echo ""

CRON_ENTRIES="
# 股票监控系统 - 早盘播报 09:30（工作日）
30 9 * * 1-5 cd $SCRIPT_DIR && $PYTHON_CMD stock_monitor.py morning >> /tmp/stock_monitor.log 2>&1

# 股票监控系统 - 早盘播报 10:00（工作日）
0 10 * * 1-5 cd $SCRIPT_DIR && $PYTHON_CMD stock_monitor.py morning >> /tmp/stock_monitor.log 2>&1

# 股票监控系统 - A股收盘分析 14:30（工作日）
30 14 * * 1-5 cd $SCRIPT_DIR && $PYTHON_CMD stock_monitor.py afternoon >> /tmp/stock_monitor.log 2>&1
"

echo "将添加以下定时任务（仅工作日）:"
echo "• 09:30 - 早盘播报"
echo "• 10:00 - 早盘播报"
echo "• 14:30 - A股收盘分析"
echo ""

read -p "是否添加这些定时任务? (y/n): " -n 1 -r
echo ""
if [[ $REPLY =~ ^[Yy]$ ]]; then
    # 备份现有crontab
    crontab -l > /tmp/crontab_backup_$(date +%Y%m%d%H%M%S) 2>/dev/null
    
    # 添加新任务
    (crontab -l 2>/dev/null; echo "$CRON_ENTRIES") | crontab -
    
    echo ""
    echo "✅ 定时任务已添加（仅工作日）"
    echo ""
    echo "当前定时任务列表:"
    crontab -l | grep -A1 "股票监控"
else
    echo ""
    echo "已取消添加定时任务"
fi

echo ""
echo "========================================"
echo ""
echo "查看日志: tail -f /tmp/stock_monitor.log"
echo "编辑定时任务: crontab -e"
echo "删除定时任务: crontab -l | grep -v '股票监控' | crontab -"
echo ""
