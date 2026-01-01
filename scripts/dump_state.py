import sys

from services.state_loader import load_recruit_snapshot, StateLoaderError


def main() -> int:
    if len(sys.argv) < 3:
        print("Usage: python scripts/dump_state.py <json_path> <my_player_id>")
        return 1

    path = sys.argv[1]
    my_player_id = sys.argv[2]

    try:
        snap = load_recruit_snapshot(path)
        me = snap.get_player(my_player_id)

        print("=== Recruit Snapshot ===")
        print(f"match_id: {snap.match_id}")
        print(f"phase: {snap.phase}  turn: {snap.turn}")
        print(f"player: {me.player_id}")
        print(f"hero: {me.hero.name}  hp: {me.health}  armor: {me.armor}")
        print(f"gold: {me.gold}  tavern_tier: {me.tavern_tier}")
        print(f"timer_ms: {me.timer_ms}")

        board_slots = [b.slot for b in me.board]
        hand_idxs = [h.hand_index for h in me.hand]
        shop_present = [s.slot for s in me.shop if not s.is_empty]

        print(f"board_count: {len(me.board)} slots={board_slots}")
        print(f"hand_count: {len(me.hand)} idxs={hand_idxs}")
        print(f"shop_slots_total: {len(me.shop)} present={shop_present}")

        if me.flags:
            print(f"flags: {me.flags}")

        return 0

    except (StateLoaderError, KeyError) as e:
        print(f"ERROR: {e}")
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
