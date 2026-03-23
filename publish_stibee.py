"""
스티비(Stibee) API를 통한 블로그 포스트 이메일 자동 발송 스크립트

사용법:
    python publish_stibee.py <post.md 파일 경로> [--reserve YYYYMMDDhhmmss]

환경 변수 (.env 파일 또는 시스템 환경 변수):
    STIBEE_API_KEY       — 스티비 API 키 (워크스페이스 설정 > API 키에서 생성)
    STIBEE_LIST_ID       — 발송 대상 주소록 ID
    STIBEE_SENDER_EMAIL  — 발신자 이메일 주소
    STIBEE_SENDER_NAME   — 발신자 이름

스티비 API 흐름:
    1. POST /v2/emails          — 이메일 생성 (제목, 발신자, 주소록 지정)
    2. POST /v2/emails/{id}/content — HTML 콘텐츠 설정
    3. POST /v2/emails/{id}/send    — 즉시 발송
       또는 POST /v2/emails/{id}/reserve?reserveTime=... — 예약 발송
"""

import os
import sys
import io
import json
import argparse
import re
import requests

# Windows 콘솔 인코딩 문제 방지
if sys.stdout.encoding and sys.stdout.encoding.lower() != "utf-8":
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding="utf-8", errors="replace")

BASE_URL = "https://api.stibee.com/v2"


def load_env(env_path=".env"):
    """간단한 .env 파일 로더 (python-dotenv 미설치 환경 대응)"""
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


