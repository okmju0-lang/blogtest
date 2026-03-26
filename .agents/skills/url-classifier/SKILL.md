# url-classifier 스킬

## 역할

URL 목록을 받아 각 URL을 `youtube` 또는 `web`으로 분류한다.

## 트리거 조건

워크플로우 1 단계 0.5: URL 목록이 주어졌을 때 Orchestrator가 호출한다.

## 사용법

```bash
python .Codex/skills/url-classifier/scripts/classify_url.py --urls "URL1,URL2,URL3"
# 또는 파일로 전달
python .Codex/skills/url-classifier/scripts/classify_url.py --file urls.txt
```

## 분류 규칙

| 조건 | 분류 |
|---|---|
| 도메인이 `youtube.com`, `youtu.be`, `m.youtube.com` | `youtube` |
| 그 외 모든 URL | `web` |

## 출력 형식

```json
[
  {"url": "https://www.youtube.com/watch?v=xxx", "type": "youtube", "video_id": "xxx"},
  {"url": "https://example.com/article", "type": "web", "url_hash": "abc123"}
]
```

## 실패 처리

- URL 형식 오류: 해당 URL을 `{"url": "...", "type": "error", "reason": "invalid_url"}`로 반환
- 도메인 판별 불가: 기본값 `"web"` 적용
