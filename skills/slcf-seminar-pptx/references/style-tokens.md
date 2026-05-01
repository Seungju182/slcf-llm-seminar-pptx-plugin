# style.yaml 스키마 레퍼런스

`assets/style.yaml`은 SLCF 세미나 양식의 모든 시각 결정사항을 한곳에 모아둡니다.
이 파일을 변경하면 모든 슬라이드 산출물의 톤이 즉시 바뀝니다.

## 로드 흐름

1. 모듈 임포트 시 `scripts/style.py`가 yaml 파일을 읽어 `STYLE` 싱글턴 생성
2. `SeminarBuilder()`가 인스턴스 속성 `self.style`에 STYLE 참조를 보관
3. 모든 의미 단위 메서드는 `self.style.{colors,fonts,sizes,grid,spacing}` 참조
4. yaml이 없거나 파싱 실패 시 `style.py`의 `_DEFAULTS` 딕셔너리 fallback (빌드는 멈추지 않음)

다른 yaml로 빌드: `SeminarBuilder('out.pptx', style_path='custom.yaml')`

## 섹션별 키

### `colors` — 모든 hex `#RRGGBB`

| 키 | 기본값 | 용도 |
|---|---|---|
| `body_text` | `#000000` | 본문 글씨. 양식 기본 파란색을 강제로 덮어씀 |
| `accent_red` | `#C00000` | 강조 — 챕터 번호, 섹션 헤더, 강조 박스 |
| `header_bg_black` | `#000000` | 표 헤더 배경, `add_box` 강조 박스 |
| `header_text` | `#FFFFFF` | 헤더 위 글씨 |
| `muted_gray` | `#A0A0A0` | 부가 정보, 캡션, 화살표 |
| `light_gray` | `#E8E8E8` | 정의 박스, 보조 영역 |
| `divider_gray` | `#D0D0D0` | (예약) 구분선 |

### `fonts` — 시스템에 설치되어 있어야 함

| 키 | 기본값 | 용도 |
|---|---|---|
| `korean` | `맑은 고딕` | 한국어 글자 (East Asian) |
| `latin` | `Calibri` | 영문/숫자 |

### `sizes` — pt 단위

10단계의 의미 위계. 발표자가 즉흥으로 폰트 크기를 정할 일이 없도록 모든 메서드 default가 이 키를 참조합니다.

| 키 | 기본값 | 용도 |
|---|---|---|
| `section_number` | 60 | 챕터 표지의 큰 'Chapter N' |
| `section_title` | 36 | 챕터 표지의 큰 제목 |
| `slide_title` | 28 | 본문 헤더바 제목 (양식 기본값) |
| `arrow` | 24 | `→` 화살표 글리프 |
| `body` | 18 | 본문 불릿, 강조 박스 |
| `body_sub` | 14 | 보조 본문, `add_textbox` 기본 |
| `table_header` | 13 | 표 첫 행 |
| `diagram_label` | 12 | 다이어그램 박스 텍스트 |
| `table_body` | 12 | 표 본문 셀 |
| `caption` | 10 | 출처 표기 `(원문 p.45)` |

### `grid` — inch 단위

16:9 와이드 (13.33 × 7.5)에서 본문 영역과 컬럼 시스템.

| 키 | 기본값 | 의미 |
|---|---|---|
| `slide_w` | 13.33 | 슬라이드 가로 |
| `slide_h` | 7.5 | 슬라이드 세로 |
| `margin_l` | 0.6 | 좌측 여백 |
| `margin_r` | 0.6 | 우측 여백 |
| `header_bottom` | 1.5 | 헤더바 아래 — 본문 시작 y |
| `footer_top` | 6.9 | 푸터/로고 위 — 본문 끝 y |
| `col_gap` | 0.25 | 컬럼 사이 간격 |
| `num_columns` | 12 | 본문 너비를 12분할 |

**Grid 헬퍼** (`b.style.grid` 또는 `STYLE.grid`):

```python
g.content_left()    # 0.6
g.content_right()   # 12.73
g.content_top()     # 1.5
g.content_bottom()  # 6.9
g.content_width()   # 12.13
g.content_height()  # 5.4
g.col(2, of=12)     # 0번부터 시작, 2번 컬럼의 (left, width)
g.span(0, 6, of=12) # 0번부터 6칸을 합친 (left, width)
```

### `spacing` — inch

슬라이드 종류별 표준 간격. 의미 단위 메서드들이 참조.

| 키 | 기본값 | 용도 |
|---|---|---|
| `bullet_top` | 2.0 | (예약) `add_title_content`의 본문 시작 y |
| `box_padding_x` | 0.15 | 박스 텍스트 좌우 패딩 |
| `box_padding_y` | 0.10 | 박스 텍스트 상하 패딩 |
| `process_box_h` | 1.0 | `add_process` 박스 높이 |
| `process_arrow_w` | 0.6 | `add_process` 화살표 영역 너비 |

## 변경 거버넌스

- **개별 발표자는 yaml을 수정하지 않습니다.** 양식 관리자만 PR로 변경.
- 변경 시 `version` 필드 증가. 현재 `1`.
- 변경 PR에는 다음을 포함:
  - 변경 전/후 동일 슬라이드를 캡처한 스크린샷
  - 영향 받는 메서드 목록
  - 발표자에게 영향 있는 경우 공지 메시지

## 다른 연구실/양식으로 fork

`assets/style.yaml`을 새 파일로 복사하고 값만 바꾸면 다른 양식이 됩니다:

```python
SeminarBuilder('out.pptx', style_path='assets/other-lab-style.yaml')
```

폰트가 다르거나 색이 다른 lab은 yaml만 갈아끼우면 됨. `template.pptx`까지 함께
바꾸면 완전한 별도 양식.

## 새 토큰 추가 절차

1. `assets/style.yaml`에 키 추가
2. `scripts/style.py`의 `_DEFAULTS`에도 동일 키 + 기본값 추가 (fallback용)
3. `_Namespace` 또는 `Grid` 클래스에 헬퍼 메서드 필요하면 추가
4. 사용처(builder.py 메서드)에서 새 키 참조
5. 이 문서에 표 한 줄 추가
