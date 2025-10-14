# 美股期权Greeks套利策略开发项目

## 项目背景
您是一家量化交易机构的期权研究员，需要围绕SPY期权链开发基于Greeks异常识别的套利策略。本测试项目旨在评估候选人对数据处理、模型构建、策略设计与回测的综合能力。

## 为什么选择 SPY
- 日成交量超过 500 万张合约，流动性极佳
- 买卖价差极窄，便于捕捉细微定价偏差
- 拥有完整的周度与月度到期期权链
- 适合作为 Greeks 异常研究的基准标的

## 数据包概览
运行 `data/get_data.py` 后将在 `data/raw/` 目录生成：
- `spy_option_chain.csv`：近 20 个交易日的期权链，包含日期、标的价格、行权价、到期日、报价、成交量、持仓量、隐含波动率等字段
- `spy_underlying.csv`：SPY ETF 历史价格，字段涵盖开收盘价、最高最低价与成交量
- `treasury_rates.csv`：10 年期美国国债收益率序列，用作无风险利率

## 项目任务
### 必做任务（全部完成）
#### Task 1：Greeks 计算与异常识别
- 使用 Black-Scholes 模型为全部期权计算 Delta、Gamma、Vega、Theta，可调用 QuantLib、SciPy 或自研实现
- 识别 Put-Call Parity 偏离（>1%）、隐含波动率 Smile/Skew 与 Term Structure 异常、Greeks 数值异常（例如 ATM Delta 明显偏离 0.5）
- 以 IV Smile 曲线、Put-Call Parity 偏离散点图、Greeks 热力图等方式可视化异常
- **评分重点**：计算准确性 15 分、异常识别逻辑 15 分、代码效率 10 分、可视化质量 10 分

#### Task 2：套利策略设计
- 基于 Task 1 的发现设计 1-2 套策略（如 Put-Call Parity 套利、波动率套利、Vertical/Calendar Spread 等）
- 明确触发条件并构建 Delta 中性或其他对冲方案
- 计入交易成本：Bid-Ask Spread、佣金（$0.65/contract）、滑点（0.5 tick），并设定止损与 Greeks 敞口管理
- **评分重点**：策略可行性 20 分、风险控制 15 分、成本考量 10 分、创新性 5 分

#### Task 3：回测与评估
- 使用 vectorbt、backtrader 或自建框架在提供数据上回测策略
- 输出关键指标：总收益/年化收益、Sharpe Ratio、Max Drawdown、Win Rate、Profit Factor、Greeks 暴露时间序列、VaR
- 总结策略优劣、适用场景、主要风险，并与买入持有 SPY 对比
- **评分重点**：回测框架合理性 15 分、结果诚实 10 分、分析深度 15 分

### 选做任务（+10 分）
在以下主题中任选其一深入展开：
- 实盘实时监控系统架构设计
- 压力测试（如 2020 年 3 月、VIX 飙升、流动性枯竭）
- 多标的扩展（QQQ、IWM、AAPL 等）的差异化方案

## 交付物
### 代码部分
```text
project/
├── requirements.txt
├── data/
│   ├── get_data.py
│   └── raw/
├── src/
│   ├── greeks_calculator.py
│   ├── anomaly_detector.py
│   ├── strategy.py
│   ├── backtest.py
│   └── visualization.py
├── notebooks/
│   └── analysis.ipynb
├── tests/
└── README.md
```

### 报告部分（8-10 页 PDF）
1. **执行摘要**：主要发现、策略核心逻辑、收益与风险预期
2. **Greeks 异常分析**：异常类型、分布特征、核心可视化
3. **策略设计**：信号逻辑、数学推导、对冲与风控
4. **回测结果**：绩效指标、收益曲线、Greeks 暴露、代表性交易
5. **局限与改进**：当前不足、实盘化需求、后续迭代方向

## 评估标准
- **技术维度（60 分）**：Greeks 计算 15、异常识别 15、策略设计 15、代码质量 15
- **思维维度（30 分）**：问题分析 10、风险意识 10、创新性 10
- **沟通维度（10 分）**：报告清晰度 5、代码可读性 5

## 快速开始
1. 安装依赖
   ```bash
   pip install -r requirements.txt
   ```
2. 获取数据
   ```bash
   cd data
   python get_data.py
   ```
3. 开始分析
   - 数据输出位置：`data/raw/`
   - 核心文件：`spy_underlying.csv`、`spy_option_chain.csv`、`treasury_rates.csv`
   - 建议在 `notebooks/analysis.ipynb` 或 `src/` 模块中开展研究

### 推荐依赖（requirements.txt）
```text
yfinance>=0.2.32
pandas>=2.0.0
numpy>=1.24.0
scipy>=1.11.0
matplotlib>=3.7.0
seaborn>=0.12.0
plotly>=5.17.0
jupyter>=1.0.0
# 可选
quantlib-python>=1.31
vectorbt>=0.25.0
```

