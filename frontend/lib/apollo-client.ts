import { ApolloClient, HttpLink, InMemoryCache, split } from "@apollo/client";
import { GraphQLWsLink } from "@apollo/client/link/subscriptions";
import { getMainDefinition } from "@apollo/client/utilities";
import { createClient } from "graphql-ws";

const httpUrl =
  process.env.NEXT_PUBLIC_HASURA_HTTP_URL ||
  "http://localhost:8080/v1/graphql";
const wsUrl =
  process.env.NEXT_PUBLIC_HASURA_WS_URL || "ws://localhost:8080/v1/graphql";

export function makeApolloClient() {
  const httpLink = new HttpLink({ uri: httpUrl });

  if (typeof window === "undefined") {
    return new ApolloClient({
      link: httpLink,
      cache: new InMemoryCache()
    });
  }

  const wsLink = new GraphQLWsLink(
    createClient({
      url: wsUrl,
      retryAttempts: 5
    })
  );

  const splitLink = split(
    ({ query }) => {
      const definition = getMainDefinition(query);
      return (
        definition.kind === "OperationDefinition" &&
        definition.operation === "subscription"
      );
    },
    wsLink,
    httpLink
  );

  return new ApolloClient({
    link: splitLink,
    cache: new InMemoryCache()
  });
}
