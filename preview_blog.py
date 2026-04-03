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
from datetime import datetime

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
        m = re.match(r"^(##|###) (.+)$", line)
        if m:
            level = 2 if m.group(1) == "##" else 3
            title = m.group(2).strip()
            anchor = re.sub(r"[^\w가-힣\s-]", "", title)
            anchor = re.sub(r"\s+", "-", anchor).strip("-").lower()
            headings.append({"title": title, "anchor": anchor, "level": level})
    return headings


def summarize_heading_for_toc(title):
    short_title = title.strip()
    for sep in (" — ", " - ", ": ", "： "):
        if sep in short_title:
            short_title = short_title.split(sep, 1)[0].strip()
            break
    question_idx = short_title.find("?")
    if question_idx != -1 and question_idx < len(short_title) - 1:
        short_title = short_title[: question_idx + 1].strip()
    return short_title


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
        action_keywords = ("교훈",)
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
                    is_action = any(k in joined for k in action_keywords)
                    if is_action:
                        result.append(f'<blockquote class="action-point">{content}</blockquote>')
                    else:
                        result.append(f"<blockquote>{content}</blockquote>")
                    in_quote = False
                    quote_lines = []
                result.append(line)
        if in_quote:
            content = "<br>".join(quote_lines)
            joined = " ".join(quote_lines)
            is_action = any(k in joined for k in action_keywords)
            if is_action:
                result.append(f'<blockquote class="action-point">{content}</blockquote>')
            else:
                result.append(f"<blockquote>{content}</blockquote>")
        return "\n".join(result)

    html = convert_blockquotes(html)

    def convert_cta_blocks(text):
        def replace_cta(match):
            inner = match.group(1)
            if "<a " not in inner:
                return match.group(0)

            parts = [part.strip() for part in inner.split("<br>") if part.strip()]
            title_html = ""
            copy_lines = []
            link_lines = []
            for part in parts:
                if "<a " in part:
                    link_lines.append(part)
                elif not title_html:
                    title_html = part if "<strong>" in part else f"<strong>{part}</strong>"
                else:
                    copy_lines.append(part)

            if not title_html or not link_lines:
                return match.group(0)

            cta_parts = [title_html]
            cta_parts.extend(f'<p class="cta-copy">{line}</p>' for line in copy_lines)
            cta_parts.extend(link_lines)
            return f'<div class="cta-block">{"".join(cta_parts)}</div>'

        return re.sub(r"<blockquote>(.*?)</blockquote>", replace_cta, text, flags=re.DOTALL)

    html = convert_cta_blocks(html)

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

    return html


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

CATEGORY_ALIASES = {
    "AI Trend": "ai-trend",
    "Thought Leadership": "thought-leadership",
    "Case Study": "case-study",
    "Company News": "company-news",
    "ai trend": "ai-trend",
    "thought leadership": "thought-leadership",
    "case study": "case-study",
    "company news": "company-news",
}


def normalize_category(category):
    if not category:
        return "thought-leadership"
    raw = str(category).strip()
    if raw in CATEGORY_LABELS:
        return raw
    return CATEGORY_ALIASES.get(raw, CATEGORY_ALIASES.get(raw.lower(), raw))


