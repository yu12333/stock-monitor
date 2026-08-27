#!/usr/bin/env node
/**
 * 测试脚本 - 验证股票监控功能
 */

const { fetchYahooData, fetchSinaData } = require('./stock_monitor');

async function testDataFetch() {
    console.log("测试数据获取功能...");
    
    // 测试Yahoo Finance API
    console.log("\n1. 测试Yahoo Finance API...");
    const usSymbols = ['^DJI', '^GSPC', '^IXIC'];
    for (const symbol of usSymbols) {
        try {
            const data = await fetchYahooData(symbol);
            console.log(`✓ ${symbol}: ${data.price.toFixed(2)} (${data.changePercent >= 0 ? '+' : ''}${data.changePercent.toFixed(2)}%)`);
        } catch (e) {
            console.error(`✗ ${symbol}: ${e.message}`);
        }
    }
    
    // 测试新浪财经API
    console.log("\n2. 测试新浪财经API...");
    const aStockCodes = ['sh000001', 'sz399001', 'sz399006'];
    for (const code of aStockCodes) {
        try {
            const data = await fetchSinaData(code);
            console.log(`✓ ${code}: ${data.price.toFixed(2)} (${data.changePercent >= 0 ? '+' : ''}${data.changePercent.toFixed(2)}%)`);
        } catch (e) {
            console.error(`✗ ${code}: ${e.message}`);
        }
    }
}

// 主测试函数
async function main() {
    console.log("股票监控系统测试 (Node.js版本)");
    console.log("=".repeat(50));
    
    await testDataFetch();
    
    console.log("\n" + "=".repeat(50));
    console.log("测试完成!");
    console.log("\n下一步:");
    console.log("1. 编辑 config.js 填入你的PushPlus Token");
    console.log("2. 运行 node stock_monitor.js morning 测试推送");
    console.log("3. 设置定时任务（参考 README.md）");
}

main().catch(console.error);
