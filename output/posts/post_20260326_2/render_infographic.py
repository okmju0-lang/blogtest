from pathlib import Path

from PIL import Image, ImageDraw, ImageFont


W, H = 1600, 1200
BG_TOP = (10, 25, 56)
BG_BOTTOM = (22, 52, 92)
CARD = (21, 38, 72)
CARD_2 = (18, 33, 64)
ACCENT = (244, 192, 74)
CYAN = (96, 211, 255)
WHITE = (245, 248, 252)
MUTED = (187, 201, 224)
RED = (255, 121, 121)


def font(path: str, size: int) -> ImageFont.FreeTypeFont:
    return ImageFont.truetype(path, size=size)


def text(draw: ImageDraw.ImageDraw, xy: tuple[int, int], value: str, face: str, size: int, fill, spacing: int = 4):
    draw.text(xy, value, font=font(face, size), fill=fill, spacing=spacing)


def main() -> None:
    root = Path.cwd()
    bold = r"C:\Windows\Fonts\malgunbd.ttf"
    regular = r"C:\Windows\Fonts\malgun.ttf"

    title_small = "\uae30\uc5c5 AX \ucd5c\ub300 \ub9ac\uc2a4\ud06c\ub294"
    title_main = "\uac70\ubc84\ub10c\uc2a4 \uc5c6\ub294 AI \ud655\uc0b0"
    subtitle = (
        "\ud604\uc7a5 \uc0ac\uc6a9 \uc18d\ub3c4\ub294 \ube60\ub978\ub370 \ud1b5\uc81c, \ub370\uc774\ud130 \uae30\uc900, \uad50\uc721\uc774 \ub530\ub77c\uc624\uc9c0 \uc54a\uc73c\uba74\n"
        "\uc0dd\uc0b0\uc131\ubcf4\ub2e4 \ub9ac\uc2a4\ud06c\uac00 \uba3c\uc800 \ucee4\uc9d1\ub2c8\ub2e4."
    )
    badge = "AX \ud575\uc2ec \uc778\uc0ac\uc774\ud2b8"
    bottom_1 = (
        "\ud575\uc2ec: \uae30\uc5c5 AX\uc5d0\uc11c \uac00\uc7a5 \uc704\ud5d8\ud55c \uc0c1\ud0dc\ub294 AI\ub97c \uc548 \uc4f0\ub294 \uc870\uc9c1\uc774 \uc544\ub2c8\ub77c,"
    )
    bottom_2 = "\uae30\uc900 \uc5c6\uc774 \ube60\ub974\uac8c \uc4f0\uace0 \uc788\ub294 \uc870\uc9c1\uc785\ub2c8\ub2e4."

    cards = [
        (
            (90, 470, 390, 700),
            "75%",
            "\uc5c5\ubb34\uc5d0 AI \uc0ac\uc6a9",
            "\uc9c0\uc2dd \uadfc\ub85c\uc790 \uae30\uc900",
            CYAN,
        ),
        (
            (430, 470, 730, 700),
            "78%",
            "\uac1c\uc778 \ub3c4\uad6c \uc0ac\uc6a9",
            "BYOAI \uc0c1\ud0dc",
            CYAN,
        ),
        (
            (770, 470, 1070, 700),
            "60%",
            "AI \uacc4\ud68d \ubd80\uc871",
            "\ub9ac\ub354 \uc751\ub2f5",
            ACCENT,
        ),
        (
            (1110, 470, 1510, 700),
            "72% vs 1/3",
            "\uc804\uc0ac \ud655\uc0b0 vs \ud1b5\uc81c",
            "EY \uc870\uc0ac \uc694\uc57d",
            ACCENT,
        ),
    ]

    flow = [
        (
            (90, 770, 380, 940),
            "\ube60\ub978 AI \ud655\uc0b0",
            "\ubcf4\uace0\uc11c, \uac80\uc0c9, \uc694\uc57d\uc5d0\nAI \uc0ac\uc6a9 \ud655\ub300",
            CYAN,
        ),
        (
            (430, 770, 720, 940),
            "\ud1b5\uc81c \uacf5\ubc31",
            "\uc2b9\uc778 \uae30\uc900, \ub370\uc774\ud130 \uc6d0\uce59,\n\ucc45\uc784 \uad6c\uc870 \ubbf8\ud761",
            RED,
        ),
        (
            (770, 770, 1060, 940),
            "\uc6b4\uc601 \ub9ac\uc2a4\ud06c",
            "\ubcf4\uc548, \uc131\uacfc \uce21\uc815,\n\ud1b5\ud569 \uc774\uc288 \ud655\ub300",
            ACCENT,
        ),
        (
            (1110, 770, 1510, 940),
            "\ud544\uc694\ud55c \ub300\uc751",
            "Govern \u00b7 Map \u00b7\nMeasure \u00b7 Manage",
            CYAN,
        ),
    ]

    img = Image.new("RGB", (W, H), BG_TOP)
    px = img.load()
    for y in range(H):
        ratio = y / (H - 1)
        r = int(BG_TOP[0] * (1 - ratio) + BG_BOTTOM[0] * ratio)
        g = int(BG_TOP[1] * (1 - ratio) + BG_BOTTOM[1] * ratio)
        b = int(BG_TOP[2] * (1 - ratio) + BG_BOTTOM[2] * ratio)
        for x in range(W):
            px[x, y] = (r, g, b)

    draw = ImageDraw.Draw(img)

    for x in range(80, W, 120):
        draw.line((x, 0, x, H), fill=(20, 45, 82), width=1)
    for y in range(110, H, 110):
        draw.line((0, y, W, y), fill=(20, 45, 82), width=1)

    draw.rounded_rectangle((90, 70, 320, 122), radius=20, fill=(38, 61, 104), outline=(110, 142, 198), width=2)
    text(draw, (120, 82), badge, bold, 28, WHITE)
    text(draw, (90, 155), title_small, bold, 64, WHITE)
    text(draw, (90, 235), title_main, bold, 78, ACCENT)
    text(draw, (90, 338), subtitle, regular, 30, MUTED, spacing=10)

    for i, (box, stat, label, sub, border) in enumerate(cards):
        fill = CARD if i < 3 else (45, 54, 93)
        draw.rounded_rectangle(box, radius=28, fill=fill, outline=border, width=4)
        x1, y1, _, _ = box
        text(draw, (x1 + 28, y1 + 24), stat, bold, 54, WHITE)
        text(draw, (x1 + 28, y1 + 108), label, bold, 30, WHITE)
        text(draw, (x1 + 28, y1 + 160), sub, regular, 24, MUTED)

    for box, label, body, border in flow:
        draw.rounded_rectangle(box, radius=26, fill=CARD_2, outline=border, width=4)
        x1, y1, _, _ = box
        text(draw, (x1 + 24, y1 + 24), label, bold, 34, WHITE)
        text(draw, (x1 + 24, y1 + 88), body, regular, 24, MUTED, spacing=8)

    for arrow_x in (405, 745, 1085):
        draw.polygon(
            [
                (arrow_x, 845),
                (arrow_x + 28, 820),
                (arrow_x + 28, 837),
                (arrow_x + 70, 837),
                (arrow_x + 70, 853),
                (arrow_x + 28, 853),
                (arrow_x + 28, 870),
            ],
            fill=WHITE,
        )

    draw.rounded_rectangle((90, 985, 1510, 1115), radius=30, fill=(247, 191, 72), outline=(255, 227, 160), width=4)
    text(draw, (130, 1018), bottom_1, bold, 34, (18, 27, 45))
    text(draw, (130, 1068), bottom_2, bold, 40, (18, 27, 45))

    out_paths = [
        root / "output" / "drafts" / "post_20260326_2" / "images" / "infographic_1.png",
        root / "output" / "posts" / "post_20260326_2" / "images" / "infographic_1.png",
    ]
    for out_path in out_paths:
        out_path.parent.mkdir(parents=True, exist_ok=True)
        img.save(out_path)
        print(out_path)
        print(out_path.stat().st_size)


if __name__ == "__main__":
    main()
