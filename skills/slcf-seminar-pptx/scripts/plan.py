"""
SLCF 세미나 plan.yaml 로더 + 검증기 (lint).

PDF→PPT 흐름의 중간 단계. plan.yaml은 PDF에서 추출한 구조와 슬라이드 순서를
담은 canonical 표현. 이 모듈이 형식·일관성·커버리지를 검증해 빌드 전에 잡는다.

사용:
    from plan import load_plan, lint, format_results
    plan = load_plan('myplan.yaml')
    errors, warnings = lint(plan)

CLI:
    python scripts/plan.py myplan.yaml         # errors 있으면 exit 1

스키마 상세는 references/plan-schema.md.
"""
import sys
from collections import Counter
from pathlib import Path


# 현재 plan.yaml 스키마 버전 (semver MAJOR.MINOR)
# - MAJOR 변경: breaking (필드 rename/remove, 타입 변경). 옛 plan은 마이그레이션 필요.
# - MINOR 변경: additive (옵션 필드 추가). 옛 plan은 그대로 동작.
CURRENT_SCHEMA_VERSION = "1.0"


def _parse_version(v):
    """'1.0' → (1, 0). 형식 오류 시 None."""
    try:
        parts = str(v).split('.')
        return int(parts[0]), int(parts[1])
    except (ValueError, IndexError, AttributeError):
        return None


# 슬라이드 type별 필수 필드
REQUIRED_FIELDS = {
    'cover':          [],   # date/title은 paper에서 자동
    'toc':            ['items'],
    'section_header': ['num', 'title'],
    'title_content':  ['title', 'bullets'],
    'title_only':     ['title'],
    'definition':     ['term', 'definition'],
    'comparison':     ['title', 'headers', 'rows'],
    'process':        ['title', 'steps'],
    'two_content':    ['title', 'left_title', 'left_bullets',
                       'right_title', 'right_bullets'],
    'image':          ['title', 'image_path'],
    'conclusion':     ['takeaways'],
}
VALID_TYPES = set(REQUIRED_FIELDS)


def load_plan(path):
    """yaml에서 plan 객체 로드. yaml 미설치 시 명확한 에러."""
    try:
        import yaml
    except ImportError as e:
        raise RuntimeError(
            "pyyaml 미설치. `pip install pyyaml` 또는 `uv add pyyaml`."
        ) from e
    with open(path, 'r', encoding='utf-8') as f:
        return yaml.safe_load(f)


