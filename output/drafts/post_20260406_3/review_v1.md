---
post_id: post_20260406_3
review_version: v1
reviewed_at: 2026-04-06
critical_count: 1
confidential_count: 0
---

## 종합 평가

초고는 MCP의 실무적 가치를 비전문가 독자에게 잘 전달하고 있으며, 소스 기반 서술이 충실하다. 논리 흐름(문제 제기 → 현장 예시 → 비교표 → 해결 방식 → 구조 설명 → 도입 시점 판단)이 자연스럽고, USB-C 비유도 적절하다. 팩트체크 결과 소스와의 수치/사실 불일치는 없었다. CTA 앞 구분선 포맷 위반 1건이 critical이며, frontmatter/H1 제목 불일치 등 정리 사항이 warning으로 존재한다.

## 팩트체크 결과

| 항목 | 초고 내용 | 소스 확인 | 판정 |
|---|---|---|---|
| 공개 MCP 서버 수 | "10,000개를 넘었고" | AAIF 소스: "more than 10,000 active public MCP servers" | PASS |
| 채택 플랫폼 목록 | "ChatGPT·Gemini·Microsoft Copilot·VS Code·Cursor" | AAIF 소스: "ChatGPT, Cursor, Gemini, Microsoft Copilot, Visual Studio Code" 일치 | PASS |
| 엔터프라이즈 인프라 지원 | "AWS·Google Cloud·Microsoft Azure가 엔터프라이즈 지원을 붙였고" | AAIF 소스: "AWS, Cloudflare, Google Cloud, and Microsoft Azure" (Cloudflare 누락했으나 전부라고 주장하지 않음) | PASS |
| SDK 월 다운로드 | "Python·TypeScript SDK 월 다운로드는 9,700만 회를 넘었습니다" | AAIF 소스: "97M+ monthly SDK downloads across Python and TypeScript" | PASS |
| Linux Foundation 기부 | "Anthropic이 Linux Foundation 산하 Agentic AI Foundation에 MCP를 기부" | AAIF 소스: 확인됨 — "donating the Model Context Protocol to the Linux Foundation's new Agentic AI Foundation" | PASS |
| Tasks/Elicitations 기능 | "AWS는 여기에 비동기 처리(Tasks)와 사용자 추가 입력 요청(Elicitations) 기능도 추가" | AWS 소스: Tasks(SEP-1686)와 Elicitations 상세 설명 확인 | PASS |
| Google 식당 에이전트 예시 | "재고 데이터베이스를 읽고, 노션 문서를 참고하고, 이메일로 공급사에 연락하는 에이전트" | Google 소스: PostgreSQL, Notion MCP, Mailgun MCP 사용하는 supply chain agent 확인 | PASS |
| OpenAI Apps SDK 설명 | "서버, 모델, UI를 맞물리게 하는 기반" | OpenAI 소스: "MCP is the backbone that keeps server, model, and UI in sync" | PASS |
| Microsoft 엔터프라이즈 관점 | "아이덴티티·신뢰·관측성·거버넌스가 함께 있어야 엔터프라이즈급이 된다" | Microsoft 소스: 8 essential components 중 Identity/Trust, Telemetry/Observability, Governance 확인 | PASS |
| Anthropic 원래 문제 인식 | "데이터와 도구에 닿지 못하는 에이전트는 실무에서 금방 막힌다" | Anthropic Intro 소스: "even the most sophisticated models are constrained by their isolation from data" | PASS |

## 피드백 목록

### [critical] CTA 블록 앞 구분선(`---`) 제거 필요

- **위치**: 91행 (CTA blockquote 바로 위의 `---`)
- **문제**: CTA blockquote 바로 앞에 `---` 구분선이 있다. 포맷 규칙(CTA 앞 `---` 없어야 함)에 위반된다.
- **수정 방향**: 91행의 `---`를 삭제한다. 마지막 본문 단락과 CTA 사이에는 빈 줄 하나만 둔다.

### [warning] frontmatter title과 H1 제목 불일치

- **위치**: 3행(frontmatter) vs 23행(H1)
- **문제**: frontmatter title은 "AI 에이전트 붙일 때마다 코드가 쌓인다면, MCP부터 보세요"인데, H1은 "AI 에이전트를 붙일수록 코드가 쌓인다면, 이 표준을 먼저 보세요"로 다르다. 발행 시 어느 쪽이 실제 제목인지 혼동이 생긴다.
- **수정 방향**: 제목 확정(단계 1.5) 후 frontmatter title과 H1을 동일하게 맞춘다.

### [warning] 제목 후보 섹션이 본문에 잔존

- **위치**: 103~107행 (`## 제목 후보` 이하)
- **문제**: 제목 후보 A/B/C 리스트는 Orchestrator/담당자용 메타 정보이며, 블로그 본문에 포함될 내용이 아니다.
- **수정 방향**: 최종본 생성 시 `## 제목 후보` 섹션 전체를 제거한다. (현재 단계에서는 제목 선택용으로 워크플로우상 허용 가능하나, 이후 반드시 삭제 확인 필요.)

### [warning] Google 소스가 frontmatter source_refs에 누락

- **위치**: frontmatter `source_refs` (14~20행) 및 참고 자료 섹션 (93~99행)
- **문제**: 본문에서 Google의 식당 공급망 에이전트 예시를 상세히 인용하고 있으나, `source_refs`에 `web_mcp_google_agent_protocols.md`가 포함되어 있음에도 참고 자료 링크의 URL이 소스 파일의 실제 URL(`https://developers.googleblog.com/developers-guide-to-ai-agent-protocols/`)과 다르다. 참고 자료의 Google 링크는 `https://developers.google.com/assistant/agent-protocols`로 되어 있다.
- **수정 방향**: 참고 자료의 Google URL을 소스 파일의 실제 URL인 `https://developers.googleblog.com/developers-guide-to-ai-agent-protocols/`로 수정하거나, 실제 접근 가능한 URL로 확인 후 교체한다.

### [warning] 참고 자료 앞 구분선 위치 재검토

- **위치**: 101행 (`---` 바로 아래 `**참고 자료**`)
- **문제**: CTA 앞 `---`(91행)가 삭제되면 CTA와 참고 자료 사이의 시각적 구분이 달라진다. 참고 자료 앞 `---`는 CTA와의 구분용으로 유지할 수 있으나, 전체 구분선 배치를 재검토할 필요가 있다.
- **수정 방향**: CTA 앞 `---` 삭제 후, CTA 뒤 참고 자료 앞에만 `---`를 유지하는 것이 적절하다.

## 기밀 필터링 결과

기밀 항목 없음. 모든 내용이 공개 소스(Anthropic, OpenAI, Microsoft, AWS, Google 공식 블로그/문서)에 기반하며, 내부 브리핑이나 비공개 정보는 포함되지 않았다. 개인정보(이메일, 전화번호 등)도 발견되지 않았다.

## 포맷 검토

- `##` 섹션 앞 `---` 구분선: 모든 `##` 섹션(33, 43, 56, 64, 73행) 앞에 있음 — PASS
- CTA 앞 `---` 금지: 91행에 구분선 존재 — FAIL (삭제 필요)
- CTA 형식: 마크다운 blockquote(`>`) 사용 — PASS
- 인라인 HTML: 없음 — PASS
- 단락 간 빈 줄: 충분한 줄바꿈 확보 — PASS
- 참고 자료 형식: 링크 포함 목록 — PASS
