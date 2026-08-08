#!/usr/bin/env python3
"""Generate a round sun for textures/environment/sun_vv.png and sun.png.

Vanilla's sun is a square: an 8x8 opaque block centred in a 32x32 texture,
shaded in three steps - a pale core (#FFFFD9), a mid tone (#FFFFAA) and a
saturated limb (#FFD54A). This redraws it as a disc of the *same apparent
diameter* (a quarter of the texture width), so the sun does not change size in
the sky - only its silhouette. The texture is rendered at 4x vanilla's
resolution because a circle of radius 4 texels is just an octagon.

Two files, because the game uses two:

- sun_vv.png is the Vibrant Visuals sun and is alpha masked, so the disc is
  drawn with an antialiased alpha edge and nothing around it. The glow around
  the sun in Vibrant Visuals comes from Mie scattering in atmospherics/, not
  from this texture, so adding a painted halo here would double it up.
- sun.png is the classic (non-Vibrant) sun, drawn additively against black,
  where black reads as transparent. That one keeps a soft radial falloff,
  matching how vanilla paints its glow.
"""

from __future__ import annotations

import struct
import zlib
from pathlib import Path

SIZE = 128
DIAMETER = 0.25  # of the texture width; measured from vanilla's 8-of-32 square
SAMPLES = 4  # supersampling per axis, for a smooth edge

CORE = (255, 255, 217)
MID = (255, 255, 170)
LIMB = (255, 213, 74)

Color = tuple[int, int, int]


def lerp(a: Color, b: Color, t: float) -> Color:
    t = max(0.0, min(1.0, t))
    return tuple(round(a[i] + (b[i] - a[i]) * t) for i in range(3))  # type: ignore[return-value]


def disc_color(r: float) -> Color:
    """Vanilla's three tones, blended smoothly from centre to limb."""
    if r < 0.55:
        return lerp(CORE, MID, r / 0.55)
    return lerp(MID, LIMB, (r - 0.55) / 0.45)


def sample(x: int, y: int, radius: float) -> tuple[Color, float]:
    """Supersampled colour and coverage for one texel."""
    centre = SIZE / 2.0
    hits = 0
    weighted = [0.0, 0.0, 0.0]
    for sy in range(SAMPLES):
        for sx in range(SAMPLES):
            px = x + (sx + 0.5) / SAMPLES - centre
            py = y + (sy + 0.5) / SAMPLES - centre
            dist = (px * px + py * py) ** 0.5
            if dist <= radius:
                hits += 1
                colour = disc_color(dist / radius)
                for i in range(3):
                    weighted[i] += colour[i]
    if not hits:
        return (0, 0, 0), 0.0
    return tuple(round(v / hits) for v in weighted), hits / (SAMPLES ** 2)  # type: ignore[return-value]


def glow(x: int, y: int, radius: float) -> float:
    """Warm falloff outside the disc, for the additive classic sun only."""
    centre = SIZE / 2.0
    dist = (((x + 0.5) - centre) ** 2 + ((y + 0.5) - centre) ** 2) ** 0.5
    if dist <= radius:
        return 0.0
    t = (dist - radius) / (centre - radius)
    return max(0.0, 0.13 * (1.0 - min(1.0, t)) ** 3)


def write_png(path: Path, rows: bytearray, channels: int) -> None:
    def chunk(tag: bytes, data: bytes) -> bytes:
        return (struct.pack(">I", len(data)) + tag + data
                + struct.pack(">I", zlib.crc32(tag + data) & 0xFFFFFFFF))

    png = b"\x89PNG\r\n\x1a\n"
    png += chunk(b"IHDR", struct.pack(">IIBBBBB", SIZE, SIZE, 8,
                                      6 if channels == 4 else 2, 0, 0, 0))
    png += chunk(b"IDAT", zlib.compress(bytes(rows), 9))
    png += chunk(b"IEND", b"")
    path.write_bytes(png)


def build() -> tuple[bytearray, bytearray]:
    radius = SIZE * DIAMETER / 2.0
    vv = bytearray()
    classic = bytearray()
    for y in range(SIZE):
        vv.append(0)
        classic.append(0)
        for x in range(SIZE):
            colour, coverage = sample(x, y, radius)
            vv += bytes((*colour, round(coverage * 255)))

            halo = glow(x, y, radius)
            lit = tuple(
                min(255, round(colour[i] * coverage + LIMB[i] * halo))
                for i in range(3)
            )
            classic += bytes(lit)
    return vv, classic


def main() -> None:
    out = Path(__file__).resolve().parent.parent / "pack" / "textures" / "environment"
    out.mkdir(parents=True, exist_ok=True)
    vv, classic = build()
    write_png(out / "sun_vv.png", vv, 4)
    write_png(out / "sun.png", classic, 3)
    for name in ("sun_vv.png", "sun.png"):
        print(f"wrote {out / name} ({(out / name).stat().st_size} bytes)")


if __name__ == "__main__":
    main()
