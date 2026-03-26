"""
블로그 디자인 매칭 HTML 프리뷰 생성기

카테고리별로 시각적으로 차별화된 디자인을 적용한다.
- AI Trend (월): 네온 그라디언트 히어로, 비교 하이라이트 카드
- Thought Leadership (수): 문제→해결 톤 전환, 실행 스텝 카드
- Case Study (금): 성과 수치 배너, Before/After 카드, 프로세스 타임라인

사용법:
    python preview_blog.py <post.md 파일 경로>
"""

import os
import sys
import io
import re
import argparse
import base64
import mimetypes

if sys.stdout.encoding and sys.stdout.encoding.lower() != "utf-8":
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding="utf-8", errors="replace")


def parse_post_md(file_path):
    with open(file_path, encoding="utf-8") as f:
        content = f.read()
    meta = {}
    body = content
    if content.startswith("---"):
        parts = content.split("---", 2)
        if len(parts) >= 3:
            frontmatter_text = parts[1].strip()
            body = parts[2].strip()
            current_key = None
            current_list = None
            for line in frontmatter_text.splitlines():
                if line.startswith("  - "):
                    if current_list is not None:
                        current_list.append(line.strip("- ").strip())
                elif ":" in line and not line.startswith(" ") and not line.startswith("-"):
                    if current_list is not None and current_key:
                        meta[current_key] = current_list
                        current_list = None
                    key, _, value = line.partition(":")
                    key = key.strip()
                    value = value.strip().strip('"').strip("'")
                    if not value:
                        current_key = key
                        current_list = []
                    else:
                        meta[key] = value
                        current_key = key
            if current_list is not None and current_key:
                meta[current_key] = current_list
    return meta, body


def extract_headings(body):
    headings = []
    for line in body.splitlines():
        m = re.match(r"^## (.+)$", line)
        if m:
            title = m.group(1).strip()
            anchor = re.sub(r"[^\w가-힣\s-]", "", title)
            anchor = re.sub(r"\s+", "-", anchor).strip("-").lower()
            headings.append({"title": title, "anchor": anchor})
    return headings


