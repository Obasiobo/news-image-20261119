#!/usr/bin/env python3
"""make.fun entry: "Sum up 19 November's world news in one image".

Writes the entry image to /output/entry.png.

The image itself (entry.png, bundled in this repository) is a front-page
summary of Thursday 19 November 2026's world news: 48 verified stories
across 7 regions, drawn as a newspaper front page with a UTC timeline,
a day-in-numbers strip, 13 illustrated feature stories, a dotted world
map and a date check. It was built by generate_image.py (also in this
repository), a pure-PIL program that draws every element from scratch:
no network, no photos, no external assets.

This entrypoint is intentionally trivial and deterministic, as the
bounty brief allows ("the simplest program copies an image the
repository holds"): it copies the bundled image to /output/entry.png,
so two runs write exactly the same bytes.
"""

import os
import shutil
import sys

HERE = os.path.dirname(os.path.abspath(__file__))


def main() -> None:
    src = os.path.join(HERE, "entry.png")
    out_dir = "/output"
    os.makedirs(out_dir, exist_ok=True)
    dst = os.path.join(out_dir, "entry.png")
    shutil.copyfile(src, dst)
    print(f"wrote {dst} ({os.path.getsize(dst)} bytes)")


if __name__ == "__main__":
    sys.exit(main())
