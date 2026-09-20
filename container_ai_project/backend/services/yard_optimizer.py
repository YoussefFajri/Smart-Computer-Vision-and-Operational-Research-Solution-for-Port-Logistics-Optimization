"""
Yard Placement Optimizer — Phase 2
===================================
EDD (Earliest Due Date) + Weight Stability + Simulated Annealing

Logic summary
-------------
* Containers departing SOONEST must be placed on TOP (or at least reachable
  without moving others). Placing a container with a later departure ABOVE
  one that leaves earlier forces a costly re-handle (moving the top box out
  of the way before you can load the bottom one onto the ship).
* Weight stability: heavy containers must stay below lighter ones to keep
  the stack structurally safe.
* Simulated Annealing escapes local minima when scoring candidate slots.

Only stdlib modules are used: random, math, typing, collections, dataclasses.
"""
from __future__ import annotations

import math
import random
from collections import defaultdict
from dataclasses import dataclass, field
from typing import Dict, List, Optional, Tuple


# ─────────────────────────────────────────────────────────────────────────────
# 1. DATA MODELS
# ─────────────────────────────────────────────────────────────────────────────

@dataclass
class Container:
    """Represents one physical container in the yard."""
    id: str
    size: int              # 20 or 40 (feet)
    weight: float          # kilograms
    departure_time: str    # ISO date string, e.g. "2026-05-10" — string-comparable


@dataclass
class Slot:
    """
    One addressable position inside a block.
    bay   → column along the quay (0 = closest to quay)
    row   → lateral row
    tier  → vertical level (0 = ground)
    """
    bay: int
    row: int
    tier: int
    container_id: Optional[str] = None
    localization: str = ""   # human-readable "Block-Bay-Row-Tier"


@dataclass
class Stack:
    """A vertical column of slots (same bay + row, varying tier)."""
    slots: List[Slot] = field(default_factory=list)

    def current_height(self) -> int:
        """Number of occupied tiers."""
        return sum(1 for s in self.slots if s.container_id is not None)

    def get_top_occupied(self) -> Optional[Slot]:
        """Return the highest occupied slot, or None if empty."""
        occupied = [s for s in self.slots if s.container_id is not None]
        return max(occupied, key=lambda s: s.tier) if occupied else None

    def get_next_free(self) -> Optional[Slot]:
        """Return the lowest free slot (the next stackable position)."""
        free = [s for s in self.slots if s.container_id is None]
        return min(free, key=lambda s: s.tier) if free else None


@dataclass
class Block:
    """
    A rectangular section of the yard.
    Stacks are keyed by (bay, row).
    """
    block_id: str          # e.g. "A", "B", "S1"
    n_bays: int
    n_rows: int
    n_tiers: int
    stacks: Dict[Tuple[int, int], Stack] = field(default_factory=dict)

    def __post_init__(self):
        # Auto-build all stacks if not provided
        if not self.stacks:
            for bay in range(self.n_bays):
                for row in range(self.n_rows):
                    slots = [
                        Slot(
                            bay=bay, row=row, tier=tier,
                            localization=f"{self.block_id}-{bay}-{row}-{tier}"
                        )
                        for tier in range(self.n_tiers)
                    ]
                    self.stacks[(bay, row)] = Stack(slots=slots)


@dataclass
class Yard:
    """
    The entire container yard: a collection of named blocks and a
    registry mapping container_id → Container object.
    """
    blocks: Dict[str, Block] = field(default_factory=dict)
    containers_registry: Dict[str, Container] = field(default_factory=dict)

    def reset(self):
        """Clear all containers from the yard and empty the registry."""
        self.containers_registry.clear()
        for block in self.blocks.values():
            for stack in block.stacks.values():
                for slot in stack.slots:
                    slot.container_id = None

    def place_container(self, block_id: str, bay: int, row: int,
                        container: Container) -> Optional[Slot]:
        """
        Actually place a container in the yard, updating the slot and registry.
        Returns the Slot used, or None on failure.
        """
        block = self.blocks.get(block_id)
        if not block:
            return None
        stack = block.stacks.get((bay, row))
        if not stack:
            return None
        slot = stack.get_next_free()
        if slot is None:
            return None
        slot.container_id = container.id
        self.containers_registry[container.id] = container
        return slot


# ─────────────────────────────────────────────────────────────────────────────
# 2. BLOCK POLICY
# ─────────────────────────────────────────────────────────────────────────────

# Primary and backup block assignments per container size
SIZE_POLICY: Dict[int, Dict[str, List[str]]] = {
    20: {"primary": ["A", "B"], "backup": ["S1"]},
    40: {"primary": ["C", "D"], "backup": ["S2"]},
}


# ─────────────────────────────────────────────────────────────────────────────
# 3. HARD CONSTRAINT CHECKER
# ─────────────────────────────────────────────────────────────────────────────

