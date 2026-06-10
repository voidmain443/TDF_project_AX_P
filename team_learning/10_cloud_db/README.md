# 10. 클라우드에 DB 만들기 — `tdfmini`를 샌드박스 VM에서 돌리기

> Part 2 시작. 지금까지(00~09) 만든 학습 크롤러 [`tdfmini/`](../tdfmini/)를 **샌드박스 VM**에서 돌려,
> **서버 안에 sqlite DB를 실제로 생성**합니다. 접속은 **ssh-keygen 키**(PuTTY 안 씀).

## 0. 접속 키 만들기 — ssh-keygen (PuTTY 불필요)
```bash
# 로컬에서 OpenSSH 키 생성 (윈도우/맥/리눅스 공통)
ssh-keygen -t ed25519 -C "<vm-user>" -f ~/.ssh/sandbox     # sandbox(+.pub) 생성
#  윈도우 경로 예: $env:USERPROFILE\.ssh\sandbox

# 공개키(.pub)를 VM에 등록 (둘 중 하나)
#  (a) 이미 접속 수단이 있으면 VM에서:  echo "<sandbox.pub 한 줄>" >> ~/.ssh/authorized_keys
#  (b) GCP 콘솔 → VM 수정 → SSH 키 추가에 sandbox.pub 붙여넣기 (형식: user:ssh-ed25519 AAAA... user)

ssh -i ~/.ssh/sandbox <vm-user>@<vm-ip>      # 접속 (변환 없이 표준 ssh!)
```
> **이 학습은 ssh-keygen 기준**입니다(가장 깔끔, PuTTY 불필요).
> `.ppk`(PuTTY)만 있는 경우의 변환·plink 방식은 로컬 `legacy/` 보관소에 따로 있습니다.

## 1. 학습 코드 올리고 환경 준비 (VM)
```bash
# VM에서
sudo apt update && sudo apt install -y git python3-venv python3-pip
git clone <your-repo> ~/work && cd ~/work/team_learning      # 또는 scp로 team_learning 전송
python3 -m venv .venv && .venv/bin/pip install requests       # tdfmini는 requests만 있으면 됨
```
> 💡 VM의 venv는 네 로컬 환경을 전혀 안 씁니다. 서버에 **독립 환경**이 새로 생겨요.

## 2. ⭐ 크롤링이 DB에 "연결"되는 지점
```
fetch.py(받기) → parse.py(파싱) → ★ store.py(저장) ★ → playground.db
```
- 어디서 쓰나: [`tdfmini/store.py`](../tdfmini/store.py)의 `upsert`가 sqlite에 씀.
- 어디에: `team_learning/playground.db` (`tdfmini/config.py`의 `DB`).
- 한 번 실행 = `(fund_code, base_date)` 한 묶음 = 그날 스냅샷 1장.

## 3. 직접 실행 — 클라우드에 DB가 생긴다
```bash
cd ~/work/team_learning
.venv/bin/python -m tdfmini.run --company A01015 --date 20260610   # 교보악사
#  → 수집 66건 → tdf_nav 총 66행

ls -lh playground.db          # DB가 '서버 안에' 생김!
.venv/bin/python - <<'PY'
import sqlite3
c=sqlite3.connect("playground.db")
print("행수:", c.execute("SELECT COUNT(*) FROM tdf_nav").fetchone()[0])
print("날짜:", [r[0] for r in c.execute("SELECT DISTINCT base_date FROM tdf_nav")])
PY
```

## 무엇을 배웠나
- ssh-keygen 키 → 변환 없이 표준 `ssh`로 접속(PuTTY 불필요).
- 학습 크롤러 `tdfmini`를 VM의 독립 venv에서 실행 → DB가 **서버 안에** 생성.
- `tdfmini/store.py`의 upsert가 "크롤링 ↔ DB 연결"의 실체.

## 실제 운영과의 관계
이건 **학습용**입니다. 실제 운영(`tdf_crawler`)을 GCP VM에 올리는 표준 절차는 [docs/DEPLOY.md](../../docs/DEPLOY.md).

➡ 다음: [11_cron_daily](../11_cron_daily/README.md) — 이걸 **매일 자동으로**(cron)
