# Loukaniko Travel Value API

A REST API that calculates **travel value indexes** to help you find the best value destinations. Compares purchasing power across countries by combining foreign exchange rates (EUR-based from ECB) with consumer price index data (World Bank CPI).

Use this to answer questions like: "Which countries give me the most bang for my buck?"

## Methodology

The travel value index uses the **Real Exchange Rate** formula, which adjusts nominal exchange rates for inflation differences between countries:

```
Real FX Rate = Nominal FX Rate × (Base Country CPI / Target Country CPI)
```

The **Travel Value Index** compares the current real exchange rate to its historical average (default: 20 years):

```
Travel Value Index = Real FX Current / Real FX Historical Average
```

**Interpretation:**
- **Index > 1.0**: Target country is better value than historical norm (currency is weaker, prices relatively lower)
- **Index < 1.0**: Target country is more expensive than historical norm (currency is stronger, prices relatively higher)
- **Index = 1.0**: Target country offers average value compared to its 20-year trend

**Why this works:**
- **Inflation-adjusted**: Raw exchange rates don't tell the full story—a weak currency with high inflation might not actually be cheap. The Real Exchange Rate accounts for this by normalizing CPI differences.
- **Historical comparison**: Comparing to a 20-year average filters out short-term volatility and reveals whether a destination is currently offering unusual value.
- **Relative measure**: By using ratios rather than absolute values, the index works across any currency pair and accounts for CPI base year differences.

This approach is grounded in economic theory (Purchasing Power Parity) and is sufficient for travel planning because it captures the two key factors that determine your actual spending power abroad: exchange rates and local price levels.

## Links
- [**API Root**](https://loukaniko.onrender.com/)
- [**Interactive Docs (Swagger)**](https://loukaniko.onrender.com/docs)
- [**ReDoc**](https://loukaniko.onrender.com/redoc)

## Limitations
- Only works for ~80 different countries due to the limited free FX rates available.

## Roadmap
- Upgrade to use [hexarate.paikama.co](https://hexarate.paikama.co/) for daily FX data covering 170+ currencies
