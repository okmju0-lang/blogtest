"""카테고리별 샘플 썸네일 합성 스크립트"""

from PIL import Image, ImageDraw, ImageFont
from pathlib import Path

BASE = Path(__file__).parent
ELEMENTS = BASE / "elements"
FONT_BOLD = "C:/Windows/Fonts/malgunbd.ttf"
FONT_REG = "C:/Windows/Fonts/malgun.ttf"

W, H = 1280, 720  # 16:9


def draw_rounded_rect(draw, xy, radius, fill):
    x0, y0, x1, y1 = xy
    draw.rounded_rectangle(xy, radius=radius, fill=fill)


def gradient_bg(w, h, color_top, color_bottom):
    img = Image.new("RGB", (w, h))
    for y in range(h):
        r = int(color_top[0] + (color_bottom[0] - color_top[0]) * y / h)
        g = int(color_top[1] + (color_bottom[1] - color_top[1]) * y / h)
        b = int(color_top[2] + (color_bottom[2] - color_top[2]) * y / h)
        for x in range(w):
            img.putpixel((x, y), (r, g, b))
    return img


def gradient_bg_fast(w, h, color_top, color_bottom):
    """빠른 그라디언트 생성 (라인 단위)"""
    img = Image.new("RGB", (w, h))
    draw = ImageDraw.Draw(img)
    for y in range(h):
        r = int(color_top[0] + (color_bottom[0] - color_top[0]) * y / h)
        g = int(color_top[1] + (color_bottom[1] - color_top[1]) * y / h)
        b = int(color_top[2] + (color_bottom[2] - color_top[2]) * y / h)
        draw.line([(0, y), (w, y)], fill=(r, g, b))
    return img


def add_text(draw, text, pos, font_size, color=(255, 255, 255), max_width=700, shadow=False):
    font = ImageFont.truetype(FONT_BOLD, font_size)
    lines = []
    for line in text.split("\n"):
        words = list(line)
        current = ""
        for ch in words:
            test = current + ch
            bbox = font.getbbox(test)
            if bbox[2] - bbox[0] > max_width and current:
                lines.append(current)
                current = ch
            else:
                current = test
        if current:
            lines.append(current)

    x, y = pos
    for line in lines:
        if shadow:
            draw.text((x + 2, y + 2), line, fill=(0, 0, 0, 180), font=font)
        draw.text((x, y), line, fill=color, font=font)
        bbox = font.getbbox(line)
        y += (bbox[3] - bbox[1]) + 12


def add_badge(base_img, text, pos, bg_color_rgb, bg_alpha=100, text_color=(255, 255, 255)):
    """반투명 뱃지를 RGBA 오버레이로 합성"""
    font = ImageFont.truetype(FONT_BOLD, 20)
    bbox = font.getbbox(text)
    tw, th = bbox[2] - bbox[0], bbox[3] - bbox[1]
    x, y = pos
    px, py = 14, 8
    bw, bh = tw + px * 2, th + py * 2

    badge = Image.new("RGBA", (bw, bh), (0, 0, 0, 0))
    badge_draw = ImageDraw.Draw(badge)
    badge_draw.rounded_rectangle((0, 0, bw - 1, bh - 1), radius=8, fill=(*bg_color_rgb, bg_alpha))
    badge_draw.text((px, py - 2), text, fill=text_color, font=font)

    base_rgba = base_img.convert("RGBA")
    base_rgba.paste(badge, (x, y), badge)
    return base_rgba.convert("RGB")


def add_logo_placeholder(draw, pos):
    """로고 파일 없으므로 텍스트 placeholder"""
    font = ImageFont.truetype(FONT_BOLD, 20)
    draw.text(pos, "magicecole", fill=(255, 255, 255, 200), font=font)


def place_element(base, element_path, region):
    """그래픽 요소를 base 이미지의 region에 합성"""
    elem = Image.open(element_path).convert("RGBA")
    rx, ry, rw, rh = region
    elem = elem.resize((rw, rh), Image.LANCZOS)
    # 반투명 합성
    base.paste(elem, (rx, ry), elem if elem.mode == "RGBA" else None)


# === 1. AI Trend ===
def make_ai_trend():
    print("  AI Trend 썸네일 생성 중...")
    bg = gradient_bg_fast(W, H, (40, 20, 120), (80, 50, 180))
    draw = ImageDraw.Draw(bg)

    # 그래픽 요소 (우측)
    elem = Image.open(ELEMENTS / "ai_trend_element.png").convert("RGBA")
    elem = elem.resize((560, 420), Image.LANCZOS)
    bg.paste(elem, (700, 180), elem)

    bg = add_badge(bg, "AI Trend", (50, 40), bg_color_rgb=(255, 255, 255), bg_alpha=45)
    draw = ImageDraw.Draw(bg)
    add_logo_placeholder(draw, (1100, 42))
    add_text(draw, "MCP가 바꾸는\nAI 에이전트의 미래", (50, 200), font_size=52)

    bg.save(BASE / "thumb_ai_trend.png")
    print("    -> thumb_ai_trend.png")


