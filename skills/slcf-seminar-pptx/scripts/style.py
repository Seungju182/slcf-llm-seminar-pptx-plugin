"""
SLCF 세미나 양식의 디자인 토큰 로더.

assets/style.yaml을 읽어 Color/Font/FontSize/Grid/Spacing 객체를 만든다.
yaml이 없거나 파일이 없으면 모듈에 박힌 기본값을 사용한다.

사용:
    from style import STYLE
    STYLE.colors.body_text       # RGBColor
    STYLE.fonts.korean           # '맑은 고딕'
    STYLE.sizes.body             # 18
    STYLE.grid.col(3, of=12)     # (left_inch, width_inch) — 12분할 그리드의 3번째 열

직접 다른 yaml을 로드:
    from style import load_style
    s = load_style('/path/to/custom_style.yaml')
"""
from pathlib import Path
from pptx.dml.color import RGBColor

DEFAULT_STYLE_PATH = Path(__file__).parent.parent / 'assets' / 'style.yaml'

# yaml 미설치 시 동일 동작을 보장하는 기본값.
# style.yaml이 잠시 없거나 파싱 실패해도 빌드는 멈추지 않음.
_DEFAULTS = {
    'version': 1,
    'colors': {
        'body_text':        '#000000',
        'accent_red':       '#C00000',
        'header_bg_black':  '#000000',
        'header_text':      '#FFFFFF',
        'important_yellow': '#FFD700',
        'muted_gray':       '#A0A0A0',
        'light_gray':       '#E8E8E8',
        'divider_gray':     '#D0D0D0',
    },
    'fonts': {
        'korean': '맑은 고딕',
        'latin':  'Calibri',
    },
    'sizes': {
        'slide_title':    28,
        'section_title':  36,
        'section_number': 60,
        'body':           18,
        'body_sub':       14,
        'table_header':   13,
        'table_body':     12,
        'caption':        10,
        'diagram_label':  12,
        'arrow':          24,
    },
    'grid': {
        'slide_w':       13.33,
        'slide_h':        7.5,
        'margin_l':       0.6,
        'margin_r':       0.6,
        'header_bottom':  1.5,
        'footer_top':     6.9,
        'col_gap':        0.25,
        'num_columns':    12,
    },
    'spacing': {
        'bullet_top':       2.0,
        'box_padding_x':    0.15,
        'box_padding_y':    0.10,
        'process_box_h':    1.0,
        'process_arrow_w':  0.6,
    },
}


def _hex_to_rgb(hex_str):
    """'#C00000' → RGBColor(0xC0, 0x00, 0x00)."""
    s = hex_str.lstrip('#')
    return RGBColor(int(s[0:2], 16), int(s[2:4], 16), int(s[4:6], 16))


def _deep_merge(base, override):
    """override의 값으로 base를 덮어씀 (재귀)."""
    out = dict(base)
    for k, v in override.items():
        if isinstance(v, dict) and isinstance(out.get(k), dict):
            out[k] = _deep_merge(out[k], v)
        else:
            out[k] = v
    return out


class _Namespace:
    """dict를 점 표기로 접근하게 해주는 단순 래퍼."""
    def __init__(self, d):
        for k, v in d.items():
            setattr(self, k, v)


class Grid(_Namespace):
    """좌표 헬퍼 포함."""
    def content_left(self):
        return self.margin_l

    def content_right(self):
        return self.slide_w - self.margin_r

    def content_width(self):
        return self.slide_w - self.margin_l - self.margin_r

    def content_top(self):
        return self.header_bottom

    def content_bottom(self):
        return self.footer_top

    def content_height(self):
        return self.footer_top - self.header_bottom

    def col(self, n, of=None):
        """num_columns 분할 그리드의 n번째 열의 (left, width) 반환.

        of=None이면 self.num_columns 사용. n은 0-based.
        col_gap이 열 사이마다 들어감.
        """
        of = of or self.num_columns
        gap = self.col_gap
        total_gap = gap * (of - 1)
        col_w = (self.content_width() - total_gap) / of
        left = self.content_left() + n * (col_w + gap)
        return left, col_w

    def span(self, start, count, of=None):
        """start번째 열부터 count개를 합친 (left, width)."""
        of = of or self.num_columns
        gap = self.col_gap
        total_gap = gap * (of - 1)
        col_w = (self.content_width() - total_gap) / of
        left = self.content_left() + start * (col_w + gap)
        width = count * col_w + (count - 1) * gap
        return left, width


class Style:
    """모든 디자인 토큰을 한곳에 모아둔 객체."""
    def __init__(self, raw):
        self.version = raw.get('version', 1)
        self.colors = _Namespace({k: _hex_to_rgb(v) for k, v in raw['colors'].items()})
        self.fonts = _Namespace(raw['fonts'])
        self.sizes = _Namespace(raw['sizes'])
        self.grid = Grid(raw['grid'])
        self.spacing = _Namespace(raw['spacing'])
        self._raw = raw


def load_style(path=None):
    """style.yaml 로드. 실패하면 기본값으로 동작.

    Args:
        path: yaml 파일 경로. None이면 assets/style.yaml.
    """
    target = Path(path) if path else DEFAULT_STYLE_PATH
    raw = dict(_DEFAULTS)

    try:
        import yaml  # type: ignore
    except ImportError:
        yaml = None

    if yaml is not None and target.exists():
        try:
            with open(target, 'r', encoding='utf-8') as f:
                user = yaml.safe_load(f) or {}
            raw = _deep_merge(_DEFAULTS, user)
        except Exception as e:
            # yaml 파싱 실패 시 기본값으로 fallback (에러는 stderr에만)
            import sys
            print(f"[style] yaml 파싱 실패, 기본값 사용: {e}", file=sys.stderr)

    return Style(raw)


# 모듈 임포트 시 한번 로드 (기본 경로). 다른 yaml을 쓰려면 load_style(path)로 재호출.
STYLE = load_style()