CURRENT_SITE_THEMES = {
    "ai-trend": {
        "accent": "#7c3aed",
        "chip_bg": "#ede9fe",
        "chip_text": "#6d28d9",
        "avatar_start": "#7c3aed",
        "avatar_end": "#a78bfa",
        "blockquote_border": "#8b5cf6",
        "blockquote_bg": "#f5f3ff",
        "cta_start": "#1e1b4b",
        "cta_end": "#7c3aed",
        "cta_copy": "#ddd6fe",
        "button_text": "#4c1d95",
        "shadow_rgb": "124, 58, 237",
    },
    "thought-leadership": {
        "accent": "#2563eb",
        "chip_bg": "#dbeafe",
        "chip_text": "#1d4ed8",
        "avatar_start": "#1e40af",
        "avatar_end": "#60a5fa",
        "blockquote_border": "#60a5fa",
        "blockquote_bg": "#eff6ff",
        "cta_start": "#1e3a5f",
        "cta_end": "#2563eb",
        "cta_copy": "#dbeafe",
        "button_text": "#1e3a5f",
        "shadow_rgb": "37, 99, 235",
    },
    "case-study": {
        "accent": "#059669",
        "chip_bg": "#d1fae5",
        "chip_text": "#047857",
        "avatar_start": "#059669",
        "avatar_end": "#34d399",
        "blockquote_border": "#34d399",
        "blockquote_bg": "#ecfdf5",
        "cta_start": "#064e3b",
        "cta_end": "#059669",
        "cta_copy": "#d1fae5",
        "button_text": "#064e3b",
        "shadow_rgb": "5, 150, 105",
    },
    "company-news": {
        "accent": "#ea580c",
        "chip_bg": "#ffedd5",
        "chip_text": "#c2410c",
        "avatar_start": "#ea580c",
        "avatar_end": "#fb923c",
        "blockquote_border": "#fb923c",
        "blockquote_bg": "#fff7ed",
        "cta_start": "#7c2d12",
        "cta_end": "#ea580c",
        "cta_copy": "#fed7aa",
        "button_text": "#7c2d12",
        "shadow_rgb": "234, 88, 12",
    },
}


def build_site_css(category):
    theme = CURRENT_SITE_THEMES.get(normalize_category(category), CURRENT_SITE_THEMES["thought-leadership"])
    theme_vars = f"""
  :root {{
    --theme-accent: {theme["accent"]};
    --theme-chip-bg: {theme["chip_bg"]};
    --theme-chip-text: {theme["chip_text"]};
    --theme-avatar-start: {theme["avatar_start"]};
    --theme-avatar-end: {theme["avatar_end"]};
    --theme-blockquote-border: {theme["blockquote_border"]};
    --theme-blockquote-bg: {theme["blockquote_bg"]};
    --theme-cta-start: {theme["cta_start"]};
    --theme-cta-end: {theme["cta_end"]};
    --theme-cta-copy: {theme["cta_copy"]};
    --theme-button-text: {theme["button_text"]};
    --theme-shadow-rgb: {theme["shadow_rgb"]};
  }}
"""
    return theme_vars + SITE_CSS

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


