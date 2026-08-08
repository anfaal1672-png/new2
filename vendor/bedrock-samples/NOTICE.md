# vendor/bedrock-samples

The JSON files under `biomes/` are unmodified copies of Minecraft: Bedrock Edition's
vanilla client biome definitions, taken from
[Mojang/bedrock-samples](https://github.com/Mojang/bedrock-samples)
(`resource_pack/biomes/`, `main` branch).

> (c) Mojang AB. All rights reserved.
> These files are subject to the [Minecraft End User License Agreement](https://www.minecraft.net/en-us/eula).

They are **not** covered by this repository's MIT license, which applies only to the
pack's own settings, tooling and documentation.

## Why they are here

A client biome file in a resource pack takes the place of the vanilla file with the same
name. Vanilla ships a full definition per biome - fog, water colour, ambient sounds,
biome music, grass and foliage tints - and this pack only wants to change two of those
components (`minecraft:lighting_identifier` and `minecraft:color_grading_identifier`).

`tools/build.py` therefore reads the vanilla definition, swaps in this pack's two
identifiers, and writes the result. Everything else about each biome is carried through
untouched, so applying the pack cannot silently remove a biome's fog or music.

## Refreshing them

```bash
python3 tools/fetch_vanilla_biomes.py
```

That re-downloads exactly the biomes listed in `tools/biome_map.json`. Run it after a
Minecraft update if a biome's vanilla definition changes, or when adding a biome to the
map.
