# schema-validator 스킬

## 역할

각 단계 산출물 파일의 구조(필수 섹션/필드)를 검증한다.

## 트리거 조건

각 단계 산출물 생성 직후 Orchestrator가 호출한다.

## 사용법

```bash
python .claude/skills/schema-validator/scripts/validate.py \
  --file "output/summaries/yt_abc123.md" \
  --schema "summary"
```

## 지원하는 스키마

| 스키마 이름 | 검증 대상 | 필수 요소 |
|---|---|---|
| `summary` | 요약 파일 | 3줄 요약 섹션, 핵심 인사이트 3개+, AX 관련성 태그 |
| `story_idea` | 글감 카드 | 제목, 앵글, 카테고리, 소스 목록, 핵심 논점 |
| `review` | 리뷰 파일 | 기밀 필터링 결과 섹션, critical_count, confidential_count, 팩트체크 섹션 |
| `brand_feedback` | 브랜드 피드백 | 가이드 항목 참조 포함 |
| `seo_feedback` | SEO 피드백 | 제목 최적화, 메타 디스크립션, 타겟 키워드, 헤딩 구조 섹션 |
| `draft` | 초고/수정본 | 제목, 메타 디스크립션, 카테고리 태그, 본문 1,500자+, 소스 크레딧 |

## 출력 형식

```json
{
  "valid": true,
  "schema": "summary",
  "file": "output/summaries/yt_abc123.md",
  "errors": []
}
```

실패 시:
```json
{
  "valid": false,
  "schema": "summary",
  "file": "output/summaries/yt_abc123.md",
  "errors": [
    "핵심 인사이트가 2개로 최소 3개 미만입니다.",
    "AX 관련성 태그가 없습니다."
  ]
}
```

## 실패 처리

- 검증 실패 시 Orchestrator에 오류 목록 반환
- Orchestrator가 해당 단계를 1회 재시도 지시