def md_to_html(md_text, category="ai-trend"):
    html = md_text

    def convert_code_block(match):
        code = match.group(2).strip()
        code = code.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")
        return f'<pre class="code-block"><code>{code}</code></pre>'

    html = re.sub(r"```(\w*)\n(.*?)```", convert_code_block, html, flags=re.DOTALL)
    html = re.sub(r"`([^`]+)`", r"<code>\1</code>", html)

    html = re.sub(
        r"!\[([^\]]*)\]\(([^)]+)\)",
        r'<figure class="post-image"><img src="\2" alt="\1" /><figcaption>\1</figcaption></figure>',
        html,
    )
    html = re.sub(r"\[([^\]]+)\]\(([^)]+)\)", r'<a href="\2">\1</a>', html)

    def h2_with_anchor(match):
        title = match.group(1).strip()
        anchor = re.sub(r"[^\w가-힣\s-]", "", title)
        anchor = re.sub(r"\s+", "-", anchor).strip("-").lower()
        return f'<h2 id="{anchor}">{title}</h2>'

    html = re.sub(r"^#### (.+)$", r"<h4>\1</h4>", html, flags=re.MULTILINE)
    html = re.sub(r"^### (.+)$", r"<h3>\1</h3>", html, flags=re.MULTILINE)
    html = re.sub(r"^## (.+)$", h2_with_anchor, html, flags=re.MULTILINE)
    html = re.sub(r"^# (.+)$", r"", html, flags=re.MULTILINE)

    html = re.sub(r"\*\*(.+?)\*\*", r"<strong>\1</strong>", html)
    html = re.sub(r"\*(.+?)\*", r"<em>\1</em>", html)

    # 인용 블록 — 카테고리별 CSS 클래스 분기
    def convert_blockquotes(text):
        cta_keywords = ("컨설팅", "문의", "상담", "진단")
        cta_actions = ("확인해보세요", "시작해보세요", "만나보세요", "알아보기", "시작할까요", "되셨나요", "있을까요")
        # case-study: "실행 포인트" / "교훈" 블록 감지
        action_keywords = ("실행 포인트", "교훈")
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
                    content = "<br>".join(quote_lines)
                    joined = " ".join(quote_lines)
                    is_cta = any(k in joined for k in cta_keywords) and any(a in joined for a in cta_actions)
                    is_action = any(k in joined for k in action_keywords)
                    if is_cta:
                        result.append(f'<div class="cta-block">{content}</div>')
                    elif is_action:
                        result.append(f'<blockquote class="action-point">{content}</blockquote>')
                    else:
                        result.append(f"<blockquote>{content}</blockquote>")
                    in_quote = False
                    quote_lines = []
                result.append(line)
        if in_quote:
            content = "<br>".join(quote_lines)
            joined = " ".join(quote_lines)
            is_cta = any(k in joined for k in cta_keywords) and any(a in joined for a in cta_actions)
            is_action = any(k in joined for k in action_keywords)
            if is_cta:
                result.append(f'<div class="cta-block">{content}</div>')
            elif is_action:
                result.append(f'<blockquote class="action-point">{content}</blockquote>')
            else:
                result.append(f"<blockquote>{content}</blockquote>")
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

    html = re.sub(r"^---+$", r"<hr />", html, flags=re.MULTILINE)
    html = re.sub(r"^- (.+)$", r'<li data-list="ul">\1</li>', html, flags=re.MULTILINE)
    html = re.sub(r"^\d+\. (.+)$", r'<li data-list="ol">\1</li>', html, flags=re.MULTILINE)
    html = re.sub(r"^&nbsp;$", "", html, flags=re.MULTILINE)

    def wrap_lists(text):
        lines = text.splitlines()
        result = []
        current_items = []
        current_list_type = None

        def flush_list():
            nonlocal current_items, current_list_type
            if not current_items:
                return
            items_html = "\n".join(
                re.sub(r'\sdata-list="(?:ul|ol)"', "", item, count=1) for item in current_items
            )
            result.append(f"<{current_list_type}>\n{items_html}\n</{current_list_type}>")
            current_items = []
            current_list_type = None

        for line in lines:
            stripped = line.strip()
            if stripped.startswith('<li data-list="'):
                list_type = "ol" if 'data-list="ol"' in stripped else "ul"
                if current_list_type and current_list_type != list_type:
                    flush_list()
                current_list_type = list_type
                current_items.append(stripped)
            else:
                flush_list()
                result.append(line)

        flush_list()
        return "\n".join(result)

    html = wrap_lists(html)

    wrapped = []
    paragraph_lines = []

    def flush_paragraph():
        nonlocal paragraph_lines
        if not paragraph_lines:
            return
        wrapped.append(f"<p>{' '.join(paragraph_lines)}</p>")
        paragraph_lines = []

    for line in html.splitlines():
        stripped = line.strip()
        if not stripped:
            flush_paragraph()
            continue
        if re.match(r"</?(h[1-6]|div|table|ul|ol|li|blockquote|pre|figure)\b", stripped) or stripped.startswith("<hr"):
            flush_paragraph()
            wrapped.append(stripped)
        else:
            paragraph_lines.append(stripped)

    flush_paragraph()
    html = "\n".join(wrapped)

    def add_structural_dividers(text):
        h2_count = 0

        def maybe_add_before_h2(match):
            nonlocal h2_count
            full = match.group(0)
            title = match.group(2).strip()
            should_divide = h2_count > 0
            h2_count += 1
            if should_divide:
                return '<hr class="section-break" />\n' + full
            return full

        text = re.sub(r'(<h2 id="[^"]+">([^<]+)</h2>)', lambda m: maybe_add_before_h2(m), text)
        text = re.sub(r'(?<!section-break" />\n)(<p><strong>참고 자료</strong></p>)', r'<hr class="section-break" />' + "\n" + r'\1', text)
        return text

    return add_structural_dividers(html)


def embed_local_images(html, post_dir):
    def replace_src(match):
        prefix = match.group(1)
        src = match.group(2)
        suffix = match.group(3)
        if src.startswith(("http://", "https://", "data:")):
            return match.group(0)
        img_path = os.path.join(post_dir, src)
        if not os.path.exists(img_path):
            return match.group(0)
        mime_type = mimetypes.guess_type(img_path)[0] or "image/png"
        with open(img_path, "rb") as f:
            encoded = base64.b64encode(f.read()).decode("ascii")
        return f'{prefix}data:{mime_type};base64,{encoded}{suffix}'
    return re.sub(r'(<img\s[^>]*src=")([^"]+)(")', replace_src, html)


