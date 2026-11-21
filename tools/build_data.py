#!/usr/bin/env python3
"""notes/meta-*.md + notes/unowned.md(없는 카드) + notes/disliked.md(싫어하는 카드) + cache/(SnapVault) -> data.js.

사용:
  python3 tools/fetch_sv.py          # SnapVault 랭크 7일 데이터 갱신 (cache/)
  python3 tools/build_data.py [notes/meta-YYYY-MM-DD.md]
인자 없으면 notes/ 안의 가장 최신 meta-*.md 사용.

- 노트의 플렉스 슬롯(A 또는 B)은 실제 12장 빌드로 펼친다.
- 빌드마다 SnapVault 랭크 7일 통계를 12장 완전 일치로 붙인다. MIN_GAMES 미만 빌드는 제외.
- 미보유 카드가 있는 빌드는 '보유 카드만 쓴 실제 유사 리스트'의 전적을 합산해 예측한다.
"""
import html
import itertools
import json
from datetime import date, datetime, timedelta, timezone
import re
import sys
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
NOTES = ROOT / "notes"
CACHE = ROOT / "cache"

MIN_GAMES = 100   # 랭크 7일 이 판수 미만 빌드는 목록에서 제외 (사용자 요청)
MIN_WR = 58.0     # 랭크 7일 승률이 이 값 이하인 빌드는 제외 (사용자 요청: "58% 이하는 선택 안 함")
EXCLUDED_TIERS = {"C": "티어 C 이하", "UT": "티어 C 이하"}  # 사용자 요청: 옛날 카드 위주라 재미없어서 제외
RECENT_DAYS = 365  # 12장이 모두 이 기간보다 전에 출시된 카드면 제외 (사용자 요청) — 기준일 = 랭크 데이터 수집일
OLD_ONLY = "1년 넘은 카드만"
MIN_PRED = 100    # 미보유 카드 없이 플레이된 같은 계열 판수가 이보다 적으면 예측하지 않음
MIN_SUB = 30      # 대체 후보 카드가 (미보유 카드를 모두 뺀) 같은 계열 리스트에서 쓰인 최소 판수
SAME_ARCH = 8     # 원본 빌드와 12장 중 이만큼 겹치면 같은 계열로 봄
RIDGE_LAMBDA = 200  # 카드 기여도 추정 축소 강도 (가상 판수)
SHRINK_K = 100    # 원본 승률을 같은 계열 평균 쪽으로 당기는 강도 (가상 판수)
CARD_COST = {}    # main에서 채움 (대체 카드 짝 표시용)
REL = {}          # 카드 id → 출시일(date) 또는 None(아주 오래됨). main에서 채움
RECENT_CUT = [date(1970, 1, 1)]  # 이 날짜 이후 출시면 '최근 카드'


def has_recent(ids) -> bool:
    return any(REL.get(c) and REL[c] >= RECENT_CUT[0] for c in ids)

TIER_HEADERS = {
    "### S 티어": "S",
    "### A 티어": "A",
    "### B 티어": "B",
    "### C 티어": "C",
    "### 티어 미부여": "UT",
    "### 참고": "REF",
}

# 노트/컬렉션 표기 -> SnapVault 카드 이름 (정규화로 안 맞는 것만)
ALIASES = {
    "kang the conqueror": "kang",
}


def norm(s: str) -> str:
    s = s.lower().replace("(", " ").replace(")", " ")
    s = re.sub(r"[^a-z0-9 ]", "", s)
    return re.sub(r"\s+", " ", s).strip()


def strip_md(s: str) -> str:
    return s.replace("**", "").strip()


def parse_cards(body: str):
    """'A, B, **X 또는 Y**, C' -> [["A"], ["B"], ["X","Y"], ["C"]]"""
    out = []
    for raw in body.split(","):
        c = strip_md(raw)
        if c:
            out.append([p.strip() for p in c.split(" 또는 ")])
    return out


def is_card_line(s: str) -> bool:
    return s.startswith("- ") and s.count(",") >= 8


