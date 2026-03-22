# file-manager 스킬

## 역할

산출물 파일의 생성, 이동, 버전 관리를 담당한다.

## 트리거 조건

모든 단계에서 파일 저장이 필요할 때 Orchestrator와 Writer가 호출한다.

## 사용법

```bash
# 파일 저장
python .claude/skills/file-manager/scripts/manage_files.py save --path "output/drafts/post_20260319_1/draft_v1.md" --content "..."

# 파일 이동 (최종 발행 시)
python .claude/skills/file-manager/scripts/manage_files.py move --src "output/drafts/post_20260319_1/draft_final.md" --dst "output/posts/post_20260319_1/post.md"

# 다음 버전 번호 조회
python .claude/skills/file-manager/scripts/manage_files.py next_version --post_id "post_20260319_1" --prefix "draft_v"

# post_id 생성
python .claude/skills/file-manager/scripts/manage_files.py new_post_id
```

## 파일 경로 규칙

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
| 최종 발행본 | `output/posts/{post_id}/post.md` |

## 버전 관리

- 같은 `post_id` 내에서 `draft_v1.md`, `draft_v2.md`, ... 순으로 버전 증가
- 이전 버전을 덮어쓰지 않는다. 항상 새 버전 파일로 저장한다.

## 성공 기준

- 파일이 지정 경로에 생성됨
- 파일 I/O 실패 시 1회 재시도
