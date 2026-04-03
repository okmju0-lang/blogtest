#!/usr/bin/env python3
"""post.md + webp images -> post_preview.html (self-contained)"""
import base64, re, html as H
from pathlib import Path

DIR = Path(__file__).parent
POST = (DIR / "post.md").read_text(encoding="utf-8")

# --- strip frontmatter ---
body = re.sub(r"^---.*?---\s*", "", POST, count=1, flags=re.S)

# --- load images as base64 data URIs ---
img_cache = {}
for img in DIR.glob("images/*.webp"):
    b64 = base64.b64encode(img.read_bytes()).decode()
    img_cache[f"images/{img.name}"] = f"data:image/webp;base64,{b64}"

# --- markdown -> HTML (minimal) ---
lines = body.split("\n")
out = []
in_table = False
in_blockquote = False
table_rows = []
bq_lines = []

def flush_table():
    global in_table, table_rows
    if not table_rows:
        return
    html = '<div class="table-wrap"><table>'
    for i, row in enumerate(table_rows):
        cells = [c.strip() for c in row.strip("|").split("|")]
        if i == 0:
            html += "<thead><tr>" + "".join(f"<th>{c}</th>" for c in cells) + "</tr></thead><tbody>"
        elif i == 1:
            continue  # separator
        else:
            html += "<tr>" + "".join(f"<td>{c}</td>" for c in cells) + "</tr>"
    html += "</tbody></table></div>"
    out.append(html)
    table_rows = []
    in_table = False

def flush_bq():
    global in_blockquote, bq_lines
    if not bq_lines:
        return
    content = "\n".join(bq_lines)
    # Check if it's a CTA block (has a link)
    if "[매직에꼴" in content or "알아보기" in content:
        # CTA block
        lines_inner = content.split("\n")
        strong_text = ""
        link_html = ""
        copy_text = ""
        for l in lines_inner:
            l = l.strip()
            link_match = re.search(r'\[([^\]]+)\]\(([^)]+)\)', l)
            strong_match = re.search(r'\*\*([^*]+)\*\*', l)
            if link_match and strong_match:
                strong_text = strong_match.group(1)
                link_html = f'<a href="{link_match.group(2)}">{link_match.group(1)}</a>'
            elif link_match:
                link_html = f'<a href="{link_match.group(2)}">{link_match.group(1)}</a>'
            elif strong_match:
                strong_text = strong_match.group(1)
            else:
                copy_text += l + " "
        html = '<div class="cta-block">'
        if strong_text:
            html += f"<strong>{H.escape(strong_text)}</strong>"
        if copy_text.strip():
            html += f'<p class="cta-copy">{H.escape(copy_text.strip())}</p>'
        if link_html:
            html += link_html
        html += "</div>"
        out.append(html)
    else:
        # Normal blockquote
        inner = inline(content)
        out.append(f"<blockquote><p>{inner}</p></blockquote>")
    bq_lines = []
    in_blockquote = False

def inline(text):
    """Convert inline markdown to HTML."""
    text = re.sub(r'\*\*([^*]+)\*\*', r'<strong>\1</strong>', text)
    text = re.sub(r'\[([^\]]+)\]\(([^)]+)\)', r'<a href="\2">\1</a>', text)
    text = re.sub(r'`([^`]+)`', r'<code>\1</code>', text)
    return text

for line in lines:
    stripped = line.strip()

    # Table
    if stripped.startswith("|"):
        if in_blockquote:
            flush_bq()
        in_table = True
        table_rows.append(stripped)
        continue
    elif in_table:
        flush_table()

    # Blockquote
    if stripped.startswith("> "):
        if in_table:
            flush_table()
        in_blockquote = True
        bq_lines.append(stripped[2:])
        continue
    elif in_blockquote:
        if stripped == "":
            flush_bq()
        else:
            # continuation
            flush_bq()

    # Empty line
    if stripped == "":
        continue

    # HR
    if stripped == "---":
        out.append("<hr>")
        continue

    # Headings
    if stripped.startswith("# "):
        # skip H1, already in header
        continue
    if stripped.startswith("### "):
        out.append(f"<h3>{inline(stripped[4:])}</h3>")
        continue
    if stripped.startswith("## "):
        out.append(f"<h2>{inline(stripped[3:])}</h2>")
        continue

    # Image
    img_match = re.match(r'!\[([^\]]*)\]\(([^)]+)\)', stripped)
    if img_match:
        alt = img_match.group(1)
        src = img_match.group(2)
        real_src = img_cache.get(src, src)
        out.append(f'<figure class="post-image"><img src="{real_src}" alt="{H.escape(alt)}"><figcaption>{H.escape(alt)}</figcaption></figure>')
        continue

    # Bold-only line (like **참고 자료**)
    if re.match(r'^\*\*[^*]+\*\*$', stripped):
        out.append(f"<p><strong>{stripped[2:-2]}</strong></p>")
        continue

    # List item
    if stripped.startswith("- "):
        out.append(f"<ul><li>{inline(stripped[2:])}</li></ul>")
        continue

    # Regular paragraph
    out.append(f"<p>{inline(stripped)}</p>")

