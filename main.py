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
import sys

from PIL import Image, ImageDraw, ImageFont

W, H = 1024, 1024

PAPER = (247, 243, 234)      # warm newsprint
INK = (17, 24, 39)
NAVY = (30, 58, 95)
NAVY_DARK = (23, 45, 76)
RED = (185, 28, 28)
GOLD = (180, 83, 9)
GREY = (100, 106, 118)
CARD = (255, 255, 255)
LINE = (203, 204, 198)
SKY = (214, 228, 240)
SEA = (96, 138, 170)

FONT_DIR = "/usr/share/fonts/truetype/dejavu"
F_BOLD = os.path.join(FONT_DIR, "DejaVuSans-Bold.ttf")
F_REG = os.path.join(FONT_DIR, "DejaVuSans.ttf")


def font(path, size):
    try:
        return ImageFont.truetype(path, size)
    except OSError:
        return ImageFont.load_default()


def wrap(draw, text, fnt, max_w):
    """Greedy word wrap returning a list of lines that fit max_w."""
    lines, cur = [], ""
    for word in text.split():
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


def draw_summit(draw, x0, y0, x1, y1):
    """Stylised Shenzhen skyline with three flags: US, China, Russia."""
    draw.rectangle([x0, y0, x1, y1], fill=SKY)
    # sun
    draw.ellipse([x1 - 52, y0 + 10, x1 - 18, y0 + 44], fill=(240, 196, 90))
    # skyline silhouettes
    towers = [(x0 + 10, 150, 46, 96), (x0 + 62, 120, 40, 126),
              (x0 + 108, 160, 52, 86), (x0 + 166, 104, 38, 142),
              (x0 + 210, 140, 44, 106), (x0 + 258, 118, 30, 128)]
    for tx, ty, tw, th in towers:
        draw.rectangle([tx, y0 + ty, tx + tw, y1 - 24], fill=(70, 90, 120))
    # windows
    for tx, ty, tw, th in towers:
        for wy in range(y0 + ty + 12, y1 - 36, 18):
            for wx in range(tx + 6, tx + tw - 6, 14):
                draw.rectangle([wx, wy, wx + 5, wy + 7], fill=(240, 196, 90))
    # ground strip
    draw.rectangle([x0, y1 - 24, x1, y1], fill=(23, 45, 76))
    # three flags on poles above the skyline
    poles = [(x0 + 40, "US"), (x0 + 148, "CN"), (x0 + 256, "RU")]
    flag_cols = {"US": [(178, 34, 52), (255, 255, 255), (60, 59, 110)],
                 "CN": [(222, 41, 16), (255, 222, 0), (222, 41, 16)],
                 "RU": [(255, 255, 255), (0, 57, 166), (213, 0, 50)]}
    for px, code in poles:
        draw.rectangle([px, y0 + 46, px + 3, y0 + 96], fill=INK)
        cols = flag_cols[code]
        for i, c in enumerate(cols):
            draw.rectangle([px + 3, y0 + 46 + i * 10, px + 33, y0 + 56 + i * 10],
                           fill=c)
    # caption
    cap = font(F_REG, 13)
    draw.text((x0 + 6, y1 - 20), "Shenzhen hosts the trilateral summit",
              font=cap, fill=(255, 255, 255))


STORIES = [
    ("GULF ON FIRE", "US and Iran trade fire as Tehran widens attacks",
     "US forces struck a missile site on Iran's Qeshm Island after Iran hit "
     "a US radar base in Bahrain. On 18 Nov Iran widened its attacks to a "
     "US base in Kuwait and struck Bahrain again."),
    ("EUROPE", "EU proposes \u20ac45bn Ukraine loan, Russia to pay",
     "The European Commission proposes a \u20ac45 billion loan to keep "
     "Ukraine's budget afloat, to be repaid after Russia pays reparations. "
     "EU leaders take up the plan on Wednesday."),
    ("CULTURE", "GTA VI begins global rollout after 13-year wait",
     "Gamers enter Vice City as Grand Theft Auto VI launches worldwide. "
     "After thirteen years of waiting, the release arrives with enormous "
     "hype and record expectations."),
    ("MARKETS", "Nvidia promises raises; Fed signals more hikes",
     "Nvidia's acting CEO Colette Kress promises earlier pay raises and "
     "more stock grants; Nvidia halts H-series chip shipments to China. "
     "Fed minutes show most officials expect further rate hikes."),
    ("US POLITICS", "Jeffries set to be first Black House Speaker",
     "Democrats nominate Hakeem Jeffries to be Speaker of the House. If "
     "confirmed, he becomes the first African-American Speaker in US "
     "history."),
    ("SPACE", "Voyager 1 reaches one light-day from Earth",
     "After almost 50 years in space, NASA's Voyager 1 probe is believed "
     "to have reached a light-day from Earth \u2014 about 26 billion km "
     "away. NASA confirms the milestone on Thursday."),
]

TICKER = ("ALSO TODAY:  Cyclone Akvan nears India's east coast  \u2022  "
         "Australia sanctions Israeli settlers over West Bank expansion  "
         "\u2022  Moldova summons Russia's envoy over drone incursions  "
         "\u2022  Islam on track to be the world's largest religion by 2035, "
         "Pew finds  \u2022  Canada recalibrates China ties, Carney says")


