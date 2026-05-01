# Plan 스키마 — PDF→PPT 중간 표현

PDF를 읽은 후 슬라이드를 빌드하기 전에 채워야 하는 **canonical YAML**.
누가/어떤 에이전트가 채우든 **같은 구조**가 나와서, 빌드 결과가 결정적으로 통일됩니다.

## 전체 흐름

```
[1] raw PDF  →  [2] plan.yaml (LLM이 채움)  →  [3] PPT 빌드 (자동)
```

- [2] 단계의 형식이 잠겨있으면 [3]은 단순 매핑이 됩니다
- [2]에 lint를 걸어 추출 누락/편향을 자동 차단

## 최상위 필드: `schema_version`

```yaml
schema_version: "1.0"   # MAJOR.MINOR
paper: ...
extraction: ...
plan: ...
```

빌더가 plan.yaml을 받아 호환성을 확인하는 단서:
- **MAJOR 변경 (1.0 → 2.0)**: breaking — 필드 rename/remove, 타입 변경. lint가 거부, 마이그레이션 필요.
- **MINOR 변경 (1.0 → 1.1)**: additive — 옵션 필드 추가만. 옛 plan은 그대로 동작.

| plan의 schema_version | 빌더의 CURRENT | lint 결과 |
|---|---|---|
| 없음 | 1.0 | warning ("`schema_version` 추가 권장", 1.0으로 간주) |
| `"1.0"` | 1.0 | OK |
| `"1.1"` | 1.0 | warning (새 필드 일부 무시될 수 있음) |
| `"2.0"` | 1.0 | error (major mismatch — 마이그레이션 필요) |
| `"v1"` 같은 비표준 | 1.0 | error (형식 오류) |

### 마이그레이션 가이드 (향후)

새 MAJOR 버전이 나오면 이 섹션에 변경 내역과 자동 마이그레이션 스크립트를 기록:

- **1.0 → 2.0** (TBD): 변경 사항 / `scripts/migrate_1_to_2.py` 사용법

현재는 1.0 단일 버전.

## 3개 섹션

### A. `paper` — PDF 메타데이터

```yaml
paper:
  title: "Denoising Diffusion Probabilistic Models"
  authors: ["Jonathan Ho", "Ajay Jain", "Pieter Abbeel"]
  venue: "NeurIPS 2020"             # 학회/저널, 책일 경우 출판사
  total_pages: 25                    # PDF 전체 페이지 수
  source_file: "ddpm.pdf"            # 원본 파일명
  presenter: "홍길동"                  # 발표자 이름
  date: "26.5.10"                    # 'YY.M.D' 발표 날짜
```

**필수**: `title`, `total_pages`, `presenter`, `date`. 나머지는 권장.

### B. `extraction` — PDF에서 추출한 구조

```yaml
extraction:
  abstract: "한 문단 요약"

  # scope (선택, 1.1+) — 부분 범위 발표
  scope:
    type: chapter                  # full | chapter | section | topic
    chapter_nums: [8]              # type=chapter일 때 어느 챕터(들)
    target_slides: 30              # 명시 분량 (없으면 importance 비례)
    focus: definitions             # definitions | comparisons | process | mixed
    description: "Ch8 (Memory) 심화 — 핵심 키워드 정의 위주"

  chapters:
    - num: 1
      title: "Introduction"
      role: "intro"                    # 선택, 자유 라벨 (lint 검사 X)
      pages: [1, 2]                    # [start, end] inclusive
      importance: 0.10                 # 0~1, 모든 챕터의 합 ≈ 1.0
      summary: "문제 정의와 기존 한계"
      key_points:                      # 청중이 가져가야 할 것 3~5개 (필수)
        - "기존 LLM 단독 한계: 다단계 추론, 외부 도구 사용 불가"
        - "Agent의 등장 — GPT-3.5 이후 도구 호출 정확도 실용 수준"
        - "본 책의 범위: 설계/UX/도구/orchestration/safety"
      key_concept_pages: [1, 2]
      figure_nums: [1]
      table_nums: []
      takeaway: "Agent는 LLM 단독으로 못 푸는 다단계 작업을 자동화"

    - num: 2
      title: "Background"
      pages: [3, 6]
      importance: 0.15
      ...

  figures:                            # PDF의 모든 figure
    - num: 1
      caption: "Diffusion process overview"
      page: 2
      type: diagram                   # diagram | photo | chart | flowchart
      importance: high                # high | medium | low
    - num: 2
      caption: "Forward/reverse trajectory"
      page: 4
      type: diagram
      importance: high

  tables:                             # PDF의 모든 table
    - num: 1
      caption: "FID comparison"
      page: 12
      importance: high

  key_terms:                          # 정의가 필요한 핵심 용어
    - term: "Markov chain"
      page: 3
      simple_definition: "현재 상태가 직전 상태에만 의존하는 확률 과정"
    - term: "Variational bound"
      page: 5
      simple_definition: "log-likelihood의 ELBO 하한"

  notable_equations:                  # 발표에 살릴 만한 수식
    - num: 1
      page: 7
      latex: "L = E_q[...]"
      meaning: "전체 손실 함수"

  skipped:                            # 의도적으로 스킵하는 것 (lint가 검증)
    figures: [5, 7]                   # 스킵할 figure 번호
    reasons:
      "5": "Appendix의 보조 figure로 본문 흐름과 무관"
      "7": "동일 개념을 figure 2가 더 잘 보여줌"
    chapters: []                      # 챕터를 통째 스킵하는 경우
```

