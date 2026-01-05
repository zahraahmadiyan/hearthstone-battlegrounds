from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional


@dataclass(slots=True)
class MinionInstance:
    instance_id: str
    card_id: str
    name: Optional[str] = None

    attack: Optional[int] = None
    health: Optional[int] = None
    tier: Optional[int] = None
    is_golden: bool = False

    keywords: List[str] = field(default_factory=list)
    extra: Dict[str, Any] = field(default_factory=dict)


@dataclass(slots=True)
class BoardSlot:
    slot: int
    minion: Optional[MinionInstance] = None


@dataclass(slots=True)
class HandCard:
    hand_index: int
    instance_id: str
    card_id: str
    name: Optional[str] = None

    attack: Optional[int] = None
    health: Optional[int] = None
    tier: Optional[int] = None
    is_golden: bool = False

    keywords: List[str] = field(default_factory=list)
    extra: Dict[str, Any] = field(default_factory=dict)


@dataclass(slots=True)
class ShopSlot:
    slot: int
    card_id: str
    frozen: bool = False
    sim_tier: Optional[int] = None
    extra: Dict[str, Any] = field(default_factory=dict)


@dataclass(slots=True)
class PlayerRecruitSnapshot:
    player_id: str
    hero: str

    health: int
    armor: int
    tavern_tier: int

    gold: int
    max_gold: Optional[int] = None

    upgrade_cost: Optional[int] = None
    refresh_cost: Optional[int] = None
    timer_ms: Optional[int] = None

    flags: Dict[str, Any] = field(default_factory=dict)

    board: List[BoardSlot] = field(default_factory=list)
    hand: List[HandCard] = field(default_factory=list)
    shop: List[Optional[ShopSlot]] = field(default_factory=list)


@dataclass(slots=True)
class RecruitSnapshot:
    match_id: str
    phase: str = "recruit"
    turn: Optional[int] = None
    players: List[PlayerRecruitSnapshot] = field(default_factory=list)

    def get_player(self, player_id: str) -> PlayerRecruitSnapshot:
        for p in self.players:
            if p.player_id == player_id:
                return p
        raise KeyError(f"Player '{player_id}' not found in snapshot")

# Data models for the Recruit phase game state.
# These classes hold the current state of the game in memory while the client is running.
# The state is first loaded from a JSON snapshot, then updated step-by-step using
# state_delta messages.
# This file only defines the structure of the data.
# Game logic, UI rendering, and networking are handled in other parts of the project.
# The UI should only read from these models.
# Any change to the state should be done through the state_reducer.