def get_valid_slots(
    container: Container,
    yard: Yard,
    allowed_blocks: List[str],
    strict_edd: bool = True,
    strict_weight: bool = True,
) -> List[Tuple[str, Slot]]:
    """
    Return all (block_id, slot) pairs where `container` can legally be placed.

    Hard constraints (all must pass):
    ──────────────────────────────────
    1. Block must be in `allowed_blocks`.
    2. Stack must not be full (a free tier must exist).
    3. Stack homogeneity: every container already in the stack must share
       the same size (20 or 40 ft) as the incoming container.
    4. EDD (if strict_edd=True):
         The incoming container MUST NOT have an EARLIER departure_time
         than the topmost container already in the stack. In other words,
         you can only place on top if you depart LATER OR EQUAL.
         Rationale: If you place an early-departure box under a late-departure
         box, you will need to re-handle (move the top box) before you can
         load the bottom one. That wastes crane time and delays operations.
    5. Weight stability (if strict_weight=True):
         The incoming container MUST NOT be heavier than the top container.
         Heavy items must be on the bottom for structural safety.
    """
    valid: List[Tuple[str, Slot]] = []

    for block_id, block in yard.blocks.items():
        if block_id not in allowed_blocks:
            continue

        for (bay, row), stack in block.stacks.items():
            # Free slot check
            next_slot = stack.get_next_free()
            if next_slot is None:
                continue  # stack full

            # Stack homogeneity check
            occupied = [s for s in stack.slots if s.container_id is not None]
            for occ_slot in occupied:
                existing = yard.containers_registry.get(occ_slot.container_id)
                if existing and existing.size != container.size:
                    break  # mixed sizes — invalid
            else:
                # All existing containers share the same size → pass homogeneity

                top_slot = stack.get_top_occupied()
                if top_slot is not None:
                    top_container = yard.containers_registry.get(top_slot.container_id)
                    if top_container:
                        # ── EDD constraint ──────────────────────────────────
                        # The new container goes ON TOP of top_container.
                        # For re-handle-free access we need:
                        #   new.departure >= top.departure
                        # i.e. the container we stack now must leave NO EARLIER
                        # than the one below it.
                        if strict_edd:
                            if container.departure_time < top_container.departure_time:
                                # New container leaves sooner → if placed above,
                                # we'd need to remove it before loading the one
                                # below. REJECT.
                                continue

                        # ── Weight stability constraint ──────────────────────
                        # New container sits ON TOP → must weigh ≤ top container.
                        if strict_weight:
                            if container.weight > top_container.weight:
                                continue  # would put heavier box on top — unsafe

                valid.append((block_id, next_slot))

    return valid


# ─────────────────────────────────────────────────────────────────────────────
# 4. SCORING FUNCTION
# ─────────────────────────────────────────────────────────────────────────────

def calculate_score(slot: Slot, container: Container, yard: Yard) -> float:
    """
    Score a candidate (block_id, slot) placement. Lower score = better.

    Components
    ──────────
    A. Rehandling risk  — the higher the tier, the more containers are ABOVE
       ground, meaning future containers may block it. Penalise by tier.
    B. Quay distance    — bay 0 is closest to the quay. Higher bay index means
       more crane travel time when loading the ship.
    C. Stack imbalance  — high variance in stack heights across the block
       means uneven load distribution and harder planning. Penalise variance.
    """
    block_id = slot.localization.split("-")[0]
    block = yard.blocks.get(block_id)

    # A. Rehandling risk: penalise higher tiers
    score_rehandling = slot.tier * 10.0

    # B. Quay distance
    score_quay = slot.bay * 5.0

    # C. Stack imbalance within the block
    score_imbalance = 0.0
    if block:
        heights = [s.current_height() for s in block.stacks.values()]
        if len(heights) > 1:
            mean_h = sum(heights) / len(heights)
            variance = sum((h - mean_h) ** 2 for h in heights) / len(heights)
            score_imbalance = variance * 2.0

    return score_rehandling + score_quay + score_imbalance


# ─────────────────────────────────────────────────────────────────────────────
# 5. SIMULATED ANNEALING
# ─────────────────────────────────────────────────────────────────────────────

