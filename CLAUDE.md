# AX 기업 블로그 에이전트 시스템 — Orchestrator 지침

## 프로젝트 개요

이 시스템은 AI Transformation(AX) 전문 기업의 공식 블로그를 위한 콘텐츠 생산 파이프라인이다.
외부 소스(YouTube, 웹 아티클) 큐레이션과 내부 브리핑을 기반으로 블로그 글을 체계적으로 생산한다.

**핵심 제약**: 블로그 글 본문 내용은 반드시 사용자가 제공한 소스(추출 텍스트 + 내부 브리핑)에만 의거한다. Orchestrator가 인터넷을 별도 리서치하여 새로운 주장이나 사례를 추가하지 않는다.

---

## 환경 사전 조건 확인

워크플로우를 시작하기 전에 Orchestrator는 다음을 확인한다.

| 확인 항목 | 확인 방법 | 실패 시 |
|---|---|---|
| `.env` 파일 존재 | 파일 존재 확인 | `.env.example`을 안내하고 사용자에게 API 키 설정 요청 |
| `TAVILY_API_KEY` 설정 | `.env` 읽기 | Reviewer 팩트체크 불가 — 사용자에게 경고 후 팩트체크 스킵 모드로 진행 가능 |
| `GOOGLE_AI_API_KEY` 설정 | `.env` 읽기 | 내부 도구(generate_image) 활용 시 불필요. 텍스트 처리용도로만 필요 |
| Playwright + Chromium 설치 | `python -c "from playwright.sync_api import sync_playwright"` | `pip install playwright && python -m playwright install chromium` 안내 |
| Python 의존성 설치 | `pip list` 또는 스크립트 실행 | `pip install -r requirements.txt` 실행 안내 |
| `output/` 디렉토리 구조 | 디렉토리 존재 확인 | `file-manager` 스킬로 자동 생성 |
| `brand-voice-guide.md` 존재 | 파일 존재 확인 | 브랜드 보이스 초기화 워크플로우 안내 (하단 참조) |

---

## 콘텐츠 카테고리 정의

| 카테고리 | 설명 | 주요 입력 소스 | 글 구조 |
|---|---|---|---|
| **Case Study** | 자체 프로젝트 사례, 솔루션 개발, 고객 AX 니즈 | 내부 브리핑 + 참고 URL (선택) | 과제 → 접근 방식 → 솔루션 → 성과/임팩트 |
| **Thought Leadership** | AX 경영전략, 리더십, 컨설팅, HR AX | 내부 브리핑 + 외부 소스 혼합 | 이슈 제기 → 분석/근거 → 인사이트 → 실무 시사점 |
| **Company News** | 강의, 시상, 정부사업 수주 등 대외 활동 | 내부 브리핑 + 참고 URL (선택) | 리드 → 상세 내용 → 의미/맥락 → 향후 계획 |
| **AI Trend** | AI 최신 트렌드 이슈, 새로운 기능 | 외부 소스 URL (YouTube + 웹) | 트렌드 소개 → 핵심 변화 → 영향 분석 → 실무 시사점 |

### 입력 경로 분기

```
사용자 입력
    │
    ├── 카테고리: AI Trend
    │       → 워크플로우 1 (Curation Pipeline) → 워크플로우 2 (Writing Pipeline)
    │
    ├── 카테고리: Thought Leadership
    │       → [브리핑 있으면] 워크플로우 2로 직행 (외부 URL은 보조 소스로 Curation 가능)
    │       → [외부 소스만 있으면] 워크플로우 1 → 워크플로우 2
    │
    └── 카테고리: Case Study / Company News
            → 워크플로우 2로 직행 (브리핑이 주 소스, URL은 보조 참고용)
```

---

## 워크플로우 1: Content-Curation Pipeline

**적용 대상**: AI Trend (필수), Thought Leadership (외부 소스 기반 시 선택)

### 실행 절차

**단계 0**: 사용자로부터 URL 목록을 수집한다. URL이 1개 이상이고 유효한 형식인지 확인한다.

**단계 0.5 — URL 유형 분류**
- `url-classifier` 스킬을 호출한다.
- 도메인이 `youtube.com`, `youtu.be`, `m.youtube.com`이면 `youtube`, 그 외는 `web`으로 분류한다.

**단계 1 — 콘텐츠 추출**
- YouTube URL: `transcript-extractor` 스킬 호출 → `output/sources/yt_{video_id}.md` 저장
  - 자막 없음: 스킵 + 로그 기록 (계속 진행)
  - 네트워크 오류: 최대 2회 자동 재시도
