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
| 같은 주제의 figure 2~4개 묶기 | `image_grid` |

한 key_point가 여러 슬라이드로 풀어쓰여도 OK (특히 important 키포인트).

## ⚠️ Deck-level 비주얼 분배 (강의자료는 글보다 그림)

세미나 발표는 **시각적**이어야 함. plan 작성 시 다음 분배를 목표로 (실측에서 글-only deck은 청중 집중도 떨어짐):

| 카테고리 | 권장 비율 | 슬라이드 type |
|---|---|---|
| **시각 우선** | **40~50%** | `image`, `image_grid`, `process`, `comparison` (표) |
| **구조적** | 20~30% | `definition`, `two_content` |
| **글-only** | **20~30% 이하** | `title_content` |
| **프레임** | 10~20% | `cover`, `toc`, `section_header`, `conclusion` |

### 글-heavy 슬라이드 줄이는 trick

| 만들고 싶은 슬라이드 | 글-only 대신 |
|---|---|
| "5개 키워드 나열" `title_content` | → `process` (각 키워드를 박스로) 또는 표 (`comparison`) |
| "긴 본문 정의" `title_content` | → `definition` (정의 박스 + 왜+예시) |
| "3개 모델 차이점 bullet" `title_content` | → `comparison` 표 |
| "프로세스 단계 bullet" `title_content` | → `process` (가로 박스 + 화살표) |
| "여러 인용/예시 bullet" `title_content` | → 본문 figure가 있으면 `image` / `image_grid`로 캡처 |

**원칙**: `title_content`로 끝내기 전에 위 표의 우측 변환이 가능한지 항상 확인.

### Figure는 캡처가 default — §3에서 강제

`extraction.figures`에 importance=high/medium 항목이 있으면 거의 무조건 `image` 또는 `image_grid` 슬라이드로 (§3 정책). PDF에 figure가 있는데 plan에 없으면 lint warning. "분량상 텍스트로 통합" 같은 자체 판단 금지.

---

# LLM/Agent 도메인 특화 룰

이 plugin은 **LLM·Agent·Orchestration 분야**의 책/논문/survey 발표를 위한 것입니다.
여기 적힌 룰은 그 도메인에 한정해 일반 가이드를 sharp하게 만든 것 — 다른 도메인엔 적용 X.

## 1. 항상 등장하는 핵심 어휘 (always-capture list)

다음 용어가 본문에 **처음 등장**하면 무조건 `definition` 슬라이드 또는 정의 박스로 보존
(이미 정의된 챕터를 따로 만든다면 그 챕터에서, 아니면 등장 시점 챕터의 슬라이드 추가):

**개념 기본**:
Agent, LLM, Tool, Memory, Orchestration, Planner, Executor, Reasoner

**패턴**:
ReAct, Reflection, Plan-and-Execute, Tree of Thoughts (ToT), Chain of Thought (CoT),
Self-Consistency, Self-Refine, Toolformer

**메커니즘**:
Function calling, Tool use, MCP (Model Context Protocol), RAG (Retrieval-Augmented Generation),
Context window, In-context learning, Few-shot, Zero-shot

**아키텍처**:
Single-agent, Multi-agent, Hierarchical agent, Agent topology,
Coordination, Delegation, Communication protocol

**실패 모드 / 안전**:
Hallucination, Prompt injection, Jailbreak, Guardrails, Red teaming,
Distribution shift, Reward hacking

**평가**:
SWE-bench, GAIA, WebArena, AgentBench, MMLU, HumanEval (대표 벤치마크),
Eval set, Golden set, A/B test

**프레임워크**:
LangGraph, AutoGen, CrewAI, OpenAI Assistants, Claude Agent SDK,
LlamaIndex, LangChain, Semantic Kernel

**비용/성능**:
Tokens (input/output), Context cost, Latency (TTFT, TPS), Throughput,
Cost-per-task, Cache hit rate

→ 이 중 **본 발표의 청중이 모를 만한 것**만 슬라이드화. SLCF 멤버 대상이면 LLM/Token 같은 기초는 skip.

