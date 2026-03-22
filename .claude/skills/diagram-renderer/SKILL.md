# diagram-renderer 스킬

## 역할

Mermaid 코드의 문법을 검증하고 PNG/SVG로 렌더링한다.

## 트리거 조건

워크플로우 2 단계 8c: `image_spec.md`의 `diagram` 타입 항목에 대해 Orchestrator가 호출한다.

## 사전 요구사항

```bash
# Node.js 기반 Mermaid CLI
npm install -g @mermaid-js/mermaid-cli

# 또는 Python 기반 (문법 검증만)
pip install mermaid-py
```

## 사용법

```bash
# 문법 검증 + PNG 렌더링
python .claude/skills/diagram-renderer/scripts/render_mermaid.py \
  --input "output/drafts/post_id/images/diagram_01.mmd" \
  --output "output/drafts/post_id/images/diagram_01.png"
```

## 절차

1. Mermaid 코드를 `.mmd` 파일로 저장
2. 문법 파싱 검증
3. PNG로 렌더링
4. 성공 시 `.mmd` + `.png` 모두 유지

## 성공 기준

- Mermaid 문법 파싱 성공
- PNG 파일 생성됨

## 실패 처리

- 문법 오류: 오류 메시지를 Orchestrator에 반환 → LLM이 Mermaid 코드 수정 후 1회 재시도
- 렌더링 오류: 스킵 + `.mmd` 파일만 저장 (담당자가 수동 렌더링 가능)

## Mermaid 문법 가이드

LLM이 다이어그램을 작성할 때 참고:

```mermaid
%% 플로우차트 예시
flowchart LR
    A[시작] --> B{조건}
    B -->|Yes| C[처리]
    B -->|No| D[종료]

%% 시퀀스 다이어그램 예시
sequenceDiagram
    participant A as 사용자
    participant B as 시스템
    A->>B: 요청
    B-->>A: 응답

%% 파이 차트 예시
pie title 구성 비율
    "항목 A" : 40
    "항목 B" : 30
    "항목 C" : 30
```

**주의**: 한글 텍스트는 지원되나, 특수문자 사용 시 따옴표로 감싼다.