def md_to_html(md_text):
    """마크다운 텍스트를 기본 HTML로 변환한다."""
    html = md_text

    # 이미지: ![alt](src) → <img>
    html = re.sub(
        r"!\[([^\]]*)\]\(([^)]+)\)",
        r'<img src="\2" alt="\1" style="max-width:100%;height:auto;" />',
        html,
    )

    # 링크: [text](url) → <a>
    html = re.sub(r"\[([^\]]+)\]\(([^)]+)\)", r'<a href="\2">\1</a>', html)

    # 헤딩: ## → <h2>, ### → <h3>
    html = re.sub(r"^#### (.+)$", r"<h4>\1</h4>", html, flags=re.MULTILINE)
    html = re.sub(r"^### (.+)$", r"<h3>\1</h3>", html, flags=re.MULTILINE)
    html = re.sub(r"^## (.+)$", r"<h2>\1</h2>", html, flags=re.MULTILINE)
    html = re.sub(r"^# (.+)$", r"<h1>\1</h1>", html, flags=re.MULTILINE)

    # 굵은 글씨: **text** → <strong>
    html = re.sub(r"\*\*(.+?)\*\*", r"<strong>\1</strong>", html)

    # 기울임: *text* → <em>
    html = re.sub(r"\*(.+?)\*", r"<em>\1</em>", html)

    # 인용 블록: > text → <blockquote> 또는 CTA 블록
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

    # 마크다운 테이블 → HTML <table>
    def convert_tables(text):
        lines = text.split("\n")
        result = []
        i = 0
        while i < len(lines):
            # 테이블 헤더 감지: | col | col | 다음 줄이 |---|---|
            if (i + 1 < len(lines)
                    and "|" in lines[i]
                    and re.match(r"^\|[\s\-:|]+\|$", lines[i + 1].strip())):
                table_lines = [lines[i]]
                i += 2  # 헤더 + 구분선 건너뛰기
                while i < len(lines) and "|" in lines[i] and lines[i].strip().startswith("|"):
                    table_lines.append(lines[i])
                    i += 1
                # 헤더 파싱
                header_cells = [c.strip() for c in table_lines[0].strip().strip("|").split("|")]
                thead = "<tr>" + "".join(f"<th>{c}</th>" for c in header_cells) + "</tr>"
                # 바디 파싱
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

    # 구분선: --- → <hr>
    html = re.sub(r"^---+$", r"<hr />", html, flags=re.MULTILINE)

    # 순서 없는 목록: - item → <li>
    html = re.sub(r"^- (.+)$", r"<li>\1</li>", html, flags=re.MULTILINE)

    # 순서 있는 목록: 1. item → <li>
    html = re.sub(r"^\d+\. (.+)$", r"<li>\1</li>", html, flags=re.MULTILINE)

    # 줄바꿈 → <br> (빈 줄은 <p> 분리)
    paragraphs = re.split(r"\n\n+", html)
    wrapped = []
    for p in paragraphs:
        p = p.strip()
        if not p:
            continue
        # 이미 블록 태그로 시작하면 감싸지 않음
        if re.match(r"<(h[1-6]|li|hr|img|div|table|ul|ol|blockquote)", p):
            wrapped.append(p)
        else:
            wrapped.append(f"<p>{p}</p>")

    html_body = "\n".join(wrapped)

    return f"""<!DOCTYPE html>
<html>
<head>
<meta charset="utf-8" />
<meta name="viewport" content="width=device-width, initial-scale=1.0" />
<style>
  body {{ font-family: 'Pretendard', -apple-system, sans-serif; line-height: 1.8; color: #333; max-width: 680px; margin: 0 auto; padding: 20px; }}
  h1 {{ font-size: 28px; margin-top: 32px; }}
  h2 {{ font-size: 22px; margin-top: 28px; color: #1a1a1a; }}
  h3 {{ font-size: 18px; margin-top: 24px; }}
  p {{ margin: 16px 0; }}
  li {{ margin: 8px 0; }}
  img {{ border-radius: 8px; margin: 16px 0; }}
  a {{ color: #2563eb; }}
  hr {{ border: none; border-top: 1px solid #e5e7eb; margin: 32px 0; }}
  strong {{ color: #111; }}
  blockquote {{ background: linear-gradient(135deg, #f0f4ff 0%, #e8eeff 100%); border-left: 4px solid #2563eb; padding: 24px 28px; margin: 32px 0; border-radius: 0 12px 12px 0; box-shadow: 0 2px 8px rgba(37, 99, 235, 0.08); font-size: 16px; line-height: 1.7; }}
  blockquote strong {{ color: #1e40af; }}
  .table-wrap {{ border-radius: 12px; overflow-x: auto; -webkit-overflow-scrolling: touch; box-shadow: 0 2px 12px rgba(0,0,0,0.08); margin: 24px 0; }}
  table {{ width: 100%; border-collapse: collapse; font-size: 15px; min-width: 320px; }}
  th {{ background: linear-gradient(135deg, #1e293b 0%, #334155 100%); color: #fff; padding: 14px 20px; text-align: left; font-weight: 600; font-size: 14px; letter-spacing: 0.3px; white-space: nowrap; }}
  td {{ padding: 13px 20px; border-bottom: 1px solid #e5e7eb; color: #374151; font-size: 14.5px; word-break: keep-all; }}
  tr:nth-child(even) td {{ background: #f8fafc; }}
  tr:last-child td {{ border-bottom: none; }}
  tr:hover td {{ background: #eef2ff; transition: background 0.15s ease; }}
  .cta-block {{ background: linear-gradient(135deg, #1e3a5f 0%, #2563eb 100%); color: #fff; padding: 32px 36px; margin: 40px 0 24px; border-radius: 16px; text-align: center; font-size: 17px; line-height: 1.7; box-shadow: 0 4px 16px rgba(37, 99, 235, 0.2); }}
  .cta-block strong {{ color: #fff; font-size: 19px; }}
  .cta-block a {{ color: #fff; background: rgba(255,255,255,0.2); padding: 10px 28px; border-radius: 8px; text-decoration: none; font-weight: 600; display: inline-block; margin-top: 12px; transition: background 0.2s ease; }}
  .cta-block a:hover {{ background: rgba(255,255,255,0.35); }}
</style>
</head>
<body>
{html_body}
</body>
</html>"""


