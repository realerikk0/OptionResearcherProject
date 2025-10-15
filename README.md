# 美股期权Greeks套利策略开发项目

## 项目背景
您是一家量化交易机构的期权研究员，需要围绕SPY期权链开发基于Greeks异常识别的套利策略。本测试项目旨在评估候选人对数据处理、模型构建、策略设计与回测的综合能力。

## 为什么选择 SPY
- 日成交量超过 500 万张合约，流动性极佳
- 买卖价差极窄，便于捕捉细微定价偏差
- 拥有完整的周度与月度到期期权链
- 适合作为 Greeks 异常研究的基准标的

## 数据包概览
运行 `data/get_data.py` 后将在 `data/raw/` 目录生成（模拟数据，执行结果可复现）：
- `spy_option_chain.csv`：20 个交易日 × 3 个到期日 × 5 个行权价 × call/put 的期权切片，包含日期、标的价格、行权价、到期日、报价、成交量、持仓量、隐含波动率等字段，并植入可识别的 Put-Call Parity、IV Curve 与 Greeks 异常
- `spy_underlying.csv`：与期权日期对齐的 SPY ETF 日线行情（20 个交易日），字段涵盖开收盘价、最高最低价与成交量
- `treasury_rates.csv`：对应日期的 10 年期无风险利率序列，用于折现与 Greeks 计算

数据规模与特征覆盖经过精心设计，确保 README 中的必做与选做任务均可在该数据集上完成；若希望对比实盘行情，可在保持字段结构的前提下替换为自定义数据。

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
pandas>=2.0.0
numpy>=1.24.0
scipy>=1.11.0
matplotlib>=3.7.0
seaborn>=0.12.0
plotly>=5.17.0
jupyter>=1.0.0
# 可选（按需单独安装）
# quantlib-python
# vectorbt
```

## 数据获取方法
### 方法一（推荐）：使用提供脚本
- 进入 `data/`，运行 `python get_data.py`
- 脚本会生成 20 个交易日的日线行情与期权切片，兼具若干可识别异常（执行耗时 < 10 秒）
- 自动生成 `data/raw/` 目录及三份 CSV 文件（重复运行会覆盖旧数据）

### 方法二：自定义数据源
- 可接入 Interactive Brokers、TD Ameritrade 等 API
- 请保持字段命名与示例 schema 一致，确保下游脚本可复用

## 数据获取脚本
完整实现位于 `data/get_data.py`，可直接运行以下命令获取数据：
```bash
cd data
python get_data.py
```
脚本主要步骤：
- 构造 20 个连续交易日的 SPY 日线行情并保存为 `data/raw/spy_underlying.csv`
- 基于 Black-Scholes 生成 3 个到期日 × 5 个行权价 × call/put 的期权切片，附加合理的 bid/ask、成交量与隐含波动率，并保存为 `data/raw/spy_option_chain.csv`
- 生成与日期对应的无风险利率曲线 `data/raw/treasury_rates.csv`
- 输出数据摘要与分布概览，便于快速确认异常分布和样本规模

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
| date | datetime | 交易日期 | 2025-01-06 |
| open | float | 开盘价 | 458.32 |
| high | float | 最高价 | 463.61 |
| low | float | 最低价 | 455.84 |
| close | float | 收盘价 | 461.27 |
| volume | int | 成交量 | 5,820,000 |

- **数据来源**：脚本生成的合成行情（20 个连续交易日）
- **更新频率**：日线（运行脚本时一次性生成）

### 2. SPY Option Chain (`spy_option_chain.csv`)
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
- **数据质量**：每个交易日含 3 个到期日 × 5 个行权价 × call/put，脚本嵌入 Put-Call Parity、隐含波动率曲线与 Greeks 异常，便于验证异常检测逻辑

### 3. Treasury Rates (`treasury_rates.csv`)
| 字段名 | 类型 | 说明 | 示例 |
|--------|------|------|------|
| date | datetime | 日期 | 2025-01-06 |
| rate_10y | float | 10 年期国债收益率 | 0.04510 |

- **用途**：无风险利率，用于定价、Greeks 计算与绩效评估
- **注意事项**：收益率已换算为小数，可在定价时直接使用；如需其他期限，可在此基础上构造利率曲线

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
