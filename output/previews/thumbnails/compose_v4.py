"""v4: flex.team style - simple, clean, bold. PIL only. No AI backgrounds."""

from PIL import Image, ImageDraw, ImageFont
from pathlib import Path
import math

BASE = Path(__file__).parent
FONT_BOLD = "C:/Windows/Fonts/malgunbd.ttf"
FONT_REG = "C:/Windows/Fonts/malgun.ttf"
W, H = 1280, 720


# ============================================================
# Helper functions
# ============================================================

def rounded_rect_img(size, radius, fill):
    """RGBA rounded rectangle image"""
    img = Image.new("RGBA", size, (0, 0, 0, 0))
    ImageDraw.Draw(img).rounded_rectangle((0, 0, size[0]-1, size[1]-1), radius=radius, fill=fill)
    return img


def paste_rgba(base, overlay, pos):
    rgba = base.convert("RGBA")
    rgba.paste(overlay, pos, overlay)
    return rgba.convert("RGB")


def draw_circle_pattern(draw, cx, cy, r, color, rings=8):
    """flex.team AXhub 스타일 — 얇은 원형 와이어프레임 패턴"""
    for i in range(rings):
        ri = r * (0.3 + i * 0.1)
        draw.ellipse((cx - ri, cy - ri, cx + ri, cy + ri), outline=color, width=1)
    # 대각선 연결
    for angle in range(0, 360, 30):
        rad = math.radians(angle)
        x1 = cx + r * 0.2 * math.cos(rad)
        y1 = cy + r * 0.2 * math.sin(rad)
        x2 = cx + r * 0.95 * math.cos(rad)
        y2 = cy + r * 0.95 * math.sin(rad)
        draw.line([(x1, y1), (x2, y2)], fill=color, width=1)


def draw_node_network(draw, cx, cy, r, color, node_color):
    """추상적 노드 네트워크 패턴"""
    import random
    random.seed(42)
    nodes = []
    for _ in range(18):
        angle = random.uniform(0, 2 * math.pi)
        dist = random.uniform(r * 0.15, r * 0.9)
        nx = cx + dist * math.cos(angle)
        ny = cy + dist * math.sin(angle)
        nodes.append((nx, ny))

    # 엣지
    for i, (x1, y1) in enumerate(nodes):
        for j, (x2, y2) in enumerate(nodes):
            if i < j:
                d = math.sqrt((x2-x1)**2 + (y2-y1)**2)
                if d < r * 0.6:
                    draw.line([(x1, y1), (x2, y2)], fill=color, width=1)

    # 노드
    for nx, ny in nodes:
        s = random.randint(3, 6)
        draw.ellipse((nx-s, ny-s, nx+s, ny+s), fill=node_color)


# ============================================================
# 1. AI Trend  (flex AXhub style)
# ============================================================
def make_ai_trend():
    print("  AI Trend...")
    bg_color = (88, 55, 180)  # 보라
    bg = Image.new("RGB", (W, H), bg_color)
    draw = ImageDraw.Draw(bg)

    # 우측 하단 장식 패턴 (와이어프레임 원형)
    line_color = (120, 85, 210)
    node_color = (160, 130, 230)
    draw_node_network(draw, 1000, 420, 320, line_color, node_color)
    draw_circle_pattern(draw, 1000, 420, 300, (110, 78, 200))

    # 카테고리 뱃지
    badge = rounded_rect_img((130, 38), 6, (255, 255, 255, 35))
    font_badge = ImageFont.truetype(FONT_REG, 18)
    ImageDraw.Draw(badge).text((16, 7), "Viewpoint", fill=(255, 255, 255), font=font_badge)
    bg = paste_rgba(bg, badge, (55, 55))

    draw = ImageDraw.Draw(bg)

    # 로고 (우상단)
    font_logo = ImageFont.truetype(FONT_BOLD, 20)
    # 아이콘 심볼
    draw.ellipse((1120, 52, 1132, 64), fill=(255, 255, 255))
    draw.ellipse((1136, 52, 1148, 64), fill=(255, 255, 255))
    draw.text((1155, 48), "magicecole", fill=(255, 255, 255), font=font_logo)

    # 제목 — 크고 굵게
    font_title = ImageFont.truetype(FONT_BOLD, 58)
    draw.text((60, 260), "MCP가 바꾸는", fill=(255, 255, 255), font=font_title)
    draw.text((60, 340), "AI 에이전트의 미래", fill=(255, 255, 255), font=font_title)

    bg.save(BASE / "v4_ai_trend.png", quality=95)


