#!/usr/bin/env python3
"""Entry point for the news-image-20261125 competition.

Copies the shipped entry.png (drawn by generate_image.py in this
repository from news verified on 25 November 2026) into the output
directory. Standard library only, no network, no randomness: every
run writes exactly the same bytes.
"""

import hashlib
import os
import sys
from pathlib import Path

PNG_SIGNATURE = b"\x89PNG\r\n\x1a\n"
MAX_BYTES = 1024 * 1024  # the gate allows at most 1 MiB
MAX_EDGE = 1024          # and at most 1024 x 1024 pixels


def fail(message: str) -> None:
    print(f"error: {message}", file=sys.stderr)
    raise SystemExit(1)


def main() -> None:
    repo = Path(__file__).resolve().parent
    source = repo / "entry.png"
    if not source.is_file():
        fail("entry.png is missing from the repository")

    payload = source.read_bytes()
    if not payload:
        fail("entry.png is empty")
    if len(payload) > MAX_BYTES:
        fail(f"entry.png is {len(payload)} bytes, over the 1 MiB limit")
    if payload[:8] != PNG_SIGNATURE:
        fail("entry.png does not start with the PNG signature")

    # The IHDR chunk follows the signature: length (4) + "IHDR" (4),
    # then width and height as big-endian 32-bit integers.
    if len(payload) < 24 or payload[12:16] != b"IHDR":
        fail("entry.png has no IHDR chunk where one belongs")
    width = int.from_bytes(payload[16:20], "big")
    height = int.from_bytes(payload[20:24], "big")
    if width == 0 or width > MAX_EDGE:
        fail(f"entry.png width {width} is outside the allowed range")
    if height == 0 or height > MAX_EDGE:
        fail(f"entry.png height {height} is outside the allowed range")

    # A whole PNG ends with the IEND chunk: length 0, "IEND", CRC.
    if not payload.endswith(b"\x00\x00\x00\x00IEND\xaeB`\x82"):
        fail("entry.png does not end with the IEND chunk; it may be truncated")

    out_dir = Path(os.environ.get("MAKEFUN_OUTPUT_DIR", "/output"))
    out_dir.mkdir(parents=True, exist_ok=True)

    staging = out_dir / "entry.png.partial"
    staging.write_bytes(payload)
    os.replace(staging, out_dir / "entry.png")

    digest = hashlib.sha256(payload).hexdigest()[:12]
    print(f"entry.png written: {len(payload)} bytes, sha256 {digest}")


if __name__ == "__main__":
    main()
