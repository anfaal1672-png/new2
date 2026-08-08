# 影 Kage Shadows

Minecraft **統合版（Bedrock Edition）** 用の、**軽いのにビジュアルが最高**なリアルタイム影アドオンです。

- 🌞 太陽・月から落ちる**方向性のあるリアルな影**
- 🧍 **自分自身にもちゃんと影が落ちる**（三人称視点で自分の影が地面に伸びます）
- 🌅 **美しい太陽** — **四角ではなく丸い太陽**。朝夕に広がるミー散乱グレア、深い青のレイリー空、夜の月グロー
- ☁️ **美しい雲** — もこもことした自然な形の雲。**バニラと同じ被覆率(27.5%)なので雲の描画コストは据え置き**
- 🌊 **美しい水面** — 波のシミュレーション、コースティクス（水底に揺れる光の網目）、物理ベースの水色
- 🎬 シネマティックなカラーグレーディング＋トーンマッピング
- 🪶 **約60KB**。同梱テクスチャは雲の256×256が1枚だけで、あとは全部JSON設定です
- 🌍 バイオームごとに4種類のライティングプロファイル（標準／乾燥・暖色／雪・寒色／暗所）

---

## ⚠️ 最初に必ず読んでください（重要）

統合版のリアルタイム影は、**ゲーム本体の「Vibrant Visuals」レンダラーの機能**です。
このアドオンはその影・光・色を**設定するパック**であって、影の機能そのものを追加するものではありません。

つまり、次の2つが揃っていないと**見た目は一切変わりません**：

1. **Minecraft 統合版 1.21.120 以降**
2. **設定 → ビデオ → グラフィック → 「Vibrant Visuals」を ON**

Vibrant Visuals は端末によっては選択できません（対応していない古いスマホ・タブレット・ゲーム機など）。
その場合、統合版のリソースパックだけで本物の動的な影を出す方法は**存在しません**。世に出回っている
「影MOD」系パックの多くは、空や霧の色を塗り替えて影っぽく見せているだけで、自分の体が落とす影は出ません。
このパックはごまかしをせず、本物の影を出す正規の仕組みだけを使っています。

---

## 導入方法

### 1. パックを作る

配布用の `.mcpack` は `dist/` に生成されます。

```bash
python3 tools/build.py
```

```
dist/kage_shadows_default.mcpack     ← おすすめ（標準）
dist/kage_shadows_lite.mcpack        ← 軽さ最優先
dist/kage_shadows_cinematic.mcpack   ← 見た目最優先
```

（Python 3.9+ だけあれば動きます。外部ライブラリは不要です。）

### 2. インストール

| 端末 | 手順 |
| --- | --- |
| Windows / Android | `.mcpack` をタップ／ダブルクリックすると Minecraft が開いてインポートされます |
| iOS / iPadOS | ファイルアプリで `.mcpack` を長押し →「共有」→ Minecraft を選択 |
| 手動 | フォルダごと `com.mojang/resource_packs/` に置いてもOK |

### 3. 有効化

1. **設定 → ストレージ／グローバルリソース**、またはワールドの **設定 → リソースパック** で「影 Kage Shadows」を有効化
2. **設定 → ビデオ → グラフィック** を **Vibrant Visuals** に変更
3. ワールドに入る

### 4. 自分の影を見る

- **F5（PC）／視点切り替えボタン** で三人称視点にすると、自分の足元から伸びる影が見えます
- 朝方・夕方（太陽が低い時間帯）が一番影が長くドラマチックです
- 一人称視点でも、地面に落ちた自分の影・手の影は見えます

---

## 3つのバリアント

| | shadow_style | トーンマッピング | 空の間接光 | 水の波 | 向いている端末 |
| --- | --- | --- | --- | --- | --- |
| **default** | soft（やわらかい影） | generic | 標準 | あり（16オクターブ） | だいたいの端末。まずこれ |
| **lite** | blocky（ドット感のある影） | reinhard_luminance | やや明るめ | **なし** | 低スペック端末 |
| **cinematic** | soft | aces | 暗め（影が濃い） | あり（24オクターブ・深め） | PC・新しめのハイエンド端末 |

