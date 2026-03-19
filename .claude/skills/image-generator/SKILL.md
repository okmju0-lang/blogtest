# image-generator 스킬

## 역할

Gemini API (Nano Banana 2)를 사용하여 AI 이미지를 생성한다.

## 트리거 조건

워크플로우 2 단계 8b: `image_spec.md`의 `thumbnail` 또는 `illustration` 타입 항목에 대해 Orchestrator가 호출한다.

## 사전 요구사항

```bash
pip install google-genai
# 환경 변수 설정 필요
export GOOGLE_AI_API_KEY="your_api_key_here"
```

## 사용법

```bash
python .claude/skills/image-generator/scripts/generate_image.py \
  --prompt "이미지 프롬프트" \
  --type "thumbnail" \
  --output "output/drafts/post_id/images/thumb_01.png"
```

## API 사양

| 항목 | 값 |
|---|---|
| 모델 | `gemini-3.1-flash-image-preview` |
| SDK | `google-genai` (Python) |
| 썸네일 해상도 | 1920×1080 (16:9) |
| 본문 삽입 해상도 | 1024×1024 (1:1) |
| 출력 형식 | PNG |
| API 키 | 환경 변수 `GOOGLE_AI_API_KEY` |

## 참조 파일

- `references/image-style-guide.md` — 카테고리별 이미지 스타일 가이드

## 성공 기준

- PNG 파일 생성됨
- 파일 크기 > 10KB (최소 해상도 확인)

## 실패 처리

- API 오류: 최대 2회 자동 재시도
- 2회 재시도 후 실패: Orchestrator에 보고 (해당 이미지 생성 실패)

## 주의사항

- SynthID 워터마크 포함 허용
- 프롬프트에 텍스트 포함 이미지 요청 지양 (AI 이미지의 텍스트 오류 위험)
- 생성된 이미지의 저작권은 Google의 이용약관을 따름
