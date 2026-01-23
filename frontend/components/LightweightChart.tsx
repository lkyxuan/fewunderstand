"use client";

import { useEffect, useMemo, useRef, useState } from "react";
import { useQuery } from "@apollo/client";
import { createChart, type CandlestickData, type LineData, type UTCTimestamp } from "lightweight-charts";
import { GET_INDICATORS, GET_KLINES } from "../lib/queries";
import { fetchBinanceKlines, type KlineData } from "../lib/binance";
import styles from "./LightweightChart.module.css";

type KlineRow = {
  time: string;
  open: string;
  high: string;
  low: string;
  close: string;
};

type IndicatorRow = {
  time: string;
  change_5min_pct: string | null;
};

type LightweightChartProps = {
  symbol: string;
  limit?: number;
};

// Auto-refresh interval: 30 seconds
const REFRESH_INTERVAL = 30000;

export default function LightweightChart({ symbol, limit = 864 }: LightweightChartProps) {
  const containerRef = useRef<HTMLDivElement | null>(null);
  const chartRef = useRef<ReturnType<typeof createChart> | null>(null);
  const candleSeriesRef = useRef<ReturnType<
    ReturnType<typeof createChart>["addCandlestickSeries"]
  > | null>(null);
  const lineSeriesRef = useRef<ReturnType<
    ReturnType<typeof createChart>["addLineSeries"]
  > | null>(null);

  const [binanceData, setBinanceData] = useState<KlineData[] | null>(null);
  const [loadingBinance, setLoadingBinance] = useState(false);
  const [binanceError, setBinanceError] = useState<string | null>(null);
  const [lastUpdate, setLastUpdate] = useState<Date>(new Date());

  const {
    data: klineData,
    loading: loadingKlines,
    error: errorKlines,
    refetch: refetchKlines
  } = useQuery<{ klines_5m: KlineRow[] }>(GET_KLINES, {
    variables: { symbol, limit },
    pollInterval: REFRESH_INTERVAL
  });

  const {
    data: indicatorData,
    loading: loadingIndicators,
    error: errorIndicators,
    refetch: refetchIndicators
  } = useQuery<{ indicators: IndicatorRow[] }>(GET_INDICATORS, {
    variables: { symbol, limit },
    pollInterval: REFRESH_INTERVAL
  });

  const hasHasuraData = (klineData?.klines_5m?.length ?? 0) > 0;

  const fetchBinanceData = async () => {
    setLoadingBinance(true);
    setBinanceError(null);

    try {
      const data = await fetchBinanceKlines(symbol, "5m", limit);
      setBinanceData(data);
      setLastUpdate(new Date());
    } catch (error: any) {
      console.error("Failed to fetch Binance data:", error);
      setBinanceError(error.message);
    } finally {
      setLoadingBinance(false);
    }
  };

  useEffect(() => {
    if (!loadingKlines && !hasHasuraData) {
      fetchBinanceData();
    } else if (hasHasuraData) {
      setBinanceData(null);
      setBinanceError(null);
      setLastUpdate(new Date());
    }
  }, [symbol, hasHasuraData, loadingKlines]);

  useEffect(() => {
    if (!hasHasuraData && binanceData) {
      const intervalId = setInterval(() => {
        fetchBinanceData();
      }, REFRESH_INTERVAL);

      return () => clearInterval(intervalId);
    }
  }, [hasHasuraData, binanceData, symbol]);

  const candles = useMemo<CandlestickData<UTCTimestamp>[]>(() => {
    if (hasHasuraData) {
      const rows = klineData?.klines_5m ?? [];
      return rows
        .map((row) => ({
          time: Math.floor(new Date(row.time).getTime() / 1000) as UTCTimestamp,
          open: Number(row.open),
          high: Number(row.high),
          low: Number(row.low),
          close: Number(row.close)
        }))
        .sort((a, b) => (a.time as number) - (b.time as number));
    }

    if (binanceData) {
      return binanceData.map(row => ({
        time: row.time as UTCTimestamp,
        open: row.open,
        high: row.high,
        low: row.low,
        close: row.close
      }));
    }

    return [];
  }, [klineData, binanceData, hasHasuraData]);

  const indicatorLine = useMemo<LineData<UTCTimestamp>[]>(() => {
    const rows = indicatorData?.indicators ?? [];
    return rows
      .filter((row) => row.change_5min_pct !== null)
      .map((row) => ({
        time: Math.floor(new Date(row.time).getTime() / 1000) as UTCTimestamp,
        value: Number(row.change_5min_pct)
      }))
      .sort((a, b) => (a.time as number) - (b.time as number));
  }, [indicatorData]);

  useEffect(() => {
    if (!containerRef.current) return;

    const chart = createChart(containerRef.current, {
      layout: {
        background: { color: "#000000" },
        textColor: "#888888"
      },
      grid: {
        vertLines: { color: "#1a1a1a" },
        horzLines: { color: "#1a1a1a" }
      },
      timeScale: {
        borderColor: "#222222",
        timeVisible: true,
        secondsVisible: false
      },
      rightPriceScale: {
        borderColor: "#222222"
      },
      crosshair: {
        mode: 1
      },
      autoSize: true
    });

    const candleSeries = chart.addCandlestickSeries({
      upColor: "#00ff88",
      downColor: "#ff4757",
      borderVisible: false,
      wickUpColor: "#00ff88",
      wickDownColor: "#ff4757"
    });

    const indicatorSeries = chart.addLineSeries({
      color: "#56ccf2",
      lineWidth: 2,
      priceScaleId: "left"
    });

    chart.priceScale("left").applyOptions({
      borderColor: "#222222",
      scaleMargins: { top: 0.8, bottom: 0 }
    });

    chartRef.current = chart;
    candleSeriesRef.current = candleSeries;
    lineSeriesRef.current = indicatorSeries;

    return () => {
      chart.remove();
      chartRef.current = null;
      candleSeriesRef.current = null;
      lineSeriesRef.current = null;
    };
  }, []);

  useEffect(() => {
    if (!candleSeriesRef.current || !chartRef.current) return;
    candleSeriesRef.current.setData(candles);
    if (candles.length > 0) {
      chartRef.current.timeScale().fitContent();
      const lastTime = candles[candles.length - 1].time;
      const firstTime = candles[0].time;
      chartRef.current.timeScale().setVisibleRange({
        from: firstTime,
        to: lastTime
      });
    }
  }, [candles]);

  const isLoading = loadingKlines || loadingIndicators || loadingBinance;
  const error = errorKlines || errorIndicators || (binanceError ? new Error(binanceError) : null);
  const dataSource = hasHasuraData ? "Hasura" : binanceData ? "Binance API" : null;

  const formatUpdateTime = (date: Date) => {
    return date.toLocaleTimeString("en-US", {
      hour: "2-digit",
      minute: "2-digit",
      second: "2-digit",
      hour12: false
    });
  };

  return (
    <div className={styles.wrapper}>
      <div ref={containerRef} className={styles.chart} />
      {dataSource && (
        <div className={styles.dataSource}>
          {dataSource === "Binance API" && "⚡ "}
          {dataSource}
          <span className={styles.updateTime}> • {formatUpdateTime(lastUpdate)}</span>
        </div>
      )}
      {isLoading && <div className={styles.overlay}>Loading data…</div>}
      {!isLoading && candles.length === 0 && !error && (
        <div className={styles.overlay}>No kline data available.</div>
      )}
      {error && (
        <div className={styles.overlay}>
          <p className={styles.errorTitle}>Chart data unavailable</p>
          <p className={styles.errorDesc}>
            {hasHasuraData ? "GraphQL request failed" : "Failed to fetch data from Binance API"}
          </p>
          <button
            className={styles.retry}
            onClick={() => {
              if (hasHasuraData || !binanceData) {
                refetchKlines();
                refetchIndicators();
              } else {
                fetchBinanceData();
              }
            }}
          >
            Retry
          </button>
        </div>
      )}
    </div>
  );
}
