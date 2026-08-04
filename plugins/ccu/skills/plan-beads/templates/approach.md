# Approach: <Feature Name>

## Gap Analysis

| Component | Have | Need | Gap |
| --------- | ---- | ---- | --- |
| ...       | ...  | ...  | ... |

## Recommended Approach

<Description>

### Alternative Approaches

1. <Option A> - Tradeoff: ...
2. <Option B> - Tradeoff: ...

## Risk Map

Risk ratings are annotations that flag novelty for workers — there is no separate verification phase. HIGH-risk components surface as `⚠ HIGH RISK` annotations in their beads with explicit "investigate before coding" guidance.

| Component   | Risk | Reason           | Worker Guidance                                       |
| ----------- | ---- | ---------------- | ----------------------------------------------------- |
| Stripe SDK  | HIGH | New external dep | Read SDK docs + validate signature flow before coding |
| User entity | LOW  | Follows existing | Proceed using established pattern                      |
