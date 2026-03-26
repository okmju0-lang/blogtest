"""v5: magicecole identity - Pretendard font, original design"""

from PIL import Image, ImageDraw, ImageFont
from pathlib import Path
import math

BASE = Path(__file__).parent
FONTS = Path(__file__).parent.parent.parent.parent / "assets" / "fonts"
F_BLACK = str(FONTS / "Pretendard-Black.otf")
F_EXTRABOLD = str(FONTS / "Pretendard-ExtraBold.otf")
F_BOLD = str(FONTS / "Pretendard-Bold.otf")
F_SEMI = str(FONTS / "Pretendard-SemiBold.otf")
F_REG = str(FONTS / "Pretendard-Regular.otf")
W, H = 1280, 720


def paste_rgba(base, overlay, pos):
    rgba = base.convert("RGBA")
    rgba.paste(overlay, pos, overlay)
    return rgba.convert("RGB")


def draw_logo(draw, x, y, color=(255, 255, 255), size=20):
    """magicecole 로고 placeholder (dot + text)"""
    font = ImageFont.truetype(F_BOLD, size)
    r = size // 4
    draw.ellipse((x, y + size//2 - r, x + r*2, y + size//2 + r), fill=color)
    draw.text((x + r*2 + 8, y), "magicecole", fill=color, font=font)


# ============================================================
# 1. AI Trend
#    보라 배경 / 좌측 큰 제목 / 우하단 얇은 곡선 장식
# ============================================================
def make_ai_trend():
    print("  AI Trend...")
    bg = Image.new("RGB", (W, H), (95, 60, 190))
    draw = ImageDraw.Draw(bg)

    # 장식: 우하단 반원형 얇은 곡선 3개 (은은하게)
    accent = (120, 85, 215)
    for i, offset in enumerate([0, 40, 80]):
        r = 350 - offset
        draw.arc((W - r - 80, H - r + 60, W + r - 80, H + r + 60),
                 start=200, end=340, fill=accent, width=2)

    # 카테고리
    font_cat = ImageFont.truetype(F_SEMI, 18)
    draw.text((64, 56), "AI Trend", fill=(220, 200, 255), font=font_cat)

    # 로고
    draw_logo(draw, 1080, 54)

    # 제목
    font_t = ImageFont.truetype(F_BLACK, 62)
    draw.text((64, 260), "MCP가 바꾸는", fill=(255, 255, 255), font=font_t)
    draw.text((64, 345), "AI 에이전트의 미래", fill=(255, 255, 255), font=font_t)

    bg.save(BASE / "v5_ai_trend.png", quality=95)


# ============================================================
# 2. Thought Leadership
#    딥네이비 / 큰 제목 / 키워드 하이라이트 / 우하단 곡선
# ============================================================
def make_thought_leadership():
    print("  Thought Leadership...")
    bg = Image.new("RGB", (W, H), (22, 27, 58))
    draw = ImageDraw.Draw(bg)

    # 장식: 우하단 곡선
    accent = (40, 48, 82)
    for i, offset in enumerate([0, 40, 80]):
        r = 350 - offset
        draw.arc((W - r - 80, H - r + 60, W + r - 80, H + r + 60),
                 start=200, end=340, fill=accent, width=2)

    # 카테고리
    font_cat = ImageFont.truetype(F_SEMI, 18)
    draw.text((64, 56), "Insight", fill=(160, 165, 195), font=font_cat)

    draw_logo(draw, 1080, 54)

    # 제목
    font_t = ImageFont.truetype(F_BLACK, 62)
    draw.text((64, 240), "AI 도입을 서두르면", fill=(255, 255, 255), font=font_t)

    # 하이라이트 키워드
    keyword = "실패하는 이유"
    kw_bbox = font_t.getbbox(keyword)
    kw_w, kw_h = kw_bbox[2] - kw_bbox[0], kw_bbox[3] - kw_bbox[1]
    hl = Image.new("RGBA", (kw_w + 24, kw_h + 10), (255, 205, 55, 255))
    bg = paste_rgba(bg, hl, (58, 334))
    draw = ImageDraw.Draw(bg)
    draw.text((64, 328), keyword, fill=(18, 22, 50), font=font_t)

    bg.save(BASE / "v5_thought_leadership.png", quality=95)


# ============================================================
# 3. Case Study (실행 가이드형)
#    좌 실사 placeholder / 우 흰 배경 + 큰 텍스트
# ============================================================
def make_case_study():
    print("  Case Study...")
    bg = Image.new("RGB", (W, H), (248, 248, 250))
    draw = ImageDraw.Draw(bg)

    # 좌측 사진 영역
    draw.rectangle((0, 0, 620, H), fill=(215, 218, 224))
    font_ph = ImageFont.truetype(F_REG, 16)
    draw.text((245, 350), "Photo", fill=(175, 180, 188), font=font_ph)

    # 우측 콘텐츠
    # 카테고리 뱃지
    badge = Image.new("RGBA", (128, 34), (0, 0, 0, 0))
    bd = ImageDraw.Draw(badge)
    bd.rounded_rectangle((0, 0, 127, 33), radius=6, fill=(50, 100, 210, 230))
    font_badge = ImageFont.truetype(F_SEMI, 16)
    bd.text((14, 7), "Case Study", fill=(255, 255, 255), font=font_badge)
    bg = paste_rgba(bg, badge, (670, 200))
    draw = ImageDraw.Draw(bg)

    # 회사명 (크게)
    font_name = ImageFont.truetype(F_BLACK, 48)
    draw.text((670, 260), "건설사 A", fill=(20, 22, 28), font=font_name)

    # 설명
    font_desc = ImageFont.truetype(F_REG, 18)
    draw.text((670, 335), "입찰 자동화로 처리시간 80% 단축", fill=(90, 95, 108), font=font_desc)
    draw.text((670, 362), "매직에꼴 AX 컨설팅과 함께합니다.", fill=(90, 95, 108), font=font_desc)

    # 로고 (우하단)
    draw_logo(draw, 1060, 640, color=(35, 38, 45), size=18)

    bg.save(BASE / "v5_case_study.png", quality=95)


# ============================================================
# 4. Company News
#    밝은 배경 / 좌측 큰 한글 제목 / 우측 단색 강조 블록
# ============================================================
def make_company_news():
    print("  Company News...")
    bg = Image.new("RGB", (W, H), (252, 252, 254))
    draw = ImageDraw.Draw(bg)

    # 우측 컬러 블록 (매직에꼴 브랜드 포인트)
    draw.rectangle((880, 0, W, H), fill=(50, 65, 210))

    # 장식: 블록 경계에 얇은 세로선
    draw.line([(878, 0), (878, H)], fill=(230, 230, 235), width=2)

    # 우측 블록 안: 연도
    font_year = ImageFont.truetype(F_BLACK, 80)
    draw.text((920, 260), "2026", fill=(255, 255, 255), font=font_year)
    font_ysub = ImageFont.truetype(F_REG, 22)
    draw.text((920, 355), "AI Innovation Award", fill=(180, 190, 255), font=font_ysub)

    # 좌측: 제목
    font_cat = ImageFont.truetype(F_SEMI, 18)
    draw.text((64, 56), "News", fill=(130, 135, 148), font=font_cat)

    font_t = ImageFont.truetype(F_BLACK, 52)
    draw.text((64, 270), "매직에꼴,", fill=(20, 22, 28), font=font_t)
    draw.text((64, 345), "AI 혁신 어워드 수상", fill=(20, 22, 28), font=font_t)

    # 로고
    draw_logo(draw, 64, 640, color=(35, 38, 45), size=18)

    bg.save(BASE / "v5_company_news.png", quality=95)


if __name__ == "__main__":
    print("[v5]")
    make_ai_trend()
    make_thought_leadership()
    make_case_study()
    make_company_news()
    print("done!")