def get_headers(api_key):
    return {"AccessToken": api_key}


def create_email(api_key, subject, sender_email, sender_name, list_id,
                 group_ids=None, segment_ids=None):
    """단계 1: 이메일 생성 → 이메일 ID 반환"""
    url = f"{BASE_URL}/emails"
    payload = {
        "subject": subject,
        "senderEmail": sender_email,
        "senderName": sender_name,
        "listId": int(list_id),
    }
    if group_ids:
        payload["groupIds"] = [int(g) for g in group_ids]
    if segment_ids:
        payload["segmentIds"] = [int(s) for s in segment_ids]

    resp = requests.post(url, headers=get_headers(api_key),
                         json=payload, timeout=30)
    if resp.status_code != 200:
        print(f"[실패] 이메일 생성 실패 — HTTP {resp.status_code}")
        print(f"  응답: {resp.text}")
        sys.exit(1)

    data = resp.json()
    email_id = data.get("id")
    if not email_id:
        print(f"[실패] 이메일 ID를 받지 못했습니다. 응답: {data}")
        sys.exit(1)

    return email_id


def set_email_content(api_key, email_id, html_content):
    """단계 2: 이메일 HTML 콘텐츠 설정"""
    url = f"{BASE_URL}/emails/{email_id}/content"
    headers = get_headers(api_key)
    headers["Content-Type"] = "text/html"

    resp = requests.post(url, headers=headers,
                         data=html_content.encode("utf-8"), timeout=30)
    if resp.status_code != 200:
        print(f"[실패] 콘텐츠 설정 실패 — HTTP {resp.status_code}")
        print(f"  응답: {resp.text}")
        sys.exit(1)

    return True


def send_email(api_key, email_id):
    """단계 3a: 즉시 발송"""
    url = f"{BASE_URL}/emails/{email_id}/send"
    resp = requests.post(url, headers=get_headers(api_key), timeout=30)
    if resp.status_code != 200:
        print(f"[실패] 이메일 발송 실패 — HTTP {resp.status_code}")
        print(f"  응답: {resp.text}")
        return False
    return True


def reserve_email(api_key, email_id, reserve_time):
    """단계 3b: 예약 발송 (reserve_time: YYYYMMDDhhmmss, KST 기준)"""
    url = f"{BASE_URL}/emails/{email_id}/reserve"
    params = {"reserveTime": reserve_time}
    resp = requests.post(url, headers=get_headers(api_key),
                         params=params, timeout=30)
    if resp.status_code != 200:
        print(f"[실패] 예약 발송 실패 — HTTP {resp.status_code}")
        print(f"  응답: {resp.text}")
        return False
    return True


