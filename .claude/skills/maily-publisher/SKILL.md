---
name: maily-publisher
description: 최종 작성된 블로그 포스트를 메일리(Maily) 뉴스레터 플랫폼에 지정된 시간(오후 6시 고정)으로 자동 업로드 및 예약 발행하는 스킬
---

# maily-publisher 스킬 지침

## 역할
Visual Editor 단계까지 모두 완료된 최종 발행본(`post.md`)과 이미지를 메일리(Maily) 플랫폼에 예약 발행한다.

## 호출 시점
워크플로우 2 **단계 11** — 비주얼 강화 완료 후.

## 스크립트 실행
```bash
python .claude/skills/maily-publisher/scripts/upload_to_maily.py --post_dir {post_dir_path} --publish_time "18:00"
```

## 파라미터
- `--post_dir`: 최종 발행본이 저장된 포스트 디렉토리 경로 (예: `output/posts/post_20260320_1`)
- `--publish_time`: 예약 발행 시간 (항상 "18:00"으로 고정)

## 출력
명령어 실행 후 스크립트는 해당 디렉토리에 `publish_log.md`를 생성한다.
Orchestrator는 해당 파일이 생성되었는지 확인하여 발행 완료 여부를 판단한다.

## 제약 사항
- 스크립트 실행 전 반드시 `post.md` 파일과 매칭된 이미지들이 폴더 내에 정확히 존재해야 한다.
- 메일리 계정 연동(Session Token 또는 API Key) 환경 변수(`MAILY_API_KEY` 혹은 `MAILY_SESSION_TOKEN`)가 `.env`에 등록되어 있어야 한다고 가정한다.
