# 이미지 스타일 가이드

> 이 가이드는 블로그 콘텐츠의 시각적 방향성을 정의한다.
> 포스트당 3장 (썸네일 1 + 본문 이미지 2) 생성에 적용된다.

---

## 썸네일 디자인 시스템

### 설계 원칙

모든 썸네일은 카테고리별로 차별화된 시각 언어를 사용하되, 다음 공통 요소로 브랜드 일관성을 유지한다.

| 공통 요소 | 규격 |
|---|---|
| 비율 | 16:9 |
| 매직에꼴 로고 | 우상단 고정 (흰색 버전, 투명 배경 PNG) |
| 카테고리 뱃지 | 좌상단 라운드 뱃지 (카테고리별 색상) |
| 제목 텍스트 | 좌측 정렬, 굵은 산세리프, 2~3줄 이내 |
| 텍스트 요약 규칙 | 원제목이 25자 초과 시 핵심 키워드 중심으로 요약 |

> **로고 파일**: `assets/logo_white.png` (추후 추가 예정). 로고 파일이 없으면 로고 삽입을 스킵하고 텍스트+그래픽만으로 구성한다.

### 제목 텍스트 처리 규칙

- 원제목 25자 이내: 그대로 사용
- 원제목 25자 초과: 핵심 키워드 2~3개를 추출하여 임팩트 있는 숏카피로 재구성
- 예시: "건설사 입찰 자동화로 처리 시간 80% 단축한 사례" → "입찰 자동화, 처리시간 80% 단축"
- 줄바꿈: 의미 단위로 2~3줄 분리 (한 줄 최대 12자 내외)
- 폰트: 굵은 산세리프 (Pretendard Bold 또는 동급)
- 색상: 흰색 기본. 배경이 밝으면 검정 또는 다크톤

---

### 카테고리별 썸네일 설계

#### 1. AI Trend (월요일) — 그래픽 타이포 스타일

**레퍼런스**: flex.team AXhub 블로그

```
+------------------------------------------+
| [AI Trend]              (magicecole logo) |
|                                          |
|  굵은 한글 제목                          |
|  2~3줄                          [나노바나나2]|
|                                 [추상 그래픽]|
|                                          |
+------------------------------------------+
```

| 요소 | 상세 |
|---|---|
| 배경 | 네온 블루~퍼플 그라디언트 단색 |
| 뱃지 색상 | 반투명 화이트 (`rgba(255,255,255,0.15)`) |
| 우측 그래픽 | 나노바나나2로 생성한 추상 기술 일러스트 (와이어프레임, 뉴럴넷, 데이터 흐름) |
| 제목 색상 | 흰색, 핵심 키워드는 밝은 시안으로 강조 가능 |
| 분위기 | 미래지향적, 역동적, "새로운 것이 왔다" |

**나노바나나2 프롬프트 방향** (우측 그래픽 요소 전용):
```
Abstract futuristic technology element, wireframe neural network visualization,
floating geometric shapes, neon blue and purple glow, transparent background style,
clean isolated graphic element, no text, no words, no letters
```

---

#### 2. Thought Leadership (수요일) — 개념적 그래픽 스타일

**레퍼런스**: flex.team + spartaclub sparta-story 혼합

```
+------------------------------------------+
| [Insight]               (magicecole logo) |
|                                          |
|  굵은 한글 제목                          |
|  핵심 키워드 강조색          [나노바나나2]  |
|                             [개념적 비주얼] |
|                                          |
+------------------------------------------+
```

| 요소 | 상세 |
|---|---|
| 배경 | 딥 블루~다크네이비 단색 |
| 뱃지 색상 | 반투명 화이트 |
| 우측 그래픽 | 나노바나나2로 생성한 개념적 메타포 일러스트 (퍼즐, 미로, 전환점, 연결) |
| 제목 색상 | 흰색, 핵심 키워드를 골드/앰버로 강조 |
| 분위기 | 사유적, 문제→해결 전환, "깊이 있는 관점" |

**나노바나나2 프롬프트 방향** (우측 그래픽 요소 전용):
```
Abstract conceptual illustration, visual metaphor of transformation,
[문제→해결 메타포: 퍼즐/미로/빛/연결 등], dark blue background,
warm gold accent highlights, sophisticated and intellectual,
clean isolated graphic element, no text, no words, no letters
```

