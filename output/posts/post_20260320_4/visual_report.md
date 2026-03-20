---
post_id: post_20260320_4
category: Thought Leadership
created_at: 2026-03-20 14:02
visual_editor_version: 1
---

## Visual Editor 작업 리포트

### A. 로컬 이미지 매칭

- **결과**: 생략
- **사유**: `assets/images/` 디렉토리가 존재하지 않음. 매칭 가능한 로컬 이미지 없음.

### B. 웹 스크린샷 캡처

| # | 대상 | URL | 파일 | 크기 | 삽입 위치 |
|---|---|---|---|---|---|
| 1 | OpenAI Symphony GitHub | https://github.com/openai/symphony | images/screenshot_1.png | 88,215 bytes | "Harness Engineering 실험" H2 직후 |
| 2 | Linear (프로젝트 관리 도구) | https://linear.app | images/screenshot_2.png | 86,851 bytes | "개발 조직 AX, 어디서부터 시작해야 할까요?" H2 직후 |

- 모든 스크린샷에 출처 URL 캡션 포함 완료.

### C. 다이어그램 생성

| # | 유형 | 설명 | 소스 파일 | PNG 파일 | 크기 | 삽입 위치 |
|---|---|---|---|---|---|---|
| 1 | flowchart | Harness Engineering 4대 핵심 요소 + 엔지니어 역할 전환 개념도 | images/diagram_1.mmd | images/diagram_1.png | 32,183 bytes | "Harness Engineering이 요구하는 것들" H3 직후 |

- Thought Leadership 컬러 팔레트 적용: 메인 #4A148C, 서브 #F3E5F5, 강조 #FFD600
- mmdc로 PNG 렌더링 성공.

### D. post.md 갱신

- 본문 텍스트 변경: 없음 (이미지 마크다운만 추가)
- 삽입된 이미지 총 3장:
  1. `screenshot_1.png` — "Harness Engineering 실험" 섹션 시작부
  2. `diagram_1.png` — "Harness Engineering이 요구하는 것들" 소제목 직후
  3. `screenshot_2.png` — "개발 조직 AX, 어디서부터 시작해야 할까요?" 섹션 시작부
- 모든 이미지에 alt_text 포함 완료.

### 이미지 총괄

| 유형 | 수량 | 비고 |
|---|---|---|
| 로컬 이미지 매칭 | 0장 | assets/images 미존재 |
| 웹 스크린샷 | 2장 | GitHub, Linear |
| 다이어그램 | 1장 | Mermaid flowchart |
| **합계** | **3장** | 섹션당 1장 규칙 준수 |
