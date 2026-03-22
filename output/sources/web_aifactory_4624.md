---
source_id: web_aifactory_4624
source_type: web
url: https://aifactory.space/page/langchainkr/forum/discussion/4624
title: 🤖 Open SWE — 내부 코딩 에이전트를 위한 오픈소스 프레임워크
extracted_at: 2026-03-19 16:07:57
---

# 🤖 Open SWE — 내부 코딩 에이전트를 위한 오픈소스 프레임워크

배경: 빅테크들은 이미 쓰고 있었다
https://blog.langchain.com/open-swe-an-open-source-framework-for-internal-coding-agents/ 블로그 내용을 번역 및 요약한 것입니다.
요즘 잘나가는 엔지니어링 팀들은 AI 코딩 에이전트를 내부에 직접 구축해서 쓰고 있어요.
- Stripe → Minions
- Ramp → Inspect
- Coinbase → Cloudbot
각자 독립적으로 만들었지만, 놀랍게도 비슷한 아키텍처 패턴으로 수렴했습니다. LangChain은 이 공통 패턴을 분석해서 누구나 쓸 수 있는 오픈소스 프레임워크로 만든 게 바로 Open SWE예요.
Open SWE 아키텍처 7가지 핵심
1. 🧠 에이전트 기반: Deep Agents + LangGraph
기존 에이전트를 포크하거나 처음부터 만드는 대신, Deep Agents 프레임워크 위에 조합(compose) 하는 방식을 택했어요. Ramp가 OpenCode 위에 Inspect를 만든 것과 같은 접근법입니다.
- Deep Agents가 개선되면 자동으로 혜택을 받음
- 포크 없이 조직별 커스터마이징 가능
2. 🏖️ 샌드박스: 격리된 클라우드 환경
각 작업은 독립된 클라우드 샌드박스에서 실행됩니다. 실수가 발생해도 프로덕션 시스템에 영향 없이 격리돼요.
- 지원 샌드박스 프로바이더: Modal, Daytona, Runloop, LangSmith (직접 구현도 가능)
3. 🛠️ 도구(Tool): 적게, 하지만 정밀하게
Stripe는 약 500개의 도구를 보유하지만 "도구의 양보다 품질이 중요"하다고 밝혔어요. Open SWE도 약 15개의 핵심 도구만 큐레이션해서 제공합니다.
| 도구 | 역할 |
|---|---|
execute | 샌드박스 내 셸 명령 실행 |
fetch_url | 웹 페이지를 마크다운으로 가져오기 |
http_request | API 호출 |
commit_and_open_pr | Git 커밋 + GitHub PR 자동 오픈 |
linear_comment | Linear 티켓에 업데이트 포스팅 |
slack_thread_reply | Slack 스레드 답장 |
4. 📚 컨텍스트 엔지니어링: AGENTS.md
레포 루트에 AGENTS.md
파일을 넣어두면, 에이전트가 작업 시작 전 자동으로 읽어서 시스템 프롬프트에 주입합니다. 팀의 코딩 컨벤션, 테스트 요구사항, 아키텍처 결정 사항 등을 담아두면 돼요.
5. 🎭 오케스트레이션: 서브에이전트 + 미들웨어
- 서브에이전트: 복잡한 작업을
task
도구로 자식 에이전트에게 위임. 각 서브에이전트는 독립된 컨텍스트를 가짐 - 미들웨어: 결정론적 로직을 에이전트 루프에 주입
check_message_queue_before_model
: 작업 중 도착한 메시지를 다음 모델 호출 전에 주입open_pr_if_needed
: 에이전트가 PR을 안 열면 자동으로 열어주는 안전망
6. 🚀 호출 방식: Slack, Linear, GitHub
개발자들이 이미 쓰는 도구에서 바로 호출할 수 있어요.
- Slack: 봇 멘션 → 스레드에서 상태 업데이트 + PR 링크 답장
- Linear: 이슈에
@openswe
댓글 → 👀 반응 후 결과를 댓글로 포스팅 - GitHub: 에이전트가 만든 PR에
@openswe
태그 → 리뷰 피드백 반영 후 같은 브랜치에 푸시
7. ✅ 검증: 프롬프트 기반 + 안전망
린터, 포매터, 테스트를 커밋 전에 실행하도록 지시하고, open_pr_if_needed
미들웨어가 최종 안전망 역할을 합니다.
내부 구현체들과 비교
| 항목 | Open SWE | Stripe (Minions) | Ramp (Inspect) | Coinbase (Cloudbot) |
|---|---|---|---|---|
| 기반 | Deep Agents/LangGraph | Goose 포크 | OpenCode 조합 | 처음부터 직접 개발 |
| 샌드박스 | 플러거블 | AWS EC2 | Modal | 자체 인프라 |
| 도구 수 | ~15개 | ~500개 | OpenCode SDK | MCPs + 커스텀 |
| 호출 방식 | Slack, Linear, GitHub | Slack + 버튼 | Slack + 웹 + 크롬 확장 | Slack 네이티브 |
커스터마이징 포인트
Open SWE는 완성품이 아닌 시작점입니다. 모든 주요 컴포넌트를 교체할 수 있어요.
- 샌드박스 프로바이더 교체
- 모델 변경 (기본값: Claude Opus 4)
- 내부 API/배포 시스템용 도구 추가
- Slack/Linear/GitHub 트리거 수정
- 미들웨어로 승인 게이트, 로깅, 안전 체크 추가
마무리
Open SWE는 "AI 코딩 에이전트를 우리 팀에 도입하고 싶은데 어디서부터 시작해야 할지 모르겠다"는 팀을 위한 프레임워크입니다. Stripe, Ramp, Coinbase가 수개월에 걸쳐 수렴한 아키텍처 패턴을 오픈소스로 공개한 것이기 때문에 시작하시는 분들에게 좋은 선택이 될 것 같습니다. MIT 라이선스이고, 기본 LLM은 Claude Opus 4 기반으로 동작합니다.
