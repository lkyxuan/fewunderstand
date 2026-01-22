"use client";

import { useEffect, useRef } from "react";
import styles from "./TradingViewChart.module.css";

type TradingViewChartProps = {
  symbol?: string;
  interval?: string;
};

export default function TradingViewChart({
  symbol = "BINANCE:BTCUSDT",
  interval = "15"
}: TradingViewChartProps) {
  const containerRef = useRef<HTMLDivElement | null>(null);

  useEffect(() => {
    if (!containerRef.current) return;
    containerRef.current.innerHTML = "";

    const wrapper = document.createElement("div");
    wrapper.className = "tradingview-widget-container";
    wrapper.style.height = "100%";
    wrapper.style.width = "100%";

    const widget = document.createElement("div");
    widget.className = "tradingview-widget-container__widget";
    widget.style.height = "100%";
    widget.style.width = "100%";

    wrapper.appendChild(widget);

    const script = document.createElement("script");
    script.type = "text/javascript";
    script.src =
      "https://s3.tradingview.com/external-embedding/embed-widget-advanced-chart.js";
    script.async = true;
    script.innerHTML = JSON.stringify({
      autosize: true,
      symbol,
      interval,
      timezone: "Etc/UTC",
      theme: "dark",
      style: "1",
      locale: "en",
      allow_symbol_change: false,
      hide_side_toolbar: true,
      withdateranges: true,
      hide_legend: false,
      hide_volume: false,
      calendar: false,
      support_host: "https://www.tradingview.com"
    });

    wrapper.appendChild(script);
    containerRef.current.appendChild(wrapper);

    return () => {
      if (containerRef.current) {
        containerRef.current.innerHTML = "";
      }
    };
  }, [symbol, interval]);

  return <div ref={containerRef} className={styles.container} />;
}
