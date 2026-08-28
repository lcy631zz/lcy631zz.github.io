---
isDraft: false
title: What's broken in Playable Ad Space?
snippet: So you want to build mini interactive games to get people to download your actual game? Seems simple enough. But having spoken to multiple people in the space, I am convinced that the this is a classic case of a system clogged by perverse incentives and lopsided power structure.
slug: whats-broken-playable-ads-space
author: Rajat Piplewar
category: Musings
readingDuration: 3
pubDate: 2025 6 29
coverAlt: Person Interacting with a Mobile Game Ad
cover: /1-whats-broken-playable-ads-space.jpg
---

# What's broken in Playable Ads Space?

So you want to build mini interactive games to get people to download your actual game? Seems simple enough. But having spoken to multiple people in the space, I am convinced that the this is a classic case of a system clogged by perverse incentives and lopsided power structure.

## How to Guarantee Failure

If you wanted to ensure playable ads were a frustrating, expensive, and rarely successful endeavor, how would you design the system?

- **Make creation agonizingly slow and eye-wateringly expensive** (Months! Thousand dollars per template!) ✓
- **Ensure only a few gatekeepers (ad networks) control the actual distribution** (supply) and charge a king's ransom, often prioritizing their own creations ✓
- **Make it impossible to get reliable data** on why something works or fails beyond "it got shown" or "it didn't" ✓
- **Require specialized, hard-to-find talent** (HTML5 playable devs) that your core game developers despise working on ✓
- **Build tools that only handle the simplest interactions** (tap-only) when core mechanics are more complex (swipe) ✓
- **Ensure that even if you could make them cheaply**, the cost of testing them becomes the next impenetrable wall ✓

It seems the current system is expertly designed not to work efficiently for the average game studio.

## The Incentive Problem

Look where the money flows and who benefits from the current friction.

### Agencies
They benefit from complexity and slow turnaround. $2-3k per template and month-long waits? Wonderful for their business model handled by humans, terrible for the client needing speed and volume.

### Dominant Ad Networks
They control the scarce supply. Why would they want a flood of easily made, cheap playables competing for limited slots and potentially driving down CPMs? They benefit from:
- High barriers to entry
- Minimum spends
- Potentially prioritizing creatives made by their own internal studios where they capture more value

Their incentive is scale and spend on their terms, not necessarily enabling broad, cheap experimentation for everyone.

### The Game Studio
They are stuck. They need better UA, they see potential in playables, but the cost, time, and risk associated with the current process make it prohibitive or limit them to tiny, incremental tests. Their incentive (efficient UA) is directly opposed by the system's structure.

## Bottleneck Succession

Solving one problem just reveals the next, bigger one.

1. **Creation**: It's slow and expensive. Okay, let's imagine Hovi solves this – "one day" creation! Hooray!

2. **Testing Budget**: Publishers immediately points this out. "Testing is also very expensive... if there's another limit that's still blocking... then what is the value?" Even if you can make 100 playables cheaply, you can only afford to test 30-40. The bottleneck shifts.

3. **Ad Network Supply/Cost/Prioritization**: Even with budget, can you get your creatives shown? A large publisher notes only network-produced playables got pickup. Networks control which creatives scale. You might make brilliant playables that never see the light of day or get enough impressions to be statistically valid because the network's algorithm or business model doesn't favor them.

4. **Ideation**: If you solve creation, budget, and supply, a large publisher team still notes: "coming up with ideas to create so many playables, that's not easy." The human creative element becomes the final constraint.

> Focusing only on creation speed is like fixing one leaky pipe in a house where the main water line is fractured. Necessary, but insufficient.

## The "Not Worth My Time" Problem

Studios tried building playables internally. It's outside their core competence (game dev), requires different skills (HTML5/JS, ad tech integration), and engineers find it less rewarding. Marketing teams know they need external help or specialized tools, creating the dependency on agencies or solutions by ad networks.

## Conclusion

The playable ads space is broken because it's a **chain of painful bottlenecks**, each reinforced by misaligned incentives:

- **Creation process**: Slow and expensive, benefiting agencies
- **Distribution (supply)**: Controlled by a few powerful networks who benefit from scarcity and high costs
- **Testing**: Budget-constrained and lacks transparency
- **Talent**: Scarce and misplaced

The result is a system where only the largest players can effectively participate at scale, while smaller studios are locked out or forced into suboptimal compromises.

Solving just the creation piece, while valuable, doesn't fix the fundamental issues of distribution cost, supply limitations, and testing capacity. It's a **Lollapalooza effect** of multiple factors conspiring against the advertiser's core need: efficiently testing many creative ideas to find winners.