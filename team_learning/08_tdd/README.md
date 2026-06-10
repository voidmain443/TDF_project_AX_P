# 08. 테스트로 안전하게 (pytest 기초) — `tdfmini.parse`

코드를 고칠 때마다 손으로 확인하면 느리고 불안합니다. **테스트**가 자동으로 확인해 줍니다.

## 왜 테스트가 가능해졌나
레슨 07에서 **파싱을 순수 함수([`tdfmini/parse.py`](../tdfmini/parse.py))로 분리**했기 때문입니다.
순수 함수는 입력만 주면 항상 같은 출력(네트워크·DB 없음) → **저장해둔 XML 한 조각**으로 검증 가능.

## tdfmini 파서 테스트 직접 실행
이미 [`tdfmini/test_parse.py`](../tdfmini/test_parse.py)가 있습니다:
```bash
pip install pytest
cd team_learning
python -m pytest tdfmini/test_parse.py -v
#  test_local_strips_namespace · test_num · test_parse_tdf_keeps_only_tdf  → 3 passed
```
핵심 테스트:
```python
def test_parse_tdf_keeps_only_tdf():
    # 'TDF'가 든 펀드 1개 + 일반펀드 1개를 주면 → TDF 1개만 남아야 한다
    rows = parse.parse_tdf(xml)
    assert len(rows) == 1 and rows[0]["code"] == "K1"
```

## 직접 해보기 (연습)
`tdfmini/test_parse.py`에 케이스를 추가하세요:
- `parse._num("1,000")` 처럼 콤마가 있으면? (지금은 None — 운영 `tdf_crawler`는 콤마 처리함. 왜 다른지 비교)
- 날짜가 8자리가 아니면 `date`가 `None`인지

## 무엇을 배웠나
- 테스트 = `test_` 함수 + `assert`. 통과하면 `.`, 실패하면 어디가 틀렸는지 알려줌.
- **순수 함수**라서 네트워크 없이 빠르게 검증(분리의 보상).
- 실제 응답에서 잘라낸 작은 샘플로 파서를 시험한다.

## TDD = 테스트 먼저
실제 운영 프로젝트도 그렇게 만들어졌습니다. `tests/`에 50개 테스트가 있죠:
```bash
cd ..        # 프로젝트 루트
python -m pytest          # tdf_crawler 전체 테스트(네트워크 없이 통과)
```

➡ 다음: [09_idempotent_schedule](../09_idempotent_schedule/README.md)
