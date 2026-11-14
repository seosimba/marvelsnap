# Marvel Snap 덱 노트

개인 덱 빌딩용 메타 정리 페이지 — https://seosimba.github.io/marvelsnap/

## 구조
- `notes/meta-YYYY-MM-DD.md` — 주간 메타 리서치 (덱 리스트·출처·티어 근거·페이지 표시 규칙)
- `notes/unowned.md` — **없는 카드** (덱은 목록에 남기고 빨간 ✕ + 내 카드로 대체 예측)
- `notes/disliked.md` — **싫어하는 카드** (들어간 덱은 순위에서 빼고 제외 이유 표시, 대체 카드로도 추천 안 함)
- `notes/substitutes.md` — **Claude 추측 대체 카드** (데이터로 예측 못 하는 덱용, 승률 없음·이유 포함)
- `tools/fetch_sv.py` — SnapVault 공개 API에서 카드 목록 + 랭크 7일 덱 통계를 `cache/`에 저장 (커밋 안 함)
- `tools/build_data.py` — 노트 + 컬렉션 + 캐시 → `data.js`
  - 덱마다 12장 검증, 플렉스 슬롯은 빌드별로 펼침
  - 빌드마다 랭크 7일 승률·판수 (12장 완전 일치), 100판 미만 제외
  - 미보유 카드가 있는 빌드는 대체 카드와 예측 승률 계산 (방법은 노트 `### 페이지 표시 규칙`)
- `index.html` + `data.js` — 페이지 (카드 이미지: Untapped.gg, 덱 코드 = 카드 코드를 쉼표로 이어 base64)

## 갱신
```bash
python3 tools/fetch_sv.py     # 랭크 7일 데이터 + 카드 출시일(Untapped) 갱신 (약 30초, 서버 부담 줄이려 페이지마다 0.5초 쉼)
python3 tools/build_data.py   # 최신 meta-*.md + unowned.md + disliked.md + cache/ → data.js
git add -A && git commit -m "..." && git push
```
