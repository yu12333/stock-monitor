# 股票监控系统 - 安装指南

## 系统要求

### 必需条件
- 网络连接（访问Yahoo Finance和新浪财经API）
- PushPlus账号（免费注册）
- 定时任务支持（cron或任务计划程序）

### 可选环境
- **Python 3.6+**（推荐）
- **Node.js 14+**
- **Bash**（基础功能）

## 安装步骤

### 方案一：Python版本（推荐）

1. **安装Python依赖**
   ```bash
   pip install requests pytz
   ```

2. **配置PushPlus**
   - 访问 http://www.pushplus.plus/
   - 微信扫码注册登录
   - 在"个人中心"复制Token
   - 编辑 `config.py`，替换 `YOUR_PUSHPLUS_TOKEN`

3. **测试运行**
   ```bash
   python stock_monitor.py morning
   ```

4. **设置定时任务**
   ```bash
   # 编辑crontab
   crontab -e
   
   # 添加以下内容
   30 9 * * 1-5 cd /path/to/stock-monitor && python stock_monitor.py morning
   0 10 * * 1-5 cd /path/to/stock-monitor && python stock_monitor.py morning
   30 14 * * 1-5 cd /path/to/stock-monitor && python stock_monitor.py afternoon
   ```

### 方案二：Node.js版本

1. **安装Node.js**
   - 访问 https://nodejs.org/ 下载安装

2. **配置PushPlus**
   - 编辑 `config.js`，替换 `YOUR_PUSHPLUS_TOKEN`

3. **测试运行**
   ```bash
   node stock_monitor.js morning
   ```

4. **设置定时任务**
   ```bash
   crontab -e
   
   # 添加以下内容
   30 9 * * 1-5 cd /path/to/stock-monitor && node stock_monitor.js morning
   0 10 * * 1-5 cd /path/to/stock-monitor && node stock_monitor.js morning
   30 14 * * 1-5 cd /path/to/stock-monitor && node stock_monitor.js afternoon
   ```

### 方案三：Bash版本（基础功能）

1. **设置执行权限**
   ```bash
   chmod +x stock_monitor.sh
   ```

2. **测试运行**
   ```bash
   ./stock_monitor.sh
   ```

3. **设置定时任务**
   ```bash
   crontab -e
   
   # 添加以下内容
   30 9 * * 1-5 /path/to/stock-monitor/stock_monitor.sh
   0 10 * * 1-5 /path/to/stock-monitor/stock_monitor.sh
   30 14 * * 1-5 /path/to/stock-monitor/stock_monitor.sh
   ```

## Windows用户

### 使用任务计划程序

1. 打开"任务计划程序"
2. 创建基本任务
3. 设置三个触发器：
   - 每天 09:30
   - 每天 10:00
   - 每天 14:30
4. 操作选择"启动程序"
5. 程序填写：
   - Python: `python`
   - Node.js: `node`
6. 参数填写：
   - 早盘: `stock_monitor.py morning` 或 `stock_monitor.js morning`
   - 收盘: `stock_monitor.py afternoon` 或 `stock_monitor.js afternoon`
7. 起始于填写脚本所在目录

## 网络问题排查

### 无法访问Yahoo Finance

1. **检查网络连接**
   ```bash
   ping query1.finance.yahoo.com
   ```

2. **使用代理**（如果需要）
   ```bash
   export http_proxy=http://proxy:port
   export https_proxy=http://proxy:port
   ```

3. **备选方案**
   - 使用其他数据源（如Google Finance、Bloomberg等）
   - 使用国内财经网站API

### 无法访问新浪财经

1. **检查网络连接**
   ```bash
   ping hq.sinajs.cn
   ```

2. **检查Referer头**
   - 新浪API需要正确的Referer头
   - 脚本已配置，请勿修改

## 验证安装

### Python版本
```bash
python test.py
```

### Node.js版本
```bash
node test.js
```

### Bash版本
```bash
./test_api.sh
```

## 常见问题

### Q: 推送失败，显示"请先配置PushPlus Token"
A: 编辑配置文件，填入你的PushPlus Token

### Q: 数据获取失败
A: 
1. 检查网络连接
2. 确认API可访问
3. 查看错误信息

### Q: 定时任务不执行
A:
1. 检查cron服务状态
2. 确认脚本路径正确
3. 查看cron日志

### Q: 如何修改推送时间
A: 编辑crontab或任务计划程序中的时间设置

## 获取帮助

如遇问题，请提供：
1. 操作系统版本
2. Python/Node.js版本
3. 错误信息截图
4. 网络连接状态

## 下一步

安装成功后，你可以：
1. 修改推送时间
2. 添加更多股票代码
3. 自定义消息格式
4. 添加技术指标分析
5. 集成更多数据源