SITE_CSS = """
  @import url('https://rsms.me/inter/inter.css');
  @import url('https://cdn.jsdelivr.net/gh/orioncactus/pretendard/dist/web/static/pretendard.css');
  * { margin: 0; padding: 0; box-sizing: border-box; }
  html { scroll-behavior: smooth; }
  body {
    font-family: Inter, 'Pretendard', -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif;
    background: #ffffff;
    color: #111827;
    -webkit-font-smoothing: antialiased;
    text-rendering: optimizeLegibility;
  }
  a { color: inherit; text-decoration: none; }
  .page { min-height: 100vh; background: #fff; }
  .site-header {
    position: fixed; top: 0; left: 0; right: 0; z-index: 50;
    background: rgba(255,255,255,0.9);
    backdrop-filter: blur(10px);
    border-bottom: 1px solid #f3f4f6;
  }
  .header-inner {
    max-width: 1152px; margin: 0 auto; padding: 0 24px; height: 56px;
    display: flex; align-items: center; justify-content: space-between;
  }
  .header-left { display: flex; align-items: center; gap: 20px; }
  .logo-link img { height: 28px; width: auto; display: block; }
  .divider { color: #e5e7eb; display: none; }
  .nav-links { display: none; align-items: center; gap: 20px; }
  .nav-links a {
    font-size: 14px; color: #6b7280; transition: color 0.2s ease;
  }
  .nav-links a:hover { color: #111827; }
  .header-cta {
    display: inline-flex; align-items: center; gap: 6px;
    background: #0f172a; color: #fff; padding: 10px 16px;
    border-radius: 12px; font-size: 14px; font-weight: 600;
    transition: background 0.2s ease;
  }
  .header-cta:hover { background: #334155; }
  .main-shell { padding-top: 80px; }
  .post-head {
    max-width: 896px; margin: 0 auto; padding: 0 24px 32px;
  }
  .chip-row {
    display: flex; align-items: center; gap: 8px; flex-wrap: wrap;
    margin-bottom: 20px;
  }
  .category-chip {
    background: var(--theme-chip-bg); color: var(--theme-chip-text);
    font-size: 12px; font-weight: 700;
    padding: 6px 12px; border-radius: 9999px;
  }
  .tag-chip {
    font-size: 12px; color: #9ca3af; background: #f3f4f6;
    padding: 5px 10px; border-radius: 9999px;
  }
  .post-title {
    font-size: 36px; line-height: 1.2; letter-spacing: -0.03em;
    font-weight: 800; color: #111827; margin-bottom: 20px;
  }
  .post-subtitle {
    font-size: 18px; line-height: 1.75; color: #6b7280; margin-bottom: 24px;
  }
  .post-meta {
    display: flex; align-items: center; gap: 12px;
    color: #9ca3af; font-size: 14px; padding-bottom: 32px;
    border-bottom: 1px solid #f3f4f6;
    flex-wrap: wrap;
  }
  .author-avatar {
    width: 32px; height: 32px; border-radius: 9999px;
    display: inline-flex; align-items: center; justify-content: center;
    background: linear-gradient(135deg, var(--theme-avatar-start), var(--theme-avatar-end)); color: #fff; font-size: 12px; font-weight: 700;
  }
  .author-name { color: #374151; font-weight: 600; }
  .hero-shell, .content-shell, .casebook-shell { max-width: 896px; margin: 0 auto; padding: 0 24px; }
  .hero-shell { margin-bottom: 40px; }
  .hero-media {
    border-radius: 24px; overflow: hidden; aspect-ratio: 16 / 7; background: #111827;
  }
  .hero-media img, .hero-media .thumbnail { width: 100%; height: 100%; object-fit: cover; display: block; margin: 0; border-radius: 0; box-shadow: none; }
  .content-shell { padding-bottom: 80px; }
  .contents-card {
    margin-bottom: 36px; background: #f9fafb; border: 1px solid #e5e7eb;
    border-radius: 24px; padding: 22px 24px;
  }
  .contents-title {
    font-size: 11px; font-weight: 800; color: #9ca3af;
    letter-spacing: 0.14em; text-transform: uppercase; margin-bottom: 14px;
  }
  .contents-nav { display: flex; flex-direction: column; gap: 2px; }
  .contents-link {
    font-size: 15px; line-height: 1.5; color: #6b7280; padding: 6px 0; transition: color 0.2s ease;
  }
  .contents-link:hover, .contents-link.active { color: var(--theme-accent); font-weight: 600; }
  .blog-prose { max-width: none; }
  .blog-prose h2 {
    font-size: 30px; line-height: 1.25; font-weight: 800; color: #111827;
    margin-top: 56px; margin-bottom: 20px; letter-spacing: -0.02em;
  }
  .blog-prose h3 {
    font-size: 22px; line-height: 1.35; font-weight: 700; color: #1f2937;
    margin-top: 36px; margin-bottom: 16px;
  }
  .blog-prose h4 {
    font-size: 18px; line-height: 1.45; font-weight: 700; color: #374151;
    margin-top: 28px; margin-bottom: 12px;
  }
  .blog-prose p, .blog-prose li {
    font-size: 17px; line-height: 1.85; color: #374151;
  }
  .blog-prose p { margin-bottom: 20px; }
  .blog-prose ul, .blog-prose ol { margin: 20px 0 28px; padding-left: 24px; }
  .blog-prose li { margin-bottom: 10px; }
  .blog-prose strong { color: #111827; }
  .blog-prose em { font-style: italic; }
  .blog-prose a { color: var(--theme-accent); }
  .blog-prose a:hover { text-decoration: underline; }
  .blog-prose hr { border: none; border-top: 1px solid #e5e7eb; margin: 40px 0; }
  .blog-prose blockquote {
    border-left: 4px solid var(--theme-blockquote-border);
    background: var(--theme-blockquote-bg);
    border-radius: 0 16px 16px 0;
    padding: 24px 28px;
    margin: 32px 0;
  }
  .blog-prose blockquote p:last-child { margin-bottom: 0; }
  .blog-prose .cta-block {
    background: linear-gradient(135deg, var(--theme-cta-start) 0%, var(--theme-cta-end) 100%);
    color: #fff; border-radius: 24px; padding: 56px 28px 60px; margin: 48px 0 32px;
    display: flex; flex-direction: column; align-items: center; justify-content: center; gap: 28px;
    text-align: center; box-shadow: 0 24px 48px rgba(var(--theme-shadow-rgb), 0.18);
  }
  .blog-prose .cta-block strong {
    color: #fff; display: block; font-size: 22px; line-height: 1.35; letter-spacing: -0.02em;
  }
  .blog-prose .cta-block .cta-copy {
    margin: -8px 0 0; max-width: 560px; color: var(--theme-cta-copy); font-size: 16px;
  }
  .blog-prose .cta-block a {
    display: inline-flex; align-items: center; justify-content: center; min-width: 280px;
    background: #fff; color: var(--theme-button-text); padding: 20px 32px; border-radius: 16px; font-weight: 800;
    font-size: 16px; box-shadow: 0 12px 28px rgba(15, 23, 42, 0.16); transition: transform 0.2s ease;
  }
  .blog-prose .cta-block a:hover { text-decoration: none; transform: translateY(-1px); }
  .blog-prose code {
    background: #eef2ff; color: #4338ca; border-radius: 8px;
    padding: 2px 7px; font-size: 14px;
  }
  .blog-prose pre {
    background: #111827; color: #f9fafb; border-radius: 20px;
    padding: 24px; overflow-x: auto; margin: 28px 0;
  }
  .blog-prose pre code { background: transparent; color: inherit; padding: 0; }
  .blog-prose .post-image { margin: 36px 0; }
  .blog-prose .post-image img {
    width: 100%; border-radius: 24px; box-shadow: 0 8px 30px rgba(15, 23, 42, 0.08);
    display: block;
  }
  .blog-prose .post-image figcaption {
    text-align: center; font-size: 13px; color: #9ca3af; margin-top: 10px;
  }
  .blog-prose .table-wrap {
    overflow-x: auto; overflow-y: hidden; -webkit-overflow-scrolling: touch;
    border-radius: 16px; margin: 28px 0;
    box-shadow: 0 2px 12px rgba(0,0,0,0.08);
  }
  .blog-prose table { width: 100%; border-collapse: collapse; min-width: 640px; }
  .blog-prose th {
    text-align: left; font-size: 14px; font-weight: 700; color: #fff;
    padding: 14px 20px; white-space: nowrap; letter-spacing: 0.2px;
    background: linear-gradient(135deg, #1e293b 0%, #334155 100%);
  }
  .blog-prose td {
    font-size: 14.5px; line-height: 1.7; color: #374151;
    padding: 13px 20px; border-bottom: 1px solid #e5e7eb; vertical-align: top;
    word-break: keep-all;
  }
  .blog-prose tbody tr:nth-child(even) td { background: #f8fafc; }
  .blog-prose tbody tr:last-child td { border-bottom: none; }
  .related-shell {
    margin-top: 64px; padding-top: 40px; border-top: 1px solid #f3f4f6;
  }
  .related-title {
    font-size: 11px; font-weight: 800; color: #9ca3af;
    letter-spacing: 0.14em; text-transform: uppercase; margin-bottom: 20px;
  }
  .related-grid {
    display: grid; grid-template-columns: repeat(3, minmax(0, 1fr)); gap: 20px;
  }
  .related-card { display: block; }
  .related-thumb {
    border-radius: 16px; overflow: hidden; background: #f3f4f6;
    aspect-ratio: 16 / 9; margin-bottom: 10px;
  }
  .related-thumb img { width: 100%; height: 100%; object-fit: cover; display: block; }
  .related-fallback {
    width: 100%; height: 100%; display: flex; align-items: center; justify-content: center;
    font-size: 28px; opacity: 0.2;
  }
  .related-card p {
    font-size: 14px; line-height: 1.45; font-weight: 700; color: #374151;
    transition: color 0.2s ease;
  }
  .related-card:hover p { color: var(--theme-accent); }
  .casebook-shell { padding-bottom: 40px; }
  .casebook-card {
    cursor: pointer; border-radius: 24px; padding: 32px;
    display: flex; flex-direction: row; justify-content: space-between; align-items: center; gap: 24px;
    background: linear-gradient(135deg, var(--theme-cta-start), var(--theme-cta-end));
    transition: transform 0.2s ease, box-shadow 0.2s ease;
  }
  .casebook-card:hover { transform: translateY(-2px); box-shadow: 0 18px 40px rgba(var(--theme-shadow-rgb), 0.18); }
  .casebook-eyebrow { color: var(--theme-cta-copy); font-size: 14px; font-weight: 500; margin-bottom: 4px; }
  .casebook-card h3 { color: #fff; font-size: 24px; font-weight: 800; margin-bottom: 10px; }
  .casebook-card p { color: var(--theme-cta-copy); font-size: 14px; line-height: 1.7; }
  .casebook-button {
    flex-shrink: 0; background: #fff; color: var(--theme-button-text); font-weight: 800;
    padding: 14px 24px; border-radius: 16px; font-size: 14px; white-space: nowrap;
  }
  .bottom-cta {
    background: linear-gradient(135deg, var(--theme-cta-start), var(--theme-cta-end)); margin-top: 8px;
  }
  .bottom-cta-inner {
    max-width: 1152px; margin: 0 auto; padding: 64px 24px; text-align: center;
  }
  .bottom-cta h2 { color: #fff; font-size: 30px; font-weight: 800; margin-bottom: 14px; }
  .bottom-cta p { color: var(--theme-cta-copy); margin-bottom: 28px; font-size: 16px; }
  .bottom-cta a {
    display: inline-flex; align-items: center; gap: 8px; background: #fff; color: var(--theme-button-text);
    padding: 16px 28px; border-radius: 9999px; font-weight: 800;
    box-shadow: 0 12px 30px rgba(15, 23, 42, 0.14);
  }
  .site-footer {
    background: #fff; color: #6b7280; border-top: 1px solid #e5e7eb;
  }
  .footer-inner { max-width: 1152px; margin: 0 auto; padding: 40px 24px 32px; }
  .footer-top {
    display: flex; flex-direction: column; align-items: flex-start; justify-content: space-between;
    gap: 24px; padding-bottom: 32px; border-bottom: 1px solid #e5e7eb;
  }
  .footer-nav { display: flex; flex-wrap: wrap; gap: 18px; font-size: 14px; }
  .footer-nav a:hover { color: var(--theme-accent); }
  .footer-body { padding: 24px 0; border-bottom: 1px solid #e5e7eb; }
  .footer-body p { font-size: 14px; color: #374151; font-weight: 700; margin-bottom: 12px; }
  .footer-row {
    display: flex; flex-wrap: wrap; gap: 12px 24px; font-size: 12px; line-height: 1.7;
    color: #6b7280; margin-bottom: 6px;
  }
  .footer-bottom {
    padding-top: 24px; display: flex; flex-direction: column; align-items: flex-start;
    gap: 12px; font-size: 12px; color: #9ca3af;
  }
  @media (min-width: 640px) {
    .divider, .nav-links { display: flex; }
    .footer-top { flex-direction: row; align-items: center; }
    .footer-bottom { flex-direction: row; align-items: center; justify-content: space-between; }
  }
  @media (max-width: 767px) {
    .post-title { font-size: 30px; }
    .post-subtitle { font-size: 17px; }
    .blog-prose h2 { font-size: 26px; }
    .blog-prose h3 { font-size: 20px; }
    .blog-prose .cta-block { padding: 40px 20px 44px; gap: 22px; border-radius: 20px; }
    .blog-prose .cta-block strong { font-size: 20px; }
    .blog-prose .cta-block a { width: 100%; min-width: 0; padding: 18px 20px; }
    .related-grid { grid-template-columns: 1fr; }
    .casebook-card { flex-direction: column; align-items: flex-start; }
    .header-cta { padding: 9px 12px; font-size: 13px; }
  }
"""


