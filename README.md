# The World in One Day — Thursday 19 November 2026

Entry for the make.fun bounty **"Sum up 19 November's world news in one image"**
(https://make.fun/bounty/news-image-20261119).

## What it is

A one-page newspaper front page that sums up Thursday 19 November 2026's
world news in a single 1024×1024 PNG:

- **48 verified stories across 7 regions** — Europe 7, The Americas 14,
  Asia-Pacific 10, Mideast 8, Africa 4, Oceania 2, World 3
- A **"The Day in UTC"** timeline strip (GTA VI on sale overnight → Shenzhen
  summit in the morning → ICJ Rohingya ruling → Crimea Bridge hit → ANT
  starts trading → COP31 talks go late)
- A **"Day in numbers"** strip: $81.3bn (Anthropic IPO), 15.9m (GTA VI
  pre-orders), 80,000+ (evacuated ahead of Cyclone Akvan), 730,000 (Rohingya
  who fled in 2017), 90 min (Shenzhen trilateral), 551,864 (Korea's Suneung)
- **3 hero stories** with original flat illustrations: the first-ever
  Trump–Xi–Putin trilateral in Shenzhen, GTA VI's launch after a 13-year
  wait, and Anthropic's Nasdaq debut in the biggest IPO on record
- **10 more illustrated feature stories**: the ICJ's Rohingya genocide
  ruling, COP31's final 48 hours, Cyclone Akvan, the Crimean Bridge struck
  again, Israel's Gaza push past the Yellow Line, three tankers hit by mines
  off Hormuz, the US–Venezuela defence pact, South Florida flooding,
  Ethiopia–Eritrea tensions, and Korea's Suneung exam
- A **dotted world map** ("Where it happened") with numbered pins for the
  13 feature stories, plus **35 one-line briefs**
- A **Date Check** box listing what was deliberately left out because it
  was first reported on Wednesday 18 November (Voyager 1's one-light-day
  milestone, Anthropic's $83 pricing, the EU's €45bn Ukraine loan plan,
  the House Democrats' 251–11 Jeffries vote, Van Gogh's $190.4m record,
  Alcaraz beating Medvedev) and what had not happened yet (Akvan's
  landfall, COP31's final text)
- Every story is sourced (Reuters, AP, AFP, BBC, Al Jazeera, Nikkei Asia,
  The Japan Times, NDTV, IMD, ICJ, IAEA, Yonhap) and claims are attributed,
  not stated as fact

## Files

| File | Purpose |
|---|---|
| `main.py` | Entry point. Copies `entry.png` to `/output/entry.png`. Deterministic: two runs write identical bytes. No network. |
| `entry.png` | The final image (1024×1024, ~211 KB, under the 1 MiB limit). |
| `generate_image.py` | The program that built `entry.png` from scratch with PIL: layout, typography (Noto Serif Display / Noto Serif / Noto Sans), flat vector-style illustrations, and the dotted world map. Pure Python, no network, no external assets. Run `python3 generate_image.py entry.png` to regenerate it byte-identically. |
| `README.md` | This file. |
| `LICENSE` | MIT. |

## How the image was made

1. The bounty page and the finished 17/18 November editions were studied
   first: the top-5 entries on each day were downloaded from make.fun's
   public API and viewed, and the winning pattern was written down (see
   the research notes in the build log).
2. The day's news was researched from multiple reputable sources and
   cross-checked for date: only stories that happened or were first
   reported on Thursday 19 November 2026 are in the 48; Wednesday's
   stories are named in the Date Check box instead.
3. `generate_image.py` draws the page and was iterated four times against
   the winning pattern until every line of text fits, nothing is clipped,
   and the layout is clean at full size.

## Regenerating

```sh
python3 generate_image.py entry.png   # rebuild the image
python3 main.py                        # writes /output/entry.png
```
