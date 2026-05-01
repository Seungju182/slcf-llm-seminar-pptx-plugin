---
name: slcf-seminar-pptx
description: SLCF(Statistical Learning and Computational Finance Lab) 연구실 세미나 발표 양식에 맞춰 PowerPoint 파일을 만드는 skill입니다. 사용자가 "SLCF 세미나 발표자료", "연구실 세미나 PPT", "랩미팅 발표자료", "논문 리뷰 발표", "책/PDF 요약 발표" 같은 요청을 하거나 SLCF 양식/템플릿/포맷을 언급하면 반드시 이 skill을 사용하세요. PDF(논문, 책, 보고서)가 함께 주어진 경우엔 단순 요약을 하지 말고, 챕터/소제목 단위로 체계적으로 분해해서 각 핵심 포인트마다 정의·예시·시각화·시사점을 갖춘 풍부한 슬라이드를 만듭니다. 어두운 배경의 표지(뇌 이미지)와 검정 헤더바 + 빨간 불릿의 본문 슬라이드를 양식과 100% 동일하게 생성합니다. 표, 다이어그램, 도형은 PDF 캡처 대신 코드로 직접 그리며, 모든 텍스트는 한국어로 작성합니다.
---

# SLCF 세미나 PPT 빌더

서울대 산업공학과 SLCF 연구실의 세미나 양식을 기반으로 발표 자료를 만드는 skill입니다.

## 핵심 원칙

1. **plan.yaml을 먼저 작성, 그 다음 빌드** — PDF를 보고 곧장 builder 메서드를 호출하지 말고, 먼저 `plan.yaml`이라는 중간 표현을 채우세요. lint가 누락·편향을 자동 감지하고, 빌드는 단순 매핑이 됩니다. 이게 발표자 간 통일성의 핵심.
2. **양식의 슬라이드를 deep copy 해서 사용** — 폰트, 색상, 로고, 배경 이미지가 100% 보존됩니다. 처음부터 새로 그리려고 하지 마세요.
3. **모든 텍스트는 한국어로 작성** — 본문, 표, 박스, 캡션 모두. 논문/모델/지표 이름 같은 고유명사만 영어 그대로 ("DDPM", "Transformer"). 슬라이드 제목도 한국어 권장.
4. **이미지 캡처 대신 직접 그리기** — PDF에서 잘라낸 표/다이어그램은 화질·톤 모두 양식과 안 맞음. `add_table`, `add_box`로 직접 그리고, 사진이나 복잡한 그래프만 `add_image`.

## 빠른 시작 (권장 흐름)

PDF를 먼저 정독하고 → `plan.yaml` 채우고 → lint → build의 3단계.

### 1) plan.yaml 작성

`assets/plan-template.yaml`을 복사해서 채웁니다. 스키마 상세는 `references/plan-schema.md`. 작은 예시 (전체 예: `samples/example-plan.yaml`):

```yaml
paper:
  title: "Denoising Diffusion Probabilistic Models"
  total_pages: 25
  presenter: "이승주"
  date: "26.5.10"

extraction:
  chapters:
    - {num: 1, title: "Introduction", pages: [1, 2], importance: 0.10}
    - {num: 2, title: "Background",   pages: [3, 6], importance: 0.20}
    - {num: 3, title: "Method",       pages: [7, 14], importance: 0.40}
    - {num: 4, title: "Experiments",  pages: [15, 20], importance: 0.20}
    - {num: 5, title: "Conclusion",   pages: [21, 22], importance: 0.10}
  figures: [...]    # 모든 figure 전수 기록
  tables: [...]
  key_terms: [...]
  skipped:          # 의도적으로 뺄 figure/chapter는 이유와 함께
    figures: [5]
    reasons: {"5": "appendix only"}

plan:
  - {type: cover}
  - {type: toc, items: ["배경", "방법", "실험", "결론"]}
  - {type: section_header, num: 1, title: "Introduction", chapter_ref: 1}
  - {type: definition, term: "Markov chain",
     definition: "현재 상태가 직전 상태에만 의존하는 확률 과정",
     why: ["..."], examples: ["..."], source_page: 3}
  - {type: comparison, title: "CIFAR-10 결과",
     headers: ["모델","FID","IS"],
     rows: [["DDPM","3.17","9.46"]],
     source_page: 17, table_ref: 1}
  - {type: process, title: "Forward / Reverse",
     steps: ["x_0","+노이즈","x_t","역방향","x_0"], emphasize: [3]}
  - {type: conclusion,
     takeaways: ["Diffusion이 GAN 안정성 문제 해결"],
     next_steps: ["샘플링 가속"]}
```