def title_to_slug(title):
    slug = re.sub(r"[^\w\s가-힣-]", "", title)
    slug = re.sub(r"\s+", "-", slug.strip())
    return slug.lower()


def calculate_reading_time(body):
    char_count = len(re.sub(r"\s+", "", body))
    return max(1, round(char_count / 500))


def format_created_date(created_at):
    raw = (created_at or "").strip()
    for fmt in ("%Y-%m-%d", "%Y-%m-%d %H:%M", "%Y-%m-%d %H:%M:%S"):
        try:
            dt = datetime.strptime(raw, fmt)
            return f"{dt.year}년 {dt.month}월 {dt.day}일"
        except ValueError:
            continue
    return raw or "날짜 미정"


def get_target_keywords(meta):
    keywords = meta.get("target_keywords", [])
    if isinstance(keywords, list):
        return keywords
    if isinstance(keywords, str):
        parts = [p.strip() for p in keywords.split(",")]
        return [p for p in parts if p]
    return []


def file_to_data_uri(file_path):
    if not file_path or not os.path.exists(file_path):
        return ""
    mime_type = mimetypes.guess_type(file_path)[0] or "image/png"
    with open(file_path, "rb") as f:
        encoded = base64.b64encode(f.read()).decode("ascii")
    return f"data:{mime_type};base64,{encoded}"