# ============================================================
# 2. Thought Leadership  (flex AXhub style, different color)
# ============================================================
def make_thought_leadership():
    print("  Thought Leadership...")
    bg_color = (20, 25, 55)  # 딥 네이비
    bg = Image.new("RGB", (W, H), bg_color)
    draw = ImageDraw.Draw(bg)

    # 우측 하단 장식 패턴
    line_color = (50, 55, 90)
    node_color = (80, 85, 120)
    draw_node_network(draw, 1000, 420, 320, line_color, node_color)
    draw_circle_pattern(draw, 1000, 420, 300, (45, 50, 85))

    # 뱃지
    badge = rounded_rect_img((130, 38), 6, (255, 255, 255, 30))
    font_badge = ImageFont.truetype(FONT_REG, 18)
    ImageDraw.Draw(badge).text((16, 7), "Viewpoint", fill=(255, 255, 255), font=font_badge)
    bg = paste_rgba(bg, badge, (55, 55))

    draw = ImageDraw.Draw(bg)

    # 로고
    font_logo = ImageFont.truetype(FONT_BOLD, 20)
    draw.ellipse((1120, 52, 1132, 64), fill=(255, 255, 255))
    draw.ellipse((1136, 52, 1148, 64), fill=(255, 255, 255))
    draw.text((1155, 48), "magicecole", fill=(255, 255, 255), font=font_logo)

    # 제목
    font_title = ImageFont.truetype(FONT_BOLD, 58)
    draw.text((60, 230), "AI 도입을 서두르면", fill=(255, 255, 255), font=font_title)

    # 강조 키워드 — 하이라이트 박스
    keyword = "실패하는 이유"
    kw_bbox = font_title.getbbox(keyword)
    kw_w = kw_bbox[2] - kw_bbox[0]
    kw_h = kw_bbox[3] - kw_bbox[1]
    # 하이라이트 배경
    hl = rounded_rect_img((kw_w + 20, kw_h + 14), 4, (255, 200, 50, 255))
    bg = paste_rgba(bg, hl, (55, 318))
    draw = ImageDraw.Draw(bg)
    draw.text((65, 320), keyword, fill=(15, 18, 45), font=font_title)

    bg.save(BASE / "v4_thought_leadership.png", quality=95)


# ============================================================
# 3. Case Study  (실사 제외 — 구조만 보여주기)
# ============================================================
def make_case_study():
    print("  Case Study...")
    bg = Image.new("RGB", (W, H), (245, 245, 245))
    draw = ImageDraw.Draw(bg)

    # 좌측: 사진 영역 placeholder (회색 박스)
    draw.rectangle((0, 0, 680, H), fill=(200, 205, 210))
    font_placeholder = ImageFont.truetype(FONT_REG, 20)
    draw.text((240, 340), "[Photo]", fill=(160, 165, 170), font=font_placeholder)
    draw.text((180, 370), "Provided by manager", fill=(160, 165, 170), font=font_placeholder)

    # 우측: 깨끗한 흰 배경 + 텍스트
    # 뱃지
    badge = rounded_rect_img((130, 36), 6, (40, 100, 200, 230))
    font_badge = ImageFont.truetype(FONT_REG, 17)
    ImageDraw.Draw(badge).text((14, 7), "Case Study", fill=(255, 255, 255), font=font_badge)
    bg = paste_rgba(bg, badge, (720, 160))
    draw = ImageDraw.Draw(bg)

    # 회사/프로젝트명 — 크게
    font_big = ImageFont.truetype(FONT_BOLD, 52)
    draw.text((720, 230), "건설사 A", fill=(20, 20, 25), font=font_big)

    # 설명
    font_desc = ImageFont.truetype(FONT_REG, 20)
    draw.text((720, 310), "입찰 자동화로 처리시간 80% 단축", fill=(80, 85, 95), font=font_desc)
    draw.text((720, 340), "매직에꼴 AX 컨설팅과 함께합니다.", fill=(80, 85, 95), font=font_desc)

    # 로고 (우하단)
    font_logo = ImageFont.truetype(FONT_BOLD, 22)
    draw.ellipse((1100, 610, 1114, 624), fill=(30, 30, 35))
    draw.ellipse((1118, 610, 1132, 624), fill=(30, 30, 35))
    draw.text((1140, 606), "magicecole", fill=(30, 30, 35), font=font_logo)

    bg.save(BASE / "v4_case_study.png", quality=95)


