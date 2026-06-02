# NBA Salary Efficiency — Decision Log

Every modeling decision documented with rationale, alternatives considered,
and conditions under which the decision should be revisited.

---

## Decision 001 — Year Range
**Date:** 2026-06-02
**Choice:** 2010–present
**Rationale:** Captures the modern NBA era including the three-point revolution
and max contract inflation. Pre-2010 salary structures and playing styles are
structurally different enough to distort cross-era comparisons without
significant additional normalization work.
**Alternatives considered:** 2000–present (adds early 2000s era but introduces
significant pace and style distortion), 2015–present (cleaner era but loses
sample size)
**Revisit if:** Era normalization methodology improves enough to handle pre-2010
data cleanly

---

## Decision 002 — Production Metric Approach
**Date:** 2026-06-02
**Choice:** Win-correlated composite of existing advanced metrics (BPM, VORP,
WS/48, TS%, usage-adjusted stats) rather than a custom proprietary metric
**Rationale:** Existing metrics are peer-reviewed, publicly documented and
defensible. Weights derived empirically by correlating each metric against
team wins — coefficients become the weights. Custom metric is V2 and can be
added as a feature to the existing composite later.
**Alternatives considered:** Custom VOR formula built from scratch, single
metric (VORP only), PER-based ranking
**Tradeoff:** Less proprietary but more credible and faster to build. Custom
metric layer added in V2.
**Revisit if:** Correlation study shows existing metrics have low predictive
power against wins

---

## Decision 003 — Salary Normalization
**Date:** 2026-06-02
**Choice:** Cap-normalize all salaries as percentage of the season salary cap
rather than using raw dollar figures
**Rationale:** Raw salary comparisons across seasons are meaningless due to
cap growth. A $20M contract in 2012 and a $20M contract in 2024 represent
completely different proportions of team spending capacity.
**Alternatives considered:** Inflation-adjusted raw dollars, raw salary with
era flags
**Revisit if:** Never — this is non-negotiable for cross-era comparability

---

## Decision 004 — Availability Score Design
**Date:** 2026-06-02
**Choice:** Separate load management DNPs from injury DNPs. Penalize load
management more heavily than injury in the availability forgiveness modifier.
**Rationale:** A player missing games due to documented injury is a different
organizational risk than a player missing games by choice. Front offices
price these differently when evaluating contracts.
**Formula (draft):**
  availability_pct = games_played / team_games
  playoff_availability_pct = playoff_gp / team_playoff_games
  forgiveness_modifier = weighted penalty scaling down salary % hit,
  with load_management weighted higher than injury
**Alternatives considered:** Flat availability % with no forgiveness, exclude
injury seasons entirely
**Tradeoff:** More nuanced but requires reliable DNP reason tagging from
nba_api — data quality risk to validate during build
**Revisit if:** DNP reason data from nba_api proves unreliable or inconsistent

---

## Decision 005 — Garbage Time Definition
**Date:** 2026-06-02
**Choice:** Tag every player-minute across four buckets:
  1. playoff_non_garbage
  2. regular_season_non_garbage
  3. playoff_garbage
  4. regular_season_garbage
**Garbage time rule:** Score margin > 15 points AND time remaining < 5 minutes
in 4th quarter or OT, OR win probability < 5% / > 95%
**Rationale:** Win probability captures garbage time more accurately than
score + time alone (a 10-point lead with 2 minutes left is effectively over).
Separating playoff from regular season preserves the higher value of playoff
minutes in downstream weighting.
**Alternatives considered:** Score + time only (simpler but less accurate),
single garbage time flag without playoff split
**Revisit if:** Win probability data proves unavailable or inconsistent in
nba_api play-by-play — fall back to score + time rule only

---

## Decision 006 — Playoff Weighting
**Date:** 2026-06-02
**Choice:** Playoff production treated as a separate dimension layered on top
of the base composite — not baked into the core surplus value calculation.
Playoff layer feeds the organizational value framing (V1b).
**Rationale:** Embedding playoff weighting directly into the base metric
disadvantages players on consistently bad teams through no fault of their own.
Keeping it as a separate layer allows both views: pure production and
org-value-adjusted production.
**Alternatives considered:** 10x playoff multiplier baked in (rejected —
too aggressive, no empirical support), 2-3x multiplier as tunable parameter
**Revisit if:** Correlation testing shows playoff production is a stronger
win predictor than regular season production at the team level

---

## Decision 007 — Minimum Inclusion Threshold
**Date:** 2026-06-02
**Choice:** No hard minimum games threshold. Availability handled via the
forgiveness modifier rather than exclusion. Injury-shortened seasons flagged
with a boolean column (injury_shortened_season = True) for sensitivity
analysis.
**Rationale:** A player on a max contract who plays 39 games is a meaningful
data point — the salary obligation doesn't change. Excluding low-game seasons
would mask exactly the overpaid signal the model is designed to surface.
**Alternatives considered:** 41 game minimum (standard in literature),
20 MPG minimum
**Tradeoff:** More noise in the cluster output from extreme outliers — managed
by the forgiveness modifier and the injury flag rather than exclusion
**Revisit if:** Cluster output shows extreme distortion from very low sample
player-seasons

---

## Decision 008 — Data Sources
**Date:** 2026-06-02
**Choice:** nba_api for player stats and game logs. Basketball Reference for
advanced metrics (BPM, VORP, WS/48). HoopsHype or Basketball Reference for
historical salary cap figures. Spotrac or Basketball Reference for player
salaries. Reconciled on player_id + season as primary key.
**Rationale:** nba_api is official and structured. Basketball Reference has
the deepest historical advanced metric coverage. No single source covers
all required fields cleanly.
**Alternatives considered:** nba_api only (missing advanced metrics),
Basketball Reference only (scraping fragility risk)
**Tradeoff:** Multi-source pipeline introduces reconciliation complexity —
name mismatches and player ID conflicts must be handled explicitly
**Revisit if:** A cleaner unified API becomes available with full historical
advanced metric coverage

---

## Decision 009 — Storage Format
**Date:** 2026-06-02
**Choice:** CSV files at each major transformation step. No database.
**Rationale:** Fully portable, inspectable, shareable and sufficient for
this data volume. Database overhead adds complexity with no benefit at this
scale.
**Alternatives considered:** SQLite, Postgres, cloud database
**Revisit if:** Data volume or multi-user access requirements change

---

## Decision 010 — Era Normalization
**Date:** 2026-06-02
**Choice:** Z-score normalize composite scores within each season before
making cross-era comparisons
**Rationale:** Pace has increased significantly since 2010, inflating
counting-stat-based metrics league-wide. Within-season normalization ensures
a player ranked in the 90th percentile in 2012 is comparable to a player
ranked in the 90th percentile in 2024.
**Alternatives considered:** Raw composite scores with era flags, percentile
ranks only
**Revisit if:** Never for cross-era comparisons — normalization is required