### 2) Lint

```bash
python scripts/plan.py myplan.yaml
```
누락 필드, 페이지 범위, 챕터 커버리지, 분량 비례, figure 미커버 등을 자동 검사. errors가 있으면 빌드 차단.

### 3) Build

```bash
python scripts/build_from_plan.py myplan.yaml --out=발표.pptx
```
lint 자동 실행 후 통과하면 PPT 생성. 실패하면 `--no-strict`로 강제 빌드 가능 (디버그용).

### 직접 builder API 호출 (fallback)

`plan.yaml`로 표현하기 어려운 자유 배치 슬라이드는 빌드 후 직접 builder를 호출:

```python
import sys
sys.path.insert(0, '<skill 폴더>/scripts')
from builder import SeminarBuilder

b = SeminarBuilder('/mnt/user-data/outputs/세미나발표.pptx')
b.set_cover(date='26.5.10', title='Diffusion Models')
# ... b.add_definition(...), b.add_comparison(...), etc
b.save()
```
하지만 가능하면 plan.yaml로 표현하는 게 통일성 면에서 유리합니다.

## 사용 가능한 메서드

### 기본 슬라이드 종류 (저수준)
| 메서드 | 용도 |
|-------|------|
| `set_cover(date, title)` | 표지 (어두운 배경 + 뇌 이미지). `date`는 'YY.M.D' 형식 |
| `add_title_content(title, bullets)` | 검정 헤더 + 빨간 불릿 + 검정 본문 |
| `add_title_only(title)` | 제목만, 본문 영역은 비어있음. 표/박스/이미지 직접 배치용 |

### 의미 단위 슬라이드 (고수준 — **이걸 우선 사용**)
좌표·폰트·색이 메서드 안에 박혀 있어 어떤 발표자가 만들어도 동일한 톤이 나옵니다.

| 메서드 | 용도 |
|-------|------|
| `add_section_header(num, title, subtitle='')` | 챕터/섹션 표지 (큰 'Chapter N' + 제목) |
| `add_toc(items, current=None)` | 목차. `current`(1-based)로 현재 항목 강조 |
| `add_definition(term, definition, why=[], examples=[], source_page=None)` | 정의 박스 + '왜 필요한가?' + '예시' |
| `add_comparison(title, headers, rows, source_page=None)` | 비교표를 콘텐츠 영역 정중앙에 자동 배치 |
| `add_process(title, steps, emphasize=[], descriptions=[], source_page=None)` | 가로 박스 N개 + 화살표 자동 분할. `emphasize=[i]`는 빨간 강조 |
| `add_two_content(title, left_title, left_bullets, right_title, right_bullets)` | 좌/우 6칸씩 분할 |
| `add_conclusion(takeaways, next_steps=None)` | '핵심 정리' / '향후 연구' 두 섹션 |

### 슬라이드에 요소 직접 추가 (저수준, 모두 inch)
| 메서드 | 용도 |
|-------|------|
| `add_table(slide, data, left, top, width, height, header_row=True)` | 표 (헤더 폰트는 STYLE.sizes.table_header 자동 사용) |
| `add_box(slide, text, left, top, width, height, fill_color=None, bold=False)` | 사각형 박스. 배경이 어두우면 글자 자동 흰색 |
| `add_textbox(slide, text, left, top, width, height, font_size=None)` | 투명 텍스트박스. font_size None이면 STYLE.sizes.body_sub |
| `add_image(slide, path, left, top, width, height)` | 이미지 (마지막 수단) |

### 슬라이드 단위 부가 기능
- `add_speaker_notes(slide, text)` — 발표자 노트 설정. PowerPoint Notes pane에 표시 (발표자만 봄). plan.yaml에선 `speaker_notes:` 필드로 자동 적용됨

### 마무리
- `b.save()` — 양식의 원본 예시 슬라이드는 자동 제거됨

슬라이드 크기: 16:9 와이드 (13.33 × 7.5 inch). 본문 영역은 `b.style.grid.content_*()`로 조회.

## PDF에서 표/다이어그램을 보고 어떻게 옮길지

논문에 있는 표/그림을 발표 자료에 넣을 때 **캡처해서 add_image로 붙이지 마세요.** 다음 흐름을 따르세요:

