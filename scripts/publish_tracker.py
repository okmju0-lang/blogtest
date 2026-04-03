#!/usr/bin/env python3
"""
발행 이력 관리 + 중복 콘텐츠 검사 스크립트

기능:
    1. 발행 이력 기록 (publish_log.md에 누적)
    2. 신규 글감/초고와 기존 발행 글 간 중복도 검사
    3. 키워드/제목 유사도 분석

사용법:
    # 발행 이력 기록
    python scripts/publish_tracker.py log <post_id> [--url <blog_url>] [--ghost-id <id>]

    # 중복 검사 — 제목으로
    python scripts/publish_tracker.py check --title "새 글 제목"

    # 중복 검사 — 글감 카드 파일로
    python scripts/publish_tracker.py check --idea output/story-ideas/idea_20260327_1.md

    # 중복 검사 — 초고 파일로
    python scripts/publish_tracker.py check --draft output/drafts/post_20260327_1/draft_v1.md

    # 발행 이력 조회
    python scripts/publish_tracker.py list

    # 발행 이력 통계
    python scripts/publish_tracker.py stats
"""

import sys
import os
import re
import io
import math
from pathlib import Path

# Windows cp949 인코딩 이슈 방지
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding="utf-8", errors="replace")
from datetime import datetime
from collections import Counter
from dataclasses import dataclass, field

PROJECT_ROOT = Path(__file__).parent.parent
POSTS_DIR = PROJECT_ROOT / "output" / "posts"
LOG_FILE = PROJECT_ROOT / "output" / "publish_log.md"


# ─── 데이터 모델 ──────────────────────────────────────────────

@dataclass
class PostMeta:
    """포스트 메타데이터"""
    post_id: str
    title: str
    category: str
    keywords: list[str]
    created_at: str
    published: bool
    meta_description: str = ""
    blog_url: str = ""
    published_at: str = ""


@dataclass
class SimilarityResult:
    """유사도 검사 결과"""
    post_id: str
    title: str
    title_similarity: float
    keyword_overlap: float
    combined_score: float

    @property
    def level(self) -> str:
        if self.combined_score >= 0.7:
            return "HIGH"
        elif self.combined_score >= 0.4:
            return "MEDIUM"
        return "LOW"


# ─── frontmatter 파싱 ─────────────────────────────────────────

def parse_frontmatter(filepath: str) -> dict:
    """마크다운 파일의 frontmatter를 딕셔너리로 파싱"""
    with open(filepath, "r", encoding="utf-8") as f:
        content = f.read()

    fm = {}
    lines = content.split("\n")
    if not lines or lines[0].strip() != "---":
        return fm

    fm_lines = []
    for line in lines[1:]:
        if line.strip() == "---":
            break
        fm_lines.append(line)

    current_key = None
    current_list = None

    for line in fm_lines:
        # 리스트 아이템
        if line.startswith("  - "):
            if current_list is not None:
                current_list.append(line.strip("- ").strip().strip('"'))
            continue

        # 키-값 쌍
        match = re.match(r"^(\w[\w_]*)\s*:\s*(.*)$", line)
        if match:
            key = match.group(1)
            value = match.group(2).strip().strip('"')

            if current_key and current_list is not None:
                fm[current_key] = current_list

            if not value:
                current_key = key
                current_list = []
            else:
                fm[key] = value
                current_key = key
                current_list = None
        elif not line.strip():
            if current_key and current_list is not None:
                fm[current_key] = current_list
                current_key = None
                current_list = None

    # 마지막 리스트 처리
    if current_key and current_list is not None:
        fm[current_key] = current_list

    return fm


def load_post_meta(post_dir: Path) -> PostMeta | None:
    """포스트 디렉토리에서 메타데이터 로드"""
    post_file = post_dir / "post.md"
    if not post_file.exists():
        return None

    fm = parse_frontmatter(str(post_file))
    if not fm.get("post_id"):
        return None

    keywords = fm.get("target_keywords", [])
    if isinstance(keywords, str):
        keywords = [keywords]

    return PostMeta(
        post_id=fm.get("post_id", ""),
        title=fm.get("title", ""),
        category=fm.get("category", ""),
        keywords=keywords,
        created_at=fm.get("created_at", ""),
        published=fm.get("published", "false").lower() == "true",
        meta_description=fm.get("meta_description", ""),
    )