# ─── 카테고리별 디자인 시스템 ───

CATEGORY_LABELS = {
    "ai-trend": "AI Trend",
    "thought-leadership": "Thought Leadership",
    "case-study": "Case Study",
    "company-news": "Company News",
}

# 공통 베이스 CSS
BASE_CSS = """
  @import url('https://cdn.jsdelivr.net/gh/orioncactus/pretendard/dist/web/static/pretendard.css');
  * { margin: 0; padding: 0; box-sizing: border-box; }
  body {
    font-family: 'Pretendard', -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif;
    color: #333; background: #fff; line-height: 1.8;
    -webkit-font-smoothing: antialiased;
  }
  .header {
    display: flex; align-items: center; justify-content: space-between;
    padding: 16px 40px; border-bottom: 1px solid #e5e7eb;
    position: sticky; top: 0; background: #fff; z-index: 100;
  }
  .header-left { display: flex; align-items: center; gap: 16px; }
  .header-logo { font-size: 18px; font-weight: 700; color: #111; text-decoration: none; }
  .header-logo span { color: #6366f1; }
  .header-nav { color: #555; font-size: 15px; border-left: 1px solid #d1d5db; padding-left: 16px; }
  .header-cta {
    background: #111; color: #fff; padding: 10px 20px; border-radius: 8px;
    font-size: 14px; font-weight: 600; text-decoration: none;
  }
  .layout {
    display: grid; grid-template-columns: 220px 1fr 260px;
    max-width: 1200px; margin: 0 auto; gap: 40px; padding: 40px 24px;
  }
  .toc { position: sticky; top: 80px; align-self: start; }
  .toc-label { font-size: 12px; font-weight: 700; letter-spacing: 1px; margin-bottom: 16px; }
  .toc-item {
    display: block; font-size: 14px; color: #6b7280; text-decoration: none;
    padding: 6px 0; border-left: 2px solid transparent; padding-left: 12px;
    transition: all 0.2s; line-height: 1.5;
  }
  .main-content { max-width: 700px; }
  .category-badge {
    display: inline-block; font-size: 13px; font-weight: 600;
    padding: 4px 14px; border-radius: 20px; margin-bottom: 16px;
  }
  .post-title {
    font-size: 32px; font-weight: 800; color: #111;
    line-height: 1.35; margin-bottom: 20px; letter-spacing: -0.5px;
  }
  .post-meta {
    display: flex; align-items: center; gap: 12px;
    margin-bottom: 32px; color: #9ca3af; font-size: 14px;
  }
  .author-avatar {
    width: 36px; height: 36px; border-radius: 50%;
    display: flex; align-items: center; justify-content: center;
    color: #fff; font-size: 14px; font-weight: 700;
  }
  .author-name { color: #374151; font-weight: 600; }
  .thumbnail { width: 100%; border-radius: 12px; margin-bottom: 32px; }
  article { font-size: 16px; line-height: 1.9; }
  article h2 { font-size: 22px; font-weight: 700; margin-top: 56px; margin-bottom: 20px; }
  article h3 { font-size: 18px; font-weight: 700; margin-top: 40px; margin-bottom: 16px; }
  article h4 { font-size: 16px; font-weight: 600; margin-top: 28px; margin-bottom: 12px; }
  article p { margin: 0; font-size: 16px; color: #374151; line-height: 1.95; }
  article p + p { margin-top: 22px; }
  article p + ul, article p + ol,
  article p + blockquote, article p + .table-wrap,
  article p + .post-image, article p + .code-block,
  article p + hr { margin-top: 28px; }
  article ul, article ol { margin: 24px 0 28px; padding-left: 4px; }
  article strong { color: #111; }
  article a { text-decoration: none; }
  article a:hover { text-decoration: underline; }
  article hr { border: none; border-top: 1px solid #e5e7eb; margin: 40px 0; }
  article hr.section-break {
    width: 96px; margin: 52px auto 36px;
    border-top: 2px solid #d1d5db; opacity: 0.9;
  }
  article li { margin: 12px 0 12px 24px; font-size: 16px; color: #374151; line-height: 1.85; padding-left: 4px; }
  article .post-image { margin: 36px 0; }
  article .post-image img { width: 100%; border-radius: 10px; }
  article .post-image figcaption { font-size: 13px; color: #9ca3af; text-align: center; margin-top: 8px; }
  article code {
    background: #f1f5f9; color: #e11d48; padding: 2px 6px; border-radius: 4px;
    font-size: 14px; font-family: 'Consolas', monospace;
  }
  article .code-block {
    background: #1e293b; color: #e2e8f0; padding: 20px 24px; border-radius: 8px;
    overflow-x: auto; font-size: 14px; line-height: 1.6; margin: 24px 0;
  }
  article .code-block code { background: none; color: inherit; padding: 0; }
  .sidebar-right { position: sticky; top: 80px; align-self: start; }
  .sidebar-label { font-size: 15px; font-weight: 600; color: #374151; margin-bottom: 16px; }
  .related-card {
    border-radius: 12px; overflow: hidden; box-shadow: 0 2px 8px rgba(0,0,0,0.06);
    margin-bottom: 16px; background: #fff; border: 1px solid #f3f4f6;
  }
  .related-card-img {
    width: 100%; height: 140px; display: flex;
    align-items: center; justify-content: center; color: #fff; font-size: 13px;
  }
  .related-card-title { padding: 12px 14px; font-size: 14px; font-weight: 600; color: #374151; line-height: 1.5; }
  .bottom-nav {
    display: flex; justify-content: space-between; padding: 24px 40px;
    border-top: 1px solid #e5e7eb; font-size: 14px;
  }
  .bottom-nav a { color: #6b7280; text-decoration: none; }
  @media (max-width: 1024px) {
    .layout { grid-template-columns: 1fr; padding: 24px 20px; }
    .toc, .sidebar-right { display: none; }
    .post-title { font-size: 26px; }
    .hero-banner { margin: 0 -20px; border-radius: 0; }
  }
"""