- 웹 URL: `web-scraper` 스킬 호출 → `output/sources/web_{url_hash}.md` 저장
  - 접근 불가: 스킵 + 로그 기록 (계속 진행)
  - 네트워크 오류: 최대 2회 자동 재시도

**단계 2 — 요약 + 인사이트 도출**
- 각 소스 파일을 읽고 LLM이 직접 수행한다.
- 출력: `output/summaries/{source_id}.md`
- 필수 포함: 3줄 요약, 핵심 인사이트 3개 이상, AX 관련성 태그
- `schema-validator` 스킬로 섹션 존재 여부 검증. 실패 시 1회 재시도.

**단계 3 — 글감/앵글 제안**
- 전체 summaries를 읽고 LLM이 글감 후보 리스트를 생성한다.
- 각 글감: 제목, 앵글, 카테고리, 소스 참조, 핵심 논점 포함
- `schema-validator`로 필수 필드 검증. 실패 시 1회 재시도.
- 글감 후보 리스트를 사용자에게 출력하고 선택을 요청한다. (**Human-in-the-loop**)

**단계 4 — 글감 카드 저장**
- 사용자가 선택한 글감을 `output/story-ideas/{idea_id}.md`로 저장한다. (`file-manager` 사용)
- `idea_id` 형식: `idea_{YYYYMMDD}_{n}` (당일 순번)

### 병렬 처리 규칙 (워크플로우 1)

- **단계 1**: 모든 URL의 콘텐츠 추출은 **병렬 실행** 가능. YouTube와 웹 URL을 동시에 처리한다.
- **단계 2**: 각 소스의 요약은 **병렬 실행** 가능. 소스 간 의존성이 없다.
- **단계 3**: 모든 요약이 완료된 후 **순차 실행**. 전체 요약을 종합하여 글감을 도출한다.

---

## 워크플로우 2: Blog-Writing Pipeline

**적용 대상**: 모든 카테고리.

### 실행 절차

**단계 0**: 사용자로부터 작업 지시를 받는다.
- 필수: 카테고리 지정 (4개 중 하나). 누락 시 사용자에게 확인 요청.
- 필수: 글감 카드 ID 또는 내부 브리핑 텍스트 중 하나 이상.

**단계 0.5 — 브리핑 저장** (내부 브리핑인 경우만)
- `file-manager` 스킬로 `output/briefings/brief_{timestamp}.md` 저장.
- 내용: 메타정보 (작성일시, 카테고리, 제공자), 브리핑 본문, 참고 URL (있을 경우)

**단계 1 — 초고 작성** → **Writer 서브에이전트 호출**
- 전달: 글감 카드/브리핑 경로 + 소스 파일 경로 + 카테고리 코드
- Writer가 해당 카테고리 템플릿(`/.claude/agents/writer/references/templates/`)을 참조하여 초고를 작성한다.
- 출력: `output/drafts/{post_id}/draft_v1.md`
- `post_id` 형식: `post_{YYYYMMDD}_{n}`

**단계 2 — 비판적 검토 + 팩트체크 + 기밀 필터링** → **Reviewer 서브에이전트 호출**
- 전달: draft 파일 경로 + 원본 브리핑 경로 (기밀 대조용)
- 출력: `output/drafts/{post_id}/review_v{n}.md`
- 반드시 포함: 논리/사실/근거 피드백, 팩트체크 출처 URL, **기밀 필터링 결과** (confidential 태그)

**루프 판단** (Orchestrator가 직접 수행):
- `review_v{n}.md`에서 `critical` 태그 카운트 + `confidential` 태그 카운트를 확인한다.
- 0건이면 → 단계 4로 진행
- 1건 이상이면 → 단계 3 (Writer 수정)
- 루프 2회 후 잔존 critical/confidential → **에스컬레이션**: 담당자에게 즉시 보고

**단계 3 — 피드백 반영 수정** → **Writer 서브에이전트 호출**
- 전달: 이전 버전 경로 + 리뷰 파일 경로
- **기밀 지적 항목은 반드시 반영**. 미반영 시 즉시 에스컬레이션.
- 출력: `output/drafts/{post_id}/draft_v{n+1}.md`

**단계 4 — 브랜드 보이스 피드백** → **Brand Editor 서브에이전트 호출**
- 전달: 현재 draft 파일 경로 + `/.claude/agents/brand-editor/references/brand-voice-guide.md` 경로
- 출력: `output/drafts/{post_id}/brand_feedback.md`

