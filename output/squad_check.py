#!/usr/bin/env python3
"""
Supplementary squad-vs-squad checker (NOT the graded engine, the reference
sim.simulate.py 1v1 duel model is). This approximates encounters A/B/C as
simultaneous team fights, to sanity-check for degenerate cheap squads.

Model: every living unit acts once per round, in speed order (ties broken by
a stable random shuffle each trial). A unit attacks the living enemy with the
lowest current HP fraction (a simple "finish the weak one" AI on both sides).
Doubling is applied per the combat-rules.md follow-up rule. This ignores
positioning/mov/range entirely, same limitation as the reference duel sim.
"""
import random
import itertools
from dataclasses import dataclass, field
import sys
sys.path.insert(0, "sim")
from simulate import load_units, hit_chance, crit_chance, doubles, power, defense_vs, clamp


@dataclass
class Combatant:
    unit: object
    hp: float
    side: str
    tag: str


def strike_dmg(attacker, target, rng):
    if rng.uniform(0, 100) > hit_chance(attacker.unit, target.unit):
        return 0
    dmg = max(1, power(attacker.unit) - defense_vs(attacker.unit, target.unit))
    if rng.uniform(0, 100) <= crit_chance(attacker.unit, target.unit):
        dmg *= 3
    return dmg


def pick_target(attacker, enemies):
    alive = [e for e in enemies if e.hp > 0]
    if not alive:
        return None
    return min(alive, key=lambda e: e.hp / e.unit.hp)


def squad_battle(player_units, enemy_units, rng, max_rounds=40):
    combatants = (
        [Combatant(u, u.hp, "player", f"P{i}") for i, u in enumerate(player_units)]
        + [Combatant(u, u.hp, "enemy", f"E{i}") for i, u in enumerate(enemy_units)]
    )
    for _round in range(max_rounds):
        order = sorted(combatants, key=lambda c: (-c.unit.spd, rng.random()))
        for c in order:
            if c.hp <= 0:
                continue
            enemies = [o for o in combatants if o.side != c.side]
            target = pick_target(c, enemies)
            if target is None:
                break
            n = 2 if doubles(c.unit, target.unit) else 1
            for _ in range(n):
                if target.hp <= 0:
                    target = pick_target(c, enemies)
                    if target is None:
                        break
                target.hp -= strike_dmg(c, target, rng)
        p_alive = any(c.hp > 0 for c in combatants if c.side == "player")
        e_alive = any(c.hp > 0 for c in combatants if c.side == "enemy")
        if not p_alive or not e_alive:
            return "player" if p_alive and not e_alive else ("enemy" if e_alive and not p_alive else "draw")
    p_hp = sum(max(c.hp, 0) for c in combatants if c.side == "player")
    e_hp = sum(max(c.hp, 0) for c in combatants if c.side == "enemy")
    return "player" if p_hp >= e_hp else "enemy"


def make_enemy(name, cls, attack_type, hp, atk, mag, def_, res, spd, skl, lck):
    U = type(load_units("output/units.balanced.csv")[0])
    return U(id=name, name=name, cls=cls, attack_type=attack_type, hp=hp, atk=atk,
              mag=mag, def_=def_, res=res, spd=spd, skl=skl, lck=lck, cost=0)


ENCOUNTERS = {
    "A_SunkenGate": (
        [make_enemy(f"GateWretch{i}", "Brigand", "physical", 22, 11, 0, 5, 2, 7, 6, 3) for i in range(3)]
        + [make_enemy("BogAcolyte", "Acolyte", "magic", 18, 0, 12, 3, 7, 8, 8, 5)]
    ),
    "B_HollowThrone": (
        [make_enemy(f"ThroneGuard{i}", "Knight", "physical", 30, 15, 0, 12, 5, 6, 8, 4) for i in range(2)]
        + [make_enemy("CrownMagus", "Battlemage", "magic", 22, 0, 17, 4, 9, 7, 10, 6)]
    ),
    "C_CarrionRun": (
        [make_enemy(f"ShrikeRunner{i}", "Skirmisher", "physical", 16, 18, 0, 4, 4, 15, 10, 6) for i in range(3)]
    ),
}


def budget_squads(units, budget=20):
    """Generate candidate squads within budget: mono-spam of every unit,
    plus a spread of mixed squads, deduplicated."""
    squads = []
    for u in units:
        n = budget // u.cost
        if n >= 1:
            squads.append((f"{n}x {u.name}", [u] * n))
    # mixed: greedy combos of up to 4 distinct units within budget (small search)
    seen = set()
    for r in range(2, 5):
        for combo in itertools.combinations_with_replacement(units, r):
            cost = sum(u.cost for u in combo)
            if cost <= budget and cost >= budget - 3:  # use most of the budget
                key = tuple(sorted(u.id for u in combo))
                if key in seen:
                    continue
                seen.add(key)
                label = "+".join(u.name for u in combo) + f" (cost {cost})"
                squads.append((label, list(combo)))
    return squads


def main():
    units = load_units("output/units.balanced.csv")
    squads = budget_squads(units, budget=20)
    trials = 500
    print(f"{len(squads)} candidate squads under budget 20\n")
    for enc_name, enemies in ENCOUNTERS.items():
        print(f"=== Encounter {enc_name} ===")
        results = []
        for label, squad in squads:
            rng = random.Random(hash((enc_name, label)) & 0xffffffff)
            wins = 0
            for _ in range(trials):
                w = squad_battle(squad, enemies, rng)
                if w == "player":
                    wins += 1
            cost = sum(u.cost for u in squad)
            results.append((label, cost, 100 * wins / trials))
        results.sort(key=lambda r: -r[2])
        for label, cost, wr in results:
            flag = "  <-- degenerate cheap sweep?" if wr >= 95 and cost <= 14 else ""
            print(f"  cost={cost:>2}  win%={wr:>5.1f}   {label}{flag}")
        print()


if __name__ == "__main__":
    main()
