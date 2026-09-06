# Design AI Workflow

**Time spent:** 3-4 hours total, across reading the assessment and the given
rules, working through the balance pass with Claude, and independently
verifying the results on my own machine.

## Tool used

**Claude** (Anthropic's assistant, used conversationally in a session with
shell and file access), used as an active design partner throughout the
whole process, not for prose polishing at the end, but for diagnosis,
proposing numbers, extending the simulator, and catching mistakes in real
time. The reason for this tool over a plain chatbot: it could actually run
`sim/simulate.py`, read the CSVs, and re-verify every claim against real
output in the same turn it was proposed, instead of me copy-pasting numbers
back and forth.

## How I actually worked with it

This wasn't a "paste the assignment, get an answer back" exchange. I gave
Claude the GitHub link to this repo and had it use its Chrome extension to
open and read the assessment page directly, rather than me copy-pasting the
instructions in by hand. Once we'd gone through the diagnosis and the
balance passes together in the chat, I had Claude package the whole project
(the original data, the sim, and everything we'd produced) and copy it
directly onto my own computer, into a Downloads folder that I explicitly
authorized it to write to, so I had a real local copy to check, not just
Claude's word for it.

From there I opened the project myself in VS Code and read through the
code and the CSVs on my own. Where I didn't follow something (how hit chance
is calculated, why a magic attacker still needs physical defense, why a
one-point stat change swung a win rate by 16 points), I asked Claude to
explain it again, deliberately in plain, non-technical language, the kind of
explanation you'd give a teenager with no game-design or programming
background, specifically so I could confirm I actually understood the
mechanics well enough to defend them myself, instead of approving numbers I
didn't really follow. That back-and-forth (read it myself, then ask for a
plain-language walkthrough of the part I wasn't sure about) is most of what
this document is actually describing, not just the five prompts below.

## Concrete prompts and what they produced

1. **"Diagnose why Ser Halden is an auto-include and Pyraxis is a trap pick,
   using the sim's own numbers, and explain it simply."**
   Produced a stat-by-stat read of both units (Halden has no weak stat at a
   below-median cost; Pyraxis's one strength, RES, is irrelevant against a
   mostly-physical roster) plus a worked duel example (Halden kills Pyraxis
   in 2 hits, Pyraxis needs 3 to return the favor) that made the mechanism
   concrete instead of just citing the win-rate gap.

2. **"Propose a first round of stat and cost changes for Halden and Pyraxis:
   fix stats first, then price the result, not the other way round."**
   Produced the Iteration 1 proposal (Halden HP/ATK/DEF trimmed + cost up;
   Pyraxis HP/DEF/RES buffed + cost down) with the reasoning for the
   "stats-then-cost" ordering, which became the standing rule for every
   later change.

3. **"Rookwood is still the strongest unit two iterations in a row and we
   haven't touched him, find out why instead of just nerfing him again."**
   This is the prompt that mattered most. Instead of guessing another stat
   nerf, it wrote a small script against the sim's own `doubles()` function
   and found that Rookwood's SPD 16 let him double-attack every unit but one
   and never be doubled back, a mechanical follow-up-turn advantage, not a
   raw-damage one. The actual fix (SPD 16→13) came from that diagnosis, not
   from another round of "reduce a stat and see what happens."

4. **"Extend the simulator to check whether any squad under the 20-point
   budget trivially wins one of the three reference encounters, the duel
   sim can't answer that on its own."**
   Produced `output/squad_check.py`, a simultaneous team-fight approximation
   built on top of the *same* hit/crit/damage/doubling functions already in
   `sim/simulate.py` (reused, not reimplemented), plus a sweep over ~60 legal
   squad combinations against all three encounters. This is also what
   surfaced the "5× Wisp / 4× Sable spam nearly always wins" finding that
   went into the GDD as a new deployment rule (max 2 copies per unit).

5. **"Draft the GDD for the deployment economy, scoped to what we actually
   found, not a generic pricing essay."**
   Produced `GDD.md`, including the duplicate-cap rule and the budget-
   granularity note, both of which came directly from the squad-check
   results in step 4 rather than from general game-design theory.

## Where the AI was wrong, and how it was caught

