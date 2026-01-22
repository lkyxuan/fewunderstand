"use client";

import { useMemo } from "react";
import { useQuery, gql } from "@apollo/client";
import styles from "./BackendStatus.module.css";

const PING = gql`
  query Ping {
    __typename
  }
`;

export default function BackendStatus() {
  const { loading, error } = useQuery(PING, { fetchPolicy: "network-only" });

  const status = useMemo(() => {
    if (loading) return "connecting";
    if (error) return "offline";
    return "online";
  }, [loading, error]);

  return (
    <span className={`${styles.badge} ${styles[status]}`}>
      <span className={styles.dot} />
      {status}
    </span>
  );
}