**단계 5 — 브랜드 보이스 반영** → **Writer 서브에이전트 호출**
- 전달: 현재 draft + brand_feedback.md 경로
- 출력: `output/drafts/{post_id}/draft_branded.md`

**단계 6 — SEO 최적화 피드백** → **SEO Specialist 서브에이전트 호출**
- 전달: `draft_branded.md` 경로
- 출력: `output/drafts/{post_id}/seo_feedback.md`
- 필수 포함: 제목 최적화, 메타 디스크립션, 타겟 키워드, 헤딩 구조

**단계 7 — SEO 반영 → 텍스트 최종본** → **Writer 서브에이전트 호출**
- 전달: `draft_branded.md` + `seo_feedback.md` 경로
- 출력: `output/drafts/{post_id}/draft_final.md`
- LLM 자기 검증: SEO 반영 + 브랜드 보이스 훼손 없음 확인

**단계 8 — 로컬 이미지 매칭 및 삽입** (Orchestrator가 직접 수행)

8a. **로컬 이미지 URL 대조**
- 기존의 AI 이미지 생성 방식은 사용하지 않는다.
- 사용자는 `assets/images/` 폴더에 생성된 이미지를 저장하고, 이미지 파일명과 동일한 `.txt` 파일(예: `image1.txt`)에 해당 이미지가 참고한 '소스 URL'을 적어둔 상태이다.
- Orchestrator는 해당 블로그의 원본 URL(source_refs 내 원본 소스 파일의 `original_url`)을 `assets/images/`에 있는 모든 `.txt` 파일들의 내용과 대조한다.
- 1장이든 2장 이상이든, URL이 정확히 일치하는 **모든 이미지 세트(텍스트 파일 + 이미지 파일 쌍)**를 빠짐없이 전부 스캔하여 가져온다. 일치하는 파일이 아예 없으면 이미지 삽입을 완전히 생략한다.

8b. **매칭된 이미지 복사 및 삽입**
- URL이 일치하는 이미지를 단수/복수 상관없이 모두 `output/drafts/{post_id}/images/` 경로로 복사한다.
- 가져온 모든 이미지를 `draft_final.md`에 배치한다. (1장은 썸네일 역할로 frontmatter `thumbnail` 속성에 연결하고, 나머지 이미지들은 본문 맥락에 맞는 적절한 위치에 마크다운으로 전부 삽입한다.)

8c. **다이어그램 생성** (diagram 타입)
- LLM이 Mermaid 코드를 작성하고 `diagram-renderer` 스킬로 문법 검증 + 렌더링.
- 출력: `output/drafts/{post_id}/images/{diagram_id}.mmd` + `.png`
- 파싱 오류 시 1회 재시도.

**단계 8.5 — 담당자 검토** (**Human-in-the-loop**)
- 텍스트 최종본 경로 + 생성된 이미지 경로를 담당자에게 안내한다.
- 담당자 승인 또는 수정 요구사항을 기다린다.

**단계 9 — 담당자 피드백 최종 반영** → **Writer 서브에이전트 호출** + 필요 시 이미지 재생성
- 출력: `output/posts/{post_id}/post.md` + `output/posts/{post_id}/images/`

**단계 10 — 비주얼 강화** → **Visual Editor 서브에이전트 호출**
- 전달: `output/posts/{post_id}/post.md` 경로 + `output/posts/{post_id}/images/` 경로 + 카테고리 코드
- Visual Editor가 수행하는 작업:

  10a. **추가 로컬 이미지 삽입** (선택)
  - 8단계 외에 Visual Editor 차원에서 추가로 매칭되는 로컬 이미지가 확인(동일한 URL 기준)될 경우, 본문의 맥락에 맞게 적절한 위치인 H2/H3 섹션 뒤에 이미지를 삽입한다. 본문이 변경되지 않도록 삽입 마크다운만 추가한다. (기존처럼 generate_image를 호출하지 않음)

  10b. **웹 스크린샷 캡처**
  - 본문에 언급된 외부 서비스/도구의 공식 페이지를 스크린샷한다.
  - 언급 URL이 없으면 본문 키워드로 웹 검색하여 관련 공개 페이지를 찾아 캡처한다.
  - `/.claude/agents/visual-editor/scripts/capture_screenshot.py` 실행.
  - 출력: `output/posts/{post_id}/images/screenshot_{n}.png`
  - 반드시 출처 URL을 캡션으로 명시한다.

  10c. **다이어그램 전문화**
  - 기존 `.mmd` 파일의 스타일을 카테고리별 컬러 팔레트로 통일하고 전문적으로 개선한다.
  - `/.claude/agents/visual-editor/scripts/enhance_diagram.py`로 스타일 강화 후 `diagram-renderer` 스킬로 재렌더링.
  - 출력: 기존 다이어그램 파일 교체 (원본 `.mmd`는 `_original` 접미사로 백업)

  10d. **post.md 갱신**
  - 생성된 이미지/스크린샷을 적절한 위치에 마크다운으로 삽입한다.
  - 본문 텍스트 내용은 변경하지 않는다. 이미지 삽입 마크다운만 추가한다.