`lite` はハイライト／シャドウ別のカラーグレーディング（画面全体に対する追加のピクセル処理）を削り、
一番安いトーンマッピング曲線に切り替え、**水の波のフラクタル計算を切って**います
（水シェーダーで一番重いのが波です。コースティクスは浅瀬の見栄えに直結するので `lite` でも残しています）。
`cinematic` は逆に空からの間接光を落として影のコントラストを強め、フィルム的な ACES 曲線を使い、
波を深く・コースティクスを強くします。

---

## なぜ軽いのか

- **ブロックテクスチャを1枚も同梱していません。** 多くの「シェーダー／RTX」パックは全ブロック分の
  法線マップやMERテクスチャ（数百MB）を同梱し、VRAMとロード時間を大きく圧迫します。このパックは
  **約60KB**（うちテクスチャは雲の1枚・3KBのみ）で、バニラのテクスチャ解像度をそのまま使います
- **雲はバニラと同じ被覆率に揃えています。** 雲の描画コストは不透明テクセルの量で決まるため、
  形だけ変えて量は変えていません
- **ポイントライトを追加していません。** 松明などを点光源にすると影が増えて一気に重くなるため、
  バニラの挙動のまま（`local_lighting` は同梱していません）
- **バニラが実際に同梱しているファイル形式だけを使っています**（下記「PBRフォールバックについて」参照）

つまり追加コストは実質「Vibrant Visuals 自体の描画負荷」だけです。

---

## 中身の構成

```
pack/
├── manifest.json              "pbr" capability + min_engine_version 1.21.120
├── pack_icon.png              tools/gen_icon.py が生成
├── shadows/global.json        影のスタイル（soft / blocky）
├── lighting/
│   ├── global.json            標準プロファイル（太陽・月・環境光・空の強さ）
│   ├── warm.json              砂漠・サバンナ・メサ
│   ├── cold.json              雪原・氷・山頂
│   └── dark.json              沼・暗い森・洞窟・ディープダーク
├── color_grading/
│   ├── color_grading.json     標準（コントラスト／彩度／色温度／トーンマッピング）
│   └── warm.json / cold.json / dark.json
├── atmospherics/
│   ├── atmospherics.json      標準（太陽のグレア／空の散乱／地平線の色）
│   └── warm.json / cold.json / dark.json
├── water/water.json           波・コースティクス・水の粒子濃度（全バイオーム共通）
├── textures/environment/
│   ├── clouds.png             tools/gen_clouds.py が生成
│   ├── sun_vv.png             丸い太陽（Vibrant Visuals用）／ tools/gen_sun.py が生成
│   └── sun.png                丸い太陽（従来レンダラー用）
└── texts/                     パック名・説明（英語／日本語）

tools/
├── build.py                   バリアント適用 + バイオームファイル生成 + .mcpack 化
├── biome_map.json             バイオーム → プロファイルの対応表
├── fetch_vanilla_biomes.py    バニラのクライアントバイオーム定義を取得
├── gen_clouds.py              clouds.png の生成
├── gen_sun.py                 sun_vv.png / sun.png の生成
└── gen_icon.py                pack_icon.png の生成

vendor/bedrock-samples/        バニラのクライアントバイオーム定義（(c) Mojang AB / MIT対象外）
```

### バイオームファイルが自動生成される理由

統合版 **1.21.90** から、バニラ本体がバイオームごとに Vibrant Visuals の設定を持つようになりました。
そしてそのバニラ設定は、カスタムパックの `lighting/global.json` などの**グローバル設定より優先されます**。
つまりグローバル設定だけを置いたパックは、バニラのバイオームでは**ほぼ何も効きません**。

そこで `tools/build.py` が `tools/biome_map.json` を読み、オーバーワールドの全バイオーム分の
`biomes/<biome>.client_biome.json` を生成して、このパックのライティング／カラーグレーディング／
大気／水の4つの識別子を明示的に割り当てます（81バイオーム）。

