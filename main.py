#!/usr/bin/env python3
"""Entrypoint for the news-image-20261124 make.fun submission.

The poster image is pre-rendered and committed to this repository as
entry.png. This script only validates that image and copies its exact
bytes to the output directory, using the standard library only.

No network access, no browser, no rendering happens at runtime.
"""

import hashlib
import os
import struct
import sys

# Official PNG signature: the first eight bytes of every PNG file.
PNG_SIGNATURE = b"\x89PNG\r\n\x1a\n"

# The poster is a square 1024x1024 image.
EXPECTED_WIDTH = 1024
EXPECTED_HEIGHT = 1024

# Submissions cap a single output file at 1 MiB.
MAX_FILE_SIZE = 1024 * 1024


def fail(message):
    """Print an error to stderr and exit non-zero."""
    print("error: %s" % message, file=sys.stderr)
    sys.exit(1)


def main():
    here = os.path.dirname(os.path.abspath(__file__))
    source_path = os.path.join(here, "entry.png")

    if not os.path.isfile(source_path):
        fail("entry.png not found next to main.py: %s" % source_path)

    size = os.path.getsize(source_path)
    if size > MAX_FILE_SIZE:
        fail(
            "entry.png is %d bytes, over the %d byte limit"
            % (size, MAX_FILE_SIZE)
        )
    if size < 8 + 25:  # signature plus a minimal IHDR chunk
        fail("entry.png is too small to be a valid PNG (%d bytes)" % size)

    with open(source_path, "rb") as handle:
        data = handle.read()

    if len(data) != size:
        fail("entry.png changed size while being read")

    if data[:8] != PNG_SIGNATURE:
        fail("entry.png does not start with the PNG signature")

    # The first chunk must be IHDR: 4-byte length, "IHDR", 13-byte payload.
    length = struct.unpack(">I", data[8:12])[0]
    chunk_type = data[12:16]
    if chunk_type != b"IHDR":
        fail("first PNG chunk is %r, expected IHDR" % chunk_type)
    if length != 13:
        fail("IHDR chunk has length %d, expected 13" % length)

    width, height = struct.unpack(">II", data[16:24])
    if width != EXPECTED_WIDTH or height != EXPECTED_HEIGHT:
        fail(
            "entry.png is %dx%d, expected %dx%d"
            % (width, height, EXPECTED_WIDTH, EXPECTED_HEIGHT)
        )

    output_dir = os.environ.get("MAKEFUN_OUTPUT_DIR") or "/output"
    os.makedirs(output_dir, exist_ok=True)
    output_path = os.path.join(output_dir, "entry.png")

    # Single write: the output is a byte-for-byte copy of the source,
    # so the submitted image is exactly the reviewed entry.png.
    with open(output_path, "wb") as handle:
        handle.write(data)

    written = os.path.getsize(output_path)
    if written != size:
        fail(
            "output file is %d bytes, expected %d bytes" % (written, size)
        )

    digest = hashlib.sha256(data).hexdigest()
    print(
        "wrote %s (%d bytes, sha256 %s)" % (output_path, size, digest)
    )
    return 0


if __name__ == "__main__":
    sys.exit(main())
