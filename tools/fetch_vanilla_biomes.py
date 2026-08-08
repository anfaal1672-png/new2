#!/usr/bin/env python3
"""Refresh vendor/bedrock-samples/biomes from Mojang's published vanilla pack.

Only the biomes listed in tools/biome_map.json are fetched. See
vendor/bedrock-samples/NOTICE.md for why the files are vendored and under what
terms they are distributed.
"""

from __future__ import annotations

import json
import sys
import urllib.error
import urllib.request
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
VENDOR = ROOT / "vendor" / "bedrock-samples" / "biomes"
BASE = "https://raw.githubusercontent.com/Mojang/bedrock-samples/main/resource_pack/biomes"


def biome_names() -> list[str]:
    with (ROOT / "tools" / "biome_map.json").open(encoding="utf-8") as fh:
        profiles = json.load(fh)["profiles"]
    return [biome for profile in profiles.values() for biome in profile["biomes"]]


def main() -> int:
    VENDOR.mkdir(parents=True, exist_ok=True)
    missing: list[str] = []

    for biome in biome_names():
        name = f"{biome}.client_biome.json"
        try:
            with urllib.request.urlopen(f"{BASE}/{name}", timeout=30) as resp:
                body = resp.read()
        except urllib.error.HTTPError as exc:
            if exc.code == 404:
                missing.append(biome)
                continue
            raise
        json.loads(body)  # reject anything that is not valid JSON
        (VENDOR / name).write_bytes(body)

    print(f"{len(biome_names()) - len(missing)} vanilla client biomes vendored")
    if missing:
        print(
            "not found upstream (remove them from tools/biome_map.json): "
            + ", ".join(missing),
            file=sys.stderr,
        )
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