def lint(plan_dict):
    """plan을 검사. (errors, warnings) 두 리스트 반환.

    errors가 비어있지 않으면 빌드 차단. warnings는 출력만.
    """
    errors = []
    warnings = []

    if not isinstance(plan_dict, dict):
        return ['plan이 dict가 아닙니다 (yaml 파일이 비었거나 잘못됨)'], []

    # ----- schema_version -----
    sv = plan_dict.get('schema_version')
    cur = _parse_version(CURRENT_SCHEMA_VERSION)
    if sv is None:
        warnings.append(
            f"schema_version 필드 없음 — {CURRENT_SCHEMA_VERSION}으로 간주. "
            f"plan.yaml 맨 위에 `schema_version: \"{CURRENT_SCHEMA_VERSION}\"` 추가 권장"
        )
    else:
        parsed = _parse_version(sv)
        if parsed is None:
            errors.append(
                f"schema_version 형식 오류: {sv!r} — '1.0' 같은 'MAJOR.MINOR' 형태"
            )
        elif parsed[0] != cur[0]:
            errors.append(
                f"schema_version {sv}의 major가 빌더({CURRENT_SCHEMA_VERSION})와 다름 — "
                f"breaking change. references/plan-schema.md의 마이그레이션 가이드 참조"
            )
        elif parsed[1] > cur[1]:
            warnings.append(
                f"schema_version {sv}가 빌더({CURRENT_SCHEMA_VERSION})보다 새로움 — "
                f"plan.yaml의 새 필드 일부가 무시될 수 있음"
            )

    # ----- paper -----
    paper = plan_dict.get('paper') or {}
    total_pages = paper.get('total_pages') or 0
    if not isinstance(total_pages, int) or total_pages <= 0:
        errors.append("paper.total_pages가 없거나 0/음수")
    for f in ('title', 'presenter', 'date'):
        if not paper.get(f):
            errors.append(f"paper.{f}이(가) 비어 있음")

    # ----- extraction -----
    ex = plan_dict.get('extraction') or {}
    chapters = ex.get('chapters') or []
    if not chapters:
        errors.append("extraction.chapters가 비어 있음 — 최소 1개 챕터 필요")

    importance_sum = sum((c.get('importance') or 0) for c in chapters)
    if chapters and (importance_sum < 0.7 or importance_sum > 1.3):
        errors.append(
            f"chapter.importance 합 {importance_sum:.2f} — [0.7, 1.3] 범위 밖. "
            "각 챕터의 분량 비중을 다시 확인하세요"
        )

    # ----- chapter content quality (key_points / takeaway) -----
    # role 카탈로그는 강제하지 않음. 모든 챕터에 공통 적용되는 콘텐츠 품질만 검사.
    for ci, c in enumerate(chapters):
        cnum = c.get('num') or f'(idx {ci})'
        ctx = f"chapter {cnum}"
        imp = c.get('importance') or 0

        # takeaway — 모든 챕터 (importance 무관) 한 줄 요약 필수
        takeaway = (c.get('takeaway') or '').strip()
        if not takeaway:
            errors.append(f"{ctx}: takeaway가 비어 있음")
        elif len(takeaway) < 10:
            warnings.append(f"{ctx}: takeaway가 너무 짧음 ({len(takeaway)}자)")
        elif takeaway.upper().startswith('TODO'):
            errors.append(f"{ctx}: takeaway가 TODO로 시작 — 실제 내용으로 채우세요")

        # key_points — importance > 0.05인 챕터에만 강제
        if imp > 0.05:
            kp = c.get('key_points') or []
            if not isinstance(kp, list):
                errors.append(f"{ctx}: key_points는 리스트여야 함")
                continue
            if not kp:
                warnings.append(
                    f"{ctx}: key_points 비어있음 — 청중이 가져가야 할 것 3~5개 작성"
                )
                continue
            # 항목별 검증
            for ki, p in enumerate(kp):
                if not isinstance(p, str):
                    errors.append(f"{ctx}: key_points[{ki}]는 문자열이어야 함")
                    continue
                ps = p.strip()
                if not ps:
                    errors.append(f"{ctx}: key_points[{ki}] 비어있음")
                elif ps.upper().startswith('TODO'):
                    errors.append(
                        f"{ctx}: key_points[{ki}]이 TODO로 시작 — 실제 내용으로 채우세요"
                    )
                elif len(ps) < 12:
                    warnings.append(
                        f"{ctx}: key_points[{ki}] 길이 {len(ps)}자 — 너무 짧음 (12자 미만)"
                    )
            # 항목 수 권고 (importance 비례)
            if imp > 0.10 and len([p for p in kp
                                   if isinstance(p, str) and p.strip()]) < 2:
                warnings.append(
                    f"{ctx}: importance {imp:.2f}인데 key_points {len(kp)}개 — 너무 압축됨 (3~5개 권장)"
                )
            if imp > 0.20 and len([p for p in kp
                                   if isinstance(p, str) and p.strip()]) < 3:
                warnings.append(
                    f"{ctx}: importance {imp:.2f}인데 key_points 3개 미만 — 분량 대비 부실"
                )

    chapter_nums = {c.get('num') for c in chapters if c.get('num') is not None}
    figure_nums = {f.get('num') for f in (ex.get('figures') or [])
                   if f.get('num') is not None}
    table_nums = {t.get('num') for t in (ex.get('tables') or [])
                  if t.get('num') is not None}

    skipped = ex.get('skipped') or {}
    skipped_figures = set(skipped.get('figures') or [])
    skipped_chapters = set(skipped.get('chapters') or [])

    # ----- plan -----
    plan = plan_dict.get('plan') or []
    if not plan:
        errors.append("plan이 비어 있음")
        return errors, warnings

    if plan[0].get('type') != 'cover':
        errors.append(
            f"plan의 첫 항목은 cover여야 함 (현재: {plan[0].get('type')!r})"
        )

    types_in_plan = [s.get('type') for s in plan]
    if 'toc' not in types_in_plan:
        warnings.append("plan에 toc가 없음 (목차 슬라이드 권장)")
    if 'conclusion' not in types_in_plan:
        warnings.append("plan에 conclusion이 없음 (결론 슬라이드 권장)")
    else:
        last_conclusion = max(i for i, t in enumerate(types_in_plan)
                              if t == 'conclusion')
        if last_conclusion < len(plan) - 3:
            warnings.append(
                f"conclusion이 plan 끝에서 너무 멀리 있음 "
                f"(idx {last_conclusion} / {len(plan)-1})"
            )

    section_chapter_refs = []
    referenced_figures = set()
    referenced_tables = set()
    referenced_pages = set()

    for i, slide in enumerate(plan):
        t = slide.get('type')
        ctx = f"plan[{i}] (type={t})"

        if t not in VALID_TYPES:
            errors.append(
                f"{ctx}: 알 수 없는 type. 허용: {sorted(VALID_TYPES)}"
            )
            continue

        # 필수 필드
        for field in REQUIRED_FIELDS[t]:
            v = slide.get(field)
            if v is None or v == '' or v == [] or v == {}:
                errors.append(f"{ctx}: 필수 필드 '{field}' 누락 또는 비어 있음")

        # source_page 범위
        sp = slide.get('source_page')
        if sp is not None:
            if not (isinstance(sp, int) and 1 <= sp <= total_pages):
                errors.append(
                    f"{ctx}: source_page={sp}이 [1, {total_pages}] 범위 밖"
                )
            else:
                referenced_pages.add(sp)

        # ref 검증
        cr = slide.get('chapter_ref')
        if cr is not None:
            if cr not in chapter_nums:
                errors.append(
                    f"{ctx}: chapter_ref={cr}이 extraction.chapters에 없음"
                )
            elif t == 'section_header':
                section_chapter_refs.append(cr)

        fr = slide.get('figure_ref')
        if fr is not None:
            if fr not in figure_nums:
                errors.append(
                    f"{ctx}: figure_ref={fr}이 extraction.figures에 없음"
                )
            else:
                referenced_figures.add(fr)

        tr = slide.get('table_ref')
        if tr is not None:
            if tr not in table_nums:
                errors.append(
                    f"{ctx}: table_ref={tr}이 extraction.tables에 없음"
                )
            else:
                referenced_tables.add(tr)

        # type별 추가 검증
        if t == 'comparison':
            headers = slide.get('headers') or []
            for ri, row in enumerate(slide.get('rows') or []):
                if not isinstance(row, list) or len(row) != len(headers):
                    errors.append(
                        f"{ctx}: rows[{ri}] 길이가 headers({len(headers)})와 다름"
                    )

        if t in ('title_content', 'two_content', 'definition', 'conclusion'):
            for bf in ('bullets', 'left_bullets', 'right_bullets',
                       'why', 'examples', 'takeaways', 'next_steps'):
                items = slide.get(bf)
                if not items:
                    continue
                if not isinstance(items, list):
                    errors.append(f"{ctx}: '{bf}'은 리스트여야 함")
                    continue
                if len(items) > 6:
                    warnings.append(
                        f"{ctx}: '{bf}'에 {len(items)}항목 (6개 초과 — 글자 작아짐)"
                    )
                for bi, b in enumerate(items):
                    if isinstance(b, str) and len(b) > 80:
                        warnings.append(
                            f"{ctx}: '{bf}'[{bi}] 길이 {len(b)}자 (80자 초과)"
                        )

        if t == 'process':
            steps = slide.get('steps') or []
            if len(steps) > 7:
                warnings.append(
                    f"{ctx}: process steps {len(steps)}개 (7개 초과 권장)"
                )
            if len(steps) < 2:
                warnings.append(
                    f"{ctx}: process steps {len(steps)}개 (2개 미만 — 다이어그램 의미 약함)"
                )

        if t == 'image' and slide.get('image_path'):
            ip = Path(slide['image_path'])
            if ip.is_absolute() and not ip.exists():
                warnings.append(
                    f"{ctx}: image_path '{ip}'이 존재하지 않음"
                )

    # ----- 챕터 커버리지 -----
    section_chapters = set(section_chapter_refs)
    for c in chapters:
        cnum = c.get('num')
        if cnum in skipped_chapters:
            continue
        if cnum not in section_chapters and (c.get('importance') or 0) > 0.05:
            warnings.append(
                f"chapter {cnum} '{c.get('title')}'이(가) plan에 "
                f"section_header로 등장하지 않음 (importance={c.get('importance')})"
            )

    # 챕터별 슬라이드 수 vs importance 비례
    chapter_slide_count = _count_slides_per_chapter(plan, chapter_nums)
    total_chapter_slides = sum(chapter_slide_count.values())
    if total_chapter_slides > 0:
        for c in chapters:
            cnum = c.get('num')
            if cnum in skipped_chapters:
                continue
            imp = c.get('importance') or 0
            if imp < 0.05:
                continue
            actual = chapter_slide_count.get(cnum, 0)
            expected = imp * total_chapter_slides
            if expected >= 1.0:
                ratio = (actual / expected) if expected else 0
                if ratio < 0.5 or ratio > 1.7:
                    warnings.append(
                        f"chapter {cnum}: 슬라이드 {actual}장 vs importance "
                        f"{imp:.2f} 기준 ~{expected:.1f}장 권장 (±50% 이탈)"
                    )
            if actual <= 1 and imp > 0.10:
                warnings.append(
                    f"chapter {cnum}: importance {imp:.2f}인데 슬라이드 {actual}장 — 너무 압축됨"
                )

    # ----- figure 커버리지 -----
    for f in ex.get('figures') or []:
        fnum = f.get('num')
        if fnum in skipped_figures:
            continue
        if fnum in referenced_figures:
            continue
        if f.get('page') in referenced_pages:
            continue
        if f.get('importance') == 'low':
            continue
        warnings.append(
            f"figure {fnum} '{f.get('caption')}' (p.{f.get('page')}): "
            f"plan에 등장하지 않음 — figure_ref로 참조하거나 "
            f"extraction.skipped.figures에 명시"
        )

    # ----- 중복 검사 -----
    fr_counts = Counter(s.get('figure_ref') for s in plan
                        if s.get('figure_ref') is not None)
    for fnum, cnt in fr_counts.items():
        if cnt > 1:
            warnings.append(f"figure_ref={fnum}이 {cnt}번 사용됨 (중복)")

    tr_counts = Counter(s.get('table_ref') for s in plan
                        if s.get('table_ref') is not None)
    for tnum, cnt in tr_counts.items():
        if cnt > 1:
            warnings.append(f"table_ref={tnum}이 {cnt}번 사용됨 (중복)")

    term_counts = Counter(s.get('term') for s in plan
                          if s.get('type') == 'definition')
    for term, cnt in term_counts.items():
        if cnt > 1:
            warnings.append(f"definition term '{term}'이 {cnt}번 등장 (중복)")

    # ----- important 슬라이드 비율 -----
    body_slides = [s for s in plan
                   if s.get('type') not in ('cover', 'toc', 'conclusion')]
    if body_slides:
        important_count = sum(1 for s in body_slides if s.get('important'))
        important_ratio = important_count / len(body_slides)
        if important_count == 0:
            warnings.append(
                "본문 슬라이드 중 important: true가 0개 — "
                "발표의 결정적 슬라이드 1~5개에 표시하세요 (헤더가 노란색으로)"
            )
        elif important_ratio > 0.25:
            warnings.append(
                f"important: true가 본문의 {important_ratio:.0%} ({important_count}/"
                f"{len(body_slides)}장) — 강조는 25% 이하로. 너무 많으면 효과 사라짐"
            )

    return errors, warnings