def parse_meta(path: Path):
    text = path.read_text(encoding="utf-8")
    sec5 = text.split("## 5.", 1)[1].split("\n## 6.", 1)[0]
    decks, refs = [], []
    tier = None
    cur = None

    for line in sec5.splitlines():
        s = line.strip()
        hit = next((t for h, t in TIER_HEADERS.items() if s.startswith(h)), None)
        if hit:
            tier, cur = hit, None
            continue
        if tier is None:
            continue
        m = re.match(r"\*\*(\d+)\. (.+?)\*\*(.*)$", s)
        if m and tier != "REF":
            no, name, rest = int(m.group(1)), m.group(2).strip(), m.group(3)
            ota = re.findall(r"([⬆⬇])\(([^)]+)\)", rest)
            fam = re.search(r"계열:\s*([^—]+?)(?:,|$)", rest)
            ut_ev = re.search(r"—\s*(UT [^,]+.*)$", rest)
            cur = {
                "no": no, "tier": tier, "name": name,
                "ota": [{"dir": "up" if d == "⬆" else "down", "card": c} for d, c in ota],
                "family": fam.group(1).strip() if fam else None,
                "evidence": [], "lists": [], "notes": [],
            }
            if ut_ev and tier == "UT":
                cur["evidence"].append(re.sub(r",?\s*계열:.*$", "", ut_ev.group(1)).strip())
            decks.append(cur)
            continue
        if tier == "REF" and s.startswith("- **"):
            m = re.match(r"- \*\*(.+?)\*\*(.*?)— (.*?):\s(.+)$", s)
            if m:
                ota = re.findall(r"([⬆⬇])\(([^)]+)\)", m.group(2))
                refs.append({
                    "no": None, "tier": "REF", "name": m.group(1).strip(),
                    "ota": [{"dir": "up" if d == "⬆" else "down", "card": c} for d, c in ota],
                    "family": None, "evidence": [m.group(3).strip()], "notes": [],
                    "lists": [{"label": None, "slots": parse_cards(m.group(4))}],
                })
            continue
        if cur is None:
            continue
        if is_card_line(s):
            body, label = s[2:], None
            vm = re.match(r"\(변형([^)]*)\)\s*(.+)$", body)
            if vm:
                label = ("변형" + (vm.group(1) or "")).strip()
                body = vm.group(2)
            cur["lists"].append({"label": label, "slots": parse_cards(body)})
        elif s.startswith("- 근거:"):
            cur["evidence"].append(strip_md(s[len("- 근거:"):]))
        elif s.startswith("- "):
            cur["notes"].append(strip_md(s[2:]))

    for d in decks + refs:
        for lst in d["lists"]:
            if len(lst["slots"]) != 12:
                raise SystemExit(f"[오류] {d.get('no') or ''} {d['name']} 카드 수 {len(lst['slots'])}장")
    return decks, refs


def parse_table(block: str):
    """마크다운 표 → 행 목록(열 리스트). 머리줄·구분줄 제외."""
    rows = []
    for line in block.splitlines():
        if not line.startswith("|") or set(line.replace("|", "").strip()) <= set("-: "):
            continue
        rows.append([c.strip() for c in line.strip("|").split("|")])
    return rows


def parse_unowned(path: Path):
    """notes/unowned.md — 없는 카드. 4열 표(시즌|카드|코스트/파워|기간) 또는 2열 표(카드|코스트/파워)."""
    text = path.read_text(encoding="utf-8")
    block = text.split("## 미보유 Series 5", 1)[1].split("\n---", 1)[0]
    cards = []
    for cols in parse_table(block):
        if cols[0] in ("시즌", "카드"):
            continue
        name = cols[1] if len(cols) >= 4 else cols[0]
        stat = cols[2] if len(cols) >= 4 else cols[1]
        cards.append({"name": name, "stat": stat})
    upd = re.search(r"마지막 갱신:\s*([0-9-]+)", text)
    return cards, (upd.group(1) if upd else None)


def parse_disliked(path: Path):
    """notes/disliked.md — 싫어하는 카드. 표(카드|표시 이유|메모). 파일이 없으면 빈 목록."""
    if not path.exists():
        return [], None
    text = path.read_text(encoding="utf-8")
    out = []
    for cols in parse_table(text):
        if cols[0] == "카드" or len(cols) < 2:
            continue
        out.append({"name": cols[0], "reason": cols[1] or cols[0], "memo": cols[2] if len(cols) > 2 else ""})
    upd = re.search(r"마지막 갱신:\s*([0-9-]+)", text)
    return out, (upd.group(1) if upd else None)


def parse_substitutes(path: Path):
    """notes/substitutes.md — 데이터로 예측 못 하는 덱에 Claude가 고른 대체 카드.
    {("no", 2) 또는 ("ref", 이름): [{"out", "in", "why"}]}"""
    if not path.exists():
        return {}
    out, key = {}, None
    for line in path.read_text(encoding="utf-8").splitlines():
        m = re.match(r"## #(\d+)\b", line)
        if m:
            key = ("no", int(m.group(1)))
            out[key] = []
            continue
        m = re.match(r"## 참고:\s*(.+)$", line)
        if m:
            key = ("ref", m.group(1).strip())
            out[key] = []
            continue
        if line.startswith("#"):
            key = None
            continue
        m = re.match(r"- (.+?) → (.+?) — (.+)$", line.strip())
        if key and m:
            out[key].append({"out": m.group(1).strip(), "in": m.group(2).strip(), "why": m.group(3).strip()})
    return out


