---
source_id: web_mcp_openai_apps_sdk
source_type: web
original_url: https://developers.openai.com/apps-sdk/concepts/mcp-server/
summarized_at: 2026-04-06 10:35
---

## 3줄 요약

1. OpenAI는 MCP를 대규모 언어 모델 클라이언트를 외부 도구와 리소스에 연결하는 개방형 사양으로 설명한다.
2. Apps SDK에서는 MCP가 서버, 모델, UI를 함께 동기화하는 기반이며, 표준화된 wire format·인증·메타데이터를 통해 ChatGPT가 앱을 기본 도구처럼 이해하게 만든다.
3. 최소 MCP 서버는 도구 목록 제공, 도구 호출, UI 컴포넌트 반환이라는 세 가지 기능을 구현하며, 웹과 모바일 등 여러 클라이언트를 별도 코드 없이 지원할 수 있다.

## 핵심 인사이트

1. **MCP는 단순 툴 호출 규격이 아니다**: 구조화된 결과와 UI 메타데이터까지 포함해 앱 경험 전체를 표준화하려는 시도다.
2. **다중 클라이언트 재사용성이 크다**: 한 번 만든 커넥터를 ChatGPT 웹·모바일 등 여러 환경에서 재활용할 수 있다는 점이 운영 효율을 높인다.
3. **인증이 프로토콜 안에 들어온다**: OAuth 2.1, protected resource metadata 같은 요소를 공식 사양 차원에서 다루기 시작했다.

## AX 관련성

- **태그**: 기술트렌드, 앱연동, 보안
- **관련성 설명**: 기업이 AI 앱을 내부 시스템과 연결할 때 기능 연결뿐 아니라 인증과 UI 일관성까지 함께 설계해야 함을 보여준다.