# ============================================================
# 4. Company News  (flex updatenote style — ultra minimal)
# ============================================================
def make_company_news():
    print("  Company News...")
    bg = Image.new("RGB", (W, H), (250, 250, 252))
    draw = ImageDraw.Draw(bg)

    # 좌상단 날짜/타이틀
    font_date = ImageFont.truetype(FONT_BOLD, 40)
    draw.text((65, 70), "2026 Award", fill=(25, 25, 30), font=font_date)

    font_sub = ImageFont.truetype(FONT_BOLD, 28)
    draw.text((65, 125), "AI Innovation", fill=(25, 25, 30), font=font_sub)

    # 중앙: 심플한 원형 아이콘 영역
    # 배경 원 (파스텔)
    cx, cy, cr = 720, 370, 180
    # 은은한 그라디언트 원
    for i in range(cr, 0, -1):
        alpha_r = int(245 - (245 - 220) * i / cr)
        alpha_g = int(245 - (245 - 225) * i / cr)
        alpha_b = int(252 - (252 - 245) * i / cr)
        draw.ellipse((cx-i, cy-i, cx+i, cy+i), fill=(alpha_r, alpha_g, alpha_b))

    # 중앙 아이콘 영역 (둥근 사각형 - 앱 아이콘 느낌)
    icon_size = 90
    ix, iy = cx - icon_size//2, cy - icon_size//2
    draw.rounded_rectangle((ix, iy, ix+icon_size, iy+icon_size), radius=20,
                          fill=(255, 255, 255), outline=(230, 230, 235), width=2)

    # 트로피 심볼 (간단한 도형)
    # 컵
    draw.rounded_rectangle((cx-18, cy-25, cx+18, cy+5), radius=4, fill=(180, 140, 50))
    # 받침대
    draw.rectangle((cx-12, cy+5, cx+12, cy+15), fill=(180, 140, 50))
    draw.rectangle((cx-20, cy+15, cx+20, cy+22), fill=(180, 140, 50))
    # 알림 dot
    draw.ellipse((cx+35, cy-40, cx+50, cy-25), fill=(255, 90, 60))

    # 주변 작은 아이콘들 (은은하게)
    small_icons = [(560, 250), (850, 280), (600, 500), (830, 490)]
    for sx, sy in small_icons:
        draw.rounded_rectangle((sx, sy, sx+45, sy+45), radius=10,
                              fill=(240, 240, 243), outline=(230, 230, 235), width=1)

    # 좌하단 브랜드 마크
    font_brand = ImageFont.truetype(FONT_BOLD, 20)
    draw.ellipse((60, 630, 74, 644), fill=(30, 30, 35))
    draw.ellipse((78, 630, 92, 644), fill=(30, 30, 35))
    font_brand_name = ImageFont.truetype(FONT_BOLD, 22)
    draw.text((100, 626), "magicecole ", fill=(30, 30, 35), font=font_brand_name)
    font_brand_sub = ImageFont.truetype(FONT_REG, 22)
    draw.text((248, 626), "news", fill=(120, 120, 130), font=font_brand_sub)

    bg.save(BASE / "v4_company_news.png", quality=95)


if __name__ == "__main__":
    print("[v4] simple & clean")
    make_ai_trend()
    make_thought_leadership()
    make_case_study()
    make_company_news()
    print("done!")
