# 股票监控系统 - 最终设置指南

## ✅ 已完成配置

- ✅ PushPlus Token 已配置: `c8747e8205a4467baf6970a1333da336`
- ✅ 配置文件已更新
- ✅ 定时任务设置脚本已创建
- ✅ 推送测试脚本已创建

## 🚀 最后三步

### 第1步：安装Python依赖

打开终端，运行以下命令：

```bash
cd /Users/yu/Documents/Codex/2026-08-19/hi/stock-monitor
pip3 install requests pytz
```

### 第2步：测试推送功能

运行测试脚本，验证PushPlus是否正常工作：

```bash
./test_push.sh
```

如果成功，你会在微信收到一条测试消息。

### 第3步：设置定时任务

运行设置脚本，自动配置定时任务：

```bash
./setup_cron.sh
```

脚本会自动添加以下定时任务：
- 每天 09:30 - 早盘播报
- 每天 10:00 - 早盘播报  
- 每天 14:30 - A股收盘分析

## 📊 手动测试

如果想手动运行一次查看效果：

```bash
# 早盘播报测试
python3 stock_monitor.py morning

# 收盘分析测试
python3 stock_monitor.py afternoon
```

## 🔧 故障排查

### 问题1：Python依赖安装失败

```bash
# 使用国内镜像
pip3 install requests pytz -i https://pypi.tuna.tsinghua.edu.cn/simple
```

### 问题2：推送测试失败

1. 检查网络连接
2. 确认Token正确
3. 访问 http://www.pushplus.plus/ 检查服务状态

### 问题3：定时任务不执行

```bash
# 查看定时任务
crontab -l

# 查看日志
tail -f /tmp/stock_monitor.log

# 手动运行测试
python3 stock_monitor.py morning
```

## 📱 消息示例

配置成功后，你将收到类似这样的消息：

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

## 📋 常用命令

```bash
# 查看定时任务
crontab -l

# 编辑定时任务
crontab -e

# 查看运行日志
tail -f /tmp/stock_monitor.log

# 手动运行早盘播报
python3 stock_monitor.py morning

# 手动运行收盘分析
python3 stock_monitor.py afternoon

# 停止定时任务（删除相关条目）
crontab -l | grep -v '股票监控' | crontab -
```

## 🎯 下一步

1. **立即测试**: 运行 `./test_push.sh` 验证推送
2. **设置定时**: 运行 `./setup_cron.sh` 配置定时任务
3. **监控运行**: 查看日志确认正常工作
4. **调整时间**: 如需修改时间，编辑 `crontab -e`

## 💡 提示

- 定时任务仅在工作日运行（周一至周五）
- 日志文件位置: `/tmp/stock_monitor.log`
- 如需修改推送时间，编辑crontab
- PushPlus免费版每天200条消息，足够使用

## 📞 需要帮助？

如果遇到问题，请提供：
1. 错误信息截图
2. 运行 `crontab -l` 的输出
3. 运行 `tail -20 /tmp/stock_monitor.log` 的输出

---

**配置完成时间**: $(date '+%Y-%m-%d %H:%M:%S')
**Token状态**: ✅ 已配置
**定时任务**: ⏳ 待设置
