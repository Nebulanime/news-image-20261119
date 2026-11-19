# news-image-20261119 — Sum up 19 November 2026's world news in one image.
#
# A deterministic, network-free program: it draws a 1024x1024 newspaper-style
# infographic with Pillow and writes it to /output/entry.png.
# Running it twice produces byte-identical output (fixed strings, fixed fonts,
# no timestamps, no randomness, no network).
#
# Run:  python3 main.py
# Requires: Pillow (PIL). Standard library otherwise.

import hashlib
import os

from PIL import Image, ImageDraw, ImageFont

W, H = 1024, 1024
OUT = "/output/entry.png"

PAPER = (247, 243, 234)      # warm newsprint
INK = (22, 26, 36)
NAVY = (27, 51, 92)
NAVY_DARK = (18, 36, 68)
RED = (178, 34, 34)
GOLD = (176, 92, 14)
GREY = (104, 109, 122)
SOFT = (58, 64, 78)
LINE = (196, 193, 184)
SKY = (205, 224, 238)
SUN = (232, 164, 48)

FONT_DIR = "/usr/share/fonts/truetype/dejavu"


def _load(name, size):
    try:
        return ImageFont.truetype(os.path.join(FONT_DIR, name), size)
    except Exception:
        return ImageFont.load_default()


def serif_b(size):
    return _load("DejaVuSerif-Bold.ttf", size)


def serif(size):
    return _load("DejaVuSerif.ttf", size)


def sans(size):
    return _load("DejaVuSans.ttf", size)


def sans_b(size):
    return _load("DejaVuSans-Bold.ttf", size)


def wrap(draw, text, fnt, max_w):
    words = text.split()
    lines = []
    cur = ""
    for word in words:
        trial = (cur + " " + word).strip()
        if draw.textlength(trial, font=fnt) <= max_w:
            cur = trial
        else:
            if cur:
                lines.append(cur)
            cur = word
    if cur:
        lines.append(cur)
    return lines


def para(draw, x, y, text, fnt, fill, max_w, leading):
    for line in wrap(draw, text, fnt, max_w):
        draw.text((x, y), line, font=fnt, fill=fill)
        y += leading
    return y


def centred(draw, cx, y, text, fnt, fill):
    w = draw.textlength(text, font=fnt)
    draw.text((cx - w / 2, y), text, font=fnt, fill=fill)


def rule(draw, x0, x1, y, fill, width=1):
    draw.line([(x0, y), (x1, y)], fill=fill, width=width)


def draw_flag_us(draw, x, y, w, h):
    draw.rectangle([x, y, x + w, y + h], fill=(255, 255, 255), outline=INK)
    stripe = h / 13.0
    for i in range(0, 13, 2):
        draw.rectangle([x, y + i * stripe, x + w, y + (i + 1) * stripe],
                       fill=RED)
    cw, ch = w * 0.4, h * 7 / 13.0
    draw.rectangle([x, y, x + cw, y + ch], fill=NAVY)


def draw_flag_cn(draw, x, y, w, h):
    draw.rectangle([x, y, x + w, y + h], fill=(222, 41, 16), outline=INK)
    draw.ellipse([x + 6, y + 5, x + 14, y + 13], fill=(255, 222, 0))
    for sx, sy in [(28, 6), (36, 12), (36, 22), (28, 28)]:
        draw.ellipse([x + sx, y + sy, x + sx + 5, y + sy + 5],
                     fill=(255, 222, 0))


def draw_flag_ru(draw, x, y, w, h):
    draw.rectangle([x, y, x + w, y + h], fill=(255, 255, 255), outline=INK)
    draw.rectangle([x, y + h / 3, x + w, y + 2 * h / 3], fill=(0, 57, 166))
    draw.rectangle([x, y + 2 * h / 3, x + w, y + h], fill=(213, 0, 0))


def draw_skyline(draw, x0, x1, base, heights, fill):
    n = len(heights)
    span = x1 - x0
    bw = span / n
    for i, hh in enumerate(heights):
        bx = x0 + i * bw
        draw.rectangle([bx + 1, base - hh, bx + bw - 1, base], fill=fill)
        # tiny lit windows
        for wy in range(int(base - hh + 6), int(base - 4), 12):
            draw.rectangle([bx + 4, wy, bx + 7, wy + 5], fill=GOLD)


