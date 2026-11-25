#!/usr/bin/env python3
"""Draw entry.png: one image summing up 25 November 2026 world news.

Broadsheet-dashboard layout in the style of past news-image winners:
masthead, region chips, UTC timeline, numbers strip, three illustrated
leads, a card grid, an "also on" long-tail list, a dotted world map with
numbered pins, credibility badges and a DATE CHECK footer.

Every story below happened or was first reported on 25 November 2026
(UTC), verified against the named sources on the day. Deterministic:
no randomness, no clock, no network — two runs write identical bytes.
"""

from PIL import Image, ImageDraw, ImageFont

W = H = 1024
MARGIN = 14
CW = W - 2 * MARGIN  # content width: 996

FONT_DIR = "/usr/share/fonts/truetype/noto/"
FONTS = {
    "mast": "NotoSerifDisplay-Black.ttf",
    "serif_b": "NotoSerif-Bold.ttf",
    "serif": "NotoSerif-Regular.ttf",
    "serif_i": "NotoSerif-Italic.ttf",
    "sans": "NotoSans-Regular.ttf",
    "sans_b": "NotoSans-Bold.ttf",
    "sans_m": "NotoSans-Medium.ttf",
    "sans_sb": "NotoSans-SemiBold.ttf",
}
_cache = {}


def font(key, size):
    k = (key, size)
    if k not in _cache:
        _cache[k] = ImageFont.truetype(FONT_DIR + FONTS[key], size)
    return _cache[k]


# ---------------------------------------------------------------- palette
PAPER = (247, 243, 234)
INK = (26, 26, 26)
NAVY = (20, 33, 61)
NAVY2 = (27, 42, 74)
RED = (179, 58, 43)
GRAY = (110, 110, 110)
LGRAY = (150, 150, 150)
LINE = (60, 60, 60)
WHITE = (255, 255, 255)
CREAM = (252, 250, 244)

REGION_COLORS = {
    "EUROPE": (51, 102, 170),
    "MIDDLE EAST": (198, 93, 33),
    "EAST ASIA": (46, 139, 110),
    "SOUTH ASIA": (140, 160, 50),
    "SE ASIA": (30, 160, 160),
    "AFRICA": (125, 60, 152),
    "AMERICAS": (176, 58, 46),
    "OCEANIA": (40, 116, 166),
    "WORLD": (85, 85, 85),
}
REGION_ORDER = ["EUROPE", "MIDDLE EAST", "EAST ASIA", "SOUTH ASIA", "SE ASIA",
                "AFRICA", "AMERICAS", "OCEANIA"]

BADGE_COLORS = {
    "CONFIRMED": (30, 132, 73),
    "OFFICIAL": (46, 90, 136),
    "REPORTED": (110, 110, 110),
    "CLAIM": (176, 58, 46),
    "ONGOING": (183, 121, 31),
}

# ---------------------------------------------------------------- stories
# n, region, loc (kicker), badge, headline, summary, source, illus, (lon, lat)
LEADS = [
    dict(n=1, region="MIDDLE EAST", loc="STRAIT OF HORMUZ", badge="CONFIRMED",
         head="Iran orders Hormuz shut \u201cfurther day by day\u201d",
         body="Tehran's army chief orders the navy to tighten the closure until "
              "seven conditions are met. Guards say two tankers hit mines at "
              "dawn on Wednesday.",
         src="Reuters \u00b7 CNN \u00b7 Arab News \u00b7 Al Jazeera",
         illus="hormuz", pin=(56.3, 26.6)),
    dict(n=2, region="EAST ASIA", loc="SEOUL \u00b7 TAIPEI \u00b7 TOKYO", badge="CONFIRMED",
         head="Asia slides: Korea -5.8% as AI rout deepens",
         body="Korean shares fell 5.8% and Taiwan's 4.7% on Wednesday as the "
              "Nvidia rally faded. Nvidia dropped 6% on Tuesday after Monday's "
              "31.5% surge.",
         src="Reuters \u00b7 Bloomberg \u00b7 Nikkei",
         illus="markets", pin=(127.0, 37.5)),
    dict(n=3, region="EAST ASIA", loc="JIUQUAN \u00b7 TIANGONG", badge="OFFICIAL",
         head="First Pakistani in orbit on Shenzhou-24",
         body="China's Shenzhou-24 lifted off at 00:18 UTC carrying Muhammad "
              "Zeeshan Ali, 40 \u2014 the first foreign astronaut aboard "
              "Tiangong. He stays about a week.",
         src="Xinhua \u00b7 Reuters \u00b7 Dawn",
         illus="rocket", pin=(100.3, 41.0)),
]

GRID = [
    dict(n=4, region="MIDDLE EAST", loc="GAZA CITY \u00b7 WAR", badge="CONFIRMED",
         head="Dawn strike kills Gaza security chief",
         body="Israeli strike on al-Shati home kills security chief, wife and "
              "two daughters.",
         src="Al Jazeera \u00b7 AFP", illus="blast", pin=(34.3, 31.5)),
    dict(n=5, region="EUROPE", loc="KYIV \u00b7 WAR", badge="OFFICIAL",
         head="Russia fires 112 drones overnight",
         body="Air defences downed 88, Ukraine says; one killed near Kyiv, one "
              "in Kharkiv region.",
         src="Ukrinform", illus="drones", pin=(30.5, 50.4)),
    dict(n=6, region="EUROPE", loc="LONDON \u00b7 ENERGY", badge="OFFICIAL",
         head="UK energy cap to jump 26%",
         body="Ofgem raises the price cap to \u00a32,166 a year from January, "
              "up \u00a3443.",
         src="Ofgem \u00b7 Reuters", illus="bolt", pin=(-0.1, 51.5)),
    dict(n=7, region="AMERICAS", loc="CARTAGENA \u00b7 CRIME", badge="CONFIRMED",
         head="Hostages freed in supermarket raid",
         body="Forces stormed an Exito store after a 17-hour siege; about 20 "
              "hostages rescued.",
         src="AFP \u00b7 Reuters", illus="rescue", pin=(-75.5, 10.4)),
    dict(n=8, region="AFRICA", loc="CAPE TOWN \u00b7 COURTS", badge="CONFIRMED",
         head="Ramaphosa wins Farmgate court bid",
         body="Court sets aside the 2022 panel report on the Phala Phala cash "
              "theft.",
         src="Reuters", illus="columns", pin=(18.4, -33.9)),
    dict(n=9, region="SOUTH ASIA", loc="DHAKA \u00b7 LABOUR", badge="OFFICIAL",
         head="Garment pay up 36% after protests",
         body="Minimum wage rises to 17,000 taka ($139) a month \u2014 smallest "
              "rise in a decade.",
         src="Reuters \u00b7 Dhaka Tribune", illus="factory", pin=(90.4, 23.8)),
    dict(n=10, region="AMERICAS", loc="SAN JUAN \u00b7 CULTURE", badge="CONFIRMED",
         head="First mother crowned Miss Universe",
         body="Jennifer Barreto, 27, of Puerto Rico won the 75th Miss Universe "
              "in San Juan.",
         src="AP \u00b7 Reuters", illus="crown", pin=(-66.1, 18.5)),
    dict(n=11, region="OCEANIA", loc="CANBERRA \u00b7 ECONOMY", badge="OFFICIAL",
         head="Australia inflation jumps to 4.9%",
         body="October CPI rose to 4.9%, up from 4.3% \u2014 above the bank's "
              "2-3% target.",
         src="ABS \u00b7 Reuters", illus="gauge", pin=(149.1, -35.3)),
    dict(n=12, region="MIDDLE EAST", loc="HODEIDAH \u00b7 WAR", badge="OFFICIAL",
         head="Coalition strikes Hodeidah port",
         body="Saudi-led coalition hit Houthi port targets and downed 4 drones "
              "over Ras Tanura.",
         src="Arab News \u00b7 Al Jazeera", illus="port", pin=(42.9, 14.8)),
    dict(n=13, region="EUROPE", loc="BRUSSELS \u00b7 TECH", badge="OFFICIAL",
         head="EU plans \u20ac50bn quantum fund",
         body="Commission proposes a sovereign tech fund to lead quantum by "
              "2030.",
         src="Reuters", illus="atom", pin=(4.4, 50.8)),
]