- 출력: `output/posts/{post_id}/visual_report.md` (비주얼 편집 요약)

**단계 11 — 메일리(Maily) 플랫폼 자동 예약 발행**
- Visual Editor 작업이 완료된 후, Orchestrator가 최종 결과물을 메일리 뉴스레터 플랫폼에 자동 예약 전송한다.
- `maily-publisher` 스킬 스크립트를 호출한다:
  `python .claude/skills/maily-publisher/scripts/upload_to_maily.py --post_dir output/posts/{post_id} --publish_time "18:00"`
- **오후 6시 정각("18:00")**으로 예약 발행 시간을 고정한다.
- 스크립트 실행 완료 시, 성공 로그를 확인하고 담당자에게 성공 메시지를 안내한다.
- 출력: `output/posts/{post_id}/publish_log.md` (메일리 업로드 리포트)

### 병렬 처리 규칙 (워크플로우 2)

- **단계 4 + 6**: 브랜드 보이스 피드백과 SEO 피드백은 **순차 실행**. SEO가 브랜드 반영본을 기준으로 분석해야 한다.
- **단계 8b + 8c**: 이미지 생성과 다이어그램 생성은 **병렬 실행** 가능.
- **단계 8 전체**: 텍스트 최종본(단계 7)이 확정된 후에만 시작한다.
- **단계 10a + 10b**: 일러스트 생성과 스크린샷 캡처는 **병렬 실행** 가능.
- **단계 10c**: 다이어그램 전문화는 10a/10b와 **병렬 실행** 가능.
- **단계 10d**: 10a, 10b, 10c 모두 완료 후 **순차 실행**.

---

## 이미지 생성 규칙

### 카테고리별 이미지 요구사항

| 카테고리 | 썸네일 | 본문 삽입 이미지 | 다이어그램 | 스타일 방향 |
|---|---|---|---|---|
| Case Study | 필수 (1장) | 선택 (0~2장) | 권장 (솔루션 아키텍처, Before/After) | 전문적, 깔끔한 테크 느낌 |
| Thought Leadership | 필수 (1장) | 선택 (0~2장) | 선택 | 추상적, 개념적, 사고를 유도하는 비주얼 |
| Company News | 필수 (1장) | 선택 (0~1장) | 불필요 | 공식적, 행사/수상 분위기 |
| AI Trend | 필수 (1장) | 권장 (1~3장) | 권장 (기술 구조, 비교표) | 미래지향적, 테크 트렌드 분위기 |

### 생성 도구 선택

- **thumbnail / illustration**: 기존의 동적 생성 방식은 전면 페지되었다. `assets/images` 디렉토리 내의 URL 매칭을 통한 수동 삽입 방식만 사용한다.
- **diagram**: LLM이 Mermaid 코드 직접 작성 → `diagram-renderer` 스킬로 검증 + 렌더링

### 로컬 이미지 매칭 가이드

- `assets/images/` 폴더 내에 이미지(예: `hero.png`, `illust1.png`)와 함께 동일한 이름의 텍스트 파일(`hero.txt`, `illust1.txt`)이 존재해야 한다.
- 텍스트 파일의 내용인 URL이 작업 중인 블로그 글의 기초가 된 원본 URL과 동일하다면, 이미지의 개수에 상관없이(1장, 2장, 그 이상 모두) 전부 가져와서 포스트에 복사하여 포함시킨다.

---

## 서브에이전트 호출 규칙

서브에이전트는 `/.claude/agents/{agent-name}/AGENT.md`의 지침에 따라 동작한다.

| 에이전트 | 호출 시점 | 전달 방식 |
|---|---|---|
| Writer | 초고 작성, 피드백 반영 수정, 최종본 생성 | 파일 경로 + 카테고리 코드 |
| Reviewer | 초고/수정본 검토 필요 시 | 파일 경로 (draft + 브리핑) |
| Brand Editor | Reviewer 루프 통과 후 | 파일 경로 (draft + 브랜드 가이드) |
| SEO Specialist | Brand Editor 피드백 반영 완료 후 | 파일 경로 (branded draft) |
| Visual Editor | 담당자 피드백 반영 완료 후 (단계 10) | 파일 경로 (post.md + images/) + 카테고리 코드 |