存在しないバイオームIDを書くと、クライアントが
`Loaded client biome but no biome with that name exists` を吐きます。`tools/biome_map.json` には
製品版に実在するIDだけを載せてください。

**重要**: リソースパック内のクライアントバイオームファイルは、同名のバニラファイルを**置き換えます**。
バニラの各バイオームは霧・水の色・環境音・BGM・草／葉の色まで持っているので、
こちらのライティング指定だけを書いた短いファイルを置くと**それらが全部消えます**。
そのため `tools/build.py` は `vendor/bedrock-samples/biomes/` にあるバニラの定義を読み込み、
このパックが担当する4つのコンポーネントだけを差し替えて出力します。霧もBGMもそのまま残ります。

バニラ定義の更新は `python3 tools/fetch_vanilla_biomes.py` で取り直せます。
これらのファイルの権利は Mojang AB にあり、MITの対象外です（[NOTICE](vendor/bedrock-samples/NOTICE.md)）。

**ネザーとエンドのバイオームはあえて上書きしていません。** バニラの雰囲気をそのまま残すためです。
上書きしたい場合は `tools/biome_map.json` に `hell` / `crimson_forest` / `warped_forest` /
`soulsand_valley` / `basalt_deltas` / `the_end` を追加してください。

---

## カスタマイズガイド

いじると効果が大きい順に並べています。編集したら `python3 tools/build.py` で再ビルドしてください。

| やりたいこと | 触る場所 | 方向 |
| --- | --- | --- |
| **影をもっと濃くしたい** | `lighting/*.json` の `sky.intensity` | 下げる（0.1〜1.0）。空からの間接光が減り影が暗くなる |
| **影の中が真っ黒すぎる** | `lighting/*.json` の `ambient.illuminance` | 上げる（0.0〜5.0、実用域は0.01〜0.05） |
| **影の向きを変えたい** | `lighting/*.json` の `orbital_offset_degrees` | 太陽の軌道を傾ける。**全ファイルで同じ値**にすること。既定は バニラと同じ `0.0`（空に描かれる太陽の位置と影の向きをずらさないため） |
| **昼をもっと眩しく** | `lighting/*.json` の `sun.illuminance` のキーフレーム | `"0.0"` と `"1.0"` が正午、`"0.5"` が真夜中。**バニラと同じ 0〜100 のスケール**を使うこと（下記参照） |
| **影をドット感のあるカクカクに** | `shadows/global.json` の `shadow_style` | `"blocky_shadows"` ＋ `"texel_size": 16` |
| **画面の色味** | `color_grading/*.json` の `temperature` | 大きく＝暖色、小さく＝寒色（`color_temperature` 時） |
| **全体のコントラスト** | `color_grading/*.json` の `midtones.contrast` | 1.0が無変化 |
| **朝夕の太陽の輝きを強く** | `atmospherics/*.json` の `sun_mie_strength` | `"0.25"` と `"0.75"` が夕方・朝方のピーク。上げるほど太陽の周りが光る |
| **空をもっと青く** | `atmospherics/*.json` の `rayleigh_strength` | 上げるほど大気の散乱が強まり深い青に（バニラは正午10.0） |
| **水の色** | `water/water.json` の `particle_concentrations` | `cdom`↑で黄褐色、`chlorophyll`↑で緑、`suspended_sediment`↑で赤褐色。全部0でバニラの透明な水 |
| **波を止めたい／重い** | `water/water.json` の `waves.enabled` | `false` に。または `octaves` を下げる（1〜30、水シェーダーで一番重い部分） |
| **水底の光の網目** | `water/water.json` の `caustics.power` | 1〜6。上げるほど明るくはっきり |
| **雲の形・量** | `tools/gen_clouds.py` の `OCTAVES` / `COVERAGE` | `COVERAGE` を上げると雲が増えるが、**雲の枚数＝描画コスト**が増える |
| **太陽の大きさ・色** | `tools/gen_sun.py` の `DIAMETER` / `CORE`・`MID`・`LIMB` | `DIAMETER` は既定 0.25（バニラの見かけの大きさと同じ）。上げると太陽が大きくなる |

### ビルド時に自動チェックされること

