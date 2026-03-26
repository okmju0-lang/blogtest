"""v6 Case Study: sparta + flex HTTT hybrid"""

from PIL import Image, ImageDraw, ImageFont
from pathlib import Path

BASE = Path(__file__).parent
FONTS = Path(__file__).parent.parent.parent.parent / "assets" / "fonts"
F_BLACK = str(FONTS / "Pretendard-Black.otf")
F_BOLD = str(FONTS / "Pretendard-Bold.otf")
F_SEMI = str(FONTS / "Pretendard-SemiBold.otf")
F_REG = str(FONTS / "Pretendard-Regular.otf")
W, H = 1280, 720


def paste_rgba(base, overlay, pos):
    rgba = base.convert("RGBA")
    rgba.paste(overlay, pos, overlay)
    return rgba.convert("RGB")


def make_case_study():
    # 1. 사진 풀블리드
    photo = Image.open(BASE / "v5_cs_photo.png").convert("RGB")
    photo = photo.resize((W, H), Image.LANCZOS)

    # 2. 좌측 그라디언트 오버레이 (flex HTTT 스타일: 좌→우 페이드)
    #    + 하단 추가 어둡게 (sparta 스타일)
    overlay = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    d = ImageDraw.Draw(overlay)

    # 좌측에서 우측으로 페이드 (좌측이 진하게)
    for x in range(W):
        if x < W * 0.45:
            alpha = 175
        elif x < W * 0.75:
            progress = (x - W * 0.45) / (W * 0.3)
            alpha = int(175 * (1 - progress))
        else:
            alpha = 0
        d.line([(x, 0), (x, H)], fill=(15, 12, 30, alpha))

    # 하단 추가 그라디언트 (전체 폭)
    for y in range(int(H * 0.7), H):
        progress = (y - H * 0.7) / (H * 0.3)
        alpha = int(progress * 100)
        d.line([(0, y), (W, y)], fill=(15, 12, 30, alpha))

    bg = Image.alpha_composite(photo.convert("RGBA"), overlay).convert("RGB")
    draw = ImageDraw.Draw(bg)

    # 3. 좌상단: Case Study 뱃지
    badge = Image.new("RGBA", (138, 34), (0, 0, 0, 0))
    bd = ImageDraw.Draw(badge)
    bd.rounded_rectangle((0, 0, 137, 33), radius=6, fill=(255, 255, 255, 210))
    font_badge = ImageFont.truetype(F_BOLD, 15)
    bd.text((14, 8), "Case Study", fill=(30, 20, 55), font=font_badge)
    bg = paste_rgba(bg, badge, (48, 42))
    draw = ImageDraw.Draw(bg)

    # 4. 우상단: 로고
    font_logo = ImageFont.truetype(F_BOLD, 18)
    draw.text((1098, 46), "magicecole", fill=(255, 255, 255), font=font_logo)

    # 5. 좌측 정보 영역 (flex HTTT 스타일)
    # 회사명 (크게)
    font_company = ImageFont.truetype(F_BLACK, 48)
    draw.text((50, 250), "건설사 A", fill=(255, 255, 255), font=font_company)

    # 헤드라인 (스파르타 스타일 큰 텍스트)
    font_headline = ImageFont.truetype(F_BLACK, 40)
    draw.text((50, 330), "입찰 자동화로", fill=(255, 255, 255), font=font_headline)
    draw.text((50, 385), "처리시간 80% 단축", fill=(255, 255, 255), font=font_headline)

    # 부제 (flex 스타일 설명)
    font_sub = ImageFont.truetype(F_REG, 17)
    draw.text((50, 450), "매직에꼴 AX 컨설팅과 함께합니다.", fill=(200, 200, 215), font=font_sub)

    bg.save(BASE / "v6_case_study.png", quality=95)
    print("  -> v6_case_study.png")


if __name__ == "__main__":
    make_case_study()