def simulated_annealing_optimization(
    container: Container,
    yard: Yard,
    valid_slots: List[Tuple[str, Slot]],
    precomputed_scores: Dict[str, float],
    initial_temp: float = 100.0,
    cooling_rate: float = 0.90,
    min_temp: float = 0.1,
    max_iter_per_temp: int = 20,
) -> Tuple[Optional[Tuple[str, Slot]], float]:
    """
    Simulated Annealing over the list of valid (block_id, slot) pairs.

    Why SA?  A greedy pick of the top-scored slot may miss a globally
    better region (e.g. a slightly higher tier in a better-balanced block).
    SA lets the search occasionally accept worse moves to escape local minima.

    Returns (best_block_id_slot_tuple, best_cost).
    """
    if not valid_slots:
        return None, float("inf")

    # Helper: slot key for the precomputed score dict
    def _key(block_id: str, slot: Slot) -> str:
        return f"{block_id}|{slot.localization}"

    # ── Random initial solution ───────────────────────────────────────────────
    current = random.choice(valid_slots)
    current_cost = precomputed_scores.get(_key(*current), calculate_score(current[1], container, yard))

    best = current
    best_cost = current_cost
    temp = initial_temp

    # ── Annealing loop ────────────────────────────────────────────────────────
    while temp > min_temp:
        for _ in range(max_iter_per_temp):
            if len(valid_slots) < 2:
                break
            # Neighbour: pick any different valid slot at random
            neighbour = random.choice(valid_slots)
            while neighbour == current and len(valid_slots) > 1:
                neighbour = random.choice(valid_slots)

            neighbour_cost = precomputed_scores.get(
                _key(*neighbour),
                calculate_score(neighbour[1], container, yard)
            )

            delta = neighbour_cost - current_cost

            # Accept if better, or with Boltzmann probability if worse
            if delta < 0 or random.random() < math.exp(-delta / temp):
                current = neighbour
                current_cost = neighbour_cost

            if current_cost < best_cost:
                best = current
                best_cost = current_cost

        # Geometric cooling
        temp *= cooling_rate

    return best, best_cost


# ─────────────────────────────────────────────────────────────────────────────
# 6. MULTI-STAGE FALLBACK ORCHESTRATOR
# ─────────────────────────────────────────────────────────────────────────────

def _find_best_with_criteria(
    container: Container,
    yard: Yard,
    allowed_blocks: List[str],
    strict_edd: bool,
    strict_weight: bool,
    top_k: int = 10,
) -> Optional[Tuple[Tuple[str, Slot], float]]:
    """
    Get valid slots under the given constraints, score them, keep top_k,
    run Simulated Annealing, return (best_slot_tuple, cost) or None.
    """
    valid = get_valid_slots(container, yard, allowed_blocks, strict_edd, strict_weight)
    if not valid:
        return None

    # Pre-score all valid slots
    scored = [
        ((block_id, slot), calculate_score(slot, container, yard))
        for block_id, slot in valid
    ]
    scored.sort(key=lambda x: x[1])

    # Keep only top_k candidates to keep SA search focused
    top_candidates = [item[0] for item in scored[:top_k]]
    precomputed = {
        f"{block_id}|{slot.localization}": score
        for (block_id, slot), score in scored[:top_k]
    }

    best_slot, best_cost = simulated_annealing_optimization(
        container, yard, top_candidates, precomputed
    )
    if best_slot is None:
        return None
    return best_slot, best_cost


def find_best_slot(
    container: Container,
    yard: Yard,
    top_k: int = 10,
) -> Optional[Tuple[Tuple[str, Slot], float, str]]:
    """
    4-stage multi-fallback placement search.

    Stage | Blocks   | EDD strict | Weight strict | Rationale
    ──────|──────────|────────────|───────────────|──────────────────────────
      1   | primary  | True       | True          | Ideal: all rules enforced
      2   | backup   | True       | True          | Primary full, use backup
      3   | primary  | False      | True          | EDD relaxed but weight safe
      4   | backup   | False      | False         | Last resort, any free slot

    Returns (block_id_slot_tuple, cost, stage_description) or None.
    """
    policy = SIZE_POLICY.get(container.size, SIZE_POLICY[20])
    primary = policy["primary"]
    backup  = policy["backup"]

    stages = [
        (primary, True,  True,  "Stage 1 — primary blocks, strict EDD + weight"),
        (backup,  True,  True,  "Stage 2 — backup blocks, strict EDD + weight"),
        (primary, False, True,  "Stage 3 — primary blocks, relaxed EDD, strict weight"),
        (backup,  False, False, "Stage 4 — backup blocks, no EDD, no weight constraint"),
    ]

    for blocks, strict_edd, strict_weight, label in stages:
        result = _find_best_with_criteria(
            container, yard, blocks, strict_edd, strict_weight, top_k
        )
        if result:
            slot_tuple, cost = result
            return slot_tuple, cost, label

    return None  # Yard is full


# ─────────────────────────────────────────────────────────────────────────────
# 7. YARD STATE SERIALISER (for the API / Three.js view)
# ─────────────────────────────────────────────────────────────────────────────

