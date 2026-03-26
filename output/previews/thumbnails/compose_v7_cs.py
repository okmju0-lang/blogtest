"""v7 Case Study: flex customer-interview style exactly"""

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
    bg = Image.new("RGB", (W, H), (255, 255, 255))
    draw = ImageDraw.Draw(bg)

    # ── 좌측: 사진 영역 (전체 너비의 약 55%) ──
    photo_w = 700
    photo = Image.open(BASE / "v5_cs_photo.png").convert("RGB")
    # 사진을 좌측 영역에 맞게 크롭+리사이즈
    ph, pw = photo.size[1], photo.size[0]
    target_ratio = photo_w / H
    src_ratio = pw / ph
    if src_ratio > target_ratio:
        new_w = int(ph * target_ratio)
        left = (pw - new_w) // 2
        photo = photo.crop((left, 0, left + new_w, ph))
    else:
        new_h = int(pw / target_ratio)
        top = (ph - new_h) // 2
        photo = photo.crop((0, top, pw, top + new_h))
    photo = photo.resize((photo_w, H), Image.LANCZOS)
    bg.paste(photo, (0, 0))

    draw = ImageDraw.Draw(bg)

    # ── 우측: 깨끗한 흰 배경 + 정보 ──
    rx = 740  # 우측 콘텐츠 시작 x

    # "with magicecole" 뱃지 (우측 상단)
    badge = Image.new("RGBA", (190, 36), (0, 0, 0, 0))
    bd = ImageDraw.Draw(badge)
    bd.rounded_rectangle((0, 0, 189, 35), radius=18, outline=(180, 185, 195, 255), width=1)
    font_badge = ImageFont.truetype(F_REG, 15)
    bd.text((16, 9), "with magicecole", fill=(100, 105, 115), font=font_badge)
    bg = paste_rgba(bg, badge, (rx + 80, 130))
    draw = ImageDraw.Draw(bg)

    # 회사명 (크고 굵게)
    font_name = ImageFont.truetype(F_BLACK, 52)
    draw.text((rx, 280), "건설사 A", fill=(20, 22, 28), font=font_name)

    # 설명 (2줄)
    font_desc = ImageFont.truetype(F_REG, 17)
    draw.text((rx, 360), "입찰 자동화로 처리시간 80% 단축", fill=(100, 105, 118), font=font_desc)
    draw.text((rx, 386), "건설사 A의 성장에 magicecole이 함께합니다.", fill=(100, 105, 118), font=font_desc)

    # 로고 (우하단)
    font_logo = ImageFont.truetype(F_BLACK, 24)
    # dot icon
    draw.ellipse((rx + 200, 560, rx + 216, 576), fill=(25, 28, 35))
    draw.text((rx + 222, 554), "magicecole", fill=(25, 28, 35), font=font_logo)

    bg.save(BASE / "v7_case_study.png", quality=95)
    print("  -> v7_case_study.png")


if __name__ == "__main__":
    make_case_study()
