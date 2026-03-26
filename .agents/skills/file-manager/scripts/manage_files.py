#!/usr/bin/env python3
"""산출물 파일 생성, 이동, 버전 관리"""

import os
import sys
import json
import shutil
import argparse
from datetime import datetime
from pathlib import Path
import re


def save_file(path: str, content: str) -> dict:
    p = Path(path)
    p.parent.mkdir(parents=True, exist_ok=True)
    for attempt in range(2):
        try:
            p.write_text(content, encoding="utf-8")
            return {"success": True, "file": str(p)}
        except Exception as e:
            if attempt == 0:
                continue
            return {"success": False, "error": str(e)}
    return {"success": False, "error": "max_retries_exceeded"}


def move_file(src: str, dst: str) -> dict:
    src_p, dst_p = Path(src), Path(dst)
    if not src_p.exists():
        return {"success": False, "error": f"Source not found: {src}"}
    dst_p.parent.mkdir(parents=True, exist_ok=True)
    try:
        shutil.copy2(str(src_p), str(dst_p))
        return {"success": True, "src": src, "dst": dst}
    except Exception as e:
        return {"success": False, "error": str(e)}


def next_version(post_id: str, prefix: str) -> dict:
    base = Path("output/drafts") / post_id
    if not base.exists():
        return {"success": True, "next_version": 1, "filename": f"{prefix}1.md"}
    pattern = re.compile(rf"^{re.escape(prefix)}(\d+)\.md$")
    versions = []
    for f in base.iterdir():
        m = pattern.match(f.name)
        if m:
            versions.append(int(m.group(1)))
    n = max(versions) + 1 if versions else 1
    return {"success": True, "next_version": n, "filename": f"{prefix}{n}.md"}


def new_post_id() -> dict:
    today = datetime.now().strftime("%Y%m%d")
    base = Path("output/drafts")
    base.mkdir(parents=True, exist_ok=True)
    pattern = re.compile(rf"^post_{today}_(\d+)$")
    existing = [int(m.group(1)) for d in base.iterdir() if d.is_dir() for m in [pattern.match(d.name)] if m]
    n = max(existing) + 1 if existing else 1
    post_id = f"post_{today}_{n}"
    (base / post_id).mkdir(parents=True, exist_ok=True)
    (base / post_id / "images").mkdir(exist_ok=True)
    return {"success": True, "post_id": post_id}


def main():
    parser = argparse.ArgumentParser(description="파일 관리 유틸리티")
    sub = parser.add_subparsers(dest="command", required=True)

    save_p = sub.add_parser("save")
    save_p.add_argument("--path", required=True)
    save_p.add_argument("--content", help="저장할 내용 (없으면 stdin)")

    move_p = sub.add_parser("move")
    move_p.add_argument("--src", required=True)
    move_p.add_argument("--dst", required=True)

    ver_p = sub.add_parser("next_version")
    ver_p.add_argument("--post_id", required=True)
    ver_p.add_argument("--prefix", default="draft_v")

    sub.add_parser("new_post_id")

    args = parser.parse_args()

    if args.command == "save":
        content = args.content if args.content else sys.stdin.read()
        result = save_file(args.path, content)
    elif args.command == "move":
        result = move_file(args.src, args.dst)
    elif args.command == "next_version":
        result = next_version(args.post_id, args.prefix)
    elif args.command == "new_post_id":
        result = new_post_id()
    else:
        result = {"success": False, "error": "unknown command"}

    print(json.dumps(result, ensure_ascii=False, indent=2))
    sys.exit(0 if result.get("success") else 1)


if __name__ == "__main__":
    main()