# Also-list: (n, region, place, text, source)
ALSO = [
    (14, "EAST ASIA", "Tokyo", "Tashima vows one term if he wins FIFA presidency", "Reuters"),
    (15, "SE ASIA", "Kuala Lumpur", "Malaysia sues Google for $146m over YouTube", "Reuters"),
    (16, "EAST ASIA", "Seoul", "Births jump 12.2% in September, record pace", "Yonhap"),
    (17, "OCEANIA", "Canberra", "Australia passes online-safety duty, 5% fines", "Reuters"),
    (18, "OCEANIA", "Canberra", "Solomons sign treaty, A$740m, no foreign base", "AFP"),
    (19, "SOUTH ASIA", "New Delhi", "Court defers bail for Khalid, Imam", "The Hindu"),
    (20, "SE ASIA", "Bangkok", "\u201cAem Cyanide\u201d sentenced to death", "Bangkok Post"),
    (21, "MIDDLE EAST", "Ajman", "Sri Lanka women win Emerging Nations Trophy", "ICC"),
    (22, "EUROPE", "Berlin", "Merz defends Ukraine aid, Russia \u201cescalating\u201d", "Reuters"),
    (23, "EUROPE", "London", "Met Police still institutionally racist: review", "Guardian"),
    (24, "EUROPE", "Samara", "Drone fires at two Rosneft refineries", "Ukrinform"),
    (25, "MIDDLE EAST", "Aden", "UN: 364,000 displaced in Yemen since August", "Al Jazeera"),
    (26, "AFRICA", "Centurion", "SA declare 494-7; Bangladesh trail by 294", "Reuters"),
    (27, "AFRICA", "Nairobi", "Steinmeier in Kenya; 9,500 Kenyans work in Germany", "The Star"),
    (28, "AFRICA", "Enugu", "Nollywood legend Pete Edochie dies aged 79", "Punch"),
    (29, "MIDDLE EAST", "Amman", "Court sentences man to death over officer's killing", "Reuters"),
    (30, "EUROPE", "Brussels", "Puigdemont to end exile, return to Spain Dec 12", "Reuters"),
    (31, "AMERICAS", "Middletown", "Army to detonate 5 tons of lead azide in Iowa", "AP"),
]

TIMELINE = [
    ("00:18", "Shenzhou-24 lifts off"),
    ("00:30", "Australia CPI 4.9%"),
    ("01:00", "Gaza dawn strike"),
    ("02:46", "Hodeidah port struck"),
    ("06:00", "Cartagena hostages freed"),
    ("07:14", "UK energy cap +26%"),
    ("08:34", "Ramaphosa court win"),
]

NUMBERS = [
    ("-45%", "Gulf ship traffic in a month"),
    ("364,000", "displaced in Yemen since August"),
    ("-5.8%", "Korea shares on Wednesday"),
    ("112", "drones fired at Ukraine overnight"),
    ("\u00a32,166", "UK energy cap from January"),
    ("+36%", "Bangladesh garment wage"),
]

DATE_CHECK = [
    "Hanoi hotpot gas blast (Tue 24 Nov)",
    "China probes Shanghai chief Chen Jining (24 Nov)",
    "Champions League Matchday 5 (Tue 24 Nov)",
    "Turkish helicopter crash, 5 killed (24 Nov)",
    "Huawei convicted in Brooklyn (24 Nov)",
]

# ---------------------------------------------------------------- helpers
def tw(f, s):
    return f.getlength(s)


def tracked(d, x, y, s, f, fill, tracking=1.2):
    cx = x
    for ch in s:
        d.text((cx, y), ch, font=f, fill=fill)
        cx += tw(f, ch) + tracking
    return cx - x - tracking


def tracked_w(f, s, tracking=1.2):
    return sum(tw(f, ch) + tracking for ch in s) - tracking


def wrap(s, f, max_w):
    words, lines, cur = s.split(), [], ""
    for wd in words:
        t = (cur + " " + wd).strip()
        if tw(f, t) <= max_w or not cur:
            cur = t
        else:
            lines.append(cur)
            cur = wd
    if cur:
        lines.append(cur)
    return lines


def badge(d, x, y, text):
    f = font("sans_b", 8)
    w = tracked_w(f, text, 0.6) + 10
    d.rounded_rectangle([x, y, x + w, y + 13], 3, outline=BADGE_COLORS[text],
                        width=1)
    tracked(d, x + 5, y + 2, text, f, BADGE_COLORS[text], 0.6)
    return w


def num_chip(d, x, y, n, color, r=9):
    d.ellipse([x, y, x + 2 * r, y + 2 * r], fill=color)
    f = font("sans_b", 10 if n < 10 else 8)
    s = str(n)
    d.text((x + r - tw(f, s) / 2, y + r - 6), s, font=f, fill=WHITE)


# ---------------------------------------------------------- illustrations
def ill_hormuz(d, b):
    x0, y0, x1, y1 = b
    d.rectangle(b, fill=(168, 205, 225))                     # sea
    d.polygon([(x0, y0), (x0 + 90, y0), (x0 + 55, y1 - 18), (x0, y1 - 18)],
              fill=(214, 190, 150))                          # Iran side
    d.polygon([(x1, y0), (x1 - 70, y0), (x1 - 40, y1 - 18), (x1, y1 - 18)],
              fill=(222, 200, 160))                          # Oman side
    # distant second tanker, higher in the channel
    dy = y0 + 34
    d.polygon([(x0 + 248, dy), (x0 + 292, dy), (x0 + 286, dy + 7),
               (x0 + 254, dy + 7)], fill=(90, 90, 100))
    d.rectangle([x0 + 262, dy - 6, x0 + 274, dy], fill=(70, 70, 80))
    sy = y1 - 34
    # wake trailing the main tanker
    for wy, wl in [(sy + 6, 46), (sy + 11, 34), (sy + 16, 24)]:
        d.line([x0 + 118 - wl, wy, x0 + 118, wy], fill=(240, 248, 252), width=2)
    d.polygon([(x0 + 120, sy), (x0 + 215, sy), (x0 + 205, sy + 12),
               (x0 + 130, sy + 12)], fill=(176, 58, 46))     # hull
    d.rectangle([x0 + 150, sy - 12, x0 + 175, sy], fill=(60, 60, 60))
    d.rectangle([x0 + 178, sy - 8, x0 + 192, sy], fill=(60, 60, 60))
    # naval mines: spiked spheres, one ringed in red
    import math
    for i, (mx, my) in enumerate([(x0 + 100, sy + 15), (x0 + 238, sy + 13),
                                  (x0 + 172, sy + 17)]):
        if i == 0:
            d.ellipse([mx - 10, my - 10, mx + 10, my + 10],
                      outline=(200, 40, 30), width=2)
        for ang in range(0, 360, 45):
            ex = mx + 8 * math.cos(math.radians(ang))
            ey = my + 8 * math.sin(math.radians(ang))
            d.line([mx, my, ex, ey], fill=(35, 35, 35), width=2)
        d.ellipse([mx - 5, my - 5, mx + 5, my + 5], fill=(35, 35, 35))
    f = font("sans_b", 10)
    d.rectangle([x0 + 30, y0 + 8, x0 + 142, y0 + 24], fill=NAVY)
    d.text((x0 + 35, y0 + 11), "226", font=f, fill=WHITE)
    ax = x0 + 35 + tw(f, "226") + 3
    d.line([ax, y0 + 16, ax + 9, y0 + 16], fill=WHITE, width=2)
    d.polygon([(ax + 9, y0 + 13), (ax + 9, y0 + 19), (ax + 13, y0 + 16)],
              fill=WHITE)
    d.text((ax + 15, y0 + 11), "125 SHIPS", font=f, fill=WHITE)