### 표 → `add_table`로 직접 작성
1. 논문 표를 보고 어떤 행/열이 있는지 파악
2. 한국어로 헤더 작성 (예: "Method" → "방법", "Accuracy" → "정확도")
3. 숫자만 그대로 옮기고, 단위는 한국어 친화적으로 (예: "8h" → "8시간")
4. `add_table`로 그리기

### 다이어그램 → `add_box` + `add_textbox`로 그리기
1. 도식의 핵심 블록 3-7개 추출 (예: 입력 → 처리 → 출력)
2. 박스 안 텍스트는 한국어로 (예: "Encoder" → "인코더")
3. `add_box`로 박스 배치, 색으로 강조 (검정/빨강은 양식 톤과 맞음)
4. 화살표는 `add_textbox(..., text='→', font_size=24)`로 표시

### 정말 그릴 수 없는 경우 (사진, 복잡한 그래프)
- 깔끔한 원본 이미지를 구해서 (가능하면 논문의 figure 파일을 직접) `add_image`로
- 캡처본을 쓸 수밖에 없다면 슬라이드 폭의 80% 이상으로 크게 배치 (작게 넣지 말 것)

## 색상 가이드

직접 색을 지정해야 할 땐 `b.style.colors`를 쓰세요. RGBColor 리터럴은 토큰 이탈을 만듭니다.

```python
b.style.colors.body_text       # 검정 — 기본 본문
b.style.colors.accent_red      # 빨강 — 핵심 강조 (양식 빨간 불릿과 동일)
b.style.colors.header_bg_black # 검정 — 강조 박스, 표 헤더
b.style.colors.light_gray      # 연회색 — 정의 박스, 보조 영역
b.style.colors.muted_gray      # 중회색 — 부가 정보, 캡션
```

박스 배경이 어두우면 `add_box`가 자동으로 글자색을 흰색으로 바꿔줍니다.

전체 토큰 목록은 `assets/style.yaml` 또는 `references/style-tokens.md` 참고.

## 발표 자료 만드는 표준 프로토콜 (PDF → plan → build)

PDF가 주어지면 **절대 곧장 builder 메서드를 호출하지 마세요.** 발표자/에이전트마다 슬라이드 분량과 구성이 들쭉날쭉해집니다. 반드시 다음 3단계를 거치세요.

### 1단계: PDF 추출 (extraction)

`assets/plan-template.yaml`을 복사해서 `extraction` 섹션을 채웁니다.

**필독**: `references/extraction-protocol.md` — 일반 가이드 + **LLM/Agent 도메인 특화 룰**(항상 등장하는 핵심 어휘, importance/figure rubric, key_points 6패턴, 안티패턴, 추출 자가점검 체크리스트). 이 plugin은 LLM·Agent·Orchestration 도메인 발표 전용 — 그에 맞춘 sharp한 룰이 들어 있음.

**모든 항목 전수 기록** (lint가 누락 검사):

- **`chapters`** — 챕터 단위 목차. 각 챕터에 다음을 채움:
  - `num`/`title`/`pages`/`importance`(0~1, 합 ≈ 1.0) — 기본 메타
  - **`key_points`**: 청중이 그 챕터에서 가져가야 할 것 **3~5개** (가장 중요한 추출 품질 지표)
  - `takeaway` — 챕터 한 줄 요약 (필수)
  - `summary` — 한 문단 (선택)
  - `role` — 자유 라벨 (선택, lint 검사 X)
- **`figures`** — 모든 figure의 `num`/`caption`/`page`/`type`/`importance`. 안 쓸 거면 `extraction.skipped.figures`에 **이유와 함께** 기록.
- **`tables`** — 모든 table 동일.
- **`key_terms`** — 정의 슬라이드로 살릴 만한 용어 후보.
- **`notable_equations`** — 발표에 살릴 수식.

**`key_points` 작성이 가장 중요.** "이 챕터를 듣지 않으면 청중이 잃을 정보"를 한 문장씩. 챕터 제목 반복 X, 추상적 일반론 X. 명사구가 아니라 **주장/지식**을 담아야 함.

추출이 부실하면 lint가 통과해도 발표 본질이 흔들립니다. 사용자에게 짧게 확인받기:
> "350페이지 책 13챕터 파악 완료: Ch5(Orchestration, 13%)와 Ch12(Security, 10%)가 핵심. 3개 챕터(7/10/11)는 분량 적어 결론에 통합. 이대로 plan 작성할까요?"

### 2단계: Plan 작성

