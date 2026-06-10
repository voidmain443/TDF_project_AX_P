# 11. cron으로 매일 자동 수집 — `tdfmini`

> 레슨 10에서 클라우드에 DB를 만들었습니다. 이제 **내가 안 켜도 매일 자동으로** 한 장씩 쌓이게 합니다.

## 1. cron이 뭔가 + crontab 한 줄 분해
`cron`은 리눅스의 **"시간표 비서"**. 정해진 시각에 명령을 대신 실행합니다.
```
0 8 * * *   cd ~/work/team_learning && .venv/bin/python -m tdfmini.run --company A01015
┬ ┬ ┬ ┬ ┬
│ │ │ │ └ 요일(*=매일)   │ │ └ 일   │ └ 시(8)   └ 분(0)   → 매일 08:00 실행
```

## 2. ⭐ 수업 중 "여러 날" 시뮬레이션 (즉석 체감)
cron은 원래 하루를 기다려야 보이죠. **날짜를 바꿔 연속 실행**해 "매일 쌓임"을 지금 재현:
```bash
cd ~/work/team_learning
for d in 20260608 20260609 20260610; do
  .venv/bin/python -m tdfmini.run --company A01015 --date $d
done
# tdf_nav 의 날짜가 3개로 늘어남 = "매일 한 장씩 쌓임"
.venv/bin/python -c "import sqlite3;print(sorted({r[0] for r in sqlite3.connect('playground.db').execute('SELECT base_date FROM tdf_nav')}))"
```
멱등 증명: 같은 날을 또 실행해도 행수 그대로 → 중복 안 쌓임.

## 3. 진짜 cron 등록 (매일)
```bash
# 먼저 cron이 돌릴 명령을 1회 손검증
cd ~/work/team_learning && .venv/bin/python -m tdfmini.run --company A01015

# 타임존·cron 데몬·로그
sudo timedatectl set-timezone Asia/Seoul
sudo systemctl enable --now cron
mkdir -p ~/work/team_learning/logs

# crontab 직접 설치 (절대경로)
echo "0 8 * * * cd $HOME/work/team_learning && $HOME/work/team_learning/.venv/bin/python -m tdfmini.run --company A01015 >> $HOME/work/team_learning/logs/cron.log 2>&1" | crontab -
crontab -l            # 확인
```
> ⚠️ `( crontab -l | grep -v ... )`를 `set -e`와 함께 쓰면 빈 crontab이 깔릴 수 있음 → `echo "..." | crontab -` 직접 설치.

## 4. 관찰 · 숙제
```bash
tail -f ~/work/team_learning/logs/cron.log
```
- **숙제**: 내일 08:00 이후 위 날짜 조회를 다시 → 날짜가 하나 더 늘었는지 확인.
- 0건이 나오면 보통 휴장일(정상).

## 무엇을 배웠나
- `cron` = 시간표 비서. `0 8 * * *` = 매일 08:00.
- 날짜를 바꿔 연속 실행하면 "매일 쌓임"을 수업 안에서 재현.
- **멱등성**이 무인 자동화를 안전하게 만든다.

## 🎉 전체 학습 완료!
```
[Part 1] HTTP → 받기 → 파싱 → 저장 → 한파일 MVP → tdfmini로 분리 → 테스트 → 멱등·백필
[Part 2] ssh-keygen으로 샌드박스 VM 접속 → tdfmini로 클라우드 DB → cron 매일 무인 수집
```
- 실제 운영(`tdf_crawler`)을 GCP VM에 올리는 표준: [docs/DEPLOY.md](../../docs/DEPLOY.md)
- 더 깊이: 역할별 [docs/](../../docs/README.md) · 손으로 더: [exercises](../exercises/README.md)
