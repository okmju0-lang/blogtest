---
source_id: web_ms_graphrag_official
source_type: web
original_url: https://microsoft.github.io/graphrag/
summarized_at: 2026-03-30 10:05
---

## 3줄 요약

1. GraphRAG는 Microsoft Research가 개발한 구조화된 계층적 RAG 접근법으로, 일반 벡터 검색 기반 RAG와 달리 지식 그래프를 활용한다.
2. 원본 텍스트에서 엔티티/관계를 추출하고, Leiden 클러스터링으로 커뮤니티 계층을 구축한 뒤, 커뮤니티 요약을 생성하여 쿼리 시 활용한다.
3. Global Search(전체 요약 질의), Local Search(특정 엔티티 탐색), DRIFT Search(커뮤니티 맥락 포함 탐색), Basic Search(기본 벡터 검색) 등 4가지 쿼리 모드를 제공한다.

## 핵심 인사이트

1. **기존 RAG의 한계 명확화**: Baseline RAG는 분산된 정보 간 연결("점 잇기")과 대규모 데이터의 전체적 의미 파악에 취약하다.
2. **계층적 클러스터링의 힘**: Leiden 알고리즘 기반 커뮤니티 구조가 데이터셋 전체의 의미적 구조를 사전에 파악하게 해준다.
3. **다중 쿼리 모드**: 질문 유형에 따라 Global/Local/DRIFT/Basic 검색을 선택할 수 있어 유연성이 높다.

## AX 관련성

- **태그**: 기술트렌드
- **관련성 설명**: 기업 내부 비공개 데이터(사내 문서, 커뮤니케이션 등)에 대한 LLM 활용 능력을 획기적으로 개선하는 기술로, AX 도입 시 지식 관리와 의사결정 지원에 직접적으로 적용 가능하다.