## 2. 챕터 importance 결정 rubric

LLM/Agent 도메인 책의 챕터 비중은 거의 정형화되어 있음:

| 챕터 성격 | 권장 importance | 예시 |
|---|---|---|
| **Architecture / Orchestration** | 0.10~0.15 | "Multi-agent topology", "Coordination patterns" |
| **Tool use / Memory** | 0.10~0.13 | "Tool calling patterns", "Long-term memory" |
| **Pattern / Reasoning** | 0.10~0.13 | "ReAct / Reflection / ToT" |
| **Evaluation / Safety** | 0.08~0.12 | "Eval methodology", "Red teaming" |
| **Frameworks / Case study** | 0.05~0.08 | "LangGraph 소개", "Production deployments" |
| **Background (LLM 역사)** | 0.03~0.05 | "Transformer 복습", "Pre-training 개요" |
| **Glossary / Appendix** | skip 또는 0.02 | "Reference reading list" |

**합 ≈ 1.0** 유지. 책의 절반이 응용/Architecture에 할애된 경우가 흔함 — Background는 짧게.

## 3. Figure importance 판정 rubric + **캡처 필수 정책**

### ⚠️ 정책 (v1.1+)

**모든 importance=`high` 또는 `medium` figure는 PDF에서 캡처해 슬라이드에 embed가 default.** "분량상 텍스트로 통합" 같은 자체 판단으로 skip 금지. 텍스트만으로 figure를 대체하면 슬라이드가 빈약해 보임 (실측 audit으로 확인됨).

`extraction.skipped.figures`에 들어갈 수 있는 것은 다음만:
- 책 표지 / page divider art / chapter opener decoration
- 본문과 무관한 보조 figure (저자가 "see appendix" 정도로만 언급)
- 동일 개념을 더 잘 보여주는 다른 figure가 이미 채택된 경우 (이유 명시)

→ **확신이 안 서면 캡처해서 image / image_grid 슬라이드로 넣을 것.**

### Figure 종류별 처리 가이드

| figure 종류 | importance | 권장 슬라이드 type |
|---|---|---|
| Architecture / component diagram | high | `image` (단독) 또는 `process`로 재현 |
| Multi-agent topology / orchestration flow | high | `image` |
| Benchmark plot (model 비교, scale plot) | high | `image` 또는 `comparison` 표 |
| ReAct/Reflection trace 캡처 | high | `image` |
| Memory / Tool 호출 sequence diagram | high | `image` |
| UI/제품 스크린샷 (책의 핵심 예시) | medium | `image` 또는 `image_grid` 묶음 |
| Toy 교육용 예시 (cat picture 등) | low | skipped 가능 (이유 기록) |
| 책 표지 / page divider art | skip | skipped.figures 등재 |
| 수식 derivation | medium | `image` (수식만 캡처) |

### 캡처 도구 — `scripts/extract_figure.py`

PDF 페이지를 PNG로 캡처:

```bash
# 단일 페이지 (가장 간단, 권장)
uv run --with pypdfium2 --with pdfplumber --with Pillow \
  python scripts/extract_figure.py book.pdf 66 --out figures/fig1.png

# 여러 페이지 한 번에
uv run --with pypdfium2 --with pdfplumber --with Pillow \
  python scripts/extract_figure.py book.pdf --pages 66,69,70,78 --outdir figures/

# 페이지의 특정 영역만 (정밀)
uv run --with pypdfium2 --with pdfplumber --with Pillow \
  python scripts/extract_figure.py book.pdf 78 --bbox 100,200,500,400 --out figures/fig4.png
```

**워크플로**:
1. `extraction.figures`에 모든 figure 기록 (num/caption/page/importance)
2. importance=high/medium인 figure 페이지를 일괄 캡처: `--pages 44,47,48,56 --outdir /tmp/ch3-figs/`
3. plan에 `image` 또는 `image_grid` 슬라이드로 추가 (`image_grid`는 1~4개 묶음)
4. 정말 안 쓸 figure만 `skipped.figures`에 이유와 함께