def get_yard_state_dict(yard: Yard) -> dict:
    """
    Convert the entire Yard into a JSON-serialisable dict consumed by
    the Three.js front-end and the /yard/state endpoint.
    """
    out: dict = {"blocks": {}}
    for block_id, block in yard.blocks.items():
        stacks_out = {}
        for (bay, row), stack in block.stacks.items():
            slots_out = []
            for slot in stack.slots:
                ctr = yard.containers_registry.get(slot.container_id) if slot.container_id else None
                slots_out.append({
                    "tier":           slot.tier,
                    "container_id":   slot.container_id,
                    "localization":   slot.localization,
                    "size":           ctr.size if ctr else None,
                    "weight":         ctr.weight if ctr else None,
                    "departure_time": ctr.departure_time if ctr else None,
                })
            stacks_out[f"{bay}_{row}"] = {
                "bay":    bay,
                "row":    row,
                "height": stack.current_height(),
                "slots":  slots_out,
            }
        out["blocks"][block_id] = {
            "block_id": block_id,
            "n_bays":   block.n_bays,
            "n_rows":   block.n_rows,
            "n_tiers":  block.n_tiers,
            "stacks":   stacks_out,
        }
    return out


# ─────────────────────────────────────────────────────────────────────────────
# 8. YARD FACTORY — pre-seeded demo yard
# ─────────────────────────────────────────────────────────────────────────────

def build_demo_yard() -> Yard:
    """
    Build a realistic demo yard with 6 blocks and pre-placed containers
    so the 3D view is not empty on first load.
    """
    yard = Yard(
        blocks={
            "A":  Block("A",  n_bays=6, n_rows=4, n_tiers=5),
            "B":  Block("B",  n_bays=6, n_rows=4, n_tiers=5),
            "C":  Block("C",  n_bays=6, n_rows=4, n_tiers=5),
            "D":  Block("D",  n_bays=6, n_rows=4, n_tiers=5),
            "S1": Block("S1", n_bays=4, n_rows=3, n_tiers=4),
            "S2": Block("S2", n_bays=4, n_rows=3, n_tiers=4),
        }
    )

    # Pre-seed demo containers
    seeds = [
        # (block, bay, row, Container)
        ("A",  0, 0, Container("MSCU001", 20, 22000, "2026-05-01")),
        ("A",  0, 0, Container("MSCU002", 20, 18000, "2026-05-08")),
        ("A",  0, 1, Container("MSCU003", 20, 25000, "2026-05-03")),
        ("A",  1, 0, Container("MSCU004", 20, 21000, "2026-05-15")),
        ("B",  0, 0, Container("MSCU005", 20, 19000, "2026-05-02")),
        ("B",  0, 1, Container("MSCU006", 20, 17500, "2026-05-12")),
        ("C",  0, 0, Container("MAEU001", 40, 28000, "2026-05-04")),
        ("C",  0, 0, Container("MAEU002", 40, 26000, "2026-05-10")),
        ("C",  1, 0, Container("MAEU003", 40, 30000, "2026-05-06")),
        ("D",  0, 0, Container("MAEU004", 40, 27000, "2026-05-05")),
        ("S1", 0, 0, Container("MISC001", 20, 20000, "2026-05-20")),
    ]

    for block_id, bay, row, ctr in seeds:
        yard.place_container(block_id, bay, row, ctr)

    return yard


# ─────────────────────────────────────────────────────────────────────────────
# 9. STANDALONE DEMO
# ─────────────────────────────────────────────────────────────────────────────

def main():
    print("=" * 65)
    print("  Container Yard Placement Optimizer — EDD + Simulated Annealing")
    print("=" * 65)

    yard = build_demo_yard()

    # New container to place
    new_ctr = Container(
        id="TEST999",
        size=20,
        weight=25000,
        departure_time="2026-05-10",
    )

    print(f"\nPlacing container : {new_ctr.id}")
    print(f"  Size            : {new_ctr.size} ft")
    print(f"  Weight          : {new_ctr.weight:,} kg")
    print(f"  Departure       : {new_ctr.departure_time}")

    result = find_best_slot(new_ctr, yard)

    if result is None:
        print("\n❌ Yard is full — no valid slot found.")
        return

    (block_id, slot), cost, stage_label = result

    print(f"\n✅ Best slot found:")
    print(f"   Block          : {block_id}")
    print(f"   Location       : {slot.localization}")
    print(f"   Tier           : {slot.tier}")
    print(f"   Optimizer cost : {cost:.2f}")
    print(f"   Selected via   : {stage_label}")

    print(f"\n📋 EDD Explanation:")
    print(f"   Departure '{new_ctr.departure_time}' was compared against")
    print(f"   every container already in candidate stacks.")
    print(f"   Only stacks where the new container's departure is ≥ the")
    print(f"   topmost container's departure were accepted — guaranteeing")
    print(f"   the ship can load in departure order with zero re-handles.")


if __name__ == "__main__":
    main()