if in_table:
    flush_table()
if in_blockquote:
    flush_bq()

body_html = "\n".join(out)

# --- merge consecutive <ul> ---
body_html = re.sub(r'</ul>\s*<ul>', '', body_html)

TEMPLATE = f'''<!DOCTYPE html>
<html lang="ko">
<head>
<meta charset="utf-8" />
<meta name="viewport" content="width=device-width, initial-scale=1.0" />
<title>"우리 데이터, AI에 쓸 수 있나요?" — 기업 데이터 준비도 자가 진단 가이드 | 매직에꼴 AX 인사이트</title>
<style>
  :root {{
    --theme-accent: #4338ca;
    --theme-chip-bg: #e0e7ff;
    --theme-chip-text: #3730a3;
    --theme-avatar-start: #1e3a5f;
    --theme-avatar-end: #3b82f6;
    --theme-blockquote-border: #c59b2c;
    --theme-blockquote-bg: #fefce8;
    --theme-cta-start: #0f172a;
    --theme-cta-end: #1e3a5f;
    --theme-cta-copy: #bfdbfe;
    --theme-button-text: #1e3a5f;
    --theme-shadow-rgb: 30, 58, 95;
  }}
  @import url('https://rsms.me/inter/inter.css');
  @import url('https://cdn.jsdelivr.net/gh/orioncactus/pretendard/dist/web/static/pretendard.css');
  * {{ margin:0; padding:0; box-sizing:border-box; }}
  html {{ scroll-behavior:smooth; }}
  body {{
    font-family: Inter,'Pretendard',-apple-system,BlinkMacSystemFont,'Segoe UI',sans-serif;
    background:#fff; color:#111827;
    -webkit-font-smoothing:antialiased; text-rendering:optimizeLegibility;
  }}
  a {{ color:inherit; text-decoration:none; }}
  .page {{ min-height:100vh; background:#fff; }}
  .site-header {{
    position:fixed; top:0; left:0; right:0; z-index:50;
    background:rgba(255,255,255,0.9); backdrop-filter:blur(10px);
    border-bottom:1px solid #f3f4f6;
  }}
  .header-inner {{
    max-width:1152px; margin:0 auto; padding:0 24px; height:56px;
    display:flex; align-items:center; justify-content:space-between;
  }}
  .header-left {{ display:flex; align-items:center; gap:20px; }}
  .logo-link img {{ height:28px; width:auto; display:block; }}
  .divider {{ color:#e5e7eb; display:none; }}
  .nav-links {{ display:none; align-items:center; gap:20px; }}
  .nav-links a {{ font-size:14px; color:#6b7280; transition:color 0.2s; }}
  .nav-links a:hover {{ color:#111827; }}
  .header-cta {{
    display:inline-flex; align-items:center; gap:6px;
    background:#0f172a; color:#fff; padding:10px 16px;
    border-radius:12px; font-size:14px; font-weight:600; transition:background 0.2s;
  }}
  .header-cta:hover {{ background:#334155; }}
  .main-shell {{ padding-top:80px; }}
  .post-head {{ max-width:896px; margin:0 auto; padding:0 24px 32px; }}
  .chip-row {{ display:flex; align-items:center; gap:8px; flex-wrap:wrap; margin-bottom:20px; }}
  .category-chip {{
    background:var(--theme-chip-bg); color:var(--theme-chip-text);
    font-size:12px; font-weight:700; padding:6px 12px; border-radius:9999px;
  }}
  .tag-chip {{ font-size:12px; color:#9ca3af; background:#f3f4f6; padding:5px 10px; border-radius:9999px; }}
  .post-title {{
    font-size:36px; line-height:1.2; letter-spacing:-0.03em;
    font-weight:800; color:#111827; margin-bottom:20px;
  }}
  .post-subtitle {{ font-size:18px; line-height:1.75; color:#6b7280; margin-bottom:24px; }}
  .post-meta {{
    display:flex; align-items:center; gap:12px;
    color:#9ca3af; font-size:14px; padding-bottom:32px;
    border-bottom:1px solid #f3f4f6; flex-wrap:wrap;
  }}
  .author-avatar {{
    width:32px; height:32px; border-radius:9999px;
    display:inline-flex; align-items:center; justify-content:center;
    background:linear-gradient(135deg,var(--theme-avatar-start),var(--theme-avatar-end));
    color:#fff; font-size:12px; font-weight:700;
  }}
  .author-name {{ color:#374151; font-weight:600; }}
  .content-shell {{ max-width:896px; margin:0 auto; padding:0 24px 80px; }}
  .blog-prose h2 {{
    font-size:30px; line-height:1.25; font-weight:800; color:#111827;
    margin-top:56px; margin-bottom:20px; letter-spacing:-0.02em;
  }}
  .blog-prose h3 {{
    font-size:22px; line-height:1.35; font-weight:700; color:#1f2937;
    margin-top:36px; margin-bottom:16px;
  }}
  .blog-prose p, .blog-prose li {{ font-size:17px; line-height:1.85; color:#374151; }}
  .blog-prose p {{ margin-bottom:20px; }}
  .blog-prose ul, .blog-prose ol {{ margin:20px 0 28px; padding-left:24px; }}
  .blog-prose li {{ margin-bottom:10px; }}
  .blog-prose strong {{ color:#111827; }}
  .blog-prose a {{ color:var(--theme-accent); }}
  .blog-prose a:hover {{ text-decoration:underline; }}
  .blog-prose hr {{ border:none; border-top:1px solid #e5e7eb; margin:40px 0; }}
  .blog-prose blockquote {{
    border-left:4px solid var(--theme-blockquote-border);
    background:var(--theme-blockquote-bg);
    border-radius:0 16px 16px 0;
    padding:24px 28px; margin:32px 0;
  }}
  .blog-prose blockquote p:last-child {{ margin-bottom:0; }}
  .blog-prose .cta-block {{
    background:linear-gradient(135deg,var(--theme-cta-start) 0%,var(--theme-cta-end) 100%);
    color:#fff; border-radius:24px; padding:56px 28px 60px; margin:48px 0 32px;
    display:flex; flex-direction:column; align-items:center; justify-content:center; gap:28px;
    text-align:center; box-shadow:0 24px 48px rgba(var(--theme-shadow-rgb),0.18);
  }}
  .blog-prose .cta-block strong {{
    color:#fff; display:block; font-size:22px; line-height:1.35; letter-spacing:-0.02em;
  }}
  .blog-prose .cta-block .cta-copy {{
    margin:-8px 0 0; max-width:560px; color:var(--theme-cta-copy); font-size:16px;
  }}
  .blog-prose .cta-block a {{
    display:inline-flex; align-items:center; justify-content:center; min-width:280px;
    background:#fff; color:var(--theme-button-text); padding:20px 32px; border-radius:16px;
    font-weight:800; font-size:16px; box-shadow:0 12px 28px rgba(15,23,42,0.16);
    transition:transform 0.2s;
  }}
  .blog-prose .cta-block a:hover {{ text-decoration:none; transform:translateY(-1px); }}
  .blog-prose .post-image {{ margin:36px 0; }}
  .blog-prose .post-image img {{
    width:100%; border-radius:24px; box-shadow:0 8px 30px rgba(15,23,42,0.08); display:block;
  }}
  .blog-prose .post-image figcaption {{
    text-align:center; font-size:13px; color:#9ca3af; margin-top:10px;
  }}
  .blog-prose .table-wrap {{
    overflow-x:auto; border:1px solid #e5e7eb; border-radius:20px; margin:28px 0;
  }}
  .blog-prose table {{ width:100%; border-collapse:collapse; }}
  .blog-prose th {{
    text-align:left; font-size:14px; font-weight:700; color:#111827;
    padding:16px 18px; background:#f8fafc; border-bottom:1px solid #e5e7eb;
  }}
  .blog-prose td {{
    font-size:15px; line-height:1.7; color:#374151;
    padding:16px 18px; border-bottom:1px solid #eef2f7; vertical-align:top;
  }}
  .blog-prose tbody tr:last-child td {{ border-bottom:none; }}
  .site-footer {{
    background:#fff; color:#6b7280; border-top:1px solid #e5e7eb;
  }}
  .footer-inner {{ max-width:1152px; margin:0 auto; padding:40px 24px 32px; }}
  .footer-top {{
    display:flex; flex-direction:column; align-items:flex-start;
    justify-content:space-between; gap:24px; padding-bottom:32px;
    border-bottom:1px solid #e5e7eb;
  }}
  .footer-nav {{ display:flex; flex-wrap:wrap; gap:18px; font-size:14px; }}
  .footer-nav a:hover {{ color:var(--theme-accent); }}
  .footer-body {{ padding:24px 0; border-bottom:1px solid #e5e7eb; }}
  .footer-body p {{ font-size:14px; color:#374151; font-weight:700; margin-bottom:12px; }}
  .footer-row {{
    display:flex; flex-wrap:wrap; gap:12px 24px; font-size:12px;
    line-height:1.7; color:#6b7280; margin-bottom:6px;
  }}
  .footer-bottom {{
    padding-top:24px; display:flex; flex-direction:column; align-items:flex-start;
    gap:12px; font-size:12px; color:#9ca3af;
  }}
  @media (min-width:640px) {{
    .divider,.nav-links {{ display:flex; }}
    .footer-top {{ flex-direction:row; align-items:center; }}
    .footer-bottom {{ flex-direction:row; align-items:center; justify-content:space-between; }}
  }}
  @media (max-width:767px) {{
    .post-title {{ font-size:30px; }}
    .post-subtitle {{ font-size:17px; }}
    .blog-prose h2 {{ font-size:26px; }}
    .blog-prose h3 {{ font-size:20px; }}
    .blog-prose .cta-block {{ padding:40px 20px 44px; gap:22px; border-radius:20px; }}
    .blog-prose .cta-block strong {{ font-size:20px; }}
    .blog-prose .cta-block a {{ width:100%; min-width:0; padding:18px 20px; }}
  }}
</style>
</head>
<body>
<div class="page">
  <header class="site-header">
    <div class="header-inner">
      <div class="header-left">
        <a class="logo-link" href="https://magicecole.com/" target="_blank">
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
        <span class="category-chip">Thought Leadership</span>
        <span class="tag-chip">#데이터 준비도</span>
        <span class="tag-chip">#AI 도입</span>
        <span class="tag-chip">#데이터 사일로</span>
        <span class="tag-chip">#데이터 거버넌스</span>
        <span class="tag-chip">#AX</span>
      </div>
      <h1 class="post-title">"우리 데이터, AI에 쓸 수 있나요?" — 기업 데이터 준비도 자가 진단 가이드</h1>
      <p class="post-subtitle">AI 프로젝트 95%가 실패하는 진짜 원인은 모델이 아니라 데이터 준비도입니다. 품질·사일로·거버넌스·드리프트 4가지 축으로 우리 회사 데이터를 지금 바로 진단해보세요.</p>
      <div class="post-meta">
        <div class="author-avatar">M</div>
        <span class="author-name">매직에꼴</span>
        <span>·</span>
        <span>2026년 4월 1일</span>
        <span>·</span>
        <span>5분 읽기</span>
      </div>
    </section>

    <section class="content-shell">
      <article class="blog-prose">
{body_html}
      </article>
    </section>
  </main>

  <footer class="site-footer">
    <div class="footer-inner">
      <div class="footer-top">
        <a class="logo-link" href="https://magicecole.com/" target="_blank">
          <img src="https://magicecole.vercel.app/logo.png" alt="매직에꼴" style="height:24px;" />
        </a>
        <nav class="footer-nav">
          <a href="https://magicecole.vercel.app/products">제품 소개</a>
          <a href="https://magicecole.vercel.app/blog">블로그</a>
          <a href="https://magicecole.vercel.app/inquiry">AX 문의</a>
        </nav>
      </div>
      <div class="footer-body">
        <p>주식회사 매직에꼴</p>
        <div class="footer-row">
          <span>대표: 정민영</span>
          <span>사업자등록번호: 506-87-03508</span>
        </div>
        <div class="footer-row">
          <span>서울 영등포구 당산로41길 11 당산 SK V1 center E동 1413호</span>
        </div>
      </div>
      <div class="footer-bottom">
        <span>&copy; 2026 매직에꼴. All rights reserved.</span>
      </div>
    </div>
  </footer>
</div>
</body>
</html>'''

out_path = DIR / "post_preview.html"
out_path.write_text(TEMPLATE, encoding="utf-8")
print(f"Preview saved: {out_path} ({out_path.stat().st_size / 1024:.0f}KB)")
