"use client";

import { useEffect, useMemo, useRef } from "react";
import { useQuery } from "@apollo/client";
import { createChart, type CandlestickData, type LineData, type UTCTimestamp } from "lightweight-charts";
import { GET_INDICATORS, GET_KLINES, DEFAULT_QUERY_VARS } from "../lib/queries";
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

export default function LightweightChart() {
  const containerRef = useRef<HTMLDivElement | null>(null);
  const chartRef = useRef<ReturnType<typeof createChart> | null>(null);
  const candleSeriesRef = useRef<ReturnType<
    ReturnType<typeof createChart>["addCandlestickSeries"]
  > | null>(null);
  const lineSeriesRef = useRef<ReturnType<
    ReturnType<typeof createChart>["addLineSeries"]
  > | null>(null);

  const {
    data: klineData,
    loading: loadingKlines,
    error: errorKlines,
    refetch: refetchKlines
  } = useQuery<{ klines_5m: KlineRow[] }>(GET_KLINES, {
    variables: DEFAULT_QUERY_VARS
  });

  const {
    data: indicatorData,
    loading: loadingIndicators,
    error: errorIndicators,
    refetch: refetchIndicators
  } = useQuery<{ indicators: IndicatorRow[] }>(GET_INDICATORS, {
    variables: DEFAULT_QUERY_VARS
  });

  const candles = useMemo<CandlestickData<UTCTimestamp>[]>(() => {
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
  }, [klineData]);

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

    // 配置左侧坐标轴（指标用）
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
      // 自动缩放到数据范围
      chartRef.current.timeScale().fitContent();
      // 设置可见范围为最近的数据
      const lastTime = candles[candles.length - 1].time;
      const firstTime = candles[0].time;
      chartRef.current.timeScale().setVisibleRange({
        from: firstTime,
        to: lastTime
      });
    }
  }, [candles]);

  // 暂时禁用 indicator 线（数据不完整）
  // useEffect(() => {
  //   if (!lineSeriesRef.current) return;
  //   lineSeriesRef.current.setData(indicatorLine);
  // }, [indicatorLine]);

  const isLoading = loadingKlines || loadingIndicators;
  const error = errorKlines || errorIndicators;

  return (
    <div className={styles.wrapper}>
      <div ref={containerRef} className={styles.chart} />
      {isLoading && <div className={styles.overlay}>Loading data…</div>}
      {!isLoading && candles.length === 0 && !error && (
        <div className={styles.overlay}>No kline data available.</div>
      )}
      {error && (
        <div className={styles.overlay}>
          <p className={styles.errorTitle}>Chart data unavailable</p>
          <p className={styles.errorDesc}>GraphQL request failed.</p>
          <button
            className={styles.retry}
            onClick={() => {
              refetchKlines();
              refetchIndicators();
            }}
          >
            Retry
          </button>
        </div>
      )}
    </div>
  );
}