def ill_markets(d, b):
    x0, y0, x1, y1 = b
    d.rectangle(b, fill=(24, 24, 34))
    pts = [(x0 + 30, y0 + 16), (x0 + 75, y0 + 24), (x0 + 120, y0 + 20),
           (x0 + 160, y0 + 38), (x0 + 195, y0 + 54), (x0 + 218, y0 + 68)]
    d.line(pts, fill=(231, 76, 60), width=3)
    for px, py in pts:
        d.ellipse([px - 3, py - 3, px + 3, py + 3], fill=(231, 76, 60))
    f1, f2 = font("sans_b", 11), font("sans_b", 12)
    rows = [("KOREA", "-5.8%"), ("TAIWAN", "-4.7%"),
            ("NVIDIA", "-6.0%")]
    ry = y0 + 10
    for name, val in rows:
        d.text((x1 - 118, ry), name, font=f1, fill=(220, 220, 220))
        d.text((x1 - tw(f2, val) - 10, ry - 1), val, font=f2, fill=(231, 76, 60))
        ry += 17


def ill_rocket(d, b):
    x0, y0, x1, y1 = b
    d.rectangle(b, fill=(16, 24, 48))
    for sx, sy in [(30, 14), (70, 30), (250, 12), (290, 34), (180, 10), (120, 40)]:
        d.ellipse([x0 + sx - 2, y0 + sy - 2, x0 + sx + 2, y0 + sy + 2],
                  fill=(230, 230, 230))
    d.pieslice([x0 - 40, y1 - 26, x1 + 40, y1 + 70], 180, 360, fill=(52, 110, 180))
    rx, ry = x0 + 150, y0 + 12
    d.polygon([(rx, ry), (rx + 9, ry + 16), (rx + 9, ry + 44), (rx - 9, ry + 44),
               (rx - 9, ry + 16)], fill=(235, 235, 235))
    d.ellipse([rx - 4, ry + 18, rx + 4, ry + 26], fill=(52, 110, 180))
    d.polygon([(rx - 9, ry + 36), (rx - 18, ry + 50), (rx - 9, ry + 50)],
              fill=(231, 76, 60))
    d.polygon([(rx + 9, ry + 36), (rx + 18, ry + 50), (rx + 9, ry + 50)],
              fill=(231, 76, 60))
    d.polygon([(rx - 5, ry + 44), (rx + 5, ry + 44), (rx, ry + 58)],
              fill=(243, 156, 18))
    sx2, sy2 = x0 + 235, y0 + 26
    d.rectangle([sx2 - 16, sy2 - 4, sx2 + 16, sy2 + 4], fill=(200, 200, 200))
    d.rectangle([sx2 - 26, sy2 - 8, sx2 - 16, sy2 + 8], fill=(52, 110, 180))
    d.rectangle([sx2 + 16, sy2 - 8, sx2 + 26, sy2 + 8], fill=(52, 110, 180))
    d.arc([x0 + 60, y0 + 6, x1 - 30, y1 - 6], 200, 340, fill=(150, 180, 220), width=1)
    f = font("sans_b", 10)
    d.rectangle([x0 + 30, y0 + 8, x0 + 118, y0 + 24], fill=(243, 156, 18))
    d.text((x0 + 35, y0 + 11), "00:18 UTC", font=f, fill=(30, 30, 30))


def ill_factory(d, b):
    x0, y0, x1, y1 = b
    d.rectangle(b, fill=(240, 230, 210))
    # chimneys with smoke
    for chx in (x0 + 26, x0 + 48):
        d.rectangle([chx, y0 + 10, chx + 9, y1 - 28], fill=(110, 110, 110))
        d.ellipse([chx - 3, y0 + 2, chx + 7, y0 + 9], fill=(200, 200, 200))
        d.ellipse([chx + 2, y0 - 3, chx + 13, y0 + 4], fill=(215, 215, 215))
    # sawtooth-roof factory hall
    base = y1 - 6
    d.rectangle([x0 + 16, y1 - 26, x0 + 122, base], fill=(150, 110, 70))
    d.polygon([(x0 + 16, y1 - 26), (x0 + 16, y1 - 38), (x0 + 42, y1 - 26),
               (x0 + 42, y1 - 38), (x0 + 68, y1 - 26), (x0 + 68, y1 - 38),
               (x0 + 94, y1 - 26), (x0 + 94, y1 - 38), (x0 + 122, y1 - 26)],
              fill=(120, 85, 55))
    for wx in (x0 + 24, x0 + 42, x0 + 60, x0 + 78, x0 + 96):
        d.rectangle([wx, y1 - 21, wx + 11, y1 - 12], fill=(250, 220, 130))
    d.rectangle([x0 + 16, base - 2, x0 + 122, base], fill=(110, 80, 50))
    f = font("sans_b", 13)
    d.text((x1 - tw(f, "+36%") - 10, y0 + 12), "+36%", font=f, fill=(30, 132, 73))


def ill_crown(d, b):
    x0, y0, x1, y1 = b
    d.rectangle(b, fill=(30, 30, 60))
    cx, cy = x0 + 52, (y0 + y1) // 2
    d.polygon([(cx - 26, cy + 8), (cx - 26, cy - 8), (cx - 13, cy),
               (cx, cy - 12), (cx + 13, cy), (cx + 26, cy - 8),
               (cx + 26, cy + 8)], fill=(243, 196, 52))
    d.rectangle([cx - 26, cy + 8, cx + 26, cy + 12], fill=(220, 170, 40))
    for jx in (cx - 15, cx, cx + 15):
        d.ellipse([jx - 2.5, cy + 2, jx + 2.5, cy + 7], fill=(231, 76, 60))
    f = font("sans_b", 11)
    d.text((x0 + 92, cy - 13), "75th", font=f, fill=(250, 230, 160))
    f2 = font("sans_b", 8.5)
    d.text((x0 + 92, cy + 1), "edition", font=f2, fill=(200, 190, 150))


