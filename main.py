#!/usr/bin/env python3
"""Copy the committed meme image to /output/entry.png.

The meme (meme.png, rendered at build time) sits next to this script.
The asset path is resolved from the script's own directory, never from
the caller's working directory, so the program runs from anywhere.
"""

import os
import shutil
import struct
import sys

ASSET = "meme.png"
OUTPUT = os.path.join("/output", "entry.png")

# The bounty's sealed gate: a whole PNG or JPEG, at most 1 MiB and at
# most 1024x1024 pixels. Validate the asset before copying so a bad
# render fails loudly here instead of scoring Valid = 0 at the gate.
MAX_BYTES = 1_048_576
MAX_DIM = 1024
PNG_SIGNATURE = b"\x89PNG\r\n\x1a\n"
JPEG_SIGNATURE = b"\xff\xd8"


def validate_image(path):
    """Return an error string if the asset breaks the gate, else None."""
    size = os.path.getsize(path)
    if size > MAX_BYTES:
        return f"asset is {size} bytes, over the {MAX_BYTES}-byte gate limit"
    with open(path, "rb") as fh:
        head = fh.read(24)
    if head.startswith(PNG_SIGNATURE):
        width, height = struct.unpack(">II", head[16:24])
        if width > MAX_DIM or height > MAX_DIM:
            return f"asset is {width}x{height}, over the {MAX_DIM}px gate limit"
        return None
    if head.startswith(JPEG_SIGNATURE):
        return None  # JPEG: the size gate above applies; dimensions unchecked
    return "asset is neither PNG nor JPEG"


def main() -> int:
    here = os.path.dirname(os.path.abspath(__file__))
    src = os.path.join(here, ASSET)
    if not os.path.isfile(src):
        print(f"error: asset not found: {src}", file=sys.stderr)
        return 1
    problem = validate_image(src)
    if problem is not None:
        print(f"error: {problem}", file=sys.stderr)
        return 1
    os.makedirs(os.path.dirname(OUTPUT), exist_ok=True)
    shutil.copyfile(src, OUTPUT)
    print(f"wrote {OUTPUT} from {src}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
