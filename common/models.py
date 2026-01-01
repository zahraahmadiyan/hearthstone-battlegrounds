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
    has_divine_shield: bool = False
    reborn_used: bool = False

    extra: Dict[str, Any] = field(default_factory=dict)


@dataclass(slots=True)
class HandCard(MinionInstance):
    hand_index: int = 0


@dataclass(slots=True)
class BoardSlot:
    slot: int
    minion: MinionInstance


@dataclass(slots=True)
class ShopSlot:
    slot: int
    card_id: Optional[str] = None
    name: Optional[str] = None
    attack: Optional[int] = None
    health: Optional[int] = None
    tier: Optional[int] = None
    sim_tier: Optional[int] = None
    cost: Optional[int] = None
    is_golden: bool = False
    frozen: bool = False
    keywords: List[str] = field(default_factory=list)
    is_empty: bool = False


@dataclass(slots=True)
class HeroState:
    card_id: Optional[str] = None
    name: Optional[str] = None
    health: Optional[int] = None
    armor: int = 0
    hero_power_cost: Optional[int] = None
    hero_power_used: Optional[bool] = None
    raw: Dict[str, Any] = field(default_factory=dict)


@dataclass(slots=True)
class PlayerRecruitSnapshot:
    player_id: str
    hero: HeroState

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
    shop: List[ShopSlot] = field(default_factory=list)


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