def apply_guess(b, swaps, res, unowned, banned, db_by_sig):
    """예측 불가 빌드에 추측 대체를 적용. 미보유 카드마다 교체가 있어야 하고, 넣는 카드는 보유·비선호 아님·중복 아님."""
    by_out = {}
    for sw in swaps:
        by_out[res.id_of(sw["out"])] = sw
    if not all(m in by_out for m in b["miss"]):
        return None
    ids = set(b["ids"])
    out = []
    for m in b["miss"]:
        sw = by_out[m]
        new = res.id_of(sw["in"])
        if new in unowned or new in banned or new in ids:
            raise SystemExit(f"[오류] substitutes.md: {sw['in']} 은(는) 미보유·싫어하는 카드이거나 이미 덱에 있음")
        ids.discard(m)
        ids.add(new)
        out.append({"out": m, "in": new, "why": sw["why"]})
    hit = db_by_sig.get(frozenset(ids))
    return {"swaps": out, "ids": sorted(ids), "exact": stat_of(hit["stats"]) if hit else None}


def parse_event(path: Path):
    """notes/event-*.md — 이벤트 모드별 덱 또는 드래프트 스타터 팩 노트."""
    text = path.read_text(encoding="utf-8")
    title = text.splitlines()[0].lstrip("# ").strip()
    info, decks, skipped = {}, [], []
    pack_lines, guide, sources = [], [], []
    sec, cur = None, None
    for line in text.splitlines():
        s = line.strip()
        if s.startswith("## "):
            sec, cur = s[3:].strip(), None
            continue
        if sec == "요약":
            m = re.match(r"- ([^:]+):\s*(.+)$", s)
            if m:
                info[m.group(1).strip()] = m.group(2).strip()
        elif sec == "덱":
            m = re.match(r"### (\d+)\. (.+)$", s)
            if m:
                cur = {"no": int(m.group(1)), "name": m.group(2).strip(), "orig": None, "cards": None,
                       "swaps": [], "notes": []}
                decks.append(cur)
                continue
            if not cur or not s.startswith("- "):
                continue
            if s.startswith("- 원본:"):
                m = re.match(r"- 원본:\s*([\d.]+)%\s*·\s*([\d,]+)판\s*·\s*([\d,]+)명(?:\s*·\s*(.+))?$", s)
                if not m:
                    raise SystemExit(f"[오류] {path.name} #{cur['no']} 원본 줄 형식: {s}")
                cur["orig"] = {"wr": float(m.group(1)), "games": int(m.group(2).replace(",", "")),
                               "players": int(m.group(3).replace(",", "")), "note": (m.group(4) or "").strip()}
            elif s.startswith("- 카드:"):
                cur["cards"] = [c.strip() for c in s[len("- 카드:"):].split(",") if c.strip()]
            elif s.startswith("- 대체("):
                m = re.match(r"- 대체\((데이터|추측)\):\s*(.+?) → (.+?) — (.+)$", s)
                if not m:
                    raise SystemExit(f"[오류] {path.name} #{cur['no']} 대체 줄 형식: {s}")
                cur["swaps"].append({"kind": "data" if m.group(1) == "데이터" else "guess",
                                     "out": m.group(2).strip(), "in": m.group(3).strip(), "why": m.group(4).strip()})
            elif s.startswith("- 메모:"):
                cur["notes"].append(strip_md(s[len("- 메모:"):]))
        elif sec == "고르지 않은 상위 덱" and s.startswith("- "):
            skipped.append(strip_md(s[2:]))
        elif sec == "스타터 팩" and s.startswith("|"):
            pack_lines.append(s)
        elif sec == "픽 가이드" and s.startswith("- "):
            guide.append(strip_md(s[2:]))
        elif sec == "출처":
            m = re.fullmatch(r"- \[([^\]]+)\]\((https://[^\s)]+)\)", s)
            if m:
                sources.append({"label": m[1], "url": m[2]})
    dates = re.findall(r"\d{4}-\d{2}-\d{2}", info.get("기간", ""))
    filename = re.fullmatch(r"event-(.+)-(\d{4}-\d{2}-\d{2})", path.stem)
    if not filename:
        raise SystemExit(f"[오류] 이벤트 노트 파일명: {path.name}")
    event = {"file": path.name, "mode": filename[1], "asOf": filename[2], "title": title,
             "info": info, "start": dates[0] if dates else None, "end": dates[1] if len(dates) > 1 else None,
             "decks": decks, "skipped": skipped}
    if pack_lines:
        packs = []
        for row in parse_table("\n".join(pack_lines)):
            if row[0] == "팩":
                continue
            if len(row) not in (4, 5):
                raise SystemExit(f"[오류] {path.name} 스타터 팩: 4열 또는 운영법 포함 5열 필요 — {row}")
            name, cards, match, run, *play = row
            pack = {"name": name, "cards": cards, "match": match, "run": run}
            if play and play[0]:
                pack["play"] = strip_md(play[0])
            packs.append(pack)
        event.update({"packs": packs, "guide": guide, "sources": sources})
    return event


