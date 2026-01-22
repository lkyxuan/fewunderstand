// 图表共享配置
export const CHART_CONFIG = {
  symbol: "BTCUSDT",
  tradingViewSymbol: "BINANCE:BTCUSDT",
  interval: "5",  // 5 分钟
  limit: 864      // 3 天数据 (3 × 24 × 12)
} as const;
