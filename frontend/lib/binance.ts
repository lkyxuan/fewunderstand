// Binance API integration for fetching real-time kline data

export type BinanceKline = [
  number,  // Open time
  string,  // Open
  string,  // High
  string,  // Low
  string,  // Close
  string,  // Volume
  number,  // Close time
  string,  // Quote asset volume
  number,  // Number of trades
  string,  // Taker buy base asset volume
  string,  // Taker buy quote asset volume
  string   // Ignore
];

export interface KlineData {
  time: number;
  open: number;
  high: number;
  low: number;
  close: number;
}

/**
 * Fetch kline data from Binance API
 * @param symbol - Trading pair symbol (e.g., "BTCUSDT")
 * @param interval - Kline interval (e.g., "5m", "15m", "1h")
 * @param limit - Number of klines to fetch (default: 864 for 3 days at 5min)
 */
export async function fetchBinanceKlines(
  symbol: string,
  interval: string = "5m",
  limit: number = 864
): Promise<KlineData[]> {
  const url = `https://api.binance.com/api/v3/klines?symbol=${symbol}&interval=${interval}&limit=${limit}`;

  try {
    const response = await fetch(url);
    
    if (!response.ok) {
      throw new Error(`Binance API error: ${response.status} ${response.statusText}`);
    }

    const data: BinanceKline[] = await response.json();

    return data.map(kline => ({
      time: Math.floor(kline[0] / 1000), // Convert ms to seconds
      open: parseFloat(kline[1]),
      high: parseFloat(kline[2]),
      low: parseFloat(kline[3]),
      close: parseFloat(kline[4])
    }));
  } catch (error) {
    console.error("Failed to fetch Binance klines:", error);
    throw error;
  }
}
