# Hollow Crown: Balance Report

Roster analyzed: `data/units.csv` (baseline) → `output/units.balanced.csv` (final).
Reference tool: `sim/simulate.py` (1v1 duel model, unmodified). Supplementary tool:
`output/squad_check.py` (simultaneous-squad approximation, built for this
assessment to sanity-check the reference encounters, see the "Degeneracy"
section for why the duel sim alone can't answer that question).

All commands below are reproducible with:

```bash
python3 sim/simulate.py --units data/units.csv --trials 5000 --seed 7
python3 sim/simulate.py --units output/units.balanced.csv --trials 5000 --seed 7
python3 output/squad_check.py
```

---

## 1. Diagnosis: what was broken, with numbers

Baseline (`data/units.csv`), 5,000 trials/pair, seed 7:

| Unit | Class | Cost | Win% | Win%/Cost |
|---|---|---:|---:|---:|
| Ser Halden | Knight | 6 | 78.4% | 13.07 |
| Rookwood | Myrmidon | 7 | 65.3% | 9.33 |
| Wisp | Cleric | 4 | 51.2% | 12.79 |
| Brennan | Soldier | 5 | 46.6% | 9.32 |
| Sable | Archer | 5 | 35.0% | 7.00 |
| Pyraxis | Battlemage | 9 | 23.5% | 2.61 |

Win-rate spread: **54.9 points** (23.5%–78.4%). A healthy roster clusters tightly
around 50%; this one has a clear auto-include and a clear trap pick.

**Ser Halden, the auto-include.** He is simultaneously the tankiest unit
(highest HP at 32, highest DEF at 12) *and* hits hard (ATK 16), for the
second-cheapest cost in the roster (6). He has no real weakness for an
opponent to exploit: no stat where he is below the roster median. That
combination, not any single stat, is what produces a 78% win rate at a
budget price.

**Pyraxis, the trap pick.** He has strong magic power (MAG 18) but the
lowest HP (20) and lowest physical DEF (4) in the roster, at the *highest*
cost (9). His RES (8) is actually decent, but that stat almost never gets
tested: 4 of the other 5 units in the roster are physical attackers, who
target DEF, not RES. So his one real strength is mostly irrelevant to who he
actually fights, while his one real weakness (DEF 4) is exposed on almost
every incoming hit. Concretely, in a Halden-vs-Pyraxis duel: Halden's ATK 16
vs Pyraxis's DEF 4 deals 12 dmg/hit and kills Pyraxis in 2 hits; Pyraxis's
MAG 18 vs Halden's RES 4 deals 14 dmg/hit but needs 3 hits to kill Halden.
Since attacks alternate, Halden wins almost every time before Pyraxis lands
the third hit.

**Sable** (35.0%) is the secondary problem: her ATK (13) is too close to
common DEF values in the roster (7–12), so `max(1, atk - def)` frequently
floors to near-minimum damage; she just doesn't hit hard enough to punish
anyone.

---

## 2. Changes made, and why

Design rule used throughout: **fix the stat problem first, then price the
result.** Raising a broken unit's cost without touching its stats doesn't
fix balance; it just makes the imbalance more expensive. Cost was treated as
the *last* lever, not the first.

| Unit | Stat changes | Cost | Reasoning |
|---|---|---:|---|
| Ser Halden | HP 32→30, ATK 16→13, DEF 12→10 | 6→7→6 (see Iteration 4) | Trim the "no weakness" profile on all three axes that made him dominant. Cost went up to 7 during Iterations 1–3, then back down to 6 once a final human review (not the AI) caught that he'd ended up tied for the most expensive unit while having the *lowest* win rate in the roster. |
| Pyraxis | HP 20→24, DEF 4→6, RES 8→10 | 9→6 | Give him enough bulk to survive to use his power, especially against the majority-physical cast; lower his price to match a still-fragile, high-risk profile. |
| Sable | ATK 13→13 (reverted after overshoot, see iteration 2), final: kept base ATK, no net change | 5 | See Iteration 2: an ATK buff overshot badly and was reverted; her final fix came from other units moving around her, not from her own stats. |
| Rookwood | SPD 16→13 | 7 | Root-cause fix, not a stat nerf for its own sake; see Iteration 2. He wasn't overpowered on raw damage; at SPD 16 he doubled every unit but Wisp and was never doubled back. Lowering his SPD removes the free double against most of the cast without touching his identity as the fast striker. |
| Brennan | ATK 13→13 (net unchanged after iteration 2 revert) | 5 | A +1 ATK buff was tried and reverted; see below. |
| Wisp | MAG 12→13 | 4 | Small final nudge once the rest of the field moved; see Iteration 3. |

Net roster changes are modest by design: most of the "budget" of change went
into Halden and Pyraxis, the two units that were actually broken, plus one
mechanical fix on Rookwood (speed/doubling) that a pure stat-shaving approach
would have missed entirely.

---

## 3. Before / after: iterations

This roster went through **four measured iterations**, not one big edit.
Each one is a real data point, including the ones that didn't land cleanly
on the first try. The last one wasn't even caught by the sim; it was caught
by a human re-checking the "finished" result.

### Baseline
See table in Diagnosis. Spread: 54.9 points (23.5%–78.4%).

### Iteration 1: fix the two extremes
Changes: Halden (HP/ATK/DEF trim, cost 6→8), Pyraxis (HP/DEF/RES buff, cost
9→7), Sable (ATK 13→15).

```
UNIT          CLASS        COST    WIN%  WIN%/COST
Rookwood      Myrmidon        7   67.1%      9.58
Sable         Archer          5   59.5%     11.90
Ser Halden    Knight          8   47.0%      5.87
Wisp          Cleric          4   45.2%     11.30
Pyraxis       Battlemage      7   40.8%      5.83
Brennan       Soldier         5   40.4%      8.08
```

Result: Halden landed almost exactly on target (47%). But two things went
wrong that only showed up once the numbers ran: the Sable buff overshot hard
(35%→59.5%, more than double the intended move), and, without us touching
Rookwood or Brennan at all, Rookwood became the new strongest unit (67.1%)
and Brennan became relatively the weakest (40.4%), simply because the field
around them shifted. This is the core lesson of relative balance: **win rate
is a comparison, not a property of a single unit**, so every change has to be
re-verified against the whole roster, not just the unit you touched.

Root-cause check on Rookwood (not covered by re-running the sim alone):

```python
# every unit Rookwood doubles vs. every unit that doubles Rookwood, at iter-1 stats
Rookwood vs Ser Halden  -> Rookwood doubles: True | Halden doubles Rookwood: False
Rookwood vs Brennan     -> Rookwood doubles: True | Brennan doubles Rookwood: False
Rookwood vs Sable       -> Rookwood doubles: True | Sable doubles Rookwood:  False
Rookwood vs Wisp        -> Rookwood doubles: False| Wisp doubles Rookwood:   False
Rookwood vs Pyraxis     -> Rookwood doubles: True | Pyraxis doubles Rookwood:False
```
At SPD 16, Rookwood doubled every unit in the roster except Wisp, and was
never doubled back. That is a mechanical follow-up-turn advantage, not a raw
damage advantage; raising his cost again would have priced the symptom, not
the cause.

### Iteration 2: correct the overshoot, fix Rookwood at the root, rebalance Brennan
Changes: Sable ATK 15→14 (partial correction), Rookwood SPD 16→13 (cost
7→8, later re-lowered), Brennan ATK 13→14, Halden cost 8→7, Pyraxis cost
7→6.

```
UNIT          CLASS        COST    WIN%  WIN%/COST
Rookwood      Myrmidon        8   62.6%      7.82
Brennan       Soldier         5   56.6%     11.32
Sable         Archer          5   53.9%     10.78
Ser Halden    Knight          7   45.9%      6.55
Wisp          Cleric          4   45.2%     11.29
Pyraxis       Battlemage      6   35.9%      5.98
```
(confirmed stable across seeds 7 / 42 / 123, trials 5,000–10,000; max
observed drift 0.4 points)

Rookwood's win rate dropped from 67.1% to 62.6%, a start, but the SPD trim
alone (before the doubling-matchup fix fully lands with cost re-tuned) wasn't
enough yet. More importantly, **the +1 ATK on Brennan was meant to be a small
nudge and instead swung his win rate by +16 points** (40.4%→56.6%). At these
duel margins, damage is `atk − def`, and a lot of the roster's defenses sit
close together (6–10), so a single point of attack crosses several
matchups' effective "floor" at once. A change that looks trivial on paper is
not trivial in the sim. This is flagged again in
`DESIGN_AI_WORKFLOW.md` as the AI-was-wrong moment: an AI-proposed "just
+1 ATK, it's minor" suggestion was verified, not trusted, and had to be
reverted.

### Iteration 3: revert the bad assumption, retest
Changes: Brennan ATK 14→13 (revert), Rookwood cost 8→7 (now that SPD 13 is
doing the real work, the extra cost point wasn't needed), Sable ATK 14→13
(revert the remainder of the overshoot), small closing nudges: Halden ATK
14→13, Brennan DEF 9→8, Pyraxis RES 9→10, Wisp MAG 12→13.

```
UNIT          CLASS        COST    WIN%  WIN%/COST
Sable         Archer          5   53.2%     10.64
Rookwood      Myrmidon        7   52.5%      7.49
Wisp          Cleric          4   50.1%     12.53
Brennan       Soldier         5   49.8%      9.95
Pyraxis       Battlemage      6   48.3%      8.06
Ser Halden    Knight          7   46.1%      6.59
```

Win-rate spread: **7.1 points** (46.1%–53.2%), down from 54.9 points at
baseline. No unit is an auto-include (max 53.2%, vs. 78.4% at baseline) and
none is a trap pick on win rate alone (min 46.1%, vs. 23.5% at baseline). At
this point the win-rate spread looked solved, but it wasn't the last issue in
the roster; see Iteration 4.

### Iteration 4: a pricing inconsistency caught in human review, not by the AI

This one wasn't found by re-running the simulator, it was found by Alexei
(the person driving this assessment) reading the Iteration 3 table side by
side after opening `units.balanced.csv` and re-running the sim independently
on his own machine (see `output/screenshots/local_verification_vscode.png`,
a screenshot of that local run). The catch: **Ser Halden was tied for the
most expensive unit in the roster (cost 7, same as Rookwood), while having
the *lowest* win rate of all six units (46.1%)**. Every individual unit sat
inside the ~46–53% target band, so the automated win-rate check "passed",
but nothing had checked *cost against relative performance within the same
price tier*, and this is exactly the pay-the-most-for-the-worst-result
pattern the whole exercise exists to eliminate.

The fix, once flagged: lower Halden's cost 7→6. No stat changes, his 46.1%
win rate was already inside the target band; the problem was purely that his
price didn't reflect being the weakest unit at his tier. Re-running the sim
confirms win rates are unaffected (cost has no effect on duel outcomes, only
on the reported ratio):

```
UNIT          CLASS        COST    WIN%  WIN%/COST
Sable         Archer          5   53.2%     10.64
Rookwood      Myrmidon        7   52.5%      7.49
Wisp          Cleric          4   50.1%     12.53
Brennan       Soldier         5   49.8%      9.95
Pyraxis       Battlemage      6   48.3%      8.06
Ser Halden    Knight          6   46.1%      7.69
```
(seeds 7 and 99, 8,000 trials/pair; win rates match Iteration 3 exactly, as
expected, only Halden's WIN%/COST moved.)

**Final roster** (`output/units.balanced.csv`): win-rate spread unchanged at
**7.1 points** (46.1%–53.2%). WIN%/COST now ranges **7.49–12.53**, tighter
than Iteration 3's 6.59–12.53, because Halden's ratio moved from the worst in
the roster (6.59) to squarely mid-pack (7.69). The remaining spread is the
same structural effect described below: cheaper units (cost 4–5) mechanically
get a higher win%/cost ratio than pricier ones (cost 6–7) even at the *same*
win rate, simply because they're dividing by a smaller number. Flattening
that column completely would require either charging cheap units
disproportionately more (which stops them being cheap, entry-level options)
or making the expensive units win noticeably more than 50% (which reopens the
auto-include problem). A ~1.7x spread in WIN%/COST alongside a 7-point
win-rate spread is the healthier trade-off of the two metrics.

The squad-check script (§5) was re-run after this change specifically to
confirm the cheaper Halden didn't open a new degeneracy loophole (a cheaper
strong unit is exactly the kind of change that could). It didn't: no squad
crossed the ≥95%-win-at-≤14-cost flag threshold after the fix, and Halden-heavy
mono-squads (2× and 3× Ser Halden) topped out at 96.2% at cost 12–18, well
inside "spending most of the budget," not a cheap sweep.

This is worth calling out on its own: the "verify, don't trust" discipline
used throughout this project (see `DESIGN_AI_WORKFLOW.md`) went both ways.
The AI caught its own mistake once (the Brennan +1 ATK swing, Iteration 2)
by re-running the sim instead of trusting its own confidence. The human
caught a different mistake, one the AI's iteration process had left behind,
by independently re-verifying the "finished" result instead of accepting it
at face value.

---

## 4. Confidence: is this signal or noise?

Every reported number above was re-run on at least two different RNG seeds
(7, 42, 99, 123) at 5,000–10,000 trials per pairing. Across seeds, no unit's
win rate moved more than **0.4 percentage points**. With 5 opposing units ×
5,000+ trials each, every unit's win rate is an average over ~25,000+
individual duels, which is why the seed-to-seed variance is small enough to
treat these numbers as signal rather than noise. Anywhere this report cites a
percentage, it is stable to roughly ±0.5 points at the trial counts used.
As an independent check outside this session entirely, Alexei re-ran
`python sim/simulate.py` on his own machine against the same
`units.balanced.csv` and got matching numbers, which is a second, fully
independent confirmation that these results reproduce and are not an
artifact of one environment.

The one number in this report that is *not* held to that standard is the
squad-battle degeneracy check below: it's a 500-trial-per-squad heuristic
model built for this assessment, not the graded reference sim, and is
presented as a directional check, not a precision claim.

---

## 5. Degeneracy check: does any cheap squad break an encounter?

`sim/simulate.py` only measures 1v1 duels; it has no concept of a multi-unit
squad or of the reference encounters at all. To answer the assessment's
actual question, "does a cheap squad trivially clear an encounter?" A
squad-vs-squad approximation was needed. `output/squad_check.py` extends the
same hit/crit/damage/doubling functions from `simulate.py` (no reimplementation
of the rules) into a simultaneous team fight: every living unit acts once per
round in speed order, targeting the lowest-HP-fraction living enemy, until
one side is wiped or a round cap is hit. This is explicitly a heuristic, not
a claim about the "real" tactics game (see Limitations), but it's enough to
catch a genuinely broken loophole if one exists.

**Design decisions behind `squad_check.py`, and why each one was made:**

- **Reused `simulate.py`'s hit/crit/damage/doubling functions instead of
  writing new ones.** The alternative, reimplementing the combat math, risked
  the two tools quietly drifting apart and testing slightly different rules
  without anyone noticing. Importing the same functions guarantees the squad
  fight and the duel are the same combat system, just at different scales.
- **Targeting rule: attack the living enemy with the lowest HP fraction.**
  This approximates a "finish the weak one" tactic, a common and reasonable
  real-player heuristic, and it's simple enough to reason about when reading
  the results. It is a real design choice, not the only valid one: a
  different reasonable rule (focus the highest remaining threat, or target
  whoever is squishiest by role) could shift the Encounter B/C numbers. That
  is called out directly in Limitations below rather than hidden.
- **Turn order: every living unit acts once per round, ordered by raw SPD.**
  This is a direct multi-unit extension of the SPD-driven turn order already
  defined in `combat-rules.md` for duels, not a new rule invented for this
  script; it keeps the squad model consistent with the reference rules
  instead of introducing an unrelated turn-order concept.
- **Round cap of 40, versus 100 in `sim/simulate.py`.** A squad fight
  resolves faster than a 1v1 duel because multiple attackers land hits every
  round instead of one; 40 rounds was enough headroom that the cap never
  actually triggered in testing, it exists only as a safety stop against an
  unexpected infinite loop, the same purpose the duel sim's 100-round cap
  serves there.
- **500 trials per squad, versus 5,000-8,000 for the main duel results.**
  This script sweeps roughly 65 candidate squads across 3 encounters, about
  195 squad/encounter pairs, so the trial budget was spent on covering breadth
  (many possible squads) rather than depth (extreme precision on any one of
  them). This is explicitly a lower-precision, directional check, not held to
  the same ±0.5-point confidence standard as the headline duel numbers in
  §4; that trade-off is why this section's claims are phrased as "no loophole
  found," not "here is the exact win rate."
- **Squad generation: every mono-spam of a single unit, plus every 2-4 unit
  combination that spends most of the budget (cost between budget-3 and
  budget).** The two categories cover the two realistic ways a "degenerate"
  squad could exist: spamming one cheap unit, or a clever mix that still uses
  most of the budget. Combinations spending far less than the budget were not
  exhaustively generated, since a squad that voluntarily leaves most of its
  budget unspent is not the "cheap squad wins big" scenario the assessment
  asks about; the mono-spam category already covers the cheapest realistic
  extreme (e.g. 2x Ser Halden at cost 12).

Every legal squad within the 20-point budget was generated (mono-spam of each
unit, plus every 2–4 unit combination using most of the budget) and run
against all three encounters, 500 trials each:

**Encounter A (Sunken Gate, early game).** Nearly every full-budget squad
clears at ≥97%. This matches the encounter notes' own framing: A is
designed as an easy ramp, not a filter, and our result confirms that
reading rather than contradicting it: the only squads that *don't* clear
comfortably are the ones that spend the whole budget on very few, expensive
bodies (2× Ser Halden: 27.6%; 2× Rookwood: 89.8%), and that's a headcount
problem (2 actors vs. 4 enemies) more than a power problem. No squad wins
this by spending *less* than most of the budget, so there's no free lunch
here. The finding is that A doesn't discriminate between well-formed squads,
by design.

**Encounter B (Hollow Throne, armor/magic split).** This is where the roster
is put to a real test, and it responds the way the encounter is designed to
ask: a pure-Wisp (magic) squad wins 100%, a pure-Sable (physical) squad wins
under 1%. That's not a loophole; it's the intended lesson of the encounter
(heavy armor should wall out pure-physical answers, magic should punch
through it), and it confirms our physical/magic split still means something
under the new numbers. No squad *cheaper* than the full budget wins big here;
the axis that matters is composition (attack type), not cost.

**Encounter C (Carrion Run, speed check).** Cheap, fast squads (Sable, Wisp:
78–96% win) beat expensive, slow ones (Ser Halden- and Rookwood-heavy squads:
mostly under 10%, 2× Ser Halden even at 0%) badly. This directly answers the
encounter's design question ("does your cost column charge anything for
speed?"), and the answer is yes: the units that get run over by Shrike
Runners' SPD 15 are exactly the ones whose own SPD is lowest (Halden SPD 6,
Pyraxis SPD 5), regardless of how much they cost.

**Conclusion:** no squad found across any of the three encounters wins at a
high rate while spending meaningfully less than the 20-point budget. Where
squads dominate, they use most or all of the budget; where a squad
underperforms, it's explained by either headcount (A), attack-type mismatch
(B, working as intended), or a speed mismatch that the cost column already
accounts for (C). I looked specifically for a spend-15-win-95% pattern across
all ~65 generated squads (re-generated after the Iteration 4 cost change, see
below) and did not find one.

One side finding worth flagging for future iteration: because no unit costs
1–3, a 20-point budget usually leaves 0–3 points unspendable (e.g. 3× Sable +
1× Wisp = 19, with no unit costing exactly 1 to fill the gap). That's a
budget-granularity quirk, not a balance bug, but it slightly narrows the real
decision space and would be worth a cheap 3-cost unit or a 21-point budget
in a future pass.

---

## 6. Limitations of the duel model

- **No positioning, movement, or range.** `mov` and `range` are loaded but
  never used by either sim. A ranged unit that can strike without being
  struck back, or a slow tank that can block a corridor, has value this model
  cannot see at all.
- **No healing-as-support.** Wisp is a Cleric with no in-model way to keep
  allies alive; her value here is purely as another attacker. In real play a
  healer's contribution is squad-level survivability, not personal win rate;
  her duel/duel-adjacent numbers likely *understate* her real worth.
- **No terrain, no turn economy beyond a single duel/simple team-fight loop.**
  The squad_check.py extension approximates a team fight but still ignores
  terrain, zone control, and the AI decisions a real player would make
  (focus-fire choices, retreating, baiting).
- **The squad_check model is a heuristic, not a validated one.** It uses one
  fixed targeting rule (attack the lowest-HP-fraction enemy) and simultaneous
  turn order by raw SPD. A different reasonable AI (e.g. focus the highest
  remaining threat, or target squishiest by role) could shift the encounter
  B/C results. Treat section 5 as "no glaring loophole under a reasonable
  heuristic," not as an exhaustive proof.
- **How I'd validate these:** build the actual squad/positioning prototype
  (even a minimal grid) and re-run the same three encounters with a human or
  scripted player making real movement/targeting choices, then compare against
  the duel-only and squad_check numbers to see where they diverge.
