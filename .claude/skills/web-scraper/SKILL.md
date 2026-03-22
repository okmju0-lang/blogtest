# web-scraper 스킬

## 역할

웹 URL에서 본문 텍스트를 추출하여 소스 파일로 저장한다.

## 트리거 조건

워크플로우 1 단계 1b: `web` 유형으로 분류된 URL에 대해 Orchestrator가 호출한다.

## 사전 요구사항

```bash
pip install requests beautifulsoup4 trafilatura
```

## 사용법

```bash
python .claude/skills/web-scraper/scripts/scrape_web.py --url "URL" --url_hash URL_HASH --output_dir output/sources
```

## 추출 전략

1. `trafilatura`로 본문 추출 시도 (1순위, 노이즈 제거 우수)
2. 실패 시 `BeautifulSoup`으로 `<article>`, `<main>`, `<p>` 태그 기반 추출 (2순위)

## 출력 파일 형식

`output/sources/web_{url_hash}.md`:

```markdown
---
source_id: web_{url_hash}
source_type: web
url: {원본 URL}
title: {페이지 제목}
extracted_at: {YYYY-MM-DD HH:MM:SS}
---

# {페이지 제목}

{본문 텍스트}
```

## 성공 기준

- 파일 생성됨
- 파일 내용이 100자 이상

## 실패 처리

| 오류 유형 | 처리 방법 |
|---|---|
| HTTP 4xx (로그인/페이월 등) | 스킵 + `output/sources/_skip_log.md`에 기록 |
| HTTP 5xx | 최대 2회 자동 재시도 후 스킵 + 로그 |
| 본문 추출 실패 (100자 미만) | 스킵 + 로그 |
| 네트워크 타임아웃 | 최대 2회 자동 재시도 후 스킵 + 로그 |

## 스킵 로그 형식

`output/sources/_skip_log.md`에 추가:
```
- {YYYY-MM-DD HH:MM} | web_{url_hash} | {오류 유형} | {URL}
```
