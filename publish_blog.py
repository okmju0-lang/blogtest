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



# ─── 마크다운 → HTML 변환 ───

def md_to_html(md_text):
    """마크다운 텍스트를 기본 HTML로 변환한다."""
    html = md_text

    # 코드 블록
    def convert_code_block(match):
        code = match.group(2).strip()
        code = code.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")
        return f"<pre><code>{code}</code></pre>"
    html = re.sub(r"```(\w*)\n(.*?)```", convert_code_block, html, flags=re.DOTALL)

    # 인라인 코드
    html = re.sub(r"`([^`]+)`", r"<code>\1</code>", html)

    # 이미지
    html = re.sub(
        r"!\[([^\]]*)\]\(([^)]+)\)",
        r'<img src="\2" alt="\1" style="max-width:100%;height:auto;" />',
        html,
    )

    # 링크
    html = re.sub(r"\[([^\]]+)\]\(([^)]+)\)", r'<a href="\2">\1</a>', html)

    # 헤딩
    html = re.sub(r"^#### (.+)$", r"<h4>\1</h4>", html, flags=re.MULTILINE)
    html = re.sub(r"^### (.+)$", r"<h3>\1</h3>", html, flags=re.MULTILINE)
    html = re.sub(r"^## (.+)$", r"<h2>\1</h2>", html, flags=re.MULTILINE)
    html = re.sub(r"^# (.+)$", r"<h1>\1</h1>", html, flags=re.MULTILINE)

    # 굵은 글씨 / 기울임
    html = re.sub(r"\*\*(.+?)\*\*", r"<strong>\1</strong>", html)
    html = re.sub(r"\*(.+?)\*", r"<em>\1</em>", html)

    # 인용 블록 + CTA 블록
    def convert_blockquotes(text):
        cta_keywords = ("컨설팅", "문의", "상담")
        cta_actions = ("확인해보세요", "시작해보세요", "만나보세요", "알아보기")
        lines = text.split("\n")
        result = []
        in_quote = False
        quote_lines = []
        for line in lines:
            if line.startswith("> "):
                if not in_quote:
                    in_quote = True
                    quote_lines = []
                quote_lines.append(line[2:])
            else:
                if in_quote:
                    content = "<br>\n".join(quote_lines)
                    joined = " ".join(quote_lines)
                    is_cta = any(k in joined for k in cta_keywords) and any(a in joined for a in cta_actions)
                    if is_cta:
                        result.append('<div class="cta-block">' + content + "</div>")
                    else:
                        result.append("<blockquote>" + content + "</blockquote>")
                    in_quote = False
                    quote_lines = []
                result.append(line)
        if in_quote:
            content = "<br>\n".join(quote_lines)
            joined = " ".join(quote_lines)
            is_cta = any(k in joined for k in cta_keywords) and any(a in joined for a in cta_actions)
            if is_cta:
                result.append('<div class="cta-block">' + content + "</div>")
            else:
                result.append("<blockquote>" + content + "</blockquote>")
        return "\n".join(result)
    html = convert_blockquotes(html)

    # 테이블
    def convert_tables(text):
        lines = text.split("\n")
        result = []
        i = 0
        while i < len(lines):
            if (i + 1 < len(lines)
                    and "|" in lines[i]
                    and re.match(r"^\|[\s\-:|]+\|$", lines[i + 1].strip())):
                table_lines = [lines[i]]
                i += 2
                while i < len(lines) and "|" in lines[i] and lines[i].strip().startswith("|"):
                    table_lines.append(lines[i])
                    i += 1
                header_cells = [c.strip() for c in table_lines[0].strip().strip("|").split("|")]
                thead = "<tr>" + "".join(f"<th>{c}</th>" for c in header_cells) + "</tr>"
                tbody_rows = []
                for row_line in table_lines[1:]:
                    cells = [c.strip() for c in row_line.strip().strip("|").split("|")]
                    tbody_rows.append("<tr>" + "".join(f"<td>{c}</td>" for c in cells) + "</tr>")
                result.append(f'<div class="table-wrap"><table><thead>{thead}</thead><tbody>{"".join(tbody_rows)}</tbody></table></div>')
            else:
                result.append(lines[i])
                i += 1
        return "\n".join(result)
    html = convert_tables(html)

    # 구분선
    html = re.sub(r"^---+$", r"<hr />", html, flags=re.MULTILINE)

    # 목록
    html = re.sub(r"^- (.+)$", r"<li>\1</li>", html, flags=re.MULTILINE)
    html = re.sub(r"^\d+\. (.+)$", r"<li>\1</li>", html, flags=re.MULTILINE)

    # 문단
    paragraphs = re.split(r"\n\n+", html)
    wrapped = []
    for p in paragraphs:
        p = p.strip()
        if not p:
            continue
        if re.match(r"<(h[1-6]|li|hr|img|div|table|ul|ol|blockquote|pre)", p):
            wrapped.append(p)
        else:
            wrapped.append(f"<p>{p}</p>")

    return "\n".join(wrapped)