# ────────────────────────────────────────────
# AI Trend (월요일): 바이올렛 액센트
# ────────────────────────────────────────────
CSS_AI_TREND = """
  /* ── AI Trend 전용 ── */
  .hero-banner {
    background: linear-gradient(135deg, #0f0a2e 0%, #1e1b4b 40%, #4c1d95 100%);
    border-radius: 16px; padding: 48px 40px; margin-bottom: 36px;
    position: relative; overflow: hidden;
  }
  .hero-banner::before {
    content: ''; position: absolute; top: -50%; right: -20%;
    width: 400px; height: 400px;
    background: radial-gradient(circle, rgba(139,92,246,0.3) 0%, transparent 70%);
    border-radius: 50%;
  }
  .hero-banner::after {
    content: ''; position: absolute; bottom: -30%; left: 10%;
    width: 300px; height: 300px;
    background: radial-gradient(circle, rgba(59,130,246,0.2) 0%, transparent 70%);
    border-radius: 50%;
  }
  .hero-banner .category-badge {
    background: rgba(139,92,246,0.25); color: #c4b5fd;
    border: 1px solid rgba(139,92,246,0.3);
  }
  .hero-banner .post-title { color: #fff; position: relative; z-index: 1; }
  .hero-banner .post-meta { color: rgba(255,255,255,0.6); position: relative; z-index: 1; }
  .hero-banner .author-name { color: #e0e7ff; }
  .author-avatar { background: linear-gradient(135deg, #7c3aed, #a78bfa); }
  .toc-label { color: #7c3aed; }
  .toc-item:hover { color: #111; border-left-color: #7c3aed; }
  article h2 { color: #1e1b4b; border-left: 4px solid #7c3aed; padding-left: 14px; }
  article a { color: #7c3aed; }
  article blockquote {
    background: linear-gradient(135deg, #ede9fe 0%, #e0e7ff 100%);
    border-left: 4px solid #7c3aed; padding: 24px 28px; margin: 28px 0;
    border-radius: 0 12px 12px 0; box-shadow: 0 2px 8px rgba(124,58,237,0.1);
    font-size: 16px; line-height: 1.7;
  }
  article blockquote strong { color: #5b21b6; }
  .table-wrap {
    border-radius: 12px; overflow: hidden;
    box-shadow: 0 2px 16px rgba(124,58,237,0.12); margin: 24px 0;
  }
  article th {
    background: linear-gradient(135deg, #1e1b4b 0%, #4c1d95 100%);
    color: #e0e7ff; padding: 14px 20px; text-align: left;
    font-weight: 600; font-size: 14px;
  }
  article td {
    padding: 13px 20px; border-bottom: 1px solid #ede9fe;
    color: #374151; font-size: 14.5px;
  }
  article tbody tr:nth-child(even) td { background: #f5f3ff; }
  article tbody tr:last-child td { border-bottom: none; }
  .cta-block {
    background: linear-gradient(135deg, #1e1b4b 0%, #7c3aed 100%);
    color: #fff; padding: 40px 36px; margin: 48px 0 24px;
    border-radius: 16px; text-align: center; font-size: 17px; line-height: 1.7;
    box-shadow: 0 4px 20px rgba(124,58,237,0.25);
  }
  .cta-block strong { color: #fff; font-size: 21px; display: block; margin-bottom: 16px; }
  .cta-block a {
    color: #4c1d95; background: #fff; padding: 14px 36px; border-radius: 8px;
    text-decoration: none; font-weight: 700; font-size: 16px;
    display: inline-block; margin-top: 8px;
  }
  .footer-cta {
    background: linear-gradient(135deg, #0f0a2e, #4c1d95);
    color: #fff; text-align: center; padding: 64px 24px; margin-top: 48px;
  }
  .footer-cta h2 { font-size: 28px; font-weight: 800; margin-bottom: 12px; }
  .footer-cta p { font-size: 16px; color: #c4b5fd; margin-bottom: 28px; }
  .footer-cta-btn {
    display: inline-block; background: #fff; color: #4c1d95;
    padding: 16px 40px; border-radius: 12px; font-size: 16px;
    font-weight: 700; text-decoration: none;
  }
  .related-card-img { background: linear-gradient(135deg, #4c1d95, #7c3aed); }
  .thumbnail { box-shadow: 0 4px 24px rgba(124,58,237,0.15); }
"""

