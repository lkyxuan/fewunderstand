"use client";

import { useEffect, useMemo, useRef, useState } from "react";
import { useQuery, useSubscription } from "@apollo/client";
import { GET_NEWS, SUBSCRIBE_NEWS } from "../lib/queries";
import styles from "./NewsFeed.module.css";

type NewsItem = {
  id: number;
  time: string;
  source: string;
  title: string;
  link: string | null;
  summary: string | null;
};

const HIGHLIGHT_MS = 3000;

export default function NewsFeed() {
  const [news, setNews] = useState<NewsItem[]>([]);
  const [highlightIds, setHighlightIds] = useState<Set<number>>(new Set());
  const timersRef = useRef<Map<number, number>>(new Map());

  const {
    data: initialData,
    loading: loadingInitial,
    error: errorInitial,
    refetch
  } = useQuery<{ news: NewsItem[] }>(GET_NEWS);

  useEffect(() => {
    if (!initialData?.news) return;
    setNews(initialData.news);
  }, [initialData]);

  const queueHighlights = (freshNews: NewsItem[]) => {
    freshNews.forEach((item) => {
      setHighlightIds((prev) => new Set([...prev, item.id]));
      if (timersRef.current.has(item.id)) {
        window.clearTimeout(timersRef.current.get(item.id));
      }
      const timer = window.setTimeout(() => {
        setHighlightIds((prev) => {
          const next = new Set(prev);
          next.delete(item.id);
          return next;
        });
        timersRef.current.delete(item.id);
      }, HIGHLIGHT_MS);
      timersRef.current.set(item.id, timer);
    });
  };

  useSubscription<{ news: NewsItem[] }>(SUBSCRIBE_NEWS, {
    onData: ({ data }) => {
      const incoming = data.data?.news ?? [];
      if (incoming.length === 0) return;
      setNews((prev) => {
        const existing = new Set(prev.map((item) => item.id));
        const fresh = incoming.filter((item) => !existing.has(item.id));
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

  const items = useMemo(() => news, [news]);

  return (
    <div className={styles.container}>
      <div className={styles.header}>
        <div>
          <p className={styles.kicker}>NEWS FLOW</p>
          <h2 className={styles.title}>Live News</h2>
        </div>
        <span className={styles.count}>{items.length}</span>
      </div>

      <div className={styles.list}>
        {loading && <div className={styles.state}>Loading news…</div>}
        {!loading && items.length === 0 && !error && (
          <div className={styles.state}>No news yet.</div>
        )}
        {error && (
          <div className={styles.state}>
            <p className={styles.errorTitle}>News feed offline</p>
            <p className={styles.errorDesc}>Subscription error.</p>
            <button className={styles.retry} onClick={() => refetch()}>
              Retry
            </button>
          </div>
        )}

        {items.map((item) => {
          const isHighlight = highlightIds.has(item.id);
          return (
            <a
              key={item.id}
              href={item.link || "#"}
              target="_blank"
              rel="noopener noreferrer"
              className={`${styles.item} ${isHighlight ? styles.highlight : ""}`}
            >
              <div className={styles.itemContent}>
                <p className={styles.itemTitle}>{item.title}</p>
                {item.summary && (
                  <p className={styles.itemSummary}>{item.summary}</p>
                )}
              </div>
              <div className={styles.itemMeta}>
                <span className={styles.itemSource}>{item.source}</span>
                <span className={styles.itemTime}>{formatTime(item.time)}</span>
              </div>
            </a>
          );
        })}
      </div>
    </div>
  );
}

function formatTime(iso: string) {
  const date = new Date(iso);
  return new Intl.DateTimeFormat("en-US", {
    hour: "2-digit",
    minute: "2-digit"
  }).format(date);
}