# ─── 인라인 스타일 ───

INLINE_STYLES = {
    "p": "margin:16px 0;",
    "li": "margin:8px 0;",
    "img": "border-radius:8px;margin:16px 0;max-width:100%;height:auto;",
    "body": "font-family:'Pretendard',-apple-system,sans-serif;line-height:1.8;color:#333;max-width:680px;margin:0 auto;padding:20px;",
    "h1": "font-size:28px;margin-top:32px;color:#111;",
    "h2": "font-size:22px;margin-top:28px;color:#1a1a1a;",
    "h3": "font-size:18px;margin-top:24px;color:#1a1a1a;",
    "h4": "font-size:16px;margin-top:20px;",
    "a": "color:#2563eb;",
    "hr": "border:none;border-top:1px solid #e5e7eb;margin:32px 0;",
    "strong": "color:#111;",
    "code": "background:#f1f5f9;color:#e11d48;padding:2px 6px;border-radius:4px;font-size:14px;font-family:'Consolas','Monaco',monospace;",
    "pre": "background:#1e293b;color:#e2e8f0;padding:20px 24px;border-radius:8px;overflow-x:auto;font-size:14px;line-height:1.6;margin:24px 0;",
    "blockquote": "background-color:#f0f4ff;background:linear-gradient(135deg,#f0f4ff 0%,#e8eeff 100%);border-left:4px solid #2563eb;padding:24px 28px;margin:32px 0;border-radius:0 12px 12px 0;box-shadow:0 2px 8px rgba(37,99,235,0.08);font-size:16px;line-height:1.7;",
    "blockquote_strong": "color:#1e40af;",
    "table_wrap": "border-radius:12px;overflow-x:auto;-webkit-overflow-scrolling:touch;box-shadow:0 2px 12px rgba(0,0,0,0.08);margin:24px 0;",
    "table": "width:100%;border-collapse:collapse;font-size:15px;min-width:320px;",
    "th": "background-color:#1e293b;background:linear-gradient(135deg,#1e293b 0%,#334155 100%);color:#fff;padding:14px 20px;text-align:left;font-weight:600;font-size:14px;letter-spacing:0.3px;white-space:nowrap;",
    "td": "padding:13px 20px;border-bottom:1px solid #e5e7eb;color:#374151;font-size:14.5px;word-break:keep-all;",
    "td_even": "padding:13px 20px;border-bottom:1px solid #e5e7eb;color:#374151;font-size:14.5px;word-break:keep-all;background:#f8fafc;",
    "td_last": "padding:13px 20px;border-bottom:none;color:#374151;font-size:14.5px;word-break:keep-all;",
    "cta_block": "background-color:#1e3a5f;background:linear-gradient(135deg,#1e3a5f 0%,#2563eb 100%);color:#fff;padding:40px 36px;margin:48px 0 24px;border-radius:16px;text-align:center;font-size:17px;line-height:1.7;box-shadow:0 4px 16px rgba(37,99,235,0.2);",
    "cta_strong": "color:#fff;font-size:21px;display:block;margin-bottom:16px;",
    "cta_a": "color:#1e3a5f;background:#fff;padding:14px 36px;border-radius:8px;text-decoration:none;font-weight:700;font-size:16px;display:inline-block;margin-top:8px;",
}