def ill_treaty(d, b):
    x0, y0, x1, y1 = b
    d.rectangle(b, fill=(235, 240, 245))
    d.rectangle([x0 + 30, y0 + 8, x0 + 95, y1 - 8], fill=WHITE, outline=LINE)
    for ly in range(y0 + 16, y1 - 20, 6):
        d.line([x0 + 38, ly, x0 + 87, ly], fill=LGRAY, width=1)
    d.line([x0 + 38, y1 - 14, x0 + 62, y1 - 18], fill=NAVY, width=2)
    d.line([x1 - 30, y0 + 12, x0 + 70, y1 - 16], fill=(60, 60, 60), width=3)
    f = font("sans_b", 11)
    d.text((x1 - tw(f, "A$740m") - 8, y1 - 20), "A$740m", font=f, fill=NAVY)


def ill_shield(d, b):
    x0, y0, x1, y1 = b
    d.rectangle(b, fill=(225, 238, 250))
    cx, cy = x0 + 55, (y0 + y1) // 2
    d.polygon([(cx, cy - 18), (cx + 16, cy - 12), (cx + 16, cy + 4),
               (cx, cy + 18), (cx - 16, cy + 4), (cx - 16, cy - 12)],
              fill=(46, 90, 136))
    d.line([cx - 7, cy, cx - 2, cy + 6, cx + 8, cy - 6], fill=WHITE, width=3)
    f = font("sans_b", 11)
    d.text((x0 + 82, cy - 14), "5% of global", font=f, fill=NAVY)
    d.text((x0 + 82, cy + 2), "turnover fines", font=f, fill=NAVY)


def ill_gavel(d, b):
    x0, y0, x1, y1 = b
    d.rectangle(b, fill=(245, 238, 225))
    d.rectangle([x0 + 40, y1 - 12, x0 + 110, y1 - 6], fill=(120, 85, 55))
    d.line([x0 + 55, y1 - 14, x0 + 95, y0 + 14], fill=(140, 100, 60), width=5)
    d.rectangle([x0 + 88, y0 + 6, x0 + 112, y0 + 20], fill=(100, 70, 40))
    f = font("sans_b", 12)
    d.text((x1 - tw(f, "$146m") - 8, y0 + 10), "$146m", font=f, fill=RED)


def ill_gauge(d, b):
    x0, y0, x1, y1 = b
    d.rectangle(b, fill=(250, 244, 230))
    cx, cy, r = x0 + 55, y1 - 8, 34
    d.pieslice([cx - r, cy - r, cx + r, cy + r], 180, 270, fill=(46, 139, 110))
    d.pieslice([cx - r, cy - r, cx + r, cy + r], 270, 315, fill=(243, 196, 52))
    d.pieslice([cx - r, cy - r, cx + r, cy + r], 315, 360, fill=(231, 76, 60))
    d.pieslice([cx - r + 9, cy - r + 9, cx + r - 9, cy + r - 9], 180, 360,
               fill=(250, 244, 230))
    d.line([cx, cy, cx + 22, cy - 18], fill=INK, width=3)
    d.ellipse([cx - 4, cy - 4, cx + 4, cy + 4], fill=INK)
    f = font("sans_b", 14)
    d.text((x0 + 100, cy - 22), "4.9%", font=f, fill=RED)


def ill_bars_up(d, b):
    x0, y0, x1, y1 = b
    d.rectangle(b, fill=(235, 245, 240))
    base = y1 - 8
    for i, h in enumerate((12, 18, 24, 32)):
        bx = x0 + 26 + i * 26
        d.rectangle([bx, base - h, bx + 16, base], fill=(46, 139, 110))
    d.line([x0 + 20, y1 - 20, x0 + 130, y0 + 10], fill=(30, 132, 73), width=2)
    f = font("sans_b", 12)
    d.text((x1 - tw(f, "+12.2%") - 8, y0 + 8), "+12.2%", font=f, fill=(30, 132, 73))


def ill_scales(d, b):
    x0, y0, x1, y1 = b
    d.rectangle(b, fill=(240, 238, 232))
    cx = x0 + 60
    d.line([cx, y0 + 10, cx, y1 - 12], fill=(90, 90, 90), width=3)
    d.line([cx - 34, y0 + 16, cx + 34, y0 + 16], fill=(90, 90, 90), width=3)
    for sx in (cx - 34, cx + 34):
        d.line([sx, y0 + 16, sx - 10, y0 + 30], fill=(90, 90, 90), width=1)
        d.line([sx, y0 + 16, sx + 10, y0 + 30], fill=(90, 90, 90), width=1)
        d.pieslice([sx - 12, y0 + 26, sx + 12, y0 + 40], 0, 180, fill=(150, 120, 70))
    d.rectangle([cx - 14, y1 - 12, cx + 14, y1 - 7], fill=(90, 90, 90))
    f = font("sans_b", 10)
    d.text((x1 - tw(f, "UAPA") - 10, y1 - 22), "UAPA", font=f, fill=NAVY)


def ill_pill(d, b):
    x0, y0, x1, y1 = b
    d.rectangle(b, fill=(245, 235, 235))
    cx, cy = x0 + 55, (y0 + y1) // 2
    d.rounded_rectangle([cx - 26, cy - 9, cx + 26, cy + 9], 9, fill=WHITE,
                        outline=LINE, width=1)
    d.rounded_rectangle([cx, cy - 9, cx + 26, cy + 9], 9, fill=(231, 76, 60))
    d.rectangle([cx, cy - 9, cx + 10, cy + 9], fill=(231, 76, 60))
    f = font("sans_b", 10)
    d.text((x0 + 92, cy - 6), "15 cases", font=f, fill=RED)


def ill_cricket(d, b):
    x0, y0, x1, y1 = b
    d.rectangle(b, fill=(225, 242, 228))
    d.polygon([(x0 + 40, y1 - 6), (x0 + 58, y1 - 6), (x0 + 86, y0 + 12),
               (x0 + 74, y0 + 8)], fill=(210, 170, 110))
    d.ellipse([x0 + 100, y0 + 14, x0 + 116, y0 + 30], fill=(200, 40, 40))
    f = font("sans_b", 12)
    d.text((x1 - tw(f, "99/4") - 10, y1 - 22), "99/4", font=f, fill=(30, 110, 60))


def ill_blast(d, b):
    x0, y0, x1, y1 = b
    # dawn sky: dark band over an orange horizon
    d.rectangle(b, fill=(52, 44, 66))
    d.rectangle([x0, y1 - 20, x1, y1], fill=(196, 106, 52))
    # half-risen sun sitting on the horizon, behind the skyline
    cx, cy = x0 + 100, y1 - 14
    d.pieslice([cx - 15, cy - 15, cx + 15, cy + 15], 180, 360,
               fill=(255, 206, 100))
    # smoke plume from the struck building
    for px, py, pr in [(cx + 26, y1 - 34, 5), (cx + 30, y1 - 40, 6),
                       (cx + 35, y1 - 46, 7)]:
        d.ellipse([px - pr, py - pr, px + pr, py + pr], fill=(150, 145, 150))
    # skyline silhouette in front of the sun
    for bx, bh in [(14, 24), (44, 30), (76, 20), (108, 28), (140, 22),
                   (166, 26)]:
        d.rectangle([x0 + bx, y1 - bh, x0 + bx + 24, y1], fill=(26, 22, 36))
    f = font("sans_b", 10)
    d.text((x1 - tw(f, "01:00 UTC") - 8, y0 + 6), "01:00 UTC", font=f,
           fill=(255, 220, 120))