def main():
    img = Image.new("RGB", (W, H), PAPER)
    d = ImageDraw.Draw(img)
    M = 36
    CW = W - 2 * M

    # ---- masthead ----
    d.rectangle([0, 0, W, 108], fill=NAVY)
    centred(d, W / 2, 16, "THE WORLD IN ONE IMAGE", serif_b(50), (255, 255, 255))
    centred(d, W / 2, 72, "THURSDAY  ·  19 NOVEMBER 2026", sans_b(20), GOLD)
    d.rectangle([0, 108, W, 113], fill=RED)

    y = 132
    # ---- lead story ----
    d.text((M, y), "LEAD STORY  —  SHENZHEN, CHINA", font=sans_b(19), fill=RED)
    y += 28
    y = para(d, M, y, "Trump, Xi and Putin meet in Shenzhen",
             serif_b(42), INK, CW, 50)
    y += 4
    y = para(d, M, y,
             "The first trilateral of the three sitting presidents — Ukraine, "
             "Iran, nuclear stability and trade on the table on the APEC sidelines.",
             sans(21), SOFT, CW, 28)
    y += 8

    # ---- illustration: sky, sun, skyline, three flags ----
    band_y = y
    band_h = 100
    d.rectangle([M, band_y, W - M, band_y + band_h], fill=SKY)
    d.ellipse([W - M - 104, band_y + 14, W - M - 36, band_y + 82], fill=SUN)
    draw_skyline(d, M + 260, W - M - 116, band_y + band_h,
                 [42, 60, 52, 78, 48, 68, 56, 82, 46, 66], NAVY_DARK)
    flags = [(draw_flag_us, 52), (draw_flag_cn, 124), (draw_flag_ru, 196)]
    for fn, fx in flags:
        d.line([(fx + 29, band_y + 12), (fx + 29, band_y + band_h)],
               fill=INK, width=2)
        fn(d, fx, band_y + 12, 58, 34)
    d.rectangle([M, band_y + band_h, W - M, band_y + band_h + 3], fill=GOLD)
    y = band_y + band_h + 8
    centred(d, W / 2, y, "SHENZHEN  —  THE THREE PRESIDENTS, TOGETHER FOR THE FIRST TIME",
            sans_b(13), GREY)
    y += 22

    # ---- lead body ----
    y = para(d, M, y,
             "The three leaders met as a trio for the first time in history, on "
             "the sidelines of the APEC summit. Shenzhen hosted the talks — and "
             "the world watched for signals on war, trade and the nuclear balance.",
             sans(18), INK, CW, 26)
    y += 8
    rule(d, M, W - M, y, INK, 2)
    rule(d, M, W - M, y + 5, INK, 1)
    y += 14

    # ---- section header ----
    d.text((M, y), "MORE FROM THE DAY", font=sans_b(20), fill=NAVY)
    rule(d, M + 250, W - M, y + 11, LINE, 2)
    y += 30

    # ---- six stories, two columns x three rows ----
    stories = [
        ("MIDDLE EAST", RED,
         "US and Iran trade fire again",
         "Tehran widens its attacks to Kuwait and Bahrain as the exchange escalates."),
        ("EUROPE", NAVY,
         "EU proposes a €45bn loan for Ukraine",
         "Repaid only once Russia pays reparations, under the bloc's new plan."),
        ("GAMES", GOLD,
         "GTA VI begins its global rollout",
         "After a 13-year wait, the most anticipated game in history launches."),
        ("MARKETS", NAVY,
         "Nvidia pledges earlier pay rises",
         "The acting CEO's promise lands as the Fed signals more rate hikes."),
        ("WASHINGTON", RED,
         "Democrats nominate Hakeem Jeffries",
         "In line to become the first Black Speaker of the House."),
        ("SPACE", GOLD,
         "Voyager 1 reaches one light-day",
         "Humanity's farthest traveller passes a new milestone from Earth."),
    ]
    col_w = (CW - 24) // 2
    row_h = 96
    for i, (kick, col, head, summ) in enumerate(stories):
        cx = M + (i % 2) * (col_w + 24)
        cy = y + (i // 2) * (row_h + 8)
        d.text((cx, cy), kick, font=sans_b(14), fill=col)
        cy = para(d, cx, cy + 19, head, sans_b(19), INK, col_w, 21)
        para(d, cx, cy + 3, summ, sans(15), GREY, col_w, 17)
    y = y + 3 * row_h + 2 * 8 + 6

    # ---- ticker ----
    rule(d, M, W - M, y, GOLD, 2)
    y += 8
    d.text((M, y), "ALSO TODAY", font=sans_b(18), fill=RED)
    y += 24
    y = para(d, M, y,
             "Cyclone Akvan nears India's east coast  •  Australia sanctions "
             "Israeli settlers  •  Moldova summons Russia's envoy over drone "
             "incursions  •  Islam is on track to be the world's largest "
             "religion by 2035 (Pew)  •  Canada recalibrates its China ties",
             sans(16), INK, CW, 22)
    y += 12

    # ---- footer ----
    rule(d, M, W - M, y, LINE, 1)
    y += 8
    centred(d, W / 2, y, "Sources: Reuters  •  AP  •  BBC  •  Al Jazeera  •  Financial Times",
            sans(15), GREY)
    y += 20
    centred(d, W / 2, y, "19 November 2026  —  built for the make.fun bounty news-image-20261119",
            sans(14), GREY)
    y += 18
    assert y <= H - 4, "layout overflow: y=%d" % y

    os.makedirs(os.path.dirname(OUT), exist_ok=True)
    img.save(OUT, "PNG")
    data = open(OUT, "rb").read()
    print("wrote", OUT)
    print("size", img.size, "bytes", len(data))
    print("sha256", hashlib.sha256(data).hexdigest())


if __name__ == "__main__":
    main()