def load_related_posts(project_root, current_post_id, limit=3):
    posts_dir = os.path.join(project_root, "output", "posts")
    if not os.path.isdir(posts_dir):
        return []

    related = []
    for entry in sorted(os.listdir(posts_dir), reverse=True):
        post_dir = os.path.join(posts_dir, entry)
        post_md = os.path.join(post_dir, "post.md")
        if not os.path.isdir(post_dir) or not os.path.exists(post_md):
            continue
        meta, _ = parse_post_md(post_md)
        if meta.get("post_id") == current_post_id:
            continue
        title = meta.get("title", "").strip('"').strip("'")
        if not title:
            continue
        thumb_rel = meta.get("thumbnail", "")
        thumb_path = os.path.join(post_dir, thumb_rel) if thumb_rel else ""
        related.append({
            "title": title,
            "slug": title_to_slug(title),
            "thumbnail_data_uri": file_to_data_uri(thumb_path),
        })
        if len(related) >= limit:
            break
    return related


def build_blog_html(meta, body_html, headings, reading_time, related_posts, thumbnail_html=""):
    title = meta.get("title", "제목 없음")
    category = normalize_category(meta.get("category", "ai-trend"))
    cat_label = CATEGORY_LABELS.get(category, category)
    created = format_created_date(meta.get("created_at", ""))
    meta_desc = meta.get("meta_description", "")
    subtitle = meta_desc or ""
    author = meta.get("author", "매직에꼴").strip('"').strip("'") or "매직에꼴"
    tags = get_target_keywords(meta)

    tag_items = "".join(f'<span class="tag-chip">#{tag}</span>' for tag in tags)
    primary_headings = [h for h in headings if h.get("level") == 2]
    toc_items = "".join(
        f'<a href="#{h["anchor"]}" class="contents-link">{summarize_heading_for_toc(h["title"])}</a>'
        for h in primary_headings
    )

    related_html = ""
    if related_posts:
        cards = []
        for post in related_posts:
            thumb = (
                f'<img src="{post["thumbnail_data_uri"]}" alt="{post["title"]}" />'
                if post["thumbnail_data_uri"]
                else '<div class="related-fallback">📄</div>'
            )
            cards.append(
                f'''<a class="related-card" href="https://magicecole.vercel.app/blog/{post["slug"]}">
  <div class="related-thumb">{thumb}</div>
  <p>{post["title"]}</p>
</a>'''
            )
        related_html = f'''
<div class="related-shell">
  <p class="related-title">이런 글은 어때요?</p>
  <div class="related-grid">
    {"".join(cards)}
  </div>
</div>'''

    contents_html = ""
    if toc_items:
        contents_html = f'''
<div class="contents-card">
  <p class="contents-title">Contents</p>
  <nav class="contents-nav">
    {toc_items}
  </nav>
</div>'''

    return f"""<!DOCTYPE html>
<html lang="ko">
<head>
<meta charset="utf-8" />
<meta name="viewport" content="width=device-width, initial-scale=1.0" />
<meta name="description" content="{meta_desc}" />
<title>{title} | 매직에꼴 AX 인사이트</title>
<style>
{build_site_css(category)}
</style>
</head>
<body>
<div class="page">
  <header class="site-header">
    <div class="header-inner">
      <div class="header-left">
        <a target="_blank" rel="noopener noreferrer" class="logo-link" href="https://magicecole.com/">
          <img src="https://magicecole.vercel.app/logo.png" alt="매직에꼴" />
        </a>
        <span class="divider">|</span>
        <nav class="nav-links">
          <a href="https://magicecole.vercel.app/products">제품 소개</a>
          <a href="https://magicecole.vercel.app/blog">블로그</a>
          <a href="https://magicecole.vercel.app/ax-diagnosis">AI 활용 진단</a>
          <a href="https://magicecole.vercel.app/inquiry">AX 문의</a>
        </nav>
      </div>
      <a class="header-cta" href="https://magicecole.vercel.app/inquiry">AX 도입 상담받기</a>
    </div>
  </header>

  <main class="main-shell">
    <section class="post-head">
      <div class="chip-row">
        <span class="category-chip">{cat_label}</span>
        {tag_items}
      </div>
      <h1 class="post-title">{title}</h1>
      {f'<p class="post-subtitle">{subtitle}</p>' if subtitle else ''}
      <div class="post-meta">
        <div class="author-avatar">M</div>
        <span class="author-name">{author}</span>
        <span>·</span>
        <span>{created}</span>
        <span>·</span>
        <span>{reading_time}분 읽기</span>
      </div>
    </section>

    {f'<section class="hero-shell"><div class="hero-media">{thumbnail_html}</div></section>' if thumbnail_html else ''}

    <section class="content-shell">
      {contents_html}
      <article class="blog-prose" id="article-content">
        {body_html}
      </article>
      {related_html}
    </section>

    <section class="casebook-shell">
      <div class="casebook-card">
        <div>
          <p class="casebook-eyebrow">무료 자료</p>
          <h3>고객사 AX 사례집 받아보기</h3>
          <p>국내 기업들이 AI 전환을 어떻게 했는지,<br />실제 사례를 정리했습니다.</p>
        </div>
        <a class="casebook-button" href="https://magicecole.vercel.app/inquiry">사례집 받기 →</a>
      </div>
    </section>
  </main>

  <section class="bottom-cta">
    <div class="bottom-cta-inner">
      <h2>우리 기업에 맞는 AX 솔루션이 궁금하신가요?</h2>
      <p>3분 무료 진단으로 최적의 AX 솔루션을 제안드립니다.</p>
      <a href="https://magicecole.vercel.app/inquiry">무료 진단 시작하기 →</a>
    </div>
  </section>

  <footer class="site-footer">
    <div class="footer-inner">
      <div class="footer-top">
        <a target="_blank" rel="noopener noreferrer" class="logo-link" href="https://magicecole.com/">
          <img src="https://magicecole.vercel.app/logo.png" alt="매직에꼴" />
        </a>
        <div class="footer-nav">
          <a href="https://magicecole.vercel.app/blog">블로그</a>
          <a href="https://magicecole.vercel.app/products">제품 소개</a>
          <a href="https://magicecole.vercel.app/ax-diagnosis">AX 진단</a>
          <a href="https://magicecole.vercel.app/inquiry">AX 문의하기</a>
          <a href="https://pf.kakao.com/_Vxifhn">카카오톡 채널</a>
        </div>
      </div>
      <div class="footer-body">
        <p>(주)매직에꼴</p>
        <div class="footer-row">
          <span>대표 최재규</span>
          <span>사업자등록번호 309-87-02279</span>
          <span>통신판매신고번호 제 2021-서울성동-01825호</span>
        </div>
        <div class="footer-row">
          <span>📍 본점 서울 성동구 성수일로 10길 26, 하우스디센종타워 1505호</span>
          <span>📍 지점 경기도 성남시 분당구 서현로210길 4층</span>
        </div>
        <div class="footer-row">
          <span>📞 02-6223-9167</span>
          <span>✉️ biz@magicecole.com</span>
          <span>고객센터 카카오톡 채널 · 평일 10:00~18:00 (토·일·공휴일 휴무)</span>
        </div>
      </div>
      <div class="footer-bottom">
        <p>Copyright © magicecole Corp. All Rights Reserved.</p>
      </div>
    </div>
  </footer>
</div>
<script>
  const links = Array.from(document.querySelectorAll('.contents-link'));
  const headings = Array.from(document.querySelectorAll('#article-content h2'));
  const setActive = (id) => {{
    links.forEach((link) => {{
      link.classList.toggle('active', link.getAttribute('href') === `#${{id}}`);
    }});
  }};
  if (headings.length) {{
    const observer = new IntersectionObserver((entries) => {{
      entries.forEach((entry) => {{
        if (entry.isIntersecting) setActive(entry.target.id);
      }});
    }}, {{ rootMargin: '-20% 0px -70% 0px' }});
    headings.forEach((heading) => observer.observe(heading));
    setActive(headings[0].id);
  }}
</script>
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
    reading_time = calculate_reading_time(body)
    related_posts = load_related_posts(os.getcwd(), meta.get("post_id", ""))
    body_html = md_to_html(body, category)
    body_html = embed_local_images(body_html, post_dir)

    html = build_blog_html(meta, body_html, headings, reading_time, related_posts, thumbnail_html)

    output_path = os.path.splitext(args.post_path)[0] + "_preview.html"
    with open(output_path, "w", encoding="utf-8") as f:
        f.write(html)

    print(f"[블로그 프리뷰]")
    print(f"  제목: {title}")
    print(f"  카테고리: {cat_label} ({category})" if (cat_label := CATEGORY_LABELS.get(category)) else f"  카테고리: {category}")
    primary_headings = [h for h in headings if h.get("level") == 2]
    print(f"  TOC: 핵심 헤더 {len(primary_headings)}개")
    print(f"  프리뷰: {output_path}")


if __name__ == "__main__":
    main()
