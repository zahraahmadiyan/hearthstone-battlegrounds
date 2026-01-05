from __future__ import annotations

from typing import Any, Dict, List, Optional

from common.models import (
    RecruitSnapshot,
    PlayerRecruitSnapshot,
    ShopSlot,
    HandCard,
    BoardSlot,
    MinionInstance,
)


class StateReducerError(Exception):
    pass


def _warn(msg: str) -> None:
    print(f"[reducer:warn] {msg}")


def _get_player(snapshot: RecruitSnapshot, player_id: str) -> PlayerRecruitSnapshot:
    try:
        return snapshot.get_player(player_id)
    except KeyError as e:
        raise StateReducerError(str(e)) from e


def _ensure_list_size(lst: List[Any], size: int, fill: Any) -> None:
    while len(lst) < size:
        lst.append(fill)


def _shop_slot_index(slot_obj: Dict[str, Any]) -> Optional[int]:
    if "index" in slot_obj and slot_obj["index"] is not None:
        return int(slot_obj["index"])
    if "slot" in slot_obj and slot_obj["slot"] is not None:
        return int(slot_obj["slot"])
    return None


def apply_state_delta(snapshot: RecruitSnapshot, delta_msg: Dict[str, Any]) -> RecruitSnapshot:
    msg_type = delta_msg.get("type")
    if msg_type != "state_delta":
        raise StateReducerError(f"Unsupported message type: {msg_type!r}")

    events = delta_msg.get("events")
    if not isinstance(events, list):
        raise StateReducerError("Delta message missing 'events' list")

    for i, ev in enumerate(events):
        if not isinstance(ev, dict):
            _warn(f"Event #{i} is not an object")
            continue

        op = ev.get("op")
        if not op:
            _warn(f"Event #{i} missing 'op'")
            continue

        try:
            if op == "gold":
                _apply_gold(snapshot, ev)
            elif op == "shop_update":
                _apply_shop_update(snapshot, ev)
            elif op == "hand_add":
                _apply_hand_add(snapshot, ev)
            elif op == "board_insert":
                _apply_board_insert(snapshot, ev)
            elif op == "board_remove":
                _apply_board_remove(snapshot, ev)
            else:
                _warn(f"Unknown op '{op}'")
        except StateReducerError as e:
            _warn(f"Failed applying event #{i} op={op!r}: {e}")

    return snapshot


def _apply_gold(snapshot: RecruitSnapshot, ev: Dict[str, Any]) -> None:
    player_id = str(ev.get("player_id", ""))
    if not player_id:
        raise StateReducerError("gold: missing player_id")
    value = ev.get("value")
    if value is None:
        raise StateReducerError("gold: missing value")
    me = _get_player(snapshot, player_id)
    me.gold = int(value)


def _apply_shop_update(snapshot: RecruitSnapshot, ev: Dict[str, Any]) -> None:
    player_id = str(ev.get("player_id", ""))
    if not player_id:
        raise StateReducerError("shop_update: missing player_id")
    slots = ev.get("slots")
    if not isinstance(slots, list):
        raise StateReducerError("shop_update: missing slots list")

    me = _get_player(snapshot, player_id)

    for s in slots:
        if not isinstance(s, dict):
            _warn("shop_update: invalid slot")
            continue

        idx = _shop_slot_index(s)
        if idx is None or idx < 0:
            _warn("shop_update: missing index/slot")
            continue

        while len(me.shop) <= idx:
            me.shop.append(None)

        me.shop[idx] = ShopSlot(
            slot=idx,
            card_id=str(s.get("card_id", "")),
            frozen=bool(s.get("frozen", False)),
            sim_tier=int(s["sim_tier"]) if s.get("sim_tier") is not None else None,
            extra={k: v for k, v in s.items() if k not in {"index", "slot", "card_id", "frozen", "sim_tier"}},
        )


def _apply_hand_add(snapshot: RecruitSnapshot, ev: Dict[str, Any]) -> None:
    player_id = str(ev.get("player_id", ""))
    if not player_id:
        raise StateReducerError("hand_add: missing player_id")
    card = ev.get("card")
    if not isinstance(card, dict):
        raise StateReducerError("hand_add: missing card")

    me = _get_player(snapshot, player_id)

    hand_index = card.get("hand_index")
    if hand_index is None:
        raise StateReducerError("hand_add: missing hand_index")

    new_card = HandCard(
        hand_index=int(hand_index),
        instance_id=str(card.get("instance_id", "")),
        card_id=str(card.get("card_id", "")),
        name=card.get("name"),
        attack=int(card["attack"]) if card.get("attack") is not None else None,
        health=int(card["health"]) if card.get("health") is not None else None,
        tier=int(card["tier"]) if card.get("tier") is not None else None,
        is_golden=bool(card.get("is_golden", False)),
        keywords=list(card.get("keywords", [])),
        extra={k: v for k, v in card.items() if k not in {
            "hand_index", "instance_id", "card_id", "name",
            "attack", "health", "tier", "is_golden", "keywords"
        }},
    )

    for i, existing in enumerate(me.hand):
        if existing.hand_index == new_card.hand_index:
            me.hand[i] = new_card
            return

    me.hand.append(new_card)


def _apply_board_insert(snapshot: RecruitSnapshot, ev: Dict[str, Any]) -> None:
    player_id = str(ev.get("player_id", ""))
    if not player_id:
        raise State
# State reducer for the Recruit phase.
# This module applies state_delta messages to the current in-memory RecruitSnapshot.
# Each delta contains a list of small events (ops) that describe how the game state
# should change (for example updating gold, shop, hand, or board).
# The reducer is responsible for translating these events into actual changes
# on the game state. It does not contain any UI, networking, or game rule logic.
# Unknown or invalid events are safely ignored with a warning to prevent crashes.
# This allows the client to stay stable even if some messages are not supported yet.