def _count_slides_per_chapter(plan, chapter_nums):
    """section_header를 기점으로 다음 section_header 전까지를 한 챕터로 묶어 카운트.

    cover, toc는 챕터에 속하지 않음.
    """
    counts = {n: 0 for n in chapter_nums}
    current = None
    for s in plan:
        t = s.get('type')
        if t == 'section_header':
            current = s.get('num')
            if current in counts:
                counts[current] += 1
        elif current is not None and t not in ('cover', 'toc'):
            counts[current] = counts.get(current, 0) + 1
    return counts


def format_results(errors, warnings):
    """사람이 읽기 좋은 결과 출력 문자열."""
    lines = []
    if errors:
        lines.append(f"✗ ERRORS ({len(errors)}):")
        for e in errors:
            lines.append(f"  • {e}")
    if warnings:
        lines.append(f"⚠ WARNINGS ({len(warnings)}):")
        for w in warnings:
            lines.append(f"  • {w}")
    if not errors and not warnings:
        lines.append("✓ lint 통과 (errors 0, warnings 0)")
    elif not errors:
        lines.append(f"✓ errors 없음 (warnings {len(warnings)} — 빌드 가능)")
    return '\n'.join(lines)


def main():
    if len(sys.argv) < 2:
        print("usage: python scripts/plan.py <plan.yaml>", file=sys.stderr)
        sys.exit(2)
    path = sys.argv[1]
    plan = load_plan(path)
    errors, warnings = lint(plan)
    print(format_results(errors, warnings))
    sys.exit(1 if errors else 0)


if __name__ == '__main__':
    main()
