#!/usr/bin/env python3
"""notes/meta-*.md + notes/collection.md -> data.js (페이지용 데이터).

사용: python3 tools/build_data.py [notes/meta-YYYY-MM-DD.md]
인자 없으면 notes/ 안의 가장 최신 meta-*.md 사용.
"""
import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
NOTES = ROOT / "notes"

TIER_HEADERS = {
    "### S 티어": "S",
    "### A 티어": "A",
    "### B 티어": "B",
    "### C 티어": "C",
    "### 티어 미부여": "UT",
    "### 참고": "REF",
}

# collection.md 표기 -> 덱 리스트 표기
NAME_FIX = {
    "Death (Fractured Frontier)": "Death Fractured Frontier",
    "Storm (부제 있는 변형판)": "Storm (variant)",
}


def strip_md(s: str) -> str:
    return s.replace("**", "").strip()


def parse_cards(body: str):
    """'A, B, **X 또는 Y**, C' -> [{"name": "A"}, {"options": ["X","Y"]}, ...]"""
    out = []
    for raw in body.split(","):
        c = strip_md(raw)
        if not c:
            continue
        if " 또는 " in c:
            out.append({"options": [p.strip() for p in c.split(" 또는 ")]})
        else:
            out.append({"name": c})
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
        for h, t in TIER_HEADERS.items():
            if s.startswith(h):
                tier = t
                cur = None
                break
        else:
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
                    ev = re.sub(r",?\s*계열:.*$", "", ut_ev.group(1)).strip()
                    cur["evidence"].append(ev)
                decks.append(cur)
                continue
            if tier == "REF" and s.startswith("- **"):
                m = re.match(r"- \*\*(.+?)\*\*(.*?)— (.*?):\s(.+)$", s)
                if m:
                    ota = re.findall(r"([⬆⬇])\(([^)]+)\)", m.group(2))
                    refs.append({
                        "name": m.group(1).strip(),
                        "ota": [{"dir": "up" if d == "⬆" else "down", "card": c} for d, c in ota],
                        "evidence": [m.group(3).strip()],
                        "lists": [{"label": None, "cards": parse_cards(m.group(4))}],
                    })
                continue
            if cur is None:
                continue
            if is_card_line(s):
                body = s[2:]
                label = None
                vm = re.match(r"\(변형([^)]*)\)\s*(.+)$", body)
                if vm:
                    label = "변형" + (vm.group(1) or "")
                    body = vm.group(2)
                cur["lists"].append({"label": label, "cards": parse_cards(body)})
            elif s.startswith("- 근거:"):
                cur["evidence"].append(strip_md(s[len("- 근거:"):]))
            elif s.startswith("- "):
                cur["notes"].append(strip_md(s[2:]))

    for d in decks + refs:
        for lst in d["lists"]:
            n = len(lst["cards"])
            if n != 12:
                raise SystemExit(f"[오류] {d.get('no', '')} {d['name']} 카드 수 {n}장")
    return decks, refs


def parse_collection(path: Path):
    text = path.read_text(encoding="utf-8")
    block = text.split("## 미보유 Series 5", 1)[1].split("\n---", 1)[0]
    cards = []
    for line in block.splitlines():
        if not line.startswith("|") or "---" in line:
            continue
        cols = [c.strip() for c in line.strip("|").split("|")]
        if cols[0] in ("시즌", "카드"):
            continue
        # 4열 표(시즌|카드|코스트/파워|기간) 또는 2열 표(카드|코스트/파워)
        name = cols[1] if len(cols) >= 4 else cols[0]
        stat = cols[2] if len(cols) >= 4 else cols[1]
        name = NAME_FIX.get(name, name)
        cards.append({"name": name, "stat": stat})
    upd = re.search(r"마지막 갱신:\s*([0-9-]+)", text)
    return cards, (upd.group(1) if upd else None)


def main():
    if len(sys.argv) > 1:
        meta = Path(sys.argv[1])
    else:
        meta = sorted(NOTES.glob("meta-*.md"))[-1]
    as_of = re.search(r"meta-(\d{4}-\d{2}-\d{2})", meta.name).group(1)
    decks, refs = parse_meta(meta)
    unowned, coll_date = parse_collection(NOTES / "collection.md")
    data = {
        "asOf": as_of,
        "collectionUpdated": coll_date,
        "decks": decks,
        "refs": refs,
        "unowned": unowned,
    }
    out = ROOT / "data.js"
    out.write_text(
        "// tools/build_data.py 로 생성 — 직접 수정하지 말 것\n"
        "window.SNAP_DATA = " + json.dumps(data, ensure_ascii=False, indent=1) + ";\n",
        encoding="utf-8",
    )
    tiers = {}
    for d in decks:
        tiers[d["tier"]] = tiers.get(d["tier"], 0) + 1
    print(f"{meta.name}: 덱 {len(decks)}개 {tiers}, 참고 {len(refs)}개, 미보유 {len(unowned)}장 -> {out}")


if __name__ == "__main__":
    main()