# ────────────────────────────────────────────
# Thought Leadership (수요일): 딥블루 액센트
# ────────────────────────────────────────────
CSS_THOUGHT_LEADERSHIP = """
  /* ── Thought Leadership 전용 ── */
  .hero-banner {
    background: linear-gradient(135deg, #0c1929 0%, #1e3a5f 40%, #1e40af 100%);
    border-radius: 16px; padding: 48px 40px; margin-bottom: 36px;
    position: relative; overflow: hidden;
  }
  .hero-banner::before {
    content: ''; position: absolute; top: -50%; right: -20%;
    width: 400px; height: 400px;
    background: radial-gradient(circle, rgba(37,99,235,0.3) 0%, transparent 70%);
    border-radius: 50%;
  }
  .hero-banner::after {
    content: ''; position: absolute; bottom: -30%; left: 10%;
    width: 300px; height: 300px;
    background: radial-gradient(circle, rgba(30,64,175,0.2) 0%, transparent 70%);
    border-radius: 50%;
  }
  .hero-banner .category-badge {
    background: rgba(37,99,235,0.25); color: #93c5fd;
    border: 1px solid rgba(37,99,235,0.3);
  }
  .hero-banner .post-title { color: #fff; position: relative; z-index: 1; }
  .hero-banner .post-meta { color: rgba(255,255,255,0.6); position: relative; z-index: 1; }
  .hero-banner .author-name { color: #bfdbfe; }
  .author-avatar { background: linear-gradient(135deg, #1e40af, #3b82f6); }
  .toc-label { color: #1e40af; }
  .toc-item:hover { color: #111; border-left-color: #1e40af; }
  article h2 { color: #1e3a5f; border-left: 4px solid #2563eb; padding-left: 14px; }
  article a { color: #2563eb; }
  article blockquote {
    background: linear-gradient(135deg, #dbeafe 0%, #e0e7ff 100%);
    border-left: 4px solid #2563eb; padding: 24px 28px; margin: 28px 0;
    border-radius: 0 12px 12px 0; box-shadow: 0 2px 8px rgba(37,99,235,0.1);
    font-size: 16px; line-height: 1.7;
  }
  article blockquote strong { color: #1e40af; }
  article blockquote.action-point {
    background: linear-gradient(135deg, #ecfdf5 0%, #d1fae5 100%);
    border-left: 4px solid #059669;
    box-shadow: 0 2px 8px rgba(5,150,105,0.1);
    position: relative; padding-left: 36px;
  }
  article blockquote.action-point::before {
    content: '\\2713'; position: absolute; left: 12px; top: 24px;
    color: #059669; font-size: 18px; font-weight: 700;
  }
  article blockquote.action-point strong { color: #065f46; }
  .table-wrap {
    border-radius: 12px; overflow: hidden;
    box-shadow: 0 2px 16px rgba(37,99,235,0.12); margin: 24px 0;
  }
  article th {
    background: linear-gradient(135deg, #1e3a5f 0%, #1e40af 100%);
    color: #bfdbfe; padding: 14px 20px; text-align: left;
    font-weight: 600; font-size: 14px;
  }
  article td {
    padding: 13px 20px; border-bottom: 1px solid #dbeafe;
    color: #374151; font-size: 14.5px;
  }
  article tbody tr:nth-child(even) td { background: #eff6ff; }
  article tbody tr:last-child td { border-bottom: none; }
  .cta-block {
    background: linear-gradient(135deg, #1e3a5f 0%, #2563eb 100%);
    color: #fff; padding: 40px 36px; margin: 48px 0 24px;
    border-radius: 16px; text-align: center; font-size: 17px; line-height: 1.7;
    box-shadow: 0 4px 20px rgba(37,99,235,0.25);
  }
  .cta-block strong { color: #fff; font-size: 21px; display: block; margin-bottom: 16px; }
  .cta-block a {
    color: #1e3a5f; background: #fff; padding: 14px 36px; border-radius: 8px;
    text-decoration: none; font-weight: 700; font-size: 16px;
    display: inline-block; margin-top: 8px;
  }
  .footer-cta {
    background: linear-gradient(135deg, #0c1929, #1e40af);
    color: #fff; text-align: center; padding: 64px 24px; margin-top: 48px;
  }
  .footer-cta h2 { font-size: 28px; font-weight: 800; margin-bottom: 12px; }
  .footer-cta p { font-size: 16px; color: #93c5fd; margin-bottom: 28px; }
  .footer-cta-btn {
    display: inline-block; background: #fff; color: #1e40af;
    padding: 16px 40px; border-radius: 12px; font-size: 16px;
    font-weight: 700; text-decoration: none;
  }
  .related-card-img { background: linear-gradient(135deg, #1e3a5f, #2563eb); }
  .thumbnail { box-shadow: 0 4px 24px rgba(37,99,235,0.15); }
"""