---

#### 3. Case Study / 실행 가이드형 (금요일) — 실사 기반 스타일

**레퍼런스**: spartaclub.kr 2025 스파르타 연말결산

```
+------------------------------------------+
| [Case Study]            (magicecole logo) |
|                                          |
|  +------------------------------------+  |
|  | 실제 사진 (풀블리드)                  |  |
|  | + 하단→상단 반투명 그라디언트 오버레이   |  |
|  |                                    |  |
|  |  굵은 흰색 헤드라인                  |  |
|  |  (성과 수치 포함)                   |  |
|  +------------------------------------+  |
+------------------------------------------+
```

| 요소 | 상세 |
|---|---|
| 배경 | **실제 사진** (담당자 제공) — 현장 사진, 서비스 UI, 업무 환경 등 |
| 오버레이 | 하단→상단 반투명 다크블루 그라디언트 (`rgba(0,20,60,0.7)` → 투명) |
| 뱃지 색상 | 반투명 화이트 |
| 제목 색상 | 흰색, 그림자(drop shadow) 적용하여 사진 위 가독성 확보 |
| 분위기 | 전문적, 신뢰감, "검증된 결과", 다큐멘터리 톤 |

**나노바나나2 미사용**. 썸네일은 실사 + 합성으로만 구성한다.

**사진 소스 워크플로우**:
1. 담당자에게 관련 사진을 요청한다 (현장, 서비스 화면, 업무 환경 등)
2. 사진을 `output/drafts/{post_id}/images/photo_source.jpg`로 저장한다
3. 합성 스크립트로 오버레이 + 텍스트 + 로고를 합성한다
4. 사진이 제공되지 않으면 담당자에게 재요청. 사진 없이는 썸네일을 생성하지 않는다

---

#### 4. Company News (비정기) — 상황별 분기

| 상황 | 썸네일 방식 |
|---|---|
| 현장 사진 있음 (행사, 강의, 시상 등) | Case Study와 동일한 실사 + 오버레이 + 로고 방식 |
| 현장 사진 없음 | 나노바나나2 그래픽 + 웜톤 배경 + 로고 합성 (AI Trend 방식과 유사하되 웜 컬러) |

**현장 사진 있을 때**:
| 요소 | 상세 |
|---|---|
| 배경 | 실제 행사/강의/시상 사진 |
| 오버레이 | 반투명 다크 그라디언트 |
| 제목 | 흰색 굵은 텍스트 |
| 분위기 | 공식적, 축하/성과, 긍정적 |

**현장 사진 없을 때**:
| 요소 | 상세 |
|---|---|
| 배경 | 웜 오렌지~앰버 단색 |
| 우측 그래픽 | 나노바나나2 생성 (마일스톤, 파트너십, 성장 메타포) |
| 제목 색상 | 검정 또는 다크브라운 |
| 분위기 | 밝고 긍정적 |

---

### 카테고리별 시각 요약

| 요소 | AI Trend (월) | Thought Leadership (수) | Case Study (금) | Company News |
|---|---|---|---|---|
| 배경 | 네온 블루+퍼플 | 딥 블루+네이비 | 실사 사진 | 실사 또는 웜 오렌지 |
| 그래픽 | 나노바나나2 추상 | 나노바나나2 개념적 | 없음 (사진) | 상황별 |
| 제목 강조색 | 시안 | 골드/앰버 | 흰색+그림자 | 상황별 |
| 뱃지 텍스트 | AI Trend | Insight | Case Study | News |
| 로고 | 흰색 우상단 | 흰색 우상단 | 흰색 우상단 | 흰색 우상단 |
| 주요 감성 | 미래지향, 역동 | 사유, 전환 | 신뢰, 검증 | 축하, 공식 |

---

## 본문 이미지 (일러스트 1, 2)

본문 이미지는 기존 방식대로 나노바나나2로 생성한다. 모든 카테고리 공통.

### 공통 원칙

