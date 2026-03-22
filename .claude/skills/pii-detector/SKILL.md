# pii-detector 스킬

## 역할

텍스트에서 개인정보(PII) 패턴을 정규식으로 탐지한다.

## 트리거 조건

Reviewer 에이전트가 기밀 필터링 수행 시 호출한다.

## 사용법

```bash
python .claude/skills/pii-detector/scripts/detect_pii.py --file "output/drafts/post_id/draft_v1.md"
# 또는 텍스트 직접 전달
python .claude/skills/pii-detector/scripts/detect_pii.py --text "검사할 텍스트"
```

## 탐지 패턴

| 유형 | 패턴 예시 |
|---|---|
| 이메일 주소 | `[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}` |
| 한국 전화번호 | `0\d{1,2}-\d{3,4}-\d{4}` |
| 주민등록번호 | `\d{6}-[1-4]\d{6}` |
| 사업자등록번호 | `\d{3}-\d{2}-\d{5}` |
| 신용카드 번호 | `\d{4}[\s-]\d{4}[\s-]\d{4}[\s-]\d{4}` |

## 출력 형식

```json
{
  "has_pii": true,
  "findings": [
    {
      "type": "email",
      "value": "example@company.com",
      "position": "단락 3, 문장 2"
    }
  ]
}
```

## 주의사항

- 정규식 탐지는 1차 필터. LLM이 맥락을 고려하여 최종 판정.
- 이메일/전화번호도 공개 정보(대표 이메일 등)일 수 있으므로 LLM이 맥락 확인 필요.
