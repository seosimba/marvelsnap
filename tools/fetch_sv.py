#!/usr/bin/env python3
"""SnapVault 공개 API에서 카드 목록과 랭크 7일 덱 통계를 받아 cache/ 에 저장.

사용: python3 tools/fetch_sv.py
- cache/sv_cards.json   : 카드 id, 이름, 코스트, 덱 코드용 deckCode
- cache/sv_ranked7.json : 랭크(ranked + ranked_infinite) 최근 7일, 10판 이상 덱의 12장 구성과 승패·큐브
- cache/ut_cards.json   : Untapped 카드 데이터 (seriesStartTimestamps 첫 값 = 출시일, 0001-01-01 = 아주 오래된 카드)
cache/ 는 커밋하지 않는다 (gitignore). build_data.py 가 읽어서 data.js 에 필요한 값만 넣는다.
"""
import json
import time
import urllib.request
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
CACHE = ROOT / "cache"
BASE = "https://www.snapvault.app/api"
UA = {"User-Agent": "Mozilla/5.0"}
MIN_GAMES = 10
PAGE = 100


def get(url, timeout=90, tries=3):
    for i in range(tries):
        try:
            with urllib.request.urlopen(urllib.request.Request(url, headers=UA), timeout=timeout) as r:
                return json.load(r)
        except Exception as e:  # 네트워크 일시 오류만 재시도
            if i == tries - 1:
                raise
            print(f"  재시도 {i + 1}: {e}")
            time.sleep(3)


def main():
    CACHE.mkdir(exist_ok=True)
    cards = get(f"{BASE}/cards/minimal-for-matches")
    (CACHE / "sv_cards.json").write_text(json.dumps(cards, ensure_ascii=False), encoding="utf-8")
    print(f"카드 {len(cards)}장")

    decks, off = {}, 0
    while True:
        url = (f"{BASE}/decks/public?statsWindow=7d&mode=ranked&minGames={MIN_GAMES}&minPlayers=1"
               f"&hideStale=false&limit={PAGE}&offset={off}&sortBy=confidence&sortDirection=desc")
        d = get(url)
        for x in d["decks"]:
            decks[x["cardSignature"]] = {"cardIds": x["cardIds"], "stats": x["matchStats"], "players": x.get("playerCount")}
        off += PAGE
        if not d["hasMore"] or off >= 10000:
            break
        time.sleep(0.5)  # 서버 부담 줄이기
    ut = get("https://snapjson.untapped.gg/v2/latest/en/cards.json")
    (CACHE / "ut_cards.json").write_text(json.dumps(ut, ensure_ascii=False), encoding="utf-8")
    print(f"Untapped 카드 {len(ut)}장 (출시일용)")

    out = {"fetchedAt": datetime.now(timezone.utc).isoformat(timespec="seconds"),
           "window": "7d", "mode": "ranked", "minGames": MIN_GAMES, "decks": list(decks.values())}
    (CACHE / "sv_ranked7.json").write_text(json.dumps(out, ensure_ascii=False), encoding="utf-8")
    print(f"랭크 7일 덱 {len(decks)}개 ({MIN_GAMES}판 이상)")


if __name__ == "__main__":
    main()
