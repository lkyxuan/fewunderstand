"use client";

import { useState, useRef, useEffect } from "react";
import styles from "./PairSelector.module.css";

type PairSelectorProps = {
  currentPair: string;
  onPairChange: (pair: string) => void;
};

const POPULAR_PAIRS = [
  "BTC/USDT",
  "ETH/USDT",
  "BNB/USDT",
  "SOL/USDT",
  "XRP/USDT",
  "ADA/USDT",
  "DOGE/USDT",
  "AVAX/USDT",
  "DOT/USDT",
  "MATIC/USDT"
];

export default function PairSelector({ currentPair, onPairChange }: PairSelectorProps) {
  const [isOpen, setIsOpen] = useState(false);
  const [searchQuery, setSearchQuery] = useState("");
  const dropdownRef = useRef<HTMLDivElement>(null);
  const inputRef = useRef<HTMLInputElement>(null);

  const filteredPairs = POPULAR_PAIRS.filter(pair =>
    pair.toLowerCase().includes(searchQuery.toLowerCase())
  );

  // Check if search query is a valid custom pair format
  const isCustomPair = searchQuery.length > 0 && 
                       !POPULAR_PAIRS.some(p => p.toLowerCase() === searchQuery.toLowerCase());

  useEffect(() => {
    const handleClickOutside = (event: MouseEvent) => {
      if (dropdownRef.current && !dropdownRef.current.contains(event.target as Node)) {
        setIsOpen(false);
        setSearchQuery("");
      }
    };

    if (isOpen) {
      document.addEventListener("mousedown", handleClickOutside);
    }

    return () => {
      document.removeEventListener("mousedown", handleClickOutside);
    };
  }, [isOpen]);

  const handlePairSelect = (pair: string) => {
    onPairChange(pair);
    setIsOpen(false);
    setSearchQuery("");
  };

  const handleKeyDown = (e: React.KeyboardEvent<HTMLInputElement>) => {
    if (e.key === "Enter" && searchQuery.trim()) {
      // Format the input: convert to uppercase and ensure /USDT suffix
      let formattedPair = searchQuery.trim().toUpperCase();
      
      // If user just typed "BTC" or "btc", add /USDT
      if (!formattedPair.includes("/")) {
        formattedPair = formattedPair + "/USDT";
      }
      
      handlePairSelect(formattedPair);
    }
  };

  return (
    <div className={styles.container} ref={dropdownRef}>
      <button 
        className={styles.trigger}
        onClick={() => setIsOpen(!isOpen)}
      >
        <span className={styles.label}>PAIR</span>
        <span className={styles.divider}>·</span>
        <span className={styles.pair}>{currentPair}</span>
      </button>

      {isOpen && (
        <div className={styles.dropdown}>
          <input
            ref={inputRef}
            type="text"
            className={styles.search}
            placeholder="Search or type pair (e.g., LINK/USDT)..."
            value={searchQuery}
            onChange={(e) => setSearchQuery(e.target.value)}
            onKeyDown={handleKeyDown}
            autoFocus
          />
          <div className={styles.list}>
            {isCustomPair && searchQuery.trim() && (
              <button
                className={`${styles.item} ${styles.customItem}`}
                onClick={() => {
                  let formattedPair = searchQuery.trim().toUpperCase();
                  if (!formattedPair.includes("/")) {
                    formattedPair = formattedPair + "/USDT";
                  }
                  handlePairSelect(formattedPair);
                }}
              >
                <span className={styles.customLabel}>Use custom:</span> {searchQuery.toUpperCase()}
                {!searchQuery.includes("/") && "/USDT"}
              </button>
            )}
            {filteredPairs.length > 0 ? (
              filteredPairs.map((pair) => (
                <button
                  key={pair}
                  className={`${styles.item} ${pair === currentPair ? styles.active : ""}`}
                  onClick={() => handlePairSelect(pair)}
                >
                  {pair}
                </button>
              ))
            ) : !isCustomPair && (
              <div className={styles.empty}>No pairs found</div>
            )}
          </div>
          <div className={styles.hint}>
            💡 Tip: Type any pair and press Enter
          </div>
        </div>
      )}
    </div>
  );
}
