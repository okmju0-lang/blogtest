# image-generator 스킬

## 역할

별도의 외부 파이썬 스크립트나 API 키 없이, 안티그래비티 내장 도구(`generate_image`)를 활용하여 AI 이미지를 생성한다.

## 트리거 조건

워크플로우 2 단계 8b: `image_spec.md`의 `thumbnail` 또는 `illustration` 타입 항목에 대해 Orchestrator가 직접 호출한다.

## 사전 요구사항

- 안티그래비티 내장 도구(`generate_image`) 사용 (외부 라이브러리/API 키 불필요)

## 사용법

안티그래비티가 제공하는 `generate_image` 도구를 호출하여 지정된 프롬프트로 이미지를 생성한다:
1. `generate_image`를 통해 이미지를 생성. (`ImageName`, `Prompt` 전달)
2. 생성된 이미지가 아티팩트 저장소에 저장되면, 파일 복사/이동을 통해 `output/drafts/{post_id}/images/{image_name}.png` 위치로 이동시킨다.

## 사양

| 항목 | 값 |
|---|---|
| 모델 | 안티그래비티 내장 고품질 이미지 생성 모델 |
| SDK | 내장 Tool (generate_image) |
| 썸네일 해상도 | 최적화된 가로형 이미지 |
| 본문 삽입 해상도 | 최적화된 정방형/가로형 이미지 |
| 출력 형식 | PNG / WebP |
| API 키 | 불필요 |

## 참조 파일

- `references/image-style-guide.md` — 카테고리별 이미지 스타일 가이드

## 성공 기준

- 툴을 통해 이미지가 생성되고 목적 경로에 파일이 존재함

## 실패 처리

- 도구 오류(Prompt 정책 제한 등): 프롬프트를 조정하여 최대 2회 자동 재시도
- 2회 재시도 후 실패: Orchestrator에 보고 (해당 이미지 생성 실패)

## 주의사항

- 프롬프트에 텍스트 포함 이미지 요청 지양 (AI 이미지의 텍스트 오류 위험)
