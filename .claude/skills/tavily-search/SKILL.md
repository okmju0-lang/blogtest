# tavily-search 스킬

## 역할

Tavily API를 사용하여 팩트체크 목적의 웹 검색을 수행한다.

## 트리거 조건

Reviewer 에이전트가 초고에서 검증이 필요한 주장을 식별했을 때 호출한다.

## 사전 요구사항

```bash
pip install tavily-python
# 환경 변수 설정 필요
export TAVILY_API_KEY="your_api_key_here"
```

## 사용법

```bash
python .claude/skills/tavily-search/scripts/search.py --query "검색어" --max_results 3
```

## 출력 형식

```json
{
  "query": "검색어",
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

## 사용 제한

- **팩트체크 전용**: 소스 콘텐츠 내 주장의 사실 여부 확인 목적으로만 사용
- 새로운 콘텐츠 추가를 위한 리서치 목적으로 사용 금지

## 실패 처리

- API 오류: 최대 2회 자동 재시도
- 2회 재시도 후 실패: 해당 주장은 "미확인"으로 처리하고 review 파일에 기록
- 전체 Tavily 실패: 팩트체크 섹션 스킵 + 로그 (논리 리뷰와 기밀 필터링은 계속 수행)
