"""
AX 블로그 어드민 API를 통한 블로그 포스트 자동 발행 스크립트

사용법:
    # 초안으로 저장 (기본)
    python publish_blog.py <post.md 파일 경로>

    # 즉시 발행
    python publish_blog.py <post.md 파일 경로> --publish

    # 슬러그 직접 지정
    python publish_blog.py <post.md 파일 경로> --publish --slug my-custom-slug

    # 대표 글로 설정
    python publish_blog.py <post.md 파일 경로> --publish --featured

블로그 API:
    POST   /api/blog           — 글 생성
    GET    /api/blog           — 글 목록 조회
    DELETE /api/blog/{id}      — 글 삭제
"""

import os
import sys
import io
import argparse
import re
import base64
import requests

from publish_stibee import md_to_html, apply_inline_styles, AVAILABLE_THEMES

# Windows 콘솔 인코딩 문제 방지
if sys.stdout.encoding and sys.stdout.encoding.lower() != "utf-8":
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding="utf-8", errors="replace")

BLOG_API_BASE = "https://ax-inquiry-system.vercel.app/api/blog"


def load_env(env_path=".env"):
    """간단한 .env 파일 로더"""
    if not os.path.exists(env_path):
        return
    with open(env_path, encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if not line or line.startswith("#"):
                continue
            if "=" in line:
                key, _, value = line.partition("=")
                os.environ.setdefault(key.strip(), value.strip())


def parse_post_md(file_path):
    """post.md 파일에서 frontmatter와 본문을 분리하여 반환한다."""
    with open(file_path, encoding="utf-8") as f:
        content = f.read()

    meta = {}
    body = content
    if content.startswith("---"):
        parts = content.split("---", 2)
        if len(parts) >= 3:
            frontmatter_text = parts[1].strip()
            body = parts[2].strip()
            for line in frontmatter_text.splitlines():
                if ":" in line and not line.startswith(" ") and not line.startswith("-"):
                    key, _, value = line.partition(":")
                    meta[key.strip()] = value.strip()

    return meta, body


def upload_image_to_imgbb(file_path, api_key):
    """이미지를 imgbb에 업로드하고 호스팅 URL을 반환한다."""
    with open(file_path, "rb") as f:
        encoded = base64.b64encode(f.read()).decode("ascii")
    try:
        resp = requests.post(
            "https://api.imgbb.com/1/upload",
            data={"key": api_key, "image": encoded},
            timeout=30,
        )
        if resp.status_code == 200:
            data = resp.json()
            if data.get("success"):
                return data["data"]["url"]
    except requests.RequestException as e:
        print(f"  [경고] imgbb 업로드 실패 ({os.path.basename(file_path)}): {e}")
    return None


def upload_local_images(body, post_dir, imgbb_key):
    """마크다운 본문 내 로컬 이미지 경로를 imgbb URL로 치환한다."""
    upload_cache = {}

    def replace_img(match):
        alt = match.group(1)
        src = match.group(2)
        if src.startswith(("http://", "https://", "data:")):
            return match.group(0)
        img_path = os.path.normpath(os.path.join(post_dir, src))
        if not os.path.exists(img_path):
            return match.group(0)
        if img_path in upload_cache:
            url = upload_cache[img_path]
        else:
            print(f"  이미지 업로드 중: {os.path.basename(img_path)}")
            url = upload_image_to_imgbb(img_path, imgbb_key)
            upload_cache[img_path] = url
        if url:
            return f"![{alt}]({url})"
        return match.group(0)

    return re.sub(r"!\[([^\]]*)\]\(([^)]+)\)", replace_img, body), upload_cache


def title_to_slug(title):
    """제목에서 URL 슬러그를 생성한다."""
    # 영문+숫자+한글 외 제거, 공백을 하이픈으로
    slug = re.sub(r"[^\w\s가-힣-]", "", title)
    slug = re.sub(r"\s+", "-", slug.strip())
    slug = slug.lower()[:80]
    return slug


def extract_subtitle(body):
    """본문 첫 문단에서 subtitle(메타 디스크립션 대체)을 추출한다."""
    lines = body.strip().split("\n")
    for line in lines:
        line = line.strip()
        # 헤딩, 이미지, 빈 줄 건너뜀
        if not line or line.startswith("#") or line.startswith("!") or line.startswith(">") or line.startswith("|") or line.startswith("-"):
            continue
        # 첫 텍스트 문단 사용
        clean = re.sub(r"\*\*([^*]+)\*\*", r"\1", line)  # bold 제거
        clean = re.sub(r"\[([^\]]+)\]\([^)]+\)", r"\1", clean)  # 링크 제거
        return clean[:200]
    return ""


def calculate_reading_time(body):
    """본문 글자 수 기반 예상 읽기 시간(분)을 계산한다."""
    # 한국어 기준 분당 약 500자
    char_count = len(re.sub(r"\s+", "", body))
    minutes = max(1, round(char_count / 500))
    return minutes


CATEGORY_MAP = {
    "case-study": "Case Study",
    "thought-leadership": "Thought Leadership",
    "company-news": "Company News",
    "ai-trend": "AI Trend",
    # 한국어 매핑
    "케이스 스터디": "Case Study",
    "사례 연구": "Case Study",
    "thought leadership": "Thought Leadership",
    "소트 리더십": "Thought Leadership",
    "company news": "Company News",
    "회사 뉴스": "Company News",
    "ai trend": "AI Trend",
    "ai 트렌드": "AI Trend",
}


def normalize_category(raw):
    """다양한 카테고리 표기를 API 호환 형식으로 정규화한다."""
    if not raw:
        return "AX"
    lower = raw.strip().strip('"').strip("'").lower()
    return CATEGORY_MAP.get(lower, raw.strip().strip('"').strip("'"))


def create_blog_post(payload):
    """블로그 API에 POST 요청으로 글을 생성한다."""
    try:
        resp = requests.post(
            BLOG_API_BASE,
            json=payload,
            headers={"Content-Type": "application/json"},
            timeout=30,
        )
    except requests.RequestException as e:
        print(f"[실패] 블로그 API 요청 실패: {e}")
        return None
    if resp.status_code not in (200, 201):
        print(f"[실패] 블로그 생성 실패 — HTTP {resp.status_code}")
        print(f"  응답: {resp.text}")
        return None
    try:
        return resp.json()
    except ValueError:
        print(f"[실패] API 응답 JSON 파싱 실패")
        print(f"  응답: {resp.text[:500]}")
        return None


def main():
    parser = argparse.ArgumentParser(
        description="AX 블로그 어드민 API를 통한 블로그 포스트 발행"
    )
    parser.add_argument("post_path", help="post.md 파일 경로")
    parser.add_argument(
        "--publish", action="store_true",
        help="즉시 발행 (미지정 시 초안으로 저장)",
    )
    parser.add_argument(
        "--slug", metavar="SLUG",
        help="URL 슬러그 직접 지정 (미지정 시 제목에서 자동 생성)",
    )
    parser.add_argument(
        "--featured", action="store_true",
        help="대표 글로 설정",
    )
    parser.add_argument(
        "--author", default="매직에꼴",
        help="저자명 (기본: 매직에꼴)",
    )
    parser.add_argument(
        "--theme", choices=AVAILABLE_THEMES, default=None,
        help=f"디자인 테마 ({', '.join(AVAILABLE_THEMES)}). 미지정 시 frontmatter의 theme 필드 → 기본 blue",
    )
    args = parser.parse_args()

    # .env 로드
    script_dir = os.path.dirname(os.path.abspath(__file__))
    load_env(os.path.join(script_dir, ".env"))

    # 파일 확인
    if not os.path.exists(args.post_path):
        print(f"[오류] 파일을 찾을 수 없습니다: {args.post_path}")
        sys.exit(1)

    # 포스트 파싱
    meta, body = parse_post_md(args.post_path)
    title = meta.get("title", "제목 없음").strip('"').strip("'")
    post_dir = os.path.dirname(os.path.abspath(args.post_path))

    print(f"[블로그 발행]")
    print(f"  제목: {title}")

    # 이미지 업로드
    imgbb_key = os.environ.get("IMGBB_API_KEY", "")
    imgbb_placeholders = {"your_imgbb_api_key_here", ""}
    thumbnail_url = None
    hero_image_url = None

    if imgbb_key and imgbb_key not in imgbb_placeholders:
        print("[이미지 호스팅] imgbb에 로컬 이미지 업로드 중...")
        body, upload_cache = upload_local_images(body, post_dir, imgbb_key)

        # 썸네일 업로드
        thumbnail_rel = meta.get("thumbnail", "")
        if thumbnail_rel:
            thumbnail_path = os.path.normpath(os.path.join(post_dir, thumbnail_rel))
            if thumbnail_path in upload_cache:
                thumbnail_url = upload_cache[thumbnail_path]
                hero_image_url = thumbnail_url
            elif os.path.exists(thumbnail_path):
                print(f"  이미지 업로드 중: {os.path.basename(thumbnail_path)}")
                thumbnail_url = upload_image_to_imgbb(thumbnail_path, imgbb_key)
                hero_image_url = thumbnail_url
    else:
        print("[경고] IMGBB_API_KEY가 설정되지 않았습니다.")
        print("  블로그 본문의 로컬 이미지가 웹에서 표시되지 않습니다.")
        print("  imgbb.com에서 무료 API 키를 발급받아 .env에 추가하세요.")
        print("  계속 진행하면 이미지 없이 텍스트만 발행됩니다.")
        # 로컬 이미지 경로를 제거하여 깨진 이미지 표시 방지
        body = re.sub(r"!\[([^\]]*)\]\((?!https?://)([^)]+)\)\n?", "", body)

    # 슬러그 생성
    slug = args.slug or title_to_slug(title)

    # 카테고리 정규화
    category = normalize_category(meta.get("category", ""))

    # 태그 추출 (frontmatter의 target_keywords)
    tags = meta.get("target_keywords", "")

    # subtitle 추출
    subtitle = meta.get("meta_description", "").strip('"').strip("'")
    if not subtitle:
        subtitle = extract_subtitle(body)

    # 읽기 시간
    reading_time = calculate_reading_time(body)

    # 테마 결정: CLI --theme > frontmatter theme > 기본 blue
    theme = args.theme or meta.get("theme", "blue").strip('"').strip("'")
    if theme not in AVAILABLE_THEMES:
        print(f"[경고] 알 수 없는 테마 '{theme}'. 기본 테마 'blue'를 사용합니다.")
        theme = "blue"

    # 마크다운 → HTML 변환 (블로그 프론트엔드가 HTML을 직접 렌더링)
    html_body = md_to_html(body)
    html_body = apply_inline_styles(html_body, theme=theme)

    # API 페이로드 구성
    payload = {
        "title": title,
        "slug": slug,
        "content": html_body,
        "subtitle": subtitle or None,
        "category": category,
        "tags": tags or None,
        "thumbnailUrl": thumbnail_url,
        "heroImageUrl": hero_image_url,
        "featured": args.featured,
        "published": args.publish,
        "author": args.author,
    }

    mode = "발행" if args.publish else "초안 저장"
    print(f"  카테고리: {category}")
    print(f"  테마: {theme}")
    print(f"  슬러그: {slug}")
    print(f"  모드: {mode}")
    print(f"  읽기 시간: {reading_time}분")
    if thumbnail_url:
        print(f"  썸네일: {thumbnail_url}")
    print()

    # API 호출
    print(f"[1/1] 블로그 글 {'발행' if args.publish else '저장'} 중...")
    result = create_blog_post(payload)

    if result:
        post_id = result.get("id", "")
        post_slug = result.get("slug", slug)
        print(f"\n[성공] 블로그 글이 {mode}되었습니다.")
        print(f"  ID: {post_id}")
        print(f"  URL: https://ax-inquiry-system.vercel.app/blog/{post_slug}")
        print(f"  어드민: https://ax-inquiry-system.vercel.app/admin/blog")
    else:
        print(f"\n[실패] 블로그 글 {mode}에 실패했습니다.")
        sys.exit(1)


if __name__ == "__main__":
    main()
