# 期权Greeks套利策略示例

## 1. Put-Call Parity套利

### 原理
根据无套利原理：

C - P = S - K·e^(-rT)

### 套利条件
当市场价格偏离理论值 > 交易成本时

### 示例
- SPY = $430
- 430 Call = $5.50
- 430 Put = $4.20
- K = $430, T = 30天, r = 4%

理论：C - P = 430 - 430·e^(-0.04·30/365) = $1.41
实际：C - P = 5.50 - 4.20 = $1.30

偏离：$0.11 (约0.03%)

**如果偏离 > 1%（$4.30）：**
- 执行套利组合
- 预期收益 = 偏离值 - 交易成本

---

## 2. Volatility Smile套利

### 现象
相同到期日，不同行权价的IV不同
- OTM Put的IV > ATM的IV （Left Skew）
- OTM Call的IV可能也偏高

### 套利策略
1. **Long低IV期权 + Short高IV期权**
2. **保持Delta中性**

### 示例
- ATM (K=430): IV = 18%
- OTM Put (K=420): IV = 22%

策略：
- Short 1 ATM Call (IV=18%)
- Long 2 OTM Calls (IV=16%)
- 调整数量使Delta=0

---

## 3. Calendar Spread

### 原理
Near-term期权时间价值衰减快于Far-term

### 示例
- Short近月ATM Call (30天，IV=18%)
- Long远月ATM Call (60天，IV=17%)
- Delta接近中性

### 盈利情况
- 标的价格横盘震荡
- 近月IV下降或远月IV上升

---

## 参考阅读
- CBOE期权策略：https://www.cboe.com/strategies/
- Hull《Options, Futures, and Other Derivatives》
- Natenberg《Option Volatility & Pricing》