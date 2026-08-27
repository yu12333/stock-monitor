#!/usr/bin/env node
/**
 * 股票市场监控脚本 (Node.js版本)
 * 收集美股、韩国、日本、A股数据并推送到微信
 */

const https = require('https');
const http = require('http');

// PushPlus配置
const PUSHPLUS_TOKEN = "YOUR_PUSHPLUS_TOKEN"; // 用户需要替换

// 市场数据获取函数
function fetchYahooData(symbol) {
    return new Promise((resolve, reject) => {
        const url = `https://query1.finance.yahoo.com/v8/finance/chart/${symbol}?interval=1d&range=1d`;
        const options = {
            headers: {
                'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36'
            }
        };

        https.get(url, options, (res) => {
            let data = '';
            res.on('data', (chunk) => data += chunk);
            res.on('end', () => {
                try {
                    const json = JSON.parse(data);
                    if (json.chart && json.chart.result) {
                        const result = json.chart.result[0];
                        const meta = result.meta;
                        const currentPrice = meta.regularMarketPrice;
                        const previousClose = meta.chartPreviousClose;
                        const change = currentPrice - previousClose;
                        const changePercent = (change / previousClose) * 100;
                        resolve({
                            price: currentPrice,
                            change: change,
                            changePercent: changePercent
                        });
                    } else {
                        reject(new Error('Invalid data format'));
                    }
                } catch (e) {
                    reject(e);
                }
            });
        }).on('error', reject);
    });
}

function fetchSinaData(code) {
    return new Promise((resolve, reject) => {
        const url = `https://hq.sinajs.cn/list=${code}`;
        const options = {
            headers: {
                'User-Agent': 'Mozilla/5.0',
                'Referer': 'https://finance.sina.com.cn'
            }
        };

        https.get(url, options, (res) => {
            let data = '';
            res.on('data', (chunk) => data += chunk);
            res.on('end', () => {
                try {
                    // 解析新浪行情数据
                    const match = data.match(/"([^"]+)"/);
                    if (match) {
                        const fields = match[1].split(',');
                        if (fields.length >= 9) {
                            const currentPrice = parseFloat(fields[3]);
                            const previousClose = parseFloat(fields[2]);
                            const change = currentPrice - previousClose;
                            const changePercent = (change / previousClose) * 100;
                            const volume = parseFloat(fields[8]) / 100000000; // 转换为亿
                            resolve({
                                price: currentPrice,
                                change: change,
                                changePercent: changePercent,
                                volume: volume
                            });
                        } else {
                            reject(new Error('Invalid data fields'));
                        }
                    } else {
                        reject(new Error('No data found'));
                    }
                } catch (e) {
                    reject(e);
                }
            });
        }).on('error', reject);
    });
}

