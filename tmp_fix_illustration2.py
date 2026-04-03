from PIL import Image, ImageDraw, ImageFont


IMG_PATH = r"output/posts/post_20260330_1/images/illustration_2.png"


def main() -> None:
    img = Image.open(IMG_PATH).convert("RGBA")
    draw = ImageDraw.Draw(img)
    # Replace only the second line while preserving the original top line.
    draw.rounded_rectangle((1035, 368, 1300, 474), radius=14, fill=(255, 255, 255, 255))
    font = ImageFont.truetype(r"C:\Windows\Fonts\malgunbd.ttf", 68)
    text = "\uc704\ud55c \uac80\uc0c9"
    bbox = draw.textbbox((0, 0), text, font=font)
    width = bbox[2] - bbox[0]
    x = 1166 - width / 2
    draw.text((x, 372), text, font=font, fill=(18, 24, 38, 255))

    img.save(IMG_PATH)


if __name__ == "__main__":
    main()