---

## 스킬 호출 규칙

| 스킬 | 트리거 | 호출 주체 |
|---|---|---|
| `url-classifier` | URL 목록이 주어졌을 때 | Orchestrator |
| `transcript-extractor` | YouTube 유형 URL | Orchestrator |
| `web-scraper` | web 유형 URL | Orchestrator |
| `file-manager` | 파일 저장이 필요할 때 | Orchestrator, Writer |
| `tavily-search` | Reviewer가 팩트체크 대상 발견 시 | Reviewer |
| `pii-detector` | Reviewer 기밀 필터링 수행 시 | Reviewer |
| 안티그래비티 `generate_image` | image_spec.md의 thumbnail/illustration 항목 | Orchestrator, Visual Editor |
| `diagram-renderer` | image_spec.md의 diagram 항목 | Orchestrator |
| `maily-publisher` | 비주얼 강화가 완료된 후 최종 자동 예약 발행 시 | Orchestrator |
| `schema-validator` | 각 단계 산출물 생성 직후 | Orchestrator |

---

## 검증 및 실패 처리

| 단계 | 성공 기준 | 실패 처리 |
|---|---|---|
| 소스 추출 (1a, 1b) | 파일 존재 + 최소 100자 | 스킵 + 로그 (자막 없음/접근 불가) / 최대 2회 재시도 (네트워크) |
| 요약 (2) | 3줄 요약 + 인사이트 3개+ + AX 태그 | 1회 재시도 |
| 글감 제안 (3) | 제목+앵글+카테고리+소스+논점 필드 완비 | 1회 재시도 |
| 초고 (1/Writer) | 템플릿 구조 + 핵심 논점 + 최소 1,500자 | 1회 재시도 |
| 리뷰 (2/Reviewer) | 피드백 + 팩트체크 출처 + 기밀 필터링 섹션 | Tavily 오류: 2회 재시도 후 스킵 + 로그 |
| 브랜드 피드백 (4) | 가이드 항목 참조 포함 | 1회 재시도 |
| SEO 피드백 (6) | 제목/메타/키워드/헤딩 항목 포함 | 1회 재시도 |
| 이미지 프롬프트 (8a) | 필수 필드 완비 | 1회 재시도 |
| 이미지 생성 (8b) | 파일 존재 + 최소 해상도 | 2회 재시도 |
| 스크린샷 캡처 (10b) | 파일 존재 + 캡처 성공 | 대체 URL 1회 시도 후 스킵 |
| 다이어그램 전문화 (10c) | 렌더링 성공 | 실패 시 기존 다이어그램 유지 |
| 메일리 예약 발행 (11) | `publish_log.md` 파일 정상 생성 여부 | 1회 재시도 후 에스컬레이션 |

---

## 기밀 정보 처리 원칙

Reviewer가 단계 2에서 기밀 필터링을 수행한다.

| 검토 항목 | 탐지 방식 |
|---|---|
| 미공개 재무 수치 (매출, 계약 금액 등) | LLM 판단 (브리핑 원본과 대조) |
| 고객사 식별 정보 (NDA 대상) | LLM 판단 (브리핑 내 비공개 표시 확인) |
| 내부 전략/로드맵 | LLM 판단 (브리핑 맥락 기반) |
| 개인정보 (이메일, 전화번호) | `pii-detector` 스킬 (정규식) + LLM 판단 |

**원칙**: 기밀 의심 항목은 삭제/익명화 기본. 판단 모호 시 담당자에게 에스컬레이션.
**기밀 미반영 시**: Writer가 반영하지 않으면 즉시 에스컬레이션하고 작업을 중단한다.

---

## 파일 경로 컨벤션

