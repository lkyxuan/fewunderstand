---
tags:
  - DeFi
  - 稳定币
  - 风险管理
category: 知识科技
description: Cork Protocol 是一个专注于稳定币和流动质押代币去锚风险管理的 DeFi 平台。
title: Cork Protocol 解析
updated: 2025-04-19 00:09:25
created: 2025-04-18
---
### 直接回答

- Cork Protocol 似乎是一个去中心化金融（DeFi）平台，专注于为稳定币和流动质押代币管理去锚风险。
- 它通过 Depeg Swaps 允许用户对冲、交易和定价去锚事件的风险，研究表明这是一种创新的金融工具。
- 该项目与 Lido、Etherfi、Ethena 等有合作关系，并从 Andreessen Horowitz 等知名投资者获得资金支持。
- 当前状态为测试网阶段，计划未来主网上线。

#### 项目概述
Cork Protocol 是一个 DeFi 平台，旨在通过其核心产品 Depeg Swaps 帮助用户管理稳定币和流动质押代币（如 stETH、USDe）的去锚风险。去锚事件是指这些资产偏离其预期锚定价值（如 1 美元或 1 ETH）的风险。Depeg Swaps 是一种衍生工具，允许用户在资产去锚时以 1:1 比率兑换回基础资产，从而对冲损失。

#### 关键机制
- **Depeg Swaps**：用户可以购买 Depeg Swaps 来保护资产，如果资产去锚，Swaps 允许兑换回基础资产。
- **Cover Tokens**：流动性提供者持有 Cover Tokens，若无去锚事件可赚取固定收益，若发生去锚则价值下降。
- 交易通过 Uniswap v4 的自动做市商（AMM）进行，动态定价去锚风险。

#### 合作与支持
Cork 与 Lido、Etherfi、Ethena 和 Sky 等项目合作，可能为这些项目的代币创建市场。此外，它与 Resolv 集成，允许用户锁定 RLP 价格或通过存款赚取额外收益。该项目已从 Andreessen Horowitz、Orange DAO 等投资者获得未公开金额的资金支持。

#### 当前状态
截至 2025 年 4 月 18 日，Cork Protocol 处于测试网阶段，并举办交易竞赛，准备未来主网上线。

---

### 详细调研报告

Cork Protocol 是一个去中心化金融（DeFi）平台，专注于为稳定币和流动质押代币（Liquid Staking Tokens, LSTs）和再质押代币（Liquid Restaking Tokens, LRTs）等锚定资产管理去锚风险。其核心创新在于 Depeg Swaps，一种允许用户定价、交易和对冲去锚事件风险的金融工具。该项目通过与多个 DeFi 协议的合作以及来自知名投资者的资金支持，旨在增强 DeFi 生态系统的稳定性和透明度。

#### 项目背景与目标
Cork Protocol 的目标是解决链上信用市场缺乏有效风险管理框架的问题，特别是针对稳定币和 LST/LRTs 等锚定资产，这些资产的总市值可能高达数百亿美元。研究表明，这些资产因去锚风险而面临潜在波动，Cork 通过其 Depeg Swaps 提供了一种类似传统金融中信用违约掉期的工具，帮助用户管理这些风险。

