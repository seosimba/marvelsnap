# 이벤트 모드 — 폭주 매치 (High Voltage) · 2026-11-15

> 페이지 '폭주 매치' 탭의 근거 문서. `tools/build_data.py`가 `notes/event-*.md`를 모두 읽어 `data.js`에 넣는다.
> 형식 — `## 요약`: `- 키: 값` 줄 (모드·기간·규칙·금지 카드·데이터·출처 링크). `## 덱`: `### N. 덱 이름` 아래
> `- 원본: 승률% · 판수판 · 플레이어명 · 메모`, `- 카드:` 원본 12장, `- 대체(데이터|추측): 빠지는 카드 → 넣을 카드 — 이유`, `- 메모:`.
> 원본에 미보유 카드(`unowned.md`)가 있으면 모두 대체가 있어야 하고, 넣는 카드는 보유·싫어하지 않음·이벤트 금지 아님·덱에 없음이어야 한다 (빌드 때 검사).

## 요약
- 모드: 폭주 매치 (High Voltage)
- 기간: 2026-11-14 ~ 2026-11-16 (SnapComplete 가이드는 11/16 종료, 덱·카드 페이지는 11/17 종료로 표기 — 게임 안 이벤트 화면 기준으로 확인)
- 규칙: 3턴만 진행 · 매 턴 최대 에너지가 무작위 2~5씩 늘어 쌓임 (양쪽 같음, 3턴째 6~15) · 손패 2장으로 시작해 매 턴 2장 드로우 · 구역 2곳을 이기면 승리 · 스냅·큐브 없음 (보상은 볼트)
- 금지 카드: Magik, Galactus, Black Widow, Alioth, Gambit, Shadow King, Ebony Maw, Arnim Zola, Ultron, Onslaught, Dragon Lord
- 데이터: SnapComplete 이번 이벤트 146,015판 · 21,039덱 (2026-11-15 확인, 봇 제외, 10판 이상 덱만 순위)
- 출처 링크: https://snapcomplete.com/play/ltgm/high-voltage/decks

