"""v3: flex.team 레퍼런스 기반 — 텍스트가 주인공, 배경은 보조"""

from PIL import Image, ImageDraw, ImageFont
from pathlib import Path

BASE = Path(__file__).parent
FONT_BOLD = "C:/Windows/Fonts/malgunbd.ttf"
FONT_REG = "C:/Windows/Fonts/malgun.ttf"
W, H = 1280, 720


def solid_bg(w, h, color):
    return Image.new("RGB", (w, h), color)


def add_badge(img, text, pos, bg_rgb, bg_alpha=180, text_color=(255, 255, 255)):
    font = ImageFont.truetype(FONT_REG, 20)
    bbox = font.getbbox(text)
    tw, th = bbox[2] - bbox[0], bbox[3] - bbox[1]
    px, py = 16, 9
    bw, bh = tw + px * 2, th + py * 2

    badge = Image.new("RGBA", (bw, bh), (0, 0, 0, 0))
    d = ImageDraw.Draw(badge)
    # 반투명 배경 + 얇은 테두리
    d.rounded_rectangle((0, 0, bw - 1, bh - 1), radius=8,
                        fill=(*bg_rgb, bg_alpha),
                        outline=(*text_color, 80), width=1)
    d.text((px, py - 2), text, fill=text_color, font=font)

    rgba = img.convert("RGBA")
    rgba.paste(badge, pos, badge)
    return rgba.convert("RGB")


def add_logo(draw, pos, color=(255, 255, 255)):
    """로고 placeholder — 추후 PNG로 교체"""
    # 아이콘 + 텍스트 조합
    font = ImageFont.truetype(FONT_BOLD, 22)
    x, y = pos
    # 작은 다이아몬드 마크
    draw.polygon([(x, y + 10), (x + 8, y + 2), (x + 16, y + 10), (x + 8, y + 18)],
                 fill=color)
    draw.text((x + 22, y), "magicecole", fill=color, font=font)


def place_element_blended(bg, element_path, region, opacity=180):
    """그래픽 요소를 반투명으로 배경에 블렌딩"""
    elem = Image.open(element_path).convert("RGBA")
    rx, ry, rw, rh = region
    elem = elem.resize((rw, rh), Image.LANCZOS)

    # 투명도 조절
    alpha = elem.split()[3]
    alpha = alpha.point(lambda p: min(p, opacity))
    elem.putalpha(alpha)

    rgba = bg.convert("RGBA")
    rgba.paste(elem, (rx, ry), elem)
    return rgba.convert("RGB")


# ============================================================
# 1. AI Trend — 보라색 단색 + 우측 추상 그래픽 + 큰 제목
# ============================================================
def make_ai_trend():
    print("  AI Trend...")
    bg = solid_bg(W, H, (75, 45, 160))

    # 우측에 배경 이미지를 반투명 블렌딩 (은은하게)
    bg = place_element_blended(bg, BASE / "v2_bg_ai_trend.png", (500, 0, 780, 720), opacity=200)

    # 뱃지
    bg = add_badge(bg, "Viewpoint", (55, 55), bg_rgb=(255, 255, 255), bg_alpha=35,
                   text_color=(255, 255, 255))

    draw = ImageDraw.Draw(bg)

    # 로고 (우상단)
    add_logo(draw, (1060, 50))

    # 제목 — 크고 굵게 (flex.team처럼)
    font_big = ImageFont.truetype(FONT_BOLD, 56)
    draw.text((55, 230), "MCP가 바꾸는", fill=(255, 255, 255), font=font_big)
    draw.text((55, 305), "AI 에이전트의 미래", fill=(255, 255, 255), font=font_big)

    bg.save(BASE / "v3_thumb_ai_trend.png", quality=95)


