"""
plan.yaml → SLCF 세미나 PPT 빌드 디스패처.

빌드 전에 plan.lint를 자동 실행하고, errors가 있으면 차단(--no-strict로 우회).
slide의 type을 builder의 의미 단위 메서드에 1:1 매핑.

CLI:
    python scripts/build_from_plan.py myplan.yaml --out=발표.pptx
    python scripts/build_from_plan.py myplan.yaml --style=other-style.yaml --out=...

import:
    from build_from_plan import build_from_plan
    out = build_from_plan('plan.yaml', 'out.pptx', strict=True)
"""
import argparse
import sys
from pathlib import Path

# 같은 디렉터리의 builder/plan/style 모듈 보장
sys.path.insert(0, str(Path(__file__).parent))

from builder import SeminarBuilder  # noqa: E402
from plan import load_plan, lint, format_results  # noqa: E402


def _dispatch(b, slide, paper):
    """한 plan 항목을 builder 메서드로 매핑."""
    t = slide.get('type')
    imp = bool(slide.get('important'))

    if t == 'cover':
        # 표지는 important 무관 (이미 special한 슬라이드)
        return b.set_cover(
            date=slide.get('date') or paper.get('date'),
            title=slide.get('title') or paper.get('title'),
        )

    if t == 'toc':
        return b.add_toc(
            items=slide['items'],
            current=slide.get('current'),
            title=slide.get('title', '목차'),
            important=imp,
        )

    if t == 'section_header':
        return b.add_section_header(
            num=slide['num'],
            title=slide['title'],
            subtitle=slide.get('subtitle', ''),
            important=imp,
        )

    if t == 'title_content':
        return b.add_title_content(
            title=slide['title'],
            bullets=slide['bullets'],
            important=imp,
        )

    if t == 'title_only':
        # plan만으로는 콘텐츠 알 수 없음. 헤더만 만들고 사람이 후처리하도록.
        s = b.add_title_only(slide['title'], important=imp)
        if slide.get('notes'):
            # notes를 시각적으로 표시 (회색)
            g = b.style.grid
            b.add_textbox(
                s, f"[직접 후처리: {slide['notes']}]",
                left=g.content_left(),
                top=g.content_top() + 0.3,
                width=g.content_width(), height=0.6,
                font_size=b.style.sizes.body_sub,
                color=b.style.colors.muted_gray,
            )
        return s

    if t == 'definition':
        return b.add_definition(
            term=slide['term'],
            definition=slide['definition'],
            why=slide.get('why'),
            examples=slide.get('examples'),
            source_page=slide.get('source_page'),
            important=imp,
        )

    if t == 'comparison':
        return b.add_comparison(
            title=slide['title'],
            headers=slide['headers'],
            rows=slide['rows'],
            source_page=slide.get('source_page'),
            important=imp,
        )

    if t == 'process':
        return b.add_process(
            title=slide['title'],
            steps=slide['steps'],
            emphasize=slide.get('emphasize'),
            descriptions=slide.get('descriptions'),
            source_page=slide.get('source_page'),
            important=imp,
        )

    if t == 'two_content':
        return b.add_two_content(
            title=slide['title'],
            left_title=slide['left_title'],
            left_bullets=slide['left_bullets'],
            right_title=slide['right_title'],
            right_bullets=slide['right_bullets'],
            source_page=slide.get('source_page'),
            important=imp,
        )

    if t == 'image_grid':
        return b.add_image_grid(
            title=slide['title'],
            images=slide['images'],
            captions=slide.get('captions'),
            source_page=slide.get('source_page'),
            important=imp,
        )

    if t == 'image':
        s = b.add_title_only(slide['title'], important=imp)
        g = b.style.grid
        b.add_image(
            s, slide['image_path'],
            left=g.content_left() + 0.5,
            top=g.content_top() + 0.4,
            width=g.content_width() - 1.0,
        )
        if slide.get('caption'):
            b.add_textbox(
                s, slide['caption'],
                left=g.content_left(),
                top=g.content_bottom() - 0.5,
                width=g.content_width(), height=0.4,
                font_size=b.style.sizes.caption,
                color=b.style.colors.muted_gray,
                align='center',
            )
        if slide.get('source_page'):
            b._add_source_caption(s, slide['source_page'])
        return s

    if t == 'conclusion':
        return b.add_conclusion(
            takeaways=slide['takeaways'],
            next_steps=slide.get('next_steps'),
            title=slide.get('title', '결론'),
            important=imp,
        )

    raise ValueError(
        f"Unknown slide type: {t!r}. "
        "허용 type은 references/plan-schema.md 참조."
    )


def build_from_plan(plan_path, out_path, style_path=None, strict=True):
    """plan.yaml을 읽어 PPT 빌드.

    Args:
        plan_path: plan yaml 경로
        out_path: 출력 .pptx 경로
        style_path: 사용자 정의 style.yaml (선택). None이면 기본 스타일.
        strict: True면 lint errors 발생 시 SystemExit. False면 warning만.

    Returns:
        저장된 pptx의 절대 경로 (string)
    """
    plan_dict = load_plan(plan_path)
    errors, warnings = lint(plan_dict)
    print(format_results(errors, warnings))

    if errors and strict:
        raise SystemExit(
            f"\n빌드 차단: errors {len(errors)}개. "
            "plan.yaml을 수정한 뒤 다시 시도하세요. "
            "(우회: --no-strict)"
        )

    paper = plan_dict.get('paper') or {}
    plan = plan_dict.get('plan') or []

    b = SeminarBuilder(out_path, style_path=style_path)
    for i, slide in enumerate(plan):
        try:
            slide_obj = _dispatch(b, slide, paper)
            notes = slide.get('speaker_notes')
            if notes and slide_obj is not None:
                b.add_speaker_notes(slide_obj, notes)
        except Exception as e:
            raise RuntimeError(
                f"plan[{i}] (type={slide.get('type')!r}) 빌드 실패: {e}"
            ) from e

    return b.save()


def main():
    p = argparse.ArgumentParser(
        description="plan.yaml에서 SLCF 세미나 PPT 빌드"
    )
    p.add_argument('plan', help="plan.yaml 경로")
    p.add_argument('--out', default='/tmp/slcf_output.pptx',
                   help="출력 .pptx (기본 /tmp/slcf_output.pptx)")
    p.add_argument('--style', default=None,
                   help="사용자 정의 style.yaml (선택)")
    p.add_argument('--no-strict', action='store_true',
                   help="lint errors가 있어도 강제 빌드 (디버그용)")
    args = p.parse_args()

    out = build_from_plan(
        args.plan, args.out, args.style, strict=not args.no_strict
    )
    print(f"\n저장 완료: {out}")


if __name__ == '__main__':
    main()