def load_all_posts() -> list[PostMeta]:
    """output/posts/ 내 모든 포스트 메타데이터 로드"""
    if not POSTS_DIR.exists():
        return []

    posts = []
    for d in sorted(POSTS_DIR.iterdir()):
        if d.is_dir():
            meta = load_post_meta(d)
            if meta:
                posts.append(meta)
    return posts


# ─── 유사도 계산 ──────────────────────────────────────────────

def tokenize_korean(text: str) -> list[str]:
    """한국어 텍스트를 단순 토큰화 (형태소 분석기 없이 2-gram + 단어)"""
    # 특수문자 제거, 소문자화
    text = re.sub(r"[^\w\s가-힣]", " ", text.lower())
    words = text.split()

    tokens = list(words)  # 단어 단위
    # 2-gram 추가 (한국어 복합어 매칭용)
    for word in words:
        if len(word) >= 4:
            for i in range(len(word) - 1):
                tokens.append(word[i:i+2])
    return tokens


def cosine_similarity(tokens_a: list[str], tokens_b: list[str]) -> float:
    """두 토큰 리스트 간 코사인 유사도"""
    if not tokens_a or not tokens_b:
        return 0.0

    counter_a = Counter(tokens_a)
    counter_b = Counter(tokens_b)

    all_tokens = set(counter_a.keys()) | set(counter_b.keys())

    dot = sum(counter_a.get(t, 0) * counter_b.get(t, 0) for t in all_tokens)
    mag_a = math.sqrt(sum(v**2 for v in counter_a.values()))
    mag_b = math.sqrt(sum(v**2 for v in counter_b.values()))

    if mag_a == 0 or mag_b == 0:
        return 0.0

    return dot / (mag_a * mag_b)


def keyword_overlap(keywords_a: list[str], keywords_b: list[str]) -> float:
    """키워드 리스트 간 겹침 비율 (Jaccard)"""
    if not keywords_a or not keywords_b:
        return 0.0

    set_a = set(k.lower().strip() for k in keywords_a)
    set_b = set(k.lower().strip() for k in keywords_b)

    intersection = set_a & set_b
    union = set_a | set_b

    if not union:
        return 0.0

    return len(intersection) / len(union)


def check_similarity(title: str, keywords: list[str], existing_posts: list[PostMeta]) -> list[SimilarityResult]:
    """신규 글과 기존 포스트들 간 유사도 검사"""
    results = []
    new_tokens = tokenize_korean(title)

    for post in existing_posts:
        title_sim = cosine_similarity(new_tokens, tokenize_korean(post.title))
        kw_overlap = keyword_overlap(keywords, post.keywords)

        # 가중 결합 (제목 60%, 키워드 40%)
        combined = title_sim * 0.6 + kw_overlap * 0.4

        results.append(SimilarityResult(
            post_id=post.post_id,
            title=post.title,
            title_similarity=title_sim,
            keyword_overlap=kw_overlap,
            combined_score=combined,
        ))

    return sorted(results, key=lambda x: -x.combined_score)


# ─── 발행 이력 기록 ───────────────────────────────────────────

def load_publish_log() -> list[dict]:
    """publish_log.md에서 기존 발행 이력 파싱"""
    if not LOG_FILE.exists():
        return []

    with open(LOG_FILE, "r", encoding="utf-8") as f:
        content = f.read()

    entries = []
    for line in content.split("\n"):
        # 테이블 행 파싱: | post_id | title | category | date | url |
        if line.startswith("|") and not line.startswith("| ---") and not line.startswith("| post_id"):
            cells = [c.strip() for c in line.split("|")[1:-1]]
            if len(cells) >= 5:
                entries.append({
                    "post_id": cells[0],
                    "title": cells[1],
                    "category": cells[2],
                    "published_at": cells[3],
                    "blog_url": cells[4],
                })
    return entries