def build():
    img = Image.new("RGB", (W, H), PAPER)
    d = ImageDraw.Draw(img)

    # ---- masthead -------------------------------------------------------
    d.rectangle([0, 0, W, 96], fill=NAVY)
    d.rectangle([0, 96, W, 100], fill=GOLD)
    mast = font(F_BOLD, 34)
    d.text((28, 26), "THE WORLD IN ONE IMAGE", font=mast, fill=(255, 255, 255))
    date_f = font(F_BOLD, 18)
    date_txt = "THURSDAY  \u00b7  19 NOVEMBER 2026"
    d.text((W - 28 - d.textlength(date_txt, font=date_f), 34),
           date_txt, font=date_f, fill=(240, 196, 90))

    # ---- lead story -----------------------------------------------------
    lx, ly = 28, 116
    kick = font(F_BOLD, 16)
    d.text((lx, ly), "LEAD STORY  \u2014  GREAT-POWER SUMMIT", font=kick, fill=RED)
    head = font(F_BOLD, 46)
    d.text((lx, ly + 28), "TRUMP, XI AND PUTIN", font=head, fill=INK)
    d.text((lx, ly + 80), "MEET IN SHENZHEN", font=head, fill=INK)
    deck = font(F_REG, 16)
    deck_lines = wrap(
        d,
        "The first-ever trilateral of sitting US, Russian and Chinese "
        "presidents meets on the APEC sidelines. Ukraine, Iran, nuclear "
        "stability and trade are on the table \u2014 but no deal is expected.",
        deck, 640)
    y = ly + 142
    for line in deck_lines:
        d.text((lx, y), line, font=deck, fill=(51, 58, 70))
        y += 24

    # summit illustration, right of the lead text
    draw_summit(d, 700, 118, 996, 330)

    d.line([28, 344, 996, 344], fill=INK, width=2)

    # ---- story grid -----------------------------------------------------
    gx, gy = 28, 358
    col_w, row_h, gap = 476, 164, 16
    kicker_f = font(F_BOLD, 13)
    head_f = font(F_BOLD, 19)
    body_f = font(F_REG, 13)
    for i, (kicker, headline, body) in enumerate(STORIES):
        col, row = i % 2, i // 2
        x0 = gx + col * (col_w + gap)
        y0 = gy + row * (row_h + gap)
        d.rectangle([x0, y0, x0 + col_w, y0 + row_h], fill=CARD, outline=LINE, width=1)
        # number badge
        d.ellipse([x0 + 12, y0 + 12, x0 + 38, y0 + 38], fill=NAVY)
        num_f = font(F_BOLD, 15)
        n = str(i + 1)
        d.text((x0 + 25 - d.textlength(n, font=num_f) / 2, y0 + 16),
               n, font=num_f, fill=(255, 255, 255))
        d.text((x0 + 48, y0 + 14), kicker, font=kicker_f, fill=RED)
        hl = wrap(d, headline, head_f, col_w - 24)
        hy = y0 + 42
        for line in hl[:2]:
            d.text((x0 + 12, hy), line, font=head_f, fill=INK)
            hy += 24
        bl = wrap(d, body, body_f, col_w - 24)
        by = hy + 4
        for line in bl[:4]:
            d.text((x0 + 12, by), line, font=body_f, fill=(51, 58, 70))
            by += 19

    # ---- ticker ---------------------------------------------------------
    ty = 884
    d.rectangle([0, ty, W, ty + 68], fill=NAVY_DARK)
    tick_f = font(F_REG, 15)
    tick_lines = wrap(d, TICKER, tick_f, W - 56)
    yy = ty + 10
    for line in tick_lines:
        d.text((28, yy), line, font=tick_f, fill=(255, 255, 255))
        yy += 20

    # ---- footer ---------------------------------------------------------
    foot_f = font(F_REG, 13)
    foot = ("Sources: Reuters \u00b7 AP \u00b7 BBC \u00b7 Al Jazeera \u00b7 Financial Times \u2014 "
            "summary of verified reports published 19 November 2026.")
    d.text(((W - d.textlength(foot, font=foot_f)) / 2, 964), foot,
           font=foot_f, fill=GREY)
    foot2 = "Built for make.fun bounty news-image-20261119  \u00b7  One image, one day of world news."
    d.text(((W - d.textlength(foot2, font=foot_f)) / 2, 986), foot2,
           font=foot_f, fill=GREY)

    return img


def main():
    img = build()
    out = "/output/entry.png"
    try:
        os.makedirs("/output", exist_ok=True)
    except OSError:
        out = os.path.join(os.path.dirname(os.path.abspath(__file__)),
                           "output", "entry.png")
        os.makedirs(os.path.dirname(out), exist_ok=True)
    img.save(out, format="PNG", optimize=True)
    size = os.path.getsize(out)
    assert img.size == (1024, 1024), img.size
    assert size <= 1024 * 1024, size
    with open(out, "rb") as fh:
        digest = hashlib.sha256(fh.read()).hexdigest()
    print(f"wrote {out} ({img.size[0]}x{img.size[1]}, {size} bytes, sha256 {digest})")


if __name__ == "__main__":
    main()
