#!/usr/bin/env python3
"""Generate the Nov 19 2026 world-news front page (1024x1024 PNG) with PIL.

Pure PIL vector-style drawing: no network, no external assets, deterministic.
Run: python3 generate_image.py [out.png]
"""
import sys
from PIL import Image, ImageDraw, ImageFont

W, H = 1024, 1024
PAPER = (247, 242, 228)
INK = (20, 20, 20)
NAVY = (22, 35, 63)
RED = (163, 30, 34)
RED_DK = (140, 22, 26)
GOLD = (200, 162, 74)
GREY = (90, 88, 80)
LINE = (120, 110, 90)
CARD_BG = (255, 253, 246)

F = "/usr/share/fonts/truetype/noto/"
FD = "/usr/share/fonts/truetype/dejavu/"


def font(path, size):
    return ImageFont.truetype(path, size)


SERIF_BLK = F + "NotoSerifDisplay-Black.ttf"
SERIF_B = F + "NotoSerif-Bold.ttf"
SERIF = F + "NotoSerif-Regular.ttf"
SERIF_I = F + "NotoSerif-Italic.ttf"
SANS = F + "NotoSans-Regular.ttf"
SANS_B = F + "NotoSans-Bold.ttf"
SANS_I = F + "NotoSans-Italic.ttf"


def wrap(draw, text, fnt, width):
    words, lines, cur = text.split(), [], ""
    for w in words:
        t = (cur + " " + w).strip()
        if draw.textlength(t, font=fnt) <= width:
            cur = t
        else:
            if cur:
                lines.append(cur)
            cur = w
    if cur:
        lines.append(cur)
    return lines


def fit_text(draw, text, fnt, width, max_lines=None):
    """Wrap text, trimming with ellipsis to fit max_lines."""
    lines = wrap(draw, text, fnt, width)
    if max_lines and len(lines) > max_lines:
        lines = lines[:max_lines]
        while lines and draw.textlength(lines[-1] + " …", font=fnt) > width:
            lines[-1] = lines[-1].rsplit(" ", 1)[0] if " " in lines[-1] else lines[-1][:-1]
        lines[-1] += " …"
    return lines


def draw_text_block(draw, x, y, lines, fnt, fill, leading):
    for ln in lines:
        draw.text((x, y), ln, font=fnt, fill=fill)
        y += leading
    return y


# ---------------------------------------------------------------- stories
# (n, region, kicker, source, headline, body)
FEATURED = [
    (1, "ASIA-PACIFIC", "SHENZHEN · SUMMIT", "CONFIRMED · REUTERS · AP",
     "Trump, Xi and Putin hold first three-way summit",
     "The three nuclear powers meet at APEC in Shenzhen — a first. After 90 minutes they pledge more oil supply and talks to cut nuclear risk; no deal on Ukraine or Iran."),
    (2, "WORLD", "WORLDWIDE · GAMES", "REUTERS",
     "GTA VI arrives after a 13-year wait",
     "Rockstar's sequel unlocks at midnight local time, New Zealand first. 15.9m pre-orders banked; $79.99 on PS5 and Xbox, no PC yet."),
    (3, "THE AMERICAS", "NASDAQ · MARKETS", "BLOOMBERG",
     "Anthropic debuts in the biggest IPO on record",
     "Priced at $83 on Wednesday, the Claude maker raised $81.3bn and is valued near $1.5tn. Shares start trading on Nasdaq as ANT."),
    (4, "EUROPE", "THE HAGUE · LAW", "ICJ",
     "World Court rules on Myanmar's Rohingya case",
     "The Gambia's case over 2017. A first: no state was ever found guilty."),
    (5, "WORLD", "ANTALYA · CLIMATE", "UNFCCC",
     "COP31 enters its final 48 hours",
     "Ministers take over the text; 'phase out' and the $120bn fund are still open."),
    (6, "ASIA-PACIFIC", "ODISHA · STORM", "IMD",
     "Akvan bears down as 80,000 flee",
     "Red alerts in 11 districts, schools shut. Landfall near Puri due Friday."),
    (7, "EUROPE", "CRIMEA · WAR", "BBC · KYIV",
     "Bridge struck again; traffic halted",
     "Third drone attack this week shuts the Kerch Strait rail line."),
    (8, "MIDEAST", "GAZA · CONFLICT", "REUTERS",
     "Israeli armour pushes into central Gaza",
     "Tanks and bulldozers pass the Yellow Line; Hamas cites a truce breach."),
    (9, "MIDEAST", "HORMUZ · ENERGY", "IRAN",
     "Three tankers catch fire after hitting mines",
     "Iran says ships struck mines east of the Strait; crews rescued."),
    (10, "THE AMERICAS", "CARACAS · DEFENCE", "AP",
     "Hegseth signs Venezuela pact",
     "On a surprise visit, the US defence secretary inks a training and arms deal."),
    (11, "THE AMERICAS", "FLORIDA · WEATHER", "AP · NWS",
     "Flooded South Florida logs 300+ rescues",
     "A foot of rain shuts Broward schools and triggers high-water rescues."),
    (12, "AFRICA", "HORN OF AFRICA · TENSIONS", "REUTERS",
     "Ethiopia and Eritrea mass troops",
     "Forces gather near Badme; monitors warn of a direct war."),
    (13, "ASIA-PACIFIC", "SEOUL · EDUCATION", "YONHAP",
     "Half a million sit Korea's Suneung",
     "551,864 take the exam; flights pause and phones are hunted by alert."),
]

