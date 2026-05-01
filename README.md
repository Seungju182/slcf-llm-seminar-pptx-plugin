# slcf-llm-seminar-pptx-plugin

SLCF 연구실 **LLM/Agent 도메인** PDF (논문·책·survey)를 통일된 디자인의 세미나 발표자료(.pptx)로 자동 생성하는 Claude Code 플러그인.

> 누가 만들어도 같은 양식. 디자인 토큰 + 의미 단위 슬라이드 메서드 + plan 스키마 lint + 도메인 추출 룰의 4중 잠금.

## 도메인 범위

- ✅ LLM, Agent, Orchestration, Tool use, Memory, Eval/Safety, Frameworks (LangGraph/AutoGen 등)
- ❌ 다른 분야 (ML 일반, 시스템, 네트워크 등) — 추출 룰이 LLM/Agent에 한정 튜닝됨

## 설치

```text
/plugin marketplace add https://github.com/Seungju182/slcf-llm-seminar-pptx-plugin
/plugin install slcf-seminar-pptx
```

의존: **uv** (스크립트가 PEP 723 inline deps 사용 — `python-pptx`, `pyyaml`, `lxml`을 자동으로 처리).

## 사용

Claude Code에 PDF를 던지면서:

> "이 PDF로 SLCF 세미나 PPT 만들어줘. 발표자: 홍길동, 날짜: 26.5.10"

Claude가 자동으로 SKILL.md를 로드해 다음 3단계 수행:

1. **추출** — `references/extraction-protocol.md`의 LLM/Agent 도메인 룰에 따라 chapters / key_points / figures 정리
2. **Plan 작성** — `assets/plan-template.yaml` 기반 `myplan.yaml`
3. **Lint + 빌드** — `scripts/plan.py` 검증 → `scripts/build_from_plan.py` → `.pptx` 출력

상세 흐름·스키마·디자인 토큰: [`skills/slcf-seminar-pptx/SKILL.md`](skills/slcf-seminar-pptx/SKILL.md)

## 핵심 잠금 장치

| 잠금 | 어디 |
|---|---|
| 디자인 토큰 (색·폰트·그리드) | `assets/style.yaml` |
| 의미 단위 슬라이드 (좌표 박힘) | `scripts/builder.py` |
| Plan 스키마 + lint | `scripts/plan.py`, `references/plan-schema.md` |
| 도메인 추출 룰 (LLM/Agent 특화) | `references/extraction-protocol.md` |

## 로드맵

- **Phase 1 (현재)** — 단일 skill plugin. Claude의 PDF 읽기 능력에 의존.
- **Phase 2** — [anthropics/skills](https://github.com/anthropics/skills)의 `pdf` skill을 prerequisite로 채택해 raw 텍스트/표/이미지/OCR 추출 위임. 본 plugin은 의미 추출 (chapter importance, key_points 결정)에 집중.
- **Phase 3** — `seminar-extractor` / `seminar-planner` skill 분리 (실사용 데이터 쌓이면).

## 라이선스

MIT