### `image_grid` 사용 패턴

비슷한 figure 2~4개를 한 슬라이드에 (1×2 / 1×3 / 2×2 자동 결정):

```yaml
- type: image_grid
  title: "AI-enabled interfaces — terminal · IDE · GUI"
  images:
    - "figs/p44_warp.png"
    - "figs/p47_n8n.png"
    - "figs/p48_cursor.png"
  captions:
    - "Warp / Claude Code (terminal)"
    - "n8n.io (visual orchestration)"
    - "Cursor (IDE)"
  source_page: 44
  figure_ref: 1
```

3개면 자동 1×3, 4개면 2×2. 각 이미지는 cell 안에서 aspect ratio 보존.

## 4. `key_points` 작성 — 도메인 특화 명제 패턴

LLM/Agent 책에서 청중에게 가치 있는 key_point는 다음 6패턴 중 하나에 들어맞아야 함:

| 패턴 | 예시 |
|---|---|
| **선택 기준** | "ReAct는 도구 호출 task에 적합, planning task엔 Plan-Executor가 우위" |
| **Trade-off 정량화** | "Reflection은 정확도 +15%지만 token cost 3배" |
| **실패 모드** | "Multi-agent는 coordination overhead로 latency 2x" |
| **모델 의존성** | "Reflection은 GPT-4 이상에서만 효과 — 작은 모델에선 오히려 악화" |
| **Production 권고** | "프로토타입은 LangGraph로 시작, scale 시 자체 orchestration 권장" |
| **제한사항 / 반증** | "ToT는 search space 큰 task에만 유리, 단순 QA엔 CoT 충분" |

❌ 안 좋은 key_point (도메인 anti-pattern):
- "Agent에는 여러 종류가 있다" — 차별화 없음
- "Tools를 잘 써야 한다" — 행동지침이 없음
- "Memory가 중요하다" — 왜 / 어떤 종류인지 빠짐
- "Multi-agent가 좋다" — 비용/실패 모드 무시

## 5. `important: true` 도메인 한정 후보

발표 1회당 **1~5개**. 다음 중에서만:

- **Agent의 정의 슬라이드** — 발표 전체의 anchor
- **Core component 4종** (Model / Tools / Memory / Orchestration) 정리
- **저자가 권장하는 default 패턴** (예: "ReAct + function calling으로 시작")
- **결정적 실패 모드** — 보안 / cost blowup / 무한 루프
- **결정 rubric** — "언제 multi-agent로 가는가", "언제 fine-tune이 RAG보다 나은가"
- **결론**

❌ important로 표시하면 안 되는 것:
- 단순 비교표 (importance: false로도 충분)
- Background / 역사 슬라이드
- 한 framework의 사용법
- 저자의 곁가지 의견

## 6. 코드 / Pseudocode 처리

LLM/Agent 책엔 코드 예시가 많이 등장:

| 코드 종류 | 처리 |
|---|---|
| **핵심 패턴 코드** (ReAct loop, Reflection cycle 등) | `image` 슬라이드로 PDF 캡처 또는 핵심 5~10줄을 `title_only` + add_textbox로 발췌 |
| **API 호출 boilerplate** | 슬라이드화 X — "원문 p.N 코드 참조"만 |
| **긴 함수 구현** (30+줄) | 핵심 5~10줄만 발췌 + "전체는 원문 p.N" 주석 |
| **prompt template** | raw quote가 가치 — `definition` 또는 `title_content`에 그대로 |
| **JSON tool spec** | `comparison` 표로 변환 (parameter 표) |

**원칙**: 다이어그램이 코드를 함께 보여줄 때만 의미. `process` 슬라이드 + 옆에 핵심 코드 발췌가 default.

## 7. 도메인 anti-patterns (lint로 못 잡는 의미적 누락)

이 도메인 발표에서 흔히 빠뜨리는 것 — extraction 단계에서 self-check:

| 안티패턴 | 보강 방법 |
|---|---|
| "ReAct / Reflection / ToT가 있다" 나열만 | 각각의 **언제 쓰는지** 한 문장 추가 |
| "Tools 사용" | 호출 flow + 결과 처리 + 실패 시 행동 명시 |
| "Memory" | short-term vs long-term, 어떤 데이터, 어떻게 검색 |
| "Multi-agent가 좋다" | coordination 비용 + 권장 규모 명시 |
| 벤치마크 점수 인용 | task 정의 + baseline + 사용 모델 명시 |
| 모델 인용 ("GPT-4가 X 함") | 버전 / 날짜 / context window 명시 |
| "Production-ready" | eval set + monitoring + rollback 체크 |
| 보안 챕터 skip | 최소 한 슬라이드는 보안/오용 다룸 |
| Cost 무시 | 핵심 패턴 1개에 대해 token cost 정량 명시 |

## 8. PDF 읽을 때 우선 추출할 페이지

LLM/Agent 책/논문에서 시간 대비 추출 효율 큰 페이지:

1. **Table of Contents** (전체 챕터 importance 분배에 필수)
2. **각 챕터 첫 1페이지** — motivation / problem statement
3. **각 챕터 마지막 1페이지** — chapter summary / takeaway
4. **모든 architecture diagram이 있는 페이지** — figure_ref 채움
5. **모든 comparison table 페이지** — table_ref 채움
6. **결론 챕터 전체** — 책의 thesis가 압축됨
7. **Index / Glossary** — 핵심 용어의 정의 위치 빠르게 찾기

논문은 보통 **Abstract / Method / Experiments / Limitations** 4개 섹션이 핵심 — Related Work는 importance 낮게.

### 권장 도구 (anthropics/skills/pdf 같이 설치된 경우)

`anthropics/skills`의 `pdf` skill이 함께 설치되어 있으면 Claude가 다음 라이브러리 사용법을 추가로 학습. 직접 호출해 추출 정확도 끌어올리기:

```python
# uv run --with pdfplumber python ...
import pdfplumber
with pdfplumber.open(pdf_path) as pdf:
    # ToC 페이지 (보통 PDF 5~10페이지) — 챕터 분배에 직결
    print(pdf.pages[6].extract_text())

    # 챕터 첫 페이지 텍스트 (book p.1 = PDF p.21~25 보통)
    print(pdf.pages[22].extract_text())

    # 표 추출 — comparison/table_ref 슬라이드 source로 직접 사용 가능
    for tbl in pdf.pages[114].extract_tables():
        for row in tbl:
            print(row)
```

추가로 `pypdfium2`로 figure 캡처(`page.render(scale=2.0).to_pil().save(...)`)해 `image` 슬라이드 source로 사용.

⚠️ extraction.yaml의 `key_points` / `importance` / `role` 같은 **의미 판단**은 여전히 Claude가 함 — pdfplumber는 raw 추출만.

## 9. 직접 인용 vs 요약 결정

| 콘텐츠 | 인용 vs 요약 | 이유 |
|---|---|---|
| **용어 정의** | raw quote 권장 | 저자 표현이 가장 정확 |
| **Trade-off 주장** | 직접 인용 | 저자 의도 보존 |
| **비교표** | 표 그대로 + 단위 명시 | 숫자는 변형 금지 |
| **벤치마크 점수** | 직접 인용 + baseline 함께 | 맥락 빠지면 오해 |
| **저자의 권고/예측** | 직접 인용 + 출처 페이지 | "저자에 따르면" 명시 |
| **일반 설명** | 요약 OK | 발표 톤에 맞춰 압축 |
| **코드** | 핵심 5~10줄만 발췌 | full을 옮기면 슬라이드 깨짐 |

`source_page` 필드는 raw quote 또는 trade-off 인용 슬라이드에 **반드시** 채울 것 — 청중이 원문 확인 가능해야.

## 10. 부분 범위 발표 (`extraction.scope`)

사용자가 **전체 책이 아닌 일부만** 발표하길 요청하는 경우 — 가장 흔한 패턴 4가지:

| 사용자 요청 | scope 설정 |
|---|---|
| "Chapter 8만 30장으로 핵심 키워드 위주" | type=chapter, chapter_nums=[8], target_slides=30, focus=definitions |
| "Memory와 Tool use 챕터 묶어서 1시간" | type=chapter, chapter_nums=[3, 8], target_slides=~25 |
| "Orchestration 패턴 비교 발표" | type=topic, target_slides=20, focus=comparisons |
| "Ch5의 보안 sub-section만" | type=section, target_slides=10, focus=definitions |

### 작성 절차 (부분 범위)

1. **`paper.total_pages`는 PDF 전체 페이지** 그대로 (Ch8만 다뤄도 책 자체의 메타는 변경 X)
2. **`extraction.scope` 블록 채움** — type, chapter_nums, target_slides, focus
3. **`extraction.chapters`엔 scope 안 챕터만 자세히** 채움. importance는 scope 안에서의 비중으로 합 ≈ 1.0:
   - Ch8만이면 `[{num: 8, importance: 1.0}]`
   - Ch3+Ch8 묶으면 `[{num: 3, importance: 0.4}, {num: 8, importance: 0.6}]`
4. scope 밖 챕터는 **언급할 필요만 있으면** importance: 0으로 한 줄씩, 아니면 생략
5. `key_points`는 scope 안 챕터 안의 sub-section/concept 단위로 더 세밀하게 (3~5개에서 5~8개로 늘려도 OK)
6. `plan`은 scope 안에서만 작성:
   - cover, toc, conclusion 3장 + 본문 (target_slides - 3)장
   - target_slides=30이면 본문 27장 → Ch8의 sub-section importance 비례로 분배
   - focus=definitions면 `definition` 슬라이드를 본문의 50% 이상으로

### scope 모드일 때 lint가 felxible해지는 부분
- 다른 챕터가 plan에 없어도 warning X (scope 밖이니까)
- 챕터 슬라이드 수 vs importance 비례 검사도 scope 안 챕터끼리만
- importance 합 [0.7, 1.3]은 여전히 검사 (scope 내 합)

### scope 모드일 때 lint가 더 엄격해지는 부분
- target_slides 명시 → plan 길이 ±15% 안 (예: 30이면 [26, 34])
- focus=definitions면 `definition` 슬라이드 50% 이상

### 도메인 특화 부분 범위 패턴 (LLM/Agent)

| 발표 주제 | scope 가이드 |
|---|---|
| **단일 패턴 심화** (예: ReAct만) | type=topic, focus=definitions, target=~20 |
| **패턴 비교** (ReAct vs Plan-Executor vs Reflection) | type=topic, focus=comparisons, target=~25 |
| **Memory 시스템** | type=chapter, focus=process (short/long-term flow) |
| **Tool use 전체** | type=chapter, focus=mixed (def + comparison + process) |
| **Eval & Safety** | type=chapter, focus=mixed, important: 보안 슬라이드 1~2장 |
| **Production 배포** | type=topic, focus=process, target=~30, 코드 슬라이드 다수 |

---

## 자가 점검 체크리스트 (extraction 끝낸 뒤)

10개 중 8개 이상 ✅이면 extraction OK:

- [ ] `extraction.chapters[].importance` 합 ∈ [0.95, 1.05]
- [ ] 모든 챕터에 `key_points` 3~5개 (importance > 0.05인 챕터)
- [ ] `key_points`가 §4 6패턴 중 하나에 들어맞음
- [ ] §1 always-capture 용어 중 본문 처음 등장하는 것은 정의 슬라이드 후보로 표시
- [ ] Architecture / orchestration figure는 모두 importance: high
- [ ] `important: true` plan 슬라이드 1~5개 (§5 후보 중)
- [ ] §7 도메인 anti-pattern 없음 (특히 "X가 좋다"만 적힌 key_point)
- [ ] 핵심 raw quote 슬라이드는 `source_page` 채움
- [ ] Eval / safety / cost 중 최소 한 챕터 포함
- [ ] `extraction.skipped` 에 의도적 제외 figure 모두 등재 (이유 포함)