BRIEFS = [
    (14, "Riyadh", "Houthi attack damages top tower"),
    (15, "Kumamoto", "M5.7 quake hits Japan, 2 hurt"),
    (16, "Dhaka", "Bangladesh starts nuclear power"),
    (17, "West Bank", "Israel delays E1; settler kills"),
    (18, "Madrid", "Spain sets snap poll for 29 Nov"),
    (19, "Seoul", "Ex-PM Han faces retrial"),
    (20, "Paris", "France jails 3 women over ISIS"),
    (21, "Manama", "US renews Gulf warnings"),
    (22, "Washington", "Russian agent held in spying case"),
    (23, "Bogotá", "Unions strike nationwide"),
    (24, "Paris", "Mélenchon leads 2027 polls"),
    (25, "Benghazi", "Cocaine, pills seized in east"),
    (26, "Jazan", "Saudi all-clear after alerts"),
    (27, "Canberra", "Jobless hits 5-year high, 4.9%"),
    (28, "Tokyo", "India, Japan hold 2+2 talks"),
    (29, "Ottawa", "Canada sanctions settler groups"),
    (30, "Nairobi", "Kenya floods kill six"),
    (31, "La Paz", "Bolivia declares El Niño alert"),
    (32, "Sacramento", "California braces for storms"),
    (33, "New Delhi", "Schools reopen as smog lifts"),
    (34, "London", "Grid debunks AI blackout hoax"),
    (35, "Ottawa", "Carney reviews China trade"),
    (36, "Washington", "Vance: no 'forever war' in Gulf"),
    (37, "Manila", "US pursues $2bn Philippines loan"),
    (38, "Auckland", "Kiwis first to play GTA VI"),
    (39, "Baghdad", "Six French ISIL men jailed"),
    (40, "Dakar", "Migrant boat sinks, dozens lost"),
    (41, "Moscow", "Plane crash kills all 19"),
    (42, "Miami", "Pastor guilty over Haiti killing"),
    (43, "Washington", "Musk 'pretty foolish' on spending"),
    (44, "Worldwide", "Muslims to top Christians by 2035"),
    (45, "Seoul", "Lee renews Pyongyang talks call"),
    (46, "Kuwait", "Kuwait repels Iranian attack"),
    (47, "Washington", "Trump: Iran eyes bio-weapons"),
    (48, "Cape Canaveral", "NASA sets CRS-25 launch cover"),
]

REGIONS = ["EUROPE", "THE AMERICAS", "ASIA-PACIFIC", "MIDEAST", "AFRICA", "OCEANIA", "WORLD"]
REGION_COLORS = {
    "EUROPE": (31, 78, 121), "THE AMERICAS": (46, 125, 50),
    "ASIA-PACIFIC": (123, 31, 162), "MIDEAST": (146, 64, 32),
    "AFRICA": (166, 110, 28), "OCEANIA": (0, 121, 107), "WORLD": (90, 90, 90),
}
REGION_SHORT = {"EUROPE": "EUROPE", "THE AMERICAS": "THE AMERICAS",
                "ASIA-PACIFIC": "ASIA-PACIFIC", "MIDEAST": "MIDEAST",
                "AFRICA": "AFRICA", "OCEANIA": "OCEANIA", "WORLD": "WORLD"}

NUMBERS = [
    ("$81.3bn", "raised by Anthropic — the largest IPO ever"),
    ("15.9m", "GTA VI pre-orders banked before launch"),
    ("80,000+", "evacuated ahead of Cyclone Akvan"),
    ("730,000", "Rohingya who fled Myanmar in 2017"),
    ("90 min", "the Shenzhen trilateral talks lasted"),
    ("551,864", "sit Korea's Suneung exam"),
]

UTC_STRIP = [
    ("OVERNIGHT", "GTA VI on sale"),
    ("MORNING", "Shenzhen opens"),
    ("MORNING", "ICJ Rohingya ruling"),
    ("AFTERNOON", "Bridge hit again"),
    ("AFTERNOON", "ANT starts trading"),
    ("EVENING", "COP31 talks go late"),
]