def main():
    parser = argparse.ArgumentParser(
        description="스티비 API를 통한 블로그 포스트 이메일 발송"
    )
    parser.add_argument("post_path", help="post.md 파일 경로")
    parser.add_argument(
        "--preview", action="store_true",
        help="발송하지 않고 이메일 내용만 미리보기 (HTML 파일 생성)",
    )
    parser.add_argument(
        "--reserve", metavar="YYYYMMDDhhmmss",
        help="예약 발송 시각 (KST 기준, 예: 20260324090000)",
    )
    parser.add_argument(
        "--group-ids", nargs="*", type=int,
        help="발송 대상 그룹 ID (복수 가능)",
    )
    parser.add_argument(
        "--segment-ids", nargs="*", type=int,
        help="발송 대상 세그먼트 ID (복수 가능)",
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
    title = meta.get("title", "제목 없음")

    # 썸네일 경로 확인 (frontmatter의 thumbnail 필드)
    thumbnail_path = meta.get("thumbnail", "")
    if thumbnail_path:
        post_dir = os.path.dirname(os.path.abspath(args.post_path))
        thumbnail_full = os.path.join(post_dir, thumbnail_path)
        if os.path.exists(thumbnail_full):
            # 본문 최상단(제목 바로 뒤)에 썸네일 삽입
            body = body.split("\n", 1)
            if len(body) == 2:
                body = body[0] + "\n\n" + f"![{title}]({thumbnail_path})" + "\n" + body[1]
            else:
                body = body[0] + "\n\n" + f"![{title}]({thumbnail_path})"

    # 마크다운 → HTML 변환
    html_content = md_to_html(body)

    # 프리뷰 모드: API 키 없이 HTML 파일만 생성
    if args.preview:
        preview_path = os.path.splitext(args.post_path)[0] + "_preview.html"
        with open(preview_path, "w", encoding="utf-8") as f:
            f.write(html_content)
        print(f"[이메일 미리보기]")
        print(f"  제목: {title}")
        print(f"  본문 길이: {len(body)}자 (MD) → {len(html_content)}자 (HTML)")
        print(f"  프리뷰 파일: {preview_path}")
        print(f"\n프리뷰 파일을 브라우저에서 열어 확인한 후,")
        print(f"발송하려면 --preview 없이 다시 실행하세요.")
        sys.exit(0)

    # 필수 환경 변수 확인 (발송 시에만 필요)
    api_key = os.environ.get("STIBEE_API_KEY")
    list_id = os.environ.get("STIBEE_LIST_ID")
    sender_email = os.environ.get("STIBEE_SENDER_EMAIL")
    sender_name = os.environ.get("STIBEE_SENDER_NAME")

    placeholders = {"your_stibee_api_key_here", "your_list_id_here",
                     "your_sender@example.com", "your_sender_name_here", ""}

    missing = []
    if not api_key or api_key in placeholders:
        missing.append("STIBEE_API_KEY")
    if not list_id or list_id in placeholders:
        missing.append("STIBEE_LIST_ID")
    if not sender_email or sender_email in placeholders:
        missing.append("STIBEE_SENDER_EMAIL")
    if not sender_name or sender_name in placeholders:
        missing.append("STIBEE_SENDER_NAME")

    if missing:
        print("[오류] 다음 환경 변수가 설정되지 않았습니다:")
        for m in missing:
            print(f"  - {m}")
        print("\n.env 파일에 추가하거나 시스템 환경 변수로 설정해 주세요.")
        print("(.env.example 파일을 참고하세요)")
        sys.exit(1)

    print(f"[스티비 이메일 발송]")
    print(f"  제목: {title}")
    print(f"  발신자: {sender_name} <{sender_email}>")
    print(f"  주소록 ID: {list_id}")
    print(f"  본문 길이: {len(body)}자 (MD) → {len(html_content)}자 (HTML)")
    if args.reserve:
        print(f"  예약 시각: {args.reserve} (KST)")
    print()

    # 단계 1: 이메일 생성
    print("[1/3] 이메일 생성 중...")
    email_id = create_email(
        api_key, title, sender_email, sender_name, list_id,
        group_ids=args.group_ids, segment_ids=args.segment_ids,
    )
    print(f"  이메일 ID: {email_id}")

    # 단계 2: HTML 콘텐츠 설정
    print("[2/3] 콘텐츠 설정 중...")
    set_email_content(api_key, email_id, html_content)
    print("  콘텐츠 설정 완료")

    # 단계 3: 발송 또는 예약
    if args.reserve:
        print(f"[3/3] 예약 발송 중 ({args.reserve})...")
        success = reserve_email(api_key, email_id, args.reserve)
    else:
        print("[3/3] 즉시 발송 중...")
        success = send_email(api_key, email_id)

    if success:
        mode = "예약" if args.reserve else "즉시"
        print(f"\n[성공] 이메일이 {mode} 발송되었습니다. (ID: {email_id})")
    else:
        sys.exit(1)


if __name__ == "__main__":
    main()
