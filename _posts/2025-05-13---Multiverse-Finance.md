---
title: "Multiverse Finance"
source: "https://www.paradigm.xyz/2025/05/multiverse-finance"
author:
  - "[[Paradigm]]"
date: "2025-05-13 12:05:21 +0800"
description: "Addressing capital efficiency in prediction markets by splitting the financial system into parallel universes"
tags:
  - "DeFi"
  - "预测市场"
  - "多宇宙金融"
categories: "金融创新"
---
https://www.paradigm.xyz/2025/05/multiverse-finance
## Introduction

Prediction markets let you bet on outcomes, but so much more is possible.

This paper introduces Multiverse Finance, which splits the financial system into parallel universes so you can short the market today only if your favorite candidate is going to lose the next election.

## Intuition

Consider a prediction market on whether Jerome Powell will be fired in 2025. If you think he won't be, you can buy a notFiredUSD token for 89 cents which will be worth $1 in 2026 if he isn't fired.  

But that's a long time to wait, and in the meantime you can't use your notFiredUSD as collateral in most financial systems -- if Powell were suddenly fired, the token's value could drop to 0 faster than the system could liquidate your debt.

However, there is no problem when using notFiredUSD as collateral to borrow, say notFiredETH. If Powell is suddenly fired, both your collateral and the asset you borrowed become worthless simultaneously, so there is no liquidation issue.

This idea is what makes Multiverse Finance possible.

The simplest version of Multiverse Finance could be implemented today on mainnet by allowing conditional tokens for the same outcomes (like firedEth and firedUSD) to be borrowed and lent against each other on an Aave-like protocol.

Further expansions are possible, including (liquidity issues aside) complete financial ecosystems with limitless chains of composibility -- you could take your firedUSD, borrow firedETH against it, provide liquidity on firedSwap to earn firedSwap tokens, stake those in firedFarm, and so on.

Like prediction markets or futarchies of the type implemented by [MetaDAO](https://metadao.fi/), in addition to allowing participants new opportunities to express financial views or hedge exposure, Metaverse Finance produces useful information about the world as a positive externality.

## Mechanism

### Verses

A "verse" is a parallel universe where some event we care about has happened or will happen at some point in the future.

Mathematically, verses correspond to [events](https://en.wikipedia.org/wiki/Event_\(probability_theory) in probability theory, which are sets of outcomes (possible states of the world) with the following structure:

- Any verse has a **complement** verse such that the two combine to cover all possible states of the world (e.g., "Powell fired by 2026" and "Powell not fired by 2026")
- Verses can be combined through countable **unions** to form new verses (e.g., "Powell fired by 2026 OR recession by 2026" is a verse where one of the two, or both, happen)
- The **intersection** of a countable set of verses forms a new verse (e.g., "Powell fired by 2026 AND recession by 2026" is a verse)

Today's universe, where the regular financial system exists, corresponds to the event containing the whole sample space.

We call a verse a "parent" to another verse if the child verse is a subset of the parent, meaning every outcome in the child verse is also in the parent verse. So, for example, "Powell fired by 2026" and "recession by 2026" are both parents of "Powell fired by 2026 AND recession by 2026."

Today's universe is a parent to all verses (although some verses, such as "Powell Fired by May 2025" become empty of possible outcomes as time goes on).

We call a set of child verses a **partition** of their parent verse if the child verses are disjoint (non-overlapping) and their union makes up the entire parent verse. For example, "Powell fired by 2026" and "Powell not fired by 2026" form a partition of today's universe.  

### Ownership Intuition

The high-level intuition when working with verses in Multiverse Finance is that owners can choose to push ownership down to a partition, or pull it up from a partition.

In other words, let's say we have a verse $V$ and some partition $P_1,P_2,P_3$ of $V$.

If I own 1 unit of a given token $T$ in $V$, I can choose to "push down" my ownership to the partition, meaning I give up my ownership of $T$ in $V$ and instead now own 1 unit of $T$ in each of $P_1,P_2$ and $P_3$. This is equivalent to how you can always take $1 and mint one YES and one NO token for a given prediction market.

Conversely, if I own 1 of token $T$ in each of $P_1,P_2$, and $P_3$, I can choose to "pull up" my ownership of $T$ to $V$, losing my ownership of it in each of those partition verses. This is equivalent to how you can take a YES and a NO token for a given prediction market and get back $1.

### Verse Resolution

Verses, like prediction markets, rely on some underlying oracle for resolution. This paper is agnostic to which type of oracle you might use.

At the time of resolution, any verse that does not contain the observed outcome reported by the oracle immediately disappears, together with all of its state.

If we had some partition $P_1,P_2,\ldots,P_N$ of a parent verse $A$, and a resolution evaporates all but one of them, such that only a single verse $P_i$ remains, $P_i$ now forms a complete partition of $A$ in and of itself, and we can pull up ownership of any given assets from $P_i$ directly to $A$.

For example, if I owned 1 USD in the "Powell not fired by 2026" verse and it's now Jan 1, 2026 and Powell has not been fired, the "Powell fired by 2026" verse disappears and "Powell not fired by 2026" partitions the full outcome space by itself, so I can pull my $1 up to the present day universe and withdraw it from the system. In this case, this is identical to normal prediction market resolution.

### Multiverse Maps

The ownership behavior described above is somewhat conceptual and could be implemented in many possible ways. We'll provide one example method here: the **multiverse map**.

This is a map (a.k.a. dictionary) datatype with two keys: verse ID and owner address.

The multiverse map is governed by two rules: one for splitting, and one for combining. We'll describe an **additive**, **non-negative** multiverse map with a single unsigned integer value.

- **Splitting**: The user controlling the owner address of a map entry for a given parent verse can subtract some quantity $x$ from the entry's value that leaves the entry non-negative, and then add $x$ to their balance in each of a set of verses that form a partition of the parent verse.
- **Combining**: The user controlling the owner address of a given map entry in each of a group of verses can subtract some quantity $x$ from the entry's values in each of those verses that leaves them all nonnegative, and then add $x$ to their balance in some parent verse that that group of verses form a partition of. As mentioned above, if the parent verse is the complete universe, this serves as a way for users to withdraw funds after event resolution.

### Multiverse Aware Applications

This primitive could be used to construct, say, a wrapper contract to make standard ERC20 tokens multiverse-ready.

Developers can also build more custom multiverse-aware applications using data structures like the multiverse map. A lending protocol like the one discussed above might, for example, specify that only assets from the same verse may be borrowed and lent against one another.

Designed properly, these protocols should be readily composable with one another as long as they are in the same verse. Again, the core insight is that developers don't need to worry about a token like notFiredEth disappearing suddenly and breaking a chain of composability, because every token in the verse should disappear simultaneously.

## Future Work

We're curious what *multiverse native* applications this concept might unlock.

If you have ideas, we'd love to hear from you.

  

***Acknowledgements***

Alpin Yukseloglu, Arjun Balaji, Dan Robinson, David Swain, Frankie, Matt Huang, Storm Slivkoff, Will Price, Jordi Alexander, Fozzy Diablo, Ella Papanek, Matt Liston, Serge Ravitch, Cristian Strat, Czar102, jdougy, Liam Zebedee, Mewny