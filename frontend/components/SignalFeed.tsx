"use client";

import { useEffect, useMemo, useRef, useState } from "react";
import { useQuery, useSubscription } from "@apollo/client";
import { GET_SIGNALS, SUBSCRIBE_SIGNALS } from "../lib/queries";
import styles from "./SignalFeed.module.css";

type Signal = {
  id: number;
  time: string;
  symbol: string;
  signal_type: string;
  change_pct: string | null;
};

const HIGHLIGHT_MS = 3000;

export default function SignalFeed() {
  const [signals, setSignals] = useState<Signal[]>([]);
  const [highlightIds, setHighlightIds] = useState<Set<number>>(new Set());
  const timersRef = useRef<Map<number, number>>(new Map());

  const {
    data: initialData,
    loading: loadingInitial,
    error: errorInitial,
    refetch
  } = useQuery<{ signals: Signal[] }>(GET_SIGNALS);

  useEffect(() => {
    if (!initialData?.signals) return;
    setSignals(initialData.signals);
  }, [initialData]);

  const queueHighlights = (freshSignals: Signal[]) => {
    freshSignals.forEach((signal) => {
      setHighlightIds((prev) => new Set([...prev, signal.id]));
      if (timersRef.current.has(signal.id)) {
        window.clearTimeout(timersRef.current.get(signal.id));
      }
      const timer = window.setTimeout(() => {
        setHighlightIds((prev) => {
          const next = new Set(prev);
          next.delete(signal.id);
          return next;
        });
        timersRef.current.delete(signal.id);
      }, HIGHLIGHT_MS);
      timersRef.current.set(signal.id, timer);
    });
  };

  useSubscription<{ signals: Signal[] }>(SUBSCRIBE_SIGNALS, {
    onData: ({ data }) => {
      const incoming = data.data?.signals ?? [];
      if (incoming.length === 0) return;
      setSignals((prev) => {
        const existing = new Set(prev.map((signal) => signal.id));
        const fresh = incoming.filter((signal) => !existing.has(signal.id));
        if (fresh.length > 0) {
          queueHighlights(fresh);
        }
        return [...fresh, ...prev].slice(0, 50);
      });
    }
  });

  useEffect(() => {
    return () => {
      timersRef.current.forEach((timer) => window.clearTimeout(timer));
      timersRef.current.clear();
    };
  }, []);

  const loading = loadingInitial;
  const error = errorInitial;

  const items = useMemo(() => signals, [signals]);

  return (
    <div className={styles.container}>
      <div className={styles.header}>
        <div>
          <p className={styles.kicker}>SIGNAL FLOW</p>
          <h2 className={styles.title}>Live Alerts</h2>
        </div>
        <span className={styles.count}>{items.length}</span>
      </div>

      <div className={styles.list}>
        {loading && <div className={styles.state}>Loading signals…</div>}
        {!loading && items.length === 0 && !error && (
          <div className={styles.state}>No signals yet.</div>
        )}
        {error && (
          <div className={styles.state}>
            <p className={styles.errorTitle}>Signal feed offline</p>
            <p className={styles.errorDesc}>Subscription error.</p>
            <button className={styles.retry} onClick={() => refetch()}>
              Retry
            </button>
          </div>
        )}

        {items.map((signal) => {
          const isHighlight = highlightIds.has(signal.id);
          return (
            <div
              key={signal.id}
              className={`${styles.item} ${isHighlight ? styles.highlight : ""}`}
            >
              <div>
                <p className={styles.itemType}>{formatSignalType(signal.signal_type)}</p>
                <p className={styles.itemSymbol}>{signal.symbol}</p>
              </div>
              <div className={styles.itemMeta}>
                <span className={styles.itemChange}>
                  {signal.change_pct ? `${Number(signal.change_pct).toFixed(2)}%` : "-"}
                </span>
                <span className={styles.itemTime}>{formatTime(signal.time)}</span>
              </div>
            </div>
          );
        })}
      </div>
    </div>
  );
}

function formatSignalType(type: string) {
  if (type === "pump_5min") return "PUMP 5M";
  if (type === "dump_5min") return "DUMP 5M";
  return type.toUpperCase();
}

function formatTime(iso: string) {
  const date = new Date(iso);
  return new Intl.DateTimeFormat("en-US", {
    hour: "2-digit",
    minute: "2-digit",
    second: "2-digit"
  }).format(date);
}