# map pins (lon, lat) for stories 1-13
PINS = {1: (114.1, 22.5), 2: (174.8, -36.8), 3: (-74.0, 40.7), 4: (4.3, 52.1),
        5: (30.7, 36.9), 6: (85.8, 20.3), 7: (34.0, 45.0), 8: (34.5, 31.5),
        9: (56.5, 26.5), 10: (-66.9, 10.5), 11: (-80.2, 26.1),
        12: (39.5, 14.5), 13: (127.0, 37.5)}

CONTINENTS = [
    [(-168, 66), (-140, 70), (-120, 72), (-95, 80), (-80, 73), (-75, 62), (-55, 52),
     (-60, 47), (-70, 42), (-75, 35), (-80, 26), (-85, 30), (-90, 21), (-95, 19),
     (-105, 20), (-110, 24), (-120, 34), (-125, 40), (-125, 49), (-140, 60),
     (-155, 58), (-165, 60)],
    [(-80, 10), (-75, 5), (-60, 0), (-50, 0), (-35, -8), (-40, -20), (-48, -28),
     (-55, -35), (-65, -40), (-70, -52), (-73, -40), (-72, -20), (-77, -12), (-80, -3)],
    [(-10, 36), (-9, 43), (-2, 48), (0, 50), (5, 53), (8, 57), (10, 59), (18, 56),
     (21, 55), (24, 58), (28, 60), (30, 62), (30, 70), (25, 71), (18, 69),
     (12, 65), (5, 60), (-5, 58), (-10, 52), (-10, 43)],
    [(-17, 15), (-10, 30), (0, 36), (10, 37), (20, 32), (32, 31), (35, 28),
     (40, 15), (43, 11), (48, 11), (51, 12), (44, 0), (40, -10), (35, -20),
     (32, -28), (26, -34), (19, -35), (15, -27), (12, -18), (9, -1), (9, 4),
     (-8, 4), (-13, 8)],
    [(30, 36), (35, 36), (40, 38), (45, 40), (50, 42), (55, 45), (60, 45),
     (65, 45), (70, 50), (75, 55), (80, 60), (90, 65), (100, 70), (110, 73),
     (120, 72), (130, 72), (140, 72), (150, 70), (160, 66), (170, 66), (178, 65),
     (170, 60), (162, 56), (158, 52), (150, 59), (142, 55), (140, 50), (135, 43),
     (130, 38), (127, 35), (122, 32), (120, 28), (110, 20), (108, 12), (105, 8),
     (100, 6), (98, 10), (95, 15), (92, 20), (90, 22), (86, 20), (82, 16),
     (80, 10), (76, 8), (72, 20), (66, 25), (60, 25), (55, 26), (50, 29),
     (48, 30), (43, 30), (40, 32), (36, 36)],
    [(113, -22), (114, -30), (115, -35), (120, -34), (125, -32), (130, -32),
     (135, -35), (140, -38), (145, -38), (150, -37), (153, -32), (153, -27),
     (150, -22), (146, -19), (142, -15), (142, -11), (137, -12), (135, -15),
     (132, -12), (130, -13), (126, -14), (122, -17), (118, -20)],
    [(95, 5), (100, 0), (105, -5), (110, -7), (115, -8), (120, -10), (125, -9),
     (130, -5), (135, -3), (140, -4), (141, -1), (136, 0), (130, 1), (125, 1),
     (120, 0), (115, 3), (110, 5), (105, 5)],
    [(130, 31), (133, 34), (137, 35), (140, 38), (141, 42), (143, 44),
     (140, 40), (136, 37), (132, 33)],
    [(167, -45), (170, -42), (173, -40), (176, -38), (178, -38),
     (175, -41), (172, -43), (168, -46)],
]


def point_in_poly(x, y, poly):
    inside, n = False, len(poly)
    j = n - 1
    for i in range(n):
        xi, yi = poly[i]
        xj, yj = poly[j]
        if ((yi > y) != (yj > y)) and (x < (xj - xi) * (y - yi) / (yj - yi) + xi):
            inside = not inside
        j = i
    return inside


