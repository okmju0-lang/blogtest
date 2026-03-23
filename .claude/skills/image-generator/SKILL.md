# image-generator 스킬

## 역할

Nano Banana 2 (`gemini-3.1-flash-image-preview`) API를 사용하여 블로그 포스트용 이미지를 생성한다.
블로그 글 최종본 작성 후, 핵심 내용 2가지 일러스트 + 종합 썸네일 1장 = 총 3장을 생성한다.

## 트리거 조건

워크플로우 2 단계 8: 텍스트 최종본(`draft_final.md`) 확정 후 Orchestrator가 호출한다.

## 사전 요구사항

- `GOOGLE_AI_API_KEY` 환경 변수 설정 (Google AI Studio에서 발급)
- `pip install google-genai` (google-genai SDK 설치)

## 이미지 생성 전략

API 비용 최소화를 위해 포스트당 정확히 **3회** API 호출로 제한한다:

| 순번 | 유형 | 비율 | 용도 |
|---|---|---|---|
| 1 | thumbnail | 16:9 | 블로그 상단 대표 이미지. 글 전체 내용을 종합적으로 시각화 |
| 2 | illustration | 4:3 | 핵심 내용 1에 대한 일러스트 |
| 3 | illustration | 4:3 | 핵심 내용 2에 대한 일러스트 |

## 사용법

### 일괄 생성 (권장)

```bash
python .claude/skills/image-generator/scripts/generate_image.py batch \
    --post-dir output/drafts/post_20260323_1 \
    --thumbnail-prompt "..." \
    --illustration1-prompt "..." \
    --illustration2-prompt "..."
```

### 개별 생성

```bash
python .claude/skills/image-generator/scripts/generate_image.py single \
    --type illustration \
    --prompt "..." \
    --output output/drafts/post_20260323_1/images/illustration_1.png
```

## 프롬프트 작성 규칙

Orchestrator(LLM)가 `draft_final.md`를 분석하여 프롬프트를 작성한다. API는 이미지 생성에만 사용한다.

### 썸네일 프롬프트

```
Professional blog thumbnail, [글 전체 주제를 시각적으로 표현하는 설명],
[카테고리별 스타일 키워드], clean modern design, high resolution, no text, no words
```

### 일러스트 프롬프트

```
Evocative illustration depicting [핵심 내용과 어울리는 장면/비유를 구체적으로 묘사],
professional editorial style, [카테고리별 컬러 팔레트],
high resolution, detailed, no text, no words, no letters
```

## 출력 파일

| 파일 | 경로 |
|---|---|
| 썸네일 | `output/drafts/{post_id}/images/thumbnail.png` |
| 일러스트 1 | `output/drafts/{post_id}/images/illustration_1.png` |
| 일러스트 2 | `output/drafts/{post_id}/images/illustration_2.png` |

## 사양

| 항목 | 값 |
|---|---|
| 모델 | gemini-3.1-flash-image-preview (Nano Banana 2) |
| SDK | google-genai |
| 썸네일 비율 | 16:9 |
| 일러스트 비율 | 4:3 |
| 출력 형식 | PNG |
| API 호출 횟수 | 포스트당 최대 3회 |
| 폴백 | 없음 (API 실패 시 재시도 1회 후 에스컬레이션) |

## 참조 파일

- `references/image-style-guide.md` — 카테고리별 이미지 스타일 가이드

## 성공 기준

- 3장 모두 생성 완료 (각 파일 10KB 이상)

## 실패 처리

- API 오류: 이미지당 1회 재시도 (간격 5초)
- API 키 오류 (401/403): 즉시 중단 + 사용자 안내
- 2장 이상 실패 시: Orchestrator에 에스컬레이션

## 비용 최적화 원칙

- API 호출은 **이미지 생성에만** 사용한다. 텍스트 분석/프롬프트 생성은 LLM이 직접 수행.
- 포스트당 3회 호출 엄수. 추가 이미지가 필요하면 담당자 승인 후에만 생성.
- 프롬프트 실패 시 프롬프트를 수정하여 재시도하되, 새로운 이미지를 추가 생성하지 않는다.