During Iteration 2, I asked for a small nudge to bring Brennan's win rate up
after it had drifted down (as a side effect of other units changing). The
proposal was "+1 ATK, that's a minor adjustment." It was framed, and I
initially accepted it, as low-risk. Re-running the sim immediately after
showed Brennan's win rate jump from 40.4% to 56.6%, a 16-point swing from a
single stat point, turning an underperforming unit into one of the
strongest in one move. The mistake was treating "+1" as inherently small
without accounting for how thin the actual damage margins are in this system
(`dmg = max(1, atk − def)`, with most DEF values clustered in a narrow 6–10
band): a single point can cross several units' effective damage floor at
once. The fix wasn't to reason more carefully about *why* it was wrong in the
abstract; it was to trust the simulator's output over the proposal's own
confidence, revert the change in the next iteration, and re-verify. That
distrust-by-default toward AI-proposed numbers, until the sim confirms them,
is the operating rule this whole exercise was run under, and it's called out
explicitly in `BALANCE_REPORT.md` §3, Iteration 2.

## Where I (not the AI) caught something, in the final review

Every mistake above was caught by re-running the sim inside the chat. The
last one wasn't. After Claude handed me what it called the "final" roster, I
didn't just accept it: I opened `units.csv` and `output/units.balanced.csv`
myself in VS Code, on my own machine, and re-ran `python sim/simulate.py`
independently to confirm the numbers matched what I'd been shown.

```
UNIT          CLASS        COST    WIN%  WIN%/COST
Sable         Archer          5   53.2%     10.64
Rookwood      Myrmidon        7   52.5%      7.49
Wisp          Cleric          4   50.1%     12.53
Brennan       Soldier         5   49.8%      9.95
Pyraxis       Battlemage      6   48.3%      8.06
Ser Halden    Knight          7   46.1%      6.59
```

Reading that table side by side is what caught it, not a script: Ser Halden
was tied for the *most expensive* unit in the roster (cost 7, same as
Rookwood) while having the *lowest* win rate of all six units. Every unit
individually sat inside the target band, so nothing had automatically
flagged it, but paying the top price for the worst result is exactly the
pattern this whole assessment is about eliminating. I raised it, and we
lowered Halden's cost from 7 to 6 (documented as Iteration 4 in
`BALANCE_REPORT.md`), then re-ran both the duel sim and the squad-check
script to confirm the fix didn't introduce a new problem elsewhere.

![Running the simulator locally in VS Code](screenshots/local_verification_vscode.png)

*My own terminal, in VS Code on my machine, re-running `sim/simulate.py`
against the roster Claude had produced, before I accepted the final numbers.*

This is the part I most want to be explicit about for the "use of AI as a
design partner" criteria: the "verify, don't trust the model's confidence"
discipline in this project ran in both directions. The AI caught its own
overconfident proposal once (the Brennan +1 ATK swing). I caught a different
issue the AI's own iteration process had quietly left behind, by insisting
on an independent local re-check of the "done" result instead of taking it
at face value. Neither direction of checking was optional; both mattered.

## How this would scale to 50+ units across multiple games per quarter

The manual back-and-forth used here (propose → apply → run sim → read →
adjust) does not scale past a handful of units: at 50+ units the surface
area of pairwise interactions is too large to eyeball. The pipeline I'd build:

1. **Automate the diagnosis pass.** A script (extending `simulate.py`'s
   output) flags every unit whose win rate or WIN%/COST sits outside a target
   band automatically, instead of a person scanning a printed table. This
   is exactly what should happen every time new units are added or an
   existing kit changes.
2. **Use AI for hypothesis generation, never for final numbers.** Feed each
   flagged unit's full stat block plus its worst/best matchups to the model
   and ask for 2–3 candidate fixes with reasoning: the same "stats before
   cost" and "check the mechanism, not just the stat" discipline used above.
   Never accept a proposed number without step 3.
3. **Auto-apply and re-simulate every proposal before a human sees it.** The
   Brennan incident shows why: a proposal that sounds minor can be wrong by
   16 points, and the only way to know is to run it. At 50+ units this has to
   be a script, not a person re-running the CLI by hand each time.
4. **Track iterations like code, one commit per balance pass, with the sim
   output attached.** This is what makes "show at least two iterations"
   possible to audit at any scale, and it's what let this report cite exact
   before/after numbers instead of a final snapshot.
5. **Build the mechanism-level checks once, reuse them everywhere.** The
   Rookwood doubling bug was found by writing a one-off script against
   `doubles()`. At 50+ units, that check (and equivalents for
   accuracy/crit-threshold interactions) should be a standing regression
   test that runs on every roster change, not something rediscovered per
   incident.
6. **Keep a human decision point at the "which system are we optimizing for"
   level** (this report's Section 3's target of ~50% ± a few points, the
   duplicate-cap rule, which encounters matter). AI accelerates the
   measure→diagnose→iterate loop, but the definition of "balanced" for a
   specific game's feel is still a design call, made by a person, that the
   pipeline serves rather than replaces.
