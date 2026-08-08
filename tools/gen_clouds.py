#!/usr/bin/env python3
"""Generate textures/environment/clouds.png - organic cloud masses, vanilla cost.

Minecraft builds cloud geometry from this texture: every opaque texel becomes a
cloud cell, and the alpha channel is a hard mask (vanilla uses only 0 and 255).
So the shapes are free to change but the *amount* of opaque texel is not - it is
the pack's cloud budget. Vanilla covers 27.6% of the sky, and this generator
solves for a threshold that lands on the same coverage, so a prettier sky costs
the same to draw.

The noise lattice wraps, because the cloud plane tiles: a seam would appear as a
straight edge running across the sky.
"""

from __future__ import annotations

import random
import struct
import zlib
from pathlib import Path

SIZE = 256
COVERAGE = 0.276  # measured from the vanilla texture
OCTAVES = ((12, 1.0), (24, 0.55), (48, 0.28), (96, 0.14))
SEED = 20260808
MIN_ISLAND = 10  # drop cloud specks smaller than this (texels)
MIN_HOLE = 8  # and fill pinholes, which read as noise rather than sky


def smoothstep(t: float) -> float:
    return t * t * (3.0 - 2.0 * t)


def octave(cells: int, rng: random.Random) -> list[list[float]]:
    """Value noise on a `cells`x`cells` lattice, wrapping at the edges."""
    lattice = [[rng.random() for _ in range(cells)] for _ in range(cells)]
    step = SIZE / cells
    field = [[0.0] * SIZE for _ in range(SIZE)]
    for y in range(SIZE):
        gy, fy = divmod(y / step, 1.0)
        y0 = int(gy) % cells
        y1 = (y0 + 1) % cells
        wy = smoothstep(fy)
        for x in range(SIZE):
            gx, fx = divmod(x / step, 1.0)
            x0 = int(gx) % cells
            x1 = (x0 + 1) % cells
            wx = smoothstep(fx)
            top = lattice[y0][x0] * (1 - wx) + lattice[y0][x1] * wx
            bot = lattice[y1][x0] * (1 - wx) + lattice[y1][x1] * wx
            field[y][x] = top * (1 - wy) + bot * wy
    return field


def fractal() -> list[list[float]]:
    rng = random.Random(SEED)
    field = [[0.0] * SIZE for _ in range(SIZE)]
    for cells, amplitude in OCTAVES:
        layer = octave(cells, rng)
        for y in range(SIZE):
            row, src = field[y], layer[y]
            for x in range(SIZE):
                row[x] += src[x] * amplitude
    return field


def threshold_for_coverage(field: list[list[float]]) -> float:
    values = sorted(v for row in field for v in row)
    return values[int(len(values) * (1.0 - COVERAGE))]


def regions(mask: list[bytearray], target: int) -> list[list[tuple[int, int]]]:
    """Connected components of `target` value, with wrap-around neighbours."""
    seen = [bytearray(SIZE) for _ in range(SIZE)]
    found: list[list[tuple[int, int]]] = []
    for sy in range(SIZE):
        for sx in range(SIZE):
            if seen[sy][sx] or mask[sy][sx] != target:
                continue
            stack = [(sy, sx)]
            seen[sy][sx] = 1
            group: list[tuple[int, int]] = []
            while stack:
                y, x = stack.pop()
                group.append((y, x))
                for dy, dx in ((1, 0), (-1, 0), (0, 1), (0, -1)):
                    ny, nx = (y + dy) % SIZE, (x + dx) % SIZE
                    if not seen[ny][nx] and mask[ny][nx] == target:
                        seen[ny][nx] = 1
                        stack.append((ny, nx))
            found.append(group)
    return found


def build_mask() -> list[bytearray]:
    field = fractal()
    cut = threshold_for_coverage(field)
    mask = [bytearray(1 if field[y][x] >= cut else 0 for x in range(SIZE))
            for y in range(SIZE)]

    for group in regions(mask, 1):
        if len(group) < MIN_ISLAND:
            for y, x in group:
                mask[y][x] = 0
    for group in regions(mask, 0):
        if len(group) < MIN_HOLE:
            for y, x in group:
                mask[y][x] = 1
    return mask


def write_png(path: Path, mask: list[bytearray]) -> float:
    rows = bytearray()
    opaque = 0
    for y in range(SIZE):
        rows.append(0)
        for x in range(SIZE):
            a = 255 if mask[y][x] else 0
            opaque += bool(a)
            rows += bytes((255, 255, 255, a))

    def chunk(tag: bytes, data: bytes) -> bytes:
        return (struct.pack(">I", len(data)) + tag + data
                + struct.pack(">I", zlib.crc32(tag + data) & 0xFFFFFFFF))

    png = b"\x89PNG\r\n\x1a\n"
    png += chunk(b"IHDR", struct.pack(">IIBBBBB", SIZE, SIZE, 8, 6, 0, 0, 0))
    png += chunk(b"IDAT", zlib.compress(bytes(rows), 9))
    png += chunk(b"IEND", b"")
    path.write_bytes(png)
    return opaque / (SIZE * SIZE)


def main() -> None:
    out = Path(__file__).resolve().parent.parent / "pack" / "textures" / "environment"
    out.mkdir(parents=True, exist_ok=True)
    target = out / "clouds.png"
    coverage = write_png(target, build_mask())
    print(f"wrote {target} ({target.stat().st_size} bytes, {coverage:.1%} coverage, "
          f"vanilla is {COVERAGE:.1%})")


if __name__ == "__main__":
    main()