def build_events(res, unowned, banned):
    """이벤트 노트 → 페이지용 데이터. 미보유 카드는 모두 대체돼야 하고, 넣는 카드는 보유·비선호 아님·이벤트 금지 아님."""
    events = []
    name_ids = {c["name"]: cid for cid, c in res.by_id.items()}
    name_options = "|".join(re.escape(name) for name in sorted(name_ids, key=len, reverse=True))
    card_pattern = re.compile(rf"(?<![a-zA-Z0-9])({name_options})(?![a-zA-Z0-9])")
    for path in sorted(NOTES.glob("event-*.md"), key=lambda p: p.stem[-10:], reverse=True):
        ev = parse_event(path)
        for pack in ev.get("packs", []):
            pack["ids"] = [res.id_of(name) for name in [pack["name"], *pack["cards"].split(" · ")]]
            if len(set(pack["ids"])) != 3:
                raise SystemExit(f"[오류] {path.name} {pack['name']}: 스타터 카드 3장이 필요합니다.")
        if "guide" in ev:
            ev["guide"] = [{"text": tip, "ids": list(dict.fromkeys(name_ids[name] for name in card_pattern.findall(tip)))}
                           for tip in ev["guide"]]
        ev_banned = [res.id_of(n) for n in ev["info"].get("금지 카드", "").split(",")
                     if norm(n) in res.by_norm]
        if ev_banned:
            ev["bannedIds"] = ev_banned
        ev_banned = set(ev_banned)
        for d in ev["decks"]:
            where = f"{path.name} #{d['no']} {d['name']}"
            if not d["orig"] or not d["cards"]:
                raise SystemExit(f"[오류] {where}: 원본·카드 줄이 없음")
            ids = [res.id_of(n) for n in d["cards"]]
            if len(set(ids)) != 12:
                raise SystemExit(f"[오류] {where}: 카드 {len(set(ids))}장 (12장이어야 함)")
            alt, swaps = set(ids), []
            for sw in d["swaps"]:
                o, n = res.id_of(sw["out"]), res.id_of(sw["in"])
                if o not in alt:
                    raise SystemExit(f"[오류] {where}: 빠지는 카드 {sw['out']} 이(가) 덱에 없음")
                if n in unowned or n in banned or n in ev_banned or n in alt:
                    raise SystemExit(f"[오류] {where}: {sw['in']} 은(는) 미보유·싫어하는 카드·이벤트 금지 카드이거나 이미 덱에 있음")
                alt.discard(o)
                alt.add(n)
                swaps.append({"kind": sw["kind"], "out": o, "in": n, "why": sw["why"]})
            left = sorted(c for c in alt if c in unowned or c in banned or c in ev_banned)
            if left:
                raise SystemExit(f"[오류] {where}: 대체 후에도 못 쓰는 카드가 남음 — {', '.join(left)}")
            d.update({"ids": ids, "miss": sorted(c for c in ids if c in unowned),
                      "alt": {"ids": sorted(alt), "swaps": swaps} if swaps else None})
            for k in ("cards", "swaps"):
                d.pop(k)
        events.append(ev)
    return events


def load_cache():
    try:
        cards = json.loads((CACHE / "sv_cards.json").read_text(encoding="utf-8"))
        ranked = json.loads((CACHE / "sv_ranked7.json").read_text(encoding="utf-8"))
        ut = json.loads((CACHE / "ut_cards.json").read_text(encoding="utf-8"))
    except FileNotFoundError:
        raise SystemExit("[오류] cache/ 가 없거나 오래됐습니다. 먼저 python3 tools/fetch_sv.py 를 실행하세요.")
    return cards, ranked, ut


def release_dates(ut_cards):
    """Untapped seriesStartTimestamps 첫 값 = 출시일. 0001-01-01(추적 이전) 이나 값 없음 = None(아주 오래됨)."""
    out = {}
    for c in ut_cards:
        ts = c.get("seriesStartTimestamps") or []
        d = None
        if ts:
            try:
                d = datetime.fromtimestamp(ts[0] / 1000, timezone.utc).date()
            except (OverflowError, OSError, ValueError):
                d = None
            if d and d.year < 2000:
                d = None
        out[c["defId"]] = d
    return out


class Resolver:
    def __init__(self, sv_cards):
        self.by_norm = {norm(c["name"]): c for c in sv_cards if not c.get("isToken")}
        self.by_id = {c["id"]: c for c in sv_cards}

    def id_of(self, name: str) -> str:
        key = norm(name)
        key = ALIASES.get(key, key)
        c = self.by_norm.get(key)
        if not c:
            raise SystemExit(f"[오류] SnapVault 카드 목록에서 '{name}' 을(를) 찾지 못함 → ALIASES 에 추가")
        return c["id"]