# ============================================================
# 2. Thought Leadership — 딥네이비 + 골드 키워드 강조 + 큰 제목
# ============================================================
def make_thought_leadership():
    print("  Thought Leadership...")
    bg = solid_bg(W, H, (18, 22, 48))

    bg = place_element_blended(bg, BASE / "v2_bg_thought_leadership.png", (450, 0, 830, 720), opacity=180)

    bg = add_badge(bg, "Viewpoint", (55, 55), bg_rgb=(255, 255, 255), bg_alpha=30,
                   text_color=(255, 255, 255))

    draw = ImageDraw.Draw(bg)
    add_logo(draw, (1060, 50))

    font_big = ImageFont.truetype(FONT_BOLD, 56)

    draw.text((55, 210), "AI 도입을 서두르면", fill=(255, 255, 255), font=font_big)

    # 강조 키워드 — 골드 배경 하이라이트
    y2 = 295
    keyword = "실패하는 이유"
    kw_bbox = font_big.getbbox(keyword)
    kw_w = kw_bbox[2] - kw_bbox[0]
    kw_h = kw_bbox[3] - kw_bbox[1]
    # 키워드 뒤에 하이라이트 박스
    highlight = Image.new("RGBA", (kw_w + 16, kw_h + 12), (255, 200, 50, 255))
    bg_rgba = bg.convert("RGBA")
    bg_rgba.paste(highlight, (50, y2 - 2), highlight)
    bg = bg_rgba.convert("RGB")

    draw = ImageDraw.Draw(bg)
    draw.text((55, y2 - 4), keyword, fill=(15, 15, 30), font=font_big)

    bg.save(BASE / "v3_thumb_thought_leadership.png", quality=95)


# ============================================================
# 3. Case Study — 다크블루 데이터 배경 + 큰 헤드라인
# ============================================================
def make_case_study():
    print("  Case Study...")
    bg = solid_bg(W, H, (8, 18, 42))

    bg = place_element_blended(bg, BASE / "v2_bg_case_study.png", (0, 0, W, H), opacity=140)

    bg = add_badge(bg, "Case Study", (55, 55), bg_rgb=(60, 130, 220), bg_alpha=200,
                   text_color=(255, 255, 255))

    draw = ImageDraw.Draw(bg)
    add_logo(draw, (1060, 50))

    font_big = ImageFont.truetype(FONT_BOLD, 58)
    # 그림자 + 본문
    for line_i, line in enumerate(["입찰 자동화로", "처리시간 80% 단축"]):
        y = 250 + line_i * 85
        draw.text((57, y + 3), line, fill=(0, 0, 0), font=font_big)
        draw.text((55, y), line, fill=(255, 255, 255), font=font_big)

    font_s = ImageFont.truetype(FONT_REG, 15)
    draw.text((55, 660), "* 운영 시 담당자 제공 실사 사진이 배경으로 교체됩니다",
              fill=(100, 130, 170), font=font_s)

    bg.save(BASE / "v3_thumb_case_study.png", quality=95)


# ============================================================
# 4. Company News — 웜 앰버 + 큰 다크 제목
# ============================================================
def make_company_news():
    print("  Company News...")
    bg = solid_bg(W, H, (195, 120, 35))

    bg = place_element_blended(bg, BASE / "v2_bg_company_news.png", (400, 0, 880, 720), opacity=200)

    bg = add_badge(bg, "News", (55, 55), bg_rgb=(0, 0, 0), bg_alpha=50,
                   text_color=(255, 255, 255))

    draw = ImageDraw.Draw(bg)
    add_logo(draw, (1060, 50), color=(60, 35, 5))

    font_big = ImageFont.truetype(FONT_BOLD, 56)
    draw.text((55, 250), "매직에꼴,", fill=(30, 15, 0), font=font_big)
    draw.text((55, 330), "AI 혁신 어워드 수상", fill=(30, 15, 0), font=font_big)

    bg.save(BASE / "v3_thumb_company_news.png", quality=95)


if __name__ == "__main__":
    print("[v3 thumbnail compositing]")
    make_ai_trend()
    make_thought_leadership()
    make_case_study()
    make_company_news()
    print("완료!")