def log_publish(post_id: str, blog_url: str = "", ghost_id: str = ""):
    """발행 이력을 publish_log.md에 추가"""
    # 포스트 메타 로드
    post_dir = POSTS_DIR / post_id
    meta = load_post_meta(post_dir)
    if not meta:
        print(f"포스트를 찾을 수 없습니다: {post_dir}")
        sys.exit(1)

    now = datetime.now().strftime("%Y-%m-%d %H:%M")

    # 로그 파일 초기화 또는 추가
    if not LOG_FILE.exists():
        header = """# 발행 이력 (Publish Log)

> 자동 생성 — `scripts/publish_tracker.py log` 실행 시 업데이트됨

| post_id | title | category | published_at | blog_url |
|---|---|---|---|---|
"""
        LOG_FILE.parent.mkdir(parents=True, exist_ok=True)
        with open(LOG_FILE, "w", encoding="utf-8") as f:
            f.write(header)

    # 중복 기록 방지
    existing = load_publish_log()
    for entry in existing:
        if entry["post_id"] == post_id:
            print(f"이미 기록된 포스트입니다: {post_id}")
            return

    # 추가
    url_display = blog_url if blog_url else "-"
    new_row = f"| {post_id} | {meta.title} | {meta.category} | {now} | {url_display} |\n"

    with open(LOG_FILE, "a", encoding="utf-8") as f:
        f.write(new_row)

    print(f"\u2705 발행 이력 기록 완료: {post_id}")
    print(f"   제목: {meta.title}")
    print(f"   카테고리: {meta.category}")
    if blog_url:
        print(f"   URL: {blog_url}")


# ─── CLI 명령어 ───────────────────────────────────────────────

def cmd_check(args: list[str]):
    """중복 검사 실행"""
    title = ""
    keywords = []

    i = 0
    while i < len(args):
        if args[i] == "--title" and i + 1 < len(args):
            title = args[i + 1]
            i += 2
        elif args[i] == "--idea" and i + 1 < len(args):
            fm = parse_frontmatter(args[i + 1])
            title = fm.get("title", "") or fm.get("제목", "")
            # 글감 카드에서 앵글/논점도 활용
            i += 2
        elif args[i] == "--draft" and i + 1 < len(args):
            fm = parse_frontmatter(args[i + 1])
            title = fm.get("title", "")
            keywords = fm.get("target_keywords", [])
            if isinstance(keywords, str):
                keywords = [keywords]
            i += 2
        elif args[i] == "--keywords" and i + 1 < len(args):
            keywords = [k.strip() for k in args[i + 1].split(",")]
            i += 2
        else:
            i += 1

    if not title:
        print("제목을 지정해주세요: --title \"제목\" 또는 --idea/--draft 파일 경로")
        sys.exit(1)

    posts = load_all_posts()
    if not posts:
        print("기존 발행 포스트가 없습니다. 중복 없음.")
        sys.exit(0)

    results = check_similarity(title, keywords, posts)

    # 출력
    print()
    print(f"{'='*60}")
    print(f"  중복 콘텐츠 검사 결과")
    print(f"{'='*60}")
    print(f"  검사 대상: \"{title}\"")
    if keywords:
        print(f"  키워드: {', '.join(keywords)}")
    print(f"  비교 대상: {len(posts)}개 기존 포스트")
    print(f"{'─'*60}")

    high_count = sum(1 for r in results if r.level == "HIGH")
    medium_count = sum(1 for r in results if r.level == "MEDIUM")

    if high_count > 0:
        print(f"\n  \u274c 높은 유사도 발견 ({high_count}건) — 주제 차별화 필요")
    elif medium_count > 0:
        print(f"\n  \u26a0\ufe0f  중간 유사도 발견 ({medium_count}건) — 앵글 차별화 권장")
    else:
        print(f"\n  \u2705 유사한 기존 글이 없습니다")

    # 상위 5개만 표시
    shown = 0
    for r in results:
        if r.combined_score < 0.1:
            break
        if shown >= 5:
            break

        level_icon = {"HIGH": "\u274c", "MEDIUM": "\u26a0\ufe0f", "LOW": "\u2022"}
        print(f"\n  {level_icon.get(r.level, '?')} [{r.level}] {r.post_id}")
        print(f"    제목: {r.title}")
        print(f"    제목 유사도: {r.title_similarity:.1%}  |  키워드 겹침: {r.keyword_overlap:.1%}  |  종합: {r.combined_score:.1%}")
        shown += 1

    print(f"\n{'='*60}")

    # 종료 코드: HIGH 존재 시 2, MEDIUM만 시 1, 그 외 0
    if high_count > 0:
        sys.exit(2)
    elif medium_count > 0:
        sys.exit(1)
    sys.exit(0)


