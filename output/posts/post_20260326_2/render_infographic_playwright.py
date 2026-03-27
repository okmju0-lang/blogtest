from pathlib import Path
from time import sleep

from playwright.sync_api import sync_playwright


def main() -> None:
    root = Path.cwd()
    post_dir = root / "output" / "posts" / "post_20260326_2"
    draft_images_dir = root / "output" / "drafts" / "post_20260326_2" / "images"
    targets = [
        ("infographic_1.html", "infographic_1.png"),
        ("infographic_2.html", "infographic_2.png"),
    ]

    with sync_playwright() as p:
        browser = p.chromium.launch()
        for html_name, image_name in targets:
            html_path = post_dir / html_name
            out_paths = [
                post_dir / "images" / image_name,
                draft_images_dir / image_name,
            ]
            page = browser.new_page(viewport={"width": 1600, "height": 1200}, device_scale_factor=2)
            page.goto(html_path.as_uri(), wait_until="load")
            page.wait_for_timeout(1200)
            sleep(0.5)
            for out_path in out_paths:
                page.screenshot(path=str(out_path), full_page=False)
            page.close()
        browser.close()

    for _, image_name in targets:
        for out_path in (
            post_dir / "images" / image_name,
            draft_images_dir / image_name,
        ):
            print(out_path)
            print(out_path.stat().st_size)


if __name__ == "__main__":
    main()
