# slcf-llm-seminar-pptx-plugin

SLCF 연구실 LLM/Agent 도메인 PDF → 통일된 디자인의 세미나 발표자료(.pptx)를 자동 생성하는 Claude Code 플러그인.

## 설치

**먼저 Anthropic의 PDF skill을 설치**한 뒤 이 plugin을 설치합니다 (PDF 추출 정확도 향상).

```text
/plugin marketplace add anthropics/skills
/plugin install pdf

/plugin marketplace add https://github.com/Seungju182/slcf-llm-seminar-pptx-plugin
/plugin install slcf-seminar-pptx
```

의존: **uv** (스크립트의 PEP 723 inline deps 자동 처리).

## 사용

Claude Code에 PDF를 던지면서 자연어로 요청:

> "이 PDF로 SLCF 세미나 PPT 만들어줘. 발표자: 한수빈, 날짜: 26.5.10"

부분 범위 발표도 그대로:

> "이 PDF의 Chapter 10에 대해 30장으로 핵심 개념 위주로 만들어줘"

Claude가 추출 → plan.yaml 작성 → lint → `.pptx` 빌드까지 자동 진행.

상세 워크플로 / 스키마 / 디자인 토큰: [`skills/slcf-seminar-pptx/SKILL.md`](skills/slcf-seminar-pptx/SKILL.md)

## 라이선스

MIT