## 数据获取方法
### 方法一（推荐）：使用提供脚本
- 进入 `data/`，运行 `python get_data.py`
- 默认采集 2024 年内数据，过程约 3-5 分钟
- 自动生成 `data/raw/` 目录及三份 CSV 文件

### 方法二：自定义数据源
- 可接入 Interactive Brokers、TD Ameritrade 等 API
- 请保持字段命名与示例 schema 一致，确保下游脚本可复用

## 数据获取脚本
```python
"""
美股期权数据获取脚本
标的：SPY（S&P 500 ETF）
"""

import yfinance as yf
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import warnings
warnings.filterwarnings('ignore')

print("=" * 70)
print("美股期权数据获取脚本 - SPY")
print("=" * 70)

# ========== 配置参数 ==========
SYMBOL = "SPY"
START_DATE = "2024-01-01"
END_DATE = "2024-12-31"

# ========== 1. 获取SPY现货数据 ==========
print("\n[1/3] 获取SPY ETF历史价格...")

def get_underlying_data():
    """获取SPY历史价格"""
    spy = yf.Ticker(SYMBOL)
    df = spy.history(start=START_DATE, end=END_DATE)
    df = df.reset_index()
    df.columns = ['date', 'open', 'high', 'low', 'close', 'volume', 'dividends', 'stock_splits']
    df = df[['date', 'open', 'high', 'low', 'close', 'volume']]
    print(f"✓ 获取到 {len(df)} 个交易日的数据")
    print(f"  日期范围: {df['date'].min()} 到 {df['date'].max()}")
    print(f"  价格范围: ${df['close'].min():.2f} - ${df['close'].max():.2f}")
    return df

spy_data = get_underlying_data()
spy_data.to_csv('raw/spy_underlying.csv', index=False)
print("  已保存到: raw/spy_underlying.csv")

# ========== 2. 获取期权链数据 ==========
print("\n[2/3] 获取SPY期权链数据...")

def get_option_chain_data(dates_sample=20):
    """获取SPY期权链数据"""
    spy = yf.Ticker(SYMBOL)
    expirations = spy.options
    print(f"  找到 {len(expirations)} 个到期日")
    selected_expirations = expirations[:3]
    print(f"  将获取以下到期日的数据: {selected_expirations}")
    all_options = []
    for exp_date in selected_expirations:
        try:
            print(f"\n  处理到期日: {exp_date}")
            opt_chain = spy.option_chain(exp_date)
            calls = opt_chain.calls.copy(); calls['option_type'] = 'call'; calls['expiration'] = exp_date
            puts = opt_chain.puts.copy(); puts['option_type'] = 'put'; puts['expiration'] = exp_date
            options = pd.concat([calls, puts], ignore_index=True)
            columns = ['contractSymbol', 'strike', 'lastPrice', 'bid', 'ask', 'volume', 'openInterest', 'impliedVolatility', 'option_type', 'expiration']
            options = options[columns]
            options.columns = ['contract_symbol', 'strike', 'last', 'bid', 'ask', 'volume', 'open_interest', 'implied_volatility', 'option_type', 'expiration']
            options['date'] = datetime.now().strftime('%Y-%m-%d')
            options['underlying_price'] = spy_data['close'].iloc[-1]
            options = options[options['bid'] > 0]
            current_price = spy_data['close'].iloc[-1]
            options['distance_from_atm'] = abs(options['strike'] - current_price)
            calls_filtered = options[options['option_type'] == 'call'].nsmallest(10, 'distance_from_atm')
            puts_filtered = options[options['option_type'] == 'put'].nsmallest(10, 'distance_from_atm')
            options_filtered = pd.concat([calls_filtered, puts_filtered])
            all_options.append(options_filtered)
            print(f"    ✓ 获取 {len(options_filtered)} 个期权合约")
        except Exception as e:
            print(f"    ✗ 失败: {e}")
    if all_options:
        df = pd.concat(all_options, ignore_index=True)
        df = df[['date', 'underlying_price', 'option_type', 'strike', 'expiration', 'bid', 'ask', 'last', 'volume', 'open_interest', 'implied_volatility', 'contract_symbol']]
        print(f"\n✓ 总共获取 {len(df)} 条期权数据")
        return df
    return None

option_data = get_option_chain_data()
if option_data is not None:
    option_data.to_csv('raw/spy_option_chain.csv', index=False)
    print("  已保存到: raw/spy_option_chain.csv")

# ========== 3. 获取无风险利率 ==========
print("\n[3/3] 获取美国国债收益率（无风险利率）...")

def get_treasury_rates():
    """获取美国10年期国债收益率"""
    try:
        treasury = yf.Ticker("^TNX")
        df = treasury.history(start=START_DATE, end=END_DATE)
        df = df.reset_index()[['Date', 'Close']]
        df.columns = ['date', 'rate_10y']
        df['rate_10y'] = df['rate_10y'] / 100
        print(f"✓ 获取到 {len(df)} 个交易日的利率数据")
        print(f"  利率范围: {df['rate_10y'].min()*100:.2f}% - {df['rate_10y'].max()*100:.2f}%")
        return df
    except Exception as e:
        print(f"  ✗ 无法获取实时利率: {e}")
        print("  使用固定利率: 4.5%")
        dates = pd.date_range(start=START_DATE, end=END_DATE, freq='D')
        return pd.DataFrame({'date': dates, 'rate_10y': 0.045})

treasury_data = get_treasury_rates()
treasury_data.to_csv('raw/treasury_rates.csv', index=False)
print("  已保存到: raw/treasury_rates.csv")

# ========== 数据摘要 ==========
print("\n" + "=" * 70)
print("数据获取完成！")
print("=" * 70)
print("\n📊 数据摘要:")
print(f"  • SPY价格数据: {len(spy_data)} 行")
print(f"  • 期权链数据: {len(option_data) if option_data is not None else 0} 行")
print(f"  • 国债利率数据: {len(treasury_data)} 行")
print("\n📁 文件位置:")
print("  • raw/spy_underlying.csv")
print("  • raw/spy_option_chain.csv")
print("  • raw/treasury_rates.csv")
print("\n✅ 您现在可以开始分析了！")

# ========== 数据质量检查 ==========
print("\n" + "=" * 70)
print("数据质量检查")
print("=" * 70)
if option_data is not None:
    print("\n期权数据样例:")
    print(option_data.head(3))
    print("\n期权类型分布:")
    print(option_data['option_type'].value_counts())
    print("\n到期日分布:")
    print(option_data['expiration'].value_counts())
    print("\n隐含波动率统计:")
    print(f"  平均IV: {option_data['implied_volatility'].mean():.2%}")
    print(f"  IV范围: {option_data['implied_volatility'].min():.2%} - {option_data['implied_volatility'].max():.2%}")
print("\n" + "=" * 70)
```

