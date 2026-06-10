"""
Generate realistic avatar images for podcast speakers.
Uses PIL to draw clean portrait-style avatars with distinct looks.
Run once: python create_avatars.py
"""

from PIL import Image, ImageDraw, ImageFont
import os

OUTPUT = "avatars"
os.makedirs(OUTPUT, exist_ok=True)

SIZE = (512, 512)

SPEAKERS = {
    "Alex": {
        "skin": (255, 220, 185),
        "hair": (60, 40, 20),
        "shirt": (70, 130, 180),
        "eye": (80, 60, 40),
        "label_color": (70, 130, 180),
    },
    "Sam": {
        "skin": (240, 195, 160),
        "hair": (180, 120, 60),
        "shirt": (180, 60, 80),
        "eye": (60, 100, 140),
        "label_color": (180, 60, 80),
    },
    "Jordan": {
        "skin": (200, 160, 120),
        "hair": (30, 20, 10),
        "shirt": (60, 160, 100),
        "eye": (80, 60, 30),
        "label_color": (60, 160, 100),
    },
    "Casey": {
        "skin": (255, 235, 210),
        "hair": (220, 180, 100),
        "shirt": (140, 80, 180),
        "eye": (100, 140, 80),
        "label_color": (140, 80, 180),
    },
    "Host": {
        "skin": (255, 220, 185),
        "hair": (80, 60, 40),
        "shirt": (50, 100, 160),
        "eye": (70, 90, 120),
        "label_color": (50, 100, 160),
    },
}


def draw_avatar(name, cfg):
    img = Image.new("RGB", SIZE, (20, 20, 35))
    d = ImageDraw.Draw(img)

    W, H = SIZE
    cx = W // 2

    skin = cfg["skin"]
    hair = cfg["hair"]
    shirt = cfg["shirt"]
    eye_c = cfg["eye"]

    # Background gradient effect
    for i in range(H):
        alpha = int(30 + (i / H) * 20)
        d.line([(0, i), (W, i)], fill=(alpha, alpha, alpha + 10))

    # Subtle glow behind head
    for r in range(160, 100, -5):
        a = int(255 * (1 - (r - 100) / 60) * 0.08)
        glow = tuple(min(255, c + a) for c in (20, 20, 35))
        d.ellipse([cx - r, 120 - r + 180, cx + r, 120 + r + 180], fill=glow)

    # Shirt / body
    d.ellipse([cx - 130, 370, cx + 130, 560], fill=shirt)
    d.rectangle([cx - 130, 430, cx + 130, 512], fill=shirt)

    # Neck
    d.rectangle([cx - 28, 330, cx + 28, 390], fill=skin)

    # Hair (back)
    d.ellipse([cx - 105, 145, cx + 105, 345], fill=hair)

    # Head
    d.ellipse([cx - 100, 155, cx + 100, 340], fill=skin)

    # Hair (top/front)
    d.ellipse([cx - 105, 145, cx + 105, 230], fill=hair)
    # Side hair
    d.ellipse([cx - 110, 160, cx - 80, 280], fill=hair)
    d.ellipse([cx + 80, 160, cx + 110, 280], fill=hair)

    # Ears
    d.ellipse([cx - 115, 220, cx - 90, 265], fill=skin)
    d.ellipse([cx + 90, 220, cx + 115, 265], fill=skin)

    # Eyes - whites
    d.ellipse([cx - 65, 225, cx - 25, 260], fill=(255, 255, 255))
    d.ellipse([cx + 25, 225, cx + 65, 260], fill=(255, 255, 255))

    # Iris
    d.ellipse([cx - 55, 230, cx - 35, 255], fill=eye_c)
    d.ellipse([cx + 35, 230, cx + 55, 255], fill=eye_c)

    # Pupils
    d.ellipse([cx - 50, 234, cx - 40, 251], fill=(10, 10, 10))
    d.ellipse([cx + 40, 234, cx + 50, 251], fill=(10, 10, 10))

    # Eye shine
    d.ellipse([cx - 48, 235, cx - 44, 239], fill=(255, 255, 255))
    d.ellipse([cx + 42, 235, cx + 46, 239], fill=(255, 255, 255))

    # Eyebrows
    d.arc([cx - 68, 210, cx - 22, 235], start=200, end=340, fill=hair, width=4)
    d.arc([cx + 22, 210, cx + 68, 235], start=200, end=340, fill=hair, width=4)

    # Nose
    d.ellipse([cx - 12, 268, cx + 12, 290], fill=tuple(max(0, c - 20) for c in skin))
    d.arc([cx - 18, 278, cx + 18, 300], start=0, end=180, fill=tuple(max(0, c - 30) for c in skin), width=2)

    # Mouth - smile
    d.arc([cx - 30, 295, cx + 30, 325], start=10, end=170, fill=(180, 80, 80), width=3)
    # Lips
    d.arc([cx - 28, 296, cx + 28, 316], start=10, end=170, fill=(200, 100, 100), width=2)

    # Collar
    d.polygon([
        (cx - 30, 385), (cx, 410), (cx + 30, 385),
        (cx + 50, 430), (cx - 50, 430)
    ], fill=tuple(max(0, c - 20) for c in shirt))

    # Name label at bottom
    label = name
    # Draw name with simple rectangle background
    label_bg = cfg["label_color"]
    d.rectangle([cx - 80, 468, cx + 80, 500], fill=label_bg)

    # Try to use a font, fallback to default
    try:
        font = ImageFont.truetype("arial.ttf", 22)
    except Exception:
        font = ImageFont.load_default()

    # Center text
    bbox = d.textbbox((0, 0), label, font=font)
    tw = bbox[2] - bbox[0]
    th = bbox[3] - bbox[1]
    d.text((cx - tw // 2, 484 - th // 2), label, fill=(255, 255, 255), font=font)

    # Microphone icon hint
    d.ellipse([cx - 12, 440, cx + 12, 462], fill=(200, 200, 200))
    d.rectangle([cx - 5, 462, cx + 5, 472], fill=(200, 200, 200))
    d.arc([cx - 14, 462, cx + 14, 478], start=0, end=180, fill=(200, 200, 200), width=2)

    out_path = os.path.join(OUTPUT, f"{name}.png")
    img.save(out_path)
    print(f"  Created: {out_path}")
    return out_path


if __name__ == "__main__":
    print("Generating avatars...")
    for name, cfg in SPEAKERS.items():
        draw_avatar(name, cfg)
    print(f"\nDone! Avatars saved to '{OUTPUT}/' folder.")
    print("You can replace these with real photos for better results.")