**필수**: `chapters` (최소 1개, 각각 `num`/`title`/`pages`/`importance`).
나머지는 PDF에 해당 요소가 있다면 모두 기록 (없으면 빈 리스트).

#### `extraction.scope` 상세 (1.1+ 선택 블록)

부분 범위 발표 (특정 챕터/주제만, 명시적 슬라이드 분량, 슬라이드 type 편향 등) 처리. 없으면 **전체 책/논문 발표**로 간주.

| 필드 | 타입 | 의미 |
|---|---|---|
| `type` | `full` \| `chapter` \| `section` \| `topic` | 범위 종류. 기본 `full`. |
| `chapter_nums` | `int[]` | `type=chapter`일 때 필수 — 어떤 챕터 번호들이 발표 대상인지 |
| `target_slides` | `int` | 명시 슬라이드 분량 (예: 30). plan 길이가 ±15% 안인지 lint가 검사 |
| `focus` | `definitions` \| `comparisons` \| `process` \| `mixed` | 슬라이드 type 편향. 매핑되는 type이 본문의 50% 미만이면 warning |
| `description` | string | 사람이 읽는 한 줄 설명 (lint 영향 X) |

**`scope.type='chapter'` 사용 패턴 (예: "Ch8만 30장")**:

```yaml
extraction:
  scope:
    type: chapter
    chapter_nums: [8]
    target_slides: 30
    focus: definitions
    description: "Ch8 (Memory) 심화"
  chapters:
    - num: 8
      title: "Memory"
      importance: 1.0          # scope 내 비중
      key_points: [...]
    # scope 밖 챕터는:
    #   (1) 아예 안 쓰거나, 또는
    #   (2) importance: 0.0 으로 두면 lint가 plan 등장 강제 안 함
```

**lint가 scope를 인식하는 방식**:
- `scope.type='chapter'`이면 `scope.chapter_nums` 안 챕터만 plan 커버리지/슬라이드 비례 검사 대상
- 그 외 챕터는 plan에 안 나와도 warning 없음
- importance 합 검사 ([0.7, 1.3])는 그대로 유지 — scope 내 챕터들의 합으로 자연스럽게 만족
- `target_slides` 명시 시 plan 길이가 ±15% 벗어나면 warning
- `focus='definitions'`이면 `definition` slide가 본문의 50% 미만일 때 warning

### C. `plan` — 슬라이드 순서대로 (배열)

각 항목은 `type`으로 분기. `type` 별 필드는 builder 메서드 시그니처와 1:1 매핑.

