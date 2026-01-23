"use client";

import { useState } from "react";
import TradingViewChart from "../components/TradingViewChart";
import LightweightChart from "../components/LightweightChart";
import NewsFeed from "../components/NewsFeed";
import BackendStatus from "../components/BackendStatus";
import PairSelector from "../components/PairSelector";
import styles from "./page.module.css";

export default function Home() {
  const [currentPair, setCurrentPair] = useState("BTC/USDT");

  // Convert "BTC/USDT" to "BTCUSDT" for queries
  const symbol = currentPair.replace("/", "");
  
  // Convert "BTC/USDT" to "BINANCE:BTCUSDT" for TradingView
  const tradingViewSymbol = `BINANCE:${symbol}`;

  return (
    <main className={styles.page}>
      <header className={styles.header}>
        <div className={styles.brand}>
          <span className={styles.logoDot} />
          <span className={styles.brandName}>signal-render</span>
          <BackendStatus />
        </div>
        <PairSelector currentPair={currentPair} onPairChange={setCurrentPair} />
      </header>

      <section className={styles.grid}>
        <div className={styles.leftColumn}>
          <div className={styles.panel}>
            <div className={styles.panelHeader}>
              <span>TradingView Pro</span>
              <span className={styles.panelBadge}>Live Market</span>
            </div>
            <TradingViewChart symbol={tradingViewSymbol} interval="5" />
          </div>

          <div className={styles.panel}>
            <div className={styles.panelHeader}>
              <span>Own Kline + Indicator</span>
              <span className={styles.panelBadgeAlt}>Hasura Feed</span>
            </div>
            <LightweightChart symbol={symbol} />
          </div>
        </div>

        <aside className={styles.rightColumn}>
          <NewsFeed />
        </aside>
      </section>
    </main>
  );
}
