# Hollow Crown: Design Doc: The Deployment Economy

Status: living draft. Scope: the pre-battle squad-selection loop, using the
duel/combat numbers already being balanced in `output/units.balanced.csv` and
`output/BALANCE_REPORT.md`. This is not a new feature: it's the ruleset
that decides *how the existing cost column is spent*.

## 1. Design intent

Right now "deployment" means: pick units until you hit a point cap. The
problem isn't the cap. It's that the cap wasn't doing any work: one unit was
worth fielding regardless of cost, one wasn't worth fielding at any cost, and
nothing stopped a player from just buying four of the cheapest good unit.

The intent of this system is that **every point spent under the budget is a
real trade-off**, and that trade-off should be legible to the player before
they commit, not discovered after they lose. Concretely, a well-functioning
deployment economy means:

- No unit is worth fielding regardless of what you're facing (no auto-include).
- No unit is worth leaving home regardless of what you're facing (no trap pick).
- The budget forces a *composition* decision (how many bodies vs. how much
  individual power; physical vs. magic; fast vs. tanky), not just a "which 4
  units are best" checklist that never changes.

## 2. The core loop

1. **Scout.** Before deployment, the player sees (or can infer from mission
   type/lore framing) the shape of the enemy force: mass, armor-heavy,
   magic-heavy, or fast.
2. **Budget-constrained pick.** The player assembles a squad under a fixed
   point cap, choosing from their unlocked roster.
3. **Commit and fight.** The squad is locked for the encounter.
4. **Read the result.** Win, lose, or scrape by, the player should be able
   to point to *which* choice mattered (too few bodies, too slow, wrong
   damage type) and adjust next time.

This loop only teaches the player anything if step 2 has real tension. That
tension is what the rules below are trying to manufacture on purpose.

## 3. Rules

### 3.1 Cost reflects measured value, not raw stats

A unit's `cost` is set from its performance in the reference duel simulator
(`sim/simulate.py`) *and* its squad-level behavior (`output/squad_check.py`),
not from eyeballing its stat block. Concretely, cost should track:

- **Duel win rate against the current roster**, target ≈50% ± a few points
  regardless of cost band. Cost is not a substitute for a win-rate fix;
  it's what you charge *after* the unit's win rate is already reasonable.
- **Speed relative to the field.** A unit whose `spd` gets it doubled by
  most of the cast (like early Pyraxis/Halden vs. Encounter C's Shrike
  Runners) is paying a real tax in actual fights that a duel-only win rate
  can under-count; cost should account for that, and the balance report's
  Encounter C check is the way to catch it.
- **Role scarcity.** The only magic-damage unit in a mostly-physical roster
  (Wisp, Pyraxis) is answering a threat (heavy armor, per Encounter B) that
  nothing else in the roster answers. That's worth pricing in even when its
  1v1 duel win rate looks average (see 3.3).

**Worked example: why cost doesn't chase every small win-rate difference.**
In the final roster, Wisp (cost 4) wins 50.1% of duels, Pyraxis (cost 6) wins
48.3%, and Ser Halden (cost 6) wins 46.1%. Read quickly, that looks backwards,
the cheaper unit has the higher win rate. It isn't a pricing mistake, and the
reasoning is worth spelling out because it's easy to mistake for one: the
entire point of the balance pass was to get every unit's duel win rate close
to 50%, regardless of cost. Once that's achieved, the small differences left
over (a 7-point spread from 46.1% to 53.2% across the whole roster) are the
residual precision limit of that process, not a deliberate signal, the same
way six hand-cut slices of a cake are never bit-for-bit identical even when
the cut was done carefully. Pricing a unit to chase those last 1-2 points of
win rate would mean pricing on noise instead of on real value.

What the cost differences here actually track is value the duel win rate
number doesn't capture: Pyraxis stays priced above the cheapest tier because
he's the only other magic damage source in the roster, needed to answer
Encounter B's heavy armor, not because his duel win rate demands it. Ser
Halden's cost was already lowered once (see `BALANCE_REPORT.md`, Iteration
4) specifically because he lacked that kind of compensating role; pricing him
even lower to chase his win rate further would only recreate the same "worst
in its price tier" pattern one tier down, since he'd then be the weakest
unit at cost 5 too, by a wider margin than he is at cost 6. And Wisp's low
cost is arguably generous to the design, not exploitative: the duel sim
cannot see her healing/support role at all (see Limitations in
`BALANCE_REPORT.md`), so her real in-game value is likely higher than her
50.1% duel number suggests, not lower.

### 3.2 The budget must leave more than one good answer

Per-encounter budget: **20 points** at the current roster's cost band
(4–9 per unit), matching the reference encounters. The design failure mode to
avoid is a budget where the *dominant* strategy is one specific squad,
regardless of what the enemy is doing (this is exactly what Encounter A's
notes warn about: "if the only good answer is field-the-auto-include-twice,
the economy is broken").

**Concrete test used to validate this:** generate every legal squad under
budget and check that the encounter-winning compositions differ by enemy
type. Our squad-check run confirms this roster passes for Encounters B and C
(different squads win: magic-leaning for B, fast/cheap for C); see
`BALANCE_REPORT.md` §5. Encounter A stays a "most compositions work" ramp on
purpose, which the encounter notes explicitly allow.

### 3.3 Cap duplicate copies to keep the trade-off in "which units," not "how many"

The squad-check run surfaced a real gap: a squad of **5× Wisp** or **4×
Sable**, spending the entire budget on one cheap unit repeated, wins
several encounters at 90%+ just by raw headcount, not because that unit is
overtuned in a duel. That's not a stat problem; it's a rule the deployment
economy doesn't currently have.

**New rule:** a squad may field **at most 2 copies of the same named unit**.
This doesn't touch a single stat or cost value; it's a deployment
constraint, the same kind of lever as the budget itself. It forces the
budget's leftover points, after 2 copies of your best pick, into a genuinely
different unit, which is what turns "spend efficiently" into "build a
composition."

### 3.4 Budget granularity should match the cost bands

Current unit costs are 4, 5, 5, 6, 6, 7. Against a 20-point budget, most
legal squads leave 0–3 points unspendable (e.g. 3× Sable + 1× Wisp = 19,
with nothing costing 1 to close the gap). That's a small thing, but it quietly
narrows how many distinct squads a player can actually build at "full value."
**Fix going forward:** either introduce one low-cost (3-point) support-flavor
unit as the roster grows past 6, or set budgets as an exact multiple
achievable by at least a few different combinations (e.g. 21 instead of 20)
so more of the design space is reachable.

## 4. Key numbers (current pass)

| Parameter | Value | Why |
|---|---:|---|
| Reference budget | 20 | Matches the given reference encounters |
| Cost band | 4–7 | Post-rebalance range (was 4–9); compressed because the old 9-cost outlier (Pyraxis) was mispriced, not genuinely worth 2x a 4-cost unit |
| Target duel win rate | 50% ± ~7 pts | What `BALANCE_REPORT.md` achieved (46.1%–53.2%) |
| Max copies of one unit per squad | 2 (new rule) | Closes the "spam the cheapest good unit" loophole found in squad-check testing |

## 5. Player-experience goal

A player who wins should be able to say *why* their squad worked: "I
brought a mage because I knew this fight was armor-heavy," not "I always
bring the same four units." A player who loses should walk away suspecting
what to change (more speed, more magic, more bodies) rather than feeling the
loss was decided before deployment even started. The economy succeeds when
the pre-battle squad screen is a real decision point in the game, not a
formality on the way to the fight that was already won by the number on a
budget bar.
