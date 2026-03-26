"""v2: 나노바나나2 배경 위에 텍스트만 오버레이하는 합성 스크립트"""

from PIL import Image, ImageDraw, ImageFont
from pathlib import Path

BASE = Path(__file__).parent
FONT_BOLD = "C:/Windows/Fonts/malgunbd.ttf"
FONT_REG = "C:/Windows/Fonts/malgun.ttf"
W, H = 1280, 720


def add_badge(img, text, pos, bg_rgb, bg_alpha=140, text_color=(255, 255, 255)):
    font = ImageFont.truetype(FONT_BOLD, 18)
    bbox = font.getbbox(text)
    tw, th = bbox[2] - bbox[0], bbox[3] - bbox[1]
    px, py = 12, 7
    bw, bh = tw + px * 2, th + py * 2

    badge = Image.new("RGBA", (bw, bh), (0, 0, 0, 0))
    d = ImageDraw.Draw(badge)
    d.rounded_rectangle((0, 0, bw - 1, bh - 1), radius=6, fill=(*bg_rgb, bg_alpha))
    d.text((px, py - 1), text, fill=text_color, font=font)

    rgba = img.convert("RGBA")
    rgba.paste(badge, pos, badge)
    return rgba.convert("RGB")


def add_logo(draw, pos, color=(255, 255, 255)):
    font = ImageFont.truetype(FONT_BOLD, 18)
    draw.text(pos, "magicecole", fill=color, font=font)


def draw_title(draw, lines, start_pos, font_size=48, color=(255, 255, 255),
               shadow_color=None, highlight=None):
    """여러 줄 제목을 그린다. highlight={"text": "문화", "color": (R,G,B)} 형태로 특정 단어 강조."""
    font = ImageFont.truetype(FONT_BOLD, font_size)
    x, y = start_pos
    line_gap = int(font_size * 1.45)

    for line in lines:
        if shadow_color:
            draw.text((x + 2, y + 2), line, fill=shadow_color, font=font)

        if highlight and highlight["text"] in line:
            # 강조 단어 전후 분리
            parts = line.split(highlight["text"], 1)
            cx = x
            if parts[0]:
                draw.text((cx, y), parts[0], fill=color, font=font)
                cx += font.getbbox(parts[0])[2] - font.getbbox(parts[0])[0]
            draw.text((cx, y), highlight["text"], fill=highlight["color"], font=font)
            cx += font.getbbox(highlight["text"])[2] - font.getbbox(highlight["text"])[0]
            if len(parts) > 1 and parts[1]:
                draw.text((cx, y), parts[1], fill=color, font=font)
        else:
            draw.text((x, y), line, fill=color, font=font)

        y += line_gap


def darken_overlay(img, opacity=80):
    """배경을 살짝 어둡게 해서 텍스트 가독성 확보"""
    overlay = Image.new("RGBA", img.size, (0, 0, 0, opacity))
    return Image.alpha_composite(img.convert("RGBA"), overlay).convert("RGB")


def left_darken(img, width_ratio=0.55, max_alpha=120):
    """좌측만 반투명 어둡게 — 텍스트 영역 가독성"""
    rgba = img.convert("RGBA")
    overlay = Image.new("RGBA", img.size, (0, 0, 0, 0))
    d = ImageDraw.Draw(overlay)
    fade_w = int(img.width * width_ratio)
    for x in range(fade_w):
        alpha = int(max_alpha * (1 - x / fade_w))
        d.line([(x, 0), (x, img.height)], fill=(0, 0, 0, alpha))
    return Image.alpha_composite(rgba, overlay).convert("RGB")


# === 1. AI Trend ===
def make_ai_trend():
    print("  AI Trend...")
    bg = Image.open(BASE / "v2_bg_ai_trend.png").resize((W, H), Image.LANCZOS)
    bg = left_darken(bg, width_ratio=0.5, max_alpha=100)

    bg = add_badge(bg, "AI Trend", (48, 38), bg_rgb=(100, 60, 200), bg_alpha=180)
    draw = ImageDraw.Draw(bg)
    add_logo(draw, (1130, 40))
    draw_title(draw, ["MCP가 바꾸는", "AI 에이전트의 미래"], (50, 250), font_size=46,
               shadow_color=(0, 0, 0, 80))

    bg.save(BASE / "v2_thumb_ai_trend.png", quality=95)


# === 2. Thought Leadership ===
def make_thought_leadership():
    print("  Thought Leadership...")
    bg = Image.open(BASE / "v2_bg_thought_leadership.png").resize((W, H), Image.LANCZOS)
    bg = left_darken(bg, width_ratio=0.5, max_alpha=130)

    bg = add_badge(bg, "Insight", (48, 38), bg_rgb=(180, 150, 40), bg_alpha=200)
    draw = ImageDraw.Draw(bg)
    add_logo(draw, (1130, 40))
    draw_title(draw, ["AI 도입 실패,", "기술이 아닌", "문화의 문제"], (50, 220), font_size=46,
               shadow_color=(0, 0, 0, 100),
               highlight={"text": "문화", "color": (255, 210, 80)})

    bg.save(BASE / "v2_thumb_thought_leadership.png", quality=95)


# === 3. Case Study ===
def make_case_study():
    print("  Case Study...")
    bg = Image.open(BASE / "v2_bg_case_study.png").resize((W, H), Image.LANCZOS)
    bg = left_darken(bg, width_ratio=0.5, max_alpha=110)

    bg = add_badge(bg, "Case Study", (48, 38), bg_rgb=(40, 100, 180), bg_alpha=200)
    draw = ImageDraw.Draw(bg)
    add_logo(draw, (1130, 40))
    draw_title(draw, ["입찰 자동화로", "처리시간 80% 단축"], (50, 260), font_size=48,
               shadow_color=(0, 0, 0, 120))

    # 실사 안내 (작게)
    font_s = ImageFont.truetype(FONT_REG, 14)
    draw.text((50, 650), "* 운영 시 담당자 제공 사진이 배경으로 교체됩니다", fill=(150, 170, 200), font=font_s)

    bg.save(BASE / "v2_thumb_case_study.png", quality=95)


# === 4. Company News ===
def make_company_news():
    print("  Company News...")
    bg = Image.open(BASE / "v2_bg_company_news.png").resize((W, H), Image.LANCZOS)
    bg = left_darken(bg, width_ratio=0.45, max_alpha=80)

    bg = add_badge(bg, "News", (48, 38), bg_rgb=(120, 70, 10), bg_alpha=200, text_color=(255, 240, 200))
    draw = ImageDraw.Draw(bg)
    add_logo(draw, (1130, 40), color=(80, 50, 10))
    draw_title(draw, ["매직에꼴,", "AI 혁신 어워드 수상"], (50, 260), font_size=46,
               color=(40, 20, 0), shadow_color=(255, 255, 255, 30))

    bg.save(BASE / "v2_thumb_company_news.png", quality=95)


if __name__ == "__main__":
    print("[v2 썸네일 합성]")
    make_ai_trend()
    make_thought_leadership()
    make_case_study()
    make_company_news()
    print("완료!")
