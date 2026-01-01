from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Dict, List

from common.models import (
    RecruitSnapshot,
    PlayerRecruitSnapshot,
    HeroState,
    ShopSlot,
    BoardSlot,
    MinionInstance,
    HandCard,
)


class StateLoaderError(Exception):
    pass


def _req(obj: Dict[str, Any], key: str) -> Any:
    if key not in obj:
        raise StateLoaderError(f"Missing required field: '{key}'")
    return obj[key]


def _as_int(value: Any, field_name: str) -> int:
    if not isinstance(value, int):
        raise StateLoaderError(f"Field '{field_name}' must be int, got {type(value).__name__}")
    return value


def _parse_hero(hero_raw: Any, fallback_health: int, fallback_armor: int) -> HeroState:
    if isinstance(hero_raw, str):
        return HeroState(
            name=hero_raw,
            health=fallback_health,
            armor=fallback_armor,
            raw={"hero": hero_raw},
        )

    if isinstance(hero_raw, dict):
        return HeroState(
            card_id=hero_raw.get("card_id"),
            name=hero_raw.get("name"),
            health=hero_raw.get("health", fallback_health),
            armor=hero_raw.get("armor", fallback_armor),
            hero_power_cost=hero_raw.get("hero_power_cost"),
            hero_power_used=hero_raw.get("hero_power_used"),
            raw=hero_raw,
        )

    raise StateLoaderError(f"Invalid hero field type: {type(hero_raw).__name__}")


def _parse_board(board_raw: List[Dict[str, Any]]) -> List[BoardSlot]:
    board: List[BoardSlot] = []
    for i, m in enumerate(board_raw):
        try:
            slot = _as_int(_req(m, "slot"), "board[].slot")
            inst = _req(m, "instance_id")
            card_id = _req(m, "card_id")

            minion = MinionInstance(
                instance_id=str(inst),
                card_id=str(card_id),
                name=m.get("name"),
                attack=m.get("attack"),
                health=m.get("health"),
                tier=m.get("tier"),
                is_golden=bool(m.get("is_golden", False)),
                keywords=list(m.get("keywords", [])),
                has_divine_shield=bool(m.get("has_divine_shield", False)),
                reborn_used=bool(m.get("reborn_used", False)),
                extra={k: v for k, v in m.items() if k not in {
                    "slot", "instance_id", "card_id", "name",
                    "attack", "health", "tier", "is_golden",
                    "keywords", "has_divine_shield", "reborn_used"
                }},
            )

            board.append(BoardSlot(slot=slot, minion=minion))
        except StateLoaderError as e:
            raise StateLoaderError(f"Board item {i}: {e}")
    return board


def _parse_hand(hand_raw: List[Dict[str, Any]]) -> List[HandCard]:
    hand: List[HandCard] = []
    for i, c in enumerate(hand_raw):
        try:
            hand_index = _as_int(_req(c, "hand_index"), "hand[].hand_index")
            inst = _req(c, "instance_id")
            card_id = _req(c, "card_id")

            hand.append(
                HandCard(
                    hand_index=hand_index,
                    instance_id=str(inst),
                    card_id=str(card_id),
                    name=c.get("name"),
                    attack=c.get("attack"),
                    health=c.get("health"),
                    tier=c.get("tier"),
                    is_golden=bool(c.get("is_golden", False)),
                    keywords=list(c.get("keywords", [])),
                    extra={k: v for k, v in c.items() if k not in {
                        "hand_index", "instance_id", "card_id", "name",
                        "attack", "health", "tier", "is_golden", "keywords"
                    }},
                )
            )
        except StateLoaderError as e:
            raise StateLoaderError(f"Hand item {i}: {e}")
    return hand


def _parse_shop(shop_raw: List[Any]) -> List[ShopSlot]:
    shop: List[ShopSlot] = []
    for idx, s in enumerate(shop_raw):
        if s is None:
            shop.append(ShopSlot(slot=idx, is_empty=True))
            continue

        if not isinstance(s, dict):
            raise StateLoaderError(f"Shop slot {idx}: must be object or null")

        slot = s.get("slot", idx)

        shop.append(
            ShopSlot(
                slot=int(slot),
                card_id=s.get("card_id"),
                name=s.get("name"),
                attack=s.get("attack"),
                health=s.get("health"),
                tier=s.get("tier"),
                sim_tier=s.get("sim_tier"),
                cost=s.get("cost"),
                is_golden=bool(s.get("is_golden", False)),
                frozen=bool(s.get("frozen", False)),
                keywords=list(s.get("keywords", [])),
                is_empty=False,
            )
        )
    return shop


def load_recruit_snapshot(path: str) -> RecruitSnapshot:
    p = Path(path)
    if not p.exists():
        raise StateLoaderError(f"File not found: {path}")

    raw = json.loads(p.read_text(encoding="utf-8"))

    match_id = _req(raw, "match_id")
    players_raw = _req(raw, "players")

    snap = RecruitSnapshot(
        match_id=str(match_id),
        phase=str(raw.get("phase", "recruit")),
        turn=raw.get("turn"),
        players=[],
    )

    if not isinstance(players_raw, list):
        raise StateLoaderError("'players' must be a list")

    for i, pr in enumerate(players_raw):
        if not isinstance(pr, dict):
            raise StateLoaderError(f"players[{i}] must be object")

        player_id = str(_req(pr, "player_id"))

        health = int(
            pr.get("health", pr.get("hero", {}).get("health", 0) if isinstance(pr.get("hero"), dict) else 0)
        )
        armor = int(
            pr.get("armor", pr.get("hero", {}).get("armor", 0) if isinstance(pr.get("hero"), dict) else 0)
        )

        hero = _parse_hero(pr.get("hero"), fallback_health=health, fallback_armor=armor)

        gold = _as_int(_req(pr, "gold"), "gold")
        tavern_tier = _as_int(_req(pr, "tavern_tier"), "tavern_tier")

        board = _parse_board(pr.get("board", []))
        hand = _parse_hand(pr.get("hand", []))
        shop = _parse_shop(pr.get("shop", []))

        snap.players.append(
            PlayerRecruitSnapshot(
                player_id=player_id,
                hero=hero,
                health=int(health),
                armor=int(armor),
                tavern_tier=tavern_tier,
                gold=gold,
                max_gold=pr.get("max_gold"),
                upgrade_cost=pr.get("upgrade_cost"),
                refresh_cost=pr.get("refresh_cost"),
                timer_ms=pr.get("timer_ms"),
                flags=dict(pr.get("flags", {})),
                board=board,
                hand=hand,
                shop=shop,
            )
        )

    return snap