def stat_of(st):
    g = st["totalGames"]
    return {
        "games": g,
        "wins": st["wins"],
        "wr": round(100 * st["wins"] / g, 1) if g else None,
        "cubes": round(st["totalCubes"] / st["cubeGames"], 2) if st.get("cubeGames") else None,
    }


def ridge_effects(rows, lam=RIDGE_LAMBDA, max_sweeps=3000, tol=1e-9):
    """가중 릿지 회귀 (좌표 하강). rows = [(카드 set, 승률 0~1, 가중치)].
    승률 ≈ b0 + Σ β_card. 반환: {card: β} (승률 단위, 0.01 = 1%p).
    카드 순서를 정렬하고 변화량이 tol 아래로 내려갈 때까지 반복 → 실행마다 같은 결과."""
    beta = Counter()
    sw = sum(w for _, _, w in rows)
    b0 = sum(y * w for _, y, w in rows) / sw
    resid = [y - b0 for _, y, _ in rows]
    by_card = {}
    for i, (s, _, w) in enumerate(rows):
        for c in sorted(s):
            by_card.setdefault(c, []).append(i)
    order = sorted(by_card)
    denom = {c: sum(rows[i][2] for i in by_card[c]) + lam for c in order}
    for _ in range(max_sweeps):
        biggest = 0.0
        for c in order:
            idx = by_card[c]
            old = beta[c]
            new = sum(rows[i][2] * (resid[i] + old) for i in idx) / denom[c]
            d = new - old
            if d:
                for i in idx:
                    resid[i] -= d
                beta[c] = new
                biggest = max(biggest, abs(d))
        shift = sum(rows[i][2] * resid[i] for i in range(len(rows))) / sw
        if shift:
            b0 += shift
            resid = [r - shift for r in resid]
        if biggest < tol and abs(shift) < tol:
            break
    return beta


def predict(ids, st_now, unowned, db, avoid=frozenset()):
    """미보유 카드를 보유 카드로 바꿨을 때의 랭크 승률 추정 (트래커 기반 참고 추정).
    1) 같은 계열 = 이 빌드와 SAME_ARCH장 이상 겹치는 랭크 7일 리스트
    2) 근거 확인: 미보유 카드 각각, 그리고 미보유 카드를 '모두' 뺀 같은 계열 전적이 MIN_PRED판 이상이어야 함
    3) 대체 카드 = 미보유 카드를 모두 뺀 같은 계열 리스트에 실제로 가장 많이 들어간 보유 카드 (MIN_SUB판 이상)
       → 함께 쓰인 조합에서 고르므로 동시 사용 근거가 있고, 카드별 탐욕 선택의 실패도 없음
    4) 카드별 기여도 = 이 빌드와 6장 이상 겹치는 리스트로 가중 릿지 회귀
    5) 기준 승률 = 원본 승률을 같은 계열 평균 쪽으로 축소 (원본 판수가 적을수록 더 많이)
    6) 예측 = 기준 승률 + Σ(들어가는 카드 기여 − 빠지는 카드 기여), 기준 승률보다 높게는 잡지 않음"""
    S = set(ids)
    miss = sorted(S & unowned)
    core = S - set(miss)
    arch = [x for x in db if len(x["set"] & S) >= SAME_ARCH]
    arch_games = sum(x["stats"]["totalGames"] for x in arch)
    arch_wins = sum(x["stats"]["wins"] for x in arch)
    base = {"archLists": len(arch), "archGames": arch_games}

    per_card = [{"id": m, "without": sum(x["stats"]["totalGames"] for x in arch if m not in x["set"])} for m in miss]
    lacking_all = [x for x in arch if not (x["set"] & set(miss))]
    without_all = sum(x["stats"]["totalGames"] for x in lacking_all)
    thin = [c for c in per_card if c["without"] < MIN_PRED]
    if thin or without_all < MIN_PRED:
        return {"ok": False, "reason": "thin", "perCard": per_card, "withoutAll": without_all, **base}

    use = Counter()
    for x in lacking_all:
        for c in sorted(x["set"] - core):
            if c not in unowned and c not in avoid:  # 미보유·제외 카드(매직 등)는 대체 후보에서 뺌
                use[c] += x["stats"]["totalGames"]
    cand = sorted(((c, g) for c, g in use.items() if g >= MIN_SUB), key=lambda cg: (-cg[1], cg[0]))
    if len(cand) < len(miss):
        return {"ok": False, "reason": "nosub", "perCard": per_card, "withoutAll": without_all,
                "subsFound": len(cand), **base}
    subs = [c for c, _ in cand[:len(miss)]]
    used = dict(cand)

    rows = [(x["set"], x["stats"]["wins"] / x["stats"]["totalGames"],
             x["stats"]["totalGames"] * (len(x["set"] & S) / 12) ** 3)
            for x in db if len(x["set"] & S) >= 6]
    beta = ridge_effects(rows)

    # 표시용 짝: 코스트가 가까운 것끼리
    left, swaps = list(subs), []
    for m in sorted(miss, key=lambda c: -CARD_COST.get(c, 0)):
        i = min(left, key=lambda c: (abs(CARD_COST.get(c, 0) - CARD_COST.get(m, 0)), c))
        left.remove(i)
        swaps.append({"out": m, "in": i, "used": used[i], "d": round(100 * (beta[i] - beta[m]), 1)})

    arch_wr = arch_wins / arch_games
    anchor = (st_now["wins"] + SHRINK_K * arch_wr) / (st_now["games"] + SHRINK_K)
    raw = 100 * sum(beta[s["in"]] - beta[s["out"]] for s in swaps)
    delta = min(0.0, raw)
    replaced = sorted(core | set(subs))
    exact = next((x for x in db if x["set"] == frozenset(replaced)), None)
    return {
        "ok": True, "anchor": round(100 * anchor, 1), "archWr": round(100 * arch_wr, 1),
        "wr": round(100 * anchor + delta, 1), "delta": round(delta, 1), "rawDelta": round(raw, 1),
        "swaps": swaps, "ids": replaced, "withoutAll": without_all, "perCard": per_card,
        "exact": stat_of(exact["stats"]) if exact else None, **base,
    }


