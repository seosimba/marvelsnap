# codex advisor artifact

- Provider: codex
- Exit code: 0
- Created at: 2026-11-14T09:29:33.468Z

## Original task

You are reviewing changes in the repo at /Users/mac_al03241630/Project/marvelsnap (a personal Marvel Snap deck-notes static page; Korean UI). Files: tools/fetch_sv.py (fetches SnapVault public API: cards + ranked 7-day deck stats into cache/), tools/build_data.py (parses notes/*.md, matches each 12-card deck build exactly against ranked 7d data, excludes builds <100 games, and for builds containing cards the user does not own computes a predicted win rate in predict(): same-archetype = lists sharing >=8 cards; if games played WITHOUT the missing card in that archetype <100 => 'engine card, no prediction'; substitute = most-played owned card in archetype lists lacking the missing card (>=50 games); card effects from weighted ridge regression (coordinate descent) on lists sharing >=6 cards, weight=games*(overlap/12)^3, lambda=200; prediction = actual wr + sum(beta_in - beta_out), capped at actual), index.html (renders data.js: card image grid from Untapped CDN, deck code copy = base64 of comma-joined per-card codes, sort by 'my expected win rate', filters). Generated data.js is present; cache/ has the raw data. Please review for: (1) correctness bugs in build_data.py (esp. predict/ridge_effects, flex-slot expansion, exclusion logic) and index.html JS (sorting, filters, toggles, copy, XSS via esc), (2) statistical soundness / misleading presentation of the prediction and suggest concrete improvements that are cheap, (3) anything in the UI text that overclaims. Run the scripts if useful (python3 tools/build_data.py; node is available). Do NOT modify files. Reply in Korean, findings ranked by severity with file:line, each with a concrete fix. Be concise.

## Final prompt

You are reviewing changes in the repo at /Users/mac_al03241630/Project/marvelsnap (a personal Marvel Snap deck-notes static page; Korean UI). Files: tools/fetch_sv.py (fetches SnapVault public API: cards + ranked 7-day deck stats into cache/), tools/build_data.py (parses notes/*.md, matches each 12-card deck build exactly against ranked 7d data, excludes builds <100 games, and for builds containing cards the user does not own computes a predicted win rate in predict(): same-archetype = lists sharing >=8 cards; if games played WITHOUT the missing card in that archetype <100 => 'engine card, no prediction'; substitute = most-played owned card in archetype lists lacking the missing card (>=50 games); card effects from weighted ridge regression (coordinate descent) on lists sharing >=6 cards, weight=games*(overlap/12)^3, lambda=200; prediction = actual wr + sum(beta_in - beta_out), capped at actual), index.html (renders data.js: card image grid from Untapped CDN, deck code copy = base64 of comma-joined per-card codes, sort by 'my expected win rate', filters). Generated data.js is present; cache/ has the raw data. Please review for: (1) correctness bugs in build_data.py (esp. predict/ridge_effects, flex-slot expansion, exclusion logic) and index.html JS (sorting, filters, toggles, copy, XSS via esc), (2) statistical soundness / misleading presentation of the prediction and suggest concrete improvements that are cheap, (3) anything in the UI text that overclaims. Run the scripts if useful (python3 tools/build_data.py; node is available). Do NOT modify files. Reply in Korean, findings ranked by severity with file:line, each with a concrete fix. Be concise.

## Raw output

```text
파일은 수정하지 않았습니다. 생성 출력을 메모리로 받아 재현한 결과이며, 심각도순입니다.

1. **[높음] 여러 카드의 동시 교체 근거를 확인하지 않습니다.** [build_data.py:227](/Users/mac_al03241630/Project/marvelsnap/tools/build_data.py:227)  
   카드별 부재 표본만 검사해, #19는 **미보유 카드를 모두 뺀 같은 계열 전적이 0판**인데도 55.0%·55.2%를 예측합니다. **수정:** 모든 미보유 카드가 동시에 없는 표본에도 100판 기준을 적용하고, 선택한 대체 카드의 동시 사용 표본도 확인하세요.

2. **[중간] 원본 승률의 잡음이 그대로 “내 기대 승률”이 됩니다.** [build_data.py:261](/Users/mac_al03241630/Project/marvelsnap/tools/build_data.py:261), [index.html:437](/Users/mac_al03241630/Project/marvelsnap/index.html:437)  
   #11은 원본 109판을 기준으로 대체 승률 63.0%가 나오며, **동일한 대체 12장도 #6에서는 56.6%, #15에서는 57.1%**입니다. 플레이어·랭크 차이도 통제하지 않아 회귀계수를 교체의 인과효과로 해석하기 어렵습니다. [계수 해석 주의사항](https://scikit-learn.org/stable/auto_examples/inspection/plot_linear_model_coefficient_interpretation.html#interpreting-coefficients-being-cautious-about-causality)  
   **수정:** 원본 승률을 계열 평균으로 축소하고 관측 신뢰구간을 표시하세요. 문구는 “트래커 기반 대체 추정”으로 바꾸고, 상한 적용 결과를 “원본과 비슷”이라고 단정하지 마세요.

3. **[중간] 릿지가 수렴 전에 종료되어 재생성 결과가 달라집니다.** [build_data.py:195](/Users/mac_al03241630/Project/marvelsnap/tools/build_data.py:195)  
   `set` 순회 순서와 고정 150회 때문에 동일 캐시에서도 #9 예측이 **59.1% 또는 59.2%**로 달라집니다. 2,000회에서는 확인한 두 시드가 같은 값으로 수렴했습니다. **수정:** 카드 순서를 정렬하고 계수·절편 변화량 기준으로 종료하세요. 대체 후보 동률에도 명시적인 정렬 기준이 필요합니다.

4. **[중간] 탐욕적 대체 선택이 가능한 조합을 놓칩니다.** [build_data.py:242](/Users/mac_al03241630/Project/marvelsnap/tools/build_data.py:242)  
   A의 후보가 X·Y이고 B의 후보가 X뿐이면, A→X를 먼저 선택하면서 `nosub`가 됩니다. A→Y, B→X는 가능한데도 실패하는 사례를 재현했습니다. **수정:** 카드별 후보를 먼저 모은 뒤, 중복 없는 배정을 작은 백트래킹으로 찾으세요.

5. **[중간] 데이터 부족을 “핵심 카드라 대체 불가”로 과장합니다.** [build_data.py:251](/Users/mac_al03241630/Project/marvelsnap/tools/build_data.py:251), [index.html:489](/Users/mac_al03241630/Project/marvelsnap/index.html:489)  
   부재 표본 부족은 엔진 카드라는 증거가 아닙니다. 특히 `nosub`는 실제 부재 표본이 있어도 `without: 0`을 넣어 잘못 표시합니다. **수정:** 실제 판수를 보존하고 `reason`별로 “부재 표본 부족”·“보유 대체 후보 부족”을 구분하세요. 필터도 “대체 불가”보다 “예측 불가”가 정확합니다.

6. **[중간] 겹치는 플렉스 선택지 하나가 전체 생성을 중단합니다.** [build_data.py:274](/Users/mac_al03241630/Project/marvelsnap/tools/build_data.py:274)  
   두 슬롯이 각각 `A 또는 B`이면 첫 중복 조합에서 종료되어 유효한 A+B 조합도 생성하지 못합니다. **수정:** 중복 카드를 가진 조합만 건너뛰고, 유효 조합이 전혀 없을 때 오류를 내세요.

7. **[낮음·조건부] `esc`를 거치지 않는 속성 삽입이 있습니다.** [index.html:506](/Users/mac_al03241630/Project/marvelsnap/index.html:506)  
   `esc` 자체는 현재 텍스트·큰따옴표 속성 문맥에서 적절합니다. 다만 `data-ids`에는 원시 ID를 넣어, API ID에 따옴표가 섞이면 속성 탈출이 가능합니다. **수정:** `esc(ids.join(","))`를 사용하고 수집 단계에서 ID 형식·숫자 필드를 검증하세요.

8. **[낮음] 복사 실패에도 성공 알림이 나옵니다.** [index.html:580](/Users/mac_al03241630/Project/marvelsnap/index.html:580)  
   `document.execCommand("copy")`가 `false`를 반환해도 `ok()`를 호출합니다. **수정:** 반환값을 검사하고 textarea 제거는 `finally`에서 처리하세요.

현재 캐시의 12장 완전 일치·100판 제외는 정상이며, Node 간이 DOM 검사에서 현재 필터·보기 토글·덱 코드 base64 왕복도 확인했습니다.


OpenAI Codex v0.167.2
--------
workdir: /Users/mac_al03241630/Project/marvelsnap
model: gpt-6.1-sol
provider: openai
approval: never
sandbox: danger-full-access
reasoning effort: xhigh
reasoning summaries: none
session id: 01a1d95d-2a51-7df3-be26-c6fe6c8c6fca
--------
user
You are reviewing changes in the repo at /Users/mac_al03241630/Project/marvelsnap (a personal Marvel Snap deck-notes static page; Korean UI). Files: tools/fetch_sv.py (fetches SnapVault public API: cards + ranked 7-day deck stats into cache/), tools/build_data.py (parses notes/*.md, matches each 12-card deck build exactly against ranked 7d data, excludes builds <100 games, and for builds containing cards the user does not own computes a predicted win rate in predict(): same-archetype = lists sharing >=8 cards; if games played WITHOUT the missing card in that archetype <100 => 'engine card, no prediction'; substitute = most-played owned card in archetype lists lacking the missing card (>=50 games); card effects from weighted ridge regression (coordinate descent) on lists sharing >=6 cards, weight=games*(overlap/12)^3, lambda=200; prediction = actual wr + sum(beta_in - beta_out), capped at actual), index.html (renders data.js: card image grid from Untapped CDN, deck code copy = base64 of comma-joined per-card codes, sort by 'my expected win rate', filters). Generated data.js is present; cache/ has the raw data. Please review for: (1) correctness bugs in build_data.py (esp. predict/ridge_effects, flex-slot expansion, exclusion logic) and index.html JS (sorting, filters, toggles, copy, XSS via esc), (2) statistical soundness / misleading presentation of the prediction and suggest concrete improvements that are cheap, (3) anything in the UI text that overclaims. Run the scripts if useful (python3 tools/build_data.py; node is available). Do NOT modify files. Reply in Korean, findings ranked by severity with file:line, each with a concrete fix. Be concise.
hook: SessionStart
hook: SessionStart Completed
hook: UserPromptSubmit
hook: UserPromptSubmit Completed
codex
코드와 원본 캐시를 확인하고, 필요하면 생성기를 임시 경로에서 실행해 예측·제외 로직과 화면 표시를 검증하겠습니다. 파일은 수정하지 않겠습니다.
hook: PreToolUse
hook: PreToolUse Completed
exec
/bin/zsh -lc "pwd; rg --files -g 'AGENTS.md' -g 'tools/*.py' -g 'index.html' -g 'data.js' -g 'notes/*.md' -g 'cache/*'" in /Users/mac_al03241630/Project/marvelsnap
 succeeded in 0ms:
/Users/mac_al03241630/Project/marvelsnap
data.js
notes/collection.md
notes/meta-2026-11-14.md
index.html
tools/build_data.py
tools/fetch_sv.py

hook: PostToolUse
hook: PostToolUse Completed
hook: PreToolUse
hook: PreToolUse
hook: PreToolUse
hook: PreToolUse
hook: PreToolUse
hook: PreToolUse
hook: PreToolUse Completed
hook: PreToolUse Completed
hook: PreToolUse Completed
hook: PreToolUse Completed
hook: PreToolUse Completed
hook: PreToolUse Completed
exec
/bin/zsh -lc 'nl -ba index.html' in /Users/mac_al03241630/Project/marvelsnap
exec
/bin/zsh -lc 'nl -ba tools/build_data.py' in /Users/mac_al03241630/Project/marvelsnap
 succeeded in 0ms:
     1	#!/usr/bin/env python3
     2	"""notes/meta-*.md + notes/collection.md + cache/(SnapVault) -> data.js (페이지용 데이터).
     3	
     4	사용:
     5	  python3 tools/fetch_sv.py          # SnapVault 랭크 7일 데이터 갱신 (cache/)
     6	  python3 tools/build_data.py [notes/meta-YYYY-MM-DD.md]
     7	인자 없으면 notes/ 안의 가장 최신 meta-*.md 사용.
     8	
     9	- 노트의 플렉스 슬롯(A 또는 B)은 실제 12장 빌드로 펼친다.
    10	- 빌드마다 SnapVault 랭크 7일 통계를 12장 완전 일치로 붙인다. MIN_GAMES 미만 빌드는 제외.
    11	- 미보유 카드가 있는 빌드는 '보유 카드만 쓴 실제 유사 리스트'의 전적을 합산해 예측한다.
    12	"""
    13	import itertools
    14	import json
    15	import re
    16	import sys
    17	from collections import Counter
    18	from pathlib import Path
    19	
    20	ROOT = Path(__file__).resolve().parent.parent
    21	NOTES = ROOT / "notes"
    22	CACHE = ROOT / "cache"
    23	
    24	MIN_GAMES = 100   # 랭크 7일 이 판수 미만 빌드는 목록에서 제외 (사용자 요청)
    25	MIN_PRED = 100    # 빠지는 카드 없이 플레이된 같은 계열 판수가 이보다 적으면 예측 불가 (엔진 카드)
    26	MIN_SUB = 50      # 대체 후보 카드가 같은 계열에서 쓰인 최소 판수
    27	SAME_ARCH = 8     # 원본 빌드와 12장 중 이만큼 겹치면 같은 계열로 봄
    28	RIDGE_LAMBDA = 200  # 카드 기여도 추정 축소 강도 (가상 판수)
    29	
    30	TIER_HEADERS = {
    31	    "### S 티어": "S",
    32	    "### A 티어": "A",
    33	    "### B 티어": "B",
    34	    "### C 티어": "C",
    35	    "### 티어 미부여": "UT",
    36	    "### 참고": "REF",
    37	}
    38	
    39	# 노트/컬렉션 표기 -> SnapVault 카드 이름 (정규화로 안 맞는 것만)
    40	ALIASES = {
    41	    "kang the conqueror": "kang",
    42	}
    43	
    44	
    45	def norm(s: str) -> str:
    46	    s = s.lower().replace("(", " ").replace(")", " ")
    47	    s = re.sub(r"[^a-z0-9 ]", "", s)
    48	    return re.sub(r"\s+", " ", s).strip()
    49	
    50	
    51	def strip_md(s: str) -> str:
    52	    return s.replace("**", "").strip()
    53	
    54	
    55	def parse_cards(body: str):
    56	    """'A, B, **X 또는 Y**, C' -> [["A"], ["B"], ["X","Y"], ["C"]]"""
    57	    out = []
    58	    for raw in body.split(","):
    59	        c = strip_md(raw)
    60	        if c:
    61	            out.append([p.strip() for p in c.split(" 또는 ")])
    62	    return out
    63	
    64	
    65	def is_card_line(s: str) -> bool:
    66	    return s.startswith("- ") and s.count(",") >= 8
    67	
    68	
    69	def parse_meta(path: Path):
    70	    text = path.read_text(encoding="utf-8")
    71	    sec5 = text.split("## 5.", 1)[1].split("\n## 6.", 1)[0]
    72	    decks, refs = [], []
    73	    tier = None
    74	    cur = None
    75	
    76	    for line in sec5.splitlines():
    77	        s = line.strip()
    78	        hit = next((t for h, t in TIER_HEADERS.items() if s.startswith(h)), None)
    79	        if hit:
    80	            tier, cur = hit, None
    81	            continue
    82	        if tier is None:
    83	            continue
    84	        m = re.match(r"\*\*(\d+)\. (.+?)\*\*(.*)$", s)
    85	        if m and tier != "REF":
    86	            no, name, rest = int(m.group(1)), m.group(2).strip(), m.group(3)
    87	            ota = re.findall(r"([⬆⬇])\(([^)]+)\)", rest)
    88	            fam = re.search(r"계열:\s*([^—]+?)(?:,|$)", rest)
    89	            ut_ev = re.search(r"—\s*(UT [^,]+.*)$", rest)
    90	            cur = {
    91	                "no": no, "tier": tier, "name": name,
    92	                "ota": [{"dir": "up" if d == "⬆" else "down", "card": c} for d, c in ota],
    93	                "family": fam.group(1).strip() if fam else None,
    94	                "evidence": [], "lists": [], "notes": [],
    95	            }
    96	            if ut_ev and tier == "UT":
    97	                cur["evidence"].append(re.sub(r",?\s*계열:.*$", "", ut_ev.group(1)).strip())
    98	            decks.append(cur)
    99	            continue
   100	        if tier == "REF" and s.startswith("- **"):
   101	            m = re.match(r"- \*\*(.+?)\*\*(.*?)— (.*?):\s(.+)$", s)
   102	            if m:
   103	                ota = re.findall(r"([⬆⬇])\(([^)]+)\)", m.group(2))
   104	                refs.append({
   105	                    "no": None, "tier": "REF", "name": m.group(1).strip(),
   106	                    "ota": [{"dir": "up" if d == "⬆" else "down", "card": c} for d, c in ota],
   107	                    "family": None, "evidence": [m.group(3).strip()], "notes": [],
   108	                    "lists": [{"label": None, "slots": parse_cards(m.group(4))}],
   109	                })
   110	            continue
   111	        if cur is None:
   112	            continue
   113	        if is_card_line(s):
   114	            body, label = s[2:], None
   115	            vm = re.match(r"\(변형([^)]*)\)\s*(.+)$", body)
   116	            if vm:
   117	                label = ("변형" + (vm.group(1) or "")).strip()
   118	                body = vm.group(2)
   119	            cur["lists"].append({"label": label, "slots": parse_cards(body)})
   120	        elif s.startswith("- 근거:"):
   121	            cur["evidence"].append(strip_md(s[len("- 근거:"):]))
   122	        elif s.startswith("- "):
   123	            cur["notes"].append(strip_md(s[2:]))
   124	
   125	    for d in decks + refs:
   126	        for lst in d["lists"]:
   127	            if len(lst["slots"]) != 12:
   128	                raise SystemExit(f"[오류] {d.get('no') or ''} {d['name']} 카드 수 {len(lst['slots'])}장")
   129	    return decks, refs
   130	
   131	
   132	def parse_collection(path: Path):
   133	    text = path.read_text(encoding="utf-8")
   134	    block = text.split("## 미보유 Series 5", 1)[1].split("\n---", 1)[0]
   135	    cards = []
   136	    for line in block.splitlines():
   137	        if not line.startswith("|") or "---" in line:
   138	            continue
   139	        cols = [c.strip() for c in line.strip("|").split("|")]
   140	        if cols[0] in ("시즌", "카드"):
   141	            continue
   142	        # 4열 표(시즌|카드|코스트/파워|기간) 또는 2열 표(카드|코스트/파워)
   143	        name = cols[1] if len(cols) >= 4 else cols[0]
   144	        stat = cols[2] if len(cols) >= 4 else cols[1]
   145	        cards.append({"name": name, "stat": stat})
   146	    upd = re.search(r"마지막 갱신:\s*([0-9-]+)", text)
   147	    return cards, (upd.group(1) if upd else None)
   148	
   149	
   150	def load_cache():
   151	    try:
   152	        cards = json.loads((CACHE / "sv_cards.json").read_text(encoding="utf-8"))
   153	        ranked = json.loads((CACHE / "sv_ranked7.json").read_text(encoding="utf-8"))
   154	    except FileNotFoundError:
   155	        raise SystemExit("[오류] cache/ 가 없습니다. 먼저 python3 tools/fetch_sv.py 를 실행하세요.")
   156	    return cards, ranked
   157	
   158	
   159	class Resolver:
   160	    def __init__(self, sv_cards):
   161	        self.by_norm = {norm(c["name"]): c for c in sv_cards if not c.get("isToken")}
   162	        self.by_id = {c["id"]: c for c in sv_cards}
   163	
   164	    def id_of(self, name: str) -> str:
   165	        key = norm(name)
   166	        key = ALIASES.get(key, key)
   167	        c = self.by_norm.get(key)
   168	        if not c:
   169	            raise SystemExit(f"[오류] SnapVault 카드 목록에서 '{name}' 을(를) 찾지 못함 → ALIASES 에 추가")
   170	        return c["id"]
   171	
   172	
   173	def stat_of(st):
   174	    g = st["totalGames"]
   175	    return {
   176	        "games": g,
   177	        "wins": st["wins"],
   178	        "wr": round(100 * st["wins"] / g, 1) if g else None,
   179	        "cubes": round(st["totalCubes"] / st["cubeGames"], 2) if st.get("cubeGames") else None,
   180	    }
   181	
   182	
   183	def ridge_effects(rows, lam=RIDGE_LAMBDA, sweeps=150):
   184	    """가중 릿지 회귀 (좌표 하강). rows = [(카드 set, 승률 0~1, 가중치)].
   185	    승률 ≈ b0 + Σ β_card. 반환: {card: β} (승률 단위, 0.01 = 1%p)."""
   186	    beta = Counter()
   187	    sw = sum(w for _, _, w in rows)
   188	    b0 = sum(y * w for _, y, w in rows) / sw
   189	    resid = [y - b0 for _, y, _ in rows]
   190	    by_card = {}
   191	    for i, (s, _, w) in enumerate(rows):
   192	        for c in s:
   193	            by_card.setdefault(c, []).append(i)
   194	    denom = {c: sum(rows[i][2] for i in idx) + lam for c, idx in by_card.items()}
   195	    for _ in range(sweeps):
   196	        for c, idx in by_card.items():
   197	            old = beta[c]
   198	            num = sum(rows[i][2] * (resid[i] + old) for i in idx)
   199	            new = num / denom[c]
   200	            if new != old:
   201	                d = new - old
   202	                for i in idx:
   203	                    resid[i] -= d
   204	                beta[c] = new
   205	        shift = sum(rows[i][2] * resid[i] for i in range(len(rows))) / sw
   206	        if shift:
   207	            b0 += shift
   208	            resid = [r - shift for r in resid]
   209	    return beta
   210	
   211	
   212	def predict(ids, wr_now, unowned, db):
   213	    """미보유 카드를 보유 카드로 바꿨을 때의 랭크 승률 추정.
   214	    1) 같은 계열 = 이 빌드와 SAME_ARCH장 이상 겹치는 랭크 7일 리스트
   215	    2) 빠지는 카드마다 같은 계열에서 그 카드 없이 플레이된 판이 MIN_PRED 미만이면 '엔진 카드' → 예측 불가
   216	    3) 대체 카드 = 같은 계열에서 그 카드가 빠진 리스트에 실제로 가장 많이 들어간 보유 카드 (MIN_SUB판 이상)
   217	       (기여도 최댓값으로 고르면 잡음이 큰 카드가 뽑혀 과대추정됨 → 사용량 기준)
   218	    4) 카드별 기여도 = 이 빌드와 6장 이상 겹치는 리스트로 가중 릿지 회귀
   219	    5) 예측 = 실제 원본 승률 + Σ(들어가는 카드 기여 − 빠지는 카드 기여), 단 원본보다 높게는 잡지 않음(보수적)"""
   220	    S = set(ids)
   221	    miss = sorted(S & unowned)
   222	    core = S - set(miss)
   223	    arch = [x for x in db if len(x["set"] & S) >= SAME_ARCH]
   224	    arch_games = sum(x["stats"]["totalGames"] for x in arch)
   225	
   226	    blockers, without_lists = [], {}
   227	    for m in miss:
   228	        wl = [x for x in arch if m not in x["set"]]
   229	        without_lists[m] = wl
   230	        g = sum(x["stats"]["totalGames"] for x in wl)
   231	        if g < MIN_PRED:
   232	            blockers.append({"id": m, "without": g})
   233	    if blockers:
   234	        return {"ok": False, "reason": "engine", "blockers": blockers,
   235	                "archLists": len(arch), "archGames": arch_games}
   236	
   237	    rows = [(x["set"], x["stats"]["wins"] / x["stats"]["totalGames"],
   238	             x["stats"]["totalGames"] * (len(x["set"] & S) / 12) ** 3)
   239	            for x in db if len(x["set"] & S) >= 6]
   240	    beta = ridge_effects(rows)
   241	
   242	    taken, swaps = set(), []
   243	    for m in miss:
   244	        use = Counter()
   245	        for x in without_lists[m]:
   246	            for c in x["set"] - S:
   247	                if c not in unowned and c not in taken:
   248	                    use[c] += x["stats"]["totalGames"]
   249	        cand = [(c, g) for c, g in use.most_common() if g >= MIN_SUB]
   250	        if not cand:
   251	            return {"ok": False, "reason": "nosub", "blockers": [{"id": m, "without": 0}],
   252	                    "archLists": len(arch), "archGames": arch_games}
   253	        sub, used_games = cand[0]
   254	        taken.add(sub)
   255	        swaps.append({"out": m, "in": sub, "used": used_games, "d": round(100 * (beta[sub] - beta[m]), 1)})
   256	    raw = 100 * sum(beta[s["in"]] - beta[s["out"]] for s in swaps)
   257	    delta = min(0.0, raw)
   258	    replaced = sorted(core | {s["in"] for s in swaps})
   259	    exact = next((x for x in db if x["set"] == frozenset(replaced)), None)
   260	    return {
   261	        "ok": True, "wr": round(wr_now + delta, 1), "delta": round(delta, 1), "rawDelta": round(raw, 1),
   262	        "swaps": swaps, "ids": replaced, "archLists": len(arch), "archGames": arch_games,
   263	        "exact": stat_of(exact["stats"]) if exact else None,
   264	    }
   265	
   266	
   267	def build_deck(d, res, unowned, db_by_sig, db):
   268	    builds = []
   269	    for lst in d["lists"]:
   270	        names_opts = lst["slots"]
   271	        flex_idx = [i for i, o in enumerate(names_opts) if len(o) > 1]
   272	        for combo in itertools.product(*names_opts):
   273	            ids = [res.id_of(n) for n in combo]
   274	            if len(set(ids)) != 12:
   275	                raise SystemExit(f"[오류] {d['name']} 중복 카드")
   276	            label_parts = [lst["label"]] if lst["label"] else []
   277	            if flex_idx:
   278	                label_parts.append(" · ".join(combo[i] for i in flex_idx) + " 빌드")
   279	            hit = db_by_sig.get(frozenset(ids))
   280	            b = {
   281	                "label": " / ".join(label_parts) or None,
   282	                "ids": ids,
   283	                "stats": stat_of(hit["stats"]) if hit else None,
   284	                "miss": sorted(set(ids) & unowned),
   285	            }
   286	            b["included"] = bool(b["stats"] and b["stats"]["games"] >= MIN_GAMES)
   287	            if b["included"] and b["miss"]:
   288	                b["pred"] = predict(ids, b["stats"]["wr"], unowned, db)
   289	            builds.append(b)
   290	    return builds
   291	
   292	
   293	def main():
   294	    meta = Path(sys.argv[1]) if len(sys.argv) > 1 else sorted(NOTES.glob("meta-*.md"))[-1]
   295	    as_of = re.search(r"meta-(\d{4}-\d{2}-\d{2})", meta.name).group(1)
   296	    decks, refs = parse_meta(meta)
   297	    unowned_list, coll_date = parse_collection(NOTES / "collection.md")
   298	    sv_cards, ranked = load_cache()
   299	    res = Resolver(sv_cards)
   300	
   301	    for u in unowned_list:
   302	        u["id"] = res.id_of(u["name"])
   303	    unowned = {u["id"] for u in unowned_list}
   304	
   305	    db = []
   306	    for x in ranked["decks"]:
   307	        db.append({"set": frozenset(x["cardIds"]), "stats": x["stats"]})
   308	    db_by_sig = {x["set"]: x for x in db}
   309	
   310	    out_decks, excluded = [], []
   311	    for d in decks + refs:
   312	        builds = build_deck(d, res, unowned, db_by_sig, db)
   313	        inc = [b for b in builds if b["included"]]
   314	        lists = d.pop("lists")
   315	        if not inc:
   316	            excluded.append({
   317	                "no": d["no"], "tier": d["tier"], "name": d["name"],
   318	                "games": max((b["stats"]["games"] if b["stats"] else 0) for b in builds),
   319	            })
   320	            continue
   321	        d["builds"] = inc
   322	        d["droppedBuilds"] = [{"label": b["label"], "games": b["stats"]["games"] if b["stats"] else 0}
   323	                              for b in builds if not b["included"]]
   324	        out_decks.append(d)
   325	
   326	    used = set()
   327	    for d in out_decks:
   328	        for b in d["builds"]:
   329	            used |= set(b["ids"])
   330	            if b.get("pred") and b["pred"]["ok"]:
   331	                used |= set(b["pred"]["ids"])
   332	    used |= unowned
   333	    cards = {
   334	        cid: {"name": res.by_id[cid]["name"], "cost": res.by_id[cid]["cost"],
   335	              "power": res.by_id[cid]["power"], "code": res.by_id[cid]["deckCode"]}
   336	        for cid in sorted(used)
   337	    }
   338	    for d in out_decks:  # 코스트 → 이름 순 정렬 (화면·덱 코드 공통)
   339	        key = lambda c: (cards[c]["cost"], cards[c]["name"])
   340	        for b in d["builds"]:
   341	            b["ids"].sort(key=key)
   342	            if b.get("pred") and b["pred"]["ok"]:
   343	                b["pred"]["ids"].sort(key=key)
   344	
   345	    data = {
   346	        "asOf": as_of,
   347	        "collectionUpdated": coll_date,
   348	        "rankedSource": {"site": "SnapVault", "window": "7일", "mode": "랭크", "fetchedAt": ranked["fetchedAt"],
   349	                         "minGames": MIN_GAMES, "minPred": MIN_PRED, "lists": len(db)},
   350	        "cards": cards,
   351	        "decks": out_decks,
   352	        "excluded": excluded,
   353	        "unowned": [{"id": u["id"], "name": u["name"], "stat": u["stat"]} for u in unowned_list],
   354	    }
   355	    out = ROOT / "data.js"
   356	    out.write_text(
   357	        "// tools/build_data.py 로 생성 — 직접 수정하지 말 것\n"
   358	        "window.SNAP_DATA = " + json.dumps(data, ensure_ascii=False, separators=(",", ":")) + ";\n",
   359	        encoding="utf-8",
   360	    )
   361	    n_main = sum(1 for d in out_decks if d["tier"] != "REF")
   362	    n_pred = sum(1 for d in out_decks for b in d["builds"] if b.get("pred", {}).get("ok"))
   363	    n_nopred = sum(1 for d in out_decks for b in d["builds"] if b["miss"] and not b.get("pred", {}).get("ok"))
   364	    print(f"{meta.name}: 표시 덱 {n_main}개 (+참고 {len(out_decks) - n_main}), 제외 {len(excluded)}개, "
   365	          f"예측 {n_pred}빌드 / 예측 불가 {n_nopred}빌드, 카드 {len(cards)}장 -> {out}")
   366	    for e in excluded:
   367	        print(f"  제외: #{e['no']} {e['name']} ({e['games']}판)")
   368	
   369	
   370	if __name__ == "__main__":
   371	    main()

 succeeded in 0ms:
     1	<!doctype html>
     2	<html lang="ko">
     3	<head>
     4	<meta charset="utf-8">
     5	<meta name="viewport" content="width=device-width, initial-scale=1">
     6	<title>Marvel Snap 덱 노트</title>
     7	<meta name="description" content="마블 스냅 메타 덱 30선과 내 컬렉션 기준 사용 가능 여부 — 개인 덱 빌딩 노트">
     8	<link rel="stylesheet" href="https://cdn.jsdelivr.net/gh/orioncactus/pretendard@v1.3.9/dist/web/variable/pretendardvariable-dynamic-subset.min.css">
     9	<style>
    10	:root {
    11	  --bg: #f6f6f9; --surface: #ffffff; --surface-2: #f0f0f5; --line: #e2e2ea;
    12	  --text: #17171c; --text-2: #55556a; --text-3: #8a8a9e;
    13	  --accent: #5b4bdb; --accent-soft: #ecebfd;
    14	  --up: #12805c; --up-soft: #e3f5ee; --down: #c4314b; --down-soft: #fde8ec;
    15	  --warn: #a35f00; --warn-soft: #fff1db;
    16	  --tier-s: #b8860b; --tier-s-bg: #fff5d6; --tier-a: #7c3aed; --tier-a-bg: #f1e9ff;
    17	  --tier-b: #1d6fd6; --tier-b-bg: #e5f0ff; --tier-c: #5f6472; --tier-c-bg: #eceef2;
    18	  --tier-ut: #8a8a9e; --tier-ut-bg: transparent;
    19	  --shadow: 0 1px 2px rgba(20,20,40,.06), 0 4px 16px rgba(20,20,40,.05);
    20	}
    21	@media (prefers-color-scheme: dark) {
    22	  :root:not([data-theme="light"]) {
    23	    --bg: #0f0f14; --surface: #191920; --surface-2: #22222b; --line: #2e2e39;
    24	    --text: #ececf3; --text-2: #a9a9bd; --text-3: #75758a;
    25	    --accent: #9d90ff; --accent-soft: #26233f;
    26	    --up: #4cd6a0; --up-soft: #13302a; --down: #ff7b91; --down-soft: #3a1820;
    27	    --warn: #ffb648; --warn-soft: #36270f;
    28	    --tier-s: #ffcf4a; --tier-s-bg: #3a2f0c; --tier-a: #c4a5ff; --tier-a-bg: #2c2045;
    29	    --tier-b: #7cb6ff; --tier-b-bg: #172a45; --tier-c: #b3b8c4; --tier-c-bg: #2a2d34;
    30	    --tier-ut: #8f8fa6; --shadow: none;
    31	  }
    32	}
    33	:root[data-theme="dark"] {
    34	  --bg: #0f0f14; --surface: #191920; --surface-2: #22222b; --line: #2e2e39;
    35	  --text: #ececf3; --text-2: #a9a9bd; --text-3: #75758a;
    36	  --accent: #9d90ff; --accent-soft: #26233f;
    37	  --up: #4cd6a0; --up-soft: #13302a; --down: #ff7b91; --down-soft: #3a1820;
    38	  --warn: #ffb648; --warn-soft: #36270f;
    39	  --tier-s: #ffcf4a; --tier-s-bg: #3a2f0c; --tier-a: #c4a5ff; --tier-a-bg: #2c2045;
    40	  --tier-b: #7cb6ff; --tier-b-bg: #172a45; --tier-c: #b3b8c4; --tier-c-bg: #2a2d34;
    41	  --tier-ut: #8f8fa6; --shadow: none;
    42	}
    43	* { box-sizing: border-box; }
    44	html { -webkit-text-size-adjust: 100%; scroll-padding-top: 64px; }
    45	body {
    46	  margin: 0; background: var(--bg); color: var(--text);
    47	  font-family: "Pretendard Variable", Pretendard, -apple-system, BlinkMacSystemFont, system-ui, sans-serif;
    48	  font-size: 15px; line-height: 1.6; word-break: keep-all; overflow-wrap: anywhere;
    49	}
    50	a { color: var(--accent); }
    51	.wrap { max-width: 1080px; margin: 0 auto; padding: 0 16px; }
    52	
    53	/* nav */
    54	nav.top {
    55	  position: sticky; top: 0; z-index: 10; background: color-mix(in srgb, var(--bg) 88%, transparent);
    56	  backdrop-filter: blur(10px); -webkit-backdrop-filter: blur(10px); border-bottom: 1px solid var(--line);
    57	}
    58	nav.top .wrap { display: flex; align-items: center; gap: 4px; height: 52px; overflow-x: auto; scrollbar-width: none; }
    59	nav.top .wrap::-webkit-scrollbar { display: none; }
    60	nav.top a { flex: none; color: var(--text-2); text-decoration: none; font-size: 14px; padding: 6px 10px; border-radius: 8px; }
    61	nav.top a:hover { background: var(--surface-2); color: var(--text); }
    62	nav.top .brand { font-weight: 700; color: var(--text); margin-right: 6px; }
    63	#themeBtn { margin-left: auto; flex: none; border: 1px solid var(--line); background: var(--surface); color: var(--text-2); border-radius: 8px; padding: 5px 10px; font: inherit; font-size: 13px; cursor: pointer; }
    64	
    65	/* hero */
    66	header.hero { padding: 36px 0 12px; }
    67	header.hero h1 { margin: 0 0 6px; font-size: 28px; letter-spacing: -0.02em; }
    68	header.hero p.sub { margin: 0; color: var(--text-2); }
    69	.stats { display: grid; grid-template-columns: repeat(4, 1fr); gap: 10px; margin: 20px 0 8px; }
    70	.stat { background: var(--surface); border: 1px solid var(--line); border-radius: 12px; padding: 12px 14px; box-shadow: var(--shadow); }
    71	.stat b { display: block; font-size: 24px; letter-spacing: -0.02em; font-variant-numeric: tabular-nums; }
    72	.stat span { color: var(--text-2); font-size: 13px; }
    73	
    74	section { padding: 28px 0 8px; }
    75	section > h2 { font-size: 21px; margin: 0 0 4px; letter-spacing: -0.01em; }
    76	section > p.lead { margin: 0 0 16px; color: var(--text-2); font-size: 14px; }
    77	.panel { background: var(--surface); border: 1px solid var(--line); border-radius: 14px; padding: 16px 18px; box-shadow: var(--shadow); }
    78	.trend { margin: 0; padding-left: 20px; }
    79	.trend li { margin: 6px 0; }
    80	.trend li::marker { color: var(--text-3); }
    81	
    82	/* filters */
    83	.filters { display: flex; flex-direction: column; gap: 10px; margin-bottom: 16px; }
    84	.frow { display: flex; align-items: center; gap: 6px; flex-wrap: wrap; }
    85	.frow .lbl { font-size: 13px; color: var(--text-3); width: 44px; flex: none; }
    86	.chip-btn { border: 1px solid var(--line); background: var(--surface); color: var(--text-2); border-radius: 999px; padding: 5px 12px; font: inherit; font-size: 13px; cursor: pointer; min-height: 32px; }
    87	.chip-btn[aria-pressed="true"] { background: var(--accent); border-color: var(--accent); color: #fff; }
    88	:root[data-theme="dark"] .chip-btn[aria-pressed="true"] { color: #121218; }
    89	@media (prefers-color-scheme: dark) { :root:not([data-theme="light"]) .chip-btn[aria-pressed="true"] { color: #121218; } }
    90	.count-line { font-size: 13px; color: var(--text-3); margin: 0 0 10px; }
    91	
    92	/* deck cards */
    93	.decks { display: grid; grid-template-columns: 1fr; gap: 14px; }
    94	@media (min-width: 980px) { .decks { grid-template-columns: 1fr 1fr; } }
    95	.deck { background: var(--surface); border: 1px solid var(--line); border-radius: 14px; padding: 14px 16px 12px; box-shadow: var(--shadow); display: flex; flex-direction: column; gap: 10px; min-width: 0; }
    96	.deck-head { display: flex; gap: 10px; align-items: flex-start; }
    97	.rank { flex: none; font-size: 12px; font-weight: 700; color: var(--text-3); width: 22px; padding-top: 8px; text-align: right; font-variant-numeric: tabular-nums; }
    98	.tier { flex: none; width: 34px; height: 34px; border-radius: 9px; display: grid; place-items: center; font-weight: 800; font-size: 15px; }
    99	.tier.S { color: var(--tier-s); background: var(--tier-s-bg); }
   100	.tier.A { color: var(--tier-a); background: var(--tier-a-bg); }
   101	.tier.B { color: var(--tier-b); background: var(--tier-b-bg); }
   102	.tier.C { color: var(--tier-c); background: var(--tier-c-bg); }
   103	.tier.UT { color: var(--tier-ut); border: 1.5px dashed var(--tier-ut); font-size: 11px; }
   104	.tier.REF { color: var(--text-3); background: var(--surface-2); font-size: 11px; }
   105	.deck-title { flex: 1; min-width: 0; }
   106	.deck-title h3 { margin: 0; font-size: 16px; line-height: 1.35; letter-spacing: -0.01em; }
   107	.deck-title .no { color: var(--text-3); font-weight: 600; margin-right: 4px; font-variant-numeric: tabular-nums; }
   108	.tags { display: flex; flex-wrap: wrap; gap: 5px; margin-top: 5px; }
   109	.tag { font-size: 12px; padding: 1px 8px; border-radius: 6px; background: var(--surface-2); color: var(--text-2); white-space: nowrap; }
   110	.tag.up { background: var(--up-soft); color: var(--up); }
   111	.tag.down { background: var(--down-soft); color: var(--down); }
   112	.own { font-size: 12.5px; font-weight: 600; padding: 3px 9px; border-radius: 7px; white-space: nowrap; flex: none; }
   113	.own.ok { background: var(--up-soft); color: var(--up); }
   114	.own.pred { background: var(--warn-soft); color: var(--warn); }
   115	.own.none { background: var(--down-soft); color: var(--down); }
   116	.build { border-top: 1px solid var(--line); padding-top: 10px; display: flex; flex-direction: column; gap: 8px; }
   117	.build:first-of-type { border-top: none; padding-top: 0; }
   118	.build-label { font-size: 12.5px; font-weight: 600; color: var(--text-2); margin: 0; }
   119	.wr-line { display: flex; align-items: baseline; gap: 8px; flex-wrap: wrap; }
   120	.wr-big { font-size: 22px; font-weight: 800; letter-spacing: -0.02em; font-variant-numeric: tabular-nums; }
   121	.wr-big.dim { font-size: 15px; font-weight: 700; color: var(--text-3); }
   122	.wr-meta { font-size: 12.5px; color: var(--text-2); font-variant-numeric: tabular-nums; }
   123	.grid12 { display: grid; grid-template-columns: repeat(6, minmax(0, 1fr)); gap: 4px 2px; }
   124	@media (max-width: 520px) { .grid12 { grid-template-columns: repeat(4, minmax(0, 1fr)); } }
   125	.grid12[hidden] { display: none; }
   126	.cimg { margin: 0; position: relative; min-width: 0; text-align: center; }
   127	.cimg img { width: 100%; height: auto; aspect-ratio: 1 / 1; display: block; object-fit: contain; }
   128	.cimg figcaption { font-size: 10.5px; line-height: 1.25; color: var(--text-2); margin-top: -2px; display: -webkit-box; -webkit-line-clamp: 2; -webkit-box-orient: vertical; overflow: hidden; word-break: break-word; }
   129	.cimg .ph { display: none; }
   130	.cimg.noimg img { display: none; }
   131	.cimg.noimg .ph { display: grid; place-items: center; aspect-ratio: 1 / 1; border-radius: 10px; background: var(--surface-2); font-weight: 800; color: var(--text-3); font-size: 18px; }
   132	.cimg.miss img { filter: grayscale(1); opacity: .38; }
   133	.cimg.miss figcaption { color: var(--down); font-weight: 600; }
   134	.cimg.miss::after { content: "✕"; position: absolute; top: 4%; right: 6%; width: 20px; height: 20px; border-radius: 50%; background: var(--down); color: #fff; font-size: 11px; font-weight: 800; display: grid; place-items: center; }
   135	.cimg.added figcaption { color: var(--up); font-weight: 700; }
   136	.cimg.added::after { content: "+"; position: absolute; top: 4%; right: 6%; width: 20px; height: 20px; border-radius: 50%; background: var(--up); color: #fff; font-size: 13px; font-weight: 800; display: grid; place-items: center; }
   137	.pred { border-radius: 10px; padding: 9px 11px; font-size: 13px; }
   138	.pred.ok { background: var(--warn-soft); }
   139	.pred.no { background: var(--surface-2); color: var(--text-2); }
   140	.pred .wr-big { color: var(--warn); font-size: 20px; }
   141	.pred-lbl { font-size: 12.5px; font-weight: 700; color: var(--warn); }
   142	.swaps { display: flex; flex-wrap: wrap; gap: 4px 10px; margin-top: 4px; }
   143	.swap { font-size: 12.5px; white-space: nowrap; }
   144	.swap s { color: var(--down); }
   145	.swap b { color: var(--up); }
   146	.btns { display: flex; flex-wrap: wrap; gap: 6px; align-items: center; }
   147	.btn { border: 1px solid var(--line); background: var(--surface); color: var(--text); font: inherit; font-size: 13px; font-weight: 600; cursor: pointer; padding: 6px 12px; border-radius: 8px; min-height: 34px; }
   148	.btn:hover { background: var(--surface-2); }
   149	.btn.primary { background: var(--accent); border-color: var(--accent); color: #fff; }
   150	.btn.primary:hover { filter: brightness(1.08); }
   151	:root[data-theme="dark"] .btn.primary { color: #121218; }
   152	@media (prefers-color-scheme: dark) { :root:not([data-theme="light"]) .btn.primary { color: #121218; } }
   153	.btn.ghost { border-color: transparent; background: none; color: var(--text-3); font-weight: 500; }
   154	.btn.ghost:hover { color: var(--text); background: var(--surface-2); }
   155	.dropped { font-size: 12px; color: var(--text-3); margin: 0; }
   156	details.ev { background: none; border: none; padding: 0; margin: 0; }
   157	details.ev > summary { padding: 2px 0; font-size: 12.5px; font-weight: 500; color: var(--text-3); }
   158	details.ev > div { padding: 2px 0 0; font-size: 12.5px; color: var(--text-2); }
   159	details.ev ul { margin: 2px 0; }
   160	.excluded { margin-top: 14px; font-size: 13px; color: var(--text-3); }
   161	.excluded b { color: var(--text-2); font-weight: 600; }
   162	.card { font-size: 13px; padding: 3px 9px; border-radius: 7px; background: var(--surface-2); border: 1px solid transparent; }
   163	.cards { display: flex; flex-wrap: wrap; gap: 5px; }
   164	.empty { color: var(--text-3); padding: 24px; text-align: center; border: 1px dashed var(--line); border-radius: 14px; }
   165	
   166	/* tables */
   167	.tbl-wrap { overflow-x: auto; border: 1px solid var(--line); border-radius: 12px; background: var(--surface); }
   168	table { border-collapse: collapse; width: 100%; font-size: 14px; }
   169	th, td { text-align: left; padding: 9px 12px; border-bottom: 1px solid var(--line); vertical-align: top; }
   170	th { font-size: 12.5px; color: var(--text-3); font-weight: 600; background: var(--surface-2); white-space: nowrap; }
   171	tr:last-child td { border-bottom: none; }
   172	td.num { font-variant-numeric: tabular-nums; white-space: nowrap; }
   173	.nerf { color: var(--down); font-weight: 600; }
   174	.buff { color: var(--up); font-weight: 600; }
   175	.grid2 { display: grid; grid-template-columns: 1fr; gap: 14px; }
   176	@media (min-width: 900px) { .grid2 { grid-template-columns: 1fr 1fr; } }
   177	h3.sub { font-size: 15px; margin: 18px 0 8px; }
   178	details { background: var(--surface); border: 1px solid var(--line); border-radius: 12px; padding: 0 16px; margin-bottom: 10px; }
   179	details > summary { cursor: pointer; padding: 13px 0; font-weight: 600; list-style: none; }
   180	details > summary::-webkit-details-marker { display: none; }
   181	details > summary::before { content: "▸ "; color: var(--text-3); }
   182	details[open] > summary::before { content: "▾ "; }
   183	details > div { padding: 0 0 14px; font-size: 14px; }
   184	details ul { padding-left: 18px; margin: 6px 0; }
   185	.muted { color: var(--text-3); font-size: 13px; }
   186	footer { padding: 32px 0 48px; color: var(--text-3); font-size: 13px; }
   187	.toast { position: fixed; left: 50%; bottom: 24px; transform: translateX(-50%) translateY(20px); background: var(--text); color: var(--bg); padding: 8px 14px; border-radius: 10px; font-size: 13px; opacity: 0; transition: .2s; pointer-events: none; }
   188	.toast.show { opacity: 1; transform: translateX(-50%) translateY(0); }
   189	@media (max-width: 640px) {
   190	  header.hero h1 { font-size: 24px; }
   191	  .stats { grid-template-columns: repeat(2, 1fr); }
   192	  .frow .lbl { width: 100%; }
   193	}
   194	</style>
   195	</head>
   196	<body>
   197	<nav class="top" aria-label="섹션">
   198	  <div class="wrap">
   199	    <a class="brand" href="#top">덱 노트</a>
   200	    <a href="#decks">덱 목록</a>
   201	    <a href="#collection">내 컬렉션</a>
   202	    <a href="#season">시즌·패치</a>
   203	    <a href="#basics">기본 규칙</a>
   204	    <a href="#sources">출처·주의</a>
   205	    <button id="themeBtn" type="button" aria-label="테마 전환">테마</button>
   206	  </div>
   207	</nav>
   208	
   209	<main class="wrap" id="top">
   210	  <header class="hero">
   211	    <h1>Marvel Snap 덱 노트</h1>
   212	    <p class="sub" id="heroSub">메타 기준일 — · Knights of Avalon 시즌 · 11/12 OTA 직후</p>
   213	    <div class="stats" id="stats"></div>
   214	  </header>
   215	
   216	  <section id="trend" aria-labelledby="trend-h">
   217	    <h2 id="trend-h">이번 주 메타 흐름</h2>
   218	    <div class="panel">
   219	      <ul class="trend">
   220	        <li><b>Anti-Polar Magneto × Arthur Pendragon (4코스트 치트)</b> 계열이 시즌 최대 화두. Untapped 인기 1위 아키타입, SnapVault S티어에도 2개. Lancelot · Mordred · Captain Britain 등 시즌 신규 카드가 그대로 들어감.</li>
   221	        <li><b>Zombie Galacti / Shuri / Wong</b> — 랭크 7일 2,239판 60.0%로 표본이 가장 큰 고성능 덱 (전체 모드 2,476판 · +0.71 큐브). 다만 MSZ 11/8 티어표·Coccia Top 10에는 없음.</li>
   222	        <li><b>Stardust / Gambit Horseman of Death</b> 생성·테크 덱 — Sasquatch형이 SnapVault S. 피니셔만 바꾼 변형이 다수. Mobius 너프 영향권.</li>
   223	        <li><b>Zombie Horde</b> — 사용량이 많고 성적이 양호 (SnapComplete 5,526판 59.1%). Zombie Scarlet Witch 너프(-1 파워).</li>
   224	        <li><b>전통 강자</b> — High Evo · Fantomex는 두 출처 대표본으로 확인, Patriot은 Onslaught 버프 수혜. Destroy · Surfer · Thor · Galactus 등은 Untapped 단독 근거.</li>
   225	        <li>많이 쓰이지만 승률은 평범 — <b>Sandstorm Patriot</b> (최다 사용 7,093판, 승률 51%).</li>
   226	      </ul>
   227	    </div>
   228	  </section>
   229	
   230	  <section id="decks" aria-labelledby="decks-h">
   231	    <h2 id="decks-h">메타 덱 — 내 기준 승률순</h2>
   232	    <p class="lead" id="decksLead"></p>
   233	    <div class="filters" role="group" aria-label="덱 필터">
   234	      <div class="frow" id="fSort"><span class="lbl">정렬</span></div>
   235	      <div class="frow" id="fOwn"><span class="lbl">보유</span></div>
   236	      <div class="frow" id="fTier"><span class="lbl">티어</span></div>
   237	      <div class="frow" id="fFam"><span class="lbl">계열</span></div>
   238	    </div>
   239	    <p class="count-line" id="countLine"></p>
   240	    <div class="decks" id="deckList"></div>
   241	    <p class="excluded" id="excludedLine"></p>
   242	  </section>
   243	
   244	  <section id="collection" aria-labelledby="coll-h">
   245	    <h2 id="coll-h">내 컬렉션 — 미보유 카드</h2>
   246	    <p class="lead" id="collLead"></p>
   247	    <h3 class="sub">획득 우선순위 (위 덱 목록 등장 수 기준)</h3>
   248	    <div class="tbl-wrap"><table id="prioTable"></table></div>
   249	    <p class="muted" style="margin-top:8px">“얻으면 바로 열리는 덱” = 그 카드 한 장만 없어서 원본 그대로 못 쓰던 덱. 괄호 안은 원본 랭크 7일 승률.</p>
   250	    <h3 class="sub">미보유 Series 5 전체</h3>
   251	    <div class="cards" id="unownedAll"></div>
   252	    <p class="muted" style="margin-top:8px">Series 4 이하 미보유 여부는 아직 반영 전입니다.</p>
   253	  </section>
   254	
   255	  <section id="season" aria-labelledby="season-h">
   256	    <h2 id="season-h">시즌 · 패치</h2>
   257	    <p class="lead">Knights of Avalon (11/3 ~ 11/30) · 다음 OTA 12/3, 패치 12/15</p>
   258	    <div class="grid2">
   259	      <div>
   260	        <h3 class="sub" style="margin-top:0">시즌 신규 카드</h3>
   261	        <div class="tbl-wrap"><table>
   262	          <thead><tr><th>카드</th><th>코/파</th><th>능력</th><th>출시</th></tr></thead>
   263	          <tbody>
   264	            <tr><td>Arthur Pendragon<br><span class="muted">시즌패스</span></td><td class="num">4/4</td><td>On Reveal: Excalibur(1/1, Ongoing: 4코스트 이상 아군 +2)를 무료로 여기에 꺼냄</td><td class="num">11/3</td></tr>
   265	            <tr><td>Merlin of Avalon<br><span class="muted">슈퍼 프리미엄</span></td><td class="num">1/2</td><td>On Reveal: The Grand Design(6/0, 생성 카드 1장 낼 때마다 1코 감소, 다른 각 로케이션 아군 1장 +5)을 손에 추가</td><td class="num">11/3</td></tr>
   266	            <tr><td>Captain Britain</td><td class="num">2/3</td><td>4코스트 이상 카드를 낸 뒤: 그 카드 +1 파워, 손의 카드 1장 -1 코스트</td><td class="num">11/3</td></tr>
   267	            <tr><td>Mordred</td><td class="num">3/4</td><td>Ongoing: 여기 있는 더 높은 코스트 카드 1장당 +2 파워</td><td class="num">11/5</td></tr>
   268	            <tr><td>Lancelot</td><td class="num">4/6</td><td>Ongoing: 파워가 증가된 아군 +1 파워</td><td class="num">11/10</td></tr>
   269	            <tr><td>Elder Dragon of the Moon</td><td class="num">?</td><td class="muted">미출시</td><td class="num">11/17</td></tr>
   270	            <tr><td>Knight's Vow<br><span class="muted">이벤트 패스</span></td><td class="num">?</td><td class="muted">미출시</td><td class="num">11/19</td></tr>
   271	            <tr><td>Sir Percy Black Knight</td><td class="num">?</td><td class="muted">미출시</td><td class="num">11/24</td></tr>
   272	          </tbody>
   273	        </table></div>
   274	      </div>
   275	      <div>
   276	        <h3 class="sub" style="margin-top:0">11/12 OTA (이번 달 유일)</h3>
   277	        <div class="tbl-wrap"><table>
   278	          <thead><tr><th>카드</th><th>변경</th></tr></thead>
   279	          <tbody>
   280	            <tr><td><span class="nerf">너프</span> Mobius M. Mobius</td><td class="num">3/3 → 3/2</td></tr>
   281	            <tr><td><span class="nerf">너프</span> Zombie Scarlet Witch</td><td class="num">3/4 → 3/3</td></tr>
   282	            <tr><td><span class="buff">버프</span> Captain Britain</td><td class="num">2/2 → 2/3</td></tr>
   283	            <tr><td><span class="buff">버프</span> Mister Sinister</td><td class="num">2/2 → 2/3</td></tr>
   284	            <tr><td><span class="buff">버프</span> Sword of Fu Xi (Lin Lie 토큰)</td><td class="num">2/2 → 2/3</td></tr>
   285	            <tr><td><span class="buff">버프</span> The Ten Rings (Shang-Chi, Master of the Rings 토큰)</td><td class="num">2/2 → 2/3, 강화형 2/3 → 2/5</td></tr>
   286	            <tr><td><span class="buff">버프</span> Shanna</td><td class="num">3/4 → 3/5</td></tr>
   287	            <tr><td><span class="buff">버프</span> Kang the Conqueror</td><td class="num">3/4 → 3/5</td></tr>
   288	            <tr><td><span class="buff">버프</span> Spider-Man Noir</td><td class="num">4/5 → 4/6</td></tr>
   289	            <tr><td><span class="buff">버프</span> Onslaught</td><td class="num">6/8 → 6/9</td></tr>
   290	          </tbody>
   291	        </table></div>
   292	        <p class="muted" style="margin-top:8px">개발사: “선두 덱들이 크게 앞서지 않는 안정적인 메타”. 일반 Shang-Chi는 버프 대상 아님. <a href="https://marvelsnap.com/balance-update-november-12-2026/" target="_blank" rel="noopener">공식 공지</a></p>
   293	      </div>
   294	    </div>
   295	  </section>
   296	
   297	  <section id="basics" aria-labelledby="basics-h">
   298	    <h2 id="basics-h">기본 규칙 · 덱 빌딩</h2>
   299	    <details open>
   300	      <summary>게임 기본 규칙</summary>
   301	      <div><ul>
   302	        <li><b>덱</b>: 12장, 같은 카드 중복 불가. 기본 6턴, N턴에 N에너지 (효과로 변동 가능)</li>
   303	        <li><b>승리</b>: 상대보다 더 많은 로케이션에서 이기면 승리 (1승 2무도 승리). 이긴 수가 같으면 총 파워 합 (Bar With No Name 같은 예외 있음)</li>
   304	        <li><b>로케이션</b>: 1·2·3턴에 하나씩 공개 — 덱 플랜을 망가뜨릴 수 있어 유연성이 중요</li>
   305	        <li><b>공개 순서</b>: 이기고 있는 로케이션이 많은 쪽 → 같으면 총 파워 높은 쪽 → 그래도 같으면 무작위</li>
   306	        <li><b>큐브</b>: 기본 1. 스냅은 각자 1회, 다음 턴 시작 시 판돈 2배 적용 → 상대는 그 전에 후퇴하면 기존 판돈만 잃음. 마지막 턴 자동 2배, 최대 8큐브</li>
   307	        <li><b>랭크</b>: 1~100, 100 도달 시 Infinite. 승률보다 <b>평균 큐브</b>가 랭크업 속도를 결정 — 이길 판은 크게, 질 판은 일찍 후퇴</li>
   308	        <li><b>카드 풀</b>: 스타터 별도 + 컬렉션 레벨에 따라 Series 1~5. 신규 카드는 주로 Series 5로 나왔다가 하향</li>
   309	      </ul></div>
   310	    </details>
   311	    <details>
   312	      <summary>덱 빌딩 원칙</summary>
   313	      <div><ul>
   314	        <li><b>코어 4~6장</b>: 승리 플랜 (시너지 엔진 + 페이오프)</li>
   315	        <li><b>커브</b>: 1~6턴 에너지를 낭비 없이. 특히 5~6턴 마무리</li>
   316	        <li><b>유연 카드 / 테크 2~3장</b>: 메타 대응</li>
   317	        <li><b>큐브 관점</b>: 판세를 일찍 읽을 수 있는 덱이 스냅·후퇴 판단에 유리</li>
   318	      </ul></div>
   319	    </details>
   320	    <details>
   321	      <summary>자주 보이는 테크 카드</summary>
   322	      <div><ul>
   323	        <li><b>Shadow King</b>: 이 로케이션 카드 파워를 기본값으로 (양쪽 모두. Ongoing 버프는 다시 적용, Luke Cage로 못 막음)</li>
   324	        <li><b>Mobius M. Mobius</b>: 내 코스트 증가 방지 + 상대 코스트 감소 차단 (11/12 너프 3/2)</li>
   325	        <li><b>Cosmo</b>: 이 로케이션 On Reveal 봉쇄 (양쪽 모두)</li>
   326	        <li><b>Luke Cage</b>: 내 카드 파워 감소 방지</li>
   327	        <li><b>Enchantress</b>: 이 로케이션 Ongoing 능력 제거 (내 카드 포함)</li>
   328	        <li><b>Rogue</b>: 이 로케이션 적 Ongoing 카드 1장의 능력을 빼앗음</li>
   329	      </ul></div>
   330	    </details>
   331	  </section>
   332	
   333	  <section id="sources" aria-labelledby="src-h">
   334	    <h2 id="src-h">출처 · 해석 주의</h2>
   335	    <div class="tbl-wrap"><table>
   336	      <thead><tr><th>출처</th><th>기간 / 모집단</th><th>특징</th></tr></thead>
   337	      <tbody>
   338	        <tr><td><a href="https://www.snapvault.app/meta" target="_blank" rel="noopener">SnapVault</a> <b>랭크 7일</b></td><td id="svSrc">최근 7일, 랭크만, 10판 이상 리스트</td><td><b>덱 카드의 승률·판수·평균 큐브</b> (12장 완전 일치). 100판 미만 빌드는 제외. 예측 승률도 이 데이터로 계산</td></tr>
   339	        <tr><td><a href="https://www.snapvault.app/meta" target="_blank" rel="noopener">SnapVault</a> 메타</td><td>최근 7일, 전체 모드</td><td>티어 산정 기준. 승률 95% 신뢰구간 하한으로 순위 → 표본 크기 반영. 100판 미만은 Rising</td></tr>
   340	        <tr><td><a href="https://snapcomplete.com/play/decks" target="_blank" rel="noopener">SnapComplete</a></td><td>이번 주, Ranked + Conquest</td><td>승률 보정(smoothing). 판수가 가장 큼</td></tr>
   341	        <tr><td><a href="https://snap.untapped.gg/en/meta" target="_blank" rel="noopener">Untapped.gg</a></td><td>30일, 랭크 10~79, Pool 3+</td><td>승률이 크게 높게 나옴 → 절대값 비교 금지</td></tr>
   342	        <tr><td><a href="https://snap.fan/cards/tier-list/" target="_blank" rel="noopener">snap.fan 카드 티어</a></td><td>11/13 갱신</td><td>SnapComplete 데이터 기반 → 독립 검증 아님</td></tr>
   343	        <tr><td><a href="https://marvelsnapzone.com/marvel-snap-ranked-meta-tier-list-november-8-2026/" target="_blank" rel="noopener">Marvel Snap Zone 티어표</a></td><td>11/8 (OTA 전)</td><td>편집자 평가, 표본 수 비공개. 참고 덱 3개(Small On Reveals · Created Disruption · Curved Wiccan)와 교차 확인에 사용</td></tr>
   344	        <tr><td><a href="https://snapcomplete.com/play/meta/ota" target="_blank" rel="noopener">SnapComplete OTA 결과</a></td><td>11/12 OTA 전후, OTA 후 랭크 29만 판</td><td>Captain Britain 승률 51.0→53.9%, Mobius 52.7→50.0%, Zombie Scarlet Witch 55.0→54.4% (영향 작음)</td></tr>
   345	        <tr><td>참고만</td><td colspan="2">Alexander Coccia 주간 Top 10, r/MarvelSnapComp 주간 스레드, Fourth Location, 디시 마블스냅 갤러리 — 리스트 교차 확인용 (승률·표본 없음)</td></tr>
   346	      </tbody>
   347	    </table></div>
   348	    <details style="margin-top:12px">
   349	      <summary>예측 승률 계산 방법</summary>
   350	      <div><ul>
   351	        <li><b>같은 계열</b> = 원본과 12장 중 8장 이상 겹치는 랭크 7일 리스트</li>
   352	        <li>같은 계열에서 그 카드 <b>없이</b> 플레이된 판이 100판 미만이면 덱의 엔진 카드로 보고 <b>예측 불가</b></li>
   353	        <li><b>대체 카드</b> = 같은 계열에서 그 카드를 뺀 리스트에 실제로 가장 많이 들어간 보유 카드 (50판 이상)</li>
   354	        <li><b>카드별 기여도</b> = 원본과 6장 이상 겹치는 리스트로 가중 릿지 회귀 (겹칠수록 가중치 큼)</li>
   355	        <li><b>예측</b> = 원본 실제 승률 + Σ(들어가는 카드 기여 − 빠지는 카드 기여). 원본보다 높게는 잡지 않음</li>
   356	        <li>한계: 카드 간 시너지를 따로 모델링하지 않고, 데이터가 얇으면 하락 폭이 작게 나올 수 있음 → <b>참고용 추정치</b></li>
   357	      </ul></div>
   358	    </details>
   359	    <details>
   360	      <summary>덱 코드 복사</summary>
   361	      <div><ul>
   362	        <li>게임 덱 편집 화면에서 붙여넣기로 덱을 만들 수 있는 코드입니다 (카드별 게임 코드를 쉼표로 이어 base64 — SnapVault · Marvel Snap Zone과 같은 형식)</li>
   363	        <li>미보유 카드가 있는 덱은 <b>대체 덱 코드</b>(내 카드로 바꾼 버전)를 쓰세요</li>
   364	      </ul></div>
   365	    </details>
   366	    <ul class="muted" style="padding-left:18px">
   367	      <li>SnapComplete · Untapped는 11/12 OTA 이전 판이 섞였을 가능성이 큼. SnapVault는 밸런스 변경 덱 제외 정책을 밝혔지만 실제 처리는 불명확</li>
   368	      <li>OTA 영향(⬆ 버프 카드 포함 · ⬇ 너프 카드 포함)은 표시만 했고 티어에는 반영하지 않음 — 다음 주 데이터로 확인 필요</li>
   369	      <li>출처마다 모집단이 달라 같은 덱도 승률이 10%p 이상 차이 남</li>
   370	    </ul>
   371	  </section>
   372	</main>
   373	
   374	<footer class="wrap">
   375	  비공식 개인 덱 빌딩 노트입니다. 수치는 각 트래커 사이트의 공개 데이터를 정리한 것으로, 집계 시점에 따라 달라질 수 있습니다. 카드 이미지: <a href="https://snap.untapped.gg/" target="_blank" rel="noopener">Untapped.gg</a>
   376	</footer>
   377	<div class="toast" id="toast" role="status" aria-live="polite"></div>
   378	
   379	<script src="data.js"></script>
   380	<script>
   381	(function () {
   382	  const D = window.SNAP_DATA;
   383	  const C = D.cards;
   384	  const $ = (id) => document.getElementById(id);
   385	  const esc = (s) => String(s).replace(/[&<>"]/g, (c) => ({ "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;" }[c]));
   386	  const nm = (id) => (C[id] ? C[id].name : id);
   387	  const num = (n) => Number(n).toLocaleString("ko-KR");
   388	  const sgn = (n) => (n > 0 ? "+" : "") + n.toFixed(2);
   389	  const IMG = (id) => `https://snapjson.untapped.gg/art/render/framebreak/common/256/${encodeURIComponent(id)}.webp`;
   390	  const deckCode = (ids) => btoa(ids.map((id) => C[id].code).join(","));
   391	
   392	  /* theme */
   393	  const root = document.documentElement;
   394	  function applyTheme(t) { if (t) root.setAttribute("data-theme", t); else root.removeAttribute("data-theme"); }
   395	  try { applyTheme(localStorage.getItem("snap-theme")); } catch (e) {}
   396	  $("themeBtn").addEventListener("click", () => {
   397	    const dark = root.getAttribute("data-theme") === "dark" ||
   398	      (!root.getAttribute("data-theme") && matchMedia("(prefers-color-scheme: dark)").matches);
   399	    const next = dark ? "light" : "dark";
   400	    applyTheme(next);
   401	    try { localStorage.setItem("snap-theme", next); } catch (e) {}
   402	  });
   403	
   404	  /* 덱별 '내 기준 승률' 계산 */
   405	  const UNOWNED = new Set(D.unowned.map((u) => u.id));
   406	  function effOf(b) {
   407	    if (!b.miss.length) return { wr: b.stats.wr, kind: "real" };
   408	    if (b.pred && b.pred.ok) return { wr: b.pred.wr, kind: "pred" };
   409	    return { wr: null, kind: "none" };
   410	  }
   411	  const cmpEff = (a, b) => (b.wr ?? -1) - (a.wr ?? -1);
   412	  D.decks.forEach((d, i) => {
   413	    d._key = "d" + i;
   414	    d.builds.forEach((b, j) => { b._eff = effOf(b); b._key = d._key + "b" + j; });
   415	    d.builds.sort((x, y) => cmpEff(x._eff, y._eff) || y.stats.wr - x.stats.wr);
   416	    d._eff = d.builds[0]._eff;
   417	    d._raw = Math.max(...d.builds.map((b) => b.stats.wr));
   418	    d._status = d.builds.some((b) => !b.miss.length) ? "ok" : d.builds.some((b) => b._eff.kind === "pred") ? "pred" : "none";
   419	    d._miss = d.builds.map((b) => b.miss).sort((x, y) => x.length - y.length)[0];
   420	  });
   421	  const byKey = Object.fromEntries(D.decks.map((d) => [d._key, d]));
   422	  const buildByKey = Object.fromEntries(D.decks.flatMap((d) => d.builds.map((b) => [b._key, b])));
   423	
   424	  const TIER_LABEL = { S: "S", A: "A", B: "B", C: "C", UT: "UT", REF: "참고" };
   425	  const TIER_ORDER = { S: 0, A: 1, B: 2, C: 3, UT: 4, REF: 5 };
   426	  const RS = D.rankedSource;
   427	
   428	  /* hero */
   429	  const nOk = D.decks.filter((d) => d._status === "ok").length;
   430	  const nPred = D.decks.filter((d) => d._status === "pred").length;
   431	  $("heroSub").textContent = `메타 기준일 ${D.asOf} · Knights of Avalon 시즌 2주차 · 11/12 OTA 직후 · 승률은 ${RS.site} ${RS.mode} ${RS.window}`;
   432	  $("stats").innerHTML = [
   433	    [D.decks.length, `랭크 ${RS.window} ${RS.minGames}판+ 덱`], [nOk, "지금 바로 사용 가능"], [nPred, "내 카드로 대체 예측"], [D.unowned.length, "미보유 Series 5"],
   434	  ].map(([n, l]) => `<div class="stat"><b>${n}</b><span>${l}</span></div>`).join("");
   435	  const fetched = RS.fetchedAt.replace("T", " ").slice(0, 16) + " UTC";
   436	  $("decksLead").innerHTML = `승률·판수는 <b>${esc(RS.site)} ${esc(RS.mode)} 최근 ${esc(RS.window)}</b>에서 12장이 똑같은 덱의 전적입니다 (${esc(fetched)} 수집, ${RS.minGames}판 미만 제외). ` +
   437	    `정렬은 <b>내가 기대할 수 있는 승률</b> 순 — 바로 쓸 수 있는 덱은 실제 승률, 미보유 카드가 있는 덱은 내 카드로 바꿨을 때의 <b>예측 승률</b>(참고용 추정)입니다. ` +
   438	    `티어 배지는 노트의 잠정 평가(전체 모드 기준)이고, 흐린 카드 ✕ = 내가 없는 카드.`;
   439	  $("svSrc").textContent = `최근 ${RS.window}, ${RS.mode}만, 10판 이상 리스트 ${num(RS.lists)}개 (${fetched})`;
   440	
   441	  /* filters */
   442	  const state = { sort: "eff", own: "all", tier: "all", fam: "all" };
   443	  try { Object.assign(state, JSON.parse(localStorage.getItem("snap-filters-v3") || "{}")); } catch (e) {}
   444	  const fams = [...new Set(D.decks.map((d) => d.family || "기타"))].sort((a, b) => (a === "기타") - (b === "기타") || a.localeCompare(b));
   445	  const FILTERS = {
   446	    sort: [["eff", "내 기준 승률"], ["raw", "원본 승률"], ["tier", "티어"]],
   447	    own: [["all", "전체"], ["ok", "바로 사용"], ["pred", "대체 예측"], ["none", "대체 불가"]],
   448	    tier: [["all", "전체"], ["S", "S"], ["A", "A"], ["B", "B"], ["C", "C"], ["UT", "UT 단독"], ["REF", "참고"]],
   449	    fam: [["all", "전체"], ...fams.map((f) => [f, f])],
   450	  };
   451	  const rowId = { sort: "fSort", own: "fOwn", tier: "fTier", fam: "fFam" };
   452	  function renderFilters() {
   453	    for (const key of Object.keys(FILTERS)) {
   454	      const row = $(rowId[key]);
   455	      row.querySelectorAll("button").forEach((b) => b.remove());
   456	      for (const [val, label] of FILTERS[key]) {
   457	        const b = document.createElement("button");
   458	        b.type = "button"; b.className = "chip-btn"; b.textContent = label;
   459	        b.setAttribute("aria-pressed", String(state[key] === val));
   460	        b.addEventListener("click", () => {
   461	          state[key] = val;
   462	          try { localStorage.setItem("snap-filters-v3", JSON.stringify(state)); } catch (e) {}
   463	          renderFilters(); renderDecks();
   464	        });
   465	        row.appendChild(b);
   466	      }
   467	    }
   468	  }
   469	
   470	  /* rendering */
   471	  function ownBadge(d) {
   472	    if (d._status === "ok") return `<span class="own ok">✓ 바로 사용</span>`;
   473	    if (d._status === "pred") return `<span class="own pred">${d._miss.length}장 대체</span>`;
   474	    return `<span class="own none">${d._miss.length}장 부족</span>`;
   475	  }
   476	  function fig(id, mark) {
   477	    const c = C[id];
   478	    const miss = UNOWNED.has(id);
   479	    const cls = ["cimg", miss ? "miss" : "", mark === "added" ? "added" : ""].filter(Boolean).join(" ");
   480	    const tip = `${c.name} (${c.cost}/${c.power})${miss ? " — 미보유" : mark === "added" ? " — 대체로 넣은 카드" : ""}`;
   481	    return `<figure class="${cls}" title="${esc(tip)}"><img loading="lazy" decoding="async" width="256" height="256" src="${IMG(id)}" alt="${esc(c.name)}" onerror="this.parentNode.classList.add('noimg')"><span class="ph">${c.cost}</span><figcaption>${esc(c.name)}</figcaption></figure>`;
   482	  }
   483	  function statLine(st, dim) {
   484	    return `<div class="wr-line"><span class="wr-big${dim ? " dim" : ""}">${st.wr.toFixed(1)}%</span><span class="wr-meta">${dim ? "원본 · " : ""}랭크 ${esc(RS.window)} · ${num(st.games)}판${st.cubes != null ? ` · 평균 큐브 ${sgn(st.cubes)}` : ""}</span></div>`;
   485	  }
   486	  function predHTML(b) {
   487	    const p = b.pred;
   488	    if (!p.ok) {
   489	      const why = (p.blockers || []).map((x) => `<b>${esc(nm(x.id))}</b> 없이 플레이된 같은 계열 판이 ${num(x.without)}판뿐`).join(", ");
   490	      return `<div class="pred no">예측 불가 — ${why || "대체할 카드 데이터 부족"}. 덱의 핵심 카드라 내 카드로 바꾼 버전의 근거가 없습니다.</div>`;
   491	    }
   492	    const diff = p.delta < 0 ? `원본 대비 ${p.delta.toFixed(1)}%p` : "원본과 비슷";
   493	    return `<div class="pred ok">
   494	      <div class="wr-line"><span class="pred-lbl">내 카드로 대체 시 예측</span><span class="wr-big">${p.wr.toFixed(1)}%</span><span class="wr-meta">${diff} · 같은 계열 ${num(p.archLists)}개 리스트 ${num(p.archGames)}판 기반</span></div>
   495	      <div class="swaps">${p.swaps.map((s) => `<span class="swap"><s>${esc(nm(s.out))}</s> → <b>${esc(nm(s.in))}</b></span>`).join("")}</div>
   496	      ${p.exact ? `<div class="wr-meta" style="margin-top:4px">이 대체 리스트 자체의 실제 전적: ${p.exact.wr.toFixed(1)}% · ${num(p.exact.games)}판</div>` : ""}
   497	    </div>`;
   498	  }
   499	  function buildHTML(b) {
   500	    const p = b.pred && b.pred.ok ? b.pred : null;
   501	    const added = p ? new Set(p.swaps.map((s) => s.in)) : null;
   502	    const gridOrig = `<div class="grid12" data-view="orig">${b.ids.map((id) => fig(id)).join("")}</div>`;
   503	    const gridAlt = p ? `<div class="grid12" data-view="alt" hidden>${p.ids.map((id) => fig(id, added.has(id) ? "added" : "")).join("")}</div>` : "";
   504	    const btns = [];
   505	    if (p) {
   506	      btns.push(`<button class="btn primary" type="button" data-act="code" data-ids="${p.ids.join(",")}" data-what="대체 덱 코드">대체 덱 코드 복사</button>`);
   507	      btns.push(`<button class="btn" type="button" data-act="view" data-b="${b._key}">대체 덱 보기</button>`);
   508	      btns.push(`<button class="btn ghost" type="button" data-act="code" data-ids="${b.ids.join(",")}" data-what="원본 덱 코드">원본 덱 코드</button>`);
   509	    } else {
   510	      btns.push(`<button class="btn${b.miss.length ? "" : " primary"}" type="button" data-act="code" data-ids="${b.ids.join(",")}" data-what="덱 코드">덱 코드 복사</button>`);
   511	    }
   512	    btns.push(`<button class="btn ghost" type="button" data-act="list" data-b="${b._key}">카드 목록</button>`);
   513	    return `<div class="build" data-b="${b._key}">
   514	      ${b.label ? `<p class="build-label">${esc(b.label)}</p>` : ""}
   515	      ${statLine(b.stats, !!b.miss.length)}
   516	      ${gridOrig}${gridAlt}
   517	      ${b.miss.length ? predHTML(b) : ""}
   518	      <div class="btns">${btns.join("")}</div>
   519	    </div>`;
   520	  }
   521	  function deckHTML(d, rank) {
   522	    const tags = [];
   523	    if (d.family) tags.push(`<span class="tag">${esc(d.family)}</span>`);
   524	    for (const o of d.ota) tags.push(`<span class="tag ${o.dir}">${o.dir === "up" ? "⬆" : "⬇"} ${esc(o.card)}</span>`);
   525	    const ev = [...d.evidence, ...(d.notes || [])];
   526	    const dropped = (d.droppedBuilds || []).length
   527	      ? `<p class="dropped">제외된 빌드: ${d.droppedBuilds.map((x) => `${esc(x.label || "기본")} (${num(x.games)}판)`).join(", ")} — 랭크 ${esc(RS.window)} ${RS.minGames}판 미만</p>` : "";
   528	    return `<article class="deck">
   529	      <div class="deck-head">
   530	        <div class="rank" aria-label="순위">${rank}</div>
   531	        <div class="tier ${d.tier}" aria-label="티어 ${TIER_LABEL[d.tier]}">${TIER_LABEL[d.tier]}</div>
   532	        <div class="deck-title"><h3>${d.no ? `<span class="no">#${d.no}</span>` : ""}${esc(d.name)}</h3>${tags.length ? `<div class="tags">${tags.join("")}</div>` : ""}</div>
   533	        ${ownBadge(d)}
   534	      </div>
   535	      ${d.builds.map(buildHTML).join("")}
   536	      ${dropped}
   537	      ${ev.length ? `<details class="ev"><summary>티어 근거 · 메모</summary><div><ul>${ev.map((e) => `<li>${esc(e)}</li>`).join("")}</ul></div></details>` : ""}
   538	    </article>`;
   539	  }
   540	
   541	  function renderDecks() {
   542	    const out = D.decks.filter((d) => {
   543	      if (state.tier !== "all" && d.tier !== state.tier) return false;
   544	      if (state.own !== "all" && d._status !== state.own) return false;
   545	      if (state.fam !== "all" && (d.family || "기타") !== state.fam) return false;
   546	      return true;
   547	    });
   548	    if (state.sort === "eff") out.sort((a, b) => cmpEff(a._eff, b._eff) || b._raw - a._raw);
   549	    else if (state.sort === "raw") out.sort((a, b) => b._raw - a._raw);
   550	    else out.sort((a, b) => TIER_ORDER[a.tier] - TIER_ORDER[b.tier] || (a.no || 99) - (b.no || 99) || b._raw - a._raw);
   551	    $("countLine").textContent = `${out.length}개 덱 표시`;
   552	    $("deckList").innerHTML = out.length ? out.map((d, i) => deckHTML(d, i + 1)).join("") : `<div class="empty">조건에 맞는 덱이 없습니다.</div>`;
   553	  }
   554	
   555	  $("deckList").addEventListener("click", (e) => {
   556	    const btn = e.target.closest("button[data-act]"); if (!btn) return;
   557	    const act = btn.dataset.act;
   558	    if (act === "code") {
   559	      const code = deckCode(btn.dataset.ids.split(","));
   560	      copy(code, `${btn.dataset.what}를 복사했어요 — 게임 덱 편집 화면에서 붙여넣기`);
   561	    } else if (act === "list") {
   562	      const b = buildByKey[btn.dataset.b];
   563	      const box = btn.closest(".build");
   564	      const alt = box.querySelector('[data-view="alt"]');
   565	      const ids = alt && !alt.hidden ? b.pred.ids : b.ids;
   566	      copy(ids.map((id) => `(${C[id].cost}) ${C[id].name}`).join("\n"), "카드 목록을 복사했어요");
   567	    } else if (act === "view") {
   568	      const box = btn.closest(".build");
   569	      const orig = box.querySelector('[data-view="orig"]'), alt = box.querySelector('[data-view="alt"]');
   570	      const showAlt = alt.hidden;
   571	      alt.hidden = !showAlt; orig.hidden = showAlt;
   572	      btn.textContent = showAlt ? "원본 덱 보기" : "대체 덱 보기";
   573	    }
   574	  });
   575	  function copy(text, msg) {
   576	    const ok = () => toast(msg), fail = () => toast("복사 실패 — 브라우저가 클립보드 접근을 막았어요");
   577	    if (navigator.clipboard && window.isSecureContext) { navigator.clipboard.writeText(text).then(ok, fail); return; }
   578	    try {
   579	      const ta = document.createElement("textarea"); ta.value = text; ta.style.position = "fixed"; ta.style.opacity = "0";
   580	      document.body.appendChild(ta); ta.select(); document.execCommand("copy"); ta.remove(); ok();
   581	    } catch (e) { fail(); }
   582	  }
   583	  let tt;
   584	  function toast(msg) { const t = $("toast"); t.textContent = msg; t.classList.add("show"); clearTimeout(tt); tt = setTimeout(() => t.classList.remove("show"), 2200); }
   585	
   586	  if (D.excluded.length) {
   587	    $("excludedLine").innerHTML = `<b>랭크 ${esc(RS.window)} ${RS.minGames}판 미만이라 제외한 덱</b> — ` +
   588	      D.excluded.map((x) => `${x.no ? "#" + x.no + " " : ""}${esc(x.name)} (${num(x.games)}판)`).join(" · ");
   589	  }
   590	
   591	  /* collection */
   592	  $("collLead").textContent = `${D.collectionUpdated} 인게임 캡처 기준 미보유 Series 5 ${D.unowned.length}장. 이 목록에 없는 Series 5는 보유한 것으로 간주합니다.`;
   593	  const label = (d) => (d.no ? "#" + d.no : esc(d.name));
   594	  const prio = D.unowned.map((u) => {
   595	    const inDecks = D.decks.filter((d) => d.builds.some((b) => b.ids.includes(u.id)));
   596	    const unlocks = D.decks.filter((d) => d._status !== "ok" && d._miss.length === 1 && d._miss[0] === u.id);
   597	    return { u, inDecks, unlocks };
   598	  }).sort((a, b) => b.inDecks.length - a.inDecks.length || b.unlocks.length - a.unlocks.length);
   599	  const fmtDecks = (arr) => arr.map((d) => `${label(d)}<span class="muted">(${d._raw.toFixed(1)}%)</span>`).join(", ");
   600	  const used = prio.filter((p) => p.inDecks.length);
   601	  const unused = prio.filter((p) => !p.inDecks.length);
   602	  $("prioTable").innerHTML = `<thead><tr><th>카드</th><th>코/파</th><th>등장</th><th>들어가는 덱</th><th>얻으면 바로 열리는 덱</th></tr></thead><tbody>` +
   603	    used.map((p) => `<tr><td><b>${esc(p.u.name)}</b></td><td class="num">${esc(p.u.stat)}</td><td class="num">${p.inDecks.length}</td><td>${fmtDecks(p.inDecks)}</td><td>${p.unlocks.length ? fmtDecks(p.unlocks) : '<span class="muted">—</span>'}</td></tr>`).join("") +
   604	    `<tr><td colspan="5" class="muted">덱 목록에 없음: ${unused.map((p) => esc(p.u.name)).join(", ")}</td></tr></tbody>`;
   605	  $("unownedAll").innerHTML = D.unowned.map((u) => `<span class="card">${esc(u.name)} <span class="muted">${esc(u.stat)}</span></span>`).join("");
   606	
   607	  renderFilters();
   608	  renderDecks();
   609	})();
   610	</script>
   611	</body>
   612	</html>

hook: PostToolUse
hook: PostToolUse
exec
/bin/zsh -lc 'for p in /AGENTS.md /Users/AGENTS.md /Users/mac_al03241630/AGENTS.md /Users/mac_al03241630/Project/AGENTS.md /Users/mac_al03241630/Project/marvelsnap/AGENTS.md; do if [ -f "$p" ]; then cat "$p"; fi; done' in /Users/mac_al03241630/Project/marvelsnap
 succeeded in 0ms:
exec
/bin/zsh -lc 'git status --short' in /Users/mac_al03241630/Project/marvelsnap
 succeeded in 0ms:
 M .gitignore
 M README.md
 M data.js
 M index.html
 M notes/collection.md
 M notes/meta-2026-11-14.md
 M tools/build_data.py
?? tools/fetch_sv.py

hook: PostToolUse
hook: PostToolUse
exec
/bin/zsh -lc 'nl -ba tools/fetch_sv.py' in /Users/mac_al03241630/Project/marvelsnap
exec
/bin/zsh -lc "rg --files --hidden -g '"'!'"\\.git/**' -g '*AGENTS.md' -g 'cache/**' -g 'notes/**' -g 'README*'" in /Users/mac_al03241630/Project/marvelsnap
 succeeded in 0ms:
     1	#!/usr/bin/env python3
     2	"""SnapVault 공개 API에서 카드 목록과 랭크 7일 덱 통계를 받아 cache/ 에 저장.
     3	
     4	사용: python3 tools/fetch_sv.py
     5	- cache/sv_cards.json   : 카드 id, 이름, 코스트, 덱 코드용 deckCode
     6	- cache/sv_ranked7.json : 랭크(ranked + ranked_infinite) 최근 7일, 10판 이상 덱의 12장 구성과 승패·큐브
     7	cache/ 는 커밋하지 않는다 (gitignore). build_data.py 가 읽어서 data.js 에 필요한 값만 넣는다.
     8	"""
     9	import json
    10	import time
    11	import urllib.request
    12	from datetime import datetime, timezone
    13	from pathlib import Path
    14	
    15	ROOT = Path(__file__).resolve().parent.parent
    16	CACHE = ROOT / "cache"
    17	BASE = "https://www.snapvault.app/api"
    18	UA = {"User-Agent": "Mozilla/5.0"}
    19	MIN_GAMES = 10
    20	PAGE = 100
    21	
    22	
    23	def get(url, timeout=90, tries=3):
    24	    for i in range(tries):
    25	        try:
    26	            with urllib.request.urlopen(urllib.request.Request(url, headers=UA), timeout=timeout) as r:
    27	                return json.load(r)
    28	        except Exception as e:  # 네트워크 일시 오류만 재시도
    29	            if i == tries - 1:
    30	                raise
    31	            print(f"  재시도 {i + 1}: {e}")
    32	            time.sleep(3)
    33	
    34	
    35	def main():
    36	    CACHE.mkdir(exist_ok=True)
    37	    cards = get(f"{BASE}/cards/minimal-for-matches")
    38	    (CACHE / "sv_cards.json").write_text(json.dumps(cards, ensure_ascii=False), encoding="utf-8")
    39	    print(f"카드 {len(cards)}장")
    40	
    41	    decks, off = {}, 0
    42	    while True:
    43	        url = (f"{BASE}/decks/public?statsWindow=7d&mode=ranked&minGames={MIN_GAMES}&minPlayers=1"
    44	               f"&hideStale=false&limit={PAGE}&offset={off}&sortBy=confidence&sortDirection=desc")
    45	        d = get(url)
    46	        for x in d["decks"]:
    47	            decks[x["cardSignature"]] = {"cardIds": x["cardIds"], "stats": x["matchStats"], "players": x.get("playerCount")}
    48	        off += PAGE
    49	        if not d["hasMore"] or off >= 10000:
    50	            break
    51	        time.sleep(0.5)  # 서버 부담 줄이기
    52	    out = {"fetchedAt": datetime.now(timezone.utc).isoformat(timespec="seconds"),
    53	           "window": "7d", "mode": "ranked", "minGames": MIN_GAMES, "decks": list(decks.values())}
    54	    (CACHE / "sv_ranked7.json").write_text(json.dumps(out, ensure_ascii=False), encoding="utf-8")
    55	    print(f"랭크 7일 덱 {len(decks)}개 ({MIN_GAMES}판 이상)")
    56	
    57	
    58	if __name__ == "__main__":
    59	    main()

 succeeded in 0ms:
notes/collection.md
notes/meta-2026-11-14.md
README.md

hook: PostToolUse Completed
hook: PostToolUse
hook: PostToolUse
hook: PostToolUse Completed
hook: PostToolUse Completed
hook: PostToolUse Completed
hook: PostToolUse Completed
hook: PostToolUse Completed
hook: PreToolUse
hook: PreToolUse
hook: PreToolUse
hook: PreToolUse
hook: PreToolUse
hook: PreToolUse
hook: PreToolUse Completed
hook: PreToolUse Completed
hook: PreToolUse Completed
hook: PreToolUse Completed
hook: PreToolUse Completed
hook: PreToolUse Completed
exec
/bin/zsh -lc 'nl -ba notes/collection.md' in /Users/mac_al03241630/Project/marvelsnap
 succeeded in 0ms:
     1	# 내 컬렉션 — 미보유 카드 목록
     2	
     3	> 마지막 갱신: 2026-11-14 (사용자 인게임 "미보유 시리즈 5 카드" 화면 캡처 기준)
     4	> 덱 추천 시 이 파일을 먼저 확인할 것. 카드 획득·추가 미보유 발견 시 즉시 갱신 (페이지 데이터 `tools/` 재생성도 같이).
     5	
     6	## 전제
     7	- 아래 **Series 5 24장 외의 Series 5 카드는 모두 보유**
     8	- Series 4 이하 미보유 여부는 **아직 미확인** → 확인되면 아래에 추가
     9	
    10	## 미보유 Series 5 (24장)
    11	
    12	### 시즌 카드 화면 (8장)
    13	| 시즌 | 카드 | 코스트/파워 | 화면 표시 기간 |
    14	|---|---|---|---|
    15	| 아발론의 기사들 (Knights of Avalon) | Lancelot | 4/6 | 7주 3일 |
    16	| 〃 | Captain Britain | 2/3 | 〃 |
    17	| 〃 | Merlin of Avalon | 1/2 | 〃 |
    18	| 뱀파이어 대 좀비 (Vampires vs. Zombies) | Vampire Deacon Frost | 4/5 | 2주 3일 |
    19	| 〃 | Zombie Black Cat | 3/5 | 〃 |
    20	| 〃 | Vampire Enchantress | 6/7 | 〃 |
    21	| 〃 | Zombie Blade | 2/3 | 〃 |
    22	| 〃 | Zombie Venom | 3/3 | 〃 |
    23	
    24	### 그 외 Series 5 (16장)
    25	| 카드 | 코스트/파워 |
    26	|---|---|
    27	| Anti-Polar Magneto | 6/8 |
    28	| Aunt May | 2/4 |
    29	| Boomerang | 2/3 |
    30	| Death (Fractured Frontier) | 5/9 |
    31	| Ezekiel Sims | 2/2 |
    32	| Friendly Neighborhood Carnage | 3/4 |
    33	| Jack Flag | 3/3 |
    34	| Kang the Conqueror | 3/5 |
    35	| Kluh | 5/11 |
    36	| Mary Jane | 3/3 |
    37	| Moondragon | 2/1 |
    38	| Rogue Scion of Division | 5/5 |
    39	| Scarlet Witch Queen of Chaos | 3/3 |
    40	| Storm Horseman of Famine | 3/1 |
    41	| Sub-Mariner | 1/2 |
    42	| Techno-Organic Virus | 2/? (원형 아트) |
    43	
    44	> 주의: 기본 **Death**, 기본 **Carnage**, 기본 **Enchantress**, 기본 **Storm**, **Zombie Scarlet Witch**는 위 카드들과 다른 카드이므로 보유한 것으로 간주.
    45	> 이름 대조 (2026-11-14, SnapVault 카드 DB): 캡처의 "Storm (부제 있는 변형판) 3/1" = **Storm Horseman of Famine**, "Kang the Conqueror" = 게임 데이터상 **Kang** (3/5).
    46	
    47	---
    48	
    49	## 메타 덱 30선 기준 사용 가능 여부 (meta-2026-11-14.md v2 번호)
    50	
    51	> v3부터 페이지가 이 판단을 자동으로 계산함 (랭크 7일 100판 미만 덱 제외, 미보유 덱은 대체 예측). 아래 표는 v2 시점 기록.
    52	> v3 결과(2026-11-14): 바로 사용 11덱 · 내 카드로 대체 예측 5덱 · 대체 불가(엔진 카드 미보유) 12덱. #10·13·16·17·25·27·30은 랭크 7일 100판 미만으로 제외.
    53	
    54	### ✅ 지금 바로 사용 가능 (미보유 0장) — 13덱 + 참고 2덱
    55	| # | 덱 | 티어 |
    56	|---|---|---|
    57	| 1 | Zombie Galacti / Shuri / Wong | **S** |
    58	| 7 | High Evolutionary | A |
    59	| 8 | Fantomex / Zombie Captain Marvel / Shadow King | A |
    60	| 12 | Zombie Galacti / Arthur / Stick | B |
    61	| 14 | Spider-Ham | B |
    62	| 18 | Patriot — Onslaught / Ultron / Blue Marvel | C |
    63	| 24 | Thor | UT 단독 |
    64	| 25 | Destroy (Death / Knull) | UT 단독 |
    65	| 26 | Silver Surfer | UT 단독 |
    66	| 27 | Galactus (두 변형 모두) | UT 단독 |
    67	| 28 | Living Tribunal | UT 단독 |
    68	| 29 | Mister Negative | UT 단독 |
    69	| 30 | Discard | UT 단독 |
    70	| 참고 | Sandstorm Patriot / Fantomex·Omega Sentinel | - |
    71	
    72	### ⚠️ 1장 미보유 — 대체 카드 검토 필요
    73	| # | 덱 | 티어 | 미보유 | 메모 |
    74	|---|---|---|---|---|
    75	| 4 | Fin Fang Foom / Gorr — Domino형 | **S** | Anti-Polar Magneto | 덱의 엔진 → 사실상 대체 불가 |
    76	| 5 | Stardust / GHoD — Sasquatch형 | **S** | Scarlet Witch Queen of Chaos | 생성 카드(Skill) 공급원 대체 필요 |
    77	| 10 | Zombie Horde — WBN / Web Sling형 | A | Scarlet Witch Queen of Chaos | Skill 생성 핵심 축 중 하나 → 약화 큼 |
    78	| 11 | Zombie Horde — Luke Cage형 | A | Scarlet Witch Queen of Chaos | 〃 |
    79	| 13 | Stardust / GHoD — Thanos FF형 | B | Scarlet Witch Queen of Chaos | 생성 카드 공급원 대체 필요 |
    80	
    81	### ❌ 핵심 2장 이상 미보유 — 현재 비추천
    82	| # | 덱 | 미보유 |
    83	|---|---|---|
    84	| 2 | APM / Arthur — Lancelot·Galacta형 | Captain Britain, Lancelot, APM |
    85	| 3 | APM / Doom — Rogue Scion형 | Captain Britain, Rogue Scion, APM |
    86	| 6 | Zombie Horde — Zombie Blade형 | Zombie Blade, SW Queen of Chaos |
    87	| 9 | Stardust / GHoD — Kluh형 | SW Queen of Chaos, Kluh |
    88	| 15 | Zombie Horde — Merlin형 | Merlin, Zombie Blade, SW Queen of Chaos |
    89	| 16 | Merlin 생성 카드 덱 | Merlin, SW Queen of Chaos |
    90	| 17 | Kitty Pryde | Merlin, SW Queen of Chaos |
    91	| 19 | APM / Jubilee형 | Captain Britain, APM (+ Lancelot 빌드면 Lancelot) |
    92	| 20 | Fin Fang Foom / Gorr — Zabu형 | Captain Britain, APM |
    93	| 21 | Zabu / Spider-Man BND / Superior Iron Man | Captain Britain, Lancelot |
    94	| 22 | Vampire Deacon Frost | Deacon Frost, Vampire Enchantress, Zombie Blade, SW QoC, APM (5장) |
    95	| 23 | Arthur / Doom — Moondragon형 | Moondragon, APM |
    96	
    97	---
    98	
    99	## 획득 우선순위 (메타 덱 30선에 들어가는 빈도 기준)
   100	
   101	| 순위 | 카드 | 들어가는 덱 | 얻으면 바로 열리는 덱 |
   102	|---|---|---|---|
   103	| 1 | **Scarlet Witch Queen of Chaos** | 10덱 (#5, 6, 9, 10, 11, 13, 15, 16, 17, 22) · snap.fan A티어 | #5(S), #10, #11(A), #13(B) |
   104	| 2 | **Anti-Polar Magneto** | 7덱 (#2, 3, 4, 19, 20, 22, 23) + Quicksilver · 시즌 최대 아키타입 | #4 FFF Domino형 (S) |
   105	| 3 | **Captain Britain** | 5덱 (#2, 3, 19, 20, 21) + Created Cards · snap.fan A티어, 11/12 버프 | APM과 함께 얻으면 #19(Captain Marvel 빌드), #20 |
   106	| 4 | Zombie Blade | 3덱 (#6, 15, 22) | SW QoC와 함께 얻으면 #6 (A) |
   107	| 4 | Lancelot | 3덱 (#2, 19 Lancelot 빌드, 21) | APM·Captain Britain과 함께 얻으면 #2(S), #21 |
   108	| 4 | Merlin of Avalon | 3덱 (#15, 16, 17) | SW QoC와 함께 얻으면 #16, #17 |
   109	| - | Rogue Scion / Kluh / Moondragon / Deacon Frost / Vampire Enchantress | 1~2덱 | 우선순위 낮음 |
   110	| - | Aunt May, Boomerang, Death FF, Ezekiel Sims, FN Carnage, Jack Flag, Kang, Mary Jane, Storm, Sub-Mariner, Techno-Organic Virus, Zombie Black Cat, Zombie Venom | 메타 30선에 없음 | 현재 메타 기준 후순위 (Kang은 11/12 버프 — 추후 재확인) |
   111	
   112	**조합 효과**: SW QoC + APM 두 장이면 바로 쓸 수 있는 덱(미보유 0장)이 13개 → 18개(#4, 5, 10, 11, 13 추가). 1장만 빠지는 덱도 7개(#6, 9, 16, 17, 19 Captain Marvel 빌드, 20, 23)로 늘어남.

hook: PostToolUse
exec
/bin/zsh -lc "nl -ba index.html | sed -n '220,405p'" in /Users/mac_al03241630/Project/marvelsnap
 succeeded in 0ms:
   220	        <li><b>Anti-Polar Magneto × Arthur Pendragon (4코스트 치트)</b> 계열이 시즌 최대 화두. Untapped 인기 1위 아키타입, SnapVault S티어에도 2개. Lancelot · Mordred · Captain Britain 등 시즌 신규 카드가 그대로 들어감.</li>
   221	        <li><b>Zombie Galacti / Shuri / Wong</b> — 랭크 7일 2,239판 60.0%로 표본이 가장 큰 고성능 덱 (전체 모드 2,476판 · +0.71 큐브). 다만 MSZ 11/8 티어표·Coccia Top 10에는 없음.</li>
   222	        <li><b>Stardust / Gambit Horseman of Death</b> 생성·테크 덱 — Sasquatch형이 SnapVault S. 피니셔만 바꾼 변형이 다수. Mobius 너프 영향권.</li>
   223	        <li><b>Zombie Horde</b> — 사용량이 많고 성적이 양호 (SnapComplete 5,526판 59.1%). Zombie Scarlet Witch 너프(-1 파워).</li>
   224	        <li><b>전통 강자</b> — High Evo · Fantomex는 두 출처 대표본으로 확인, Patriot은 Onslaught 버프 수혜. Destroy · Surfer · Thor · Galactus 등은 Untapped 단독 근거.</li>
   225	        <li>많이 쓰이지만 승률은 평범 — <b>Sandstorm Patriot</b> (최다 사용 7,093판, 승률 51%).</li>
   226	      </ul>
   227	    </div>
   228	  </section>
   229	
   230	  <section id="decks" aria-labelledby="decks-h">
   231	    <h2 id="decks-h">메타 덱 — 내 기준 승률순</h2>
   232	    <p class="lead" id="decksLead"></p>
   233	    <div class="filters" role="group" aria-label="덱 필터">
   234	      <div class="frow" id="fSort"><span class="lbl">정렬</span></div>
   235	      <div class="frow" id="fOwn"><span class="lbl">보유</span></div>
   236	      <div class="frow" id="fTier"><span class="lbl">티어</span></div>
   237	      <div class="frow" id="fFam"><span class="lbl">계열</span></div>
   238	    </div>
   239	    <p class="count-line" id="countLine"></p>
   240	    <div class="decks" id="deckList"></div>
   241	    <p class="excluded" id="excludedLine"></p>
   242	  </section>
   243	
   244	  <section id="collection" aria-labelledby="coll-h">
   245	    <h2 id="coll-h">내 컬렉션 — 미보유 카드</h2>
   246	    <p class="lead" id="collLead"></p>
   247	    <h3 class="sub">획득 우선순위 (위 덱 목록 등장 수 기준)</h3>
   248	    <div class="tbl-wrap"><table id="prioTable"></table></div>
   249	    <p class="muted" style="margin-top:8px">“얻으면 바로 열리는 덱” = 그 카드 한 장만 없어서 원본 그대로 못 쓰던 덱. 괄호 안은 원본 랭크 7일 승률.</p>
   250	    <h3 class="sub">미보유 Series 5 전체</h3>
   251	    <div class="cards" id="unownedAll"></div>
   252	    <p class="muted" style="margin-top:8px">Series 4 이하 미보유 여부는 아직 반영 전입니다.</p>
   253	  </section>
   254	
   255	  <section id="season" aria-labelledby="season-h">
   256	    <h2 id="season-h">시즌 · 패치</h2>
   257	    <p class="lead">Knights of Avalon (11/3 ~ 11/30) · 다음 OTA 12/3, 패치 12/15</p>
   258	    <div class="grid2">
   259	      <div>
   260	        <h3 class="sub" style="margin-top:0">시즌 신규 카드</h3>
   261	        <div class="tbl-wrap"><table>
   262	          <thead><tr><th>카드</th><th>코/파</th><th>능력</th><th>출시</th></tr></thead>
   263	          <tbody>
   264	            <tr><td>Arthur Pendragon<br><span class="muted">시즌패스</span></td><td class="num">4/4</td><td>On Reveal: Excalibur(1/1, Ongoing: 4코스트 이상 아군 +2)를 무료로 여기에 꺼냄</td><td class="num">11/3</td></tr>
   265	            <tr><td>Merlin of Avalon<br><span class="muted">슈퍼 프리미엄</span></td><td class="num">1/2</td><td>On Reveal: The Grand Design(6/0, 생성 카드 1장 낼 때마다 1코 감소, 다른 각 로케이션 아군 1장 +5)을 손에 추가</td><td class="num">11/3</td></tr>
   266	            <tr><td>Captain Britain</td><td class="num">2/3</td><td>4코스트 이상 카드를 낸 뒤: 그 카드 +1 파워, 손의 카드 1장 -1 코스트</td><td class="num">11/3</td></tr>
   267	            <tr><td>Mordred</td><td class="num">3/4</td><td>Ongoing: 여기 있는 더 높은 코스트 카드 1장당 +2 파워</td><td class="num">11/5</td></tr>
   268	            <tr><td>Lancelot</td><td class="num">4/6</td><td>Ongoing: 파워가 증가된 아군 +1 파워</td><td class="num">11/10</td></tr>
   269	            <tr><td>Elder Dragon of the Moon</td><td class="num">?</td><td class="muted">미출시</td><td class="num">11/17</td></tr>
   270	            <tr><td>Knight's Vow<br><span class="muted">이벤트 패스</span></td><td class="num">?</td><td class="muted">미출시</td><td class="num">11/19</td></tr>
   271	            <tr><td>Sir Percy Black Knight</td><td class="num">?</td><td class="muted">미출시</td><td class="num">11/24</td></tr>
   272	          </tbody>
   273	        </table></div>
   274	      </div>
   275	      <div>
   276	        <h3 class="sub" style="margin-top:0">11/12 OTA (이번 달 유일)</h3>
   277	        <div class="tbl-wrap"><table>
   278	          <thead><tr><th>카드</th><th>변경</th></tr></thead>
   279	          <tbody>
   280	            <tr><td><span class="nerf">너프</span> Mobius M. Mobius</td><td class="num">3/3 → 3/2</td></tr>
   281	            <tr><td><span class="nerf">너프</span> Zombie Scarlet Witch</td><td class="num">3/4 → 3/3</td></tr>
   282	            <tr><td><span class="buff">버프</span> Captain Britain</td><td class="num">2/2 → 2/3</td></tr>
   283	            <tr><td><span class="buff">버프</span> Mister Sinister</td><td class="num">2/2 → 2/3</td></tr>
   284	            <tr><td><span class="buff">버프</span> Sword of Fu Xi (Lin Lie 토큰)</td><td class="num">2/2 → 2/3</td></tr>
   285	            <tr><td><span class="buff">버프</span> The Ten Rings (Shang-Chi, Master of the Rings 토큰)</td><td class="num">2/2 → 2/3, 강화형 2/3 → 2/5</td></tr>
   286	            <tr><td><span class="buff">버프</span> Shanna</td><td class="num">3/4 → 3/5</td></tr>
   287	            <tr><td><span class="buff">버프</span> Kang the Conqueror</td><td class="num">3/4 → 3/5</td></tr>
   288	            <tr><td><span class="buff">버프</span> Spider-Man Noir</td><td class="num">4/5 → 4/6</td></tr>
   289	            <tr><td><span class="buff">버프</span> Onslaught</td><td class="num">6/8 → 6/9</td></tr>
   290	          </tbody>
   291	        </table></div>
   292	        <p class="muted" style="margin-top:8px">개발사: “선두 덱들이 크게 앞서지 않는 안정적인 메타”. 일반 Shang-Chi는 버프 대상 아님. <a href="https://marvelsnap.com/balance-update-november-12-2026/" target="_blank" rel="noopener">공식 공지</a></p>
   293	      </div>
   294	    </div>
   295	  </section>
   296	
   297	  <section id="basics" aria-labelledby="basics-h">
   298	    <h2 id="basics-h">기본 규칙 · 덱 빌딩</h2>
   299	    <details open>
   300	      <summary>게임 기본 규칙</summary>
   301	      <div><ul>
   302	        <li><b>덱</b>: 12장, 같은 카드 중복 불가. 기본 6턴, N턴에 N에너지 (효과로 변동 가능)</li>
   303	        <li><b>승리</b>: 상대보다 더 많은 로케이션에서 이기면 승리 (1승 2무도 승리). 이긴 수가 같으면 총 파워 합 (Bar With No Name 같은 예외 있음)</li>
   304	        <li><b>로케이션</b>: 1·2·3턴에 하나씩 공개 — 덱 플랜을 망가뜨릴 수 있어 유연성이 중요</li>
   305	        <li><b>공개 순서</b>: 이기고 있는 로케이션이 많은 쪽 → 같으면 총 파워 높은 쪽 → 그래도 같으면 무작위</li>
   306	        <li><b>큐브</b>: 기본 1. 스냅은 각자 1회, 다음 턴 시작 시 판돈 2배 적용 → 상대는 그 전에 후퇴하면 기존 판돈만 잃음. 마지막 턴 자동 2배, 최대 8큐브</li>
   307	        <li><b>랭크</b>: 1~100, 100 도달 시 Infinite. 승률보다 <b>평균 큐브</b>가 랭크업 속도를 결정 — 이길 판은 크게, 질 판은 일찍 후퇴</li>
   308	        <li><b>카드 풀</b>: 스타터 별도 + 컬렉션 레벨에 따라 Series 1~5. 신규 카드는 주로 Series 5로 나왔다가 하향</li>
   309	      </ul></div>
   310	    </details>
   311	    <details>
   312	      <summary>덱 빌딩 원칙</summary>
   313	      <div><ul>
   314	        <li><b>코어 4~6장</b>: 승리 플랜 (시너지 엔진 + 페이오프)</li>
   315	        <li><b>커브</b>: 1~6턴 에너지를 낭비 없이. 특히 5~6턴 마무리</li>
   316	        <li><b>유연 카드 / 테크 2~3장</b>: 메타 대응</li>
   317	        <li><b>큐브 관점</b>: 판세를 일찍 읽을 수 있는 덱이 스냅·후퇴 판단에 유리</li>
   318	      </ul></div>
   319	    </details>
   320	    <details>
   321	      <summary>자주 보이는 테크 카드</summary>
   322	      <div><ul>
   323	        <li><b>Shadow King</b>: 이 로케이션 카드 파워를 기본값으로 (양쪽 모두. Ongoing 버프는 다시 적용, Luke Cage로 못 막음)</li>
   324	        <li><b>Mobius M. Mobius</b>: 내 코스트 증가 방지 + 상대 코스트 감소 차단 (11/12 너프 3/2)</li>
   325	        <li><b>Cosmo</b>: 이 로케이션 On Reveal 봉쇄 (양쪽 모두)</li>
   326	        <li><b>Luke Cage</b>: 내 카드 파워 감소 방지</li>
   327	        <li><b>Enchantress</b>: 이 로케이션 Ongoing 능력 제거 (내 카드 포함)</li>
   328	        <li><b>Rogue</b>: 이 로케이션 적 Ongoing 카드 1장의 능력을 빼앗음</li>
   329	      </ul></div>
   330	    </details>
   331	  </section>
   332	
   333	  <section id="sources" aria-labelledby="src-h">
   334	    <h2 id="src-h">출처 · 해석 주의</h2>
   335	    <div class="tbl-wrap"><table>
   336	      <thead><tr><th>출처</th><th>기간 / 모집단</th><th>특징</th></tr></thead>
   337	      <tbody>
   338	        <tr><td><a href="https://www.snapvault.app/meta" target="_blank" rel="noopener">SnapVault</a> <b>랭크 7일</b></td><td id="svSrc">최근 7일, 랭크만, 10판 이상 리스트</td><td><b>덱 카드의 승률·판수·평균 큐브</b> (12장 완전 일치). 100판 미만 빌드는 제외. 예측 승률도 이 데이터로 계산</td></tr>
   339	        <tr><td><a href="https://www.snapvault.app/meta" target="_blank" rel="noopener">SnapVault</a> 메타</td><td>최근 7일, 전체 모드</td><td>티어 산정 기준. 승률 95% 신뢰구간 하한으로 순위 → 표본 크기 반영. 100판 미만은 Rising</td></tr>
   340	        <tr><td><a href="https://snapcomplete.com/play/decks" target="_blank" rel="noopener">SnapComplete</a></td><td>이번 주, Ranked + Conquest</td><td>승률 보정(smoothing). 판수가 가장 큼</td></tr>
   341	        <tr><td><a href="https://snap.untapped.gg/en/meta" target="_blank" rel="noopener">Untapped.gg</a></td><td>30일, 랭크 10~79, Pool 3+</td><td>승률이 크게 높게 나옴 → 절대값 비교 금지</td></tr>
   342	        <tr><td><a href="https://snap.fan/cards/tier-list/" target="_blank" rel="noopener">snap.fan 카드 티어</a></td><td>11/13 갱신</td><td>SnapComplete 데이터 기반 → 독립 검증 아님</td></tr>
   343	        <tr><td><a href="https://marvelsnapzone.com/marvel-snap-ranked-meta-tier-list-november-8-2026/" target="_blank" rel="noopener">Marvel Snap Zone 티어표</a></td><td>11/8 (OTA 전)</td><td>편집자 평가, 표본 수 비공개. 참고 덱 3개(Small On Reveals · Created Disruption · Curved Wiccan)와 교차 확인에 사용</td></tr>
   344	        <tr><td><a href="https://snapcomplete.com/play/meta/ota" target="_blank" rel="noopener">SnapComplete OTA 결과</a></td><td>11/12 OTA 전후, OTA 후 랭크 29만 판</td><td>Captain Britain 승률 51.0→53.9%, Mobius 52.7→50.0%, Zombie Scarlet Witch 55.0→54.4% (영향 작음)</td></tr>
   345	        <tr><td>참고만</td><td colspan="2">Alexander Coccia 주간 Top 10, r/MarvelSnapComp 주간 스레드, Fourth Location, 디시 마블스냅 갤러리 — 리스트 교차 확인용 (승률·표본 없음)</td></tr>
   346	      </tbody>
   347	    </table></div>
   348	    <details style="margin-top:12px">
   349	      <summary>예측 승률 계산 방법</summary>
   350	      <div><ul>
   351	        <li><b>같은 계열</b> = 원본과 12장 중 8장 이상 겹치는 랭크 7일 리스트</li>
   352	        <li>같은 계열에서 그 카드 <b>없이</b> 플레이된 판이 100판 미만이면 덱의 엔진 카드로 보고 <b>예측 불가</b></li>
   353	        <li><b>대체 카드</b> = 같은 계열에서 그 카드를 뺀 리스트에 실제로 가장 많이 들어간 보유 카드 (50판 이상)</li>
   354	        <li><b>카드별 기여도</b> = 원본과 6장 이상 겹치는 리스트로 가중 릿지 회귀 (겹칠수록 가중치 큼)</li>
   355	        <li><b>예측</b> = 원본 실제 승률 + Σ(들어가는 카드 기여 − 빠지는 카드 기여). 원본보다 높게는 잡지 않음</li>
   356	        <li>한계: 카드 간 시너지를 따로 모델링하지 않고, 데이터가 얇으면 하락 폭이 작게 나올 수 있음 → <b>참고용 추정치</b></li>
   357	      </ul></div>
   358	    </details>
   359	    <details>
   360	      <summary>덱 코드 복사</summary>
   361	      <div><ul>
   362	        <li>게임 덱 편집 화면에서 붙여넣기로 덱을 만들 수 있는 코드입니다 (카드별 게임 코드를 쉼표로 이어 base64 — SnapVault · Marvel Snap Zone과 같은 형식)</li>
   363	        <li>미보유 카드가 있는 덱은 <b>대체 덱 코드</b>(내 카드로 바꾼 버전)를 쓰세요</li>
   364	      </ul></div>
   365	    </details>
   366	    <ul class="muted" style="padding-left:18px">
   367	      <li>SnapComplete · Untapped는 11/12 OTA 이전 판이 섞였을 가능성이 큼. SnapVault는 밸런스 변경 덱 제외 정책을 밝혔지만 실제 처리는 불명확</li>
   368	      <li>OTA 영향(⬆ 버프 카드 포함 · ⬇ 너프 카드 포함)은 표시만 했고 티어에는 반영하지 않음 — 다음 주 데이터로 확인 필요</li>
   369	      <li>출처마다 모집단이 달라 같은 덱도 승률이 10%p 이상 차이 남</li>
   370	    </ul>
   371	  </section>
   372	</main>
   373	
   374	<footer class="wrap">
   375	  비공식 개인 덱 빌딩 노트입니다. 수치는 각 트래커 사이트의 공개 데이터를 정리한 것으로, 집계 시점에 따라 달라질 수 있습니다. 카드 이미지: <a href="https://snap.untapped.gg/" target="_blank" rel="noopener">Untapped.gg</a>
   376	</footer>
   377	<div class="toast" id="toast" role="status" aria-live="polite"></div>
   378	
   379	<script src="data.js"></script>
   380	<script>
   381	(function () {
   382	  const D = window.SNAP_DATA;
   383	  const C = D.cards;
   384	  const $ = (id) => document.getElementById(id);
   385	  const esc = (s) => String(s).replace(/[&<>"]/g, (c) => ({ "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;" }[c]));
   386	  const nm = (id) => (C[id] ? C[id].name : id);
   387	  const num = (n) => Number(n).toLocaleString("ko-KR");
   388	  const sgn = (n) => (n > 0 ? "+" : "") + n.toFixed(2);
   389	  const IMG = (id) => `https://snapjson.untapped.gg/art/render/framebreak/common/256/${encodeURIComponent(id)}.webp`;
   390	  const deckCode = (ids) => btoa(ids.map((id) => C[id].code).join(","));
   391	
   392	  /* theme */
   393	  const root = document.documentElement;
   394	  function applyTheme(t) { if (t) root.setAttribute("data-theme", t); else root.removeAttribute("data-theme"); }
   395	  try { applyTheme(localStorage.getItem("snap-theme")); } catch (e) {}
   396	  $("themeBtn").addEventListener("click", () => {
   397	    const dark = root.getAttribute("data-theme") === "dark" ||
   398	      (!root.getAttribute("data-theme") && matchMedia("(prefers-color-scheme: dark)").matches);
   399	    const next = dark ? "light" : "dark";
   400	    applyTheme(next);
   401	    try { localStorage.setItem("snap-theme", next); } catch (e) {}
   402	  });
   403	
   404	  /* 덱별 '내 기준 승률' 계산 */
   405	  const UNOWNED = new Set(D.unowned.map((u) => u.id));

hook: PostToolUse
exec
/bin/zsh -lc "sed -n '1,220p' index.html" in /Users/mac_al03241630/Project/marvelsnap
 succeeded in 0ms:
<!doctype html>
<html lang="ko">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>Marvel Snap 덱 노트</title>
<meta name="description" content="마블 스냅 메타 덱 30선과 내 컬렉션 기준 사용 가능 여부 — 개인 덱 빌딩 노트">
<link rel="stylesheet" href="https://cdn.jsdelivr.net/gh/orioncactus/pretendard@v1.3.9/dist/web/variable/pretendardvariable-dynamic-subset.min.css">
<style>
:root {
  --bg: #f6f6f9; --surface: #ffffff; --surface-2: #f0f0f5; --line: #e2e2ea;
  --text: #17171c; --text-2: #55556a; --text-3: #8a8a9e;
  --accent: #5b4bdb; --accent-soft: #ecebfd;
  --up: #12805c; --up-soft: #e3f5ee; --down: #c4314b; --down-soft: #fde8ec;
  --warn: #a35f00; --warn-soft: #fff1db;
  --tier-s: #b8860b; --tier-s-bg: #fff5d6; --tier-a: #7c3aed; --tier-a-bg: #f1e9ff;
  --tier-b: #1d6fd6; --tier-b-bg: #e5f0ff; --tier-c: #5f6472; --tier-c-bg: #eceef2;
  --tier-ut: #8a8a9e; --tier-ut-bg: transparent;
  --shadow: 0 1px 2px rgba(20,20,40,.06), 0 4px 16px rgba(20,20,40,.05);
}
@media (prefers-color-scheme: dark) {
  :root:not([data-theme="light"]) {
    --bg: #0f0f14; --surface: #191920; --surface-2: #22222b; --line: #2e2e39;
    --text: #ececf3; --text-2: #a9a9bd; --text-3: #75758a;
    --accent: #9d90ff; --accent-soft: #26233f;
    --up: #4cd6a0; --up-soft: #13302a; --down: #ff7b91; --down-soft: #3a1820;
    --warn: #ffb648; --warn-soft: #36270f;
    --tier-s: #ffcf4a; --tier-s-bg: #3a2f0c; --tier-a: #c4a5ff; --tier-a-bg: #2c2045;
    --tier-b: #7cb6ff; --tier-b-bg: #172a45; --tier-c: #b3b8c4; --tier-c-bg: #2a2d34;
    --tier-ut: #8f8fa6; --shadow: none;
  }
}
:root[data-theme="dark"] {
  --bg: #0f0f14; --surface: #191920; --surface-2: #22222b; --line: #2e2e39;
  --text: #ececf3; --text-2: #a9a9bd; --text-3: #75758a;
  --accent: #9d90ff; --accent-soft: #26233f;
  --up: #4cd6a0; --up-soft: #13302a; --down: #ff7b91; --down-soft: #3a1820;
  --warn: #ffb648; --warn-soft: #36270f;
  --tier-s: #ffcf4a; --tier-s-bg: #3a2f0c; --tier-a: #c4a5ff; --tier-a-bg: #2c2045;
  --tier-b: #7cb6ff; --tier-b-bg: #172a45; --tier-c: #b3b8c4; --tier-c-bg: #2a2d34;
  --tier-ut: #8f8fa6; --shadow: none;
}
* { box-sizing: border-box; }
html { -webkit-text-size-adjust: 100%; scroll-padding-top: 64px; }
body {
  margin: 0; background: var(--bg); color: var(--text);
  font-family: "Pretendard Variable", Pretendard, -apple-system, BlinkMacSystemFont, system-ui, sans-serif;
  font-size: 15px; line-height: 1.6; word-break: keep-all; overflow-wrap: anywhere;
}
a { color: var(--accent); }
.wrap { max-width: 1080px; margin: 0 auto; padding: 0 16px; }

/* nav */
nav.top {
  position: sticky; top: 0; z-index: 10; background: color-mix(in srgb, var(--bg) 88%, transparent);
  backdrop-filter: blur(10px); -webkit-backdrop-filter: blur(10px); border-bottom: 1px solid var(--line);
}
nav.top .wrap { display: flex; align-items: center; gap: 4px; height: 52px; overflow-x: auto; scrollbar-width: none; }
nav.top .wrap::-webkit-scrollbar { display: none; }
nav.top a { flex: none; color: var(--text-2); text-decoration: none; font-size: 14px; padding: 6px 10px; border-radius: 8px; }
nav.top a:hover { background: var(--surface-2); color: var(--text); }
nav.top .brand { font-weight: 700; color: var(--text); margin-right: 6px; }
#themeBtn { margin-left: auto; flex: none; border: 1px solid var(--line); background: var(--surface); color: var(--text-2); border-radius: 8px; padding: 5px 10px; font: inherit; font-size: 13px; cursor: pointer; }

/* hero */
header.hero { padding: 36px 0 12px; }
header.hero h1 { margin: 0 0 6px; font-size: 28px; letter-spacing: -0.02em; }
header.hero p.sub { margin: 0; color: var(--text-2); }
.stats { display: grid; grid-template-columns: repeat(4, 1fr); gap: 10px; margin: 20px 0 8px; }
.stat { background: var(--surface); border: 1px solid var(--line); border-radius: 12px; padding: 12px 14px; box-shadow: var(--shadow); }
.stat b { display: block; font-size: 24px; letter-spacing: -0.02em; font-variant-numeric: tabular-nums; }
.stat span { color: var(--text-2); font-size: 13px; }

section { padding: 28px 0 8px; }
section > h2 { font-size: 21px; margin: 0 0 4px; letter-spacing: -0.01em; }
section > p.lead { margin: 0 0 16px; color: var(--text-2); font-size: 14px; }
.panel { background: var(--surface); border: 1px solid var(--line); border-radius: 14px; padding: 16px 18px; box-shadow: var(--shadow); }
.trend { margin: 0; padding-left: 20px; }
.trend li { margin: 6px 0; }
.trend li::marker { color: var(--text-3); }

/* filters */
.filters { display: flex; flex-direction: column; gap: 10px; margin-bottom: 16px; }
.frow { display: flex; align-items: center; gap: 6px; flex-wrap: wrap; }
.frow .lbl { font-size: 13px; color: var(--text-3); width: 44px; flex: none; }
.chip-btn { border: 1px solid var(--line); background: var(--surface); color: var(--text-2); border-radius: 999px; padding: 5px 12px; font: inherit; font-size: 13px; cursor: pointer; min-height: 32px; }
.chip-btn[aria-pressed="true"] { background: var(--accent); border-color: var(--accent); color: #fff; }
:root[data-theme="dark"] .chip-btn[aria-pressed="true"] { color: #121218; }
@media (prefers-color-scheme: dark) { :root:not([data-theme="light"]) .chip-btn[aria-pressed="true"] { color: #121218; } }
.count-line { font-size: 13px; color: var(--text-3); margin: 0 0 10px; }

/* deck cards */
.decks { display: grid; grid-template-columns: 1fr; gap: 14px; }
@media (min-width: 980px) { .decks { grid-template-columns: 1fr 1fr; } }
.deck { background: var(--surface); border: 1px solid var(--line); border-radius: 14px; padding: 14px 16px 12px; box-shadow: var(--shadow); display: flex; flex-direction: column; gap: 10px; min-width: 0; }
.deck-head { display: flex; gap: 10px; align-items: flex-start; }
.rank { flex: none; font-size: 12px; font-weight: 700; color: var(--text-3); width: 22px; padding-top: 8px; text-align: right; font-variant-numeric: tabular-nums; }
.tier { flex: none; width: 34px; height: 34px; border-radius: 9px; display: grid; place-items: center; font-weight: 800; font-size: 15px; }
.tier.S { color: var(--tier-s); background: var(--tier-s-bg); }
.tier.A { color: var(--tier-a); background: var(--tier-a-bg); }
.tier.B { color: var(--tier-b); background: var(--tier-b-bg); }
.tier.C { color: var(--tier-c); background: var(--tier-c-bg); }
.tier.UT { color: var(--tier-ut); border: 1.5px dashed var(--tier-ut); font-size: 11px; }
.tier.REF { color: var(--text-3); background: var(--surface-2); font-size: 11px; }
.deck-title { flex: 1; min-width: 0; }
.deck-title h3 { margin: 0; font-size: 16px; line-height: 1.35; letter-spacing: -0.01em; }
.deck-title .no { color: var(--text-3); font-weight: 600; margin-right: 4px; font-variant-numeric: tabular-nums; }
.tags { display: flex; flex-wrap: wrap; gap: 5px; margin-top: 5px; }
.tag { font-size: 12px; padding: 1px 8px; border-radius: 6px; background: var(--surface-2); color: var(--text-2); white-space: nowrap; }
.tag.up { background: var(--up-soft); color: var(--up); }
.tag.down { background: var(--down-soft); color: var(--down); }
.own { font-size: 12.5px; font-weight: 600; padding: 3px 9px; border-radius: 7px; white-space: nowrap; flex: none; }
.own.ok { background: var(--up-soft); color: var(--up); }
.own.pred { background: var(--warn-soft); color: var(--warn); }
.own.none { background: var(--down-soft); color: var(--down); }
.build { border-top: 1px solid var(--line); padding-top: 10px; display: flex; flex-direction: column; gap: 8px; }
.build:first-of-type { border-top: none; padding-top: 0; }
.build-label { font-size: 12.5px; font-weight: 600; color: var(--text-2); margin: 0; }
.wr-line { display: flex; align-items: baseline; gap: 8px; flex-wrap: wrap; }
.wr-big { font-size: 22px; font-weight: 800; letter-spacing: -0.02em; font-variant-numeric: tabular-nums; }
.wr-big.dim { font-size: 15px; font-weight: 700; color: var(--text-3); }
.wr-meta { font-size: 12.5px; color: var(--text-2); font-variant-numeric: tabular-nums; }
.grid12 { display: grid; grid-template-columns: repeat(6, minmax(0, 1fr)); gap: 4px 2px; }
@media (max-width: 520px) { .grid12 { grid-template-columns: repeat(4, minmax(0, 1fr)); } }
.grid12[hidden] { display: none; }
.cimg { margin: 0; position: relative; min-width: 0; text-align: center; }
.cimg img { width: 100%; height: auto; aspect-ratio: 1 / 1; display: block; object-fit: contain; }
.cimg figcaption { font-size: 10.5px; line-height: 1.25; color: var(--text-2); margin-top: -2px; display: -webkit-box; -webkit-line-clamp: 2; -webkit-box-orient: vertical; overflow: hidden; word-break: break-word; }
.cimg .ph { display: none; }
.cimg.noimg img { display: none; }
.cimg.noimg .ph { display: grid; place-items: center; aspect-ratio: 1 / 1; border-radius: 10px; background: var(--surface-2); font-weight: 800; color: var(--text-3); font-size: 18px; }
.cimg.miss img { filter: grayscale(1); opacity: .38; }
.cimg.miss figcaption { color: var(--down); font-weight: 600; }
.cimg.miss::after { content: "✕"; position: absolute; top: 4%; right: 6%; width: 20px; height: 20px; border-radius: 50%; background: var(--down); color: #fff; font-size: 11px; font-weight: 800; display: grid; place-items: center; }
.cimg.added figcaption { color: var(--up); font-weight: 700; }
.cimg.added::after { content: "+"; position: absolute; top: 4%; right: 6%; width: 20px; height: 20px; border-radius: 50%; background: var(--up); color: #fff; font-size: 13px; font-weight: 800; display: grid; place-items: center; }
.pred { border-radius: 10px; padding: 9px 11px; font-size: 13px; }
.pred.ok { background: var(--warn-soft); }
.pred.no { background: var(--surface-2); color: var(--text-2); }
.pred .wr-big { color: var(--warn); font-size: 20px; }
.pred-lbl { font-size: 12.5px; font-weight: 700; color: var(--warn); }
.swaps { display: flex; flex-wrap: wrap; gap: 4px 10px; margin-top: 4px; }
.swap { font-size: 12.5px; white-space: nowrap; }
.swap s { color: var(--down); }
.swap b { color: var(--up); }
.btns { display: flex; flex-wrap: wrap; gap: 6px; align-items: center; }
.btn { border: 1px solid var(--line); background: var(--surface); color: var(--text); font: inherit; font-size: 13px; font-weight: 600; cursor: pointer; padding: 6px 12px; border-radius: 8px; min-height: 34px; }
.btn:hover { background: var(--surface-2); }
.btn.primary { background: var(--accent); border-color: var(--accent); color: #fff; }
.btn.primary:hover { filter: brightness(1.08); }
:root[data-theme="dark"] .btn.primary { color: #121218; }
@media (prefers-color-scheme: dark) { :root:not([data-theme="light"]) .btn.primary { color: #121218; } }
.btn.ghost { border-color: transparent; background: none; color: var(--text-3); font-weight: 500; }
.btn.ghost:hover { color: var(--text); background: var(--surface-2); }
.dropped { font-size: 12px; color: var(--text-3); margin: 0; }
details.ev { background: none; border: none; padding: 0; margin: 0; }
details.ev > summary { padding: 2px 0; font-size: 12.5px; font-weight: 500; color: var(--text-3); }
details.ev > div { padding: 2px 0 0; font-size: 12.5px; color: var(--text-2); }
details.ev ul { margin: 2px 0; }
.excluded { margin-top: 14px; font-size: 13px; color: var(--text-3); }
.excluded b { color: var(--text-2); font-weight: 600; }
.card { font-size: 13px; padding: 3px 9px; border-radius: 7px; background: var(--surface-2); border: 1px solid transparent; }
.cards { display: flex; flex-wrap: wrap; gap: 5px; }
.empty { color: var(--text-3); padding: 24px; text-align: center; border: 1px dashed var(--line); border-radius: 14px; }

/* tables */
.tbl-wrap { overflow-x: auto; border: 1px solid var(--line); border-radius: 12px; background: var(--surface); }
table { border-collapse: collapse; width: 100%; font-size: 14px; }
th, td { text-align: left; padding: 9px 12px; border-bottom: 1px solid var(--line); vertical-align: top; }
th { font-size: 12.5px; color: var(--text-3); font-weight: 600; background: var(--surface-2); white-space: nowrap; }
tr:last-child td { border-bottom: none; }
td.num { font-variant-numeric: tabular-nums; white-space: nowrap; }
.nerf { color: var(--down); font-weight: 600; }
.buff { color: var(--up); font-weight: 600; }
.grid2 { display: grid; grid-template-columns: 1fr; gap: 14px; }
@media (min-width: 900px) { .grid2 { grid-template-columns: 1fr 1fr; } }
h3.sub { font-size: 15px; margin: 18px 0 8px; }
details { background: var(--surface); border: 1px solid var(--line); border-radius: 12px; padding: 0 16px; margin-bottom: 10px; }
details > summary { cursor: pointer; padding: 13px 0; font-weight: 600; list-style: none; }
details > summary::-webkit-details-marker { display: none; }
details > summary::before { content: "▸ "; color: var(--text-3); }
details[open] > summary::before { content: "▾ "; }
details > div { padding: 0 0 14px; font-size: 14px; }
details ul { padding-left: 18px; margin: 6px 0; }
.muted { color: var(--text-3); font-size: 13px; }
footer { padding: 32px 0 48px; color: var(--text-3); font-size: 13px; }
.toast { position: fixed; left: 50%; bottom: 24px; transform: translateX(-50%) translateY(20px); background: var(--text); color: var(--bg); padding: 8px 14px; border-radius: 10px; font-size: 13px; opacity: 0; transition: .2s; pointer-events: none; }
.toast.show { opacity: 1; transform: translateX(-50%) translateY(0); }
@media (max-width: 640px) {
  header.hero h1 { font-size: 24px; }
  .stats { grid-template-columns: repeat(2, 1fr); }
  .frow .lbl { width: 100%; }
}
</style>
</head>
<body>
<nav class="top" aria-label="섹션">
  <div class="wrap">
    <a class="brand" href="#top">덱 노트</a>
    <a href="#decks">덱 목록</a>
    <a href="#collection">내 컬렉션</a>
    <a href="#season">시즌·패치</a>
    <a href="#basics">기본 규칙</a>
    <a href="#sources">출처·주의</a>
    <button id="themeBtn" type="button" aria-label="테마 전환">테마</button>
  </div>
</nav>

<main class="wrap" id="top">
  <header class="hero">
    <h1>Marvel Snap 덱 노트</h1>
    <p class="sub" id="heroSub">메타 기준일 — · Knights of Avalon 시즌 · 11/12 OTA 직후</p>
    <div class="stats" id="stats"></div>
  </header>

  <section id="trend" aria-labelledby="trend-h">
    <h2 id="trend-h">이번 주 메타 흐름</h2>
    <div class="panel">
      <ul class="trend">
        <li><b>Anti-Polar Magneto × Arthur Pendragon (4코스트 치트)</b> 계열이 시즌 최대 화두. Untapped 인기 1위 아키타입, SnapVault S티어에도 2개. Lancelot · Mordred · Captain Britain 등 시즌 신규 카드가 그대로 들어감.</li>

hook: PostToolUse
hook: PostToolUse Completed
exec
/bin/zsh -lc "nl -ba notes/meta-2026-11-14.md | sed -n '100,340p'" in /Users/mac_al03241630/Project/marvelsnap
 succeeded in 0ms:
   100	  1. 같은 계열 = 원본과 12장 중 8장 이상 겹치는 랭크 7일 리스트
   101	  2. 같은 계열에서 그 카드 **없이** 플레이된 판이 100판 미만이면 엔진 카드로 보고 **예측 불가**
   102	  3. 대체 카드 = 같은 계열에서 그 카드를 뺀 리스트에 **실제로 가장 많이 들어간 보유 카드** (50판 이상)
   103	  4. 카드별 기여도 = 원본과 6장 이상 겹치는 리스트로 가중 릿지 회귀 (겹침이 많을수록 가중치 큼, λ=200판)
   104	  5. 예측 = 원본 실제 승률 + Σ(들어가는 카드 기여 − 빠지는 카드 기여). **원본보다 높게는 잡지 않음** (보수적)
   105	  - 한계: 카드 간 시너지를 따로 모델링하지 않음. 계열 데이터가 얇으면 기여도가 0 쪽으로 줄어들어 하락 폭이 작게 나올 수 있음
   106	- 덱 정렬 = 내가 기대할 수 있는 승률 순 (바로 사용 가능 빌드는 실제 승률, 미보유 빌드는 예측 승률, 예측 불가는 맨 뒤)
   107	- 덱 코드 = 카드별 게임 코드(`IrnPtrtB` 형식)를 쉼표로 이어 base64. SnapVault·MSZ 덱 코드 15개를 풀어서 같은 형식임을 확인
   108	
   109	---
   110	
   111	## 4. 메타 흐름 요약
   112	
   113	1. **Anti-Polar Magneto × Arthur Pendragon (4코스트 치트) 계열이 시즌 최대 화두** — UT 기준 인기 1위 아키타입(Arthur 7.4~7.8%). SV S티어에도 2개. Lancelot / Mordred / Captain Britain 등 시즌 신규 카드가 그대로 들어가는 구조.
   114	2. **Zombie Galacti / Shuri / Wong** — SV에서 가장 큰 표본(2,476판)으로 60% · +0.71 큐브. 근거가 가장 탄탄한 고성능 덱.
   115	3. **Stardust / Gambit Horseman of Death 생성·테크 덱** — Sasquatch형이 SV S. snap.fan 카드 티어 유일한 S가 Gambit Horseman of Death(단, SC 기반). 피니셔(Sasquatch / Kluh / Thanos FF)만 바꾼 변형이 다수. Mobius 너프 영향권.
   116	4. **Zombie Horde(뱀파이어·좀비 Skill 덱)** — **사용량이 많고 성적이 양호** (SC 5,526판 59.1%). 11/12에 Zombie Scarlet Witch 너프(-1 파워). Merlin of Avalon 채용형도 등장.
   117	5. **전통 강자** — High Evo, Fantomex는 SV + UT 대표본으로 확인. Patriot은 Onslaught 버프 수혜. Destroy / Surfer / Thor / Galactus / Deacon 등은 UT 단독 근거.
   118	6. **많이 쓰이지만 승률은 평범** — Sandstorm Patriot (SC 최다 사용 7,093판, 승률 51%).
   119	
   120	### 계열별 색인 (변형을 독립 아키타입으로 과대평가하지 않도록)
   121	| 계열 | 덱 번호 |
   122	|---|---|
   123	| Anti-Polar Magneto / Arthur | #2, #3, #4, #19, #20, #21, #23 |
   124	| Stardust / Gambit HoD | #5, #9, #13 (+ #16 Merlin 생성 덱과 카드 다수 공유) |
   125	| Zombie Horde | #6, #10, #11, #15 |
   126	| Zombie Galacti | #1, #12 |
   127	
   128	### snap.fan 카드 티어 상위 (11/13, SC 데이터 기반)
   129	- **S**: Gambit Horseman of Death
   130	- **A**: Spider-Man Brand New Day, Venus, Captain Britain, Deafening Chord, Scarlet Witch Queen of Chaos, Surge
   131	
   132	---
   133	
   134	## 5. 고승률 덱 30선
   135	
   136	### 티어 산정 규칙 (잠정 편집자 평가)
   137	1. **기준점 = SnapVault 티어** (신뢰구간 하한 기반이라 표본 크기가 반영됨)
   138	2. SV 티어가 없는 덱(미등재·Rising): **SC만 있으면** 승률 58% 이상 B / 미만 C
   139	3. **다른 출처에서 1,000판 이상 표본으로 확인되면 한 단계 상향** (최대 S)
   140	4. **UT 단독 근거 덱은 티어를 매기지 않고** 별도 그룹으로 분리 (UT 승률은 다른 출처와 비교 불가)
   141	5. OTA 영향은 티어에 반영하지 않고 표시만: ⬆ 버프 카드 포함 · ⬇ 너프 카드 포함
   142	
   143	표기: SV = SnapVault(7일) / SC = SnapComplete(이번 주) / UT = Untapped · 승률 / 판수 / 평균 큐브
   144	
   145	### S 티어
   146	
   147	**1. Zombie Galacti / Shuri / Wong** — 계열: Zombie Galacti
   148	- 근거: SV **S** 60.0% / **2,476판** / **+0.71**
   149	- Deafening Chord, Majestic Wingbeat, Echo, Spider-Man Brand New Day, Adam Warlock, Surge, Magik, Superior Spider-Man, Mister Fantastic First Steps, Wong, Shuri, Zombie Galacti
   150	
   151	**2. Anti-Polar Magneto / Arthur — Lancelot · Galacta형** ⬆(Captain Britain) — 계열: APM
   152	- 근거: SV A 62.3% / 260판 / **+0.81** → SC 58.9% / 1,941판으로 확인되어 상향
   153	- Zabu, Surge, Captain Britain, Caliban Horseman of Pestilence, Mordred, Arthur Pendragon, Wolverine Horseman of War, Captain Marvel, Galacta, Lancelot, Iron Lad, Anti-Polar Magneto
   154	
   155	**3. Anti-Polar Magneto / Doctor Doom — Rogue Scion · Mordred형** ⬆(Captain Britain) — 계열: APM
   156	- 근거: SV **S** 62.8% / 368판 / +0.65
   157	- Red Wolf Fractured Frontier, Captain Britain, Drax Avatar of Life, Caliban Horseman of Pestilence, Mordred, Arthur Pendragon, En Sabah Nur, Doctor Doom 2099, Iron Lad, Rogue Scion of Division, Doctor Doom, Anti-Polar Magneto
   158	
   159	**4. Fin Fang Foom / Gorr / Dragon Lord — Domino형** — 계열: APM
   160	- 근거: SV **S** 67.6% / 306판 / +0.66 (SC 59.5% / 370판 / +0.47)
   161	- Domino, Jane Foster Fractured Frontier, Caliban Horseman of Pestilence, Jubilee, Arthur Pendragon, En Sabah Nur, Captain Marvel, Iron Lad, Dragon Lord, Gorr the God Butcher, Anti-Polar Magneto, Fin Fang Foom
   162	
   163	**5. Stardust / Gambit HoD — Sasquatch형** ⬇(Mobius) — 계열: Stardust
   164	- 근거: SV **S** 65.4% / 306판 / +0.64
   165	- Deafening Chord, King Eitri, Hydra Bob, Iron Patriot, Shadowlands Daredevil, Valentina, Mobius M. Mobius, Scarlet Witch Queen of Chaos, Shadow King, Gambit Horseman of Death, Stardust, Sasquatch
   166	
   167	### A 티어
   168	
   169	**6. Zombie Horde — Zombie Blade형** ⬇(Zombie SW) — 계열: Horde
   170	- 근거: SV B 58.9% / 1,156판 / +0.41 → SC 59.1% / 5,526판으로 확인되어 상향 (UT 아키타입 69.3%)
   171	- Majestic Wingbeat, The Hunger, Nicholas Scratch, Vampire Killmonger, Zombie Mister Fantastic, Joaquin Torres Falcon II, Zombie Blade, Venus, Scarlet Witch Queen of Chaos, Zombie Scarlet Witch, Zombie Giant-Man, Sasquatch
   172	- 플랜: Horde 누적 + Scarlet Witch QoC / Vampire Killmonger로 Skill 생성 → Zombie Giant-Man · Sasquatch 페이오프
   173	
   174	**7. High Evolutionary (Hulk / Abomination)**
   175	- 근거: SV B 59.8% / 396판 / +0.38 → UT 대표 덱 73.4% / 2,200판으로 확인되어 상향
   176	- Sunspot, Misty Knight, Armor, Scorpion, Shocker, Cyclops, Shang-Chi, High Evolutionary, The Thing, Enchantress, Abomination, Hulk
   177	- 플랜: High Evolutionary가 무능력 카드의 숨은 능력을 해금
   178	
   179	**8. Fantomex / Zombie Captain Marvel / Shadow King** ⬇(Mobius)
   180	- 근거: SV B 56.9% / 1,874판 / +0.52 → UT 67.3% / 1,500판(UT 티어 A)으로 확인되어 상향
   181	- The Hood, Blade, Wild Child, Bucky Barnes, Carnage, Marrow, Mobius M. Mobius, Gambit, Killmonger, Shadow King, Zombie Captain Marvel, Fantomex
   182	
   183	**9. Stardust / Gambit HoD — Kluh형** ⬇(Mobius) — 계열: Stardust
   184	- 근거: SV A 59.7% / 1,105판 / +0.49 (Maria Hill 빌드) · SV A 59.4% / 1,189판 / +0.34 (Deafening Chord 빌드)
   185	- King Eitri, **Maria Hill 또는 Deafening Chord**, Hydra Bob, Iron Patriot, Shadowlands Daredevil, Valentina, Mobius M. Mobius, Scarlet Witch Queen of Chaos, Shadow King, Gambit Horseman of Death, Stardust, Kluh
   186	
   187	**10. Zombie Horde — Werewolf By Night / Web Sling형** ⬇(Zombie SW) — 계열: Horde
   188	- 근거: SV A 66.3% / 104판 / +0.63 (소표본)
   189	- Majestic Wingbeat, The Hunger, Web Sling, Nicholas Scratch, Vampire Killmonger, Joaquin Torres Falcon II, Venus, Scarlet Witch Queen of Chaos, Werewolf By Night, Zombie Scarlet Witch, Zombie Giant-Man, Sasquatch
   190	- 참고: UT 대표 덱(69.1% / 860판)은 Web Sling 대신 Zombie Blade를 쓰는 다른 리스트
   191	
   192	**11. Zombie Horde — Luke Cage형** ⬇(Zombie SW) — 계열: Horde
   193	- 근거: SV A 65.8% / 114판 / **+0.93** (소표본)
   194	- Majestic Wingbeat, The Hunger, Nicholas Scratch, Luke Cage, Vampire Killmonger, Zombie Mister Fantastic, Joaquin Torres Falcon II, Venus, Scarlet Witch Queen of Chaos, Zombie Scarlet Witch, Zombie Giant-Man, Sasquatch
   195	
   196	### B 티어
   197	
   198	**12. Zombie Galacti / Arthur / Stick** — 계열: Zombie Galacti
   199	- 근거: SV B 60.2% / 377판 / +0.51
   200	- Majestic Wingbeat, America Chavez, Adam Warlock, Surge, Doctor Octopus Fractured Frontier, Magik, Maverick, Superior Spider-Man, Jubilee Silver Surfer, Stick, Arthur Pendragon, Zombie Galacti
   201	
   202	**13. Stardust / Gambit HoD — Thanos Fractured Frontier형** ⬇(Mobius) — 계열: Stardust
   203	- 근거: SC 59.2% / 779판 (SV Rising 68.8% / 48판)
   204	- Deafening Chord, King Eitri, Maria Hill, Iron Patriot, Shadowlands Daredevil, Valentina, Mobius M. Mobius, Scarlet Witch Queen of Chaos, Shadow King, Gambit Horseman of Death, Stardust, Thanos Fractured Frontier
   205	
   206	**14. Spider-Ham**
   207	- 근거: SC 59.3% / 1,357판
   208	- Spider-Ham, America Chavez, Nico Minoru, Spider-Man Brand New Day, Nightcrawler, Adam Warlock, Marvel Boy, Venus, Jane Foster Fractured Frontier, Elsa Bloodstone, Stardust, Thanos Fractured Frontier
   209	
   210	**15. Zombie Horde — Merlin of Avalon형** ⬇(Zombie SW) — 계열: Horde
   211	- 근거: SC 58.9% / 1,644판
   212	- Majestic Wingbeat, The Hunger, Merlin of Avalon, Nicholas Scratch, Vampire Killmonger, Joaquin Torres Falcon II, Zombie Blade, Venus, Scarlet Witch Queen of Chaos, Zombie Scarlet Witch, Zombie Giant-Man, Sasquatch
   213	
   214	**16. Merlin of Avalon 생성 카드 덱**
   215	- 근거: SC 60.4% / 253판 / +0.51 (소표본)
   216	- Merlin of Avalon, Clea, Nicholas Scratch, Vampire Killmonger, Cobra, Shadowlands Daredevil, Valentina, Marvel Boy, Scarlet Witch Queen of Chaos, Gambit Horseman of Death, Stardust, Sasquatch
   217	
   218	**17. Kitty Pryde**
   219	- 근거: SC 58.9% / 285판 (소표본)
   220	- Kitty Pryde, America Chavez, Merlin of Avalon, Maria Hill, Nightcrawler, Vampire Killmonger, Angela, The Collector, Bishop, Scarlet Witch Queen of Chaos, Shang-Chi, Thanos Fractured Frontier
   221	
   222	### C 티어
   223	
   224	**18. Patriot — Onslaught / Ultron / Blue Marvel** ⬆(Onslaught)
   225	- 근거: SV C 60.8% / 222판 / +0.58 (UT 68.0% / 800판 — 1,000판 미만이라 상향 안 함)
   226	- Ant Man, Squirrel Girl, Misty Knight, Dazzler, Armor, Mystique, Patriot, Cosmo, Ka-Zar, Blue Marvel, Ultron, Onslaught
   227	
   228	**19. Anti-Polar Magneto / Jubilee형 — Lancelot 또는 Captain Marvel** ⬆(Captain Britain) — 계열: APM
   229	- 근거: SV C 57.4% / 1,023판 / +0.33 (Lancelot 빌드) · SV C 58.1% / 651판 / +0.60 (Captain Marvel 빌드) — 두 빌드는 11장 동일
   230	- Zabu, Surge, Captain Britain, Mordred, Jubilee, Jubilee Silver Surfer, Arthur Pendragon, Wolverine Horseman of War, En Sabah Nur, **Lancelot 또는 Captain Marvel**, Iron Lad, Anti-Polar Magneto
   231	
   232	**20. Fin Fang Foom / Gorr — Zabu형** ⬆(Captain Britain) — 계열: APM
   233	- 근거: SV C 56.7% / 1,506판 / +0.42
   234	- Zabu, Captain Britain, Mordred, Jubilee, Arthur Pendragon, En Sabah Nur, Captain Marvel, Iron Lad, Dragon Lord, Gorr the God Butcher, Anti-Polar Magneto, Fin Fang Foom
   235	
   236	**21. Zabu / Spider-Man BND / Superior Iron Man** ⬆(Captain Britain) — 계열: APM 주변
   237	- 근거: SC 56% / 5,437판 (사용량 3위)
   238	- Zabu, Spider-Man Brand New Day, Surge, Jeff the Baby Dolphin!?, Captain Britain, Mister Fantastic First Steps, Jubilee Silver Surfer, Arthur Pendragon, Wolverine Horseman of War, Lancelot, Iron Lad, Superior Iron Man
   239	
   240	### 티어 미부여 — Untapped 단독 근거 (보수적 출처에서 교차 확인 안 됨)
   241	UT 덱 승률 순. `(30일)` = 아키타입 페이지(최근 30일, 랭크 10~79, Pool 3+), `(필터 미확인)` = 덱 목록 페이지.
   242	
   243	**22. Vampire Deacon Frost** — UT 69.0% / 580판 (30일), UT 티어 C
   244	- Silver Sable, Vampire Killmonger, Zombie Blade, Cassandra Nova, Scarlet Witch Queen of Chaos, Dragon of the Moon, En Sabah Nur, Laufey, Vampire Deacon Frost, Stryfe, Vampire Enchantress, Anti-Polar Magneto
   245	
   246	**23. Arthur / Doctor Doom — Moondragon · Astral Projection형** — UT 65.6% / 940판 (30일), 계열: APM
   247	- Moondragon, Luke Cage, Astral Projection, Drax Avatar of Life, Invisible Woman First Steps, Caliban Horseman of Pestilence, Arthur Pendragon, Captain Marvel, Doctor Doom 2099, Iron Lad, Doctor Doom, Anti-Polar Magneto
   248	
   249	**24. Thor (Odin / Jane Foster)** — UT 65.3% / 260판 (필터 미확인)
   250	- Wasp, Iceman, King Eitri, Surge, Lockjaw, Phastos, Thor, Beta Ray Bill, Thanos Fractured Frontier, Jane Foster Mighty Thor, Gorr the God Butcher, Odin
   251	
   252	**25. Destroy (Death / Knull)** — UT 64.7% / 1,300판 (30일), 아키타입 인기 6.3%
   253	- Deadpool, X-23, Nico Minoru, Carnage, Hulkbuster, Wolverine, Killmonger, Venom, Deathlok, Arnim Zola, Knull, Death
   254	
   255	**26. Silver Surfer** — UT 63.7% / 740판 (30일)
   256	- Luke Cage, Ironheart, Mystique, Brood, Magik, Silver Surfer, Hazmat, Rogue, Wong, Absorbing Man, Sera, Odin
   257	
   258	**27. Galactus (Destroyer)** — UT 60.7% / 700판 (30일), UT 티어 D
   259	- Nebula, Selene, Daredevil, Green Goblin, Magik, Electro, Wave, Negasonic Teenage Warhead, Hobgoblin, Spider-Woman, Galactus, Destroyer
   260	- (변형, SV Rising 71.7% / 60판 / +1.42) Selene, Daredevil, Wolverine, Green Goblin, Electro, Wave, Hobgoblin, Knull, Galactus, Alioth, Destroyer, Death
   261	
   262	**28. Living Tribunal** ⬆(Onslaught) — UT 60.5% / 210판 (필터 미확인)
   263	- Howard the Duck, Ravonna Renslayer, Mystique, Magik, Wave, Jubilee, Super-Skrull, Iron Lad, Iron Man, Sera, Onslaught, The Living Tribunal
   264	
   265	**29. Mister Negative** — UT 59.9% / 200판 (필터 미확인)
   266	- Psylocke, Ravonna Renslayer, Cassandra Nova, Mystique, Magik, Mister Negative, Shang-Chi, Iron Man, Jane Foster Mighty Thor, Arnim Zola, Knull, Gorr the God Butcher
   267	
   268	**30. Discard (Apocalypse / Dracula)** — UT 57.1% / 230판 (필터 미확인), 아키타입 64.8%
   269	- Blade, Swarm, Morbius, The Collector, Wolverine, Colleen Wing, Gambit, Moon Knight, Lady Sif, Dracula, M.O.D.O.K., Apocalypse
   270	
   271	### 참고 (표본 부족 / 인기만 높음)
   272	- **Sandstorm Patriot** — SC 최다 사용 7,093판이지만 51% / UT 62.9% / 250판: Sandstorm, Zombie Mister Fantastic, H.E.R.B.I.E., Rhino, Patriot, Prodigy, Shadow King, Luna Snow, Debrii, Selene Horseman of Famine, Ozymandias, Mockingbird
   273	- **Fantomex / Omega Sentinel** — SV Rising 65.8% / 73판: Blade, Fastball Special, Kid Omega, Wild Child, Marrow, Gambit, Jocasta, Air-Walker, Prodigy, Shadow King, Omega Sentinel, Fantomex
   274	- **Created Cards (Quinjet / Mother Askani)** ⬆(Captain Britain) — UT 54.5% / 560판: Quinjet, Zabu, Surge, Psylocke, Victoria Hand, Captain Britain, Valentina, Bastion, Arthur Pendragon, Mother Askani, Moon Girl, Moonstone
   275	- **Quicksilver (Conquest 1위)** — SC Conquest 65% / 16,018판(집계 기간 미표기): Quicksilver, Domino, Jane Foster Fractured Frontier, Speed, Caliban Horseman of Pestilence, Jubilee, En Sabah Nur, Karen Page, Captain Marvel, Rogue Scion of Division, Thanos Fractured Frontier, Anti-Polar Magneto
   276	- **Small On Reveals (Merlin by Night)** — MSZ 11/8 Tier 1 (63% / 큐브 0.9, OTA 전) · Coccia #208 6위: Majestic Wingbeat, Iceman, Merlin of Avalon, Nicholas Scratch, Merlin, Vampire Killmonger, Joaquin Torres Falcon II, Venus, Scarlet Witch Queen of Chaos, Werewolf By Night, Shou-Lao the Undying, Sasquatch
   277	- **Created Disruption (Techno-Organic Virus)** — MSZ 11/8 Tier 1 (OTA 전): Cable, Hydra Bob, Iceman, Iron Patriot, Martyr, Mobius M. Mobius, Nico Minoru, Quinjet, Shadow King, Stardust, Techno-Organic Virus, Thanos Fractured Frontier
   278	- **Curved Wiccan (Thanos Kluh)** ⬇(Mobius) — MSZ 11/8 Tier 2 (59% / 큐브 0.6, OTA 전) · Coccia #208 4위: Quicksilver, Domino, Mobius M. Mobius, Rogue, Speed, Shadow King, Mister Fantastic First Steps, Stardust, Wiccan, Thanos Fractured Frontier, Kluh, Vampire Enchantress
   279	
   280	---
   281	
   282	## 6. 앞으로 볼 것
   283	- 11/17 Elder Dragon of the Moon, 11/19 Knight's Vow, 11/24 Sir Percy Black Knight 출시 → 메타 변동
   284	- 12/3 OTA, 12/15 패치
   285	- OTA가 반영된 다음 주 데이터로 Zombie Horde · Stardust · Fantomex(너프 카드 포함) 계열과 APM · Patriot(버프 카드 포함) 계열 변화 재확인
   286	
   287	## 7. 검증 이력
   288	- 덱 리스트 전부 12장 · 중복 없음 (스크립트 검증)
   289	- Codex 리뷰(2026-11-14): 리스트·OTA 화살표 검증 통과, SV #4·#5 / SC #14·Sandstorm 수치 웹 재확인 일치. 지적 사항(티어 규칙 불명확, 규칙 설명 누락, 주의문 단정) 반영 → v2
   290	- v3 (2026-11-14 저녁): SnapVault 랭크 7일 수치 결합, 100판 미만 제외(#10, 13, 16, 17, 25, 27, 30 / 참고 Fantomex·Omega Sentinel, Created Cards), 예측 승률 추가, 추가 출처 조사 반영(MSZ 티어표·SC OTA 결과, 참고 덱 3개 추가). 30덱 리스트 중 랭크 7일 12장 완전 일치가 없는 건 #16·#17뿐
   291	- 교차 확인(MSZ 11/8 · Coccia #208, OTA 전): #6 Horde MSZ Tier 1 1위 / #9 Kluh MSZ Tier 1 / #4 Domino형 MSZ Tier 1(큐브 1.05, Captain Marvel 대신 Baron Zemo) / #22·#24·#28 MSZ와 12장 동일 / #1 Zombie Galacti는 MSZ·Coccia 목록에 없음 / #3 APM Doom 유사 계열은 MSZ Tier 2 / #7 High Evo는 MSZ 빌드와 7장만 겹침

hook: PostToolUse
hook: PostToolUse Completed
hook: PostToolUse Completed
exec
/bin/zsh -lc 'git diff -- tools/build_data.py index.html' in /Users/mac_al03241630/Project/marvelsnap
 succeeded in 0ms:
diff --git a/index.html b/index.html
index 4abeeb3..a4c251f 100644
--- a/index.html
+++ b/index.html
@@ -90,10 +90,11 @@ section > p.lead { margin: 0 0 16px; color: var(--text-2); font-size: 14px; }
 .count-line { font-size: 13px; color: var(--text-3); margin: 0 0 10px; }
 
 /* deck cards */
-.decks { display: grid; grid-template-columns: 1fr; gap: 12px; }
-@media (min-width: 900px) { .decks { grid-template-columns: 1fr 1fr; } }
-.deck { background: var(--surface); border: 1px solid var(--line); border-radius: 14px; padding: 14px 16px 12px; box-shadow: var(--shadow); display: flex; flex-direction: column; gap: 8px; }
+.decks { display: grid; grid-template-columns: 1fr; gap: 14px; }
+@media (min-width: 980px) { .decks { grid-template-columns: 1fr 1fr; } }
+.deck { background: var(--surface); border: 1px solid var(--line); border-radius: 14px; padding: 14px 16px 12px; box-shadow: var(--shadow); display: flex; flex-direction: column; gap: 10px; min-width: 0; }
 .deck-head { display: flex; gap: 10px; align-items: flex-start; }
+.rank { flex: none; font-size: 12px; font-weight: 700; color: var(--text-3); width: 22px; padding-top: 8px; text-align: right; font-variant-numeric: tabular-nums; }
 .tier { flex: none; width: 34px; height: 34px; border-radius: 9px; display: grid; place-items: center; font-weight: 800; font-size: 15px; }
 .tier.S { color: var(--tier-s); background: var(--tier-s-bg); }
 .tier.A { color: var(--tier-a); background: var(--tier-a-bg); }
@@ -110,20 +111,56 @@ section > p.lead { margin: 0 0 16px; color: var(--text-2); font-size: 14px; }
 .tag.down { background: var(--down-soft); color: var(--down); }
 .own { font-size: 12.5px; font-weight: 600; padding: 3px 9px; border-radius: 7px; white-space: nowrap; flex: none; }
 .own.ok { background: var(--up-soft); color: var(--up); }
-.own.one { background: var(--warn-soft); color: var(--warn); }
-.own.many { background: var(--down-soft); color: var(--down); }
-.ev { font-size: 13px; color: var(--text-2); margin: 0; font-variant-numeric: tabular-nums; }
-.list-label { font-size: 12px; color: var(--text-3); margin: 2px 0 -2px; }
-.cards { display: flex; flex-wrap: wrap; gap: 5px; }
+.own.pred { background: var(--warn-soft); color: var(--warn); }
+.own.none { background: var(--down-soft); color: var(--down); }
+.build { border-top: 1px solid var(--line); padding-top: 10px; display: flex; flex-direction: column; gap: 8px; }
+.build:first-of-type { border-top: none; padding-top: 0; }
+.build-label { font-size: 12.5px; font-weight: 600; color: var(--text-2); margin: 0; }
+.wr-line { display: flex; align-items: baseline; gap: 8px; flex-wrap: wrap; }
+.wr-big { font-size: 22px; font-weight: 800; letter-spacing: -0.02em; font-variant-numeric: tabular-nums; }
+.wr-big.dim { font-size: 15px; font-weight: 700; color: var(--text-3); }
+.wr-meta { font-size: 12.5px; color: var(--text-2); font-variant-numeric: tabular-nums; }
+.grid12 { display: grid; grid-template-columns: repeat(6, minmax(0, 1fr)); gap: 4px 2px; }
+@media (max-width: 520px) { .grid12 { grid-template-columns: repeat(4, minmax(0, 1fr)); } }
+.grid12[hidden] { display: none; }
+.cimg { margin: 0; position: relative; min-width: 0; text-align: center; }
+.cimg img { width: 100%; height: auto; aspect-ratio: 1 / 1; display: block; object-fit: contain; }
+.cimg figcaption { font-size: 10.5px; line-height: 1.25; color: var(--text-2); margin-top: -2px; display: -webkit-box; -webkit-line-clamp: 2; -webkit-box-orient: vertical; overflow: hidden; word-break: break-word; }
+.cimg .ph { display: none; }
+.cimg.noimg img { display: none; }
+.cimg.noimg .ph { display: grid; place-items: center; aspect-ratio: 1 / 1; border-radius: 10px; background: var(--surface-2); font-weight: 800; color: var(--text-3); font-size: 18px; }
+.cimg.miss img { filter: grayscale(1); opacity: .38; }
+.cimg.miss figcaption { color: var(--down); font-weight: 600; }
+.cimg.miss::after { content: "✕"; position: absolute; top: 4%; right: 6%; width: 20px; height: 20px; border-radius: 50%; background: var(--down); color: #fff; font-size: 11px; font-weight: 800; display: grid; place-items: center; }
+.cimg.added figcaption { color: var(--up); font-weight: 700; }
+.cimg.added::after { content: "+"; position: absolute; top: 4%; right: 6%; width: 20px; height: 20px; border-radius: 50%; background: var(--up); color: #fff; font-size: 13px; font-weight: 800; display: grid; place-items: center; }
+.pred { border-radius: 10px; padding: 9px 11px; font-size: 13px; }
+.pred.ok { background: var(--warn-soft); }
+.pred.no { background: var(--surface-2); color: var(--text-2); }
+.pred .wr-big { color: var(--warn); font-size: 20px; }
+.pred-lbl { font-size: 12.5px; font-weight: 700; color: var(--warn); }
+.swaps { display: flex; flex-wrap: wrap; gap: 4px 10px; margin-top: 4px; }
+.swap { font-size: 12.5px; white-space: nowrap; }
+.swap s { color: var(--down); }
+.swap b { color: var(--up); }
+.btns { display: flex; flex-wrap: wrap; gap: 6px; align-items: center; }
+.btn { border: 1px solid var(--line); background: var(--surface); color: var(--text); font: inherit; font-size: 13px; font-weight: 600; cursor: pointer; padding: 6px 12px; border-radius: 8px; min-height: 34px; }
+.btn:hover { background: var(--surface-2); }
+.btn.primary { background: var(--accent); border-color: var(--accent); color: #fff; }
+.btn.primary:hover { filter: brightness(1.08); }
+:root[data-theme="dark"] .btn.primary { color: #121218; }
+@media (prefers-color-scheme: dark) { :root:not([data-theme="light"]) .btn.primary { color: #121218; } }
+.btn.ghost { border-color: transparent; background: none; color: var(--text-3); font-weight: 500; }
+.btn.ghost:hover { color: var(--text); background: var(--surface-2); }
+.dropped { font-size: 12px; color: var(--text-3); margin: 0; }
+details.ev { background: none; border: none; padding: 0; margin: 0; }
+details.ev > summary { padding: 2px 0; font-size: 12.5px; font-weight: 500; color: var(--text-3); }
+details.ev > div { padding: 2px 0 0; font-size: 12.5px; color: var(--text-2); }
+details.ev ul { margin: 2px 0; }
+.excluded { margin-top: 14px; font-size: 13px; color: var(--text-3); }
+.excluded b { color: var(--text-2); font-weight: 600; }
 .card { font-size: 13px; padding: 3px 9px; border-radius: 7px; background: var(--surface-2); border: 1px solid transparent; }
-.card.miss { background: var(--down-soft); color: var(--down); border-color: color-mix(in srgb, var(--down) 35%, transparent); }
-.card.miss::after { content: " ✕"; font-size: 11px; }
-.card.flex { border: 1px dashed var(--text-3); }
-.card .alt-miss { color: var(--down); text-decoration: line-through; }
-.notes { margin: 0; padding-left: 18px; font-size: 13px; color: var(--text-2); }
-.deck-foot { display: flex; justify-content: flex-end; }
-.copy { border: none; background: none; color: var(--text-3); font: inherit; font-size: 12.5px; cursor: pointer; padding: 4px 6px; border-radius: 6px; }
-.copy:hover { background: var(--surface-2); color: var(--text); }
+.cards { display: flex; flex-wrap: wrap; gap: 5px; }
 .empty { color: var(--text-3); padding: 24px; text-align: center; border: 1px dashed var(--line); border-radius: 14px; }
 
 /* tables */
@@ -160,7 +197,7 @@ footer { padding: 32px 0 48px; color: var(--text-3); font-size: 13px; }
 <nav class="top" aria-label="섹션">
   <div class="wrap">
     <a class="brand" href="#top">덱 노트</a>
-    <a href="#decks">덱 30선</a>
+    <a href="#decks">덱 목록</a>
     <a href="#collection">내 컬렉션</a>
     <a href="#season">시즌·패치</a>
     <a href="#basics">기본 규칙</a>
@@ -181,7 +218,7 @@ footer { padding: 32px 0 48px; color: var(--text-3); font-size: 13px; }
     <div class="panel">
       <ul class="trend">
         <li><b>Anti-Polar Magneto × Arthur Pendragon (4코스트 치트)</b> 계열이 시즌 최대 화두. Untapped 인기 1위 아키타입, SnapVault S티어에도 2개. Lancelot · Mordred · Captain Britain 등 시즌 신규 카드가 그대로 들어감.</li>
-        <li><b>Zombie Galacti / Shuri / Wong</b> — SnapVault 최대 표본(2,476판)으로 60% · +0.71 큐브. 근거가 가장 탄탄한 고성능 덱.</li>
+        <li><b>Zombie Galacti / Shuri / Wong</b> — 랭크 7일 2,239판 60.0%로 표본이 가장 큰 고성능 덱 (전체 모드 2,476판 · +0.71 큐브). 다만 MSZ 11/8 티어표·Coccia Top 10에는 없음.</li>
         <li><b>Stardust / Gambit Horseman of Death</b> 생성·테크 덱 — Sasquatch형이 SnapVault S. 피니셔만 바꾼 변형이 다수. Mobius 너프 영향권.</li>
         <li><b>Zombie Horde</b> — 사용량이 많고 성적이 양호 (SnapComplete 5,526판 59.1%). Zombie Scarlet Witch 너프(-1 파워).</li>
         <li><b>전통 강자</b> — High Evo · Fantomex는 두 출처 대표본으로 확인, Patriot은 Onslaught 버프 수혜. Destroy · Surfer · Thor · Galactus 등은 Untapped 단독 근거.</li>
@@ -191,23 +228,25 @@ footer { padding: 32px 0 48px; color: var(--text-3); font-size: 13px; }
   </section>
 
   <section id="decks" aria-labelledby="decks-h">
-    <h2 id="decks-h">고승률 덱 30선</h2>
-    <p class="lead">티어는 SnapVault 티어를 기준점으로, 다른 출처에서 1,000판 이상 확인되면 한 단계 올린 <b>잠정 평가</b>입니다. Untapped 단독 근거 덱은 티어를 매기지 않았습니다. 빨간 카드 = 내가 아직 없는 카드.</p>
+    <h2 id="decks-h">메타 덱 — 내 기준 승률순</h2>
+    <p class="lead" id="decksLead"></p>
     <div class="filters" role="group" aria-label="덱 필터">
-      <div class="frow" id="fTier"><span class="lbl">티어</span></div>
+      <div class="frow" id="fSort"><span class="lbl">정렬</span></div>
       <div class="frow" id="fOwn"><span class="lbl">보유</span></div>
+      <div class="frow" id="fTier"><span class="lbl">티어</span></div>
       <div class="frow" id="fFam"><span class="lbl">계열</span></div>
     </div>
     <p class="count-line" id="countLine"></p>
     <div class="decks" id="deckList"></div>
+    <p class="excluded" id="excludedLine"></p>
   </section>
 
   <section id="collection" aria-labelledby="coll-h">
     <h2 id="coll-h">내 컬렉션 — 미보유 카드</h2>
     <p class="lead" id="collLead"></p>
-    <h3 class="sub">획득 우선순위 (메타 덱 30선 등장 수 기준)</h3>
+    <h3 class="sub">획득 우선순위 (위 덱 목록 등장 수 기준)</h3>
     <div class="tbl-wrap"><table id="prioTable"></table></div>
-    <p class="muted" style="margin-top:8px">“얻으면 바로 열리는 덱” = 그 카드 한 장만 없어서 못 쓰던 덱. Scarlet Witch QoC + Anti-Polar Magneto 두 장이면 바로 쓸 수 있는 덱이 크게 늘어납니다.</p>
+    <p class="muted" style="margin-top:8px">“얻으면 바로 열리는 덱” = 그 카드 한 장만 없어서 원본 그대로 못 쓰던 덱. 괄호 안은 원본 랭크 7일 승률.</p>
     <h3 class="sub">미보유 Series 5 전체</h3>
     <div class="cards" id="unownedAll"></div>
     <p class="muted" style="margin-top:8px">Series 4 이하 미보유 여부는 아직 반영 전입니다.</p>
@@ -296,12 +335,34 @@ footer { padding: 32px 0 48px; color: var(--text-3); font-size: 13px; }
     <div class="tbl-wrap"><table>
       <thead><tr><th>출처</th><th>기간 / 모집단</th><th>특징</th></tr></thead>
       <tbody>
-        <tr><td><a href="https://www.snapvault.app/meta" target="_blank" rel="noopener">SnapVault</a></td><td>최근 7일, 전체 모드</td><td>승률 95% 신뢰구간 하한으로 순위 → 표본 크기 반영. 100판 미만은 Rising</td></tr>
+        <tr><td><a href="https://www.snapvault.app/meta" target="_blank" rel="noopener">SnapVault</a> <b>랭크 7일</b></td><td id="svSrc">최근 7일, 랭크만, 10판 이상 리스트</td><td><b>덱 카드의 승률·판수·평균 큐브</b> (12장 완전 일치). 100판 미만 빌드는 제외. 예측 승률도 이 데이터로 계산</td></tr>
+        <tr><td><a href="https://www.snapvault.app/meta" target="_blank" rel="noopener">SnapVault</a> 메타</td><td>최근 7일, 전체 모드</td><td>티어 산정 기준. 승률 95% 신뢰구간 하한으로 순위 → 표본 크기 반영. 100판 미만은 Rising</td></tr>
         <tr><td><a href="https://snapcomplete.com/play/decks" target="_blank" rel="noopener">SnapComplete</a></td><td>이번 주, Ranked + Conquest</td><td>승률 보정(smoothing). 판수가 가장 큼</td></tr>
         <tr><td><a href="https://snap.untapped.gg/en/meta" target="_blank" rel="noopener">Untapped.gg</a></td><td>30일, 랭크 10~79, Pool 3+</td><td>승률이 크게 높게 나옴 → 절대값 비교 금지</td></tr>
         <tr><td><a href="https://snap.fan/cards/tier-list/" target="_blank" rel="noopener">snap.fan 카드 티어</a></td><td>11/13 갱신</td><td>SnapComplete 데이터 기반 → 독립 검증 아님</td></tr>
+        <tr><td><a href="https://marvelsnapzone.com/marvel-snap-ranked-meta-tier-list-november-8-2026/" target="_blank" rel="noopener">Marvel Snap Zone 티어표</a></td><td>11/8 (OTA 전)</td><td>편집자 평가, 표본 수 비공개. 참고 덱 3개(Small On Reveals · Created Disruption · Curved Wiccan)와 교차 확인에 사용</td></tr>
+        <tr><td><a href="https://snapcomplete.com/play/meta/ota" target="_blank" rel="noopener">SnapComplete OTA 결과</a></td><td>11/12 OTA 전후, OTA 후 랭크 29만 판</td><td>Captain Britain 승률 51.0→53.9%, Mobius 52.7→50.0%, Zombie Scarlet Witch 55.0→54.4% (영향 작음)</td></tr>
+        <tr><td>참고만</td><td colspan="2">Alexander Coccia 주간 Top 10, r/MarvelSnapComp 주간 스레드, Fourth Location, 디시 마블스냅 갤러리 — 리스트 교차 확인용 (승률·표본 없음)</td></tr>
       </tbody>
     </table></div>
+    <details style="margin-top:12px">
+      <summary>예측 승률 계산 방법</summary>
+      <div><ul>
+        <li><b>같은 계열</b> = 원본과 12장 중 8장 이상 겹치는 랭크 7일 리스트</li>
+        <li>같은 계열에서 그 카드 <b>없이</b> 플레이된 판이 100판 미만이면 덱의 엔진 카드로 보고 <b>예측 불가</b></li>
+        <li><b>대체 카드</b> = 같은 계열에서 그 카드를 뺀 리스트에 실제로 가장 많이 들어간 보유 카드 (50판 이상)</li>
+        <li><b>카드별 기여도</b> = 원본과 6장 이상 겹치는 리스트로 가중 릿지 회귀 (겹칠수록 가중치 큼)</li>
+        <li><b>예측</b> = 원본 실제 승률 + Σ(들어가는 카드 기여 − 빠지는 카드 기여). 원본보다 높게는 잡지 않음</li>
+        <li>한계: 카드 간 시너지를 따로 모델링하지 않고, 데이터가 얇으면 하락 폭이 작게 나올 수 있음 → <b>참고용 추정치</b></li>
+      </ul></div>
+    </details>
+    <details>
+      <summary>덱 코드 복사</summary>
+      <div><ul>
+        <li>게임 덱 편집 화면에서 붙여넣기로 덱을 만들 수 있는 코드입니다 (카드별 게임 코드를 쉼표로 이어 base64 — SnapVault · Marvel Snap Zone과 같은 형식)</li>
+        <li>미보유 카드가 있는 덱은 <b>대체 덱 코드</b>(내 카드로 바꾼 버전)를 쓰세요</li>
+      </ul></div>
+    </details>
     <ul class="muted" style="padding-left:18px">
       <li>SnapComplete · Untapped는 11/12 OTA 이전 판이 섞였을 가능성이 큼. SnapVault는 밸런스 변경 덱 제외 정책을 밝혔지만 실제 처리는 불명확</li>
       <li>OTA 영향(⬆ 버프 카드 포함 · ⬇ 너프 카드 포함)은 표시만 했고 티어에는 반영하지 않음 — 다음 주 데이터로 확인 필요</li>
@@ -311,7 +372,7 @@ footer { padding: 32px 0 48px; color: var(--text-3); font-size: 13px; }
 </main>
 
 <footer class="wrap">
-  비공식 개인 덱 빌딩 노트입니다. 수치는 각 트래커 사이트의 공개 데이터를 정리한 것으로, 집계 시점에 따라 달라질 수 있습니다.
+  비공식 개인 덱 빌딩 노트입니다. 수치는 각 트래커 사이트의 공개 데이터를 정리한 것으로, 집계 시점에 따라 달라질 수 있습니다. 카드 이미지: <a href="https://snap.untapped.gg/" target="_blank" rel="noopener">Untapped.gg</a>
 </footer>
 <div class="toast" id="toast" role="status" aria-live="polite"></div>
 
@@ -319,15 +380,20 @@ footer { padding: 32px 0 48px; color: var(--text-3); font-size: 13px; }
 <script>
 (function () {
   const D = window.SNAP_DATA;
+  const C = D.cards;
   const $ = (id) => document.getElementById(id);
   const esc = (s) => String(s).replace(/[&<>"]/g, (c) => ({ "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;" }[c]));
+  const nm = (id) => (C[id] ? C[id].name : id);
+  const num = (n) => Number(n).toLocaleString("ko-KR");
+  const sgn = (n) => (n > 0 ? "+" : "") + n.toFixed(2);
+  const IMG = (id) => `https://snapjson.untapped.gg/art/render/framebreak/common/256/${encodeURIComponent(id)}.webp`;
+  const deckCode = (ids) => btoa(ids.map((id) => C[id].code).join(","));
 
   /* theme */
   const root = document.documentElement;
-  const btn = $("themeBtn");
   function applyTheme(t) { if (t) root.setAttribute("data-theme", t); else root.removeAttribute("data-theme"); }
   try { applyTheme(localStorage.getItem("snap-theme")); } catch (e) {}
-  btn.addEventListener("click", () => {
+  $("themeBtn").addEventListener("click", () => {
     const dark = root.getAttribute("data-theme") === "dark" ||
       (!root.getAttribute("data-theme") && matchMedia("(prefers-color-scheme: dark)").matches);
     const next = dark ? "light" : "dark";
@@ -335,39 +401,54 @@ footer { padding: 32px 0 48px; color: var(--text-3); font-size: 13px; }
     try { localStorage.setItem("snap-theme", next); } catch (e) {}
   });
 
-  /* ownership */
-  const UNOWNED = new Set(D.unowned.map((u) => u.name));
-  const cardMissing = (c) => c.options ? c.options.every((o) => UNOWNED.has(o)) : UNOWNED.has(c.name);
-  const missingOf = (list) => list.cards.filter(cardMissing).map((c) => c.options ? c.options.join(" / ") : c.name);
-  function deckMissing(d) {
-    let best = null;
-    for (const l of d.lists) { const m = missingOf(l); if (!best || m.length < best.length) best = m; }
-    return best || [];
+  /* 덱별 '내 기준 승률' 계산 */
+  const UNOWNED = new Set(D.unowned.map((u) => u.id));
+  function effOf(b) {
+    if (!b.miss.length) return { wr: b.stats.wr, kind: "real" };
+    if (b.pred && b.pred.ok) return { wr: b.pred.wr, kind: "pred" };
+    return { wr: null, kind: "none" };
   }
-  D.decks.forEach((d) => { d._miss = deckMissing(d); });
-  D.refs.forEach((d, i) => { d._miss = deckMissing(d); d.tier = "REF"; d.no = null; d._refIdx = i; });
+  const cmpEff = (a, b) => (b.wr ?? -1) - (a.wr ?? -1);
+  D.decks.forEach((d, i) => {
+    d._key = "d" + i;
+    d.builds.forEach((b, j) => { b._eff = effOf(b); b._key = d._key + "b" + j; });
+    d.builds.sort((x, y) => cmpEff(x._eff, y._eff) || y.stats.wr - x.stats.wr);
+    d._eff = d.builds[0]._eff;
+    d._raw = Math.max(...d.builds.map((b) => b.stats.wr));
+    d._status = d.builds.some((b) => !b.miss.length) ? "ok" : d.builds.some((b) => b._eff.kind === "pred") ? "pred" : "none";
+    d._miss = d.builds.map((b) => b.miss).sort((x, y) => x.length - y.length)[0];
+  });
+  const byKey = Object.fromEntries(D.decks.map((d) => [d._key, d]));
+  const buildByKey = Object.fromEntries(D.decks.flatMap((d) => d.builds.map((b) => [b._key, b])));
 
   const TIER_LABEL = { S: "S", A: "A", B: "B", C: "C", UT: "UT", REF: "참고" };
   const TIER_ORDER = { S: 0, A: 1, B: 2, C: 3, UT: 4, REF: 5 };
+  const RS = D.rankedSource;
 
   /* hero */
-  const ready = D.decks.filter((d) => d._miss.length === 0).length;
-  const one = D.decks.filter((d) => d._miss.length === 1).length;
-  $("heroSub").textContent = `메타 기준일 ${D.asOf} · Knights of Avalon 시즌 2주차 · 11/12 OTA 직후`;
+  const nOk = D.decks.filter((d) => d._status === "ok").length;
+  const nPred = D.decks.filter((d) => d._status === "pred").length;
+  $("heroSub").textContent = `메타 기준일 ${D.asOf} · Knights of Avalon 시즌 2주차 · 11/12 OTA 직후 · 승률은 ${RS.site} ${RS.mode} ${RS.window}`;
   $("stats").innerHTML = [
-    [D.decks.length, "메타 덱"], [ready, "지금 바로 사용 가능"], [one, "1장만 부족"], [D.unowned.length, "미보유 Series 5"],
+    [D.decks.length, `랭크 ${RS.window} ${RS.minGames}판+ 덱`], [nOk, "지금 바로 사용 가능"], [nPred, "내 카드로 대체 예측"], [D.unowned.length, "미보유 Series 5"],
   ].map(([n, l]) => `<div class="stat"><b>${n}</b><span>${l}</span></div>`).join("");
+  const fetched = RS.fetchedAt.replace("T", " ").slice(0, 16) + " UTC";
+  $("decksLead").innerHTML = `승률·판수는 <b>${esc(RS.site)} ${esc(RS.mode)} 최근 ${esc(RS.window)}</b>에서 12장이 똑같은 덱의 전적입니다 (${esc(fetched)} 수집, ${RS.minGames}판 미만 제외). ` +
+    `정렬은 <b>내가 기대할 수 있는 승률</b> 순 — 바로 쓸 수 있는 덱은 실제 승률, 미보유 카드가 있는 덱은 내 카드로 바꿨을 때의 <b>예측 승률</b>(참고용 추정)입니다. ` +
+    `티어 배지는 노트의 잠정 평가(전체 모드 기준)이고, 흐린 카드 ✕ = 내가 없는 카드.`;
+  $("svSrc").textContent = `최근 ${RS.window}, ${RS.mode}만, 10판 이상 리스트 ${num(RS.lists)}개 (${fetched})`;
 
   /* filters */
-  const state = { tier: "all", own: "all", fam: "all" };
-  try { Object.assign(state, JSON.parse(localStorage.getItem("snap-filters") || "{}")); } catch (e) {}
+  const state = { sort: "eff", own: "all", tier: "all", fam: "all" };
+  try { Object.assign(state, JSON.parse(localStorage.getItem("snap-filters-v3") || "{}")); } catch (e) {}
   const fams = [...new Set(D.decks.map((d) => d.family || "기타"))].sort((a, b) => (a === "기타") - (b === "기타") || a.localeCompare(b));
   const FILTERS = {
+    sort: [["eff", "내 기준 승률"], ["raw", "원본 승률"], ["tier", "티어"]],
+    own: [["all", "전체"], ["ok", "바로 사용"], ["pred", "대체 예측"], ["none", "대체 불가"]],
     tier: [["all", "전체"], ["S", "S"], ["A", "A"], ["B", "B"], ["C", "C"], ["UT", "UT 단독"], ["REF", "참고"]],
-    own: [["all", "전체"], ["ok", "바로 사용"], ["one", "1장 부족"], ["many", "2장+ 부족"]],
     fam: [["all", "전체"], ...fams.map((f) => [f, f])],
   };
-  const rowId = { tier: "fTier", own: "fOwn", fam: "fFam" };
+  const rowId = { sort: "fSort", own: "fOwn", tier: "fTier", fam: "fFam" };
   function renderFilters() {
     for (const key of Object.keys(FILTERS)) {
       const row = $(rowId[key]);
@@ -378,7 +459,7 @@ footer { padding: 32px 0 48px; color: var(--text-3); font-size: 13px; }
         b.setAttribute("aria-pressed", String(state[key] === val));
         b.addEventListener("click", () => {
           state[key] = val;
-          try { localStorage.setItem("snap-filters", JSON.stringify(state)); } catch (e) {}
+          try { localStorage.setItem("snap-filters-v3", JSON.stringify(state)); } catch (e) {}
           renderFilters(); renderDecks();
         });
         row.appendChild(b);
@@ -386,78 +467,141 @@ footer { padding: 32px 0 48px; color: var(--text-3); font-size: 13px; }
     }
   }
 
-  function ownBadge(miss) {
-    if (miss.length === 0) return `<span class="own ok">✓ 바로 사용</span>`;
-    if (miss.length === 1) return `<span class="own one">1장 부족</span>`;
-    return `<span class="own many">${miss.length}장 부족</span>`;
+  /* rendering */
+  function ownBadge(d) {
+    if (d._status === "ok") return `<span class="own ok">✓ 바로 사용</span>`;
+    if (d._status === "pred") return `<span class="own pred">${d._miss.length}장 대체</span>`;
+    return `<span class="own none">${d._miss.length}장 부족</span>`;
+  }
+  function fig(id, mark) {
+    const c = C[id];
+    const miss = UNOWNED.has(id);
+    const cls = ["cimg", miss ? "miss" : "", mark === "added" ? "added" : ""].filter(Boolean).join(" ");
+    const tip = `${c.name} (${c.cost}/${c.power})${miss ? " — 미보유" : mark === "added" ? " — 대체로 넣은 카드" : ""}`;
+    return `<figure class="${cls}" title="${esc(tip)}"><img loading="lazy" decoding="async" width="256" height="256" src="${IMG(id)}" alt="${esc(c.name)}" onerror="this.parentNode.classList.add('noimg')"><span class="ph">${c.cost}</span><figcaption>${esc(c.name)}</figcaption></figure>`;
+  }
+  function statLine(st, dim) {
+    return `<div class="wr-line"><span class="wr-big${dim ? " dim" : ""}">${st.wr.toFixed(1)}%</span><span class="wr-meta">${dim ? "원본 · " : ""}랭크 ${esc(RS.window)} · ${num(st.games)}판${st.cubes != null ? ` · 평균 큐브 ${sgn(st.cubes)}` : ""}</span></div>`;
+  }
+  function predHTML(b) {
+    const p = b.pred;
+    if (!p.ok) {
+      const why = (p.blockers || []).map((x) => `<b>${esc(nm(x.id))}</b> 없이 플레이된 같은 계열 판이 ${num(x.without)}판뿐`).join(", ");
+      return `<div class="pred no">예측 불가 — ${why || "대체할 카드 데이터 부족"}. 덱의 핵심 카드라 내 카드로 바꾼 버전의 근거가 없습니다.</div>`;
+    }
+    const diff = p.delta < 0 ? `원본 대비 ${p.delta.toFixed(1)}%p` : "원본과 비슷";
+    return `<div class="pred ok">
+      <div class="wr-line"><span class="pred-lbl">내 카드로 대체 시 예측</span><span class="wr-big">${p.wr.toFixed(1)}%</span><span class="wr-meta">${diff} · 같은 계열 ${num(p.archLists)}개 리스트 ${num(p.archGames)}판 기반</span></div>
+      <div class="swaps">${p.swaps.map((s) => `<span class="swap"><s>${esc(nm(s.out))}</s> → <b>${esc(nm(s.in))}</b></span>`).join("")}</div>
+      ${p.exact ? `<div class="wr-meta" style="margin-top:4px">이 대체 리스트 자체의 실제 전적: ${p.exact.wr.toFixed(1)}% · ${num(p.exact.games)}판</div>` : ""}
+    </div>`;
   }
-  function cardChip(c) {
-    if (c.options) {
-      const inner = c.options.map((o) => UNOWNED.has(o) ? `<span class="alt-miss">${esc(o)}</span>` : esc(o)).join(" / ");
-      return `<span class="card flex${cardMissing(c) ? " miss" : ""}" title="둘 중 하나 선택">${inner}</span>`;
+  function buildHTML(b) {
+    const p = b.pred && b.pred.ok ? b.pred : null;
+    const added = p ? new Set(p.swaps.map((s) => s.in)) : null;
+    const gridOrig = `<div class="grid12" data-view="orig">${b.ids.map((id) => fig(id)).join("")}</div>`;
+    const gridAlt = p ? `<div class="grid12" data-view="alt" hidden>${p.ids.map((id) => fig(id, added.has(id) ? "added" : "")).join("")}</div>` : "";
+    const btns = [];
+    if (p) {
+      btns.push(`<button class="btn primary" type="button" data-act="code" data-ids="${p.ids.join(",")}" data-what="대체 덱 코드">대체 덱 코드 복사</button>`);
+      btns.push(`<button class="btn" type="button" data-act="view" data-b="${b._key}">대체 덱 보기</button>`);
+      btns.push(`<button class="btn ghost" type="button" data-act="code" data-ids="${b.ids.join(",")}" data-what="원본 덱 코드">원본 덱 코드</button>`);
+    } else {
+      btns.push(`<button class="btn${b.miss.length ? "" : " primary"}" type="button" data-act="code" data-ids="${b.ids.join(",")}" data-what="덱 코드">덱 코드 복사</button>`);
     }
-    return `<span class="card${UNOWNED.has(c.name) ? " miss" : ""}">${esc(c.name)}</span>`;
+    btns.push(`<button class="btn ghost" type="button" data-act="list" data-b="${b._key}">카드 목록</button>`);
+    return `<div class="build" data-b="${b._key}">
+      ${b.label ? `<p class="build-label">${esc(b.label)}</p>` : ""}
+      ${statLine(b.stats, !!b.miss.length)}
+      ${gridOrig}${gridAlt}
+      ${b.miss.length ? predHTML(b) : ""}
+      <div class="btns">${btns.join("")}</div>
+    </div>`;
   }
-  function deckHTML(d, key) {
+  function deckHTML(d, rank) {
     const tags = [];
     if (d.family) tags.push(`<span class="tag">${esc(d.family)}</span>`);
     for (const o of d.ota) tags.push(`<span class="tag ${o.dir}">${o.dir === "up" ? "⬆" : "⬇"} ${esc(o.card)}</span>`);
-    const lists = d.lists.map((l, i) => `${l.label ? `<p class="list-label">${esc(l.label)}</p>` : ""}<div class="cards">${l.cards.map(cardChip).join("")}</div>`).join("");
-    const notes = d.notes && d.notes.length ? `<ul class="notes">${d.notes.map((n) => `<li>${esc(n)}</li>`).join("")}</ul>` : "";
-    const missLine = d._miss.length ? `<p class="ev" style="color:var(--down)">미보유: ${d._miss.map(esc).join(", ")}</p>` : "";
+    const ev = [...d.evidence, ...(d.notes || [])];
+    const dropped = (d.droppedBuilds || []).length
+      ? `<p class="dropped">제외된 빌드: ${d.droppedBuilds.map((x) => `${esc(x.label || "기본")} (${num(x.games)}판)`).join(", ")} — 랭크 ${esc(RS.window)} ${RS.minGames}판 미만</p>` : "";
     return `<article class="deck">
       <div class="deck-head">
+        <div class="rank" aria-label="순위">${rank}</div>
         <div class="tier ${d.tier}" aria-label="티어 ${TIER_LABEL[d.tier]}">${TIER_LABEL[d.tier]}</div>
         <div class="deck-title"><h3>${d.no ? `<span class="no">#${d.no}</span>` : ""}${esc(d.name)}</h3>${tags.length ? `<div class="tags">${tags.join("")}</div>` : ""}</div>
-        ${ownBadge(d._miss)}
+        ${ownBadge(d)}
       </div>
-      ${d.evidence.map((e) => `<p class="ev">${esc(e)}</p>`).join("")}
-      ${missLine}
-      ${lists}
-      ${notes}
-      <div class="deck-foot"><button class="copy" type="button" data-key="${key}">카드 목록 복사</button></div>
+      ${d.builds.map(buildHTML).join("")}
+      ${dropped}
+      ${ev.length ? `<details class="ev"><summary>티어 근거 · 메모</summary><div><ul>${ev.map((e) => `<li>${esc(e)}</li>`).join("")}</ul></div></details>` : ""}
     </article>`;
   }
 
-  const ALL = [...D.decks.map((d, i) => ({ d, key: "d" + i })), ...D.refs.map((d, i) => ({ d, key: "r" + i }))];
-  const byKey = Object.fromEntries(ALL.map((x) => [x.key, x.d]));
   function renderDecks() {
-    const out = ALL.filter(({ d }) => {
-      if (state.tier === "all" ? d.tier === "REF" : d.tier !== state.tier) return false;
-      const n = d._miss.length;
-      if (state.own === "ok" && n !== 0) return false;
-      if (state.own === "one" && n !== 1) return false;
-      if (state.own === "many" && n < 2) return false;
+    const out = D.decks.filter((d) => {
+      if (state.tier !== "all" && d.tier !== state.tier) return false;
+      if (state.own !== "all" && d._status !== state.own) return false;
       if (state.fam !== "all" && (d.family || "기타") !== state.fam) return false;
       return true;
-    }).sort((a, b) => TIER_ORDER[a.d.tier] - TIER_ORDER[b.d.tier] || (a.d.no || 0) - (b.d.no || 0));
-    $("countLine").textContent = `${out.length}개 덱 표시` + (state.tier === "all" ? " (참고 덱은 ‘참고’ 필터에서)" : "");
-    $("deckList").innerHTML = out.length ? out.map(({ d, key }) => deckHTML(d, key)).join("") : `<div class="empty">조건에 맞는 덱이 없습니다.</div>`;
+    });
+    if (state.sort === "eff") out.sort((a, b) => cmpEff(a._eff, b._eff) || b._raw - a._raw);
+    else if (state.sort === "raw") out.sort((a, b) => b._raw - a._raw);
+    else out.sort((a, b) => TIER_ORDER[a.tier] - TIER_ORDER[b.tier] || (a.no || 99) - (b.no || 99) || b._raw - a._raw);
+    $("countLine").textContent = `${out.length}개 덱 표시`;
+    $("deckList").innerHTML = out.length ? out.map((d, i) => deckHTML(d, i + 1)).join("") : `<div class="empty">조건에 맞는 덱이 없습니다.</div>`;
   }
+
   $("deckList").addEventListener("click", (e) => {
-    const b = e.target.closest(".copy"); if (!b) return;
-    const d = byKey[b.dataset.key];
-    const text = d.lists.map((l) => (l.label ? `[${l.label}]\n` : "") + l.cards.map((c) => c.options ? c.options.join(" 또는 ") : c.name).join("\n")).join("\n\n");
-    const done = () => toast("카드 목록을 복사했어요");
-    if (navigator.clipboard) navigator.clipboard.writeText(`${d.name}\n${text}`).then(done, () => toast("복사 실패"));
+    const btn = e.target.closest("button[data-act]"); if (!btn) return;
+    const act = btn.dataset.act;
+    if (act === "code") {
+      const code = deckCode(btn.dataset.ids.split(","));
+      copy(code, `${btn.dataset.what}를 복사했어요 — 게임 덱 편집 화면에서 붙여넣기`);
+    } else if (act === "list") {
+      const b = buildByKey[btn.dataset.b];
+      const box = btn.closest(".build");
+      const alt = box.querySelector('[data-view="alt"]');
+      const ids = alt && !alt.hidden ? b.pred.ids : b.ids;
+      copy(ids.map((id) => `(${C[id].cost}) ${C[id].name}`).join("\n"), "카드 목록을 복사했어요");
+    } else if (act === "view") {
+      const box = btn.closest(".build");
+      const orig = box.querySelector('[data-view="orig"]'), alt = box.querySelector('[data-view="alt"]');
+      const showAlt = alt.hidden;
+      alt.hidden = !showAlt; orig.hidden = showAlt;
+      btn.textContent = showAlt ? "원본 덱 보기" : "대체 덱 보기";
+    }
   });
+  function copy(text, msg) {
+    const ok = () => toast(msg), fail = () => toast("복사 실패 — 브라우저가 클립보드 접근을 막았어요");
+    if (navigator.clipboard && window.isSecureContext) { navigator.clipboard.writeText(text).then(ok, fail); return; }
+    try {
+      const ta = document.createElement("textarea"); ta.value = text; ta.style.position = "fixed"; ta.style.opacity = "0";
+      document.body.appendChild(ta); ta.select(); document.execCommand("copy"); ta.remove(); ok();
+    } catch (e) { fail(); }
+  }
   let tt;
-  function toast(msg) { const t = $("toast"); t.textContent = msg; t.classList.add("show"); clearTimeout(tt); tt = setTimeout(() => t.classList.remove("show"), 1600); }
+  function toast(msg) { const t = $("toast"); t.textContent = msg; t.classList.add("show"); clearTimeout(tt); tt = setTimeout(() => t.classList.remove("show"), 2200); }
+
+  if (D.excluded.length) {
+    $("excludedLine").innerHTML = `<b>랭크 ${esc(RS.window)} ${RS.minGames}판 미만이라 제외한 덱</b> — ` +
+      D.excluded.map((x) => `${x.no ? "#" + x.no + " " : ""}${esc(x.name)} (${num(x.games)}판)`).join(" · ");
+  }
 
   /* collection */
   $("collLead").textContent = `${D.collectionUpdated} 인게임 캡처 기준 미보유 Series 5 ${D.unowned.length}장. 이 목록에 없는 Series 5는 보유한 것으로 간주합니다.`;
-  const tierOf = (d) => TIER_LABEL[d.tier];
+  const label = (d) => (d.no ? "#" + d.no : esc(d.name));
   const prio = D.unowned.map((u) => {
-    const inDecks = D.decks.filter((d) => d.lists.some((l) => l.cards.some((c) => c.name === u.name || (c.options && c.options.includes(u.name)))));
-    const unlocks = D.decks.filter((d) => d._miss.length === 1 && d._miss[0] === u.name);
+    const inDecks = D.decks.filter((d) => d.builds.some((b) => b.ids.includes(u.id)));
+    const unlocks = D.decks.filter((d) => d._status !== "ok" && d._miss.length === 1 && d._miss[0] === u.id);
     return { u, inDecks, unlocks };
   }).sort((a, b) => b.inDecks.length - a.inDecks.length || b.unlocks.length - a.unlocks.length);
-  const fmtDecks = (arr) => arr.map((d) => `#${d.no}<span class="muted">(${tierOf(d)})</span>`).join(", ");
+  const fmtDecks = (arr) => arr.map((d) => `${label(d)}<span class="muted">(${d._raw.toFixed(1)}%)</span>`).join(", ");
   const used = prio.filter((p) => p.inDecks.length);
   const unused = prio.filter((p) => !p.inDecks.length);
   $("prioTable").innerHTML = `<thead><tr><th>카드</th><th>코/파</th><th>등장</th><th>들어가는 덱</th><th>얻으면 바로 열리는 덱</th></tr></thead><tbody>` +
     used.map((p) => `<tr><td><b>${esc(p.u.name)}</b></td><td class="num">${esc(p.u.stat)}</td><td class="num">${p.inDecks.length}</td><td>${fmtDecks(p.inDecks)}</td><td>${p.unlocks.length ? fmtDecks(p.unlocks) : '<span class="muted">—</span>'}</td></tr>`).join("") +
-    `<tr><td colspan="5" class="muted">메타 30선에 없음: ${unused.map((p) => esc(p.u.name)).join(", ")}</td></tr></tbody>`;
+    `<tr><td colspan="5" class="muted">덱 목록에 없음: ${unused.map((p) => esc(p.u.name)).join(", ")}</td></tr></tbody>`;
   $("unownedAll").innerHTML = D.unowned.map((u) => `<span class="card">${esc(u.name)} <span class="muted">${esc(u.stat)}</span></span>`).join("");
 
   renderFilters();
diff --git a/tools/build_data.py b/tools/build_data.py
index baf4713..8ede20f 100644
--- a/tools/build_data.py
+++ b/tools/build_data.py
@@ -1,16 +1,31 @@
 #!/usr/bin/env python3
-"""notes/meta-*.md + notes/collection.md -> data.js (페이지용 데이터).
+"""notes/meta-*.md + notes/collection.md + cache/(SnapVault) -> data.js (페이지용 데이터).
 
-사용: python3 tools/build_data.py [notes/meta-YYYY-MM-DD.md]
+사용:
+  python3 tools/fetch_sv.py          # SnapVault 랭크 7일 데이터 갱신 (cache/)
+  python3 tools/build_data.py [notes/meta-YYYY-MM-DD.md]
 인자 없으면 notes/ 안의 가장 최신 meta-*.md 사용.
+
+- 노트의 플렉스 슬롯(A 또는 B)은 실제 12장 빌드로 펼친다.
+- 빌드마다 SnapVault 랭크 7일 통계를 12장 완전 일치로 붙인다. MIN_GAMES 미만 빌드는 제외.
+- 미보유 카드가 있는 빌드는 '보유 카드만 쓴 실제 유사 리스트'의 전적을 합산해 예측한다.
 """
+import itertools
 import json
 import re
 import sys
+from collections import Counter
 from pathlib import Path
 
 ROOT = Path(__file__).resolve().parent.parent
 NOTES = ROOT / "notes"
+CACHE = ROOT / "cache"
+
+MIN_GAMES = 100   # 랭크 7일 이 판수 미만 빌드는 목록에서 제외 (사용자 요청)
+MIN_PRED = 100    # 빠지는 카드 없이 플레이된 같은 계열 판수가 이보다 적으면 예측 불가 (엔진 카드)
+MIN_SUB = 50      # 대체 후보 카드가 같은 계열에서 쓰인 최소 판수
+SAME_ARCH = 8     # 원본 빌드와 12장 중 이만큼 겹치면 같은 계열로 봄
+RIDGE_LAMBDA = 200  # 카드 기여도 추정 축소 강도 (가상 판수)
 
 TIER_HEADERS = {
     "### S 티어": "S",
@@ -21,28 +36,29 @@ TIER_HEADERS = {
     "### 참고": "REF",
 }
 
-# collection.md 표기 -> 덱 리스트 표기
-NAME_FIX = {
-    "Death (Fractured Frontier)": "Death Fractured Frontier",
-    "Storm (부제 있는 변형판)": "Storm (variant)",
+# 노트/컬렉션 표기 -> SnapVault 카드 이름 (정규화로 안 맞는 것만)
+ALIASES = {
+    "kang the conqueror": "kang",
 }
 
 
+def norm(s: str) -> str:
+    s = s.lower().replace("(", " ").replace(")", " ")
+    s = re.sub(r"[^a-z0-9 ]", "", s)
+    return re.sub(r"\s+", " ", s).strip()
+
+
 def strip_md(s: str) -> str:
     return s.replace("**", "").strip()
 
 
 def parse_cards(body: str):
-    """'A, B, **X 또는 Y**, C' -> [{"name": "A"}, {"options": ["X","Y"]}, ...]"""
+    """'A, B, **X 또는 Y**, C' -> [["A"], ["B"], ["X","Y"], ["C"]]"""
     out = []
     for raw in body.split(","):
         c = strip_md(raw)
-        if not c:
-            continue
-        if " 또는 " in c:
-            out.append({"options": [p.strip() for p in c.split(" 또는 ")]})
-        else:
-            out.append({"name": c})
+        if c:
+            out.append([p.strip() for p in c.split(" 또는 ")])
     return out
 
 
@@ -59,62 +75,57 @@ def parse_meta(path: Path):
 
     for line in sec5.splitlines():
         s = line.strip()
-        for h, t in TIER_HEADERS.items():
-            if s.startswith(h):
-                tier = t
-                cur = None
-                break
-        else:
-            if tier is None:
-                continue
-            m = re.match(r"\*\*(\d+)\. (.+?)\*\*(.*)$", s)
-            if m and tier != "REF":
-                no, name, rest = int(m.group(1)), m.group(2).strip(), m.group(3)
-                ota = re.findall(r"([⬆⬇])\(([^)]+)\)", rest)
-                fam = re.search(r"계열:\s*([^—]+?)(?:,|$)", rest)
-                ut_ev = re.search(r"—\s*(UT [^,]+.*)$", rest)
-                cur = {
-                    "no": no, "tier": tier, "name": name,
+        hit = next((t for h, t in TIER_HEADERS.items() if s.startswith(h)), None)
+        if hit:
+            tier, cur = hit, None
+            continue
+        if tier is None:
+            continue
+        m = re.match(r"\*\*(\d+)\. (.+?)\*\*(.*)$", s)
+        if m and tier != "REF":
+            no, name, rest = int(m.group(1)), m.group(2).strip(), m.group(3)
+            ota = re.findall(r"([⬆⬇])\(([^)]+)\)", rest)
+            fam = re.search(r"계열:\s*([^—]+?)(?:,|$)", rest)
+            ut_ev = re.search(r"—\s*(UT [^,]+.*)$", rest)
+            cur = {
+                "no": no, "tier": tier, "name": name,
+                "ota": [{"dir": "up" if d == "⬆" else "down", "card": c} for d, c in ota],
+                "family": fam.group(1).strip() if fam else None,
+                "evidence": [], "lists": [], "notes": [],
+            }
+            if ut_ev and tier == "UT":
+                cur["evidence"].append(re.sub(r",?\s*계열:.*$", "", ut_ev.group(1)).strip())
+            decks.append(cur)
+            continue
+        if tier == "REF" and s.startswith("- **"):
+            m = re.match(r"- \*\*(.+?)\*\*(.*?)— (.*?):\s(.+)$", s)
+            if m:
+                ota = re.findall(r"([⬆⬇])\(([^)]+)\)", m.group(2))
+                refs.append({
+                    "no": None, "tier": "REF", "name": m.group(1).strip(),
                     "ota": [{"dir": "up" if d == "⬆" else "down", "card": c} for d, c in ota],
-                    "family": fam.group(1).strip() if fam else None,
-                    "evidence": [], "lists": [], "notes": [],
-                }
-                if ut_ev and tier == "UT":
-                    ev = re.sub(r",?\s*계열:.*$", "", ut_ev.group(1)).strip()
-                    cur["evidence"].append(ev)
-                decks.append(cur)
-                continue
-            if tier == "REF" and s.startswith("- **"):
-                m = re.match(r"- \*\*(.+?)\*\*(.*?)— (.*?):\s(.+)$", s)
-                if m:
-                    ota = re.findall(r"([⬆⬇])\(([^)]+)\)", m.group(2))
-                    refs.append({
-                        "name": m.group(1).strip(),
-                        "ota": [{"dir": "up" if d == "⬆" else "down", "card": c} for d, c in ota],
-                        "evidence": [m.group(3).strip()],
-                        "lists": [{"label": None, "cards": parse_cards(m.group(4))}],
-                    })
-                continue
-            if cur is None:
-                continue
-            if is_card_line(s):
-                body = s[2:]
-                label = None
-                vm = re.match(r"\(변형([^)]*)\)\s*(.+)$", body)
-                if vm:
-                    label = "변형" + (vm.group(1) or "")
-                    body = vm.group(2)
-                cur["lists"].append({"label": label, "cards": parse_cards(body)})
-            elif s.startswith("- 근거:"):
-                cur["evidence"].append(strip_md(s[len("- 근거:"):]))
-            elif s.startswith("- "):
-                cur["notes"].append(strip_md(s[2:]))
+                    "family": None, "evidence": [m.group(3).strip()], "notes": [],
+                    "lists": [{"label": None, "slots": parse_cards(m.group(4))}],
+                })
+            continue
+        if cur is None:
+            continue
+        if is_card_line(s):
+            body, label = s[2:], None
+            vm = re.match(r"\(변형([^)]*)\)\s*(.+)$", body)
+            if vm:
+                label = ("변형" + (vm.group(1) or "")).strip()
+                body = vm.group(2)
+            cur["lists"].append({"label": label, "slots": parse_cards(body)})
+        elif s.startswith("- 근거:"):
+            cur["evidence"].append(strip_md(s[len("- 근거:"):]))
+        elif s.startswith("- "):
+            cur["notes"].append(strip_md(s[2:]))
 
     for d in decks + refs:
         for lst in d["lists"]:
-            n = len(lst["cards"])
-            if n != 12:
-                raise SystemExit(f"[오류] {d.get('no', '')} {d['name']} 카드 수 {n}장")
+            if len(lst["slots"]) != 12:
+                raise SystemExit(f"[오류] {d.get('no') or ''} {d['name']} 카드 수 {len(lst['slots'])}장")
     return decks, refs
 
 
@@ -131,37 +142,229 @@ def parse_collection(path: Path):
         # 4열 표(시즌|카드|코스트/파워|기간) 또는 2열 표(카드|코스트/파워)
         name = cols[1] if len(cols) >= 4 else cols[0]
         stat = cols[2] if len(cols) >= 4 else cols[1]
-        name = NAME_FIX.get(name, name)
         cards.append({"name": name, "stat": stat})
     upd = re.search(r"마지막 갱신:\s*([0-9-]+)", text)
     return cards, (upd.group(1) if upd else None)
 
 
+def load_cache():
+    try:
+        cards = json.loads((CACHE / "sv_cards.json").read_text(encoding="utf-8"))
+        ranked = json.loads((CACHE / "sv_ranked7.json").read_text(encoding="utf-8"))
+    except FileNotFoundError:
+        raise SystemExit("[오류] cache/ 가 없습니다. 먼저 python3 tools/fetch_sv.py 를 실행하세요.")
+    return cards, ranked
+
+
+class Resolver:
+    def __init__(self, sv_cards):
+        self.by_norm = {norm(c["name"]): c for c in sv_cards if not c.get("isToken")}
+        self.by_id = {c["id"]: c for c in sv_cards}
+
+    def id_of(self, name: str) -> str:
+        key = norm(name)
+        key = ALIASES.get(key, key)
+        c = self.by_norm.get(key)
+        if not c:
+            raise SystemExit(f"[오류] SnapVault 카드 목록에서 '{name}' 을(를) 찾지 못함 → ALIASES 에 추가")
+        return c["id"]
+
+
+def stat_of(st):
+    g = st["totalGames"]
+    return {
+        "games": g,
+        "wins": st["wins"],
+        "wr": round(100 * st["wins"] / g, 1) if g else None,
+        "cubes": round(st["totalCubes"] / st["cubeGames"], 2) if st.get("cubeGames") else None,
+    }
+
+
+def ridge_effects(rows, lam=RIDGE_LAMBDA, sweeps=150):
+    """가중 릿지 회귀 (좌표 하강). rows = [(카드 set, 승률 0~1, 가중치)].
+    승률 ≈ b0 + Σ β_card. 반환: {card: β} (승률 단위, 0.01 = 1%p)."""
+    beta = Counter()
+    sw = sum(w for _, _, w in rows)
+    b0 = sum(y * w for _, y, w in rows) / sw
+    resid = [y - b0 for _, y, _ in rows]
+    by_card = {}
+    for i, (s, _, w) in enumerate(rows):
+        for c in s:
+            by_card.setdefault(c, []).append(i)
+    denom = {c: sum(rows[i][2] for i in idx) + lam for c, idx in by_card.items()}
+    for _ in range(sweeps):
+        for c, idx in by_card.items():
+            old = beta[c]
+            num = sum(rows[i][2] * (resid[i] + old) for i in idx)
+            new = num / denom[c]
+            if new != old:
+                d = new - old
+                for i in idx:
+                    resid[i] -= d
+                beta[c] = new
+        shift = sum(rows[i][2] * resid[i] for i in range(len(rows))) / sw
+        if shift:
+            b0 += shift
+            resid = [r - shift for r in resid]
+    return beta
+
+
+def predict(ids, wr_now, unowned, db):
+    """미보유 카드를 보유 카드로 바꿨을 때의 랭크 승률 추정.
+    1) 같은 계열 = 이 빌드와 SAME_ARCH장 이상 겹치는 랭크 7일 리스트
+    2) 빠지는 카드마다 같은 계열에서 그 카드 없이 플레이된 판이 MIN_PRED 미만이면 '엔진 카드' → 예측 불가
+    3) 대체 카드 = 같은 계열에서 그 카드가 빠진 리스트에 실제로 가장 많이 들어간 보유 카드 (MIN_SUB판 이상)
+       (기여도 최댓값으로 고르면 잡음이 큰 카드가 뽑혀 과대추정됨 → 사용량 기준)
+    4) 카드별 기여도 = 이 빌드와 6장 이상 겹치는 리스트로 가중 릿지 회귀
+    5) 예측 = 실제 원본 승률 + Σ(들어가는 카드 기여 − 빠지는 카드 기여), 단 원본보다 높게는 잡지 않음(보수적)"""
+    S = set(ids)
+    miss = sorted(S & unowned)
+    core = S - set(miss)
+    arch = [x for x in db if len(x["set"] & S) >= SAME_ARCH]
+    arch_games = sum(x["stats"]["totalGames"] for x in arch)
+
+    blockers, without_lists = [], {}
+    for m in miss:
+        wl = [x for x in arch if m not in x["set"]]
+        without_lists[m] = wl
+        g = sum(x["stats"]["totalGames"] for x in wl)
+        if g < MIN_PRED:
+            blockers.append({"id": m, "without": g})
+    if blockers:
+        return {"ok": False, "reason": "engine", "blockers": blockers,
+                "archLists": len(arch), "archGames": arch_games}
+
+    rows = [(x["set"], x["stats"]["wins"] / x["stats"]["totalGames"],
+             x["stats"]["totalGames"] * (len(x["set"] & S) / 12) ** 3)
+            for x in db if len(x["set"] & S) >= 6]
+    beta = ridge_effects(rows)
+
+    taken, swaps = set(), []
+    for m in miss:
+        use = Counter()
+        for x in without_lists[m]:
+            for c in x["set"] - S:
+                if c not in unowned and c not in taken:
+                    use[c] += x["stats"]["totalGames"]
+        cand = [(c, g) for c, g in use.most_common() if g >= MIN_SUB]
+        if not cand:
+            return {"ok": False, "reason": "nosub", "blockers": [{"id": m, "without": 0}],
+                    "archLists": len(arch), "archGames": arch_games}
+        sub, used_games = cand[0]
+        taken.add(sub)
+        swaps.append({"out": m, "in": sub, "used": used_games, "d": round(100 * (beta[sub] - beta[m]), 1)})
+    raw = 100 * sum(beta[s["in"]] - beta[s["out"]] for s in swaps)
+    delta = min(0.0, raw)
+    replaced = sorted(core | {s["in"] for s in swaps})
+    exact = next((x for x in db if x["set"] == frozenset(replaced)), None)
+    return {
+        "ok": True, "wr": round(wr_now + delta, 1), "delta": round(delta, 1), "rawDelta": round(raw, 1),
+        "swaps": swaps, "ids": replaced, "archLists": len(arch), "archGames": arch_games,
+        "exact": stat_of(exact["stats"]) if exact else None,
+    }
+
+
+def build_deck(d, res, unowned, db_by_sig, db):
+    builds = []
+    for lst in d["lists"]:
+        names_opts = lst["slots"]
+        flex_idx = [i for i, o in enumerate(names_opts) if len(o) > 1]
+        for combo in itertools.product(*names_opts):
+            ids = [res.id_of(n) for n in combo]
+            if len(set(ids)) != 12:
+                raise SystemExit(f"[오류] {d['name']} 중복 카드")
+            label_parts = [lst["label"]] if lst["label"] else []
+            if flex_idx:
+                label_parts.append(" · ".join(combo[i] for i in flex_idx) + " 빌드")
+            hit = db_by_sig.get(frozenset(ids))
+            b = {
+                "label": " / ".join(label_parts) or None,
+                "ids": ids,
+                "stats": stat_of(hit["stats"]) if hit else None,
+                "miss": sorted(set(ids) & unowned),
+            }
+            b["included"] = bool(b["stats"] and b["stats"]["games"] >= MIN_GAMES)
+            if b["included"] and b["miss"]:
+                b["pred"] = predict(ids, b["stats"]["wr"], unowned, db)
+            builds.append(b)
+    return builds
+
+
 def main():
-    if len(sys.argv) > 1:
-        meta = Path(sys.argv[1])
-    else:
-        meta = sorted(NOTES.glob("meta-*.md"))[-1]
+    meta = Path(sys.argv[1]) if len(sys.argv) > 1 else sorted(NOTES.glob("meta-*.md"))[-1]
     as_of = re.search(r"meta-(\d{4}-\d{2}-\d{2})", meta.name).group(1)
     decks, refs = parse_meta(meta)
-    unowned, coll_date = parse_collection(NOTES / "collection.md")
+    unowned_list, coll_date = parse_collection(NOTES / "collection.md")
+    sv_cards, ranked = load_cache()
+    res = Resolver(sv_cards)
+
+    for u in unowned_list:
+        u["id"] = res.id_of(u["name"])
+    unowned = {u["id"] for u in unowned_list}
+
+    db = []
+    for x in ranked["decks"]:
+        db.append({"set": frozenset(x["cardIds"]), "stats": x["stats"]})
+    db_by_sig = {x["set"]: x for x in db}
+
+    out_decks, excluded = [], []
+    for d in decks + refs:
+        builds = build_deck(d, res, unowned, db_by_sig, db)
+        inc = [b for b in builds if b["included"]]
+        lists = d.pop("lists")
+        if not inc:
+            excluded.append({
+                "no": d["no"], "tier": d["tier"], "name": d["name"],
+                "games": max((b["stats"]["games"] if b["stats"] else 0) for b in builds),
+            })
+            continue
+        d["builds"] = inc
+        d["droppedBuilds"] = [{"label": b["label"], "games": b["stats"]["games"] if b["stats"] else 0}
+                              for b in builds if not b["included"]]
+        out_decks.append(d)
+
+    used = set()
+    for d in out_decks:
+        for b in d["builds"]:
+            used |= set(b["ids"])
+            if b.get("pred") and b["pred"]["ok"]:
+                used |= set(b["pred"]["ids"])
+    used |= unowned
+    cards = {
+        cid: {"name": res.by_id[cid]["name"], "cost": res.by_id[cid]["cost"],
+              "power": res.by_id[cid]["power"], "code": res.by_id[cid]["deckCode"]}
+        for cid in sorted(used)
+    }
+    for d in out_decks:  # 코스트 → 이름 순 정렬 (화면·덱 코드 공통)
+        key = lambda c: (cards[c]["cost"], cards[c]["name"])
+        for b in d["builds"]:
+            b["ids"].sort(key=key)
+            if b.get("pred") and b["pred"]["ok"]:
+                b["pred"]["ids"].sort(key=key)
+
     data = {
         "asOf": as_of,
         "collectionUpdated": coll_date,
-        "decks": decks,
-        "refs": refs,
-        "unowned": unowned,
+        "rankedSource": {"site": "SnapVault", "window": "7일", "mode": "랭크", "fetchedAt": ranked["fetchedAt"],
+                         "minGames": MIN_GAMES, "minPred": MIN_PRED, "lists": len(db)},
+        "cards": cards,
+        "decks": out_decks,
+        "excluded": excluded,
+        "unowned": [{"id": u["id"], "name": u["name"], "stat": u["stat"]} for u in unowned_list],
     }
     out = ROOT / "data.js"
     out.write_text(
         "// tools/build_data.py 로 생성 — 직접 수정하지 말 것\n"
-        "window.SNAP_DATA = " + json.dumps(data, ensure_ascii=False, indent=1) + ";\n",
+        "window.SNAP_DATA = " + json.dumps(data, ensure_ascii=False, separators=(",", ":")) + ";\n",
         encoding="utf-8",
     )
-    tiers = {}
-    for d in decks:
-        tiers[d["tier"]] = tiers.get(d["tier"], 0) + 1
-    print(f"{meta.name}: 덱 {len(decks)}개 {tiers}, 참고 {len(refs)}개, 미보유 {len(unowned)}장 -> {out}")
+    n_main = sum(1 for d in out_decks if d["tier"] != "REF")
+    n_pred = sum(1 for d in out_decks for b in d["builds"] if b.get("pred", {}).get("ok"))
+    n_nopred = sum(1 for d in out_decks for b in d["builds"] if b["miss"] and not b.get("pred", {}).get("ok"))
+    print(f"{meta.name}: 표시 덱 {n_main}개 (+참고 {len(out_decks) - n_main}), 제외 {len(excluded)}개, "
+          f"예측 {n_pred}빌드 / 예측 불가 {n_nopred}빌드, 카드 {len(cards)}장 -> {out}")
+    for e in excluded:
+        print(f"  제외: #{e['no']} {e['name']} ({e['games']}판)")
 
 
 if __name__ == "__main__":

hook: PostToolUse
exec
/bin/zsh -lc "python3 -B - <<'PY'
import json, pathlib, collections, importlib.util
p=pathlib.Path('.')
r=json.loads((p/'cache/sv_ranked7.json').read_text())
c=json.loads((p/'cache/sv_cards.json').read_text())
d=json.loads((p/'data.js').read_text().split('window.SNAP_DATA = ',1)[1].rsplit(';',1)[0])
print('Cache:',{k:v for k,v in r.items() if k"'!='"'decks'})
print('Rows:',len(r['decks']),'games:',sum(x['stats']['totalGames'] for x in r['decks']))
print('Duplicate signatures:',len(r['decks'])-len({frozenset(x['cardIds']) for x in r['decks']}))
print('Bad card count:',sum(len(set(x['cardIds']))"'!=12 for x in r['"'decks']))
print('Stats example:',r['decks'][0])
print('Cards example:',c[0])
print('Output metadata:',{k:v for k,v in d.items() if k not in ['decks','cards','unowned']})
for x in d['decks']:
 print(x['no'],x['name'],[(b['label'],b['stats'],b['miss'],b.get('pred')) for b in x['builds']])
try:
 import numpy
 print('numpy',numpy.__version__)
except ImportError:
 print('no numpy')
PY" in /Users/mac_al03241630/Project/marvelsnap
 succeeded in 0ms:
Cache: {'fetchedAt': '2026-11-14T09:16:00+00:00', 'window': '7d', 'mode': 'ranked', 'minGames': 10}
Rows: 2559 games: 96927
Duplicate signatures: 0
Bad card count: 0
Stats example: {'cardIds': ['HydraBob', 'Iceman', 'IronPatriot', 'Martyr', 'MobiusMMobius', 'Quinjet', 'ShadowKing', 'Stardust', 'TechnoOrganicVirus', 'ThanosFracturedFrontier', 'Valentina', 'WilsonFisk'], 'stats': {'wins': 10, 'losses': 0, 'totalCubes': 27, 'totalGames': 10, 'cubeGames': 10}, 'players': 2}
Cards example: {'id': 'IronPatriot', 'name': 'Iron Patriot', 'cost': 2, 'power': 3, 'deckCode': 'IrnPtrtB', 'isToken': False, 'ability': "On Reveal: Add a random 4-Cost or more card to your hand. If you're winning here after next turn, give it -3 Cost.", 'flavor': None}
Output metadata: {'asOf': '2026-11-14', 'collectionUpdated': '2026-11-14', 'rankedSource': {'site': 'SnapVault', 'window': '7일', 'mode': '랭크', 'fetchedAt': '2026-11-14T09:16:00+00:00', 'minGames': 100, 'minPred': 100, 'lists': 2559}, 'excluded': [{'no': 10, 'tier': 'A', 'name': 'Zombie Horde — Werewolf By Night / Web Sling형', 'games': 91}, {'no': 13, 'tier': 'B', 'name': 'Stardust / Gambit HoD — Thanos Fractured Frontier형', 'games': 35}, {'no': 16, 'tier': 'B', 'name': 'Merlin of Avalon 생성 카드 덱', 'games': 0}, {'no': 17, 'tier': 'B', 'name': 'Kitty Pryde', 'games': 0}, {'no': 25, 'tier': 'UT', 'name': 'Destroy (Death / Knull)', 'games': 34}, {'no': 27, 'tier': 'UT', 'name': 'Galactus (Destroyer)', 'games': 62}, {'no': 30, 'tier': 'UT', 'name': 'Discard (Apocalypse / Dracula)', 'games': 77}, {'no': None, 'tier': 'REF', 'name': 'Fantomex / Omega Sentinel', 'games': 72}, {'no': None, 'tier': 'REF', 'name': 'Created Cards (Quinjet / Mother Askani)', 'games': 46}]}
1 Zombie Galacti / Shuri / Wong [(None, {'games': 2241, 'wins': 1345, 'wr': 60.0, 'cubes': 0.71}, [], None)]
2 Anti-Polar Magneto / Arthur — Lancelot · Galacta형 [(None, {'games': 207, 'wins': 123, 'wr': 59.4, 'cubes': 0.79}, ['AntiPolarMagneto', 'CaptainBritain', 'Lancelot'], {'ok': False, 'reason': 'engine', 'blockers': [{'id': 'CaptainBritain', 'without': 88}], 'archLists': 61, 'archGames': 3383})]
3 Anti-Polar Magneto / Doctor Doom — Rogue Scion · Mordred형 [(None, {'games': 354, 'wins': 224, 'wr': 63.3, 'cubes': 0.65}, ['AntiPolarMagneto', 'CaptainBritain', 'RogueScionOfDivision'], {'ok': False, 'reason': 'engine', 'blockers': [{'id': 'AntiPolarMagneto', 'without': 0}], 'archLists': 68, 'archGames': 2404})]
4 Fin Fang Foom / Gorr / Dragon Lord — Domino형 [(None, {'games': 192, 'wins': 120, 'wr': 62.5, 'cubes': 0.69}, ['AntiPolarMagneto'], {'ok': False, 'reason': 'engine', 'blockers': [{'id': 'AntiPolarMagneto', 'without': 22}], 'archLists': 58, 'archGames': 3834})]
5 Stardust / Gambit HoD — Sasquatch형 [(None, {'games': 309, 'wins': 199, 'wr': 64.4, 'cubes': 0.63}, ['ScarletWitchQueenOfChaos'], {'ok': False, 'reason': 'engine', 'blockers': [{'id': 'ScarletWitchQueenOfChaos', 'without': 42}], 'archLists': 42, 'archGames': 4267})]
6 Zombie Horde — Zombie Blade형 [(None, {'games': 1038, 'wins': 606, 'wr': 58.4, 'cubes': 0.38}, ['ScarletWitchQueenOfChaos', 'ZombieBlade'], {'ok': True, 'wr': 56.6, 'delta': -1.8, 'rawDelta': -1.8, 'swaps': [{'out': 'ScarletWitchQueenOfChaos', 'in': 'AbsorbingMan', 'used': 134, 'd': -0.5}, {'out': 'ZombieBlade', 'in': 'WerewolfByNight', 'used': 664, 'd': -1.3}], 'ids': ['MajesticWingbeat', 'NicholasScratch', 'TheHunger', 'JoaquinTorres', 'VampireKillmonger', 'ZombieMisterFantastic', 'Venus', 'WerewolfByNight', 'ZombieScarletWitch', 'AbsorbingMan', 'ZombieGiantMan', 'Sasquatch'], 'archLists': 89, 'archGames': 4579, 'exact': None})]
7 High Evolutionary (Hulk / Abomination) [(None, {'games': 379, 'wins': 228, 'wr': 60.2, 'cubes': 0.41}, [], None)]
8 Fantomex / Zombie Captain Marvel / Shadow King [(None, {'games': 1667, 'wins': 938, 'wr': 56.3, 'cubes': 0.49}, [], None)]
9 Stardust / Gambit HoD — Kluh형 [('Maria Hill 빌드', {'games': 984, 'wins': 579, 'wr': 58.8, 'cubes': 0.5}, ['Kluh', 'ScarletWitchQueenOfChaos'], {'ok': True, 'wr': 58.8, 'delta': 0.0, 'rawDelta': 0.6, 'swaps': [{'out': 'Kluh', 'in': 'DeafeningChord', 'used': 772, 'd': -0.2}, {'out': 'ScarletWitchQueenOfChaos', 'in': 'Merlin', 'used': 91, 'd': 0.8}], 'ids': ['DeafeningChord', 'HydraBob', 'KingEitri', 'MariaHill', 'IronPatriot', 'Merlin', 'ShadowlandsDaredevil', 'Valentina', 'MobiusMMobius', 'ShadowKing', 'GambitHorseman', 'Stardust'], 'archLists': 44, 'archGames': 4365, 'exact': None}), ('Deafening Chord 빌드', {'games': 1102, 'wins': 653, 'wr': 59.3, 'cubes': 0.34}, ['Kluh', 'ScarletWitchQueenOfChaos'], {'ok': True, 'wr': 59.2, 'delta': -0.1, 'rawDelta': -0.1, 'swaps': [{'out': 'Kluh', 'in': 'ThanosFracturedFrontier', 'used': 506, 'd': -0.2}, {'out': 'ScarletWitchQueenOfChaos', 'in': 'Merlin', 'used': 91, 'd': 0.1}], 'ids': ['DeafeningChord', 'HydraBob', 'KingEitri', 'IronPatriot', 'Merlin', 'ShadowlandsDaredevil', 'Valentina', 'MobiusMMobius', 'ShadowKing', 'GambitHorseman', 'Stardust', 'ThanosFracturedFrontier'], 'archLists': 44, 'archGames': 4365, 'exact': None})]
11 Zombie Horde — Luke Cage형 [(None, {'games': 109, 'wins': 70, 'wr': 64.2, 'cubes': 0.82}, ['ScarletWitchQueenOfChaos'], {'ok': True, 'wr': 63.0, 'delta': -1.2, 'rawDelta': -1.2, 'swaps': [{'out': 'ScarletWitchQueenOfChaos', 'in': 'AbsorbingMan', 'used': 123, 'd': -1.2}], 'ids': ['MajesticWingbeat', 'NicholasScratch', 'TheHunger', 'JoaquinTorres', 'LukeCage', 'VampireKillmonger', 'ZombieMisterFantastic', 'Venus', 'ZombieScarletWitch', 'AbsorbingMan', 'ZombieGiantMan', 'Sasquatch'], 'archLists': 82, 'archGames': 4404, 'exact': None})]
12 Zombie Galacti / Arthur / Stick [(None, {'games': 322, 'wins': 187, 'wr': 58.1, 'cubes': 0.48}, [], None)]
14 Spider-Ham [(None, {'games': 133, 'wins': 83, 'wr': 62.4, 'cubes': 0.65}, [], None)]
15 Zombie Horde — Merlin of Avalon형 [(None, {'games': 369, 'wins': 213, 'wr': 57.7, 'cubes': 0.26}, ['MerlinOfAvalon', 'ScarletWitchQueenOfChaos', 'ZombieBlade'], {'ok': True, 'wr': 57.1, 'delta': -0.6, 'rawDelta': -0.6, 'swaps': [{'out': 'MerlinOfAvalon', 'in': 'ZombieMisterFantastic', 'used': 1896, 'd': 1.3}, {'out': 'ScarletWitchQueenOfChaos', 'in': 'AbsorbingMan', 'used': 134, 'd': -0.5}, {'out': 'ZombieBlade', 'in': 'WerewolfByNight', 'used': 1272, 'd': -1.4}], 'ids': ['MajesticWingbeat', 'NicholasScratch', 'TheHunger', 'JoaquinTorres', 'VampireKillmonger', 'ZombieMisterFantastic', 'Venus', 'WerewolfByNight', 'ZombieScarletWitch', 'AbsorbingMan', 'ZombieGiantMan', 'Sasquatch'], 'archLists': 91, 'archGames': 5151, 'exact': None})]
18 Patriot — Onslaught / Ultron / Blue Marvel [(None, {'games': 221, 'wins': 134, 'wr': 60.6, 'cubes': 0.53}, [], None)]
19 Anti-Polar Magneto / Jubilee형 — Lancelot 또는 Captain Marvel [('Lancelot 빌드', {'games': 874, 'wins': 502, 'wr': 57.4, 'cubes': 0.36}, ['AntiPolarMagneto', 'CaptainBritain', 'Lancelot'], {'ok': True, 'wr': 55.0, 'delta': -2.4, 'rawDelta': -2.4, 'swaps': [{'out': 'AntiPolarMagneto', 'in': 'SuperiorIronMan', 'used': 946, 'd': -0.6}, {'out': 'CaptainBritain', 'in': 'Psylocke', 'used': 288, 'd': -1.1}, {'out': 'Lancelot', 'in': 'CaptainMarvel', 'used': 2527, 'd': -0.7}], 'ids': ['Zabu', 'Psylocke', 'Surge', 'Mordred', 'ArthurPendragon', 'CaptainMarvel', 'EnSabahNur', 'IronLad', 'Jubilee', 'JubileeSilverSurfer', 'WolverineHorseman', 'SuperiorIronMan'], 'archLists': 95, 'archGames': 6714, 'exact': None}), ('Captain Marvel 빌드', {'games': 562, 'wins': 322, 'wr': 57.3, 'cubes': 0.6}, ['AntiPolarMagneto', 'CaptainBritain'], {'ok': True, 'wr': 55.2, 'delta': -2.1, 'rawDelta': -2.1, 'swaps': [{'out': 'AntiPolarMagneto', 'in': 'Isca', 'used': 135, 'd': -1.3}, {'out': 'CaptainBritain', 'in': 'Psylocke', 'used': 318, 'd': -0.9}], 'ids': ['Zabu', 'Psylocke', 'Surge', 'Mordred', 'ArthurPendragon', 'CaptainMarvel', 'EnSabahNur', 'IronLad', 'Isca', 'Jubilee', 'JubileeSilverSurfer', 'WolverineHorseman'], 'archLists': 93, 'archGames': 5793, 'exact': None})]
20 Fin Fang Foom / Gorr — Zabu형 [(None, {'games': 1217, 'wins': 665, 'wr': 54.6, 'cubes': 0.41}, ['AntiPolarMagneto', 'CaptainBritain'], {'ok': False, 'reason': 'engine', 'blockers': [{'id': 'AntiPolarMagneto', 'without': 12}], 'archLists': 82, 'archGames': 5919})]
21 Zabu / Spider-Man BND / Superior Iron Man [(None, {'games': 778, 'wins': 433, 'wr': 55.7, 'cubes': 0.31}, ['CaptainBritain', 'Lancelot'], {'ok': False, 'reason': 'engine', 'blockers': [{'id': 'CaptainBritain', 'without': 14}], 'archLists': 24, 'archGames': 2327})]
22 Vampire Deacon Frost [(None, {'games': 860, 'wins': 473, 'wr': 55.0, 'cubes': 0.25}, ['AntiPolarMagneto', 'ScarletWitchQueenOfChaos', 'VampireDeaconFrost', 'VampireEnchantress', 'ZombieBlade'], {'ok': False, 'reason': 'engine', 'blockers': [{'id': 'VampireDeaconFrost', 'without': 0}, {'id': 'VampireEnchantress', 'without': 25}], 'archLists': 20, 'archGames': 1469})]
23 Arthur / Doctor Doom — Moondragon · Astral Projection형 [(None, {'games': 357, 'wins': 176, 'wr': 49.3, 'cubes': 0.25}, ['AntiPolarMagneto', 'Moondragon'], {'ok': False, 'reason': 'engine', 'blockers': [{'id': 'AntiPolarMagneto', 'without': 16}], 'archLists': 53, 'archGames': 1571})]
24 Thor (Odin / Jane Foster) [(None, {'games': 591, 'wins': 318, 'wr': 53.8, 'cubes': 0.35}, [], None)]
26 Silver Surfer [(None, {'games': 149, 'wins': 78, 'wr': 52.3, 'cubes': 0.35}, [], None)]
28 Living Tribunal [(None, {'games': 199, 'wins': 99, 'wr': 49.7, 'cubes': 0.14}, [], None)]
29 Mister Negative [(None, {'games': 152, 'wins': 82, 'wr': 53.9, 'cubes': 0.55}, [], None)]
None Sandstorm Patriot [(None, {'games': 1567, 'wins': 850, 'wr': 54.2, 'cubes': 0.31}, [], None)]
None Quicksilver (Conquest 1위) [(None, {'games': 193, 'wins': 113, 'wr': 58.5, 'cubes': 0.45}, ['AntiPolarMagneto', 'RogueScionOfDivision'], {'ok': False, 'reason': 'engine', 'blockers': [{'id': 'AntiPolarMagneto', 'without': 0}], 'archLists': 18, 'archGames': 666})]
None Small On Reveals (Merlin by Night) [(None, {'games': 376, 'wins': 214, 'wr': 56.9, 'cubes': 0.31}, ['MerlinOfAvalon', 'ScarletWitchQueenOfChaos'], {'ok': False, 'reason': 'engine', 'blockers': [{'id': 'ScarletWitchQueenOfChaos', 'without': 14}], 'archLists': 67, 'archGames': 4233})]
None Created Disruption (Techno-Organic Virus) [(None, {'games': 379, 'wins': 212, 'wr': 55.9, 'cubes': 0.25}, ['TechnoOrganicVirus'], {'ok': False, 'reason': 'engine', 'blockers': [{'id': 'TechnoOrganicVirus', 'without': 0}], 'archLists': 17, 'archGames': 776})]
None Curved Wiccan (Thanos Kluh) [(None, {'games': 521, 'wins': 290, 'wr': 55.7, 'cubes': 0.4}, ['Kluh', 'VampireEnchantress'], {'ok': False, 'reason': 'engine', 'blockers': [{'id': 'Kluh', 'without': 27}, {'id': 'VampireEnchantress', 'without': 55}], 'archLists': 11, 'archGames': 815})]
no numpy

hook: PostToolUse
hook: PostToolUse Completed
hook: PostToolUse Completed
hook: PostToolUse Completed
hook: PreToolUse
hook: PreToolUse Completed
exec
/bin/zsh -lc "nl -ba index.html | sed -n '338,395p'" in /Users/mac_al03241630/Project/marvelsnap
 succeeded in 0ms:
   338	        <tr><td><a href="https://www.snapvault.app/meta" target="_blank" rel="noopener">SnapVault</a> <b>랭크 7일</b></td><td id="svSrc">최근 7일, 랭크만, 10판 이상 리스트</td><td><b>덱 카드의 승률·판수·평균 큐브</b> (12장 완전 일치). 100판 미만 빌드는 제외. 예측 승률도 이 데이터로 계산</td></tr>
   339	        <tr><td><a href="https://www.snapvault.app/meta" target="_blank" rel="noopener">SnapVault</a> 메타</td><td>최근 7일, 전체 모드</td><td>티어 산정 기준. 승률 95% 신뢰구간 하한으로 순위 → 표본 크기 반영. 100판 미만은 Rising</td></tr>
   340	        <tr><td><a href="https://snapcomplete.com/play/decks" target="_blank" rel="noopener">SnapComplete</a></td><td>이번 주, Ranked + Conquest</td><td>승률 보정(smoothing). 판수가 가장 큼</td></tr>
   341	        <tr><td><a href="https://snap.untapped.gg/en/meta" target="_blank" rel="noopener">Untapped.gg</a></td><td>30일, 랭크 10~79, Pool 3+</td><td>승률이 크게 높게 나옴 → 절대값 비교 금지</td></tr>
   342	        <tr><td><a href="https://snap.fan/cards/tier-list/" target="_blank" rel="noopener">snap.fan 카드 티어</a></td><td>11/13 갱신</td><td>SnapComplete 데이터 기반 → 독립 검증 아님</td></tr>
   343	        <tr><td><a href="https://marvelsnapzone.com/marvel-snap-ranked-meta-tier-list-november-8-2026/" target="_blank" rel="noopener">Marvel Snap Zone 티어표</a></td><td>11/8 (OTA 전)</td><td>편집자 평가, 표본 수 비공개. 참고 덱 3개(Small On Reveals · Created Disruption · Curved Wiccan)와 교차 확인에 사용</td></tr>
   344	        <tr><td><a href="https://snapcomplete.com/play/meta/ota" target="_blank" rel="noopener">SnapComplete OTA 결과</a></td><td>11/12 OTA 전후, OTA 후 랭크 29만 판</td><td>Captain Britain 승률 51.0→53.9%, Mobius 52.7→50.0%, Zombie Scarlet Witch 55.0→54.4% (영향 작음)</td></tr>
   345	        <tr><td>참고만</td><td colspan="2">Alexander Coccia 주간 Top 10, r/MarvelSnapComp 주간 스레드, Fourth Location, 디시 마블스냅 갤러리 — 리스트 교차 확인용 (승률·표본 없음)</td></tr>
   346	      </tbody>
   347	    </table></div>
   348	    <details style="margin-top:12px">
   349	      <summary>예측 승률 계산 방법</summary>
   350	      <div><ul>
   351	        <li><b>같은 계열</b> = 원본과 12장 중 8장 이상 겹치는 랭크 7일 리스트</li>
   352	        <li>같은 계열에서 그 카드 <b>없이</b> 플레이된 판이 100판 미만이면 덱의 엔진 카드로 보고 <b>예측 불가</b></li>
   353	        <li><b>대체 카드</b> = 같은 계열에서 그 카드를 뺀 리스트에 실제로 가장 많이 들어간 보유 카드 (50판 이상)</li>
   354	        <li><b>카드별 기여도</b> = 원본과 6장 이상 겹치는 리스트로 가중 릿지 회귀 (겹칠수록 가중치 큼)</li>
   355	        <li><b>예측</b> = 원본 실제 승률 + Σ(들어가는 카드 기여 − 빠지는 카드 기여). 원본보다 높게는 잡지 않음</li>
   356	        <li>한계: 카드 간 시너지를 따로 모델링하지 않고, 데이터가 얇으면 하락 폭이 작게 나올 수 있음 → <b>참고용 추정치</b></li>
   357	      </ul></div>
   358	    </details>
   359	    <details>
   360	      <summary>덱 코드 복사</summary>
   361	      <div><ul>
   362	        <li>게임 덱 편집 화면에서 붙여넣기로 덱을 만들 수 있는 코드입니다 (카드별 게임 코드를 쉼표로 이어 base64 — SnapVault · Marvel Snap Zone과 같은 형식)</li>
   363	        <li>미보유 카드가 있는 덱은 <b>대체 덱 코드</b>(내 카드로 바꾼 버전)를 쓰세요</li>
   364	      </ul></div>
   365	    </details>
   366	    <ul class="muted" style="padding-left:18px">
   367	      <li>SnapComplete · Untapped는 11/12 OTA 이전 판이 섞였을 가능성이 큼. SnapVault는 밸런스 변경 덱 제외 정책을 밝혔지만 실제 처리는 불명확</li>
   368	      <li>OTA 영향(⬆ 버프 카드 포함 · ⬇ 너프 카드 포함)은 표시만 했고 티어에는 반영하지 않음 — 다음 주 데이터로 확인 필요</li>
   369	      <li>출처마다 모집단이 달라 같은 덱도 승률이 10%p 이상 차이 남</li>
   370	    </ul>
   371	  </section>
   372	</main>
   373	
   374	<footer class="wrap">
   375	  비공식 개인 덱 빌딩 노트입니다. 수치는 각 트래커 사이트의 공개 데이터를 정리한 것으로, 집계 시점에 따라 달라질 수 있습니다. 카드 이미지: <a href="https://snap.untapped.gg/" target="_blank" rel="noopener">Untapped.gg</a>
   376	</footer>
   377	<div class="toast" id="toast" role="status" aria-live="polite"></div>
   378	
   379	<script src="data.js"></script>
   380	<script>
   381	(function () {
   382	  const D = window.SNAP_DATA;
   383	  const C = D.cards;
   384	  const $ = (id) => document.getElementById(id);
   385	  const esc = (s) => String(s).replace(/[&<>"]/g, (c) => ({ "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;" }[c]));
   386	  const nm = (id) => (C[id] ? C[id].name : id);
   387	  const num = (n) => Number(n).toLocaleString("ko-KR");
   388	  const sgn = (n) => (n > 0 ? "+" : "") + n.toFixed(2);
   389	  const IMG = (id) => `https://snapjson.untapped.gg/art/render/framebreak/common/256/${encodeURIComponent(id)}.webp`;
   390	  const deckCode = (ids) => btoa(ids.map((id) => C[id].code).join(","));
   391	
   392	  /* theme */
   393	  const root = document.documentElement;
   394	  function applyTheme(t) { if (t) root.setAttribute("data-theme", t); else root.removeAttribute("data-theme"); }
   395	  try { applyTheme(localStorage.getItem("snap-theme")); } catch (e) {}

hook: PostToolUse
hook: PostToolUse Completed
hook: PreToolUse
hook: PreToolUse Completed
exec
/bin/zsh -lc "nl -ba notes/meta-2026-11-14.md | sed -n '110,275p'" in /Users/mac_al03241630/Project/marvelsnap
 succeeded in 0ms:
   110	
   111	## 4. 메타 흐름 요약
   112	
   113	1. **Anti-Polar Magneto × Arthur Pendragon (4코스트 치트) 계열이 시즌 최대 화두** — UT 기준 인기 1위 아키타입(Arthur 7.4~7.8%). SV S티어에도 2개. Lancelot / Mordred / Captain Britain 등 시즌 신규 카드가 그대로 들어가는 구조.
   114	2. **Zombie Galacti / Shuri / Wong** — SV에서 가장 큰 표본(2,476판)으로 60% · +0.71 큐브. 근거가 가장 탄탄한 고성능 덱.
   115	3. **Stardust / Gambit Horseman of Death 생성·테크 덱** — Sasquatch형이 SV S. snap.fan 카드 티어 유일한 S가 Gambit Horseman of Death(단, SC 기반). 피니셔(Sasquatch / Kluh / Thanos FF)만 바꾼 변형이 다수. Mobius 너프 영향권.
   116	4. **Zombie Horde(뱀파이어·좀비 Skill 덱)** — **사용량이 많고 성적이 양호** (SC 5,526판 59.1%). 11/12에 Zombie Scarlet Witch 너프(-1 파워). Merlin of Avalon 채용형도 등장.
   117	5. **전통 강자** — High Evo, Fantomex는 SV + UT 대표본으로 확인. Patriot은 Onslaught 버프 수혜. Destroy / Surfer / Thor / Galactus / Deacon 등은 UT 단독 근거.
   118	6. **많이 쓰이지만 승률은 평범** — Sandstorm Patriot (SC 최다 사용 7,093판, 승률 51%).
   119	
   120	### 계열별 색인 (변형을 독립 아키타입으로 과대평가하지 않도록)
   121	| 계열 | 덱 번호 |
   122	|---|---|
   123	| Anti-Polar Magneto / Arthur | #2, #3, #4, #19, #20, #21, #23 |
   124	| Stardust / Gambit HoD | #5, #9, #13 (+ #16 Merlin 생성 덱과 카드 다수 공유) |
   125	| Zombie Horde | #6, #10, #11, #15 |
   126	| Zombie Galacti | #1, #12 |
   127	
   128	### snap.fan 카드 티어 상위 (11/13, SC 데이터 기반)
   129	- **S**: Gambit Horseman of Death
   130	- **A**: Spider-Man Brand New Day, Venus, Captain Britain, Deafening Chord, Scarlet Witch Queen of Chaos, Surge
   131	
   132	---
   133	
   134	## 5. 고승률 덱 30선
   135	
   136	### 티어 산정 규칙 (잠정 편집자 평가)
   137	1. **기준점 = SnapVault 티어** (신뢰구간 하한 기반이라 표본 크기가 반영됨)
   138	2. SV 티어가 없는 덱(미등재·Rising): **SC만 있으면** 승률 58% 이상 B / 미만 C
   139	3. **다른 출처에서 1,000판 이상 표본으로 확인되면 한 단계 상향** (최대 S)
   140	4. **UT 단독 근거 덱은 티어를 매기지 않고** 별도 그룹으로 분리 (UT 승률은 다른 출처와 비교 불가)
   141	5. OTA 영향은 티어에 반영하지 않고 표시만: ⬆ 버프 카드 포함 · ⬇ 너프 카드 포함
   142	
   143	표기: SV = SnapVault(7일) / SC = SnapComplete(이번 주) / UT = Untapped · 승률 / 판수 / 평균 큐브
   144	
   145	### S 티어
   146	
   147	**1. Zombie Galacti / Shuri / Wong** — 계열: Zombie Galacti
   148	- 근거: SV **S** 60.0% / **2,476판** / **+0.71**
   149	- Deafening Chord, Majestic Wingbeat, Echo, Spider-Man Brand New Day, Adam Warlock, Surge, Magik, Superior Spider-Man, Mister Fantastic First Steps, Wong, Shuri, Zombie Galacti
   150	
   151	**2. Anti-Polar Magneto / Arthur — Lancelot · Galacta형** ⬆(Captain Britain) — 계열: APM
   152	- 근거: SV A 62.3% / 260판 / **+0.81** → SC 58.9% / 1,941판으로 확인되어 상향
   153	- Zabu, Surge, Captain Britain, Caliban Horseman of Pestilence, Mordred, Arthur Pendragon, Wolverine Horseman of War, Captain Marvel, Galacta, Lancelot, Iron Lad, Anti-Polar Magneto
   154	
   155	**3. Anti-Polar Magneto / Doctor Doom — Rogue Scion · Mordred형** ⬆(Captain Britain) — 계열: APM
   156	- 근거: SV **S** 62.8% / 368판 / +0.65
   157	- Red Wolf Fractured Frontier, Captain Britain, Drax Avatar of Life, Caliban Horseman of Pestilence, Mordred, Arthur Pendragon, En Sabah Nur, Doctor Doom 2099, Iron Lad, Rogue Scion of Division, Doctor Doom, Anti-Polar Magneto
   158	
   159	**4. Fin Fang Foom / Gorr / Dragon Lord — Domino형** — 계열: APM
   160	- 근거: SV **S** 67.6% / 306판 / +0.66 (SC 59.5% / 370판 / +0.47)
   161	- Domino, Jane Foster Fractured Frontier, Caliban Horseman of Pestilence, Jubilee, Arthur Pendragon, En Sabah Nur, Captain Marvel, Iron Lad, Dragon Lord, Gorr the God Butcher, Anti-Polar Magneto, Fin Fang Foom
   162	
   163	**5. Stardust / Gambit HoD — Sasquatch형** ⬇(Mobius) — 계열: Stardust
   164	- 근거: SV **S** 65.4% / 306판 / +0.64
   165	- Deafening Chord, King Eitri, Hydra Bob, Iron Patriot, Shadowlands Daredevil, Valentina, Mobius M. Mobius, Scarlet Witch Queen of Chaos, Shadow King, Gambit Horseman of Death, Stardust, Sasquatch
   166	
   167	### A 티어
   168	
   169	**6. Zombie Horde — Zombie Blade형** ⬇(Zombie SW) — 계열: Horde
   170	- 근거: SV B 58.9% / 1,156판 / +0.41 → SC 59.1% / 5,526판으로 확인되어 상향 (UT 아키타입 69.3%)
   171	- Majestic Wingbeat, The Hunger, Nicholas Scratch, Vampire Killmonger, Zombie Mister Fantastic, Joaquin Torres Falcon II, Zombie Blade, Venus, Scarlet Witch Queen of Chaos, Zombie Scarlet Witch, Zombie Giant-Man, Sasquatch
   172	- 플랜: Horde 누적 + Scarlet Witch QoC / Vampire Killmonger로 Skill 생성 → Zombie Giant-Man · Sasquatch 페이오프
   173	
   174	**7. High Evolutionary (Hulk / Abomination)**
   175	- 근거: SV B 59.8% / 396판 / +0.38 → UT 대표 덱 73.4% / 2,200판으로 확인되어 상향
   176	- Sunspot, Misty Knight, Armor, Scorpion, Shocker, Cyclops, Shang-Chi, High Evolutionary, The Thing, Enchantress, Abomination, Hulk
   177	- 플랜: High Evolutionary가 무능력 카드의 숨은 능력을 해금
   178	
   179	**8. Fantomex / Zombie Captain Marvel / Shadow King** ⬇(Mobius)
   180	- 근거: SV B 56.9% / 1,874판 / +0.52 → UT 67.3% / 1,500판(UT 티어 A)으로 확인되어 상향
   181	- The Hood, Blade, Wild Child, Bucky Barnes, Carnage, Marrow, Mobius M. Mobius, Gambit, Killmonger, Shadow King, Zombie Captain Marvel, Fantomex
   182	
   183	**9. Stardust / Gambit HoD — Kluh형** ⬇(Mobius) — 계열: Stardust
   184	- 근거: SV A 59.7% / 1,105판 / +0.49 (Maria Hill 빌드) · SV A 59.4% / 1,189판 / +0.34 (Deafening Chord 빌드)
   185	- King Eitri, **Maria Hill 또는 Deafening Chord**, Hydra Bob, Iron Patriot, Shadowlands Daredevil, Valentina, Mobius M. Mobius, Scarlet Witch Queen of Chaos, Shadow King, Gambit Horseman of Death, Stardust, Kluh
   186	
   187	**10. Zombie Horde — Werewolf By Night / Web Sling형** ⬇(Zombie SW) — 계열: Horde
   188	- 근거: SV A 66.3% / 104판 / +0.63 (소표본)
   189	- Majestic Wingbeat, The Hunger, Web Sling, Nicholas Scratch, Vampire Killmonger, Joaquin Torres Falcon II, Venus, Scarlet Witch Queen of Chaos, Werewolf By Night, Zombie Scarlet Witch, Zombie Giant-Man, Sasquatch
   190	- 참고: UT 대표 덱(69.1% / 860판)은 Web Sling 대신 Zombie Blade를 쓰는 다른 리스트
   191	
   192	**11. Zombie Horde — Luke Cage형** ⬇(Zombie SW) — 계열: Horde
   193	- 근거: SV A 65.8% / 114판 / **+0.93** (소표본)
   194	- Majestic Wingbeat, The Hunger, Nicholas Scratch, Luke Cage, Vampire Killmonger, Zombie Mister Fantastic, Joaquin Torres Falcon II, Venus, Scarlet Witch Queen of Chaos, Zombie Scarlet Witch, Zombie Giant-Man, Sasquatch
   195	
   196	### B 티어
   197	
   198	**12. Zombie Galacti / Arthur / Stick** — 계열: Zombie Galacti
   199	- 근거: SV B 60.2% / 377판 / +0.51
   200	- Majestic Wingbeat, America Chavez, Adam Warlock, Surge, Doctor Octopus Fractured Frontier, Magik, Maverick, Superior Spider-Man, Jubilee Silver Surfer, Stick, Arthur Pendragon, Zombie Galacti
   201	
   202	**13. Stardust / Gambit HoD — Thanos Fractured Frontier형** ⬇(Mobius) — 계열: Stardust
   203	- 근거: SC 59.2% / 779판 (SV Rising 68.8% / 48판)
   204	- Deafening Chord, King Eitri, Maria Hill, Iron Patriot, Shadowlands Daredevil, Valentina, Mobius M. Mobius, Scarlet Witch Queen of Chaos, Shadow King, Gambit Horseman of Death, Stardust, Thanos Fractured Frontier
   205	
   206	**14. Spider-Ham**
   207	- 근거: SC 59.3% / 1,357판
   208	- Spider-Ham, America Chavez, Nico Minoru, Spider-Man Brand New Day, Nightcrawler, Adam Warlock, Marvel Boy, Venus, Jane Foster Fractured Frontier, Elsa Bloodstone, Stardust, Thanos Fractured Frontier
   209	
   210	**15. Zombie Horde — Merlin of Avalon형** ⬇(Zombie SW) — 계열: Horde
   211	- 근거: SC 58.9% / 1,644판
   212	- Majestic Wingbeat, The Hunger, Merlin of Avalon, Nicholas Scratch, Vampire Killmonger, Joaquin Torres Falcon II, Zombie Blade, Venus, Scarlet Witch Queen of Chaos, Zombie Scarlet Witch, Zombie Giant-Man, Sasquatch
   213	
   214	**16. Merlin of Avalon 생성 카드 덱**
   215	- 근거: SC 60.4% / 253판 / +0.51 (소표본)
   216	- Merlin of Avalon, Clea, Nicholas Scratch, Vampire Killmonger, Cobra, Shadowlands Daredevil, Valentina, Marvel Boy, Scarlet Witch Queen of Chaos, Gambit Horseman of Death, Stardust, Sasquatch
   217	
   218	**17. Kitty Pryde**
   219	- 근거: SC 58.9% / 285판 (소표본)
   220	- Kitty Pryde, America Chavez, Merlin of Avalon, Maria Hill, Nightcrawler, Vampire Killmonger, Angela, The Collector, Bishop, Scarlet Witch Queen of Chaos, Shang-Chi, Thanos Fractured Frontier
   221	
   222	### C 티어
   223	
   224	**18. Patriot — Onslaught / Ultron / Blue Marvel** ⬆(Onslaught)
   225	- 근거: SV C 60.8% / 222판 / +0.58 (UT 68.0% / 800판 — 1,000판 미만이라 상향 안 함)
   226	- Ant Man, Squirrel Girl, Misty Knight, Dazzler, Armor, Mystique, Patriot, Cosmo, Ka-Zar, Blue Marvel, Ultron, Onslaught
   227	
   228	**19. Anti-Polar Magneto / Jubilee형 — Lancelot 또는 Captain Marvel** ⬆(Captain Britain) — 계열: APM
   229	- 근거: SV C 57.4% / 1,023판 / +0.33 (Lancelot 빌드) · SV C 58.1% / 651판 / +0.60 (Captain Marvel 빌드) — 두 빌드는 11장 동일
   230	- Zabu, Surge, Captain Britain, Mordred, Jubilee, Jubilee Silver Surfer, Arthur Pendragon, Wolverine Horseman of War, En Sabah Nur, **Lancelot 또는 Captain Marvel**, Iron Lad, Anti-Polar Magneto
   231	
   232	**20. Fin Fang Foom / Gorr — Zabu형** ⬆(Captain Britain) — 계열: APM
   233	- 근거: SV C 56.7% / 1,506판 / +0.42
   234	- Zabu, Captain Britain, Mordred, Jubilee, Arthur Pendragon, En Sabah Nur, Captain Marvel, Iron Lad, Dragon Lord, Gorr the God Butcher, Anti-Polar Magneto, Fin Fang Foom
   235	
   236	**21. Zabu / Spider-Man BND / Superior Iron Man** ⬆(Captain Britain) — 계열: APM 주변
   237	- 근거: SC 56% / 5,437판 (사용량 3위)
   238	- Zabu, Spider-Man Brand New Day, Surge, Jeff the Baby Dolphin!?, Captain Britain, Mister Fantastic First Steps, Jubilee Silver Surfer, Arthur Pendragon, Wolverine Horseman of War, Lancelot, Iron Lad, Superior Iron Man
   239	
   240	### 티어 미부여 — Untapped 단독 근거 (보수적 출처에서 교차 확인 안 됨)
   241	UT 덱 승률 순. `(30일)` = 아키타입 페이지(최근 30일, 랭크 10~79, Pool 3+), `(필터 미확인)` = 덱 목록 페이지.
   242	
   243	**22. Vampire Deacon Frost** — UT 69.0% / 580판 (30일), UT 티어 C
   244	- Silver Sable, Vampire Killmonger, Zombie Blade, Cassandra Nova, Scarlet Witch Queen of Chaos, Dragon of the Moon, En Sabah Nur, Laufey, Vampire Deacon Frost, Stryfe, Vampire Enchantress, Anti-Polar Magneto
   245	
   246	**23. Arthur / Doctor Doom — Moondragon · Astral Projection형** — UT 65.6% / 940판 (30일), 계열: APM
   247	- Moondragon, Luke Cage, Astral Projection, Drax Avatar of Life, Invisible Woman First Steps, Caliban Horseman of Pestilence, Arthur Pendragon, Captain Marvel, Doctor Doom 2099, Iron Lad, Doctor Doom, Anti-Polar Magneto
   248	
   249	**24. Thor (Odin / Jane Foster)** — UT 65.3% / 260판 (필터 미확인)
   250	- Wasp, Iceman, King Eitri, Surge, Lockjaw, Phastos, Thor, Beta Ray Bill, Thanos Fractured Frontier, Jane Foster Mighty Thor, Gorr the God Butcher, Odin
   251	
   252	**25. Destroy (Death / Knull)** — UT 64.7% / 1,300판 (30일), 아키타입 인기 6.3%
   253	- Deadpool, X-23, Nico Minoru, Carnage, Hulkbuster, Wolverine, Killmonger, Venom, Deathlok, Arnim Zola, Knull, Death
   254	
   255	**26. Silver Surfer** — UT 63.7% / 740판 (30일)
   256	- Luke Cage, Ironheart, Mystique, Brood, Magik, Silver Surfer, Hazmat, Rogue, Wong, Absorbing Man, Sera, Odin
   257	
   258	**27. Galactus (Destroyer)** — UT 60.7% / 700판 (30일), UT 티어 D
   259	- Nebula, Selene, Daredevil, Green Goblin, Magik, Electro, Wave, Negasonic Teenage Warhead, Hobgoblin, Spider-Woman, Galactus, Destroyer
   260	- (변형, SV Rising 71.7% / 60판 / +1.42) Selene, Daredevil, Wolverine, Green Goblin, Electro, Wave, Hobgoblin, Knull, Galactus, Alioth, Destroyer, Death
   261	
   262	**28. Living Tribunal** ⬆(Onslaught) — UT 60.5% / 210판 (필터 미확인)
   263	- Howard the Duck, Ravonna Renslayer, Mystique, Magik, Wave, Jubilee, Super-Skrull, Iron Lad, Iron Man, Sera, Onslaught, The Living Tribunal
   264	
   265	**29. Mister Negative** — UT 59.9% / 200판 (필터 미확인)
   266	- Psylocke, Ravonna Renslayer, Cassandra Nova, Mystique, Magik, Mister Negative, Shang-Chi, Iron Man, Jane Foster Mighty Thor, Arnim Zola, Knull, Gorr the God Butcher
   267	
   268	**30. Discard (Apocalypse / Dracula)** — UT 57.1% / 230판 (필터 미확인), 아키타입 64.8%
   269	- Blade, Swarm, Morbius, The Collector, Wolverine, Colleen Wing, Gambit, Moon Knight, Lady Sif, Dracula, M.O.D.O.K., Apocalypse
   270	
   271	### 참고 (표본 부족 / 인기만 높음)
   272	- **Sandstorm Patriot** — SC 최다 사용 7,093판이지만 51% / UT 62.9% / 250판: Sandstorm, Zombie Mister Fantastic, H.E.R.B.I.E., Rhino, Patriot, Prodigy, Shadow King, Luna Snow, Debrii, Selene Horseman of Famine, Ozymandias, Mockingbird
   273	- **Fantomex / Omega Sentinel** — SV Rising 65.8% / 73판: Blade, Fastball Special, Kid Omega, Wild Child, Marrow, Gambit, Jocasta, Air-Walker, Prodigy, Shadow King, Omega Sentinel, Fantomex
   274	- **Created Cards (Quinjet / Mother Askani)** ⬆(Captain Britain) — UT 54.5% / 560판: Quinjet, Zabu, Surge, Psylocke, Victoria Hand, Captain Britain, Valentina, Bastion, Arthur Pendragon, Mother Askani, Moon Girl, Moonstone
   275	- **Quicksilver (Conquest 1위)** — SC Conquest 65% / 16,018판(집계 기간 미표기): Quicksilver, Domino, Jane Foster Fractured Frontier, Speed, Caliban Horseman of Pestilence, Jubilee, En Sabah Nur, Karen Page, Captain Marvel, Rogue Scion of Division, Thanos Fractured Frontier, Anti-Polar Magneto

hook: PostToolUse
hook: PostToolUse Completed
hook: PreToolUse
hook: PreToolUse Completed
exec
/bin/zsh -lc 'nl -ba notes/collection.md' in /Users/mac_al03241630/Project/marvelsnap
 succeeded in 0ms:
     1	# 내 컬렉션 — 미보유 카드 목록
     2	
     3	> 마지막 갱신: 2026-11-14 (사용자 인게임 "미보유 시리즈 5 카드" 화면 캡처 기준)
     4	> 덱 추천 시 이 파일을 먼저 확인할 것. 카드 획득·추가 미보유 발견 시 즉시 갱신 (페이지 데이터 `tools/` 재생성도 같이).
     5	
     6	## 전제
     7	- 아래 **Series 5 24장 외의 Series 5 카드는 모두 보유**
     8	- Series 4 이하 미보유 여부는 **아직 미확인** → 확인되면 아래에 추가
     9	
    10	## 미보유 Series 5 (24장)
    11	
    12	### 시즌 카드 화면 (8장)
    13	| 시즌 | 카드 | 코스트/파워 | 화면 표시 기간 |
    14	|---|---|---|---|
    15	| 아발론의 기사들 (Knights of Avalon) | Lancelot | 4/6 | 7주 3일 |
    16	| 〃 | Captain Britain | 2/3 | 〃 |
    17	| 〃 | Merlin of Avalon | 1/2 | 〃 |
    18	| 뱀파이어 대 좀비 (Vampires vs. Zombies) | Vampire Deacon Frost | 4/5 | 2주 3일 |
    19	| 〃 | Zombie Black Cat | 3/5 | 〃 |
    20	| 〃 | Vampire Enchantress | 6/7 | 〃 |
    21	| 〃 | Zombie Blade | 2/3 | 〃 |
    22	| 〃 | Zombie Venom | 3/3 | 〃 |
    23	
    24	### 그 외 Series 5 (16장)
    25	| 카드 | 코스트/파워 |
    26	|---|---|
    27	| Anti-Polar Magneto | 6/8 |
    28	| Aunt May | 2/4 |
    29	| Boomerang | 2/3 |
    30	| Death (Fractured Frontier) | 5/9 |
    31	| Ezekiel Sims | 2/2 |
    32	| Friendly Neighborhood Carnage | 3/4 |
    33	| Jack Flag | 3/3 |
    34	| Kang the Conqueror | 3/5 |
    35	| Kluh | 5/11 |
    36	| Mary Jane | 3/3 |
    37	| Moondragon | 2/1 |
    38	| Rogue Scion of Division | 5/5 |
    39	| Scarlet Witch Queen of Chaos | 3/3 |
    40	| Storm Horseman of Famine | 3/1 |
    41	| Sub-Mariner | 1/2 |
    42	| Techno-Organic Virus | 2/? (원형 아트) |
    43	
    44	> 주의: 기본 **Death**, 기본 **Carnage**, 기본 **Enchantress**, 기본 **Storm**, **Zombie Scarlet Witch**는 위 카드들과 다른 카드이므로 보유한 것으로 간주.
    45	> 이름 대조 (2026-11-14, SnapVault 카드 DB): 캡처의 "Storm (부제 있는 변형판) 3/1" = **Storm Horseman of Famine**, "Kang the Conqueror" = 게임 데이터상 **Kang** (3/5).
    46	
    47	---
    48	
    49	## 메타 덱 30선 기준 사용 가능 여부 (meta-2026-11-14.md v2 번호)
    50	
    51	> v3부터 페이지가 이 판단을 자동으로 계산함 (랭크 7일 100판 미만 덱 제외, 미보유 덱은 대체 예측). 아래 표는 v2 시점 기록.
    52	> v3 결과(2026-11-14): 바로 사용 11덱 · 내 카드로 대체 예측 5덱 · 대체 불가(엔진 카드 미보유) 12덱. #10·13·16·17·25·27·30은 랭크 7일 100판 미만으로 제외.
    53	
    54	### ✅ 지금 바로 사용 가능 (미보유 0장) — 13덱 + 참고 2덱
    55	| # | 덱 | 티어 |
    56	|---|---|---|
    57	| 1 | Zombie Galacti / Shuri / Wong | **S** |
    58	| 7 | High Evolutionary | A |
    59	| 8 | Fantomex / Zombie Captain Marvel / Shadow King | A |
    60	| 12 | Zombie Galacti / Arthur / Stick | B |
    61	| 14 | Spider-Ham | B |
    62	| 18 | Patriot — Onslaught / Ultron / Blue Marvel | C |
    63	| 24 | Thor | UT 단독 |
    64	| 25 | Destroy (Death / Knull) | UT 단독 |
    65	| 26 | Silver Surfer | UT 단독 |
    66	| 27 | Galactus (두 변형 모두) | UT 단독 |
    67	| 28 | Living Tribunal | UT 단독 |
    68	| 29 | Mister Negative | UT 단독 |
    69	| 30 | Discard | UT 단독 |
    70	| 참고 | Sandstorm Patriot / Fantomex·Omega Sentinel | - |
    71	
    72	### ⚠️ 1장 미보유 — 대체 카드 검토 필요
    73	| # | 덱 | 티어 | 미보유 | 메모 |
    74	|---|---|---|---|---|
    75	| 4 | Fin Fang Foom / Gorr — Domino형 | **S** | Anti-Polar Magneto | 덱의 엔진 → 사실상 대체 불가 |
    76	| 5 | Stardust / GHoD — Sasquatch형 | **S** | Scarlet Witch Queen of Chaos | 생성 카드(Skill) 공급원 대체 필요 |
    77	| 10 | Zombie Horde — WBN / Web Sling형 | A | Scarlet Witch Queen of Chaos | Skill 생성 핵심 축 중 하나 → 약화 큼 |
    78	| 11 | Zombie Horde — Luke Cage형 | A | Scarlet Witch Queen of Chaos | 〃 |
    79	| 13 | Stardust / GHoD — Thanos FF형 | B | Scarlet Witch Queen of Chaos | 생성 카드 공급원 대체 필요 |
    80	
    81	### ❌ 핵심 2장 이상 미보유 — 현재 비추천
    82	| # | 덱 | 미보유 |
    83	|---|---|---|
    84	| 2 | APM / Arthur — Lancelot·Galacta형 | Captain Britain, Lancelot, APM |
    85	| 3 | APM / Doom — Rogue Scion형 | Captain Britain, Rogue Scion, APM |
    86	| 6 | Zombie Horde — Zombie Blade형 | Zombie Blade, SW Queen of Chaos |
    87	| 9 | Stardust / GHoD — Kluh형 | SW Queen of Chaos, Kluh |
    88	| 15 | Zombie Horde — Merlin형 | Merlin, Zombie Blade, SW Queen of Chaos |
    89	| 16 | Merlin 생성 카드 덱 | Merlin, SW Queen of Chaos |
    90	| 17 | Kitty Pryde | Merlin, SW Queen of Chaos |
    91	| 19 | APM / Jubilee형 | Captain Britain, APM (+ Lancelot 빌드면 Lancelot) |
    92	| 20 | Fin Fang Foom / Gorr — Zabu형 | Captain Britain, APM |
    93	| 21 | Zabu / Spider-Man BND / Superior Iron Man | Captain Britain, Lancelot |
    94	| 22 | Vampire Deacon Frost | Deacon Frost, Vampire Enchantress, Zombie Blade, SW QoC, APM (5장) |
    95	| 23 | Arthur / Doom — Moondragon형 | Moondragon, APM |
    96	
    97	---
    98	
    99	## 획득 우선순위 (메타 덱 30선에 들어가는 빈도 기준)
   100	
   101	| 순위 | 카드 | 들어가는 덱 | 얻으면 바로 열리는 덱 |
   102	|---|---|---|---|
   103	| 1 | **Scarlet Witch Queen of Chaos** | 10덱 (#5, 6, 9, 10, 11, 13, 15, 16, 17, 22) · snap.fan A티어 | #5(S), #10, #11(A), #13(B) |
   104	| 2 | **Anti-Polar Magneto** | 7덱 (#2, 3, 4, 19, 20, 22, 23) + Quicksilver · 시즌 최대 아키타입 | #4 FFF Domino형 (S) |
   105	| 3 | **Captain Britain** | 5덱 (#2, 3, 19, 20, 21) + Created Cards · snap.fan A티어, 11/12 버프 | APM과 함께 얻으면 #19(Captain Marvel 빌드), #20 |
   106	| 4 | Zombie Blade | 3덱 (#6, 15, 22) | SW QoC와 함께 얻으면 #6 (A) |
   107	| 4 | Lancelot | 3덱 (#2, 19 Lancelot 빌드, 21) | APM·Captain Britain과 함께 얻으면 #2(S), #21 |
   108	| 4 | Merlin of Avalon | 3덱 (#15, 16, 17) | SW QoC와 함께 얻으면 #16, #17 |
   109	| - | Rogue Scion / Kluh / Moondragon / Deacon Frost / Vampire Enchantress | 1~2덱 | 우선순위 낮음 |
   110	| - | Aunt May, Boomerang, Death FF, Ezekiel Sims, FN Carnage, Jack Flag, Kang, Mary Jane, Storm, Sub-Mariner, Techno-Organic Virus, Zombie Black Cat, Zombie Venom | 메타 30선에 없음 | 현재 메타 기준 후순위 (Kang은 11/12 버프 — 추후 재확인) |
   111	
   112	**조합 효과**: SW QoC + APM 두 장이면 바로 쓸 수 있는 덱(미보유 0장)이 13개 → 18개(#4, 5, 10, 11, 13 추가). 1장만 빠지는 덱도 7개(#6, 9, 16, 17, 19 Captain Marvel 빌드, 20, 23)로 늘어남.

hook: PostToolUse
hook: PostToolUse Completed
codex
현재 캐시에서는 플렉스 빌드와 100판 기준 제외가 의도대로 적용됩니다. 예측 쪽은 여러 미보유 카드를 각각 검사한 뒤 조합 전체의 근거 없이 통과시키는 부분과, 표본 부족을 “핵심 카드라 대체 불가”로 단정하는 문구가 보입니다. 수치와 재현 사례를 추가로 확인하겠습니다.
hook: PreToolUse
hook: PreToolUse Completed
web search: 
web search: https://scikit-learn.org/stable/modules/linear_model.html#ridge-regression-and-classification
hook: PostToolUse
hook: PostToolUse Completed
hook: PreToolUse
hook: PreToolUse Completed
exec
/bin/zsh -lc "python3 -B - <<'PY'
import importlib.util, json, pathlib, sys, time
spec=importlib.util.spec_from_file_location('bd','tools/build_data.py'); m=importlib.util.module_from_spec(spec); spec.loader.exec_module(m)
old=pathlib.Path.write_text
captured={}
def capture(p,s,*a,**k):
 if p.name"'!='"'data.js': raise AssertionError(p)
 captured['out']=s
 return len(s)
pathlib.Path.write_text=capture
start=time.monotonic(); m.main(); print('seconds',round(time.monotonic()-start,3))
current=(m.ROOT/'data.js').read_text()
new=json.loads(captured['out'].split('window.SNAP_DATA = ',1)[1].rsplit(';',1)[0]); old_data=json.loads(current.split('window.SNAP_DATA = ',1)[1].rsplit(';',1)[0])
print('Regeneration semantically equal:',new==old_data)
for d in new['decks']:
 for b in d['builds']:
  if b.get('pred',{}).get('ok'):
   prev=next(x for x in old_data['decks'] if x['name']==d['name'])
   pb=next(x for x in prev['builds'] if x['label']==b['label'])
   if b['pred']"'!=pb['"'pred']: print('PRED DIFF',d['name'],b['label'],pb['pred'],b['pred'])
PY" in /Users/mac_al03241630/Project/marvelsnap
 succeeded in 132ms:
meta-2026-11-14.md: 표시 덱 23개 (+참고 5), 제외 9개, 예측 7빌드 / 예측 불가 12빌드, 카드 172장 -> /Users/mac_al03241630/Project/marvelsnap/data.js
  제외: #10 Zombie Horde — Werewolf By Night / Web Sling형 (91판)
  제외: #13 Stardust / Gambit HoD — Thanos Fractured Frontier형 (35판)
  제외: #16 Merlin of Avalon 생성 카드 덱 (0판)
  제외: #17 Kitty Pryde (0판)
  제외: #25 Destroy (Death / Knull) (34판)
  제외: #27 Galactus (Destroyer) (62판)
  제외: #30 Discard (Apocalypse / Dracula) (77판)
  제외: #None Fantomex / Omega Sentinel (72판)
  제외: #None Created Cards (Quinjet / Mother Askani) (46판)
seconds 0.189
Regeneration semantically equal: True

hook: PostToolUse
hook: PostToolUse Completed
hook: PreToolUse
hook: PreToolUse Completed
exec
/bin/zsh -lc "python3 -B - <<'PY'
import importlib.util,json,pathlib,math
spec=importlib.util.spec_from_file_location('bd','tools/build_data.py'); m=importlib.util.module_from_spec(spec); spec.loader.exec_module(m)
d=json.loads(pathlib.Path('data.js').read_text().split('window.SNAP_DATA = ',1)[1].rsplit(';',1)[0]); c,r=m.load_cache(); db=[{'set':frozenset(x['cardIds']),'stats':x['stats'],'players':x['players']} for x in r['decks']]
groups={}
for deck in d['decks']:
 for b in deck['builds']:
  p=b.get('pred',{})
  if not p.get('ok'): continue
  S=set(b['ids']); missing=set(b['miss']); arch=[x for x in db if len(x['set']&S)>=8]
  joint=[x for x in arch if not (x['set']&missing)]
  subs={x['in'] for x in p['swaps']}; paired=[x for x in joint if subs<=x['set']]
  rows=[(x['set'],x['stats']['wins']/x['stats']['totalGames'],x['stats']['totalGames']*(len(x['set']&S)/12)**3) for x in db if len(x['set']&S)>=6]
  beta150=m.ridge_effects(rows); beta2000=m.ridge_effects(rows,sweeps=2000)
  delta=lambda be:100*sum(be[x['in']]-be[x['out']] for x in p['swaps'])
  print(deck['no'],b['label'],'joint_missing_free=',sum(x['stats']['totalGames'] for x in joint),'all_chosen_subs=',sum(x['stats']['totalGames'] for x in paired),'rows/games=',len(rows),sum(x[2] for x in rows),'rawDelta150/2000=',round(delta(beta150),6),round(delta(beta2000),6),'maxBetaDiff_pp=',round(100*max(abs(beta150[k]-beta2000[k]) for k in beta150),6))
  groups.setdefault(tuple(sorted(p['ids'])),[]).append((deck['no'],p['wr']))
print('Identical proposed deck predictions:',[v for v in groups.values() if len(v)>1])
print('One-player cache rows',sum(x.get('players')==1 for x in db))
for deck in d['decks']:
 for b in deck['builds']:
  if deck['no']==11:
   g=b['stats']['games']; w=b['stats']['wins']; pp=w/g; z=1.96; den=1+z*z/g; mu=(pp+z*z/(2*g))/den; h=z*math.sqrt(pp*(1-pp)/g+z*z/(4*g*g))/den
   print('Deck11 Wilson95',100*(mu-h),100*(mu+h),'players',next(x['players'] for x in db if x['set']==set(b['ids'])))
PY" in /Users/mac_al03241630/Project/marvelsnap
 succeeded in 1975ms:
6 None joint_missing_free= 104 all_chosen_subs= 12 rows/games= 144 3522.8350694444434 rawDelta150/2000= -1.787104 -1.786741 maxBetaDiff_pp= 0.011825
9 Maria Hill 빌드 joint_missing_free= 26 all_chosen_subs= 26 rows/games= 91 3477.197916666666 rawDelta150/2000= 0.586869 0.595585 maxBetaDiff_pp= 0.010079
9 Deafening Chord 빌드 joint_missing_free= 26 all_chosen_subs= 0 rows/games= 87 3597.611689814815 rawDelta150/2000= -0.172418 -0.16665 maxBetaDiff_pp= 0.005887
11 None joint_missing_free= 238 all_chosen_subs= 123 rows/games= 144 2956.402199074073 rawDelta150/2000= -1.20778 -1.208249 maxBetaDiff_pp= 0.007317
15 None joint_missing_free= 81 all_chosen_subs= 12 rows/games= 149 3443.727430555557 rawDelta150/2000= -0.634743 -0.635412 maxBetaDiff_pp= 0.00762
19 Lancelot 빌드 joint_missing_free= 0 all_chosen_subs= 0 rows/games= 273 4129.163773148146 rawDelta150/2000= -2.368532 -2.365513 maxBetaDiff_pp= 0.005811
19 Captain Marvel 빌드 joint_missing_free= 0 all_chosen_subs= 0 rows/games= 281 4206.161458333332 rawDelta150/2000= -2.145 -2.144179 maxBetaDiff_pp= 0.002172
Identical proposed deck predictions: [[(6, 56.6), (15, 57.1)]]
One-player cache rows 1869
Deck11 Wilson95 54.87826871568701 72.59386921925898 players 5

hook: PostToolUse
hook: PostToolUse Completed
hook: PreToolUse
hook: PreToolUse Completed
exec
/bin/zsh -lc "node - <<'JS'
const fs = require('fs');const vm=require('vm');
const data={window:{}};vm.runInNewContext(fs.readFileSync('data.js','utf8'),data);let D=data.window.SNAP_DATA;
const eff=b=>"'!b.miss.length?{wr:b.stats.wr,kind:'"'real'}:b.pred&&b.pred.ok?{wr:b.pred.wr,kind:'pred'}:{wr:null,kind:'none'};
for(let d of D.decks){ d.builds.forEach(b=>b._eff=eff(b));d.builds.sort((x,y)=>(y._eff.wr??-1)-(x._eff.wr??-1)||y.stats.wr-x.stats.wr);d._eff=d.builds[0]._eff;d._raw=Math.max(...d.builds.map(b=>b.stats.wr));d._status=d.builds.some(b=>"'!b.miss.length)?'"'ok':d.builds.some(b=>b._eff.kind==='pred')?'pred':'none';d._miss=d.builds.map(b=>b.miss).sort((x,y)=>x.length-y.length)[0]; }
console.log('Misaligned build badge',D.decks.filter(d=>d._miss.length"'!==d.builds[0].miss.length).map(d=>({name:d.name,badge:d._miss,top:d.builds[0].miss})));
console.log('"'Raw sort top build mismatch',D.decks.filter(d=>d._raw"'!==d.builds[0].stats.wr).map(d=>({name:d.name,sort:d._raw,top:d.builds[0].stats.wr})));
console.log('"'Code: empty/nonascii/comma codes',Object.entries(D.cards).filter(([id,c])=>typeof c.code"'!=='"'string'||"'!/''^['"\\x00-\\x7f]+"'$/.test(c.code)||c.code.includes('"',')));
const h=fs.readFileSync('index.html','utf8');const js=h.match(/<script>\\s*([\\s\\S]+?)<\\/script>/)[1];new vm.Script(js);console.log('Inline JS syntax OK');
JS" in /Users/mac_al03241630/Project/marvelsnap
 succeeded in 0ms:
Misaligned build badge []
Raw sort top build mismatch [
  {
    name: 'Anti-Polar Magneto / Jubilee형 — Lancelot 또는 Captain Marvel',
    sort: 57.4,
    top: 57.3
  }
]
Code: empty/nonascii/comma codes []
Inline JS syntax OK

hook: PostToolUse
hook: PostToolUse Completed
hook: PreToolUse
hook: PreToolUse Completed
exec
/bin/zsh -lc "python3 -B - <<'PY'
import subprocess,sys,json
src=r'''
import importlib.util,pathlib,json,contextlib,io
s=importlib.util.spec_from_file_location('bd','tools/build_data.py'); m=importlib.util.module_from_spec(s); s.loader.exec_module(m)
out={}
def capture(p,t,*a,**k):
 out['text']=t
 return len(t)
pathlib.Path.write_text=capture
with contextlib.redirect_stdout(io.StringIO()): m.main()
d=json.loads(out['text'].split('window.SNAP_DATA = ',1)[1].rsplit(';',1)[0])
print(json.dumps([(x['no'],b['label'],b['pred']['wr'],b['pred']['rawDelta'],[(s['out'],s['in']) for s in b['pred']['swaps']]) for x in d['decks'] for b in x['builds'] if b.get('pred',{}).get('ok')]))
'''
import os
for seed in ['0','1','2','3','4','5']:
 p=subprocess.run([sys.executable,'-B','-c',src],env={**os.environ,'PYTHONHASHSEED':seed},capture_output=True,text=True,check=True)
 print('seed',seed,p.stdout.strip())
PY" in /Users/mac_al03241630/Project/marvelsnap
 succeeded in 1199ms:
seed 0 [[6, null, 56.6, -1.8, [["ScarletWitchQueenOfChaos", "AbsorbingMan"], ["ZombieBlade", "WerewolfByNight"]]], [9, "Maria Hill \ube4c\ub4dc", 58.8, 0.6, [["Kluh", "DeafeningChord"], ["ScarletWitchQueenOfChaos", "Merlin"]]], [9, "Deafening Chord \ube4c\ub4dc", 59.1, -0.2, [["Kluh", "ThanosFracturedFrontier"], ["ScarletWitchQueenOfChaos", "Merlin"]]], [11, null, 63.0, -1.2, [["ScarletWitchQueenOfChaos", "AbsorbingMan"]]], [15, null, 57.1, -0.6, [["MerlinOfAvalon", "ZombieMisterFantastic"], ["ScarletWitchQueenOfChaos", "AbsorbingMan"], ["ZombieBlade", "WerewolfByNight"]]], [19, "Lancelot \ube4c\ub4dc", 55.0, -2.4, [["AntiPolarMagneto", "SuperiorIronMan"], ["CaptainBritain", "Psylocke"], ["Lancelot", "CaptainMarvel"]]], [19, "Captain Marvel \ube4c\ub4dc", 55.2, -2.1, [["AntiPolarMagneto", "Isca"], ["CaptainBritain", "Psylocke"]]]]
seed 1 [[6, null, 56.6, -1.8, [["ScarletWitchQueenOfChaos", "AbsorbingMan"], ["ZombieBlade", "WerewolfByNight"]]], [9, "Maria Hill \ube4c\ub4dc", 58.8, 0.7, [["Kluh", "DeafeningChord"], ["ScarletWitchQueenOfChaos", "Merlin"]]], [9, "Deafening Chord \ube4c\ub4dc", 59.2, -0.1, [["Kluh", "ThanosFracturedFrontier"], ["ScarletWitchQueenOfChaos", "Merlin"]]], [11, null, 63.0, -1.2, [["ScarletWitchQueenOfChaos", "AbsorbingMan"]]], [15, null, 57.1, -0.6, [["MerlinOfAvalon", "ZombieMisterFantastic"], ["ScarletWitchQueenOfChaos", "AbsorbingMan"], ["ZombieBlade", "WerewolfByNight"]]], [19, "Lancelot \ube4c\ub4dc", 55.0, -2.4, [["AntiPolarMagneto", "SuperiorIronMan"], ["CaptainBritain", "Psylocke"], ["Lancelot", "CaptainMarvel"]]], [19, "Captain Marvel \ube4c\ub4dc", 55.2, -2.1, [["AntiPolarMagneto", "Isca"], ["CaptainBritain", "Psylocke"]]]]
seed 2 [[6, null, 56.6, -1.8, [["ScarletWitchQueenOfChaos", "AbsorbingMan"], ["ZombieBlade", "WerewolfByNight"]]], [9, "Maria Hill \ube4c\ub4dc", 58.8, 0.6, [["Kluh", "DeafeningChord"], ["ScarletWitchQueenOfChaos", "Merlin"]]], [9, "Deafening Chord \ube4c\ub4dc", 59.1, -0.2, [["Kluh", "ThanosFracturedFrontier"], ["ScarletWitchQueenOfChaos", "Merlin"]]], [11, null, 63.0, -1.2, [["ScarletWitchQueenOfChaos", "AbsorbingMan"]]], [15, null, 57.1, -0.6, [["MerlinOfAvalon", "ZombieMisterFantastic"], ["ScarletWitchQueenOfChaos", "AbsorbingMan"], ["ZombieBlade", "WerewolfByNight"]]], [19, "Lancelot \ube4c\ub4dc", 55.0, -2.4, [["AntiPolarMagneto", "SuperiorIronMan"], ["CaptainBritain", "Psylocke"], ["Lancelot", "CaptainMarvel"]]], [19, "Captain Marvel \ube4c\ub4dc", 55.2, -2.1, [["AntiPolarMagneto", "Isca"], ["CaptainBritain", "Psylocke"]]]]
seed 3 [[6, null, 56.6, -1.8, [["ScarletWitchQueenOfChaos", "AbsorbingMan"], ["ZombieBlade", "WerewolfByNight"]]], [9, "Maria Hill \ube4c\ub4dc", 58.8, 0.6, [["Kluh", "DeafeningChord"], ["ScarletWitchQueenOfChaos", "Merlin"]]], [9, "Deafening Chord \ube4c\ub4dc", 59.2, -0.1, [["Kluh", "ThanosFracturedFrontier"], ["ScarletWitchQueenOfChaos", "Merlin"]]], [11, null, 63.0, -1.2, [["ScarletWitchQueenOfChaos", "AbsorbingMan"]]], [15, null, 57.1, -0.6, [["MerlinOfAvalon", "ZombieMisterFantastic"], ["ScarletWitchQueenOfChaos", "AbsorbingMan"], ["ZombieBlade", "WerewolfByNight"]]], [19, "Lancelot \ube4c\ub4dc", 55.0, -2.4, [["AntiPolarMagneto", "SuperiorIronMan"], ["CaptainBritain", "Psylocke"], ["Lancelot", "CaptainMarvel"]]], [19, "Captain Marvel \ube4c\ub4dc", 55.2, -2.1, [["AntiPolarMagneto", "Isca"], ["CaptainBritain", "Psylocke"]]]]
seed 4 [[6, null, 56.6, -1.8, [["ScarletWitchQueenOfChaos", "AbsorbingMan"], ["ZombieBlade", "WerewolfByNight"]]], [9, "Maria Hill \ube4c\ub4dc", 58.8, 0.6, [["Kluh", "DeafeningChord"], ["ScarletWitchQueenOfChaos", "Merlin"]]], [9, "Deafening Chord \ube4c\ub4dc", 59.1, -0.2, [["Kluh", "ThanosFracturedFrontier"], ["ScarletWitchQueenOfChaos", "Merlin"]]], [11, null, 63.0, -1.2, [["ScarletWitchQueenOfChaos", "AbsorbingMan"]]], [15, null, 57.1, -0.6, [["MerlinOfAvalon", "ZombieMisterFantastic"], ["ScarletWitchQueenOfChaos", "AbsorbingMan"], ["ZombieBlade", "WerewolfByNight"]]], [19, "Lancelot \ube4c\ub4dc", 55.0, -2.4, [["AntiPolarMagneto", "SuperiorIronMan"], ["CaptainBritain", "Psylocke"], ["Lancelot", "CaptainMarvel"]]], [19, "Captain Marvel \ube4c\ub4dc", 55.2, -2.1, [["AntiPolarMagneto", "Isca"], ["CaptainBritain", "Psylocke"]]]]
seed 5 [[6, null, 56.6, -1.8, [["ScarletWitchQueenOfChaos", "AbsorbingMan"], ["ZombieBlade", "WerewolfByNight"]]], [9, "Maria Hill \ube4c\ub4dc", 58.8, 0.6, [["Kluh", "DeafeningChord"], ["ScarletWitchQueenOfChaos", "Merlin"]]], [9, "Deafening Chord \ube4c\ub4dc", 59.2, -0.1, [["Kluh", "ThanosFracturedFrontier"], ["ScarletWitchQueenOfChaos", "Merlin"]]], [11, null, 63.0, -1.2, [["ScarletWitchQueenOfChaos", "AbsorbingMan"]]], [15, null, 57.1, -0.6, [["MerlinOfAvalon", "ZombieMisterFantastic"], ["ScarletWitchQueenOfChaos", "AbsorbingMan"], ["ZombieBlade", "WerewolfByNight"]]], [19, "Lancelot \ube4c\ub4dc", 55.0, -2.4, [["AntiPolarMagneto", "SuperiorIronMan"], ["CaptainBritain", "Psylocke"], ["Lancelot", "CaptainMarvel"]]], [19, "Captain Marvel \ube4c\ub4dc", 55.2, -2.1, [["AntiPolarMagneto", "Isca"], ["CaptainBritain", "Psylocke"]]]]

hook: PostToolUse
hook: PostToolUse Completed
hook: PreToolUse
hook: PreToolUse Completed
exec
/bin/zsh -lc "node - <<'JS'
for(const x of ['jsdom','playwright','puppeteer','linkedom']) {try {console.log(x,require.resolve(x));}catch{}}
JS" in /Users/mac_al03241630/Project/marvelsnap
 succeeded in 0ms:
hook: PostToolUse
hook: PostToolUse Completed
codex
캐시에서 #19는 미보유 카드를 모두 뺀 같은 계열 전적이 0판인데도 예측이 생성됩니다. 같은 대체 덱이 원본에 따라 56.6%와 57.1%로 표시되는 사례도 확인했습니다. 또 동일 입력을 별도 프로세스에서 재생성하면 #9 예측이 59.1% 또는 59.2%로 달라져, 회귀의 수렴·순서 문제를 확인하고 있습니다.
hook: PreToolUse
hook: PreToolUse Completed
exec
/bin/zsh -lc "python3 -B - <<'PY'
import importlib.util
s=importlib.util.spec_from_file_location('bd','tools/build_data.py');m=importlib.util.module_from_spec(s);s.loader.exec_module(m)
S=set([f'C{i}' for i in range(10)]+['A','B']); core=S-{'A','B'}
def row(cards,g):return {'set':frozenset(cards),'stats':{'wins':g//2,'totalGames':g,'cubeGames':g,'totalCubes':0}}
db=[row(S,100),row(core|{'B','X'},200),row(core|{'B','Y'},150),row(core|{'A','X'},100)]
print('Greedy false nosub:',m.predict(list(S),50,{'A','B'},db))
print('B-absent games:',sum(x['stats']['totalGames'] for x in db if 'B' not in x['set']))
slots=[[f'C{i}'] for i in range(10)]+[['A','B'],['A','B']]
class Res:
 def id_of(self,n):return n
try: print('Overlapping flex',m.build_deck({'name':'overlapping flex','lists':[{'slots':slots,'label':None}]},Res(),set(),{},[]))
except SystemExit as e: print('Overlapping flex abort:',e)
PY" in /Users/mac_al03241630/Project/marvelsnap
 succeeded in 0ms:
Greedy false nosub: {'ok': False, 'reason': 'nosub', 'blockers': [{'id': 'B', 'without': 0}], 'archLists': 4, 'archGames': 550}
B-absent games: 100
Overlapping flex abort: [오류] overlapping flex 중복 카드

hook: PostToolUse
hook: PostToolUse Completed
hook: PreToolUse
hook: PreToolUse Completed
exec
/bin/zsh -lc "node - <<'JS'
const fs=require('fs'),vm=require('vm');
const raw=fs.readFileSync('index.html','utf8').match(/<script>\\s*([\\s\\S]+?)<\\/script>/)[1];
const data={window:{}};vm.runInNewContext(fs.readFileSync('data.js','utf8'),data);
const sourceData=JSON.parse(JSON.stringify(data.window.SNAP_DATA));
function run(D,state={},execSuccess=false){
 const els={};const added=[];
 function element(){return {textContent:'',innerHTML:'',children:[],dataset:{},events:{},classList:{add(){},remove(){}},setAttribute(){},getAttribute(){return null},querySelectorAll(){return []},addEventListener(k,fn){this.events[k]=fn},appendChild(x){this.children.push(x)},remove(){},select(){},style:{}};}
 const document={documentElement:element(),body:element(),getElementById(id){return els[id]??=element()},createElement(){return element()}};
 const ctx={window:{SNAP_DATA:D,isSecureContext:false},document,navigator:{},matchMedia(){return {matches:false}},localStorage:{getItem(key){return key==='snap-filters-v3'?JSON.stringify(state):null},setItem(){}},btoa:s=>Buffer.from(s,'latin1').toString('base64'),setTimeout(){return 1},clearTimeout(){},console};
 document.execCommand=()=>execSuccess;
 vm.runInNewContext(raw.replace(/\\}\\)\\(\\);\\s*"'$/,'"'window.test={esc,copy,deckCode,fig,predHTML};})();'),ctx);
 return {ctx,els};
}
let {ctx,els}=run(JSON.parse(JSON.stringify(sourceData)));
console.log('Initial render:',els.countLine.textContent,'articles:',(els.deckList.innerHTML.match(/<article /g)||[]).length);
for(const own of ['ok','pred','none']) {let r=run(JSON.parse(JSON.stringify(sourceData)),{own});console.log('Filter',own,r.els.countLine.textContent);}
const b=sourceData.decks.find(d=>d.no===19).builds[0];
const orig={hidden:false},alt={hidden:true};const box={querySelector(q){return q.includes('orig')?orig:alt}};
const btn={dataset:{act:'view'},closest(){return box}};els.deckList.events.click({target:{closest(){return btn}}});
console.log('Toggle to alternative:',{origHidden:orig.hidden,altHidden:alt.hidden,label:btn.textContent});
els.deckList.events.click({target:{closest(){return btn}}});console.log('Toggle back:',{origHidden:orig.hidden,altHidden:alt.hidden,label:btn.textContent});
console.log('Deck code roundtrip:',Buffer.from(ctx.window.test.deckCode(b.ids),'base64').toString()===b.ids.map(id=>sourceData.cards[id].code).join(','));
ctx.window.test.copy('payload','SUCCESS');console.log('execCommand false toast:',els.toast.textContent);
console.log('esc payload:',ctx.window.test.esc('\"\\'><img src=x onerror=alert(1)> &'));
const bad='evil\" onmouseover=\"alert(1)';const badD=JSON.parse(JSON.stringify(sourceData));badD.cards[bad]={name:'test',cost:1,power:1,code:'X'};badD.decks[0].builds[0].ids[0]=bad;
let badR=run(badD);console.log('Raw ID HTML injection:',badR.els.deckList.innerHTML.includes('data-ids=\"evil\" onmouseover=\"alert(1),'));
const miss=sourceData.decks.find(d=>d.no===11).builds[0].miss[0];console.log('nosub HTML:',ctx.window.test.predHTML({pred:{ok:false,reason:'nosub',blockers:[{id:miss,without:0}]}}));
JS" in /Users/mac_al03241630/Project/marvelsnap
 succeeded in 0ms:
Initial render: 28개 덱 표시 articles: 28
Filter ok 11개 덱 표시
Filter pred 5개 덱 표시
Filter none 12개 덱 표시
Toggle to alternative: { origHidden: true, altHidden: false, label: '원본 덱 보기' }
Toggle back: { origHidden: false, altHidden: true, label: '대체 덱 보기' }
Deck code roundtrip: true
execCommand false toast: SUCCESS
esc payload: &quot;'&gt;&lt;img src=x onerror=alert(1)&gt; &amp;
Raw ID HTML injection: true
nosub HTML: <div class="pred no">예측 불가 — <b>Scarlet Witch Queen of Chaos</b> 없이 플레이된 같은 계열 판이 0판뿐. 덱의 핵심 카드라 내 카드로 바꾼 버전의 근거가 없습니다.</div>

hook: PostToolUse
hook: PostToolUse Completed
hook: PreToolUse
hook: PreToolUse Completed
exec
/bin/zsh -lc "python3 -B - <<'PY'
import importlib.util,subprocess,sys,os,json
script=r'''
import importlib.util
s=importlib.util.spec_from_file_location('bd','tools/build_data.py');m=importlib.util.module_from_spec(s);s.loader.exec_module(m)
c,r=m.load_cache();res=m.Resolver(c);decks,refs=m.parse_meta(m.NOTES/'meta-2026-11-14.md');target=next(d for d in decks if d['no']==9);names=[o[-1] for o in target['lists'][0]['slots']];S=set(map(res.id_of,names));db=[{'set':frozenset(x['cardIds']),'stats':x['stats']} for x in r['decks']];rows=[(x['set'],x['stats']['wins']/x['stats']['totalGames'],x['stats']['totalGames']*(len(x['set']&S)/12)**3) for x in db if len(x['set']&S)>=6]
for n in [150,2000]:
 b=m.ridge_effects(rows,sweeps=n);delta=100*(b['ThanosFracturedFrontier']-b['Kluh']+b['Merlin']-b['ScarletWitchQueenOfChaos']);print(n,round(delta,8))
'''
for seed in ['0','1']:
 p=subprocess.run([sys.executable,'-B','-c',script],env={**os.environ,'PYTHONHASHSEED':seed},check=True,text=True,capture_output=True);print('seed',seed,p.stdout.strip())
PY" in /Users/mac_al03241630/Project/marvelsnap
 succeeded in 361ms:
seed 0 150 -0.16464167
2000 -0.1666503
seed 1 150 -0.07910799
2000 -0.1666503

hook: PostToolUse
hook: PostToolUse Completed
hook: PreToolUse
hook: PreToolUse Completed
exec
/bin/zsh -lc 'git status --short' in /Users/mac_al03241630/Project/marvelsnap
 succeeded in 0ms:
 M .gitignore
 M README.md
 M data.js
 M index.html
 M notes/collection.md
 M notes/meta-2026-11-14.md
 M tools/build_data.py
?? tools/fetch_sv.py

hook: PostToolUse
hook: PostToolUse Completed
hook: PreToolUse
hook: PreToolUse Completed
web search: 
web search: https://scikit-learn.org/stable/auto_examples/inspection/plot_linear_model_coefficient_interpretation.html
hook: PostToolUse
hook: PostToolUse Completed
codex
파일은 수정하지 않았습니다. 생성 출력을 메모리로 받아 재현한 결과이며, 심각도순입니다.

1. **[높음] 여러 카드의 동시 교체 근거를 확인하지 않습니다.** [build_data.py:227](/Users/mac_al03241630/Project/marvelsnap/tools/build_data.py:227)  
   카드별 부재 표본만 검사해, #19는 **미보유 카드를 모두 뺀 같은 계열 전적이 0판**인데도 55.0%·55.2%를 예측합니다. **수정:** 모든 미보유 카드가 동시에 없는 표본에도 100판 기준을 적용하고, 선택한 대체 카드의 동시 사용 표본도 확인하세요.

2. **[중간] 원본 승률의 잡음이 그대로 “내 기대 승률”이 됩니다.** [build_data.py:261](/Users/mac_al03241630/Project/marvelsnap/tools/build_data.py:261), [index.html:437](/Users/mac_al03241630/Project/marvelsnap/index.html:437)  
   #11은 원본 109판을 기준으로 대체 승률 63.0%가 나오며, **동일한 대체 12장도 #6에서는 56.6%, #15에서는 57.1%**입니다. 플레이어·랭크 차이도 통제하지 않아 회귀계수를 교체의 인과효과로 해석하기 어렵습니다. [계수 해석 주의사항](https://scikit-learn.org/stable/auto_examples/inspection/plot_linear_model_coefficient_interpretation.html#interpreting-coefficients-being-cautious-about-causality)  
   **수정:** 원본 승률을 계열 평균으로 축소하고 관측 신뢰구간을 표시하세요. 문구는 “트래커 기반 대체 추정”으로 바꾸고, 상한 적용 결과를 “원본과 비슷”이라고 단정하지 마세요.

3. **[중간] 릿지가 수렴 전에 종료되어 재생성 결과가 달라집니다.** [build_data.py:195](/Users/mac_al03241630/Project/marvelsnap/tools/build_data.py:195)  
   `set` 순회 순서와 고정 150회 때문에 동일 캐시에서도 #9 예측이 **59.1% 또는 59.2%**로 달라집니다. 2,000회에서는 확인한 두 시드가 같은 값으로 수렴했습니다. **수정:** 카드 순서를 정렬하고 계수·절편 변화량 기준으로 종료하세요. 대체 후보 동률에도 명시적인 정렬 기준이 필요합니다.

4. **[중간] 탐욕적 대체 선택이 가능한 조합을 놓칩니다.** [build_data.py:242](/Users/mac_al03241630/Project/marvelsnap/tools/build_data.py:242)  
   A의 후보가 X·Y이고 B의 후보가 X뿐이면, A→X를 먼저 선택하면서 `nosub`가 됩니다. A→Y, B→X는 가능한데도 실패하는 사례를 재현했습니다. **수정:** 카드별 후보를 먼저 모은 뒤, 중복 없는 배정을 작은 백트래킹으로 찾으세요.

5. **[중간] 데이터 부족을 “핵심 카드라 대체 불가”로 과장합니다.** [build_data.py:251](/Users/mac_al03241630/Project/marvelsnap/tools/build_data.py:251), [index.html:489](/Users/mac_al03241630/Project/marvelsnap/index.html:489)  
   부재 표본 부족은 엔진 카드라는 증거가 아닙니다. 특히 `nosub`는 실제 부재 표본이 있어도 `without: 0`을 넣어 잘못 표시합니다. **수정:** 실제 판수를 보존하고 `reason`별로 “부재 표본 부족”·“보유 대체 후보 부족”을 구분하세요. 필터도 “대체 불가”보다 “예측 불가”가 정확합니다.

6. **[중간] 겹치는 플렉스 선택지 하나가 전체 생성을 중단합니다.** [build_data.py:274](/Users/mac_al03241630/Project/marvelsnap/tools/build_data.py:274)  
   두 슬롯이 각각 `A 또는 B`이면 첫 중복 조합에서 종료되어 유효한 A+B 조합도 생성하지 못합니다. **수정:** 중복 카드를 가진 조합만 건너뛰고, 유효 조합이 전혀 없을 때 오류를 내세요.

7. **[낮음·조건부] `esc`를 거치지 않는 속성 삽입이 있습니다.** [index.html:506](/Users/mac_al03241630/Project/marvelsnap/index.html:506)  
   `esc` 자체는 현재 텍스트·큰따옴표 속성 문맥에서 적절합니다. 다만 `data-ids`에는 원시 ID를 넣어, API ID에 따옴표가 섞이면 속성 탈출이 가능합니다. **수정:** `esc(ids.join(","))`를 사용하고 수집 단계에서 ID 형식·숫자 필드를 검증하세요.

8. **[낮음] 복사 실패에도 성공 알림이 나옵니다.** [index.html:580](/Users/mac_al03241630/Project/marvelsnap/index.html:580)  
   `document.execCommand("copy")`가 `false`를 반환해도 `ok()`를 호출합니다. **수정:** 반환값을 검사하고 textarea 제거는 `finally`에서 처리하세요.

현재 캐시의 12장 완전 일치·100판 제외는 정상이며, Node 간이 DOM 검사에서 현재 필터·보기 토글·덱 코드 base64 왕복도 확인했습니다.
hook: Stop
hook: Stop Completed
tokens used
87,644

```

## Concise summary

Provider completed successfully. Review the raw output for details.

## Action items

- Review the response and extract decisions you want to apply.
- Capture follow-up implementation tasks if needed.
