#!/usr/bin/env python3
"""Build the Kage Shadows resource pack into installable .mcpack files.

Usage:
    python3 tools/build.py                 # build every variant
    python3 tools/build.py default lite    # build only the named variants

Output lands in dist/: an unpacked folder plus a zipped .mcpack per variant.
The source of truth is pack/; variants are produced by patching the parsed
JSON in memory, so there is only ever one copy of the settings to maintain.
"""

from __future__ import annotations

import argparse
import json
import shutil
import sys
import uuid
import zipfile
from pathlib import Path
from typing import Any, Callable

ROOT = Path(__file__).resolve().parent.parent
PACK = ROOT / "pack"
DIST = ROOT / "dist"
BIOME_MAP = ROOT / "tools" / "biome_map.json"
VANILLA_BIOMES = ROOT / "vendor" / "bedrock-samples" / "biomes"

# Stable namespace so a rebuild keeps the same pack UUIDs and Minecraft treats
# the result as an update of the installed pack rather than a second copy.
NAMESPACE = uuid.UUID("b2a01a91-1938-4270-80ef-f4f8f30f9ab8")


# --------------------------------------------------------------------------
# variants
# --------------------------------------------------------------------------

def patch_lite(pack: dict[str, Any]) -> None:
    """Cheapest configuration: blocky shadows, low-cost tone mapping, flat grade."""
    pack["shadows/global.json"]["minecraft:shadow_settings"] = {
        "shadow_style": "blocky_shadows",
        "texel_size": 16,
    }
    for name, doc in pack.items():
        if name.startswith("color_grading/"):
            settings = doc["minecraft:color_grading_settings"]
            settings["tone_mapping"]["operator"] = "reinhard_luminance"
            grading = settings["color_grading"]
            # Per-luminance grading is the most expensive part of the grade and
            # the least visible on low-end hardware; keep midtones only.
            grading.pop("highlights", None)
            grading.pop("shadows", None)
        if name.startswith("lighting/"):
            sky = doc["minecraft:lighting_settings"]["sky"]
            # Slightly brighter indirect light so shadow interiors stay readable
            # without any highlight/shadow grading to lift them.
            sky["intensity"] = round(min(1.0, sky["intensity"] * 1.15), 3)


def patch_cinematic(pack: dict[str, Any]) -> None:
    """Deeper, more contrasted shadows and a filmic curve."""
    for name, doc in pack.items():
        if name.startswith("lighting/"):
            settings = doc["minecraft:lighting_settings"]
            sky = settings["sky"]
            sky["intensity"] = round(max(0.1, sky["intensity"] * 0.82), 3)
            ambient = settings["ambient"]
            ambient["illuminance"] = round(ambient["illuminance"] * 0.8, 4)
        if name.startswith("color_grading/"):
            settings = doc["minecraft:color_grading_settings"]
            settings["tone_mapping"]["operator"] = "aces"
            grading = settings["color_grading"]
            midtones = grading["midtones"]
            midtones["contrast"] = [round(v * 1.06, 3) for v in midtones["contrast"]]
            midtones["saturation"] = [round(v * 1.04, 3) for v in midtones["saturation"]]
            if "shadows" in grading:
                grading["shadows"]["shadowsMax"] = min(
                    1.0, round(grading["shadows"]["shadowsMax"] + 0.1, 3)
                )


VARIANTS: dict[str, dict[str, Any]] = {
    "default": {
        "suffix": "",
        "name_en": "Kage Shadows",
        "name_ja": "影 Kage Shadows",
        "patch": None,
    },
    "lite": {
        "suffix": " Lite",
        "name_en": "Kage Shadows Lite",
        "name_ja": "影 Kage Shadows Lite",
        "patch": patch_lite,
    },
    "cinematic": {
        "suffix": " Cinematic",
        "name_en": "Kage Shadows Cinematic",
        "name_ja": "影 Kage Shadows Cinematic",
        "patch": patch_cinematic,
    },
}