def build_deck(d, res, unowned, banned, db_by_sig, db):
    builds = []
    for lst in d["lists"]:
        names_opts = lst["slots"]
        flex_idx = [i for i, o in enumerate(names_opts) if len(o) > 1]
        for combo in itertools.product(*names_opts):
            ids = [res.id_of(n) for n in combo]
            if len(set(ids)) != 12:
                continue  # 플렉스 선택지가 다른 슬롯과 겹치는 조합만 건너뜀
            label_parts = [lst["label"]] if lst["label"] else []
            if flex_idx:
                label_parts.append(" · ".join(combo[i] for i in flex_idx) + " 빌드")
            hit = db_by_sig.get(frozenset(ids))
            b = {
                "label": " / ".join(label_parts) or None,
                "ids": ids,
                "stats": stat_of(hit["stats"]) if hit else None,
                "miss": sorted(set(ids) & unowned),
            }
            b["banned"] = sorted({banned[c] for c in ids if c in banned})
            b["oldOnly"] = not has_recent(ids)
            b["included"] = (bool(b["stats"] and b["stats"]["games"] >= MIN_GAMES)
                             and b["stats"]["wr"] > MIN_WR and not b["banned"] and not b["oldOnly"])
            if b["included"] and b["miss"]:
                b["pred"] = predict(ids, b["stats"], unowned, db, avoid=set(banned))
            builds.append(b)
    if not builds:
        raise SystemExit(f"[오류] {d['name']} 유효한 12장 조합 없음 (중복 카드)")
    return builds