// 主函数
async function main(analysisType = 'morning') {
    console.log(`开始收集市场数据... (${analysisType})`);
    
    try {
        // 美股数据
        const usSymbols = {
            '^DJI': '道琼斯',
            '^GSPC': '标普500',
            '^IXIC': '纳斯达克'
        };
        
        const usData = [];
        for (const [symbol, name] of Object.entries(usSymbols)) {
            try {
                const data = await fetchYahooData(symbol);
                usData.push({ name, ...data });
                console.log(`✓ ${name}: ${data.price.toFixed(2)} (${data.changePercent >= 0 ? '+' : ''}${data.changePercent.toFixed(2)}%)`);
            } catch (e) {
                console.error(`✗ ${name}: ${e.message}`);
                usData.push({ name, price: 0, change: 0, changePercent: 0 });
            }
        }
        
        // 韩国和日本数据
        const kjSymbols = {
            '^KS11': '韩国KOSPI',
            '^N225': '日经225'
        };
        
        const kjData = [];
        for (const [symbol, name] of Object.entries(kjSymbols)) {
            try {
                const data = await fetchYahooData(symbol);
                kjData.push({ name, ...data });
                console.log(`✓ ${name}: ${data.price.toFixed(2)} (${data.changePercent >= 0 ? '+' : ''}${data.changePercent.toFixed(2)}%)`);
            } catch (e) {
                console.error(`✗ ${name}: ${e.message}`);
                kjData.push({ name, price: 0, change: 0, changePercent: 0 });
            }
        }
        
        // A股数据
        const aStockCodes = {
            'sh000001': '上证指数',
            'sz399001': '深证成指',
            'sz399006': '创业板指',
            'sh000688': '科创50'
        };
        
        const aData = [];
        for (const [code, name] of Object.entries(aStockCodes)) {
            try {
                const data = await fetchSinaData(code);
                aData.push({ name, ...data });
                const volumeStr = data.volume ? ` 成交量:${data.volume.toFixed(0)}亿` : '';
                console.log(`✓ ${name}: ${data.price.toFixed(2)} (${data.changePercent >= 0 ? '+' : ''}${data.changePercent.toFixed(2)}%)${volumeStr}`);
            } catch (e) {
                console.error(`✗ ${name}: ${e.message}`);
                aData.push({ name, price: 0, change: 0, changePercent: 0, volume: 0 });
            }
        }
        
        // 生成消息
        const now = new Date();
        const timeStr = now.toLocaleString('zh-CN', { timeZone: 'Asia/Shanghai' });
        const title = analysisType === 'morning' ? 
            `📊 早盘市场播报 - ${timeStr}` : 
            `📊 A股收盘分析 - ${timeStr}`;
        
        let message = `${title}\n\n`;
        
        // 外盘数据
        message += "【外盘市场】\n";
        for (const stock of usData) {
            const arrow = stock.changePercent >= 0 ? "↑" : "↓";
            message += `${stock.name}: ${stock.price.toFixed(2)} ${arrow}${stock.changePercent >= 0 ? '+' : ''}${stock.changePercent.toFixed(2)}%\n`;
        }
        
        for (const stock of kjData) {
            const arrow = stock.changePercent >= 0 ? "↑" : "↓";
            message += `${stock.name}: ${stock.price.toFixed(2)} ${arrow}${stock.changePercent >= 0 ? '+' : ''}${stock.changePercent.toFixed(2)}%\n`;
        }
        
        message += "\n";
        
        // A股数据
        message += "【A股市场】\n";
        for (const stock of aData) {
            const arrow = stock.changePercent >= 0 ? "↑" : "↓";
            const volumeStr = stock.volume ? `成交量:${stock.volume.toFixed(0)}亿` : "";
            message += `${stock.name}: ${stock.price.toFixed(2)} ${arrow}${stock.changePercent >= 0 ? '+' : ''}${stock.changePercent.toFixed(2)}% ${volumeStr}\n`;
        }
        
        console.log("\n" + "=".repeat(50));
        console.log(message);
        console.log("=".repeat(50));
        
        // 推送到微信（如果配置了Token）
        if (PUSHPLUS_TOKEN !== "YOUR_PUSHPLUS_TOKEN") {
            await sendToWechat(message, title);
        } else {
            console.log("\n⚠️  PushPlus Token未配置，跳过微信推送");
            console.log("请编辑 config.js 填入你的PushPlus Token");
        }
        
    } catch (error) {
        console.error("数据收集失败:", error);
    }
}

// PushPlus推送函数
function sendToWechat(message, title) {
    return new Promise((resolve, reject) => {
        const postData = JSON.stringify({
            token: PUSHPLUS_TOKEN,
            title: title,
            content: message,
            template: "txt"
        });
        
        const options = {
            hostname: 'www.pushplus.plus',
            port: 80,
            path: '/send',
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'Content-Length': Buffer.byteLength(postData)
            }
        };
        
        const req = http.request(options, (res) => {
            let data = '';
            res.on('data', (chunk) => data += chunk);
            res.on('end', () => {
                try {
                    const result = JSON.parse(data);
                    if (result.code === 200) {
                        console.log("✅ 推送成功");
                        resolve(result);
                    } else {
                        console.error("❌ 推送失败:", result);
                        reject(new Error(result.msg));
                    }
                } catch (e) {
                    reject(e);
                }
            });
        });
        
        req.on('error', (e) => {
            console.error("❌ 推送异常:", e);
            reject(e);
        });
        
        req.write(postData);
        req.end();
    });
}

// 命令行参数处理
const analysisType = process.argv[2] || 'morning';
main(analysisType);
