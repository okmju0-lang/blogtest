# 이미지 스타일 가이드

> 이 가이드는 블로그 이미지 생성의 **단일 권위 소스**다.
> 메모리의 피드백이 모두 반영되어 있으므로, 이 가이드만 따르면 된다.

---

## 핵심 원칙 (우선순위 순)

1. **본문 이미지는 시각적 정보 전달 우선**: 인포그래픽, 다이어그램, 비교 차트, 프로세스 흐름 등 데이터 시각화를 단순 분위기 일러스트보다 우선한다.
2. **썸네일은 추상 일러스트 유지**: 썸네일은 인포그래픽으로 바꾸지 않는다. 감성적 추상 일러스트로 시선을 끄는 역할.
3. **텍스트 검증 필수**: 텍스트가 포함된 이미지 생성 후 반드시 Read로 열어 깨짐/오타/잘림/중복을 확인한다. 이상 시 재생성.
4. **API 비용 최소화**: 포스트당 3회 호출 엄수. 프롬프트 작성은 LLM이 직접 수행.

---

## 포스트당 이미지 구성

| 순번 | 파일명 | 비율 | 용도 | 스타일 |
|---|---|---|---|---|
| 1 | `thumbnail.png` | 16:9 | 블로그 대표 이미지 | 추상 일러스트 (카테고리별 톤) |
| 2 | `illustration_1.png` | 4:3 | 핵심 내용 1 시각화 | **인포그래픽/다이어그램 우선**, 해당 없으면 일러스트 |
| 3 | `illustration_2.png` | 4:3 | 핵심 내용 2 시각화 | **인포그래픽/다이어그램 우선**, 해당 없으면 일러스트 |

---

## 썸네일 규격

모든 카테고리 공통으로 Nano Banana 2가 직접 생성한다. PIL 합성 없음.

| 공통 요소 | 규격 |
|---|---|
| 비율 | 16:9 |
| 스타일 | 추상 일러스트 (텍스트 없음) |
| 텍스트 | `no text, no words, no letters` 필수 |

### 카테고리별 썸네일 톤

| 카테고리 | 색감 | 분위기 키워드 |
|---|---|---|
| AI Trend | 네온 블루 + 퍼플 그라디언트 | 미래지향, 역동, 추상 기술 비주얼 |
| Thought Leadership | 딥 블루 + 다크네이비 | 사유, 전환, 개념적 메타포 |
| Case Study | 블루 + 화이트 | 전문적, 신뢰, 변환 |
| Company News | 웜 오렌지 + 앰버 | 밝고 긍정적, 성과 |

### 썸네일 프롬프트 템플릿

```
Abstract [카테고리 분위기] illustration depicting [글 전체 주제의 시각적 비유],
[카테고리 색감] palette, clean modern design, professional,
high resolution, no text, no words, no letters
```

---

## 본문 이미지 (illustration_1, illustration_2)

### 판단 기준: 인포그래픽 vs 일러스트

글 본문에 아래 요소가 있으면 **인포그래픽/다이어그램**으로 생성한다:

- 비교 데이터 (Before/After, A vs B)
- 프로세스/단계별 흐름
- 통계 수치, 퍼센트
- 카테고리 분류, 매트릭스
- 타임라인, 로드맵

위 요소가 없으면 일반 일러스트로 생성한다.

### 인포그래픽 프롬프트 규칙

인포그래픽/다이어그램 생성 시:

1. `no text` 키워드를 **넣지 않는다** (텍스트가 필요하므로)
2. **한글(Korean Hangul)을 1순위** 텍스트로 명시한다
3. 영문은 제품명/고유명사/약어(AI, API, CRM 등)에만 허용
4. `style_prompts.py`의 스타일 프리픽스를 활용할 수 있다

**인포그래픽 프롬프트 템플릿:**
```
[style_prompts.py 스타일 프리픽스 (선택)]
[시각화할 데이터/프로세스를 구체적으로 설명],
clean layout, professional infographic, high resolution.
All labels and text in Korean Hangul. Use English only for product names or acronyms.
```

**사용 가능한 스타일** (`style_prompts.py` 참조):

| 스타일 키 | 적합한 상황 |
|---|---|
| `graphic-recording` | 따뜻한 톤, 교육적 콘텐츠, 핸드드로잉 느낌 |
| `modern` | 테크/스타트업, 깔끔한 인디고+시안 |
| `minimal` | 흑백, 인쇄 친화적, 최소 장식 |
| `corporate` | 공식 발표, 네이비+골드, 임원 프레젠테이션 |

### 일반 일러스트 프롬프트 규칙

인포그래픽 대상이 아닌 경우:

1. `no text, no words, no letters` **필수**
2. 카테고리별 색감 적용
3. 사람 얼굴은 실루엣/추상 표현만
4. 실제 브랜드 로고/제품 묘사 금지

**일러스트 프롬프트 템플릿:**
```
Evocative illustration depicting [핵심 내용의 시각적 비유],
professional editorial style, [카테고리별 색감],
high resolution, detailed, no text, no words, no letters
```

### 카테고리별 본문 이미지 색감

| 카테고리 | 색감 방향 |
|---|---|
| AI Trend | 네온 블루 + 퍼플, 미래적 |
| Thought Leadership | 일러스트1: 다크 블루 (문제) → 일러스트2: 웜 골드 (해결) |
| Case Study | 블루 + 화이트, 클린 테크 |
| Company News | 밝고 따뜻한 컬러 |

---

## 텍스트 검증 절차 (필수)

이미지 생성 직후 **반드시** 다음을 수행한다:

1. Read로 생성된 이미지를 열어 시각적으로 확인
2. 검증 항목:
   - 글자 깨짐 (garbled/corrupted text)
   - 오타 (misspelling)
   - 문장 잘림 (truncated)
   - 라벨 중복 (같은 텍스트 2번 표시)
   - 의미 불일치 (프롬프트 의도와 다른 내용)
3. 이상 발견 시:
   - 어떤 텍스트가 어떻게 잘못됐는지 구체적으로 파악
   - 수정 프롬프트로 해당 이미지만 재생성
   - 재생성 후 다시 검증 (최대 2회 재시도)
4. `no text` 이미지(썸네일, 일반 일러스트)도 의도치 않은 텍스트가 삽입되지 않았는지 확인

---

## 프롬프트 품질 팁

1. **구체적 스타일**: "flat design", "isometric", "3D render", "watercolor" 등 명시
2. **분위기 키워드**: "cinematic", "minimalist", "vibrant", "serene" 등
3. **품질 키워드**: `high resolution, professional, detailed` 포함
4. **인포그래픽 특화**: `data visualization`, `visual hierarchy`, `clean layout` 활용

---

*최종 업데이트: 2026-03-26 — 피드백 통합 재구축 (인포그래픽 우선, 썸네일 스타일 유지, 텍스트 검증, compose 스크립트 폐기)*