## 项目目录建议
```text
spy_options_project/
├── README.md
├── requirements.txt
├── data/
│   ├── get_data.py
│   └── raw/
├── docs/
│   ├── data_dictionary.md
│   └── strategy_examples.md
└── sample_submission/
    ├── src/
    ├── notebooks/
    └── report.pdf
```

## 时间要求与技术栈
- 建议投入 10-15 小时，提交期限为收到项目后 7 天内
- 推荐使用 Python 3.8+ 与 pandas、numpy、scipy/QuantLib、matplotlib/plotly、vectorbt/backtrader 等库
- 代码需可运行，提交前附运行说明

## 注意事项
- 诚实最重要，我们关注思路而非完美结果
- 可以使用开源库，但务必注明
- 遇到问题可邮件沟通（不影响评分）
- 建议在美股盘外时间（EST 9:30-16:00 之外）获取数据以避免实时波动
- 数据获取可能耗时 3-5 分钟，支持代理与自动重试

## 技术支持
如遇问题，请联系 HR。

## 提示
- 若 yfinance 下载缓慢，可配置代理
- 若数据获取失败，脚本会启用重试机制
- 建议在提交前检查 `data/raw/` 文件是否完整

## 参考资源
- [CBOE 期权白皮书](https://www.cboe.com/education/)
- [QuantLib 官方文档](https://www.quantlib.org/)
- [Options Greeks 教程](https://www.optionsplaybook.com/options-introduction/option-greeks/)

## 数据字典
### 1. SPY Underlying Data (`spy_underlying.csv`)
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

### 2. SPY Option Chain (`spy_option_chain.csv`)
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

### 3. Treasury Rates (`treasury_rates.csv`)
| 字段名 | 类型 | 说明 | 示例 |
|--------|------|------|------|
| date | datetime | 日期 | 2024-10-15 |
| rate_10y | float | 10 年期国债收益率 | 0.045 |

- **用途**：无风险利率，用于定价、Greeks 计算与绩效评估
- **注意事项**：收益率已换算为小数，可在定价时直接使用；必要时可替换为期限匹配的利率

## 计算公式参考
### Put-Call Parity
```
C - P = S - K * e^{-rT}
```
- C：Call 价格
- P：Put 价格
- S：标的价格
- K：行权价
- r：无风险利率
- T：到期时间（年）

### Black-Scholes Greeks
详见 [Options Greeks 参考](https://www.optionsplaybook.com/options-introduction/option-greeks/)

### 隐含波动率计算
使用牛顿迭代法求解 BS 定价公式的逆问题：
```
market_price = BS(S, K, T, r, σ)
```
求解 σ（implied volatility）。