# ---------------------------------------------------------------- illustrations
def flag(draw, x, y, w, h, kind):
    """Simple flat flag on a pole."""
    draw.line([(x + w // 2, y), (x + w // 2, y + h + 26)], fill=INK, width=2)
    if kind == "us":
        for i in range(7):
            draw.rectangle([x, y + i * h // 7, x + w, y + (i + 1) * h // 7],
                           fill=RED if i % 2 == 0 else (255, 255, 255))
        draw.rectangle([x, y, x + w * 0.45, y + h * 0.55], fill=NAVY)
    elif kind == "cn":
        draw.rectangle([x, y, x + w, y + h], fill=(222, 41, 16))
        for sx, sy in [(0.22, 0.3), (0.45, 0.18), (0.5, 0.42), (0.32, 0.55)]:
            draw.ellipse([x + w * sx - 2, y + h * sy - 2, x + w * sx + 2, y + h * sy + 2],
                         fill=(255, 222, 0))
    elif kind == "ru":
        for i, c in enumerate([(255, 255, 255), (0, 57, 166), (213, 0, 50)]):
            draw.rectangle([x, y + i * h // 3, x + w, y + (i + 1) * h // 3], fill=c)


def skyline(draw, x, y, w, h, base, color, heights):
    n = len(heights)
    bw = w // n
    for i, hh in enumerate(heights):
        draw.rectangle([x + i * bw + 1, y + h - hh, x + (i + 1) * bw - 1, y + h],
                       fill=color)
    draw.rectangle([x, y + h, x + w, y + h + 2], fill=base)


def ill_summit(d, x, y, w, h):
    d.rectangle([x, y, x + w, y + h], fill=(214, 228, 240))
    skyline(d, x, y + h - 46, w, 34, INK, (90, 100, 110),
            [18, 30, 22, 34, 26, 30, 20, 32, 24, 30, 18, 26])
    d.rectangle([x, y + h - 12, x + w, y + h], fill=(150, 120, 90))
    flag(d, x + 52, y + 22, 44, 26, "us")
    flag(d, x + w // 2 - 10, y + 14, 44, 26, "cn")
    flag(d, x + w - 96, y + 22, 44, 26, "ru")


def ill_gta(d, x, y, w, h):
    for i in range(h):
        t = i / h
        r = int(90 + 90 * t)
        g = int(40 + 60 * t)
        b = int(110 - 40 * t)
        d.line([(x, y + i), (x + w, y + i)], fill=(r, g, b))
    d.ellipse([x + w - 96, y + 12, x + w - 36, y + 72], fill=(255, 190, 90))
    skyline(d, x, y + h - 52, w, 40, INK, (40, 20, 60),
            [22, 34, 26, 40, 30, 36, 24, 38, 28, 34, 22, 30])
    d.ellipse([x + 24, y + h - 26, x + 44, y + h - 6], fill=(30, 30, 50))
    d.rectangle([x + 32, y + h - 34, x + 36, y + h - 8], fill=(30, 30, 50))


def ill_anthropic(d, x, y, w, h):
    d.rectangle([x, y, x + w, y + h], fill=(16, 60, 44))
    for i in range(5):
        yy = y + 14 + i * (h - 28) // 4
        d.line([(x + 8, yy), (x + w - 8, yy)], fill=(255, 255, 255, 40) if False else (40, 90, 72), width=1)
    candles = [(14, 62, 78, 52), (30, 58, 74, 46), (46, 50, 66, 40), (62, 44, 58, 32),
               (76, 38, 50, 26), (88, 30, 40, 18)]
    for cx, top, bot, _ in candles:
        px = x + cx
        d.line([(px + 8, y + top - 6), (px + 8, y + bot + 6)], fill=(255, 255, 255), width=1)
        d.rectangle([px, y + top, px + 16, y + bot], fill=(60, 200, 130))
    d.line([(x + 10, y + 78), (x + w - 20, y + 26)], fill=(255, 214, 90), width=3)
    d.text((x + 10, y + 6), "ANT  $83", font=font(SANS_B, 15), fill=(255, 214, 90))


def ill_court(d, x, y, w, h):
    d.rectangle([x, y, x + w, y + h], fill=(226, 232, 240))
    d.polygon([(x + 14, y + 34), (x + w // 2, y + 10), (x + w - 14, y + 34)], fill=(120, 110, 95))
    for i in range(5):
        cx = x + 26 + i * ((w - 52) // 4)
        d.rectangle([cx - 4, y + 36, cx + 4, y + h - 8], fill=(240, 238, 230))
    d.rectangle([x + 12, y + 34, x + w - 12, y + 40], fill=(90, 85, 75))
    d.rectangle([x + 10, y + h - 10, x + w - 10, y + h - 4], fill=(90, 85, 75))


def ill_climate(d, x, y, w, h):
    d.rectangle([x, y, x + w, y + h], fill=(200, 226, 235))
    d.ellipse([x + w - 52, y + 8, x + w - 16, y + 44], fill=(255, 190, 60))
    for i in range(3):
        yy = y + 40 + i * 10
        d.arc([x + 8, yy - 6, x + w - 8, yy + 10], 200, 340, fill=(40, 110, 160), width=3)
    d.rectangle([x + 14, y + h - 26, x + 34, y + h - 6], fill=(90, 140, 90))
    d.rectangle([x + 40, y + h - 20, x + 58, y + h - 6], fill=(60, 110, 70))


def ill_cyclone(d, x, y, w, h):
    d.rectangle([x, y, x + w, y + h], fill=(210, 222, 232))
    cx, cy = x + w // 2, y + h // 2
    for r in range(6, 34, 6):
        d.arc([cx - r, cy - r, cx + r, cy + r], 20 + r * 8, 300 + r * 8,
              fill=(30, 80, 140), width=4)
    d.ellipse([cx - 4, cy - 4, cx + 4, cy + 4], fill=(30, 80, 140))
    d.text((x + 8, y + 4), "RED ALERT", font=font(SANS_B, 11), fill=RED)


def ill_bridge(d, x, y, w, h):
    d.rectangle([x, y, x + w, y + h], fill=(196, 216, 232))
    d.rectangle([x, y + h - 22, x + w, y + h - 16], fill=(120, 120, 125))
    for i, px in enumerate([x + 30, x + w // 2, x + w - 30]):
        d.line([(px, y + 8), (px, y + h - 16)], fill=(90, 90, 95), width=3)
        d.line([(px, y + 8), (px - 46, y + h - 16)], fill=(90, 90, 95), width=1)
        d.line([(px, y + 8), (px + 46, y + h - 16)], fill=(90, 90, 95), width=1)
    d.ellipse([x + w // 2 - 12, y + 16, x + w // 2 + 12, y + 40], fill=(255, 140, 0))
    for a in range(8):
        import math
        ang = a * 3.14159 / 4
        d.line([(x + w // 2, y + 28),
                (x + w // 2 + 16 * math.cos(ang), y + 28 + 16 * math.sin(ang))],
               fill=(255, 140, 0), width=2)


def ill_tank(d, x, y, w, h):
    d.rectangle([x, y, x + w, y + h], fill=(228, 220, 200))
    d.rectangle([x + 18, y + h - 34, x + w - 40, y + h - 18], fill=(90, 100, 70))
    d.rectangle([x + 30, y + h - 46, x + w - 60, y + h - 32], fill=(110, 120, 85))
    d.line([(x + w - 58, y + h - 40), (x + w - 8, y + h - 48)], fill=(90, 100, 70), width=4)
    for i in range(5):
        d.ellipse([x + 24 + i * 12, y + h - 16, x + 32 + i * 12, y + h - 8], fill=(60, 60, 60))
    d.line([(x + 8, y + 12), (x + w - 8, y + 12)], fill=RED, width=2)
    d.text((x + 8, y + 16), "YELLOW LINE", font=font(SANS_B, 10), fill=RED)


def ill_tanker(d, x, y, w, h):
    d.rectangle([x, y, x + w, y + h], fill=(190, 210, 225))
    d.polygon([(x + 14, y + h - 30), (x + 34, y + h - 44), (x + w - 34, y + h - 44),
               (x + w - 14, y + h - 30)], fill=(60, 60, 70))
    d.rectangle([x + w // 2 - 8, y + h - 58, x + w // 2 + 8, y + h - 42], fill=(120, 60, 50))
    d.ellipse([x + w - 52, y + 10, x + w - 28, y + 34], fill=(255, 120, 0))
    d.ellipse([x + w - 44, y + 4, x + w - 30, y + 18], fill=(255, 180, 40))
    for i in range(3):
        d.arc([x + 10 + i * 16, y + h - 14, x + 26 + i * 16, y + h + 2], 180, 360,
              fill=(40, 110, 160), width=2)


def ill_pact(d, x, y, w, h):
    d.rectangle([x, y, x + w, y + h], fill=(232, 228, 214))
    flag(d, x + 22, y + 16, 34, 20, "us")
    flag(d, x + w - 56, y + 16, 34, 20, "ru")
    d.rectangle([x + w // 2 - 26, y + h - 34, x + w // 2 + 26, y + h - 10],
                fill=(255, 255, 255), outline=INK, width=1)
    d.line([(x + w // 2 - 18, y + h - 26), (x + w // 2 + 18, y + h - 26)], fill=INK, width=1)
    d.line([(x + w // 2 - 18, y + h - 20), (x + w // 2 + 10, y + h - 20)], fill=INK, width=1)


def ill_flood(d, x, y, w, h):
    d.rectangle([x, y, x + w, y + h], fill=(180, 200, 215))
    for i in range(12):
        xx = x + 8 + (i * 17) % (w - 16)
        d.line([(xx, y + 4 + (i % 3) * 6), (xx - 3, y + 16 + (i % 3) * 6)],
               fill=(255, 255, 255), width=2)
    d.polygon([(x + 26, y + 34), (x + w // 2, y + 16), (x + w - 26, y + 34)], fill=(140, 60, 50))
    d.rectangle([x + 32, y + 34, x + w - 32, y + h - 16], fill=(240, 230, 210))
    d.rectangle([x + w // 2 - 8, y + h - 28, x + w // 2 + 8, y + h - 16], fill=(90, 70, 60))
    d.rectangle([x, y + h - 14, x + w, y + h], fill=(40, 110, 160))
    d.text((x + 8, y + h - 13), "300+ RESCUES", font=font(SANS_B, 10), fill=(255, 255, 255))


def ill_troops(d, x, y, w, h):
    d.rectangle([x, y, x + w, y + h], fill=(226, 214, 190))
    d.polygon([(x + 10, y + h - 14), (x + w // 2 - 8, y + 12), (x + w // 2 - 8, y + h - 14)],
              fill=(120, 90, 60))
    d.polygon([(x + w - 10, y + h - 14), (x + w // 2 + 8, y + 12), (x + w // 2 + 8, y + h - 14)],
              fill=(140, 50, 40))
    d.line([(x + w // 2, y + 10), (x + w // 2, y + h - 12)], fill=RED, width=2)
    for i in range(3):
        d.ellipse([x + 22 + i * 14, y + h - 34, x + 30 + i * 14, y + h - 26], fill=(60, 60, 60))
        d.ellipse([x + w - 30 - i * 14, y + h - 34, x + w - 22 - i * 14, y + h - 26],
                  fill=(60, 60, 60))


def ill_exam(d, x, y, w, h):
    d.rectangle([x, y, x + w, y + h], fill=(235, 232, 222))
    d.rectangle([x + 12, y + h - 26, x + w - 12, y + h - 18], fill=(150, 110, 70))
    d.rectangle([x + 20, y + h - 44, x + w - 40, y + h - 26], fill=(255, 255, 255),
                outline=INK, width=1)
    for i in range(3):
        d.line([(x + 26, y + h - 40 + i * 5), (x + w - 46, y + h - 40 + i * 5)],
               fill=(150, 150, 150), width=1)
    d.ellipse([x + w - 30, y + 8, x + w - 8, y + 30], fill=(255, 255, 255), outline=INK)
    d.line([(x + w - 19, y + 19), (x + w - 19, y + 12)], fill=INK, width=2)
    d.line([(x + w - 19, y + 19), (x + w - 14, y + 23)], fill=INK, width=2)
    d.text((x + 8, y + 6), "08:40", font=font(SANS_B, 12), fill=INK)


ILLUSTRATIONS = {1: ill_summit, 2: ill_gta, 3: ill_anthropic, 4: ill_court,
                 5: ill_climate, 6: ill_cyclone, 7: ill_bridge, 8: ill_tank,
                 9: ill_tanker, 10: ill_pact, 11: ill_flood, 12: ill_troops,
                 13: ill_exam}


# ---------------------------------------------------------------- build
def build(out_path):
    img = Image.new("RGB", (W, H), PAPER)
    d = ImageDraw.Draw(img)
    # frame
    d.rectangle([6, 6, W - 7, H - 7], outline=RED, width=2)
    d.rectangle([11, 11, W - 12, H - 12], outline=RED, width=1)
    MX = 22  # margin x
    CW = W - 2 * MX

    # ---- masthead
    y = 20
    d.text((MX, y), "THE WORLD IN ONE DAY", font=font(SANS_B, 13), fill=RED)
    meta = "48 STORIES · 7 REGIONS · ONE PAGE"
    d.text((W - MX - d.textlength(meta, font=font(SANS_B, 11)), y + 2), meta,
           font=font(SANS_B, 11), fill=INK)
    y = 38
    d.text((MX, y), "Thursday 19 November 2026", font=font(SERIF_BLK, 60), fill=INK)
    y = 108
    d.text((MX, y), "Three leaders meet in Shenzhen · A court rules on Myanmar · The biggest IPO ever debuts",
           font=font(SERIF_I, 17), fill=RED_DK)
    d.line([(MX, 132), (W - MX, 132)], fill=INK, width=2)

    # ---- region bar (equal segments so every label fits)
    all_stories = [(n, r) for n, r, *_ in FEATURED] + [(n, _region_of(n)) for n, _, _ in BRIEFS]
    counts = {r: sum(1 for _, rr in all_stories if rr == r) for r in REGIONS}
    y = 138
    x = MX
    seg_w = CW / 7
    for r in REGIONS:
        d.rectangle([x, y, x + seg_w - 1, y + 20], fill=REGION_COLORS[r])
        label = f"{REGION_SHORT[r]} {counts[r]}"
        fnt = font(SANS_B, 9)
        tw = d.textlength(label, font=fnt)
        d.text((x + (seg_w - tw) / 2, y + 5), label, font=fnt, fill=(255, 255, 255))
        x += seg_w

    # ---- UTC strip
    y = 164
    d.rectangle([MX, y, MX + 104, y + 22], fill=RED)
    d.text((MX + 8, y + 4), "THE DAY IN UTC", font=font(SANS_B, 10), fill=(255, 255, 255))
    xx = MX + 112
    for label, txt in UTC_STRIP:
        d.text((xx, y + 5), label, font=font(SANS_B, 9), fill=RED)
        tx = xx + d.textlength(label + "  ", font=font(SANS_B, 9))
        d.text((tx, y + 5), txt, font=font(SANS, 9), fill=INK)
        xx = tx + d.textlength(txt, font=font(SANS, 9)) + 16
        if label != UTC_STRIP[-1][0] or txt != UTC_STRIP[-1][1]:
            d.text((xx - 11, y + 5), "·", font=font(SANS, 9), fill=RED)

    # ---- numbers strip
    y = 192
    d.line([(MX, y), (W - MX, y)], fill=LINE, width=1)
    col_w = CW / 6
    for i, (num, cap) in enumerate(NUMBERS):
        cx = MX + i * col_w
        d.text((cx + 4, y + 5), num, font=font(SERIF_B, 21), fill=RED_DK)
        lines = fit_text(d, cap, font(SANS, 9), col_w - 10, max_lines=2)
        draw_text_block(d, cx + 4, y + 30, lines, font(SANS, 9), INK, 11)
        if i:
            d.line([(cx, y + 4), (cx, y + 52)], fill=LINE, width=1)
    d.line([(MX, y + 56), (W - MX, y + 56)], fill=LINE, width=1)

    # ---- hero row (3 cards)
    y0 = 254
    hero_h = 190
    gap = 8
    hw = (CW - 2 * gap) / 3
    for i, (n, region, kicker, source, headline, body) in enumerate(FEATURED[:3]):
        x = MX + i * (hw + gap)
        d.rectangle([x, y0, x + hw, y0 + hero_h], fill=CARD_BG, outline=INK, width=1)
        ILLUSTRATIONS[n](d, x + 1, y0 + 1, hw - 2, 92)
        yy = y0 + 98
        d.text((x + 6, yy), f"{n} · {kicker}", font=font(SANS_B, 10), fill=REGION_COLORS[region])
        sw = d.textlength(source, font=font(SANS, 8))
        d.text((x + hw - 6 - sw, yy + 1), source, font=font(SANS, 8), fill=GREY)
        yy += 15
        lines = fit_text(d, headline, font(SERIF_B, 18), hw - 12, max_lines=2)
        yy = draw_text_block(d, x + 6, yy, lines, font(SERIF_B, 18), INK, 20)
        lines = fit_text(d, body, font(SANS, 10), hw - 12, max_lines=3)
        draw_text_block(d, x + 6, yy + 2, lines, font(SANS, 10), INK, 12)

    # ---- medium rows (5 + 5)
    med_h = 124
    mw = (CW - 4 * gap) / 5
    for row in range(2):
        y0 = 452 + row * (med_h + gap)
        for i in range(5):
            n, region, kicker, source, headline, body = FEATURED[3 + row * 5 + i]
            x = MX + i * (mw + gap)
            d.rectangle([x, y0, x + mw, y0 + med_h], fill=CARD_BG, outline=INK, width=1)
            ILLUSTRATIONS[n](d, x + 1, y0 + 1, mw - 2, 52)
            yy = y0 + 57
            d.text((x + 5, yy), f"{n} · {kicker}", font=font(SANS_B, 8), fill=REGION_COLORS[region])
            yy += 12
            lines = fit_text(d, headline, font(SERIF_B, 13), mw - 10, max_lines=2)
            yy = draw_text_block(d, x + 5, yy, lines, font(SERIF_B, 13), INK, 14)
            lines = fit_text(d, body, font(SANS, 9), mw - 10, max_lines=2)
            draw_text_block(d, x + 5, yy + 1, lines, font(SANS, 9), INK, 11)

    # ---- lower section: map + briefs
    y0 = 714
    sec_h = 232
    map_w = 280
    d.text((MX, y0), "WHERE IT HAPPENED", font=font(SANS_B, 11), fill=RED)
    d.text((MX + map_w + 16, y0), "ALSO ON THURSDAY 19 NOVEMBER — 35 MORE STORIES",
           font=font(SANS_B, 11), fill=RED)
    my = y0 + 16
    mh = sec_h - 26
    # map box
    d.rectangle([MX, my, MX + map_w, my + mh], fill=(238, 234, 220), outline=INK, width=1)
    draw_map(d, MX, my, map_w, mh)
    # legend
    ly = my + mh + 4
    d.text((MX, ly), "Red numbers = stories 1–13. Positions approximate.",
           font=font(SANS, 8), fill=GREY)
    # briefs in 3 columns
    bx = MX + map_w + 16
    bw = (W - MX - bx) / 3
    cols = [BRIEFS[i::3] for i in range(3)]
    # distribute 35 as 12/12/11 by slicing in order instead
    cols = [BRIEFS[0:12], BRIEFS[12:24], BRIEFS[24:35]]
    for ci, col in enumerate(cols):
        cx = bx + ci * bw
        yy = my + 2
        for n, place, txt in col:
            place = {"Washington": "Wash.", "Cape Canaveral": "Cape Canav.",
                     "New Delhi": "Delhi"}.get(place, place)
            fnt_n = font(SANS_B, 9)
            fnt_t = font(SANS, 9)
            prefix = f"{n}  {place} — "
            pw = d.textlength(prefix, font=fnt_n)
            d.text((cx, yy), f"{n}", font=fnt_n, fill=RED)
            d.text((cx + d.textlength(f"{n}  ", font=fnt_n), yy), place,
                   font=fnt_n, fill=INK)
            avail = bw - pw - 4
            t = txt
            while t and d.textlength(t, font=fnt_t) > avail:
                t = t.rsplit(" ", 1)[0] if " " in t else t[:-1]
            if t != txt:
                t += "…"
            d.text((cx + pw, yy), t, font=fnt_t, fill=INK)
            yy += 16

    # ---- date check
    y0 = 950
    d.rectangle([MX, y0, W - MX, y0 + 34], outline=RED, width=1)
    d.rectangle([MX, y0, MX + 96, y0 + 34], fill=RED)
    d.text((MX + 8, y0 + 9), "DATE CHECK", font=font(SANS_B, 12), fill=(255, 255, 255))
    dc = ("Left out on purpose — first reported Wednesday 18 Nov: Voyager 1 one light-day out · "
          "Anthropic's $83 pricing · EU's €45bn Ukraine loan plan · House Democrats' 251–11 Jeffries vote · "
          "Van Gogh's $190.4m record · Alcaraz beats Medvedev.  Not yet: Cyclone Akvan's landfall (Fri) · "
          "COP31's final text (Fri).")
    lines = fit_text(d, dc, font(SANS, 10), W - MX - 96 - 16, max_lines=2)
    draw_text_block(d, MX + 104, y0 + 4, lines, font(SANS, 10), INK, 13)

    # ---- footer
    y0 = 990
    d.text((MX, y0), "Every story here happened, or was first reported, on Thursday 19 November 2026. "
                     "Claims are attributed, not stated as fact.",
           font=font(SANS, 9), fill=GREY)
    d.text((MX, y0 + 11), "Sources: Reuters, AP, AFP, BBC, Al Jazeera, Nikkei Asia, The Japan Times, NDTV, "
                          "IMD, ICJ, IAEA, Yonhap. Original drawings.",
           font=font(SANS, 9), fill=GREY)

    img.save(out_path, "PNG", optimize=True)
    return out_path


def _region_of(n):
    m = {14: "MIDEAST", 15: "ASIA-PACIFIC", 16: "ASIA-PACIFIC", 17: "MIDEAST",
         18: "EUROPE", 19: "ASIA-PACIFIC", 20: "EUROPE", 21: "MIDEAST",
         22: "THE AMERICAS", 23: "THE AMERICAS", 24: "EUROPE", 25: "AFRICA",
         26: "MIDEAST", 27: "OCEANIA", 28: "ASIA-PACIFIC", 29: "THE AMERICAS",
         30: "AFRICA", 31: "THE AMERICAS", 32: "THE AMERICAS", 33: "ASIA-PACIFIC",
         34: "EUROPE", 35: "THE AMERICAS", 36: "THE AMERICAS", 37: "ASIA-PACIFIC",
         38: "OCEANIA", 39: "MIDEAST", 40: "AFRICA", 41: "EUROPE",
         42: "THE AMERICAS", 43: "THE AMERICAS", 44: "WORLD", 45: "ASIA-PACIFIC",
         46: "MIDEAST", 47: "THE AMERICAS", 48: "THE AMERICAS"}
    return m[n]


def draw_map(d, x0, y0, w, h):
    lon0, lon1, lat0, lat1 = -170, 190, 78, -58

    def proj(lon, lat):
        return (x0 + (lon - lon0) / (lon1 - lon0) * w,
                y0 + (lat0 - lat) / (lat0 - lat1) * h)

    step = 5
    yy = y0 + 4
    while yy < y0 + h - 3:
        xx = x0 + 4
        while xx < x0 + w - 3:
            lon = lon0 + (xx - x0) / w * (lon1 - lon0)
            lat = lat0 - (yy - y0) / h * (lat0 - lat1)
            if any(point_in_poly(lon, lat, poly) for poly in CONTINENTS):
                d.ellipse([xx - 1.5, yy - 1.5, xx + 1.5, yy + 1.5], fill=(150, 140, 115))
            xx += step
        yy += step
    for n, (lon, lat) in PINS.items():
        px, py = proj(lon, lat)
        d.ellipse([px - 7, py - 7, px + 7, py + 7], fill=RED, outline=(255, 255, 255))
        t = str(n)
        fnt = font(SANS_B, 9)
        tw = d.textlength(t, font=fnt)
        d.text((px - tw / 2, py - 5), t, font=fnt, fill=(255, 255, 255))


if __name__ == "__main__":
    out = sys.argv[1] if len(sys.argv) > 1 else "entry.png"
    build(out)
    import os
    print(out, os.path.getsize(out), "bytes")