# ────────────────────────────────────────────
# Case Study (금요일): 틸 액센트
# ────────────────────────────────────────────
CSS_CASE_STUDY = """
  /* ── Case Study 전용 ── */
  .hero-banner {
    background: linear-gradient(135deg, #042f2e 0%, #064e3b 40%, #059669 100%);
    border-radius: 16px; padding: 48px 40px; margin-bottom: 36px;
    position: relative; overflow: hidden;
  }
  .hero-banner::before {
    content: ''; position: absolute; top: -50%; right: -20%;
    width: 400px; height: 400px;
    background: radial-gradient(circle, rgba(16,185,129,0.3) 0%, transparent 70%);
    border-radius: 50%;
  }
  .hero-banner::after {
    content: ''; position: absolute; bottom: -30%; left: 10%;
    width: 300px; height: 300px;
    background: radial-gradient(circle, rgba(5,150,105,0.2) 0%, transparent 70%);
    border-radius: 50%;
  }
  .hero-banner .category-badge {
    background: rgba(16,185,129,0.25); color: #a7f3d0;
    border: 1px solid rgba(16,185,129,0.3);
  }
  .hero-banner .post-title { color: #fff; position: relative; z-index: 1; }
  .hero-banner .post-meta { color: rgba(255,255,255,0.6); position: relative; z-index: 1; }
  .hero-banner .author-name { color: #d1fae5; }
  .author-avatar { background: linear-gradient(135deg, #059669, #10b981); }
  .toc-label { color: #059669; }
  .toc-item:hover { color: #111; border-left-color: #059669; }
  article h2 { color: #064e3b; border-left: 4px solid #059669; padding-left: 14px; }
  article a { color: #059669; }
  article blockquote {
    background: linear-gradient(135deg, #ecfdf5 0%, #d1fae5 100%);
    border-left: 4px solid #059669; padding: 24px 28px; margin: 28px 0;
    border-radius: 0 12px 12px 0; box-shadow: 0 2px 8px rgba(5,150,105,0.1);
    font-size: 16px; line-height: 1.7;
  }
  article blockquote strong { color: #065f46; }
  article blockquote.action-point {
    background: linear-gradient(135deg, #f0f9ff 0%, #e0f2fe 100%);
    border-left: 4px solid #0284c7;
    box-shadow: 0 2px 8px rgba(2,132,199,0.08);
    position: relative; padding-left: 36px;
  }
  article blockquote.action-point::before {
    content: '\\279C'; position: absolute; left: 12px; top: 24px;
    color: #0284c7; font-size: 16px; font-weight: 700;
  }
  article blockquote.action-point strong { color: #075985; }
  .table-wrap {
    border-radius: 12px; overflow: hidden;
    box-shadow: 0 2px 16px rgba(5,150,105,0.12); margin: 24px 0;
  }
  article th {
    background: linear-gradient(135deg, #064e3b 0%, #059669 100%);
    color: #d1fae5; padding: 14px 20px; text-align: left;
    font-weight: 600; font-size: 14px;
  }
  article td {
    padding: 13px 20px; border-bottom: 1px solid #d1fae5;
    color: #374151; font-size: 14.5px;
  }
  article tbody tr:nth-child(even) td { background: #f0fdf4; }
  article tbody tr:last-child td { border-bottom: none; }
  .cta-block {
    background: linear-gradient(135deg, #064e3b 0%, #059669 100%);
    color: #fff; padding: 40px 36px; margin: 48px 0 24px;
    border-radius: 16px; text-align: center; font-size: 17px; line-height: 1.7;
    box-shadow: 0 4px 20px rgba(5,150,105,0.25);
  }
  .cta-block strong { color: #fff; font-size: 21px; display: block; margin-bottom: 16px; }
  .cta-block a {
    color: #064e3b; background: #fff; padding: 14px 36px; border-radius: 8px;
    text-decoration: none; font-weight: 700; font-size: 16px;
    display: inline-block; margin-top: 8px;
  }
  .footer-cta {
    background: linear-gradient(135deg, #042f2e, #059669);
    color: #fff; text-align: center; padding: 64px 24px; margin-top: 48px;
  }
  .footer-cta h2 { font-size: 28px; font-weight: 800; margin-bottom: 12px; }
  .footer-cta p { font-size: 16px; color: #a7f3d0; margin-bottom: 28px; }
  .footer-cta-btn {
    display: inline-block; background: #fff; color: #064e3b;
    padding: 16px 40px; border-radius: 12px; font-size: 16px;
    font-weight: 700; text-decoration: none;
  }
  .related-card-img { background: linear-gradient(135deg, #064e3b, #10b981); }
  .thumbnail { box-shadow: 0 4px 24px rgba(5,150,105,0.15); }
"""

