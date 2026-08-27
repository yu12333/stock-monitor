# 🚀 在你的电脑上运行测试

## 为什么需要在本地运行？

Codex环境有网络限制，无法直接访问外部API。你需要在自己的电脑上运行测试。

## 📋 快速步骤

### 第1步：下载项目

项目位置：
```
/Users/yu/Documents/Codex/2026-08-19/hi/stock-monitor/
```

### 第2步：打开终端

1. 打开"终端"应用（macOS）或"命令提示符"（Windows）
2. 进入项目目录：
   ```bash
   cd /Users/yu/Documents/Codex/2026-08-19/hi/stock-monitor
   ```

### 第3步：安装依赖

```bash
pip3 install requests pytz
```

如果提示pip3不存在，尝试：
```bash
pip install requests pytz
```

### 第4步：测试推送

```bash
# 运行测试脚本
./test_local.sh
```

或者直接运行Python测试：
```bash
python3 -c "
import requests
import json
from datetime import datetime

token = 'c8747e8205a4467baf6970a1333da336'
url = 'http://www.pushplus.plus/send'

data = {
    'token': token,
    'title': '股票监控测试',
    'content': f'测试消息\\n\\n时间: {datetime.now().strftime(\"%Y-%m-%d %H:%M:%S\")}',
    'template': 'txt'
}

try:
    response = requests.post(url, json=data, timeout=10)
    result = response.json()
    print(f'响应: {result}')
    
    if result.get('code') == 200:
        print('✅ 推送成功！请检查微信。')
    else:
        print('❌ 推送失败，请检查Token。')
except Exception as e:
    print(f'❌ 错误: {e}')
"
```

### 第5步：设置定时任务

如果推送成功，设置定时任务：

```bash
# 运行设置脚本
./setup_cron.sh
```

## 🔧 故障排查

### 问题1：Python未安装

**macOS:**
```bash
# 检查Python
python3 --version

# 如果未安装，使用Homebrew
brew install python3
```

**Windows:**
访问 https://www.python.org/downloads/ 下载安装

### 问题2：依赖安装失败

**使用国内镜像：**
```bash
pip3 install requests pytz -i https://pypi.tuna.tsinghua.edu.cn/simple
```

### 问题3：推送失败

**检查网络：**
```bash
ping pushplus.plus
```

**检查Token：**
确保Token正确：`c8747e8205a4467baf6970a1333da336`

**手动测试：**
访问 http://www.pushplus.plus/send 手动发送测试

### 问题4：定时任务不执行

**查看日志：**
```bash
tail -f /tmp/stock_monitor.log
```

**查看定时任务：**
```bash
crontab -l
```

**手动运行：**
```bash
python3 stock_monitor.py morning
```

## 📊 测试成功后

你会在微信收到类似这样的消息：

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

## ⏰ 推送时间

- **09:30** - 早盘播报
- **10:00** - 早盘播报
- **14:30** - A股收盘分析

（仅工作日：周一至周五）

## 📞 需要帮助？

如果遇到问题，请提供：
1. 操作系统版本
2. Python版本（`python3 --version`）
3. 错误信息截图
4. 运行 `crontab -l` 的输出

## 🎯 下一步

1. ✅ 测试推送成功
2. ✅ 设置定时任务
3. ✅ 明天早上9:30查看微信消息！

---

**项目位置**: `/Users/yu/Documents/Codex/2026-08-19/hi/stock-monitor/`
**Token**: `c8747e8205a4467baf6970a1333da336`
**状态**: ✅ 配置完成，待本地测试
