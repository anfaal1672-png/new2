#!/usr/bin/env python3
"""Generate pack_icon.png without any third-party imaging library.

The icon is drawn procedurally: a graded sky, a lit ground plane, a blocky
character and the long directional shadow it casts - i.e. the whole point of
the pack in one image. Written as a plain RGB PNG through zlib.
"""

from __future__ import annotations

import struct
import zlib
from pathlib import Path

SIZE = 256
HORIZON = 150

Color = tuple[int, int, int]


def lerp(a: Color, b: Color, t: float) -> Color:
    t = max(0.0, min(1.0, t))
    return tuple(round(a[i] + (b[i] - a[i]) * t) for i in range(3))  # type: ignore[return-value]


def mix(dst: Color, src: Color, alpha: float) -> Color:
    return lerp(dst, src, alpha)


def sky(y: int) -> Color:
    t = y / HORIZON
    if t < 0.55:
        return lerp((26, 38, 68), (86, 108, 150), t / 0.55)
    return lerp((86, 108, 150), (240, 186, 122), (t - 0.55) / 0.45)


def ground(y: int) -> Color:
    t = (y - HORIZON) / (SIZE - HORIZON)
    return lerp((150, 132, 96), (96, 84, 62), t)


def in_character(x: int, y: int) -> bool:
    # head + body, deliberately blocky
    if 108 <= x < 148 and 62 <= y < 102:
        return True
    if 114 <= x < 142 and 102 <= y < 158:
        return True
    return False


def in_shadow(x: int, y: int) -> bool:
    """The character's silhouette projected along the light direction."""
    if y < HORIZON:
        return False
    depth = (y - HORIZON) / (SIZE - HORIZON)  # 0 at horizon, 1 at bottom
    # Skew and stretch the footprint away from the low sun.
    sx = x + round(depth * 74)
    half = 16 + depth * 16
    return 112 - half + 16 <= sx <= 112 + half + 16 and depth <= 1.0


def build_rows() -> list[bytearray]:
    rows: list[bytearray] = []
    for y in range(SIZE):
        row = bytearray()
        for x in range(SIZE):
            if y < HORIZON:
                px = sky(y)
                # soft sun glow near the horizon on the right
                d = ((x - 214) ** 2 + (y - 136) ** 2) ** 0.5
                if d < 70:
                    px = mix(px, (255, 236, 196), max(0.0, 1.0 - d / 70) ** 2.2)
            else:
                px = ground(y)
                if in_shadow(x, y):
                    # shadow fades with distance, and stays blue rather than black
                    depth = (y - HORIZON) / (SIZE - HORIZON)
                    px = mix(px, (38, 46, 74), 0.72 - 0.3 * depth)

            if in_character(x, y):
                lit = x > 128
                px = (206, 176, 132) if lit else (92, 78, 62)

            row += bytes(px)
        rows.append(row)
    return rows


def write_png(path: Path, rows: list[bytearray]) -> None:
    raw = b"".join(b"\x00" + bytes(r) for r in rows)

    def chunk(tag: bytes, data: bytes) -> bytes:
        return (
            struct.pack(">I", len(data))
            + tag
            + data
            + struct.pack(">I", zlib.crc32(tag + data) & 0xFFFFFFFF)
        )

    png = b"\x89PNG\r\n\x1a\n"
    png += chunk(b"IHDR", struct.pack(">IIBBBBB", SIZE, SIZE, 8, 2, 0, 0, 0))
    png += chunk(b"IDAT", zlib.compress(raw, 9))
    png += chunk(b"IEND", b"")
    path.write_bytes(png)


def main() -> None:
    out = Path(__file__).resolve().parent.parent / "pack" / "pack_icon.png"
    write_png(out, build_rows())
    print(f"wrote {out} ({out.stat().st_size} bytes)")


if __name__ == "__main__":
    main()