CATEGORY_CSS = {
    "ai-trend": CSS_AI_TREND,
    "thought-leadership": CSS_THOUGHT_LEADERSHIP,
    "case-study": CSS_CASE_STUDY,
    "company-news": CSS_THOUGHT_LEADERSHIP,  # 기본 폴백
}


def build_blog_html(meta, body_html, headings, thumbnail_html=""):
    title = meta.get("title", "제목 없음")
    category = meta.get("category", "ai-trend")
    cat_label = CATEGORY_LABELS.get(category, category)
    created = meta.get("created_at", "2026-03-25")
    meta_desc = meta.get("meta_description", "")
    cat_css = CATEGORY_CSS.get(category, CSS_THOUGHT_LEADERSHIP)

    toc_items = ""
    for h in headings:
        toc_items += f'<a href="#{h["anchor"]}" class="toc-item">{h["title"]}</a>\n'

    return f"""<!DOCTYPE html>
<html lang="ko">
<head>
<meta charset="utf-8" />
<meta name="viewport" content="width=device-width, initial-scale=1.0" />
<meta name="description" content="{meta_desc}" />
<title>{title} | 매직에꼴 AX 인사이트</title>
<style>
{BASE_CSS}
{cat_css}
</style>
</head>
<body>

<header class="header">
  <div class="header-left">
    <a href="#" class="header-logo"><span>magic</span>ecole</a>
    <span class="header-nav">AX 인사이트</span>
  </div>
  <a href="https://ax-inquiry-system.vercel.app/inquiry" class="header-cta">AX 교육 문의하기 &rarr;</a>
</header>

<div class="layout">
  <nav class="toc">
    <div class="toc-label">CONTENTS</div>
    {toc_items}
  </nav>

  <main class="main-content">
    <div class="hero-banner">
      <span class="category-badge">{cat_label}</span>
      <h1 class="post-title">{title}</h1>
      <div class="post-meta">
        <div class="author-avatar">M</div>
        <div>
          <span class="author-name">매직에꼴</span>
          <span style="margin: 0 6px; opacity: 0.4;">|</span>
          <span>{created}</span>
        </div>
      </div>
    </div>
    {thumbnail_html}
    <article>
      {body_html}
    </article>
  </main>

  <aside class="sidebar-right">
    <div class="sidebar-label">이런 글은 어때요?</div>
    <div class="related-card">
      <div class="related-card-img">관련 글 썸네일</div>
      <div class="related-card-title">AI 도입했는데 달라진 게 없다면, 문제는 AI가 아닙니다</div>
    </div>
    <div class="related-card">
      <div class="related-card-img">관련 글 썸네일</div>
      <div class="related-card-title">제조 R&amp;D 기술 문서 분석, 3일에서 4시간으로</div>
    </div>
  </aside>
</div>

<section class="footer-cta">
  <h2>우리 기업에 맞는 AX 교육이 궁금하신가요?</h2>
  <p>3분 무료 진단으로 최적의 AX 교육 솔루션을 추천해 드립니다.</p>
  <a href="https://ax-inquiry-system.vercel.app/inquiry" class="footer-cta-btn">무료 AX 진단 받기 &rarr;</a>
</section>

<div class="bottom-nav">
  <a href="#">&larr; 블로그 목록으로</a>
  <a href="#">교육 문의하기</a>
</div>

</body>
</html>"""


