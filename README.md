# slcf-seminar-pptx (Claude Code Plugin)

SLCF 연구실 세미나 발표자료를 **통일된 디자인**으로 자동 생성하는 Claude Code 플러그인.
PDF 논문/책을 입력하면 → `plan.yaml` 중간표현 → `.pptx` 슬라이드까지 만든다.

> 누가 발표를 만들어도 같은 양식이 나오게 하는 게 목적.
> 디자인 토큰(`assets/style.yaml`) + 의미 단위 슬라이드 메서드 + plan 스키마 lint 3중 잠금.

## 설치

### 1. 이 marketplace 추가

```text
/plugin marketplace add <repo-url-or-local-path>
```

레포가 GitHub에 있다면:
```text
/plugin marketplace add https://github.com/Seungju182/slcf-llm-seminar-pptx-plugin
```

로컬 개발 중이라면:
```bash
claude --plugin-dir /Users/seungjulee/workspace/slcf-llm-seminar-pptx-plugin
```

### 2. 플러그인 설치

```text
/plugin install slcf-seminar-pptx
```

### 3. (권장) 의존 환경

- **uv** — 스크립트가 PEP 723 inline deps를 사용 (`uv run --with python-pptx ...`)
- **LibreOffice** (선택) — 결과 PPTX를 PDF로 변환해 시각 검증할 때만 필요
- **macOS 사용자** — Microsoft Office의 한글 폰트(맑은 고딕) 누락 시 일부 PDF 미리보기에서 폰트 fallback 발생. PowerPoint/Windows에서는 정상.

## 사용 워크플로

Claude Code에서 PDF를 던지면서:

```text
이 PDF로 SLCF 세미나 PPT 만들어줘.
발표자: 홍길동, 날짜: 26.5.10
```

Claude가 자동으로 SKILL.md를 로드해 다음을 수행:

1. **추출** — PDF를 읽고 `extraction.chapters[].key_points`(3-5개) 채움
2. **plan 작성** — `assets/plan-template.yaml` 기반으로 `myplan.yaml` 생성
3. **lint** — `python scripts/plan.py myplan.yaml`
4. **빌드** — `python scripts/build_from_plan.py myplan.yaml --out=발표.pptx`

직접 CLI로 돌릴 수도 있다:
```bash
PLUGIN=~/.claude/plugins/slcf-seminar-pptx
uv run --with python-pptx --with pyyaml --with lxml \
  python $PLUGIN/skills/slcf-seminar-pptx/scripts/build_from_plan.py \
  myplan.yaml --out=발표.pptx
```

상세 가이드: `skills/slcf-seminar-pptx/SKILL.md`

## 핵심 기능

- **통일 디자인**: `assets/style.yaml` 한 파일로 색/폰트/그리드 잠금
- **Plan 스키마 lint**: `paper.total_pages` / `chapters[].importance` 합 / `key_points` 누락 등 자동 검증
- **`important: true`**: 핵심 슬라이드의 헤더를 #FFD700 노란색으로 강조 (전체 본문의 25% 넘으면 lint warning)
- **의미 단위 메서드**: `add_definition`, `add_comparison`, `add_process`, `add_two_content`, `add_conclusion` 등 — 좌표를 직접 만지지 않음
- **템플릿 충실도**: 슬라이드 마스터의 로고/배경 이미지를 rId remap으로 보존

## 로드맵

### Phase 1 (현재) — 단일 skill plugin
PDF 이해 + plan 작성 + 빌드를 한 skill 안에서. Claude의 PDF 읽기 능력에 의존.

### Phase 2 (예정) — Anthropic 공식 PDF skill 의존
[anthropics/skills](https://github.com/anthropics/skills)의 `pdf` skill을 prerequisite로 채택해
- 텍스트 + 표 + 이미지 + OCR 파싱을 위임
- 본 plugin은 **의미 추출**(chapter importance, key_points 결정)에 집중
- `seminar-extractor` skill을 추가해 Anthropic의 raw 추출 → `extraction.yaml` 변환

설치 시 prerequisite:
```text
/plugin marketplace add anthropics/skills
/plugin install pdf
```

### Phase 3 (예정) — 모듈러 분해
실사용 데이터가 쌓이면 `seminar-planner` skill을 분리 (lint 규칙 진화에 따라).

## 디렉터리 구조

```
slcf-llm-seminar-pptx-plugin/
├── .claude-plugin/
│   └── plugin.json
├── skills/
│   └── slcf-seminar-pptx/
│       ├── SKILL.md
│       ├── scripts/         # builder.py, plan.py, build_from_plan.py, style.py
│       ├── assets/          # template.pptx, style.yaml, plan-template.yaml
│       ├── references/      # plan-schema.md, extraction-protocol.md, …
│       └── samples/         # example-plan.yaml
├── marketplace.json
└── README.md
```

## 라이선스

MIT
