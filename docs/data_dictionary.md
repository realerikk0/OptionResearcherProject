# 数据字典

## 1. SPY Underlying Data (`spy_underlying.csv`)

| 字段名 | 类型 | 说明 | 示例 |
|--------|------|------|------|
| date | datetime | 交易日期 | 2025-01-06 |
| open | float | 开盘价 | 458.32 |
| high | float | 最高价 | 463.61 |
| low | float | 最低价 | 455.84 |
| close | float | 收盘价 | 461.27 |
| volume | int | 成交量 | 5,820,000 |

- **数据来源**：脚本生成的合成行情（20 个连续交易日）
- **更新频率**：日线（运行脚本时一次性生成）

## 2. SPY Option Chain (`spy_option_chain.csv`)

| 字段名 | 类型 | 说明 | 取值范围/示例 |
|--------|------|------|---------------|
| date | datetime | 数据日期 | 2025-01-06 |
| underlying_price | float | 标的当前价格 | 461.27 |
| option_type | string | 期权类型 | `call` / `put` |
| strike | float | 行权价 | 460.00 |
| expiration | date | 到期日 | 2025-02-14 |
| bid | float | 买价 | 16.57 |
| ask | float | 卖价 | 21.57 |
| last | float | 最新成交价 | 19.02 |
| volume | int | 当日成交量 | 1,820 |
| open_interest | int | 未平仓合约数 | 3,540 |
| implied_volatility | float | 隐含波动率 | 0.2380 |
| contract_symbol | string | 期权合约代码 | SPY250214C00460000 |

- **合约代号格式**：`SPY` + `YYMMDD` + `C/P` + `价格（8位）`
- **数据质量**：每个交易日含 3 个到期日 × 5 个行权价 × call/put，脚本嵌入 Put-Call Parity、隐含波动率曲线与 Greeks 异常，适合验证异常检测逻辑

## 3. Treasury Rates (`treasury_rates.csv`)

| 字段名 | 类型 | 说明 | 示例 |
|--------|------|------|------|
| date | datetime | 日期 | 2025-01-06 |
| rate_10y | float | 10 年期国债收益率 | 0.04510 |

- **用途**：无风险利率，用于定价、Greeks 计算与绩效评估
- **注意事项**：收益率已换算为小数，可在定价时直接使用；如需其他期限，可在此基础上构造利率曲线