Vibrant Visuals にはバイオーム間で**補間できないパラメータ**があり、パック内で値が食い違うと
バイオームをまたいだ瞬間に画面がガクッと変わります。`tools/build.py` は次の3つを検証し、
食い違っていればビルドを失敗させます。

- 全 `color_grading/*.json` の `tone_mapping.operator` が同一であること
- 全 `lighting/*.json` の `orbital_offset_degrees` が同一であること
- 全 `water/*.json` の `waves.enabled` と `caustics` が同一であること

さらにライティングのスキーマ整合性もチェックします。

- `directional_lights.orbital` / `flash` を使うなら `format_version` は **1.21.80 以降**であること。
  古いバージョンを宣言すると、太陽・月が「必須フィールドが無い」と報告され、色も 1.21.60 以前の
  RGBA ルールで解釈されてエラーになります
- 色は 16進文字列ではなく `[r, g, b]` の配列で書くこと（6桁hexはスキーマによって受け付けられません）
- 太陽・月の `illuminance` と `color` は**必ずキーフレーム**（`{"0.0": ..., "1.0": ...}` の形）で書くこと。
  定数を書くと `Expected keyframes.` になります

### 雲について（JSONでは設定できません）

Vibrant Visuals に雲の設定スキーマは**存在しません**。バニラのリソースパックにも雲のJSONは無く、
実体は `textures/environment/clouds.png`（256×256・アルファは0か255の二値・白）1枚だけです。
Minecraft はこのテクスチャの**不透明なテクセル1つ1つを雲のセルとして立体化する**ので、
不透明部分の割合がそのまま雲の描画コストになります。

そこで `tools/gen_clouds.py` は、ラップする（継ぎ目の出ない）フラクタルノイズで雲を作り、
**しきい値を解いてバニラと同じ被覆率 27.6% に着地させています**。形だけ自然にして、コストは据え置きです。
1テクセルだけの点や穴は、空に浮かぶゴミにしか見えないので連結成分ごと除去しています。

### 太陽について

バニラの太陽は、32×32テクスチャの**中央にある8×8の正方形**です（外周 `#FFD54A` →
中間 `#FFFFAA` → 芯 `#FFFFD9` の3段階）。`tools/gen_sun.py` はこれを**同じ見かけの大きさ・同じ配色のまま
円に描き直します**。空での太陽のサイズは変わらず、輪郭だけが丸くなります。
半径4テクセルの円はただの八角形になるので、テクスチャはバニラの4倍解像度（128×128）で出力しています。

ゲームは太陽のテクスチャを2枚使うので、両方を差し替えています。

- `sun_vv.png` … Vibrant Visuals用。アルファでマスクされるので、**周囲に光の輪は描いていません**。
  太陽の周りの輝きは `atmospherics/` のミー散乱が担当するため、テクスチャにも描くと二重になります
- `sun.png` … 従来レンダラー用。黒を透明として加算合成されるので、こちらはバニラ同様に
  柔らかい放射状のグローを描いています

**月は四角のままです。** `moon_phases.png` は8つの満ち欠けを1枚に並べたテクスチャで、
太陽とは作りが違うため今回は手を付けていません。

### 水とバイオームについて

波のオン／オフとコースティクスは、Vibrant Visuals が**バイオーム間で補間できないパラメータ**です。
そのため水の設定は `water/water.json` 1つだけを全バイオームで共有しています（ビルド時に検証されます）。

大気（`atmospherics/`）はライティングと同じ4プロファイルに割り当てています。
バニラは砂漠・沼地・メサなどにもっと細かく空を出し分けているので、その分の細かさは失われます。
バイオームごとに分けたい場合は `atmospherics/` にファイルを増やし、
`tools/biome_map.json` のプロファイルを増やしてください。

### 明るさの単位について

公式ドキュメントは「実世界のlux（正午の太陽 = 約10万lx）」と説明していますが、
**製品版のバニラのファイルは正午の太陽 = `100.0`、環境光 = `0.02` というスケールを使っています**。
ドキュメント通りの10万を入れると環境光との比が1000倍ずれ、影の中と洞窟が完全に潰れます。
このパックはバニラと同じスケール（正午 84〜108、月 0.28〜0.5、環境光 0.010〜0.022）に合わせています。

