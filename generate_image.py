#!/usr/bin/env python3
"""Draw entry.png for the news-image-20261125 competition.

An editorial front page for Wednesday 25 November 2026: a serif
masthead naming the day, one dark hero panel on the Strait of Hormuz
with a ship-traffic bar chart, and four number-led story cards.
Every fact and figure was checked against Reuters, CNN, Arab News
and Al Jazeera reporting dated 25 November 2026.

Build-time only (Pillow); the graded program is main.py, which copies
the finished PNG. Rendering is deterministic: fixed layout, fixed
text, no clock, no randomness.
"""

from pathlib import Path

from PIL import Image, ImageDraw, ImageFont

HERE = Path(__file__).resolve().parent

# ---------------------------------------------------------------- canvas
W = H = 1024
MARGIN = 48
CONTENT_W = W - 2 * MARGIN

PAPER = (246, 241, 231)
INK = (28, 26, 22)
FAINT_INK = (96, 90, 78)
CARD_BG = (252, 250, 244)
HERO_BG = (20, 32, 43)
HERO_TEXT = (243, 238, 227)
HERO_FAINT = (168, 182, 196)
BRICK = (179, 64, 42)
BAR_HI = (127, 179, 200)
BAR_LO = (240, 166, 120)

FONT_DIR = Path("/usr/share/fonts/truetype/noto")
SERIF_DISPLAY_BOLD = FONT_DIR / "NotoSerifDisplay-Bold.ttf"
SERIF_BOLD = FONT_DIR / "NotoSerif-Bold.ttf"
SERIF_REG = FONT_DIR / "NotoSerif-Regular.ttf"
SANS_BOLD = FONT_DIR / "NotoSans-Bold.ttf"
SANS_SEMI = FONT_DIR / "NotoSans-SemiBold.ttf"
SANS_REG = FONT_DIR / "NotoSans-Regular.ttf"

_fonts = {}


def font(path: Path, size: int) -> ImageFont.FreeTypeFont:
    key = (str(path), size)
    if key not in _fonts:
        _fonts[key] = ImageFont.truetype(str(path), size)
    return _fonts[key]


def text_w(draw: ImageDraw.ImageDraw, s: str, f: ImageFont.FreeTypeFont) -> float:
    return draw.textlength(s, font=f)


def wrap(draw, s: str, f, max_w: float) -> list[str]:
    """Greedy word wrap measured with the real font metrics."""
    lines, cur = [], ""
    for word in s.split():
        trial = word if not cur else cur + " " + word
        if text_w(draw, trial, f) <= max_w:
            cur = trial
        else:
            if cur:
                lines.append(cur)
            cur = word
    if cur:
        lines.append(cur)
    return lines


def draw_block(draw, x, y, s, f, fill, max_w, leading):
    """Draw wrapped text; returns the y just below the block."""
    for line in wrap(draw, s, f, max_w):
        draw.text((x, y), line, font=f, fill=fill)
        y += leading
    return y


def letterspaced(draw, x, y, s, f, fill, tracking=3):
    """Draw small-caps style text with manual letter tracking."""
    for ch in s:
        draw.text((x, y), ch, font=f, fill=fill)
        x += text_w(draw, ch, f) + tracking
    return x - tracking


def letterspaced_w(draw, s, f, tracking=3) -> float:
    return sum(text_w(draw, ch, f) + tracking for ch in s) - tracking


def draw_numeral(draw, x, y, s, f, fill, size):
    """Draw a big numeral. A leading hyphen is drawn as a proper minus
    bar, tight against the digits (the font's hyphen glyph is a short
    thin dash that reads as detached). Returns the ink right edge."""
    if s.startswith("-"):
        rest = s[1:]
        bb = draw.textbbox((0, 0), rest, font=f)
        ink_h = bb[3] - bb[1]
        bar_w = round(size * 0.40)
        bar_h = max(4, round(ink_h * 0.14))
        mid = y + (bb[1] + bb[3]) / 2
        draw.rectangle([x, mid - bar_h / 2, x + bar_w, mid + bar_h / 2],
                       fill=fill)
        dx = x + bar_w + 3
        draw.text((dx, y), rest, font=f, fill=fill)
        return dx + bb[2]
    bb = draw.textbbox((0, 0), s, font=f)
    draw.text((x, y), s, font=f, fill=fill)
    return x + bb[2]