# === 2. Thought Leadership ===
def make_thought_leadership():
    print("  Thought Leadership 썸네일 생성 중...")
    bg = gradient_bg_fast(W, H, (10, 15, 50), (25, 35, 80))
    draw = ImageDraw.Draw(bg)

    elem = Image.open(ELEMENTS / "thought_leadership_element.png").convert("RGBA")
    elem = elem.resize((520, 390), Image.LANCZOS)
    bg.paste(elem, (720, 200), elem)

    bg = add_badge(bg, "Insight", (50, 40), bg_color_rgb=(255, 255, 255), bg_alpha=45)
    draw = ImageDraw.Draw(bg)
    add_logo_placeholder(draw, (1100, 42))

    # 제목 + 강조색 키워드
    font_title = ImageFont.truetype(FONT_BOLD, 50)
    draw.text((50, 220), "AI 도입 실패,", fill=(255, 255, 255), font=font_title)
    draw.text((50, 295), "기술이 아닌", fill=(255, 255, 255), font=font_title)

    font_accent = ImageFont.truetype(FONT_BOLD, 50)
    draw.text((50, 370), "문화", fill=(255, 200, 60), font=font_accent)
    bbox2 = font_accent.getbbox("문화")
    draw.text((50 + bbox2[2] - bbox2[0], 370), "의 문제", fill=(255, 255, 255), font=font_title)

    bg.save(BASE / "thumb_thought_leadership.png")
    print("    -> thumb_thought_leadership.png")


# === 3. Case Study (실사 없이 그라디언트+오버레이+텍스트) ===
def make_case_study():
    print("  Case Study 썸네일 생성 중 (실사 제외)...")
    # 실사 사진 대신 진한 블루 그라디언트 + 패턴 느낌
    bg = gradient_bg_fast(W, H, (0, 30, 80), (0, 15, 45))
    draw = ImageDraw.Draw(bg)

    # 하단 반투명 오버레이 효과 (실사 위에 올라갈 것을 시뮬레이션)
    overlay = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    overlay_draw = ImageDraw.Draw(overlay)
    for y in range(H // 2, H):
        alpha = int(80 + (y - H // 2) / (H // 2) * 120)
        overlay_draw.line([(0, y), (W, y)], fill=(0, 20, 60, alpha))
    bg = Image.alpha_composite(bg.convert("RGBA"), overlay).convert("RGB")

    bg = bg.convert("RGB")
    bg = add_badge(bg, "Case Study", (50, 40), bg_color_rgb=(255, 255, 255), bg_alpha=50)
    draw = ImageDraw.Draw(bg)
    add_logo_placeholder(draw, (1080, 42))

    # 중앙 안내 텍스트
    font_note = ImageFont.truetype(FONT_REG, 18)
    draw.text((50, 560), "* 실제 사진은 담당자 제공 후 합성 예정", fill=(140, 160, 190), font=font_note)

    # 제목 (성과 수치 포함, 큰 글씨, 그림자) — 중앙 배치
    font_title = ImageFont.truetype(FONT_BOLD, 58)
    lines = ["입찰 자동화로", "처리시간 80% 단축"]
    y_start = 280
    for i, line in enumerate(lines):
        y = y_start + i * 85
        draw.text((53, y + 3), line, fill=(0, 0, 0), font=font_title)
        draw.text((50, y), line, fill=(255, 255, 255), font=font_title)

    bg.save(BASE / "thumb_case_study.png")
    print("    -> thumb_case_study.png")


# === 4. Company News ===
def make_company_news():
    print("  Company News 썸네일 생성 중...")
    bg = gradient_bg_fast(W, H, (200, 120, 30), (230, 160, 50))
    draw = ImageDraw.Draw(bg)

    elem = Image.open(ELEMENTS / "company_news_element.png").convert("RGBA")
    elem = elem.resize((500, 375), Image.LANCZOS)
    bg.paste(elem, (740, 200), elem)

    bg = add_badge(bg, "News", (50, 40), bg_color_rgb=(0, 0, 0), bg_alpha=70, text_color=(255, 255, 255))
    draw = ImageDraw.Draw(bg)
    add_logo_placeholder(draw, (1100, 42))
    add_text(
        draw,
        "매직에꼴,\nAI 혁신 어워드 수상",
        (50, 220),
        font_size=52,
        color=(30, 20, 0),
    )

    bg.save(BASE / "thumb_company_news.png")
    print("    -> thumb_company_news.png")


if __name__ == "__main__":
    print("[썸네일 샘플 합성]")
    make_ai_trend()
    make_thought_leadership()
    make_case_study()
    make_company_news()
    print("\n완료! output/previews/thumbnails/ 에서 확인하세요.")
