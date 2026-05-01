# SLCF 세미나 양식 구조 참고

`assets/template.pptx`의 내부 구조 분석 결과. 새 슬라이드 종류를 추가하거나
양식이 업데이트됐을 때 참고하세요.

## 슬라이드 크기

- 16:9 와이드스크린: 13.33 × 7.5 inch (12,192,000 × 6,858,000 EMU)

## 양식에 포함된 슬라이드 (2장)

### Slide 0: 표지

- 레이아웃: `Blank`
- Shape 구성:
  - `object 4` (TEXT_BOX) — 좌하단 날짜 텍스트 ("25.4.24 세미나")
  - `object 5` (AUTO_SHAPE, blipFill) — 화면 상단 절반에 깔린 **뇌 이미지** (rId3 참조)
  - `부제목 2` (TEXT_BOX) — 우하단 연구실 정보 (3줄: lab명, 학과, URL)
- 배경: 어두운 색 (마스터 슬라이드)

### Slide 1: 본문 예시 (state space model)

- 레이아웃: `1_사용자 지정 레이아웃`
- Shape 구성:
  - `제목 2` (PLACEHOLDER) — 검정 헤더바의 흰 글씨 제목
  - `텍스트 개체 틀 3` (PLACEHOLDER) — 빨간 불릿 본문
  - `그림 3` (PICTURE) — 본문 영역의 예시 이미지

## 슬라이드 레이아웃 (11개)

`prs.slide_layouts` 인덱스 기준:

| idx | name | 용도 |
|-----|------|------|
| 0 | Section Header | 섹션 구분용. 큰 제목만 |
| 1 | 1_사용자 지정 레이아웃 | 검정 헤더 + 본문 영역 (양식 본문이 사용) |
| 2 | Title Only | 검정 헤더만 |
| 3 | 1_Two Content | 좌우 두 칸 본문 |
| 4 | 1_제목 및 내용 | 검정 헤더 + 본문 |
| 5 | 1_Title Slide | 표지 (어두운 배경) |
| 6 | 1_Title Only | 검정 헤더만 (다른 스타일) |
| 7 | Blank | 완전 빈 슬라이드 (페이지 번호 + 로고만) |
| 8 | 2_Title Slide | 좌측 검정 사이드바 표지 |
| 9 | 3_Title Slide | 표지 변형 |
| 10 | 2_사용자 지정 레이아웃 | 검정 헤더 + 빈 본문 |

**중요**: 빈 레이아웃을 직접 사용하면 표지 배경 이미지가 누락됩니다.
표지/본문은 반드시 양식의 슬라이드(SOURCE_SLIDE_INDEX)를 deep copy 해서 쓰세요.

## 미디어 파일

`ppt/media/` 안에:
- `image1.jpeg` — 표지 뇌 이미지 (rId3에서 참조)
- `image2.png` ~ `image5.png` — 본문 예시 이미지들

## 슬라이드 마스터 (3개)

다양한 디자인의 마스터가 있어 표지 변형이 가능. 일반 사용 시 첫 마스터로
충분합니다.

## XML 참조 패턴

### 이미지 참조 (blipFill)
```xml
<a:blipFill>
  <a:blip r:embed="rId3" cstate="print"/>
  <a:stretch><a:fillRect/></a:stretch>
</a:blipFill>
```

`r:embed` 값은 **슬라이드의 rels에 등록된 rId**. 슬라이드를 복제할 때 새
슬라이드의 rels에 같은 target_part로 관계를 추가하고, 새 rId로 교체해야 함.
`builder.py`의 `_clone_slide`가 자동 처리.

### 텍스트 서식
양식의 paragraph는 `<a:r>` 안에 폰트, 색상, 크기 등 모든 서식을 포함.
`text_frame.text = ...` 로 통째로 바꾸면 이 서식이 다 날아가므로,
첫 `run`의 텍스트만 교체하는 방식(`_set_text_in_shape`) 사용.

## 양식 업데이트 시 체크리스트

양식 파일이 새 버전으로 교체되면:
1. `extract-text assets/template.pptx`로 슬라이드 텍스트 확인
2. `python /mnt/skills/public/pptx/scripts/thumbnail.py assets/template.pptx`로 시각 확인
3. 표지 / 본문 슬라이드의 인덱스가 바뀌었는지 확인 → `SOURCE_SLIDE_INDEX` 업데이트
4. 이 문서도 업데이트
