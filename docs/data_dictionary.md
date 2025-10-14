# 数据字典

## 1. SPY Underlying Data (`spy_underlying.csv`)

| 字段名 | 类型 | 说明 | 示例 |
|--------|------|------|------|
| date | datetime | 交易日期 | 2024-10-15 |
| open | float | 开盘价 | 425.30 |
| high | float | 最高价 | 427.80 |
| low | float | 最低价 | 424.50 |
| close | float | 收盘价 | 426.90 |
| volume | int | 成交量 | 75,000,000 |

- **数据来源**：Yahoo Finance via yfinance
- **更新频率**：日线，按交易日更新

## 2. SPY Option Chain (`spy_option_chain.csv`)

| 字段名 | 类型 | 说明 | 取值范围/示例 |
|--------|------|------|---------------|
| date | datetime | 数据获取日期 | 2024-10-15 |
| underlying_price | float | 标的当前价格 | 426.90 |
| option_type | string | 期权类型 | `call` / `put` |
| strike | float | 行权价 | 430.00 |
| expiration | date | 到期日 | 2024-11-15 |
| bid | float | 买价 | 2.50 |
| ask | float | 卖价 | 2.55 |
| last | float | 最新成交价 | 2.52 |
| volume | int | 当日成交量 | 1,250 |
| open_interest | int | 未平仓合约数 | 5,430 |
| implied_volatility | float | 隐含波动率 | 0.18 (18%) |
| contract_symbol | string | 期权合约代码 | SPY241115C00430000 |

- **合约代号格式**：`SPY` + `YYMMDD` + `C/P` + `价格（8位）`
- **数据质量**：已过滤 `bid = 0` 的合约，并保留每个到期日最接近 ATM 的约 20 个合约

## 3. Treasury Rates (`treasury_rates.csv`)

| 字段名 | 类型 | 说明 | 示例 |
|--------|------|------|------|
| date | datetime | 日期 | 2024-10-15 |
| rate_10y | float | 10 年期国债收益率 | 0.045 |

- **用途**：无风险利率，用于定价、Greeks 计算与绩效评估
- **注意事项**：收益率已换算为小数，可在定价时直接使用；必要时可替换为期限匹配的利率
