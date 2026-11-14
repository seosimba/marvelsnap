# Marvel Snap 덱 노트

개인 덱 빌딩용 메타 정리 페이지 — https://seosimba.github.io/marvelsnap/

## 구조
- `notes/meta-YYYY-MM-DD.md` — 주간 메타 리서치 (덱 리스트·출처·티어 근거)
- `notes/collection.md` — 미보유 카드 목록
- `tools/build_data.py` — 노트 → `data.js` 변환 (덱 카드 수 12장 검증 포함)
- `index.html` + `data.js` — 페이지

## 갱신
```bash
python3 tools/build_data.py   # 최신 meta-*.md + collection.md → data.js
git add -A && git commit -m "..." && git push
```