```yaml
plan:
  - type: cover                       # → b.set_cover(date, title)
    # date, title 생략 시 paper에서 자동 (date=paper.date, title=paper.title)

  - type: toc                          # → b.add_toc(items, current=None)
    items: ["배경", "방법", "실험", "결론"]
    current: null

  - type: section_header               # → b.add_section_header(num, title, subtitle)
    num: 1
    title: "배경"
    subtitle: "Diffusion Models의 등장"
    chapter_ref: 1                     # validation: extraction.chapters[?].num과 매칭

  - type: title_content                # → b.add_title_content(title, bullets)
    title: "Diffusion Model이란"
    bullets:
      - "노이즈 추가 → 학습 → 역과정으로 샘플 생성"
      - "GAN 대비 학습이 안정적"
    source_page: 1

  - type: definition                   # → b.add_definition(...)
    term: "Markov chain"
    definition: "현재 상태가 직전 상태에만 의존하는 확률 과정"
    why:
      - "Diffusion 과정의 수학적 토대"
      - "각 step의 독립성 보장"
    examples:
      - "DDPM의 forward process q(x_t | x_{t-1})"
    source_page: 3

  - type: comparison                   # → b.add_comparison(title, headers, rows)
    title: "주요 모델 비교"
    headers: ["모델", "FID ↓", "샘플링 시간"]
    rows:
      - ["DDPM", "3.17", "1000 step"]
      - ["DDIM", "4.04", "50 step"]
      - ["LDM", "3.60", "50 step"]
    source_page: 12
    table_ref: 1                        # validation: extraction.tables[?].num

  - type: process                      # → b.add_process(title, steps, emphasize, descriptions)
    title: "학습 파이프라인"
    steps: ["데이터", "전처리", "학습", "샘플링", "평가"]
    emphasize: [2]
    descriptions: ["수집", "정규화", "denoise 학습", "역방향", "FID"]
    source_page: 8
    figure_ref: 2                       # validation: extraction.figures[?].num

  - type: two_content                  # → b.add_two_content(...)
    title: "장단점"
    left_title: "장점"
    left_bullets: ["품질 우수", "안정적"]
    right_title: "단점"
    right_bullets: ["느림", "메모리 큼"]

  - type: image                        # → b.add_title_only + add_image
    title: "노이즈 스케줄"
    image_path: "figures/fig3.png"
    caption: "linear vs cosine schedule"
    source_page: 9
    figure_ref: 3

  - type: title_only                   # → b.add_title_only (자유 배치 fallback)
    title: "수식 정리"
    notes: "이후는 직접 builder 호출"      # plan에서 자동 빌드 X, 사람이 후처리

  - type: conclusion                   # → b.add_conclusion(takeaways, next_steps)
    takeaways:
      - "Diffusion이 GAN의 안정성 문제를 해결"
      - "샘플 품질 SOTA"
    next_steps:
      - "샘플링 가속화"
      - "조건부 생성"
```

## 슬라이드 type 전체 목록

