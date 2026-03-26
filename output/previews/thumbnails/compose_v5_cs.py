"""v5 Case Study: sparta style - full bleed photo + overlay + headline"""

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

    # 2. 하단 그라디언트 오버레이 (보라~투명, 스파르타 스타일)
    overlay = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    d = ImageDraw.Draw(overlay)

    # 상단 1/3: 살짝 어둡게 (뱃지/로고 가독성)
    for y in range(0, H // 4):
        alpha = int(60 * (1 - y / (H // 4)))
        d.line([(0, y), (W, y)], fill=(20, 15, 40, alpha))

    # 하단 2/3: 진한 보라 그라디언트 (아래로 갈수록 진하게)
    start_y = H // 3
    for y in range(start_y, H):
        progress = (y - start_y) / (H - start_y)
        alpha = int(40 + progress * 180)
        d.line([(0, y), (W, y)], fill=(35, 20, 65, alpha))

    bg = Image.alpha_composite(photo.convert("RGBA"), overlay).convert("RGB")

    # 3. 좌상단 뱃지
    badge = Image.new("RGBA", (148, 36), (0, 0, 0, 0))
    bd = ImageDraw.Draw(badge)
    bd.rounded_rectangle((0, 0, 147, 35), radius=6, fill=(255, 255, 255, 200))
    font_badge = ImageFont.truetype(F_BOLD, 16)
    bd.text((14, 8), "Case Study", fill=(35, 20, 65), font=font_badge)
    bg = paste_rgba(bg, badge, (48, 40))

    draw = ImageDraw.Draw(bg)

    # 4. 우상단 로고
    font_logo = ImageFont.truetype(F_BOLD, 20)
    # 그림자
    draw.text((1082, 47), "magicecole", fill=(0, 0, 0, 60), font=font_logo)
    draw.text((1080, 45), "magicecole", fill=(255, 255, 255), font=font_logo)

    # 5. 하단 헤드라인 (크고 굵게)
    font_t = ImageFont.truetype(F_BLACK, 56)
    lines = ["입찰 자동화로", "처리시간 80% 단축"]
    y_start = 480
    for i, line in enumerate(lines):
        y = y_start + i * 72
        # 그림자
        draw.text((52, y + 2), line, fill=(0, 0, 0, 100), font=font_t)
        draw.text((50, y), line, fill=(255, 255, 255), font=font_t)

    bg.save(BASE / "v5_case_study.png", quality=95)
    print("  -> v5_case_study.png")


if __name__ == "__main__":
    print("[v5 Case Study]")
    make_case_study()
    print("done!")
