# Assumptions

> The abstractions this model is built on — distinct from [limitations.md](limitations.md)
> (what you cannot conclude) and [decisions.md](decisions.md) (choices with logged
> alternatives). If an assumption below strikes you as wrong, the matching D-number
> is where to argue.

## About people

1. **Adoption is social.** An agent's decision depends on the share of credible
   contacts who already adopted — not on product quality, price, mandates, or
   marketing content. The broadcast channel carries *credibility 0.3*, not arguments. (D3, D8)
2. **Thresholds are stable personal traits** drawn once (Beta + innovator atom),
   not states that campaigns can lower. (D1, D2)
3. **Willingness and ability are independent coin flips** fixed at t=0 — disposition
   is not persuadable and capacity is not fixable within a run. (D5, D6)
4. **Innovators exist**: 2.5% of agents adopt on first awareness, after which they
   never relapse (they need no social proof — measured consequence of D2+D7).
5. People know who in their network adopted, immediately and accurately
   (no misperception, no signaling games).

## About organizations

6. **Influence follows structure**: teams are dense, departments are sticky, silos
   are real, cross-silo ties are scarce and weaker. (D10)
7. **Credibility is relational closeness**: close collaborator 1.0 > own manager 0.7 >
   distant peer 0.6 > central comms 0.3. Hierarchy carries little extra credibility. (D3)
8. The org chart and the influence network are *different graphs* — the divergence is
   the core demonstrative device (spec §2.1).
9. Organizations are static during a rollout: no turnover, no reorgs, no new ties
   forming around the new tool.

## About the process

10. **Time is synchronous rounds** of simultaneous evaluation — everyone "checks"
    at the same abstract cadence. (D7)
11. **Seeds really adopt**: pilot users are committed at t=0 (and get access), though
    they may relapse later under decay. (D9)
12. **A broadcast is one-shot awareness**, not a sustained campaign: its credibility
    term lasts `broadcast_steps` (default 1) and vanishes. (D8)
13. Error bands mean variation **across organizations of the same kind** (full
    regeneration per replicate), not across reruns on one org. (D14)