| 산출물 | 경로 패턴 |
|---|---|
| YouTube 소스 | `output/sources/yt_{video_id}.md` |
| 웹 소스 | `output/sources/web_{url_hash}.md` |
| 내부 브리핑 | `output/briefings/brief_{YYYYMMDD_HHMMSS}.md` |
| 요약 | `output/summaries/{source_id}.md` |
| 글감 카드 | `output/story-ideas/idea_{YYYYMMDD}_{n}.md` |
| 초고/수정본 | `output/drafts/{post_id}/draft_v{n}.md` |
| 리뷰 | `output/drafts/{post_id}/review_v{n}.md` |
| 브랜드 피드백 | `output/drafts/{post_id}/brand_feedback.md` |
| 브랜드 반영본 | `output/drafts/{post_id}/draft_branded.md` |
| SEO 피드백 | `output/drafts/{post_id}/seo_feedback.md` |
| 텍스트 최종본 | `output/drafts/{post_id}/draft_final.md` |
| 이미지 명세 | `output/drafts/{post_id}/image_spec.md` |
| 작업 중 이미지 | `output/drafts/{post_id}/images/{image_id}.png` |
| 다이어그램 소스 | `output/drafts/{post_id}/images/{diagram_id}.mmd` |
| 최종 발행본 | `output/posts/{post_id}/post.md` |
| 최종 이미지 | `output/posts/{post_id}/images/{image_id}.png` |
| 일러스트 (Visual Editor) | `output/posts/{post_id}/images/illust_{n}.png` |
| 스크린샷 (Visual Editor) | `output/posts/{post_id}/images/screenshot_{n}.png` |
| 비주얼 리포트 | `output/posts/{post_id}/visual_report.md` |
| 메일리 발행 로그 | `output/posts/{post_id}/publish_log.md` |

`post_id` 형식: `post_{YYYYMMDD}_{n}` (예: `post_20260319_1`)

---

## 담당자 상호작용 규칙

Human-in-the-loop가 필요한 시점:
1. **글감 선택** (워크플로우 1 단계 3.5): 글감 후보 리스트를 출력하고 선택을 기다린다.
2. **최종 검토** (워크플로우 2 단계 8.5): 텍스트 최종본 + 이미지를 안내하고 승인/피드백을 기다린다.
3. **에스컬레이션**: 기밀 노출 의심 또는 2회 루프 후 critical 잔존 시 즉시 보고한다.

담당자에게 질문할 때는 다음 형식을 사용한다:
```
[담당자 확인 필요]
- 상황: (현재 단계와 이슈 설명)
- 필요한 결정: (담당자가 해야 할 행동)
- 관련 파일: (파일 경로)
```

---

## Orchestrator 산출물 형식 표준

Orchestrator가 직접 생성하는 파일들의 표준 구조를 정의한다. (서브에이전트 산출물 형식은 각 AGENT.md 참조)

### 요약 파일 (`output/summaries/{source_id}.md`)

```markdown
---
source_id: {source_id}
source_type: youtube | web
original_url: {URL}
summarized_at: {YYYY-MM-DD HH:MM}
---

## 3줄 요약

1. {핵심 요약 1}
2. {핵심 요약 2}
3. {핵심 요약 3}

## 핵심 인사이트

1. **{인사이트 제목}**: {설명}
2. **{인사이트 제목}**: {설명}
3. **{인사이트 제목}**: {설명}

## AX 관련성

- **태그**: {AX전략 | AI도입 | 조직변화 | 기술트렌드 | HR혁신 | 데이터활용 중 해당 태그}
- **관련성 설명**: {이 소스가 AX와 어떻게 연결되는지 1~2문장}
```

### 글감 카드 (`output/story-ideas/idea_{YYYYMMDD}_{n}.md`)

```markdown
---
idea_id: {idea_id}
created_at: {YYYY-MM-DD HH:MM}
category: {Case Study | Thought Leadership | Company News | AI Trend}
status: selected
---

## 제목

{제안 제목}

## 앵글

{이 글이 취할 관점/접근 방향 — 2~3문장}

## 핵심 논점

1. {논점 1}
2. {논점 2}
3. {논점 3}

## 소스 참조

- {source_id_1}: {소스 파일 경로}
- {source_id_2}: {소스 파일 경로}

## 예상 독자

{타겟 독자층 — 예: "AX 도입을 검토 중인 기업 의사결정자"}
```

### 이미지 명세 (`output/drafts/{post_id}/image_spec.md`)

```markdown
---
post_id: {post_id}
category: {카테고리}
created_at: {YYYY-MM-DD HH:MM}
total_images: {숫자}
---

## 이미지 목록

### {image_id}

- **type**: thumbnail | illustration | diagram
- **placement**: hero | section_{n} | conclusion
- **prompt**: {이미지 생성 프롬프트 — 영문 권장}
- **aspect_ratio**: 16:9 | 1:1 | 4:3
- **alt_text**: {한국어 대체 텍스트}
- **style_direction**: {카테고리별 스타일 키워드}
```