def ill_drones(d, b):
    x0, y0, x1, y1 = b
    d.rectangle(b, fill=(18, 24, 44))
    for sx, sy in [(24, 10), (80, 6), (150, 12), (170, 28)]:
        d.ellipse([x0 + sx - 1.5, y0 + sy - 1.5, x0 + sx + 1.5, y0 + sy + 1.5],
                  fill=(200, 200, 200))
    for dx, dy in [(45, 18), (95, 12), (140, 22), (70, 30)]:
        cx, cy = x0 + dx, y0 + dy
        d.line([cx - 9, cy - 4, cx + 9, cy + 4], fill=(220, 220, 220), width=2)
        d.line([cx - 9, cy + 4, cx + 9, cy - 4], fill=(220, 220, 220), width=2)
        for px, py in [(cx - 9, cy - 4), (cx + 9, cy - 4), (cx - 9, cy + 4),
                       (cx + 9, cy + 4)]:
            d.ellipse([px - 2.5, py - 2.5, px + 2.5, py + 2.5],
                      fill=(220, 220, 220))
        d.ellipse([cx - 2.5, cy - 2.5, cx + 2.5, cy + 2.5], fill=(231, 76, 60))
    f = font("sans_b", 13)
    d.text((x1 - tw(f, "112") - 10, y1 - 20), "112", font=f, fill=(255, 200, 80))


def ill_bolt(d, b):
    x0, y0, x1, y1 = b
    d.rectangle(b, fill=(250, 246, 230))
    cx = x0 + 48
    d.polygon([(cx + 8, y0 + 6), (cx - 8, y0 + 24), (cx + 2, y0 + 24),
               (cx - 8, y1 - 6), (cx + 10, y0 + 20), (cx, y0 + 20)],
              fill=(243, 156, 18))
    f = font("sans_b", 12)
    d.text((x0 + 74, y0 + 10), "+26%", font=f, fill=RED)
    f2 = font("sans_b", 10)
    d.text((x0 + 74, y0 + 25), "\u00a32,166/yr", font=f2, fill=INK)


def ill_rescue(d, b):
    x0, y0, x1, y1 = b
    d.rectangle(b, fill=(232, 240, 245))
    d.rectangle([x0 + 20, y0 + 12, x0 + 105, y1 - 6], fill=(120, 140, 160))
    d.rectangle([x0 + 20, y0 + 12, x0 + 105, y0 + 19], fill=(176, 58, 46))
    for wx in (x0 + 27, x0 + 44, x0 + 61, x0 + 78):
        d.rectangle([wx, y0 + 23, wx + 11, y0 + 30], fill=(250, 230, 150))
    d.rectangle([x0 + 55, y1 - 16, x0 + 70, y1 - 6], fill=(60, 70, 85))
    cx, cy = x1 - 32, (y0 + y1) // 2 + 4
    d.ellipse([cx - 10, cy - 10, cx + 10, cy + 10], fill=(30, 132, 73))
    d.line([cx - 5, cy, cx - 1, cy + 4, cx + 6, cy - 4], fill=WHITE, width=2)
    f = font("sans_b", 10)
    d.text((cx - tw(f, "17h") / 2, y0 + 3), "17h", font=f, fill=RED)


def ill_columns(d, b):
    x0, y0, x1, y1 = b
    d.rectangle(b, fill=(240, 238, 232))
    d.polygon([(x0 + 25, y0 + 14), (x0 + 95, y0 + 14), (x0 + 60, y0 + 5)],
              fill=(120, 115, 105))
    for cx in (x0 + 32, x0 + 48, x0 + 64, x0 + 80):
        d.rectangle([cx, y0 + 16, cx + 7, y1 - 12], fill=(150, 145, 135))
    d.rectangle([x0 + 25, y1 - 12, x0 + 95, y1 - 7], fill=(120, 115, 105))
    f = font("sans_b", 10)
    d.text((x1 - tw(f, "2022") - 10, y1 - 20), "2022", font=f, fill=NAVY)


def ill_port(d, b):
    x0, y0, x1, y1 = b
    d.rectangle(b, fill=(168, 205, 225))                     # sky/water
    quay = y1 - 12
    d.rectangle([x0, quay, x1, y1], fill=(110, 130, 145))    # quay
    # container ship at the berth (right)
    d.polygon([(x0 + 108, quay - 2), (x0 + 182, quay - 2), (x0 + 174, quay + 5),
               (x0 + 116, quay + 5)], fill=(45, 50, 62))
    for i, cc in enumerate([(198, 93, 33), (46, 139, 110), (176, 58, 46),
                            (51, 102, 170)]):
        d.rectangle([x0 + 116 + i * 16, quay - 10, x0 + 130 + i * 16, quay - 2],
                    fill=cc)
    d.rectangle([x0 + 168, quay - 16, x0 + 178, quay - 2], fill=(230, 230, 230))
    # gantry crane straddling the quay (left)
    for lx in (x0 + 26, x0 + 78):
        d.line([lx, quay, lx, y0 + 8], fill=(60, 60, 60), width=3)
    d.line([x0 + 18, y0 + 8, x0 + 98, y0 + 8], fill=(60, 60, 60), width=3)
    d.line([x0 + 26, y0 + 20, x0 + 78, y0 + 8], fill=(60, 60, 60), width=1)
    d.line([x0 + 88, y0 + 8, x0 + 88, y0 + 17], fill=(60, 60, 60), width=1)
    d.rectangle([x0 + 80, y0 + 17, x0 + 96, y0 + 24], fill=(198, 93, 33))
    # container stacks on the quay
    d.rectangle([x0 + 30, quay - 7, x0 + 46, quay], fill=(46, 139, 110))
    d.rectangle([x0 + 48, quay - 7, x0 + 64, quay], fill=(176, 58, 46))
    d.rectangle([x0 + 39, quay - 14, x0 + 55, quay - 7], fill=(51, 102, 170))
    f = font("sans_b", 10)
    d.text((x1 - tw(f, "4 downed") - 8, y0 + 6), "4 downed", font=f, fill=NAVY)


def ill_atom(d, b):
    x0, y0, x1, y1 = b
    d.rectangle(b, fill=(22, 26, 52))
    cx, cy = x0 + 48, (y0 + y1) // 2
    d.ellipse([cx - 4, cy - 4, cx + 4, cy + 4], fill=(243, 196, 52))
    for rx, ry in [(22, 9), (9, 22)]:
        d.ellipse([cx - rx, cy - ry, cx + rx, cy + ry], outline=(120, 180, 255),
                  width=1)
    d.line([cx - 16, cy - 16, cx + 16, cy + 16], fill=(120, 180, 255), width=1)
    d.line([cx - 16, cy + 16, cx + 16, cy - 16], fill=(120, 180, 255), width=1)
    f = font("sans_b", 12)
    d.text((x0 + 84, cy - 7), "\u20ac50bn", font=f, fill=(255, 230, 150))


def ill_generic(d, b):
    x0, y0, x1, y1 = b
    d.rectangle(b, fill=(238, 238, 238))
    d.ellipse([x0 + 40, y0 + 10, x0 + 70, y1 - 10], outline=LGRAY, width=2)