- **기본은 텍스트 없는 일러스트**: 일반 일러스트 프롬프트 끝에는 `no text, no words, no letters`를 유지한다.
- **예외 규칙**: 인포그래픽, 다이어그램, 비교 차트처럼 텍스트가 필요한 시각물은 텍스트를 허용한다. 이 경우 한글을 1순위로 사용하고, 제품명·고유명사·약어처럼 꼭 필요한 경우에만 영문을 2순위로 허용한다.
- **사람 얼굴**: 특정 인물 묘사 지양. 실루엣 또는 추상적 표현 사용
- **저작권**: 실제 브랜드 로고, 특정 제품 묘사 금지
- **API 비용 절약**: 프롬프트를 명확하고 구체적으로 작성하여 재생성 최소화
- **시각적 정보 우선**: 가능하면 인포그래픽, 다이어그램, 비교 차트 등 정보를 담은 이미지를 생성. 단순 분위기 일러스트보다 데이터 시각화 형태 선호

### AI Trend (월요일) 본문 이미지

**일러스트 1** (핵심 기술 변화):
```
Futuristic illustration depicting [기존 방식 vs 새로운 방식의 대비],
cutting-edge technology aesthetic, neon blue and purple palette,
dynamic composition, cinematic lighting, high resolution,
no text, no words, no letters
```

**일러스트 2** (기업 적용 장면):
```
Professional corporate illustration showing [기업 업무 환경에서의 AI 활용 장면],
modern workplace setting, futuristic blue and purple tones,
clean and sophisticated, high resolution,
no text, no words, no letters
```

### Thought Leadership (수요일) 본문 이미지

**일러스트 1** (문제/원인 시각화):
```
Conceptual illustration depicting [문제 상황의 시각적 비유],
abstract artistic style, dark and moody atmosphere,
deep blue and navy palette, intellectual tone, high resolution,
no text, no words, no letters
```

**일러스트 2** (해결/실행 시각화):
```
Conceptual illustration depicting [해결 방향의 시각적 비유],
abstract artistic style, hopeful and clear atmosphere,
warm gold and bright palette, professional tone, high resolution,
no text, no words, no letters
```

### Case Study (금요일) 본문 이미지

**일러스트 1** (문제 → 솔루션 전환):
```
Evocative illustration depicting [기존 문제에서 AI 솔루션으로의 전환],
professional editorial style, clean tech aesthetic,
blue and white palette, transformation theme, high resolution,
no text, no words, no letters
```

**일러스트 2** (성과/임팩트):
```
Professional illustration showing [성과를 상징하는 시각적 비유],
clean corporate style, blue and white palette,
achievement and growth theme, data-driven aesthetic, high resolution,
no text, no words, no letters
```

### Company News 본문 이미지

**일러스트** (공통):
```
Evocative illustration depicting [뉴스 핵심 내용과 어울리는 장면],
professional corporate style, bright and warm palette,
celebratory atmosphere, high resolution, detailed,
no text, no words, no letters
```

---

## 프롬프트 품질 향상 팁

1. **구체적인 스타일**: "flat design", "isometric", "3D render", "watercolor" 등 명시
2. **분위기 키워드**: "cinematic", "minimalist", "vibrant", "serene" 등 추가
3. **텍스트 처리 규칙**: 일반 일러스트는 `no text, no words, no letters`를 유지하고, 인포그래픽/다이어그램은 한글 우선 텍스트 규칙을 명시한다
4. **품질 키워드**: `high resolution, professional, detailed` 포함
5. **일러스트 특화**: `data visualization`, `visual hierarchy`, `illustration style` 활용

---

## 구현 참고 (추후)

썸네일 합성 스크립트(`compose_thumbnail.py`)가 필요하며, 다음 기능을 포함해야 한다:

- 배경 생성 (단색 그라디언트 또는 실사 사진 리사이즈)
- 나노바나나2 그래픽 요소 합성 (AI Trend, Thought Leadership)
- 반투명 오버레이 적용 (Case Study, Company News 실사)
- 제목 텍스트 렌더링 (자동 줄바꿈, 요약, 강조색)
- 카테고리 뱃지 삽입
- 매직에꼴 로고 삽입 (`assets/logo_white.png`)
- 16:9 비율 출력

> 스크립트 구현은 별도 지시 시 진행한다.

---

*최종 업데이트: 2026-03-25 — 카테고리별 썸네일 차별화 설계 반영*