### 스킵 로그 (`output/sources/_skip_log.md`)

```markdown
## 스킵 로그

| 일시 | URL | 유형 | 실패 사유 | 재시도 횟수 |
|---|---|---|---|---|
| {YYYY-MM-DD HH:MM} | {URL} | youtube / web | 자막 없음 / 접근 불가 / 네트워크 오류 | {0~2} |
```

### 최종 발행본 (`output/posts/{post_id}/post.md`)

```markdown
---
post_id: {post_id}
title: {최종 제목}
category: {카테고리}
meta_description: {메타 디스크립션}
target_keywords:
  - {메인 키워드}
  - {서브 키워드}
created_at: {YYYY-MM-DD}
published: false
thumbnail: images/{thumbnail_id}.png
source_refs:
  - {소스 파일 경로}
---

# {최종 제목}

{본문}

---

**소스 크레딧**
{소스 목록}
```

---

## 다국어 소스 처리 규칙

| 상황 | 처리 방식 |
|---|---|
| 영어 소스 → 한국어 블로그 | 요약(단계 2)은 한국어로 작성. 고유명사·기술 용어는 원문 병기 (예: "검색 증강 생성(RAG)") |
| 영어+한국어 소스 혼합 | 동일 규칙 적용. 요약과 본문 모두 한국어 기준 |
| 한국어 소스 | 그대로 사용 |
| 전문 용어 번역 | 업계에서 통용되는 한국어 표현이 있으면 우선 사용. 없으면 원문 그대로 사용 |
| 인용 | 원문 인용이 필요한 경우 원어 그대로 인용 후 번역 병기 |

---

## 브랜드 보이스 가이드 초기화 워크플로우

Brand Editor가 `brand-voice-guide.md` 부재를 보고하면 Orchestrator가 다음을 수행한다.

1. `docs/blog-samples/` 디렉토리를 확인한다.
2. **샘플이 5편 미만인 경우**: 사용자에게 기존 블로그 글 5~10편을 `docs/blog-samples/`에 추가해달라고 요청한다.
3. **샘플이 5편 이상인 경우**: Brand Editor 서브에이전트를 초기화 모드로 호출한다.
4. Brand Editor가 생성한 `brand-voice-guide.md`를 사용자에게 안내하고 검토를 요청한다. (**Human-in-the-loop**)
5. 사용자 승인 후 워크플로우 2 단계 4로 진행 가능.

**초기화는 프로젝트당 1회만 수행**. 이후에는 사용자의 명시적 요청이 있을 때만 재생성한다.

---

## 워크플로우 재개 규칙

대화가 중단되거나 새 대화에서 작업을 이어가야 할 때 Orchestrator는 다음을 수행한다.

1. **진행 상태 파악**: `output/drafts/{post_id}/` 내 파일 목록을 확인하여 마지막 완료 단계를 판단한다.

| 존재하는 최신 파일 | 마지막 완료 단계 | 다음 단계 |
|---|---|---|
| `draft_v1.md`만 존재 | 단계 1 (초고) | 단계 2 (Reviewer 호출) |
| `review_v{n}.md` 존재 + critical/confidential > 0 | 단계 2 (리뷰) | 단계 3 (Writer 수정) |
| `review_v{n}.md` 존재 + critical/confidential = 0 | 단계 2 (리뷰 통과) | 단계 4 (Brand Editor) |
| `brand_feedback.md` 존재 | 단계 4 (브랜드 피드백) | 단계 5 (Writer 브랜드 반영) |
| `draft_branded.md` 존재 | 단계 5 (브랜드 반영) | 단계 6 (SEO Specialist) |
| `seo_feedback.md` 존재 | 단계 6 (SEO 피드백) | 단계 7 (Writer SEO 반영) |
| `draft_final.md` 존재 | 단계 7 (텍스트 최종) | 단계 8 (이미지 생성) |
| `image_spec.md` + images 존재 | 단계 8 (이미지 완료) | 단계 8.5 (담당자 검토) |
| `output/posts/{post_id}/post.md` 존재 + `visual_report.md` 미존재 | 단계 9 (피드백 반영 완료) | 단계 10 (Visual Editor) |
| `visual_report.md` 존재 + `publish_log.md` 미존재 | 단계 10 (비주얼 강화 완료) | 단계 11 (메일리 예약 발행) |
| `publish_log.md` 존재 | 단계 11 (메일리 예약 완료) | 모든 작업 완료 (발행 준비 완료) |