ILLUS = {
    "hormuz": ill_hormuz, "markets": ill_markets, "rocket": ill_rocket,
    "factory": ill_factory, "crown": ill_crown, "treaty": ill_treaty,
    "shield": ill_shield, "gavel": ill_gavel, "gauge": ill_gauge,
    "bars_up": ill_bars_up, "scales": ill_scales, "pill": ill_pill,
    "cricket": ill_cricket, "blast": ill_blast, "drones": ill_drones,
    "bolt": ill_bolt, "rescue": ill_rescue, "columns": ill_columns,
    "port": ill_port, "atom": ill_atom,
}

# ------------------------------------------------------------- world map
LAND = [
    [(-168, 66), (-140, 70), (-125, 71), (-110, 68), (-95, 69), (-85, 66),
     (-80, 62), (-78, 58), (-70, 55), (-65, 50), (-60, 46), (-65, 44),
     (-70, 42), (-74, 40), (-76, 37), (-80, 32), (-81, 26), (-84, 30),
     (-89, 30), (-94, 29), (-97, 26), (-97, 22), (-94, 18), (-90, 15),
     (-86, 13), (-83, 9), (-79, 9), (-81, 13), (-84, 16), (-88, 21),
     (-90, 21), (-91, 19), (-97, 16), (-102, 18), (-105, 20), (-110, 23),
     (-114, 29), (-117, 33), (-122, 37), (-124, 42), (-124, 47),
     (-130, 54), (-135, 57), (-150, 60), (-158, 58), (-162, 61), (-168, 66)],
    [(-45, 60), (-30, 68), (-22, 70), (-20, 76), (-25, 80), (-40, 80),
     (-55, 76), (-58, 70), (-52, 62), (-45, 60)],
    [(-79, 9), (-75, 11), (-72, 12), (-64, 10), (-60, 8), (-52, 5), (-50, 0),
     (-44, -3), (-35, -8), (-39, -13), (-40, -21), (-48, -26), (-52, -33),
     (-58, -39), (-62, -41), (-65, -45), (-67, -50), (-68, -54), (-71, -54),
     (-73, -50), (-73, -44), (-72, -37), (-71, -30), (-70, -20), (-70, -18),
     (-75, -15), (-77, -12), (-80, -5), (-81, 1), (-79, 9)],
    [(-6, 35), (0, 36), (10, 37), (11, 34), (20, 32), (30, 31), (32, 31),
     (34, 28), (35, 24), (37, 22), (39, 20), (40, 15), (43, 12), (48, 11),
     (51, 12), (51, 10), (48, 5), (42, -2), (40, -8), (39, -15), (36, -20),
     (35, -24), (33, -27), (27, -33), (20, -35), (17, -32), (15, -27),
     (12, -18), (13, -12), (9, -1), (9, 4), (6, 4), (-2, 5), (-8, 5),
     (-13, 8), (-17, 15), (-17, 21), (-16, 24), (-13, 28), (-9, 31), (-6, 35)],
    [(43, -16), (47, -14), (50, -16), (47, -24), (45, -25), (44, -20), (43, -16)],
    [(-9, 43), (-9, 37), (-6, 36), (-2, 37), (0, 39), (3, 42), (7, 44),
     (10, 44), (12, 44), (14, 42), (16, 40), (18, 40), (19, 42), (21, 40),
     (23, 37), (24, 38), (26, 40), (28, 41), (30, 46), (33, 46), (35, 45),
     (38, 47), (40, 48), (42, 50), (40, 52), (38, 55), (35, 58), (30, 60),
     (28, 61), (30, 64), (28, 66), (25, 67), (20, 69), (15, 68), (12, 65),
     (10, 62), (5, 60), (5, 58), (8, 57), (10, 57), (18, 56), (21, 55),
     (24, 58), (21, 60), (18, 60), (16, 58), (13, 55), (8, 55), (5, 53),
     (2, 51), (0, 49), (-2, 49), (-5, 48), (-2, 44), (-9, 43)],
    [(-5, 50), (-3, 53), (-5, 55), (-3, 58), (-1, 57), (0, 53), (1, 51), (-5, 50)],
    [(26, 41), (30, 41), (36, 36), (36, 33), (34, 28), (35, 24), (38, 21),
     (40, 15), (43, 12), (45, 12), (48, 14), (52, 15), (55, 17), (58, 20),
     (59, 22), (57, 24), (52, 25), (50, 26), (48, 28), (49, 30), (50, 29),
     (54, 26), (56, 27), (57, 27), (61, 25), (66, 25), (67, 24), (72, 20),
     (73, 16), (76, 10), (77, 8), (80, 10), (80, 13), (82, 16), (86, 20),
     (88, 22), (92, 16), (93, 17), (94, 16), (97, 10), (99, 7), (100, 6),
     (103, 1), (104, 2), (103, 5), (100, 8), (98, 10), (98, 13), (100, 13),
     (101, 12), (103, 10), (105, 9), (107, 11), (109, 12), (109, 15),
     (106, 17), (108, 18), (110, 20), (114, 22), (118, 25), (120, 27),
     (122, 29), (121, 31), (120, 34), (122, 37), (120, 35), (119, 35),
     (118, 39), (120, 40), (122, 40), (124, 40), (126, 41), (128, 42),
     (130, 42), (132, 43), (135, 45), (138, 46), (140, 48), (142, 50),
     (141, 52), (142, 54), (143, 59), (150, 60), (155, 59), (158, 52),
     (160, 55), (162, 58), (162, 60), (170, 66), (178, 65), (178, 68),
     (170, 69), (160, 69), (150, 71), (140, 72), (130, 72), (120, 73),
     (110, 74), (100, 77), (90, 75), (80, 73), (70, 72), (60, 69),
     (50, 68), (45, 68), (40, 66), (35, 65), (33, 67), (30, 70),
     (25, 71), (18, 69), (20, 64), (25, 60), (28, 59), (30, 60),
     (28, 61), (24, 59), (21, 60), (24, 58), (28, 55), (30, 52),
     (32, 50), (35, 48), (38, 47), (40, 48), (38, 45), (36, 42),
     (33, 42), (30, 41), (26, 41)],
    [(95, 5), (100, 0), (104, -3), (106, -6), (102, -4), (98, 2), (95, 5)],
    [(105, -6), (110, -7), (114, -8), (114, -9), (108, -8), (105, -7)],
    [(109, 1), (113, 4), (117, 6), (119, 2), (117, -2), (113, -3), (110, -2),
     (109, 1)],
    [(131, -1), (136, -2), (141, -3), (146, -6), (150, -9), (147, -9),
     (142, -8), (137, -7), (132, -4), (131, -1)],
    [(130, 31), (133, 34), (137, 35), (140, 36), (141, 40), (142, 44),
     (140, 43), (139, 38), (136, 34), (132, 33), (130, 31)],
    [(113, -22), (114, -28), (115, -34), (118, -35), (124, -33), (129, -32),
     (132, -32), (135, -35), (138, -36), (140, -38), (145, -38), (150, -37),
     (153, -32), (153, -27), (151, -24), (149, -20), (146, -19), (146, -15),
     (143, -13), (142, -11), (142, -14), (141, -17), (140, -18), (136, -15),
     (135, -12), (132, -11), (130, -12), (126, -14), (122, -17), (118, -20),
     (114, -22), (113, -22)],
    [(167, -45), (169, -43), (172, -41), (174, -39), (176, -38), (178, -37),
     (175, -37), (174, -41), (172, -43), (169, -46), (167, -45)],
]


