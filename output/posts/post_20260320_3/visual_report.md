---
post_id: post_20260320_3
enhanced_at: 2026-03-20 13:30
status: pending_images
---

## 비주얼 편집 요약

| 유형 | 파일명 | 위치 | 설명 | 상태 |
|---|---|---|---|---|
| thumbnail | thumb_01.png | hero | 비개발자가 AI 에이전트 가상 팀에 둘러싸인 미래지향적 일러스트 | 미생성 (서버 불안정) |
| illustration | illust_01.png | section_2 | AI 활용 3단계(증강, 자동화, 조직화) 개념 시각화 | 미생성 (서버 불안정) |
| illustration | illust_02.png | section_3 | 1인 기업가의 가상 AI 팀 구성 장면 | 미생성 (서버 불안정) |

## 변경 사항

- 추가된 이미지: 0장 (Pollinations.ai 서버 500/429 에러로 전량 스킵)
- 개선된 다이어그램: 0장
- 추가된 스크린샷: 0장

## 이미지 생성 재시도 안내

이미지 프롬프트는 `output/drafts/post_20260320_3/image_spec.md`에 저장되어 있습니다.
서버 복구 후 다음 명령으로 재생성 가능:

```bash
python .claude/skills/image-generator/scripts/generate_image.py --prompt "{프롬프트}" --type thumbnail --output "output/posts/post_20260320_3/images/thumb_01.png" --aspect-ratio "16:9"
python .claude/skills/image-generator/scripts/generate_image.py --prompt "{프롬프트}" --type illustration --output "output/posts/post_20260320_3/images/illust_01.png" --aspect-ratio "4:3"
python .claude/skills/image-generator/scripts/generate_image.py --prompt "{프롬프트}" --type illustration --output "output/posts/post_20260320_3/images/illust_02.png" --aspect-ratio "4:3"
```

또는 `.env`에 `GOOGLE_AI_API_KEY`를 설정하면 Gemini 모델로 고품질 이미지 생성이 가능합니다.