def apply_inline_styles(html_body):
    """HTML 본문의 태그에 인라인 style 속성을 삽입한다."""
    s = INLINE_STYLES
    result = html_body

    # 이미지
    result = re.sub(
        r'<img ([^>]*)style="[^"]*"([^>]*)/>',
        lambda m: f'<img {m.group(1)}style="{s["img"]}"{m.group(2)}/>',
        result,
    )

    # CTA 블록
    def style_cta_block(match):
        block = match.group(0)
        block = block.replace('<div class="cta-block">', f'<div style="{s["cta_block"]}">')
        block = re.sub(r"<strong>", f'<strong style="{s["cta_strong"]}">', block)
        block = re.sub(r"<a ", f'<a style="{s["cta_a"]}" ', block)
        return block
    result = re.sub(r'<div class="cta-block">.*?</div>', style_cta_block, result, flags=re.DOTALL)

    # blockquote 내부 strong
    def style_blockquote(match):
        block = match.group(0)
        block = re.sub(r"<strong>", f'<strong style="{s["blockquote_strong"]}">', block)
        return block
    result = re.sub(r"<blockquote>.*?</blockquote>", style_blockquote, result, flags=re.DOTALL)

    # table-wrap
    result = result.replace('<div class="table-wrap">', f'<div style="{s["table_wrap"]}">')

    # 테이블 행 스타일
    def style_table(match):
        table_html = match.group(0)
        table_html = table_html.replace("<table>", f'<table style="{s["table"]}">')
        table_html = re.sub(r"<th>", f'<th style="{s["th"]}">', table_html)
        rows = re.findall(r"<tr><td.*?</tr>", table_html)
        for idx, row in enumerate(rows):
            is_last = (idx == len(rows) - 1)
            is_even = (idx % 2 == 1)
            if is_last and is_even:
                style = s["td_last"].rstrip(";") + ";background:#f8fafc;"
            elif is_last:
                style = s["td_last"]
            elif is_even:
                style = s["td_even"]
            else:
                style = s["td"]
            styled_row = re.sub(r"<td>", f'<td style="{style}">', row)
            table_html = table_html.replace(row, styled_row, 1)
        return table_html
    result = re.sub(r"<table>.*?</table>", style_table, result, flags=re.DOTALL)

    # 단순 태그
    for tag in ("h1", "h2", "h3", "h4", "p", "li", "hr", "strong", "blockquote", "a", "pre", "code"):
        result = re.sub(
            rf"<{tag}(?![^>]*style=)([^>]*)>",
            f'<{tag} style="{s[tag]}"\\1>',
            result,
        )

    # pre 안의 code 스타일 제거
    def strip_code_style_in_pre(m):
        inner = m.group(1)
        inner = re.sub(r'<code style="[^"]*"', "<code", inner)
        return f'<pre style="{s["pre"]}"{inner}'
    result = re.sub(r'<pre style="[^"]*"(.*?</pre>)', strip_code_style_in_pre, result, flags=re.DOTALL)

    return result


def host_local_images(html, post_dir, imgbb_api_key):
    """HTML 내 로컬 이미지를 imgbb에 업로드하고 호스팅 URL로 치환한다."""
    upload_cache = {}

    def replace_src(match):
        prefix = match.group(1)
        src = match.group(2)
        suffix = match.group(3)
        if src.startswith(("http://", "https://", "data:")):
            return match.group(0)
        img_path = os.path.normpath(os.path.join(post_dir, src))
        if not os.path.exists(img_path):
            return match.group(0)
        if img_path in upload_cache:
            hosted_url = upload_cache[img_path]
        else:
            print(f"  이미지 업로드 중: {os.path.basename(img_path)}")
            hosted_url = upload_image_to_imgbb(img_path, imgbb_api_key)
            upload_cache[img_path] = hosted_url
        if hosted_url:
            return f'{prefix}{hosted_url}{suffix}'
        return match.group(0)

    return re.sub(r'(<img\s[^>]*src=")([^"]+)(")', replace_src, html)


def render_post_markdown_html(body):
    """마크다운 본문을 블로그용 HTML로 변환한다. (md_to_html 래퍼)"""
    return md_to_html(body)

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

    # 마크다운 → HTML 변환 (블로그 프론트엔드가 HTML을 직접 렌더링)
    html_body = render_post_markdown_html(body)
    if imgbb_key and imgbb_key not in imgbb_placeholders:
        html_body = host_local_images(html_body, post_dir, imgbb_key)
    html_body = apply_inline_styles(html_body)

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