# ---------------------------------------------------------------- masthead
def paint_masthead(draw) -> int:
    y = 24
    kick = font(SANS_BOLD, 20)
    left = "WORLD NEWS"
    right = "ONE DAY · ONE IMAGE"
    letterspaced(draw, MARGIN, y, left, kick, BRICK)
    rw = letterspaced_w(draw, right, kick)
    letterspaced(draw, W - MARGIN - rw, y, right, kick, FAINT_INK)
    y += 29

    date_font = font(SERIF_DISPLAY_BOLD, 58)
    date = "Wednesday 25 November 2026"
    dw = text_w(draw, date, date_font)
    draw.text(((W - dw) / 2, y), date, font=date_font, fill=INK)
    y += 70

    sub = font(SERIF_REG, 23)
    line = "The day's most consequential stories, drawn on one page"
    lw = text_w(draw, line, sub)
    draw.text(((W - lw) / 2, y), line, font=sub, fill=FAINT_INK)
    y += 32

    # double rule, newspaper style
    draw.line([(MARGIN, y), (W - MARGIN, y)], fill=INK, width=3)
    draw.line([(MARGIN, y + 7), (W - MARGIN, y + 7)], fill=INK, width=1)
    return y + 20


# ---------------------------------------------------------------- hero
def paint_hero(draw, top: int) -> int:
    height = 334
    draw.rectangle([MARGIN, top, W - MARGIN, top + height], fill=HERO_BG)
    pad = 36
    x0 = MARGIN + pad
    chart_x = 616
    text_w_max = chart_x - x0 - 28

    y = top + 24
    letterspaced(draw, x0, y, "STRAIT OF HORMUZ · MIDDLE EAST",
                 font(SANS_BOLD, 19), BAR_LO)
    y += 30

    headline = font(SERIF_BOLD, 40)
    y = draw_block(draw, x0, y,
                   "Iran orders Hormuz shut \u201cfurther day by day\u201d",
                   headline, HERO_TEXT, text_w_max, 51)
    y += 9

    stand = font(SANS_REG, 19)
    y = draw_block(
        draw, x0, y,
        "Tehran's army chief orders the navy to tighten the closure until "
        "Iran's seven conditions are met. The Revolutionary Guards say two "
        "more tankers hit mines at dawn on Wednesday.",
        stand, HERO_FAINT, text_w_max, 22)

    # --- ship-traffic chart, right column
    cx = chart_x
    cy = top + 24
    letterspaced(draw, cx, cy, "GULF SHIP TRAFFIC", font(SANS_BOLD, 18), HERO_TEXT)
    cy += 27
    cap = font(SANS_REG, 18)
    cy = draw_block(draw, cx, cy, "Vessels entering or leaving the Gulf",
                    cap, HERO_FAINT, W - MARGIN - pad - cx, 22)
    cy += 13

    bars = [("First week of November", 226, BAR_HI),
            ("17\u201323 November", 125, BAR_LO)]
    bar_max_w = 250
    label_f = font(SANS_SEMI, 19)
    num_f = font(SANS_BOLD, 28)
    for label, value, colour in bars:
        draw.text((cx, cy), label, font=label_f, fill=HERO_TEXT)
        cy += 26
        bw = bar_max_w * value / 226
        draw.rectangle([cx, cy, cx + bw, cy + 26], fill=colour)
        draw.text((cx + bw + 18, cy - 2), str(value), font=num_f, fill=HERO_TEXT)
        cy += 43

    cy += 5
    big = font(SERIF_DISPLAY_BOLD, 50)
    draw_numeral(draw, cx, cy, "-45%", big, BAR_LO, 50)
    cy += 56
    draw_block(draw, cx, cy, "traffic through the strait in a month",
               font(SANS_REG, 18), HERO_FAINT, W - MARGIN - pad - cx, 22)

    return top + height


