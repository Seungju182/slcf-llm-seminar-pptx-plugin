# PDF 추출 프로토콜

발표자/에이전트가 `plan.yaml`을 채울 때 따라야 할 **콘텐츠 품질 가이드**.
이 skill은 LLM/Agents/Orchestration 같은 광범위한 발표 자료를 다루므로,
**미리 정의된 role/슬롯에 끼워맞추지 않습니다.** 대신 모든 챕터에 공통으로 적용되는
"청중이 가져가야 할 것"을 강제합니다.

## 핵심 원칙

방대한 책(예: 350페이지 O'Reilly 기술서)을 다룰 때 챕터 형태가 너무 다양합니다:
"User Experience Design", "Orchestration", "Tool Use" 같은 챕터를 미리 정한
4~5개 role 안에 우격다짐으로 넣으면 어색해집니다.

대신:

1. **`key_points`**: 각 챕터에서 청중이 반드시 가져가야 할 것 **3~5개** 리스트
2. **`takeaway`**: 챕터 한 줄 요약 (이전 단계와 동일)
3. **`role`** (선택): 자유 라벨. lint는 검사하지 않음. 단지 분류용
4. **`important: true`**: 발표 흐름의 결정적 슬라이드는 plan에서 표시 (헤더 노란색)

## chapter 작성 가이드

### `key_points` 작성법 (가장 중요)

이게 발표 품질의 핵심 지표. **"이 챕터를 듣지 않으면 청중이 잃을 정보"**를 3~5개 한 줄 문장으로.

좋은 예 (Ch 5: Orchestration):
```yaml
key_points:
  - "ReAct, Planner-Executor 등 6가지 agent type의 차이점"
  - "도구 선택 전략: Standard / Semantic / Hierarchical"
  - "Tool topology — 직렬 vs 병렬 vs 계층"
  - "Orchestration이 싱글 agent와 multi-agent의 분기점"
```

나쁜 예:
```yaml
key_points:
  - "여러 가지 내용"           # ❌ 너무 추상적
  - "TODO"                    # ❌ 채워지지 않음
  - "Orchestration 설명함"     # ❌ 챕터 제목 반복일 뿐
```

**기준:**
- 한 문장으로 쓰되 명사구가 아니라 **주장/지식**을 담아야 함
- "X가 Y이다"보다 "X와 Y의 차이는 Z이다", "X를 선택하는 기준은 Q이다"같은 형태
- PDF에서 직접 발췌해도 OK — 단, 챕터 제목 요약 X
- 챕터 importance에 비례: importance 높으면 5개, 낮으면 2~3개

### `role` (선택)

자유 라벨. 본인이 챕터를 정리하기 좋은 이름이면 무엇이든:
- `intro`, `agent_basics`, `frameworks`, `ux_design`, `tooling`,
  `orchestration`, `evaluation`, `safety`, `case_study`, `practices`,
  `wrap_up`, ...

lint가 검증하지 않습니다. 누락해도 됨.

### `summary` (선택)

챕터 본문을 한 문단으로 압축. PDF의 챕터 첫/끝 문단을 합쳐서 작성하면 빠름.

### `takeaway` (필수)

청중이 이 챕터를 보고 한 마디로 가져가야 할 것 — 한 줄.

## Lint가 검사하는 것

`scripts/plan.py`가 자동 검사:

| 위반 | 레벨 | 의미 |
|---|---|---|
| `key_points` 누락 또는 비어있음 (importance > 0.05) | warning | 챕터의 핵심을 정리 안 했음 |
| `key_points` 항목 < 2개 (importance > 0.10) | warning | 너무 압축 |
| `key_points` 항목이 비어있거나 'TODO'로 시작 | error | 작성 미완료 |
| `key_points[i]` 길이 < 12자 | warning | 너무 짧음 (성의없는 추출) |
| `takeaway` 비어있거나 < 10자 | error | 챕터 요약 누락 |

## 중요 슬라이드 (`important: true`)

발표 흐름의 결정적 슬라이드는 plan에서 표시 — **헤더바 글씨가 노란색(#FFD700)**으로 렌더됩니다.

```yaml
plan:
  - type: definition
    term: "Agent"
    definition: "..."
    important: true        # 이 슬라이드는 발표의 핵심
```

| Lint | 레벨 |
|---|---|
| 본문(cover/toc/conclusion 외) `important: true` 비율 > 25% | warning (강조 남발) |
| 본문 `important: true`가 0개 | warning (발표의 핵심이 어디인지 표시 안 됨) |

## 실전 작성 흐름 (방대한 책 350페이지 기준)

1. **표지·판권·서문 스킵**, Table of Contents 펴기
2. 각 챕터를 `extraction.chapters`에 등록 (num/title/pages/importance/role)
   - importance 합 ≈ 1.0이 되게 분배
   - 실용서는 보통 응용 챕터에 더 많이 배분
3. 각 챕터에 들어가서:
   - 챕터 시작 1-2 페이지 + 끝 1-2 페이지 + 모든 sub-section heading 추출
   - **`key_points` 3~5개 작성** — 이게 핵심. PDF 본문 한 문단씩 읽고 결정
   - `takeaway` 한 줄
   - 가능하면 `summary` 한 문단
4. PDF 전체의 `figures` / `tables` 전수 기록 (책의 경우 figure가 적을 수 있음)
5. `plan` 작성 — chapter importance 비례로 슬라이드 수 배분, key_points를 슬라이드로 변환
6. **결정적 슬라이드 1~5개에 `important: true`** — 청중이 책 전체에서 단 한 페이지만 본다면 어떤 슬라이드인가
7. `python scripts/plan.py myplan.yaml` 으로 lint
8. 통과하면 `python scripts/build_from_plan.py myplan.yaml --out=...`

## 권장 슬라이드 매핑 (key_points → slide types)

`key_points` 항목의 성격에 따라 어떤 type을 쓸지 가이드:

| key_point의 성격 | 추천 slide type |
|---|---|
| 새 개념의 정의 + 의미 | `definition` |
| 두 옵션 비교 / 표 형식 데이터 | `comparison` |
| 단계 / 흐름 / 파이프라인 | `process` |
| 장단점 / 전후 / 두 관점 | `two_content` |
| 일반 정리 / 불릿 본문 | `title_content` |
| 사진/도식 살려야 함 | `image` |

한 key_point가 여러 슬라이드로 풀어쓰여도 OK (특히 important 키포인트).
