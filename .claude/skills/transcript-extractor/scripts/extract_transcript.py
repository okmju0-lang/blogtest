#!/usr/bin/env python3
"""YouTube Transcript 추출기"""

import os
import sys
import time
import argparse
from datetime import datetime
from pathlib import Path


def extract_transcript(video_id: str, output_dir: str) -> dict:
    try:
        from youtube_transcript_api import YouTubeTranscriptApi, NoTranscriptFound, TranscriptsDisabled
    except ImportError:
        return {"success": False, "error": "youtube-transcript-api not installed. Run: pip install youtube-transcript-api"}

    output_path = Path(output_dir)
    output_path.mkdir(parents=True, exist_ok=True)
    out_file = output_path / f"yt_{video_id}.md"
    skip_log = output_path / "_skip_log.md"

    for attempt in range(3):
        try:
            # v1.x API: 인스턴스 생성 후 fetch 호출
            try:
                ytt = YouTubeTranscriptApi()
                entries = ytt.fetch(video_id, languages=["ko", "ko-KR", "en", "en-US"])
            except (NoTranscriptFound, TranscriptsDisabled) as e:
                # 자막 없음 — 스킵
                _log_skip(skip_log, f"yt_{video_id}", "NoTranscript", f"https://www.youtube.com/watch?v={video_id}")
                return {"success": False, "skipped": True, "reason": str(e)}

            text = "\n".join(entry.text for entry in entries)
            if len(text) < 100:
                _log_skip(skip_log, f"yt_{video_id}", "TooShort", f"https://www.youtube.com/watch?v={video_id}")
                return {"success": False, "skipped": True, "reason": "transcript too short"}

            content = f"""---
source_id: yt_{video_id}
source_type: youtube
url: https://www.youtube.com/watch?v={video_id}
title: (제목 수동 확인 필요)
extracted_at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
---

# YouTube Transcript: {video_id}

{text}
"""
            out_file.write_text(content, encoding="utf-8")
            return {"success": True, "file": str(out_file), "chars": len(text)}

        except Exception as e:
            if attempt < 2:
                time.sleep(2 ** attempt)
                continue
            _log_skip(skip_log, f"yt_{video_id}", f"Error:{type(e).__name__}", f"https://www.youtube.com/watch?v={video_id}")
            return {"success": False, "skipped": True, "reason": str(e)}

    return {"success": False, "reason": "max_retries_exceeded"}


def _log_skip(log_file: Path, source_id: str, reason: str, url: str):
    ts = datetime.now().strftime("%Y-%m-%d %H:%M")
    line = f"- {ts} | {source_id} | {reason} | {url}\n"
    with open(log_file, "a", encoding="utf-8") as f:
        f.write(line)


def main():
    parser = argparse.ArgumentParser(description="YouTube Transcript 추출기")
    parser.add_argument("--video_id", required=True, help="YouTube 동영상 ID")
    parser.add_argument("--output_dir", default="output/sources", help="출력 디렉토리")
    args = parser.parse_args()

    result = extract_transcript(args.video_id, args.output_dir)
    import json
    print(json.dumps(result, ensure_ascii=False, indent=2))
    sys.exit(0 if result.get("success") or result.get("skipped") else 1)


if __name__ == "__main__":
    main()