모든 type은 다음 두 universal optional 필드를 받음:
- `important: true` — 헤더 글씨가 노란색(#FFD700)으로 강조
- `speaker_notes: "..."` — 발표자 노트. PowerPoint Notes pane에 들어감 (발표자만 봄)

아래 표의 "선택 필드"엔 type별 고유 필드만 표기 (universal 두 개는 모두 가능).

| type | 매핑 메서드 | 필수 필드 | 선택 필드 |
|---|---|---|---|
| `cover` | `set_cover` | — (paper에서 자동) | `date`, `title` |
| `toc` | `add_toc` | `items` | `current`, `title` |
| `section_header` | `add_section_header` | `num`, `title` | `subtitle`, `chapter_ref` |
| `title_content` | `add_title_content` | `title`, `bullets` | `source_page` |
| `title_only` | `add_title_only` | `title` | `notes` (post-process TODO) |
| `definition` | `add_definition` | `term`, `definition` | `why`, `examples`, `source_page` |
| `comparison` | `add_comparison` | `title`, `headers`, `rows` | `source_page`, `table_ref` |
| `process` | `add_process` | `title`, `steps` | `emphasize`, `descriptions`, `source_page`, `figure_ref` |
| `two_content` | `add_two_content` | `title`, `left_title`, `left_bullets`, `right_title`, `right_bullets` | `source_page` |
| `image` | `add_title_only` + `add_image` | `title`, `image_path` | `caption`, `source_page`, `figure_ref` |
| `image_grid` | `add_image_grid` | `title`, `images` (1~4) | `captions`, `source_page`, `figure_refs` (list — 여러 figure를 한 슬라이드에 묶을 때) |
| `conclusion` | `add_conclusion` | `takeaways` | `next_steps`, `title` |

### `important: true` 사용 가이드

발표 흐름의 결정적 슬라이드(전체에서 하나만 본다면 그것)에 표시. 전체 본문의 25%를 넘으면 lint warning — 강조는 희소할 때만 효과 있음.

```yaml
- type: definition
  term: "ReAct"
  definition: "Reasoning + Acting을 번갈아 수행하는 agent 패턴"
  important: true        # 헤더 노란색
  ...
```

### `speaker_notes` 사용 가이드

슬라이드 본문엔 안 들어가지만 발표자가 말로 풀 내용을 적어두는 곳. PowerPoint의 Notes pane에 들어감.

권장 길이: 슬라이드당 2~5문장. 슬라이드 본문을 그대로 옮겨 적지 말고 **추가 맥락**(왜 이 슬라이드를 넣었는지, 청중이 흔히 묻는 질문, 다음 슬라이드와의 연결)을 적기.

```yaml
- type: definition
  term: "ReAct"
  definition: "Reasoning + Acting을 번갈아 수행하는 agent 패턴"
  speaker_notes: |
    ReAct는 Yao et al. 2023 ICLR 논문에서 처음 제안.
    Chain-of-Thought + tool use를 한 loop로 묶은 게 핵심.
    "왜 단순 prompting과 다른가?" 질문이 자주 나오는데,
    답: action 결과를 다시 LLM에 feed back해 reasoning이 진화.
  ...
```

⚠️ `title_only` type의 `notes` 필드와 혼동 금지:
- `title_only.notes` = 슬라이드 본문에 회색 placeholder로 "직접 후처리" 안내문 표시
- `speaker_notes` = 발표자 노트 (모든 type 공통, 화면에 안 보임)

## Lint 규칙 (자동 검증)

`build_from_plan`이 실행 직전에 자동으로 돌립니다. 위반 종류:

### Errors (빌드 차단)
- `paper.total_pages` 없거나 0
- `extraction.chapters` 없거나 비어 있음
- `chapter.importance` 합이 0.7 미만 또는 1.3 초과
- `plan`이 비어 있음, 또는 `cover`가 첫 항목 아님
- 슬라이드의 `source_page`가 `[1, total_pages]` 범위 밖
- `chapter_ref`/`figure_ref`/`table_ref`가 extraction에 없는 번호
- 필수 필드 누락 (위 표 참조)

### Warnings (빌드는 진행, 보고)
- `extraction.chapters` 중 plan에 등장하지 않는 챕터 (importance > 0.05)
- `extraction.figures` 중 어느 슬라이드의 source_page와도 매칭되지 않고 `skipped`에도 없음
- 챕터별 슬라이드 수가 importance 비례에서 ±50% 이탈
- `toc`가 plan에 없음
- `conclusion`이 plan 마지막 근처에 없음
- 같은 `term`/`figure_ref`를 여러 슬라이드가 참조 (중복)
- 한 챕터의 슬라이드가 0~1장 (importance > 0.1인데도)
- 슬라이드별 `bullets` 5개 초과
- `bullets[i]` 길이 80자 초과

위반 시 `scripts/plan.py` 실행 결과로 표시 + 빌드 단계에서 errors는 raise.

## 작성 절차 (LLM/사람용)

1. `assets/plan-template.yaml`을 복사해 `myplan.yaml`로 시작
2. `paper` 섹션 채우기 (PDF 1페이지 + 마지막 페이지 보고)
3. `extraction.chapters`를 PDF 목차에서 채우기 — **반드시 모든 챕터, importance 합 ≈ 1.0**
4. `extraction.figures` / `tables` / `key_terms` / `notable_equations` 전수 기록 — 빠뜨리면 lint가 잡음
5. `extraction.skipped`에 의도적으로 제외할 figure/chapter 명시 (이유 포함)
6. `plan` 작성 — chapter importance 비례로 슬라이드 수 배분
7. `python scripts/plan.py myplan.yaml` 으로 lint
8. errors 0개가 되면 `python scripts/build_from_plan.py myplan.yaml --out=발표.pptx`

## 비고

- `plan` 안에 자동 매핑 안 되는 type(`title_only` with `notes`)이 있으면, 빌드는 헤더만 만든 상태로 그 슬라이드를 만들고 사람이 직접 builder API로 후처리.
- `paper` 섹션은 lint와 페이지 범위 검증에 쓰이고, `set_cover` 자동 채움에도 사용됨.
- chapter importance는 발표 분량 결정에 사용. 합이 1이 아니면 자동 정규화 (warning).
- 다른 양식으로 fork했다면 `build_from_plan` 호출 시 `--style=other-style.yaml` 인자로 스타일 교체 가능.
