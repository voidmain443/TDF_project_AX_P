# 🚀 운영 배포 — GCP VM에 git clone 해서 매일 돌리기 (표준)

> 운영 프로젝트(`tdf_crawler`)를 **GitHub → GCP VM(리눅스)** 으로 올려 **매일 자동 수집**하는 단일 표준 경로.
> 접속은 **ssh-keygen(OpenSSH) 키** 기준(PuTTY 불필요). 도커 등 다른 옵션은 [legacy/](../legacy/README.md) 참고.

## 0. 한눈에
```
[로컬: 개발·커밋·push]  →  GitHub(비공개)  →  [GCP VM: git clone → venv → cron]
        ssh-keygen 키로 VM 접속 / 코드는 git, 키 아님
```

## 1. SSH 키 준비 (ssh-keygen, 1회)
```bash
# 로컬에서 OpenSSH 키 생성
ssh-keygen -t ed25519 -C "<vm-user>" -f ~/.ssh/gcp_tdf          # gcp_tdf(+.pub)

# 공개키(.pub)를 VM에 등록 — 셋 중 하나
#  (a) GCP 콘솔 → VM 수정 → SSH 키 추가에 gcp_tdf.pub 내용 붙여넣기  (형식: user:ssh-ed25519 AAAA... user)
#  (b) 이미 접속 가능하면 VM에서: echo "<gcp_tdf.pub 한 줄>" >> ~/.ssh/authorized_keys
#  (c) OS Login VM: gcloud compute os-login ssh-keys add --key-file=~/.ssh/gcp_tdf.pub

ssh -i ~/.ssh/gcp_tdf <vm-user>@<vm-ip>        # 접속 확인
```
> 키 종류·등록 자세히: 학습 문서 [team_learning/10_cloud_db](../team_learning/10_cloud_db/README.md) 또는 windows는 `$env:USERPROFILE\.ssh\`.

## 2. 코드 올리기 (GitHub → VM)
```bash
# 로컬: 비공개 repo에 push (data/·키·legacy/ 는 .gitignore로 제외됨)
git init && git add . && git commit -m "tdf crawler"
git remote add origin https://github.com/<계정>/tdf-crawler.git
git push -u origin main

# VM: 클론(최초) / 갱신(이후)
ssh -i ~/.ssh/gcp_tdf <vm-user>@<vm-ip>
sudo apt update && sudo apt install -y git python3-venv python3-pip
git clone https://github.com/<계정>/tdf-crawler.git ~/tdf-crawler   # 최초
cd ~/tdf-crawler && git pull                                        # 갱신
```

## 3. 환경 구성 + 첫 적재 (VM)
```bash
cd ~/tdf-crawler
python3 -m venv .venv && .venv/bin/pip install -e .
.venv/bin/python -m tdf_crawler.run                      # 오늘자 1회
.venv/bin/python -m tdf_crawler.backfill --start 2024-01-01   # 과거 누적(선택)
# 1주일치 빠른 빌드 + 검증:
bash cloud_quickstart/run_week.sh && bash cloud_quickstart/verify.sh
```

## 4. 매일 자동 (cron)
```bash
sudo timedatectl set-timezone Asia/Seoul
mkdir -p ~/tdf-crawler/logs
echo "0 8 * * * cd ~/tdf-crawler && ~/tdf-crawler/.venv/bin/python -m tdf_crawler.run >> ~/tdf-crawler/logs/crawl.log 2>&1" | crontab -
crontab -l            # 확인 · systemctl is-active cron
```
> ⚠️ `( crontab -l | grep -v ... )`를 `set -e`와 함께 쓰면 빈 crontab이 깔릴 수 있음 → 위처럼 `echo "..." | crontab -` 직접 설치.

## 5. 운영 루프 / 검증
- 수정: 로컬에서 커밋·push → VM `cd ~/tdf-crawler && git pull` (cron은 그대로 유지)
- 검증: `bash cloud_quickstart/verify.sh`, 로그 `tail -f ~/tdf-crawler/logs/crawl.log`
- 상태: `crawl_runs` 테이블 최신 status, 복구·백업은 [운영자 문서](operator/README.md)

## 보안
- 개인키(`~/.ssh/gcp_tdf`)·`data/tdf.db`는 **절대 git/VM 공개경로에 두지 말 것**(.gitignore 확인). 공개키만 VM 등록.
- cron 크롤러는 아웃바운드(KOFIA)만 필요 → 인바운드 방화벽 추가 불필요(SSH 22만).