根据 [Cork Protocol 官方文档](https://docs.cork.tech/)，该协议旨在通过 tokenizing 风险，使市场能够对去锚事件进行定价、交易和对冲，最终构建一个更稳定、透明和开放的 DeFi 生态系统。

#### 核心机制与功能
Cork Protocol 的核心机制包括 Depeg Swaps 和 Cover Tokens，具体运作如下：

- **Depeg Swaps**：
  - Depeg Swaps 是一种衍生工具，允许持有者在其到期前以 1:1 比率兑换锚定资产（Pegged Asset）为基础资产（Redemption Asset）。例如，在 ETH:stETH 市场中，若 stETH 去锚，持有 Depeg Swap 的用户可将其 stETH 加上 Swap 兑换为 ETH，从而对冲损失。
  - 这种机制通过 Peg Stability Module（PSM）实现，PSM 接受基础资产（如 ETH、USDC）以创建 Depeg Swaps 和 Cover Tokens。
  - 根据 [Cork 技术网站](https://www.cork.tech/)，Depeg Swaps 的应用包括对冲小规模临时去锚到大规模“黑天鹅”事件的风险，涵盖风险定价（高价格表示高风险，低价格表示低风险）、对冲（保护资产免受去锚影响）、交易（做多或做空去锚风险）以及 DeFi 集成（如杠杆收益耕作无需清算风险，或在无去锚暴露下赚取收益）。

- **Cover Tokens**：
  - Cover Tokens 由流动性提供者持有，他们承担去锚风险。若在期限内无去锚事件，Cover Tokens 可赚取固定收益；若发生去锚，Cover Tokens 的价值会下降，以覆盖损失。
  - Depeg Swaps 和 Cover Tokens 的价值运动相反：当去锚发生时，Depeg Swaps 价值上升，Cover Tokens 价值下降；反之亦然。这种对立关系通过 Uniswap v4 的自动做市商（AMM）实现动态定价。

- **市场结构**：
  - 每个 Cork 市场由一对资产组成：基础资产（如 ETH）和锚定资产（如 stETH），并有固定到期时间。
  - 例如，市场可能包括 ETH:stETH、wstETH:weETH、sUSDS:USDe、sUSDe:USDT 等，涵盖稳定币和 LST/LRTs。
  - 流动性池通过 AMM 管理 Depeg Swaps 和 Cover Tokens 的铸造和交易，确保市场流动性和价格发现。

#### 合作与集成
Cork Protocol 与多个 DeFi 项目建立了合作伙伴关系，包括：
- Lido：提供 stETH 等流动质押代币。
- Etherfi：可能涉及 eETH 或类似资产。
- Ethena：提供 USDe 等稳定币。
- Sky：可能涉及其他锚定资产。

此外，根据 X 帖子（例如 [Corkprotocol X 帖子](https://x.com/Corkprotocol/status/1912838520768741673)），Cork 与 Resolv 集成，允许用户：
- 通过支付 0.007 美元锁定 RLP 价格 53 天（年化成本 4.7%）。
- 通过将 stUSR 存入 Cork 赚取双重奖励，包括 Resolv 质押和 Cork 收益。

这些集成扩展了 Cork 的应用场景，使其能够服务于更广泛的 DeFi 用户。

#### 资金与支持
Cork Protocol 已从多个知名投资者获得资金支持。根据 [Mentibus.xyz 公司简介](https://mentibus.xyz/companies/cork-protocol/) 和新闻报道（如 [CryptoSlate 新闻](https://cryptoslate.com/press-releases/cork-protocol-joins-a16z-cryptos-csx-fall-2024-cohort-with-investor-announcement-and-testnet-trading-competition/)），投资者包括：
- Andreessen Horowitz (a16z)
- Orange DAO
- Founderheads
- IDEO CoLab Ventures
- Unbounded Capital
- Outliers Fund
- Steakhouse Financial

2024 年 9 月 9 日的新闻报道显示，Cork 加入了 a16z Crypto 的 CSX 2024 秋季队列，并通过投资者公告和测试网交易竞赛加速其上市策略。这表明项目在早期阶段已获得强有力的支持。

#### 当前状态与未来计划
截至 2025 年 4 月 18 日，Cork Protocol 处于测试网阶段。根据 [Cork 官方网站](https://www.cork.tech/) 和 X 帖子（例如 [Corkprotocol X 帖子](https://x.com/Corkprotocol/status/1912838592411685275)），当前正在举办交易竞赛，吸引用户参与测试并提供反馈。竞赛旨在为即将到来的主网发布做准备。

#### 团队与透明度
关于团队信息，公开资料中未详细列出具体成员姓名，但 X 帖子提到联合创始人 Philfog（@Philfog），并在讨论中涉及 Resolv 的联合创始人 Iv4n_Ko（@Iv4n_Ko）。合作伙伴包括 Lido、Etherfi 等，显示项目有一定行业认可。

#### 潜在争议与局限
目前，Cork Protocol 尚处于测试网阶段，尚未主网上线，这可能意味着其风险管理工具的实际效果和市场接受度仍需验证。此外，Depeg Swaps 和 Cover Tokens 的复杂性可能对普通用户造成理解和使用障碍。研究表明，DeFi 项目的成功往往依赖于社区采用和监管环境，而这些因素对 Cork 的未来发展可能构成挑战。

#### 总结
Cork Protocol 通过 Depeg Swaps 和 Cover Tokens 提供了一种创新的去锚风险管理工具，填补了 DeFi 生态系统中链上信用市场的风险管理空白。其与 Lido、Etherfi 等项目的合作以及来自 a16z 等投资者的支持显示了其潜力。然而，作为一个仍在测试网阶段的项目，其长期影响和市场接受度仍有待观察。

#### 关键引用
- [Cork Protocol 官方文档 什么是 Cork](https://docs.cork.tech/)
- [Cork 技术网站 DeFi 原语 Depeg Swaps](https://www.cork.tech/)
- [Mentibus.xyz Cork Protocol 公司简介](https://mentibus.xyz/companies/cork-protocol/)
- [CryptoSlate Cork Protocol 加入 a16z Crypto CSX 2024 秋季队列](https://cryptoslate.com/press-releases/cork-protocol-joins-a16z-cryptos-csx-fall-2024-cohort-with-investor-announcement-and-testnet-trading-competition/)