같은 yaml 안의 `plan` 배열을 순서대로 채움. 각 항목은 `type` 키로 builder 메서드와 1:1 매핑.

권장 분량 가이드:
- **표지** 1, **목차** 1, **결론** 1
- **챕터당** `section_header` 1장 + 본문 슬라이드들. 본문 수는 `chapter.importance × (총 슬라이드 수 - 표지/목차/결론)` 비례
- 전체 길이: PDF 페이지 수 × 0.6 ~ 1.0 (40페이지 → 25~40장, 200페이지 → 30~50장)

각 슬라이드는 의미 단위 type을 우선 사용:

| PDF 발견 | plan type |
|---|---|
| 챕터 시작 | `section_header` |
| 새 개념 정의 (term + why + examples) | `definition` |
| 표/벤치마크 | `comparison` |
| 절차·파이프라인·flowchart | `process` |
| 좌우 대조 (장단점, 전후) | `two_content` |
| 단순 핵심 정리 | `title_content` |
| figure/사진을 살려야 할 때 | `image` (image_path 필수) |

**중요 슬라이드 표시 (`important: true`)**: 발표 흐름의 결정적 슬라이드(전체에서 단 하나만 본다면 그것)에 표시 — 헤더바 글씨가 **노란색(#FFD700)**으로 렌더됩니다. 본문의 5~25%만 사용 권장.

```yaml
- type: definition
  term: "AI Agent"
  important: true        # 노란 헤더로 강조
  ...
```

**발표자 노트 (`speaker_notes`)**: 모든 슬라이드 type이 받는 universal optional 필드. PowerPoint Notes pane에 들어가 발표자만 봄. 슬라이드당 2~5문장 권장. 본문 그대로 옮기지 말고 **추가 맥락**(왜 이 슬라이드, 자주 나오는 질문, 다음 슬라이드와의 연결)을 적기.

```yaml
- type: definition
  term: "ReAct"
  important: true
  speaker_notes: |
    ReAct는 Yao et al. 2023 ICLR에서 처음 제안.
    "왜 단순 prompting과 다른가?" 질문이 자주 나오는데
    답: action 결과를 다시 LLM에 feed back해 reasoning이 진화.
```

⚠️ `title_only`의 `notes` 필드와 혼동 주의: `title_only.notes`는 슬라이드 본문에 회색 placeholder로 보이는 "직접 후처리" 안내문, `speaker_notes`는 모든 type 공통 — 화면에 안 보이는 발표자 대본.

### 3단계: Lint → Build

```bash
python scripts/plan.py myplan.yaml          # 빌드 전 검사
python scripts/build_from_plan.py myplan.yaml --out=발표.pptx
```

`build_from_plan`은 자동으로 lint를 돌리고 errors 발견 시 빌드 차단.

### 흔한 lint 위반과 해결

| 위반 | 의미 | 해결 |
|---|---|---|
| `chapter.importance 합 0.60` | 챕터 분량 비중을 빠뜨렸거나 잘못 책정 | 모든 챕터 importance 다시 매기고 합이 1에 가깝게 |
| `chapter X: takeaway가 비어 있음` | 챕터 한 줄 요약 누락 | 한 문장으로 핵심 정리 |
| `chapter X: key_points 비어있음` | 청중이 가져갈 것 미정의 | 3~5개의 한 줄 명제 작성 |
| `key_points[i]이 TODO로 시작` | 채우지 않고 템플릿 그대로 | 실제 내용으로 교체 |
| `key_points[i] 길이 12자 미만` | 너무 짧음 — 추상적 | 구체적 주장으로 풀어쓰기 |
| `figure 3 ... plan에 등장하지 않음` | 추출은 했지만 슬라이드로 안 살림 | 슬라이드 추가, 또는 `skipped.figures`에 이유와 함께 |
| `chapter X: 슬라이드 0장` | 챕터 통째 누락 | section_header + 본문 슬라이드 추가 |
| `source_page=999이 [1, 25] 범위 밖` | 페이지 오타 | 정정 |
| `definition term 'X'이 N번 등장` | 같은 용어를 여러 슬라이드에 정의 | 한 곳만 두고 나머지 제거 |
| `important: true가 본문의 30%` | 강조 남발 | 결정적 슬라이드만 골라서 25% 이하로 |
| `본문 important: true가 0개` | 발표의 핵심 표시 안 됨 | 1~5개 슬라이드에 표시 |

### 자동 매핑 안 되는 슬라이드

수식 풀어쓰기처럼 의미 메서드에 안 맞는 경우 plan에 `type: title_only` + `notes`로 표시:

```yaml
- type: title_only
  title: "Loss 함수 유도"
  notes: "수식 3종을 직접 add_image / add_textbox로 후처리"
```

build_from_plan은 헤더만 있는 빈 슬라이드를 만들고, 사람이 빌드 후 직접 builder를 호출해 채웁니다.

## 슬라이드 종류별 매핑

대부분의 패턴은 의미 단위 메서드 한 줄로 끝납니다.

| 발표 의도 | 메서드 |
|---|---|
| 챕터/섹션 시작 | `add_section_header(num, title, subtitle)` |
| 발표 흐름 안내 | `add_toc(items, current=None)` |
| 새 개념 도입 | `add_definition(term, definition, why=[], examples=[], source_page=N)` |
| 둘 이상 항목 비교 | `add_comparison(title, headers, rows)` |
| 프로세스/단계 흐름 | `add_process(title, steps, emphasize=[i])` |
| 좌우 두 칸 (장단점, 전후, 두 모델) | `add_two_content(title, l_title, l_bullets, r_title, r_bullets)` |
| 마무리 | `add_conclusion(takeaways, next_steps=None)` |
| 단순 불릿 본문 | `add_title_content(title, bullets)` |

### 의미 단위 메서드에 없는 경우 (예: 수식 슬라이드)

수식은 가능하면 텍스트로 풀어쓰되 (예: `Loss = MSE(예측, 실제) + λ × |가중치|`),
복잡한 수식은 PDF 원본을 캡처해서 `add_image`로:

```python
g = b.style.grid
s = b.style.sizes
slide = b.add_title_only('Loss 함수')
b.add_textbox(slide, '전체 손실 함수:',
    left=g.content_left(), top=g.content_top() + 0.3,
    width=g.content_width(), height=0.5,
    font_size=s.body, bold=True)
b.add_image(slide, 'eq_loss.png',
    left=g.content_left() + 1, top=g.content_top() + 1.0, width=g.content_width() - 2)
b.add_textbox(slide,
    '• λ: 정칙화 강도\n• |w|: 가중치의 절댓값 합\n• MSE: 예측-실제 평균제곱오차',
    left=g.content_left(), top=g.content_top() + 3.5,
    width=g.content_width(), height=2, font_size=s.body_sub)
```

좌표는 항상 `b.style.grid` 헬퍼로 도출해야 발표자 간 정렬이 일치합니다.
하드코딩된 `left=2, top=3` 같은 값은 톤 이탈의 주범.

## "풍부함"의 기준 (자가 점검)

PPT를 만든 후 다음 질문에 모두 "예"라고 답할 수 있어야 합니다:

- [ ] PDF의 모든 챕터/주요 섹션이 다뤄졌는가?
- [ ] 각 챕터당 최소 2장 이상의 슬라이드가 있는가?
- [ ] PDF의 주요 figure/table 중 빠뜨린 것이 없는가?
- [ ] 시각화(표, 박스, 다이어그램)가 전체 슬라이드의 30% 이상에 들어있는가?
- [ ] 추상적 개념마다 구체적 예시가 따라붙는가?
- [ ] 비교 가능한 항목들이 표로 정리되어 있는가?
- [ ] 핵심 용어가 처음 등장할 때 정의되어 있는가?

## 본문 작성 톤

- 한 슬라이드에 불릿은 4-6개, 각 불릿은 1-2줄
- 문장 끝의 "~다", "~함", "~음"은 일관되게 — 발표용은 "~함" 또는 명사형 권장
- 영문 약어는 첫 등장 시 풀어쓰기 (예: "CNN(합성곱 신경망)")
- 한국어 친화적으로: "8h" → "8시간", "10K" → "1만 개"

## 양식 정보

- 양식 파일: `assets/template.pptx`
- 슬라이드 크기: 16:9 와이드 (13.33 × 7.5 inch)
- 본문 영역: 가용 너비 약 12.3 inch, 높이 약 5.5 inch (헤더와 푸터 제외)
- 페이지 번호와 SLCF 로고는 모든 본문 슬라이드 하단에 자동 표시

## 작업 후 검증 (필수)

PPT를 생성한 뒤 반드시 시각적으로 확인하세요:

```bash
python /mnt/skills/public/pptx/scripts/thumbnail.py <output.pptx>
```

생성된 `thumbnails.jpg`를 view 해서 점검:
- 표지에 뇌 이미지가 보이는지 (안 보이면 rId 매핑 문제)
- 본문 헤더의 검정 바와 흰 글씨 제목이 잘 보이는지
- **본문 글씨가 검정인지** (파란색이면 `_set_bullets_keep_format`의 `force_black` 체크)
- 표/박스 안의 한국어가 깨지지 않는지
- 텍스트가 잘리거나 박스 밖으로 넘치지 않는지
- 페이지 번호와 로고가 모든 슬라이드에 있는지

문제 발견 시 수정 후 재생성. 이상 없으면 `present_files`로 사용자에게 전달.

## 주의 사항

### 디자인 보존
- **빈 레이아웃에 새로 그리지 마세요** — 양식의 표지 배경 이미지가 슬라이드 자체에 박혀있어서, 빈 레이아웃 사용 시 누락됩니다. 반드시 `_clone_slide`로 양식 슬라이드를 복제해야 합니다.
- **이미지 참조의 rId 재매핑** — `_clone_slide`가 자동 처리하지만, 새 메서드 추가 시 주의.

### 텍스트 색상
- **본문 글씨는 자동으로 검정 강제** — 양식 기본값이 파란색이라 강제로 덮어씁니다 (`_force_run_color` 함수).
- **제목(헤더바)은 색상 강제 안 함** — 흰 글씨가 유지되어야 함. `_set_text_in_shape(shape, title, force_black=False)`.
- 새 메서드를 만들 때, 본문 영역엔 `force_black=True`(기본), 헤더엔 `force_black=False`.

### 한국어 폰트
- `add_table`, `add_box`, `add_textbox`는 한국어 폰트(`맑은 고딕`)를 자동 적용합니다.
- 새 도형/텍스트박스를 직접 추가할 때는 `_apply_korean_font(run, ...)` 헬퍼 사용.

### Presentation 객체
- **`Presentation()` 객체를 두 개 동시에 띄우지 마세요** — zip 충돌. `SeminarBuilder`는 하나로 in-place 복제합니다.

## 새로운 슬라이드 종류 추가 가이드

특수한 레이아웃이 필요하면 (예: 좌우 두 칸, 차트 슬라이드):

1. 양식 슬라이드 중 비슷한 것 찾기 (없으면 양식에 추가)
2. `SOURCE_SLIDE_INDEX`에 등록
3. 새 메서드에서 `_clone_slide(source)` 호출 후 텍스트만 교체
4. 본문 텍스트는 `force_black=True`로, 헤더는 `force_black=False`로
5. `references/template-structure.md` 업데이트

## 디자인 토큰 (`assets/style.yaml`)

모든 색상·폰트·크기·그리드는 `assets/style.yaml` 한 곳에서 관리합니다.
이 파일을 수정하면 모든 산출물의 톤이 일괄 변경됩니다 (개별 발표자 코드 X).

```yaml
colors:
  body_text:    "#000000"
  accent_red:   "#C00000"
  ...
fonts:
  korean: "맑은 고딕"
  latin:  "Calibri"
sizes:
  slide_title:   28      # 헤더바 제목
  section_title: 36      # 챕터 큰 제목
  body:          18      # 본문 불릿
  body_sub:      14      # 보조 본문
  table_body:    12
  caption:       10      # 출처 표기
grid:
  margin_l:      0.6
  header_bottom: 1.5     # 본문 시작 y
  footer_top:    6.9     # 본문 끝 y
  num_columns:   12      # 컬럼 분할
```

코드에서 직접 참조:
```python
b = SeminarBuilder('out.pptx')
b.style.colors.accent_red    # RGBColor(0xC0, 0x00, 0x00)
b.style.sizes.body            # 18
b.style.grid.col(0, of=12)    # (left, width)  — 12분할 그리드 0번 컬럼
b.style.grid.span(0, 6)       # (left, width)  — 첫 6칸을 합친 영역
```

**다른 양식으로 fork하려면**: `style.yaml`만 새 파일로 복사 + 수정 후
`SeminarBuilder('out.pptx', style_path='my-style.yaml')`로 로드.

**거버넌스 원칙**: 개별 발표자가 `style.yaml`을 수정하지 않습니다. 양식 관리자만
PR로 변경. 발표자는 의미 단위 메서드(`add_definition` 등)만 호출 → 톤 일관성 보장.

스키마 상세는 `references/style-tokens.md` 참고.