---

## PBRフォールバックについて（同梱していません）

公式ドキュメントには `pbr/global.json`（テクスチャセット未指定時の
metalness / emissive / roughness / subsurface の既定値）が載っていますが、**このパックでは同梱していません**。

理由は、製品版のバニラリソースパックにこのファイルが**一切存在しない**ためです。
バニラが同梱しているVV関連ファイルは `lighting/` だけで、`pbr/` も `shadows/` も `local_lighting/` も
ありません。つまり `pbr/global.json` は実物で答え合わせができない唯一のファイルで、実際に同梱していた版では
`[Lighting][error] missing required field` と `Expected [r, g, b, a] ...` が出ていました
（ドキュメントに載っているサンプル自体、括弧が閉じていない壊れたJSONです）。

必要なら手動で `pack/pbr/global.json` を作れば同梱されます。その際、値は**浮動小数ではなく整数**で
試してください（エラーメッセージが「0-255の範囲の値」を求めているため）。

```json
{
  "format_version": "1.21.40",
  "minecraft:pbr_fallback_settings": {
    "blocks":    { "global_metalness_emissive_roughness_subsurface": [0, 0, 235, 0] },
    "actors":    { "global_metalness_emissive_roughness_subsurface": [0, 0, 215, 20] },
    "particles": { "global_metalness_emissive_roughness_subsurface": [0, 0, 255, 0] },
    "items":     { "global_metalness_emissive_roughness_subsurface": [0, 0, 225, 0] }
  }
}
```

無くても影・ライティング・カラーグレーディングは完全に機能します。

## 既知の制限

- **Vibrant Visuals が OFF、または非対応端末では何も変わりません**（上記の注意書きを参照）
- 一人称視点で「鏡に映った自分」のような反射は出せません（統合版の画面空間反射の制限）
- ガラスなどの半透明ブロックには反射が乗りません（水は例外）
- `dappled_forest` / `sulfur_caves` など新しめ・実験的なバイオームIDも含めています。
  そのバージョンに存在しないIDは無視されます（コンテンツログに警告が出ることがあります）
- マーケットプレイスの一部のワールド／パックは独自の Vibrant Visuals 設定を持っており、
  優先順位によってはこのパックが効かないことがあります

---

## 開発

```bash
python3 tools/build.py                 # 全バリアントをビルド
python3 tools/build.py default         # 1つだけビルド
python3 tools/gen_icon.py              # アイコンを作り直す
```

`pack/` が唯一のソースです。バリアントは `tools/build.py` 内で JSON を読み込んでから
パッチを当てて作られるので、設定の実体が二重管理になることはありません。

---

## ライセンス

このパック自身の設定・ツール・ドキュメントは MIT License（[LICENSE](LICENSE)）。改変・再配布自由です。

ただし `vendor/bedrock-samples/` 以下のバニラ定義は **(c) Mojang AB / Minecraft EULA 準拠**で、
MITの対象外です（[NOTICE](vendor/bedrock-samples/NOTICE.md)）。

## 参考資料（公式ドキュメント）

- [Vibrant Visuals Resource Packs](https://learn.microsoft.com/en-us/minecraft/creator/documents/vibrantvisuals/vvresourcepacks)
- [Shadows](https://learn.microsoft.com/en-us/minecraft/creator/documents/vibrantvisuals/shadowscustomization)
- [Light Sources](https://learn.microsoft.com/en-us/minecraft/creator/documents/vibrantvisuals/lightingcustomization)
- [Color Grading and Tone Mapping](https://learn.microsoft.com/en-us/minecraft/creator/documents/vibrantvisuals/colorgradingtonemappingcustomization)
- [Biome Customization](https://learn.microsoft.com/en-us/minecraft/creator/documents/vibrantvisuals/biomecustomization)
- [Client Biomes JSON](https://learn.microsoft.com/en-us/minecraft/creator/reference/content/clientbiomesreference/examples/clientbiomesoverview)