def in_poly(lon, lat, poly):
    inside = False
    j = len(poly) - 1
    for i in range(len(poly)):
        xi, yi = poly[i]
        xj, yj = poly[j]
        if (yi > lat) != (yj > lat) and \
                lon < (xj - xi) * (lat - yi) / (yj - yi) + xi:
            inside = not inside
        j = i
    return inside


def draw_map(d, box, pins):
    x0, y0, x1, y1 = box
    d.rectangle(box, fill=(238, 242, 238), outline=LINE, width=1)
    lon_lo, lon_hi, lat_hi, lat_lo = -170, 190, 78, -58
    step = 5
    for gy in range(y0 + 4, y1 - 3, step):
        lat = lat_hi - (gy - y0) / (y1 - y0) * (lat_hi - lat_lo)
        for gx in range(x0 + 4, x1 - 3, step):
            lon = lon_lo + (gx - x0) / (x1 - x0) * (lon_hi - lon_lo)
            if any(in_poly(lon, lat, p) for p in LAND):
                d.ellipse([gx - 1.5, gy - 1.5, gx + 1.5, gy + 1.5],
                          fill=(150, 165, 150))
    # display nudges (px) so clustered pins stay readable; true lon/lat kept
    PIN_NUDGE = {1: (5, -3), 4: (-7, -4), 5: (6, -6), 6: (-11, -7),
                 7: (-6, 6), 9: (-2, 6), 10: (6, -6), 12: (1, 7), 13: (6, 8)}
    for n, (lon, lat), color in pins:
        px = x0 + (lon - lon_lo) / (lon_hi - lon_lo) * (x1 - x0)
        py = y0 + (lat_hi - lat) / (lat_hi - lat_lo) * (y1 - y0)
        dx, dy = PIN_NUDGE.get(n, (0, 0))
        num_chip(d, px - 8 + dx, py - 8 + dy, n, color, r=8)


# ------------------------------------------------------------------ cards
def illus_layer(fn, w, h):
    """Render an illustration on its own layer so nothing spills out."""
    layer = Image.new("RGB", (w, h), PAPER)
    fn(ImageDraw.Draw(layer), (0, 0, w, h))
    return layer


def lead_card(img, d, x, y, w, h, s):
    d.rectangle([x, y, x + w, y + h], fill=CREAM, outline=LINE, width=1)
    ih = 82
    img.paste(illus_layer(ILLUS.get(s["illus"], ill_generic), w - 2, ih),
              (x + 1, y + 1))
    num_chip(d, x + 6, y + 6, s["n"], REGION_COLORS[s["region"]])
    ty = y + ih + 6
    fk = font("sans_b", 10)
    tracked(d, x + 9, ty, s["loc"], fk, REGION_COLORS[s["region"]], 0.8)
    badge(d, x + w - 9 - (tracked_w(font("sans_b", 8), s["badge"], 0.6) + 10),
          ty - 1, s["badge"])
    ty += 17
    fh = font("serif_b", 20)
    for ln in wrap(s["head"], fh, w - 18)[:2]:
        d.text((x + 9, ty), ln, font=fh, fill=INK)
        ty += 23
    ty += 1
    fb = font("sans", 11.5)
    for ln in wrap(s["body"], fb, w - 18)[:3]:
        d.text((x + 9, ty), ln, font=fb, fill=(50, 50, 50))
        ty += 14
    fs = font("sans", 9.5)
    d.text((x + 9, y + h - 15), s["src"], font=fs, fill=GRAY)


def grid_card(img, d, x, y, w, h, s):
    d.rectangle([x, y, x + w, y + h], fill=CREAM, outline=LINE, width=1)
    ih = 42
    img.paste(illus_layer(ILLUS.get(s["illus"], ill_generic), w - 2, ih),
              (x + 1, y + 1))
    num_chip(d, x + 5, y + 5, s["n"], REGION_COLORS[s["region"]], r=8)
    ty = y + ih + 5
    fk = font("sans_b", 8.5)
    tracked(d, x + 8, ty, s["loc"], fk, REGION_COLORS[s["region"]], 0.5)
    ty += 14
    fh = font("serif_b", 14.5)
    for ln in wrap(s["head"], fh, w - 16)[:2]:
        d.text((x + 8, ty), ln, font=fh, fill=INK)
        ty += 17
    ty += 1
    fb = font("sans", 10)
    for ln in wrap(s["body"], fb, w - 16)[:3]:
        d.text((x + 8, ty), ln, font=fb, fill=(50, 50, 50))
        ty += 12.5
    fs = font("sans", 8.5)
    d.text((x + 8, y + h - 13), s["src"], font=fs, fill=GRAY)
    badge(d, x + w - 8 - (tracked_w(font("sans_b", 8), s["badge"], 0.6) + 10),
          y + h - 15, s["badge"])


