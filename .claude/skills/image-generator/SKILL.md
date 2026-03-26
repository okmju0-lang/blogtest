# image-generator 스킬

## 역할

Nano Banana 2 (`gemini-3.1-flash-image-preview`) API를 사용하여 블로그 포스트용 이미지를 생성한다.

## 트리거 조건

워크플로우 2 단계 8: 텍스트 최종본(`draft_final.md`) 확정 후 Orchestrator가 호출한다.

## 사전 요구사항

- `GOOGLE_AI_API_KEY` 환경 변수 설정 (Google AI Studio에서 발급)
- `pip install google-genai` (google-genai SDK 설치)

## 이미지 생성 전략

포스트당 정확히 **3회** API 호출:

| 순번 | 유형 | 비율 | 스타일 방향 |
|---|---|---|---|
| 1 | thumbnail | 16:9 | **추상 일러스트** (카테고리별 톤). 인포그래픽 금지 |
| 2 | illustration | 4:3 | **인포그래픽/다이어그램 우선**. 해당 없으면 일러스트 |
| 3 | illustration | 4:3 | **인포그래픽/다이어그램 우선**. 해당 없으면 일러스트 |

### 본문 이미지 판단 기준

`draft_final.md`에 비교 데이터, 프로세스 흐름, 통계 수치, 분류 체계, 타임라인 등이 있으면 → 인포그래픽으로 생성.
없으면 → 일반 일러스트로 생성.

상세 스타일 규칙은 `references/image-style-guide.md` 참조.

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

## 생성 후 필수 절차: 텍스트 검증

이미지 생성 직후 **반드시** Read로 이미지를 열어 검증한다:

1. 텍스트 포함 이미지: 깨짐, 오타, 잘림, 중복, 의미 불일치 확인
2. 텍스트 없는 이미지: 의도치 않은 텍스트 삽입 여부 확인
3. 이상 발견 시: 수정 프롬프트로 해당 이미지만 재생성 (최대 2회)

## 출력 파일

| 파일 | 경로 |
|---|---|
| 썸네일 | `output/drafts/{post_id}/images/thumbnail.png` |
| 일러스트 1 | `output/drafts/{post_id}/images/illustration_1.png` |
| 일러스트 2 | `output/drafts/{post_id}/images/illustration_2.png` |

## 참조 파일

- `references/image-style-guide.md` — 카테고리별 스타일 + 프롬프트 템플릿 + 텍스트 검증 절차
- `scripts/style_prompts.py` — 인포그래픽 스타일 프리픽스 (graphic-recording, modern, minimal, corporate)

## 성공 기준

- 3장 모두 생성 완료 (각 파일 10KB 이상)
- 텍스트 검증 통과

## 실패 처리

- API 오류: 이미지당 1회 재시도 (간격 5초)
- API 키 오류 (401/403): 즉시 중단 + 사용자 안내
- 2장 이상 실패 시: Orchestrator에 에스컬레이션