def cmd_list(args: list[str]):
    """발행 이력 조회"""
    entries = load_publish_log()

    if not entries:
        # 로그가 없으면 포스트 디렉토리에서 직접 조회
        posts = load_all_posts()
        if not posts:
            print("발행 이력이 없습니다.")
            return

        print()
        print(f"{'='*60}")
        print(f"  발행 이력 (output/posts/ 기준, {len(posts)}건)")
        print(f"{'='*60}")
        for p in posts:
            status = "\u2705" if p.published else "\u23f3"
            print(f"  {status} {p.post_id:22s} | {p.category:20s} | {p.title[:30]}")
        print(f"{'='*60}")
        return

    print()
    print(f"{'='*60}")
    print(f"  발행 이력 ({len(entries)}건)")
    print(f"{'='*60}")
    for e in entries:
        print(f"  {e['post_id']:22s} | {e['category']:20s} | {e['title'][:30]}")
        if e.get("blog_url") and e["blog_url"] != "-":
            print(f"  {'':22s} | URL: {e['blog_url']}")
    print(f"{'='*60}")


def cmd_stats(args: list[str]):
    """발행 통계"""
    posts = load_all_posts()
    if not posts:
        print("포스트가 없습니다.")
        return

    # 카테고리별 집계
    by_category = Counter(p.category for p in posts)
    by_month = Counter(p.created_at[:7] for p in posts if p.created_at)

    # 키워드 빈도
    all_keywords = []
    for p in posts:
        all_keywords.extend(p.keywords)
    kw_freq = Counter(k.lower().strip() for k in all_keywords)

    print()
    print(f"{'='*60}")
    print(f"  발행 통계 (총 {len(posts)}건)")
    print(f"{'='*60}")

    print(f"\n  카테고리별:")
    for cat, count in by_category.most_common():
        bar = "\u2588" * count
        print(f"    {cat:25s} {bar} {count}건")

    print(f"\n  월별:")
    for month, count in sorted(by_month.items()):
        bar = "\u2588" * count
        print(f"    {month:25s} {bar} {count}건")

    print(f"\n  자주 사용된 키워드 (상위 10개):")
    for kw, count in kw_freq.most_common(10):
        print(f"    {kw:30s} {count}회")

    print(f"\n{'='*60}")


def cmd_log(args: list[str]):
    """발행 이력 기록"""
    if not args:
        print("post_id를 지정해주세요: python scripts/publish_tracker.py log <post_id>")
        sys.exit(1)

    post_id = args[0]
    blog_url = ""
    ghost_id = ""

    i = 1
    while i < len(args):
        if args[i] == "--url" and i + 1 < len(args):
            blog_url = args[i + 1]
            i += 2
        elif args[i] == "--ghost-id" and i + 1 < len(args):
            ghost_id = args[i + 1]
            i += 2
        else:
            i += 1

    log_publish(post_id, blog_url, ghost_id)


# ─── 메인 ────────────────────────────────────────────────────

def main():
    if len(sys.argv) < 2:
        print(__doc__)
        sys.exit(1)

    command = sys.argv[1]
    remaining = sys.argv[2:]

    commands = {
        "log": cmd_log,
        "check": cmd_check,
        "list": cmd_list,
        "stats": cmd_stats,
    }

    if command not in commands:
        print(f"알 수 없는 명령: {command}")
        print(f"사용 가능: {', '.join(commands.keys())}")
        sys.exit(1)

    commands[command](remaining)


if __name__ == "__main__":
    main()