def main():
    meta = Path(sys.argv[1]) if len(sys.argv) > 1 else sorted(NOTES.glob("meta-*.md"))[-1]
    as_of = re.search(r"meta-(\d{4}-\d{2}-\d{2})", meta.name).group(1)
    decks, refs = parse_meta(meta)
    unowned_list, coll_date = parse_unowned(NOTES / "unowned.md")
    banned_list, disliked_date = parse_disliked(NOTES / "disliked.md")
    guesses = parse_substitutes(NOTES / "substitutes.md")
    sv_cards, ranked, ut_cards = load_cache()
    res = Resolver(sv_cards)
    ko_path = CACHE / "ut_cards_ko.json"
    if not ko_path.exists():
        raise SystemExit("[오류] 한국어 카드 캐시가 없습니다. 먼저 python3 tools/fetch_sv.py 를 실행하세요.")
    ko_cards = {c["defId"]: c for c in json.loads(ko_path.read_text(encoding="utf-8"))}
    card_names = {}
    for cid, c in res.by_id.items():
        ko_name = ko_cards.get(cid, {}).get("name", "")
        if re.search(r"[가-힣]", ko_name):
            card_names[c["name"]] = ko_name
    REL.update(release_dates(ut_cards))
    fetched = datetime.fromisoformat(ranked["fetchedAt"]).date()
    RECENT_CUT[0] = fetched - timedelta(days=RECENT_DAYS)
    CARD_COST.update({c["id"]: c["cost"] for c in sv_cards})

    for u in unowned_list:
        u["id"] = res.id_of(u["name"])
    unowned = {u["id"] for u in unowned_list}
    banned = {res.id_of(b["name"]): b["reason"] for b in banned_list}

    db = []
    for x in ranked["decks"]:
        db.append({"set": frozenset(x["cardIds"]), "stats": x["stats"]})
    db_by_sig = {x["set"]: x for x in db}

    out_decks, excluded = [], []
    note_sets = set()  # 노트에 있는 모든 빌드 (제외된 것 포함) — 발견 덱에 다시 나오지 않게
    for d in decks + refs:
        builds = build_deck(d, res, unowned, banned, db_by_sig, db)
        note_sets.update(frozenset(b["ids"]) for b in builds)
        inc = [b for b in builds if b["included"]]
        lists = d.pop("lists")
        tier_reason = EXCLUDED_TIERS.get(d["tier"])
        if tier_reason:
            inc = []

        def why(b):
            r = ([tier_reason] if tier_reason else []) + ([OLD_ONLY] if b["oldOnly"] else []) + list(b["banned"])
            if not (b["stats"] and b["stats"]["games"] >= MIN_GAMES):
                r.append(f"랭크 7일 {MIN_GAMES}판 미만")
            elif b["stats"]["wr"] <= MIN_WR:
                r.append(f"승률 {MIN_WR:g}% 이하")
            return r
        if not inc:
            reasons = []
            for b in builds:
                for r in why(b):
                    if r not in reasons:
                        reasons.append(r)
            excluded.append({
                "no": d["no"], "tier": d["tier"], "name": d["name"],
                "games": max((b["stats"]["games"] if b["stats"] else 0) for b in builds),
                "reasons": reasons,
            })
            continue
        d["builds"] = inc
        d["droppedBuilds"] = [{"label": b["label"], "games": b["stats"]["games"] if b["stats"] else 0,
                               "reasons": why(b)} for b in builds if not b["included"]]
        out_decks.append(d)

    # 서로 다른 원본에서 같은 대체 12장이 나오면 예측값을 하나로 통일 (원본 판수가 가장 많은 쪽 기준)
    best_rep = {}
    for d in out_decks:
        for b in d["builds"]:
            p = b.get("pred")
            if p and p["ok"]:
                k = tuple(sorted(p["ids"]))
                if k not in best_rep or b["stats"]["games"] > best_rep[k][0]:
                    best_rep[k] = (b["stats"]["games"], p)
    for d in out_decks:
        for b in d["builds"]:
            p = b.get("pred")
            if p and p["ok"]:
                src = best_rep[tuple(sorted(p["ids"]))][1]
                if src is not p:
                    for f in ("wr", "anchor", "delta", "rawDelta", "archWr"):
                        p[f] = src[f]
                    p["shared"] = True

    # 데이터로 예측 못 한 빌드에 Claude 추측 대체 적용
    for d in out_decks:
        swaps = guesses.get(("no", d["no"])) if d["no"] else guesses.get(("ref", d["name"]))
        for b in d["builds"]:
            p = b.get("pred")
            if swaps and b["miss"] and p and not p["ok"]:
                g = apply_guess(b, swaps, res, unowned, set(banned), db_by_sig)
                if g:
                    b["guess"] = g
                else:
                    print(f"  [주의] #{d['no']} {d['name']} 추측 대체가 미보유 카드를 다 덮지 못함")

    # 발견 덱: 노트 목록 밖이지만 내 카드만으로 바로 만들 수 있고 같은 조건(판수·승률·싫어하는 카드)을 통과하는 랭크 7일 리스트
    inc_sets = [(d, frozenset(b["ids"])) for d in out_decks for b in d["builds"]]
    discovered = []
    for x in db:
        st = stat_of(x["stats"])
        if (st["games"] < MIN_GAMES or st["wr"] <= MIN_WR or (x["set"] & unowned) or (x["set"] & set(banned))
                or not has_recent(x["set"])):
            continue
        if x["set"] in note_sets:
            continue  # 노트에 있는 빌드 (목록에 있거나, 티어·매직 등으로 일부러 뺀 것)
        near_d, ov = max(((d, len(x["set"] & s_)) for d, s_ in inc_sets), key=lambda t: t[1], default=(None, 0))
        ids = sorted(x["set"])
        key = sorted(ids, key=lambda c: (-res.by_id[c]["cost"], -res.by_id[c]["power"], res.by_id[c]["name"]))[:3]
        discovered.append({
            "name": " · ".join(res.by_id[c]["name"] for c in key),
            "ids": ids, "stats": st,
            "similar": {"no": near_d["no"], "name": near_d["name"], "overlap": ov} if near_d and ov >= 9 else None,
        })

    events = build_events(res, unowned, set(banned))

    page = (ROOT / "index.html").read_text(encoding="utf-8")
    page_cards = set(re.findall(r'\bdata-card="([A-Za-z0-9]+)"', page))
    abilities = set(re.findall(r'\bdata-card-ability="([A-Za-z0-9]+)"', page))
    used = page_cards | abilities
    if missing := used - res.by_id.keys():
        raise SystemExit(f"[오류] 페이지 카드 ID를 찾을 수 없습니다. {', '.join(sorted(missing))}")
    for ev in events:
        for pack in ev.get("packs", []):
            used.update(pack["ids"])
        for tip in ev.get("guide", []):
            used.update(tip["ids"])
        used.update(ev.get("bannedIds", []))
        for d in ev["decks"]:
            used |= set(d["ids"])
            if d["alt"]:
                used |= set(d["alt"]["ids"])
    for x in discovered:
        used |= set(x["ids"])
    for d in out_decks:
        for b in d["builds"]:
            used |= set(b["ids"])
            if b.get("pred") and b["pred"]["ok"]:
                used |= set(b["pred"]["ids"])
            if b.get("guess"):
                used |= set(b["guess"]["ids"])
    used |= unowned
    used |= set(banned)
    cards = {
        cid: {"name": res.by_id[cid]["name"], "cost": res.by_id[cid]["cost"],
              "power": res.by_id[cid]["power"], "code": res.by_id[cid]["deckCode"],
              "rel": REL[cid].isoformat() if REL.get(cid) else None}
        for cid in sorted(used)
    }
    for cid in abilities:
        detail = ko_cards.get(cid, {}).get("description") or res.by_id[cid].get("ability") or ""
        cards[cid]["ability"] = html.unescape(re.sub(r"<[^>]+>", "", detail))
    key = lambda c: (cards[c]["cost"], cards[c]["name"])
    for ev in events:
        for d in ev["decks"]:
            d["ids"].sort(key=key)
            if d["alt"]:
                d["alt"]["ids"].sort(key=key)
    for d in out_decks:  # 코스트 → 이름 순 정렬 (화면·덱 코드 공통)
        for x in discovered:
            x["ids"].sort(key=key)
        for b in d["builds"]:
            b["ids"].sort(key=key)
            if b.get("pred") and b["pred"]["ok"]:
                b["pred"]["ids"].sort(key=key)
            if b.get("guess"):
                b["guess"]["ids"].sort(key=key)

    data = {
        "asOf": as_of,
        "collectionUpdated": coll_date,
        "rankedSource": {"site": "SnapVault", "window": "7일", "mode": "랭크", "fetchedAt": ranked["fetchedAt"],
                         "minGames": MIN_GAMES, "minWr": MIN_WR, "minPred": MIN_PRED,
                         "recentCut": RECENT_CUT[0].isoformat(), "lists": len(db)},
        "cards": cards,
        "cardNames": card_names,
        "decks": out_decks,
        "excluded": excluded,
        "discovered": discovered,
        "unowned": [{"id": u["id"], "name": u["name"], "stat": u["stat"]} for u in unowned_list],
        "banned": [{"id": res.id_of(b["name"]), "name": b["name"], "reason": b["reason"], "memo": b["memo"]}
                   for b in banned_list],
        "dislikedUpdated": disliked_date,
        "events": events,
    }
    out = ROOT / "data.js"
    out.write_text(
        "// tools/build_data.py 로 생성 — 직접 수정하지 말 것\n"
        "window.SNAP_DATA = " + json.dumps(data, ensure_ascii=False, separators=(",", ":")) + ";\n",
        encoding="utf-8",
    )
    n_main = sum(1 for d in out_decks if d["tier"] != "REF")
    n_pred = sum(1 for d in out_decks for b in d["builds"] if b.get("pred", {}).get("ok"))
    n_nopred = sum(1 for d in out_decks for b in d["builds"] if b["miss"] and not b.get("pred", {}).get("ok"))
    n_guess = sum(1 for d in out_decks for b in d["builds"] if b.get("guess"))
    print(f"{meta.name}: 표시 덱 {n_main}개 (+참고 {len(out_decks) - n_main}), 제외 {len(excluded)}개, "
          f"예측 {n_pred}빌드 / 예측 불가 {n_nopred}빌드(추측 대체 {n_guess}), 발견 덱 {len(discovered)}개, 카드 {len(cards)}장 -> {out}")
    for e in excluded:
        print(f"  제외: #{e['no']} {e['name']} ({e['games']}판) — {', '.join(e['reasons'])}")
    for ev in events:
        count = f"팩 {len(ev['packs'])}개" if ev.get("packs") else f"덱 {len(ev['decks'])}개"
        print(f"  이벤트: {ev['file']} ({ev['start']} ~ {ev['end']}) {count}")


if __name__ == "__main__":
    main()