def main():
    parser = argparse.ArgumentParser(description="블로그 디자인 프리뷰 생성")
    parser.add_argument("post_path", help="post.md 파일 경로")
    args = parser.parse_args()

    if not os.path.exists(args.post_path):
        print(f"[오류] 파일을 찾을 수 없습니다: {args.post_path}")
        sys.exit(1)

    meta, body = parse_post_md(args.post_path)

    title = meta.get("title", "")
    if not title:
        h1_match = re.match(r"^# (.+)$", body, re.MULTILINE)
        if h1_match:
            title = h1_match.group(1).strip()
    if not title:
        title = "제목 없음"
    meta["title"] = title

    post_dir = os.path.dirname(os.path.abspath(args.post_path))
    category = meta.get("category", "ai-trend")

    thumbnail_html = ""
    thumbnail_path = meta.get("thumbnail", "")
    if thumbnail_path:
        thumb_full = os.path.join(post_dir, thumbnail_path)
        if os.path.exists(thumb_full):
            mime_type = mimetypes.guess_type(thumb_full)[0] or "image/png"
            with open(thumb_full, "rb") as f:
                encoded = base64.b64encode(f.read()).decode("ascii")
            thumbnail_html = f'<img class="thumbnail" src="data:{mime_type};base64,{encoded}" alt="{title}" />'

    headings = extract_headings(body)
    body_html = md_to_html(body, category)
    body_html = embed_local_images(body_html, post_dir)

    html = build_blog_html(meta, body_html, headings, thumbnail_html)

    output_path = os.path.splitext(args.post_path)[0] + "_preview.html"
    with open(output_path, "w", encoding="utf-8") as f:
        f.write(html)

    print(f"[블로그 프리뷰]")
    print(f"  제목: {title}")
    print(f"  카테고리: {cat_label} ({category})" if (cat_label := CATEGORY_LABELS.get(category)) else f"  카테고리: {category}")
    print(f"  TOC: {len(headings)}개")
    print(f"  프리뷰: {output_path}")


if __name__ == "__main__":
    main()
