# transcript-extractor 스킬

## 역할

YouTube URL에서 자막(transcript)을 추출하여 소스 파일로 저장한다.

## 트리거 조건

워크플로우 1 단계 1a: `youtube` 유형으로 분류된 URL에 대해 Orchestrator가 호출한다.

## 사전 요구사항

```bash
pip install youtube-transcript-api
```

## 사용법

```bash
python .claude/skills/transcript-extractor/scripts/extract_transcript.py --video_id VIDEO_ID --output_dir output/sources
```

## 출력 파일 형식

`output/sources/yt_{video_id}.md`:

```markdown
---
source_id: yt_{video_id}
source_type: youtube
url: https://www.youtube.com/watch?v={video_id}
title: {영상 제목}
extracted_at: {YYYY-MM-DD HH:MM:SS}
---

# {영상 제목}

{자막 전문 텍스트}
```

## 성공 기준

- 파일 생성됨
- 파일 내용이 100자 이상

## 실패 처리

| 오류 유형 | 처리 방법 |
|---|---|
| 자막 없음 (NoTranscriptFound) | 스킵 + `output/sources/_skip_log.md`에 기록 |
| 네트워크 오류 | 최대 2회 자동 재시도 후 스킵 + 로그 |
| 그 외 오류 | 스킵 + 로그 |

## 스킵 로그 형식

`output/sources/_skip_log.md`에 추가:
```
- {YYYY-MM-DD HH:MM} | yt_{video_id} | {오류 유형} | {URL}
```