# --------------------------------------------------------------------------
# build
# --------------------------------------------------------------------------

def load_pack() -> tuple[dict[str, Any], dict[str, bytes]]:
    """Split the source pack into parsed JSON documents and verbatim assets."""
    docs: dict[str, Any] = {}
    assets: dict[str, bytes] = {}
    for path in sorted(PACK.rglob("*")):
        if not path.is_file():
            continue
        rel = path.relative_to(PACK).as_posix()
        if path.suffix == ".json":
            with path.open(encoding="utf-8") as fh:
                docs[rel] = json.load(fh)
        else:
            assets[rel] = path.read_bytes()
    return docs, assets


def client_biome(biome: str, profile: dict[str, Any]) -> dict[str, Any]:
    """Vanilla's definition for `biome` with this pack's identifiers swapped in.

    A client biome file in a resource pack stands in for the vanilla file of the
    same name, and vanilla's definition carries fog, water colour, ambient
    sounds, music and foliage tints besides the lighting identifiers. Writing a
    two-component file of our own would drop all of that, so we start from the
    vanilla definition and only replace what this pack actually owns.
    """
    source = VANILLA_BIOMES / f"{biome}.client_biome.json"
    if not source.exists():
        raise SystemExit(
            f"missing vanilla definition for '{biome}': "
            f"run python3 tools/fetch_vanilla_biomes.py"
        )
    with source.open(encoding="utf-8") as fh:
        doc = json.load(fh)

    components = doc["minecraft:client_biome"]["components"]
    components["minecraft:lighting_identifier"] = {
        "lighting_identifier": profile["lighting_identifier"]
    }
    components["minecraft:color_grading_identifier"] = {
        "color_grading_identifier": profile["color_grading_identifier"]
    }
    return doc


def add_biomes(docs: dict[str, Any]) -> int:
    with BIOME_MAP.open(encoding="utf-8") as fh:
        profiles = json.load(fh)["profiles"]

    seen: set[str] = set()
    for profile_name, profile in profiles.items():
        for biome in profile["biomes"]:
            if biome in seen:
                raise SystemExit(
                    f"biome '{biome}' is listed in more than one profile "
                    f"(second occurrence in '{profile_name}')"
                )
            seen.add(biome)
            docs[f"biomes/{biome}.client_biome.json"] = client_biome(biome, profile)
    return len(seen)


def apply_identity(docs: dict[str, Any], assets: dict[str, bytes], variant: str) -> None:
    spec = VARIANTS[variant]
    manifest = docs["manifest.json"]
    manifest["header"]["uuid"] = str(uuid.uuid5(NAMESPACE, f"{variant}:header"))
    manifest["modules"][0]["uuid"] = str(uuid.uuid5(NAMESPACE, f"{variant}:resources"))

    for lang, key in (("en_US", "name_en"), ("ja_JP", "name_ja")):
        rel = f"texts/{lang}.lang"
        lines = assets[rel].decode("utf-8").splitlines()
        lines = [
            f"pack.name={spec[key]}" if line.startswith("pack.name=") else line
            for line in lines
        ]
        assets[rel] = ("\n".join(lines) + "\n").encode("utf-8")


def check_lighting_schema(docs: dict[str, Any]) -> None:
    """Lighting settings must declare a schema version that matches their shape.

    The sun/moon moved under a "directional_lights.orbital" wrapper in schema
    1.21.80, the same version that added "flash". Declaring an older version
    while using the newer shape makes the client report the sun and moon as
    missing required fields, and colours get parsed under the pre-1.21.60 RGBA
    rules. Colours are written as explicit component arrays for the same
    reason: a 6-digit hex string is only valid under the RGB-era schemas.
    """
    for name, doc in docs.items():
        if not name.startswith("lighting/"):
            continue
        version = tuple(int(part) for part in doc["format_version"].split("."))
        lights = doc["minecraft:lighting_settings"]["directional_lights"]
        if ("orbital" in lights or "flash" in lights) and version < (1, 21, 80):
            raise SystemExit(
                f"{name}: 'orbital'/'flash' need format_version 1.21.80 or newer, "
                f"got {doc['format_version']}"
            )
        for label, value in walk_colors(doc):
            if isinstance(value, str):
                raise SystemExit(
                    f"{name}: write {label} as a component array instead of the "
                    f"hex string {value!r}"
                )

        # The sun and moon are keyframed in the vanilla pack, and a constant
        # there is reported as "Expected keyframes." Keep every orbital value a
        # keyframe map, even when it holds a single value at both ends.
        orbital = lights["orbital"]
        for body in ("sun", "moon"):
            for field in ("illuminance", "color"):
                if not isinstance(orbital[body][field], dict):
                    raise SystemExit(
                        f"{name}: {body}.{field} must be a keyframe map, "
                        f"not a constant"
                    )


