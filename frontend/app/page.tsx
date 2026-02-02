import TradingViewChart from "../components/TradingViewChart";
import LightweightChart from "../components/LightweightChart";
import NewsFeed from "../components/NewsFeed";
import BackendStatus from "../components/BackendStatus";
import { CHART_CONFIG } from "../lib/config";
import styles from "./page.module.css";

export default function Home() {
  return (
    <main className={styles.page}>
      <header className={styles.header}>
        <div className={styles.brand}>
          <span className={styles.logoDot} />
          <span className={styles.brandName}>signal-render</span>
          <BackendStatus />
        </div>
        <div className={styles.pairTag}>PAIR · BTC/USDT</div>
      </header>

      <section className={styles.grid}>
        <div className={styles.leftColumn}>
          <div className={styles.panel}>
            <div className={styles.panelHeader}>
              <span>TradingView Pro</span>
              <span className={styles.panelBadge}>Live Market</span>
            </div>
            <TradingViewChart symbol={CHART_CONFIG.tradingViewSymbol} interval={CHART_CONFIG.interval} />
          </div>

          <div className={styles.panel}>
            <div className={styles.panelHeader}>
              <span>Own Kline + Indicator</span>
              <span className={styles.panelBadgeAlt}>Hasura Feed</span>
            </div>
            <LightweightChart />
          </div>
        </div>

        <aside className={styles.rightColumn}>
          <NewsFeed />
        </aside>
      </section>
    </main>
  );
}