# ------------------------------------------------------------------- main
def build():
    img = Image.new("RGB", (W, H), PAPER)
    d = ImageDraw.Draw(img)
    x0 = MARGIN

    all_stories = LEADS + GRID
    total = len(all_stories) + len(ALSO)
    regions = {}
    for s in all_stories:
        regions[s["region"]] = regions.get(s["region"], 0) + 1
    for _n, reg, _p, _t, _s in ALSO:
        regions[reg] = regions.get(reg, 0) + 1

    # top bar
    d.rectangle([0, 0, W, 26], fill=NAVY)
    ft = font("sans_b", 11)
    tracked(d, x0, 7, "THE WORLD IN ONE DAY", ft, WHITE, 1.6)
    right = "%d STORIES \u00b7 %d REGIONS \u00b7 EVERY ONE FROM THIS WEDNESDAY" \
        % (total, len(regions))
    tracked(d, W - x0 - tracked_w(ft, right, 1.2), 7, right, ft, WHITE, 1.2)

    # masthead
    fm = font("mast", 58)
    date = "Wednesday 25 November 2026"
    d.text(((W - tw(fm, date)) / 2, 32), date, font=fm, fill=INK)
    fs = font("serif_i", 18)
    stand = ("Iran tightens Hormuz closure \u00b7 Asia markets slide \u00b7 "
             "First Pakistani in orbit")
    d.text(((W - tw(fs, stand)) / 2, 101), stand, font=fs, fill=RED)
    d.line([x0, 124, W - x0, 124], fill=INK, width=2)

    # region chips
    cy = 132
    fc = font("sans_b", 10)
    cx = x0
    for reg in REGION_ORDER:
        if reg not in regions:
            continue
        label = "%s %d" % (reg, regions[reg])
        wch = tracked_w(fc, label, 0.8) + 16
        d.rounded_rectangle([cx, cy, cx + wch, cy + 18], 4,
                            fill=REGION_COLORS[reg])
        tracked(d, cx + 8, cy + 4, label, fc, WHITE, 0.8)
        cx += wch + 8

    # UTC timeline
    ty = 158
    d.rectangle([x0, ty, W - x0, ty + 26], fill=NAVY2)
    fl = font("sans_b", 9)
    d.text((x0 + 8, ty + 3), "THE DAY", font=fl, fill=(243, 196, 52))
    d.text((x0 + 8, ty + 14), "IN UTC", font=fl, fill=(243, 196, 52))
    fe = font("sans", 9.5)
    fet = font("sans_b", 9.5)
    ex = x0 + 62
    for t, ev in TIMELINE:
        d.text((ex, ty + 3), t, font=fet, fill=(243, 196, 52))
        d.text((ex, ty + 14), ev, font=fe, fill=WHITE)
        ex += max(tw(fe, ev), tw(fet, t)) + 18

    # numbers strip
    ny = 192
    d.rectangle([x0, ny, x0 + 66, ny + 40], fill=RED)
    fnl = font("sans_b", 8.5)
    d.text((x0 + 6, ny + 4), "THE DAY", font=fnl, fill=WHITE)
    d.text((x0 + 6, ny + 15), "IN NUMBERS", font=fnl, fill=WHITE)
    d.text((x0 + 6, ny + 26), "25 NOV", font=fnl, fill=WHITE)
    fn = font("serif_b", 21)
    fnc = font("sans", 9)
    cell_w = (CW - 66) / len(NUMBERS)
    for i, (num, cap) in enumerate(NUMBERS):
        cxp = x0 + 66 + i * cell_w
        if i:
            d.line([cxp, ny + 4, cxp, ny + 36], fill=LGRAY, width=1)
        if ">" in num:  # draw a real arrow between the two figures
            a, b = num.split(">")
            total_w = tw(fn, a) + 16 + tw(fn, b)
            sx = cxp + (cell_w - total_w) / 2
            d.text((sx, ny + 2), a, font=fn, fill=INK)
            ax = sx + tw(fn, a) + 3
            d.line([ax, ny + 13, ax + 10, ny + 13], fill=INK, width=2)
            d.polygon([(ax + 10, ny + 9), (ax + 10, ny + 17), (ax + 15, ny + 13)],
                      fill=INK)
            d.text((ax + 16, ny + 2), b, font=fn, fill=INK)
        else:
            d.text((cxp + (cell_w - tw(fn, num)) / 2, ny + 2), num, font=fn,
                   fill=INK)
        for j, ln in enumerate(wrap(cap, fnc, cell_w - 12)[:2]):
            d.text((cxp + (cell_w - tw(fnc, ln)) / 2, ny + 27 + j * 10), ln,
                   font=fnc, fill=GRAY)

    # leads
    ly = 240
    lw = 326
    for i, s in enumerate(LEADS):
        lead_card(img, d, x0 + i * (lw + 9), ly, lw, 216, s)

    # grid
    gw = 192
    for r in range(2):
        gy = 464 + r * 160
        for c in range(5):
            grid_card(img, d, x0 + c * (gw + 9), gy, gw, 152, GRID[r * 5 + c])

    # bottom band: also-list + map
    by = 784
    fh2 = font("sans_b", 11)
    tracked(d, x0, by, "ALSO ON WEDNESDAY 25 NOVEMBER", fh2, INK, 1.0)
    d.line([x0, by + 17, x0 + 636, by + 17], fill=INK, width=1)
    fa = font("sans", 9)
    fab = font("sans_b", 9)
    fas = font("sans", 8)
    col_w = 212
    per_col = 6
    for i, (n, reg, place, text, src) in enumerate(ALSO):
        col, row = divmod(i, per_col)
        ax = x0 + col * col_w
        ay = by + 24 + row * 21
        num_chip(d, ax, ay, n, REGION_COLORS[reg], r=7)
        d.text((ax + 19, ay - 1), place + ":", font=fab, fill=INK)
        rest = text
        first_w = col_w - 24 - tw(fab, place + ": ")
        words, l1 = rest.split(), ""
        while words and tw(fa, (l1 + " " + words[0]).strip()) <= first_w:
            l1 = (l1 + " " + words.pop(0)).strip()
        d.text((ax + 19 + tw(fab, place + ": "), ay - 1), l1, font=fa, fill=INK)
        l2 = " ".join(words)
        if l2:
            d.text((ax + 19, ay + 10), l2 + " (" + src + ")", font=fas, fill=GRAY)
        else:
            d.text((ax + 19, ay + 10), "(" + src + ")", font=fas, fill=GRAY)

    # map
    mx = x0 + 648
    tracked(d, mx, by, "WHERE IT HAPPENED", fh2, INK, 1.0)
    fsmall = font("sans", 8.5)
    d.text((mx + 150, by + 2), "pins = story numbers", font=fsmall, fill=GRAY)
    pins = [(s["n"], s["pin"], REGION_COLORS[s["region"]]) for s in all_stories]
    draw_map(d, (mx, by + 20, W - x0, by + 118), pins)
    # region legend under map (two rows)
    legend_names = {"SE ASIA": "SE Asia"}
    for ri, reg in enumerate([r for r in REGION_ORDER if r in regions]):
        lx = mx + (ri % 4) * 87
        ly2 = by + 124 + (ri // 4) * 11
        d.ellipse([lx, ly2 + 1, lx + 7, ly2 + 8], fill=REGION_COLORS[reg])
        d.text((lx + 10, ly2 - 1),
               "%s %d" % (legend_names.get(reg, reg.title()), regions[reg]),
               font=fsmall, fill=INK)

    # date check
    dy = 934
    d.rectangle([x0, dy, W - x0, dy + 36], outline=RED, width=1)
    d.rectangle([x0, dy, x0 + 92, dy + 36], fill=RED)
    fd = font("sans_b", 11)
    d.text((x0 + 8, dy + 5), "DATE", font=fd, fill=WHITE)
    d.text((x0 + 8, dy + 19), "CHECK", font=fd, fill=WHITE)
    fdc = font("sans", 10)
    txt = ("Every story on this page happened, or was first reported, on "
           "Wednesday 25 November 2026 (UTC). Left out as other days' news: "
           + " \u00b7 ".join(DATE_CHECK) + ".")
    for j, ln in enumerate(wrap(txt, fdc, CW - 112)[:2]):
        d.text((x0 + 102, dy + 6 + j * 13), ln, font=fdc, fill=INK)

    # footer
    fy = 980
    ff = font("sans", 9.5)
    ffb = font("sans_b", 9.5)
    d.text((x0, fy), "HOW SURE:", font=ffb, fill=INK)
    fx = x0 + tw(ffb, "HOW SURE: ")
    for bname, desc in [("CONFIRMED", "2+ outlets"), ("OFFICIAL", "on the record"),
                        ("REPORTED", "one outlet"), ("CLAIM", "one side's account")]:
        d.rectangle([fx, fy + 1, fx + 8, fy + 9], fill=BADGE_COLORS[bname])
        d.text((fx + 11, fy), "%s %s" % (bname, desc), font=ff, fill=INK)
        fx += 11 + tw(ff, "%s %s" % (bname, desc)) + 14
    src_line = "Sources named beside each story \u00b7 Illustrations drawn in code"
    d.text((W - x0 - tw(ff, src_line), fy), src_line, font=ff, fill=GRAY)
    d.text((x0, fy + 14),
           "Every story here happened, or was first reported, on Wednesday "
           "25 November 2026.", font=ff, fill=GRAY)

    img.save("entry.png", format="PNG", optimize=False)
    print("wrote entry.png")


if __name__ == "__main__":
    build()