## 고르는 기준
- 이번 이벤트 덱 승률 순위(SnapComplete 상위 8덱)에서 **미보유 카드가 적은 덱을 승률 순**으로 3개.
- 상위 8덱이 **모두 Anti-Polar Magneto(미보유)** 를 씀 → 셋 다 APM을 Doctor Doom으로 대체 (Claude 추측, `substitutes.md` #2와 같은 논리).
  - APM: 6코스트, 손의 3·4코스트 카드를 다른 두 구역에 1장씩 꺼냄 → 3턴째 큰 에너지로 판 전체를 채우는 역할.
  - Doom: 6코스트, 다른 두 구역에 5파워 DoomBot. DoomBot은 6코스트 토큰이라 Caliban 목표(4코스트 이상 아군 3장)·Mordred(+2/더 높은 코스트)·Excalibur(4코스트 이상 +2)와도 맞음.
- 원본 승률은 APM이 들어간 수치라 대체 덱은 이보다 낮을 가능성이 큼. 덱 데이터가 8개뿐이라 예측 승률은 계산하지 않음.

## 덱

### 1. FFF · Thanos FF · Caliban
- 원본: 66.0% · 5,264판 · 495명 · 이벤트 순위 2위 (표본 가장 큼)
- 카드: Grand Master, Caliban Horseman of Pestilence, Psylocke Fractured Frontier, Jubilee, Arthur Pendragon, En Sabah Nur, Captain Marvel, Iron Lad, Rogue Scion of Division, Thanos Fractured Frontier, Anti-Polar Magneto, Fin Fang Foom
- 대체(데이터): Rogue Scion of Division → Cosmic Ghost Rider — 이 카드만 바꾼 리스트가 이벤트 순위 5위 (63.3% · 114판 · 12명)
- 대체(추측): Anti-Polar Magneto → Doctor Doom — 같은 6코스트로 다른 두 구역을 채움. Doom 한 장이 DoomBot 2개까지 '4코스트 이상 아군 3장'이라 Caliban 목표가 바로 달성
- 메모: Psylocke FF로 Doom·Thanos FF·Fin Fang Foom 비용을 낮추고, Grand Master로 On Reveal 카드를 가운데로 옮겨 한 번 더 발동

### 2. Giganto · Infinaut 큰 몸통
- 원본: 62.7% · 2,213판 · 249명 · 이벤트 순위 6위
- 카드: Grand Master, Jane Foster Fractured Frontier, Mordred, Psylocke Fractured Frontier, Jubilee, Dracula, Crossbones, Blink, Anti-Polar Magneto, Giganto, The Infinaut, Fin Fang Foom
- 대체(추측): Anti-Polar Magneto → Doctor Doom — 같은 6코스트로 다른 두 구역에 5파워 DoomBot. Mordred 구역에 깔리면 DoomBot도 더 높은 코스트라 +2씩
- 메모: Jubilee(덱 맨 위 카드를 꺼냄)·Blink(방금 낸 카드를 덱의 같거나 더 비싼 카드와 교체)로 Giganto·Infinaut·Fin Fang Foom을 일찍 꺼내는 덱. Giganto는 왼쪽 구역에만, Infinaut은 지난 턴에 카드를 냈으면 못 냄

### 3. Odin · Iron Man
- 원본: 61.7% · 900판 · 132명 · 이벤트 순위 8위
- 카드: Psylocke, Mordred, Jubilee, Super-Skrull, Shang-Chi, Arthur Pendragon, Captain Marvel, Iron Man, White Tiger, Leader, Anti-Polar Magneto, Odin
- 대체(추측): Anti-Polar Magneto → Doctor Doom — 6코스트로 다른 두 구역을 채우는 역할. Odin을 Doom과 같은 구역에 나중에 내면 DoomBot을 한 번 더 깖
- 메모: Odin은 같은 구역 아군의 On Reveal(White Tiger·Leader·Doom)을 다시 발동. Iron Man 구역은 파워 2배

## 고르지 않은 상위 덱
- 이벤트 순위 1위 67.0% · 1,998판 — 미보유 3장 (Captain Britain, Lancelot, Anti-Polar Magneto)
- 이벤트 순위 3위·4위 65.0% · 516판/876판 — 미보유 3장 (Captain Britain, Lancelot, Anti-Polar Magneto)
- 이벤트 순위 7위 62.2% · 205판 — 미보유 3장 (Captain Britain, Lancelot, Anti-Polar Magneto)

## 카드 승률 상위 (이번 이벤트, 뽑았을 때 승률 · 판수)
| 카드 | 승률 | 판수 | 보유 |
|---|---|---|---|
| Caliban Horseman of Pestilence | 63.4% | 11,945 | ✓ |
| Arthur Pendragon | 63.4% | 27,585 | ✓ |
| Captain Marvel | 63.1% | 16,759 | ✓ |
| Wolverine Horseman of War | 63.0% | 7,930 | ✓ |
| En Sabah Nur | 62.7% | 16,435 | ✓ |
| Anti-Polar Magneto | 62.4% | 30,726 | ✕ |
| Lancelot | 61.2% | 11,375 | ✕ |
| Mordred | 61.0% | 20,487 | ✓ |
| Captain Britain | 60.8% | 12,879 | ✕ |
| Iron Lad | 60.4% | 26,832 | ✓ |

출처: [SnapComplete 덱](https://snapcomplete.com/play/ltgm/high-voltage/decks) · [카드](https://snapcomplete.com/play/ltgm/high-voltage/cards) · [가이드](https://snapcomplete.com/play/ltgm/high-voltage) · [공식 도움말](https://marvelsnap.helpshift.com/hc/ko/3-marvel-snap/faq/365-how-does-high-voltage-work/)