def walk_colors(node: Any, path: str = "") -> list[tuple[str, Any]]:
    """Collect every value stored under a "color" key, keyframes included."""
    found: list[tuple[str, Any]] = []
    if isinstance(node, dict):
        for key, value in node.items():
            here = f"{path}.{key}" if path else key
            if key == "color":
                if isinstance(value, dict):  # keyframed colour
                    found += [(f"{here}[{k}]", v) for k, v in value.items()]
                else:
                    found.append((here, value))
            else:
                found += walk_colors(value, here)
    return found


def check_invariants(docs: dict[str, Any]) -> None:
    """Guard the two things Vibrant Visuals refuses to blend between biomes."""
    operators = {
        doc["minecraft:color_grading_settings"]["tone_mapping"]["operator"]
        for name, doc in docs.items()
        if name.startswith("color_grading/")
    }
    if len(operators) > 1:
        raise SystemExit(f"tone mapping operators must match across the pack: {operators}")

    offsets = {
        doc["minecraft:lighting_settings"]["directional_lights"]["orbital"][
            "orbital_offset_degrees"
        ]
        for name, doc in docs.items()
        if name.startswith("lighting/")
    }
    if len(offsets) > 1:
        raise SystemExit(f"orbital_offset_degrees must match across the pack: {offsets}")


def build(variant: str) -> Path:
    docs, assets = load_pack()
    patch: Callable[[dict[str, Any]], None] | None = VARIANTS[variant]["patch"]
    if patch is not None:
        patch(docs)
    biome_count = add_biomes(docs)
    apply_identity(docs, assets, variant)
    check_lighting_schema(docs)
    check_invariants(docs)

    out_dir = DIST / f"kage_shadows_{variant}"
    if out_dir.exists():
        shutil.rmtree(out_dir)

    files: dict[str, bytes] = {
        name: (json.dumps(doc, indent=2, ensure_ascii=False) + "\n").encode("utf-8")
        for name, doc in docs.items()
    }
    files.update(assets)

    for rel, data in files.items():
        target = out_dir / rel
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_bytes(data)

    mcpack = DIST / f"kage_shadows_{variant}.mcpack"
    with zipfile.ZipFile(mcpack, "w", zipfile.ZIP_DEFLATED) as zf:
        for rel in sorted(files):
            zf.writestr(rel, files[rel])

    size_kb = mcpack.stat().st_size / 1024
    print(
        f"{variant:<10} {len(files):>3} files "
        f"({biome_count} client biomes)  ->  {mcpack.relative_to(ROOT)} ({size_kb:.1f} KB)"
    )
    return mcpack


def main(argv: list[str]) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "variants",
        nargs="*",
        default=[],
        metavar="VARIANT",
        help=f"variants to build, any of {', '.join(VARIANTS)} (default: all)",
    )
    args = parser.parse_args(argv)

    unknown = [v for v in args.variants if v not in VARIANTS]
    if unknown:
        parser.error(
            f"unknown variant(s): {', '.join(unknown)} "
            f"(choose from {', '.join(VARIANTS)})"
        )

    DIST.mkdir(exist_ok=True)
    for variant in args.variants or list(VARIANTS):
        build(variant)
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
