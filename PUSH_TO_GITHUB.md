# 🚀 推送到GitHub并配置Actions

## 第1步：推送代码到GitHub

在终端运行：

```bash
cd /Users/yu/Documents/Codex/2026-08-19/hi/stock-monitor

git remote add origin https://github.com/yu12333/stock-monitor.git
git branch -M main
git push -u origin main
```

如果提示输入用户名密码：
- 用户名：`yu12333`
- 密码：使用GitHub Personal Access Token（不是登录密码）

### 如何获取GitHub Token？

1. 访问：https://github.com/settings/tokens
2. 点击 "Generate new token (classic)"
3. 勾选 `repo` 权限
4. 生成并复制token

---

## 第2步：配置PushPlus Token

1. 打开你的GitHub仓库：https://github.com/yu12333/stock-monitor

2. 点击 "Settings" → "Secrets and variables" → "Actions"

3. 点击 "New repository secret"

4. 填写：
   - Name: `PUSHPLUS_TOKEN`
   - Secret: `c8747e8205a4467baf6970a1333da336`

5. 点击 "Add secret"

---

## 第3步：测试运行

1. 在仓库页面点击 "Actions" 标签

2. 点击左侧 "股票监控推送"

3. 点击 "Run workflow" → "Run workflow"

4. 等待运行完成，检查微信是否收到消息

---

## ✅ 完成！

配置成功后，每天会自动推送：

| 时间 | 内容 |
|------|------|
| 09:30 | 早盘播报 |
| 10:00 | 早盘播报 |
| 14:30 | A股收盘分析 |

（仅工作日：周一至周五）

---

## 📊 你会收到的消息

```
📊 早盘市场播报 - 2026-08-28 09:30

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

---

## 🔧 故障排查

### 推送失败

1. 检查Secrets配置是否正确
2. 查看Actions运行日志
3. 确认PushPlus Token有效

### 定时任务不触发

1. 检查仓库是否为公开仓库（Private仓库的Actions有限制）
2. 确认workflow文件正确
3. 手动触发测试

---

## 📞 需要帮助？

如果遇到问题，请告诉我：
1. 推送代码时的错误信息
2. Actions运行日志截图
3. Secrets配置截图