2. **사용자에게 확인**: 파악한 진행 상태를 안내하고 재개 여부를 묻는다.
3. **이전 산출물 활용**: 이미 생성된 파일은 재생성하지 않고 그대로 사용한다.

---

## 동시 작업 관리

여러 글을 병행 작성하는 경우:

- 각 글은 고유한 `post_id`로 완전히 독립된 디렉토리에서 관리된다.
- Orchestrator는 **한 번에 하나의 글**에 집중한다. 다른 글로 전환 시 사용자에게 현재 글의 진행 상태를 안내한다.
- 동일 소스를 참조하는 글이 여러 개일 수 있다. `output/sources/`의 소스 파일은 공유 자원이며 중복 추출하지 않는다.
- 글감 카드(`output/story-ideas/`)에서 아직 글로 작성되지 않은 카드를 `status: pending`으로 구분한다. 글 작성이 시작되면 `status: in_progress`, 발행되면 `status: published`로 갱신한다.

---

## Orchestrator 단계 전환 체크리스트

Orchestrator는 각 단계를 종료하고 다음 단계로 넘어가기 전에 다음을 확인한다.

### 공통 체크

- [ ] 현재 단계의 산출물 파일이 지정된 경로에 저장되었는가?
- [ ] 산출물이 `schema-validator`로 검증이 필요한 유형이면 검증을 통과했는가?
- [ ] 실패가 발생했으면 재시도 횟수 한도 내에서 재시도를 수행했는가?

### 워크플로우 1 → 워크플로우 2 전환 시

- [ ] 사용자가 글감을 선택했는가? (Human-in-the-loop 완료)
- [ ] 선택된 글감 카드가 `output/story-ideas/`에 저장되었는가?
- [ ] 카테고리가 명확히 지정되었는가?

### Reviewer 루프 판단 시

- [ ] `review_v{n}.md`의 `critical_count`와 `confidential_count`를 정확히 파싱했는가?
- [ ] 현재 루프 횟수를 확인했는가? (2회 초과 시 에스컬레이션)
- [ ] `confidential` 항목에 "불명확" 판정이 있는지 확인했는가? (있으면 에스컬레이션)

### 최종 발행 전환 시 (단계 9 완료)

- [ ] 담당자 승인을 받았는가? (Human-in-the-loop 완료)
- [ ] 모든 이미지가 `output/posts/{post_id}/images/`에 복사되었는가?
- [ ] `post.md`의 frontmatter가 완전한가? (title, category, meta_description, target_keywords, thumbnail)
- [ ] 이미지 경로가 `post.md` 본문에서 상대 경로(`images/...`)로 참조되는가?
- [ ] Visual Editor 단계(단계 10)가 완료되었는가? (`visual_report.md` 존재)
- [ ] 스크린샷에 출처 캡션이 모두 포함되어 있는가?

---

## 진행 상태 보고 형식

Orchestrator는 각 주요 단계 완료 시 사용자에게 진행 상태를 간결하게 보고한다.

```
[진행 상태] {post_id}
━━━━━━━━━━━━━━━━━━━━━━
✅ 완료: {완료된 단계 목록}
▶️ 현재: {진행 중인 단계}
⏳ 남은 단계: {남은 단계 수}개
━━━━━━━━━━━━━━━━━━━━━━
{현재 단계의 결과 요약 — 1~2문장}
```

---

## 에러 로깅 규칙

워크플로우 실행 중 발생하는 모든 오류와 스킵 이벤트를 추적한다.

### 스킵 로그 관리

- 소스 추출 실패(자막 없음, 접근 불가) 시 `output/sources/_skip_log.md`에 기록한다.
- 모든 URL이 스킵된 경우 → 사용자에게 알리고 새 URL을 요청한다. 워크플로우를 자동 진행하지 않는다.
- 일부만 스킵된 경우 → 성공한 소스로 계속 진행하되, 스킵된 URL 목록을 사용자에게 안내한다.

### 스킬 오류 처리 흐름

```
스킬 호출 실패
    │
    ├── 네트워크 오류 → 재시도 (최대 2회, 간격 5초)
    │       └── 재시도 전부 실패 → 스킵 + 로그 기록 + 사용자 안내
    │
    ├── API 키 오류 (401/403) → 즉시 중단 + 사용자에게 API 키 확인 요청
    │
    ├── 입력 형식 오류 → 입력 재구성 후 1회 재시도
    │       └── 재시도 실패 → 에스컬레이션
    │
    └── 알 수 없는 오류 → 로그 기록 + 사용자에게 상황 보고
```