# ---------------------------------------------------------------- cards
CARDS = [
    {
        "kicker": "MARKETS · ASIA",
        "numeral": "-5.8%",
        "headline": "Korea leads Asia's slide",
        "body": "Korean shares fell 5.8% and Taiwan's 4.7% on Wednesday as the "
                "Huang-return rally at Nvidia faded. Nvidia fell 6% Tuesday "
                "after Monday's 31.5% surge.",
    },
    {
        "kicker": "SPACE · CHINA",
        "numeral": "1st",
        "headline": "First Pakistani in orbit",
        "body": "China's Shenzhou-24 lifted off at 00:18 UTC carrying Muhammad "
                "Zeeshan Ali, 40 — the first foreign astronaut to board "
                "Tiangong. He stays about a week.",
    },
    {
        "kicker": "LABOUR · BANGLADESH",
        "numeral": "+36%",
        "headline": "Garment pay rise after protests",
        "body": "Bangladesh raised garment workers' minimum wage to 17,000 "
                "taka ($139) a month after weeks of protests — the smallest "
                "rise in over a decade.",
    },
    {
        "kicker": "CULTURE · PUERTO RICO",
        "numeral": "1st",
        "headline": "First mother crowned Miss Universe",
        "body": "Jennifer Barreto, 27, of Puerto Rico won the 75th Miss "
                "Universe in San Juan, beating 115 rivals — the first mother "
                "to take the crown since the rules changed in 2023.",
    },
]


def paint_card(draw, x, y, w, h, card):
    draw.rectangle([x, y, x + w, y + h], fill=CARD_BG, outline=INK, width=2)
    pad = 24
    inner_w = w - 2 * pad
    cy = y + 16

    letterspaced(draw, x + pad, cy, card["kicker"], font(SANS_BOLD, 17), BRICK)
    cy += 28

    # numeral and headline share one band; fixed ink-to-ink gutter
    num_f = font(SERIF_DISPLAY_BOLD, 50)
    ink_right = draw_numeral(draw, x + pad, cy, card["numeral"], num_f, INK, 50)
    head_x = ink_right + 20
    draw_block(draw, head_x, cy + 4, card["headline"],
               font(SERIF_BOLD, 25), INK, x + pad + inner_w - head_x, 33)
    cy += 70

    draw_block(draw, x + pad, cy, card["body"],
               font(SANS_REG, 17), FAINT_INK, inner_w, 20)


def paint_cards(draw, top: int) -> int:
    gutter = 14
    card_w = (CONTENT_W - gutter) // 2
    card_h = 218
    for i, card in enumerate(CARDS):
        cx = MARGIN + (i % 2) * (card_w + gutter)
        cy = top + (i // 2) * (card_h + gutter)
        paint_card(draw, cx, cy, card_w, card_h, card)
    return top + 2 * card_h + gutter


# ---------------------------------------------------------------- footer
def paint_footer(draw, top: int) -> None:
    y = top + 6
    draw.line([(MARGIN, y), (W - MARGIN, y)], fill=INK, width=1)
    y += 5
    note = font(SANS_REG, 17)
    left = "Sources: Reuters · CNN · Arab News · Al Jazeera (MarineTraffic data)"
    draw.text((MARGIN, y), left, font=note, fill=FAINT_INK)
    right = "Wednesday 25 November 2026"
    rw = text_w(draw, right, note)
    draw.text((W - MARGIN - rw, y), right, font=note, fill=FAINT_INK)


# ---------------------------------------------------------------- main
def main() -> None:
    img = Image.new("RGB", (W, H), PAPER)
    draw = ImageDraw.Draw(img)

    y = paint_masthead(draw)
    y = paint_hero(draw, y)
    y = paint_cards(draw, y + 13)
    paint_footer(draw, y)

    out = HERE / "entry.png"
    img.save(out, format="PNG", optimize=True)
    print(f"wrote {out} ({out.stat().st_size} bytes)")


if __name__ == "__main__":
    main()
