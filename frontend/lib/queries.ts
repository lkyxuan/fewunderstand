import { gql } from "@apollo/client";
import { CHART_CONFIG } from "./config";

export const GET_KLINES = gql`
  query GetKlines($symbol: String!, $limit: Int!) {
    klines_5m(
      where: { symbol: { _eq: $symbol } }
      order_by: { time: desc }
      limit: $limit
    ) {
      time
      open
      high
      low
      close
    }
  }
`;

export const GET_INDICATORS = gql`
  query GetIndicators($symbol: String!, $limit: Int!) {
    indicators(
      where: { symbol: { _eq: $symbol } }
      order_by: { time: desc }
      limit: $limit
    ) {
      time
      change_5min_pct
    }
  }
`;

// 默认查询变量
export const DEFAULT_QUERY_VARS = {
  symbol: CHART_CONFIG.symbol,
  limit: CHART_CONFIG.limit
};

export const GET_SIGNALS = gql`
  query GetSignals {
    signals(order_by: { time: desc }, limit: 50) {
      id
      time
      symbol
      signal_type
      change_pct
    }
  }
`;

export const SUBSCRIBE_SIGNALS = gql`
  subscription SubscribeSignals {
    signals(order_by: { time: desc }, limit: 10) {
      id
      time
      symbol
      signal_type
      change_pct
    }
  }
`;

// 新闻查询
export const GET_NEWS = gql`
  query GetNews {
    news(order_by: { time: desc }, limit: 50) {
      id
      time
      source
      title
      link
      summary
    }
  }
`;

// 新闻实时订阅
export const SUBSCRIBE_NEWS = gql`
  subscription SubscribeNews {
    news(order_by: { time: desc }, limit: 20) {
      id
      time
      source
      title
      link
      summary
    }
  }
`;
