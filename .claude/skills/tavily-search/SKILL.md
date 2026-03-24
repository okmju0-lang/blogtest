# tavily-search 스킬

## 역할

Tavily API를 사용하여 두 가지 목적의 웹 검색을 수행한다:
1. **주제 리서치**: 사용자가 제공한 주제 키워드를 기반으로 블로그 작성 소스를 수집한다.
2. **팩트체크**: Reviewer가 초고에서 검증이 필요한 주장을 식별했을 때 사실 여부를 확인한다.

## 트리거 조건

| 모드 | 트리거 | 호출 주체 |
|---|---|---|
| `research` | 워크플로우 1 단계 0.7: 주제 키워드만 입력된 경우 | Orchestrator |
| `factcheck` | 워크플로우 2 단계 2: Reviewer가 검증 필요한 주장 식별 시 | Reviewer |

## 사전 요구사항

```bash
pip install tavily-python
# 환경 변수 설정 필요
export TAVILY_API_KEY="your_api_key_here"
```

## 사용법

```bash
# 주제 리서치 (심층 검색, 결과 5개)
python .claude/skills/tavily-search/scripts/search.py \
  --query "MCP Model Context Protocol" --mode research --max_results 5

# 팩트체크 (기본 검색, 결과 3개)
python .claude/skills/tavily-search/scripts/search.py \
  --query "GPT-4 출시일" --mode factcheck --max_results 3
```

## 모드별 동작

### research 모드
- `search_depth`: "advanced" (심층 검색)
- `max_results`: 기본 5개
- 용도: 주제에 대한 포괄적인 정보 수집
- 결과에 URL, 제목, 본문 요약 포함
- 수집된 URL은 이후 `web-scraper`로 본문 전체를 추출할 수 있다.

### factcheck 모드 (기본)
- `search_depth`: "basic" (기본 검색)
- `max_results`: 기본 3개
- 용도: 특정 주장의 사실 확인
- 새로운 콘텐츠 추가를 위한 리서치 목적으로는 사용하지 않는다.

## 출력 형식

```json
{
  "success": true,
  "query": "검색어",
  "mode": "research",
  "answer": "Tavily가 생성한 요약 답변",
  "results": [
    {
      "title": "결과 제목",
      "url": "https://...",
      "content": "관련 내용 요약",
      "score": 0.95
    }
  ]
}
```

## 실패 처리

- API 오류: 최대 2회 자동 재시도
- 2회 재시도 후 실패: 해당 주장은 "미확인"으로 처리하고 review 파일에 기록
- 전체 Tavily 실패 (팩트체크): 팩트체크 섹션 스킵 + 로그 (논리 리뷰와 기밀 필터링은 계속 수행)
- 전체 Tavily 실패 (리서치): 사용자에게 URL 직접 제공을 요청
