# 影 Kage Shadows

Minecraft **統合版（Bedrock Edition）** 用の、**軽いのにビジュアルが最高**なリアルタイム影アドオンです。

- 🌞 太陽・月から落ちる**方向性のあるリアルな影**
- 🧍 **自分自身にもちゃんと影が落ちる**（三人称視点で自分の影が地面に伸びます）
- 🎬 シネマティックなカラーグレーディング＋トーンマッピング
- 🪶 **JSONだけ・約45KB**。追加テクスチャ0枚なので端末への負担がほとんど増えません
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

| | shadow_style | トーンマッピング | 空の間接光 | 向いている端末 |
| --- | --- | --- | --- | --- |
| **default** | soft（やわらかい影） | generic | 標準 | だいたいの端末。まずこれ |
| **lite** | blocky（ドット感のある影） | reinhard_luminance | やや明るめ | 低スペック端末・ハイライト／シャドウ別のグレーディングを省略 |
| **cinematic** | soft | aces | 暗め（影が濃い） | PC・新しめのハイエンド端末 |

`lite` はハイライト／シャドウ別のカラーグレーディング（画面全体に対する追加のピクセル処理）を削り、
一番安いトーンマッピング曲線に切り替えたものです。`cinematic` は逆に空からの間接光を落として
影のコントラストを強め、フィルム的な ACES 曲線を使います。

---

## なぜ軽いのか

- **テクスチャを1枚も同梱していません。** 多くの「シェーダー／RTX」パックは全ブロック分の法線マップや
  MERテクスチャ（数百MB）を同梱し、VRAMとロード時間を大きく圧迫します。このパックは JSON 設定のみで
  **約45KB**、バニラのテクスチャ解像度をそのまま使います
- **ポイントライトを追加していません。** 松明などを点光源にすると影が増えて一気に重くなるため、
  バニラの挙動のまま（`local_lighting` は同梱していません）
- **PBRのフォールバック値**（`pbr/global.json`）で全ブロック・全モブに一括でざらついた質感を与えているので、
  テクスチャを増やさずに立体感だけが増えます

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
│   ├── warm.json / cold.json / dark.json
├── pbr/global.json            テクスチャセット未指定時のPBRフォールバック
└── texts/                     パック名・説明（英語／日本語）

tools/
├── build.py                   バリアント適用 + バイオームファイル生成 + .mcpack 化
├── biome_map.json             バイオーム → プロファイルの対応表
└── gen_icon.py                pack_icon.png の生成
```

### バイオームファイルが自動生成される理由

統合版 **1.21.90** から、バニラ本体がバイオームごとに Vibrant Visuals の設定を持つようになりました。
そしてそのバニラ設定は、カスタムパックの `lighting/global.json` などの**グローバル設定より優先されます**。
つまりグローバル設定だけを置いたパックは、バニラのバイオームでは**ほぼ何も効きません**。

そこで `tools/build.py` が `tools/biome_map.json` を読み、オーバーワールドの全バイオーム分の
`biomes/<biome>.client_biome.json` を生成して、このパックのライティング／グレーディング識別子を
明示的に割り当てます（81バイオーム）。

存在しないバイオームIDを書くと、クライアントが
`Loaded client biome but no biome with that name exists` を吐きます。`tools/biome_map.json` には
製品版に実在するIDだけを載せてください。

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
| **影の向きを変えたい** | `lighting/*.json` の `orbital_offset_degrees` | 太陽の軌道を傾ける。**全ファイルで同じ値**にすること |
| **昼をもっと眩しく** | `lighting/*.json` の `sun.illuminance` のキーフレーム | `"0.0"` と `"1.0"` が正午、`"0.5"` が真夜中 |
| **影をドット感のあるカクカクに** | `shadows/global.json` の `shadow_style` | `"blocky_shadows"` ＋ `"texel_size": 16` |
| **画面の色味** | `color_grading/*.json` の `temperature` | 大きく＝暖色、小さく＝寒色（`color_temperature` 時） |
| **全体のコントラスト** | `color_grading/*.json` の `midtones.contrast` | 1.0が無変化 |

### ビルド時に自動チェックされること

Vibrant Visuals にはバイオーム間で**補間できないパラメータ**があり、パック内で値が食い違うと
バイオームをまたいだ瞬間に画面がガクッと変わります。`tools/build.py` は次の2つを検証し、
食い違っていればビルドを失敗させます。

- 全 `color_grading/*.json` の `tone_mapping.operator` が同一であること
- 全 `lighting/*.json` の `orbital_offset_degrees` が同一であること

さらにライティングのスキーマ整合性もチェックします。

- `directional_lights.orbital` / `flash` を使うなら `format_version` は **1.21.80 以降**であること。
  古いバージョンを宣言すると、太陽・月が「必須フィールドが無い」と報告され、色も 1.21.60 以前の
  RGBA ルールで解釈されてエラーになります
- 色は 16進文字列ではなく `[r, g, b]` の配列で書くこと（6桁hexはスキーマによって受け付けられません）

---

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

MIT License（[LICENSE](LICENSE)）。改変・再配布自由です。

## 参考資料（公式ドキュメント）

- [Vibrant Visuals Resource Packs](https://learn.microsoft.com/en-us/minecraft/creator/documents/vibrantvisuals/vvresourcepacks)
- [Shadows](https://learn.microsoft.com/en-us/minecraft/creator/documents/vibrantvisuals/shadowscustomization)
- [Light Sources](https://learn.microsoft.com/en-us/minecraft/creator/documents/vibrantvisuals/lightingcustomization)
- [Color Grading and Tone Mapping](https://learn.microsoft.com/en-us/minecraft/creator/documents/vibrantvisuals/colorgradingtonemappingcustomization)
- [Biome Customization](https://learn.microsoft.com/en-us/minecraft/creator/documents/vibrantvisuals/biomecustomization)
- [Client Biomes JSON](https://learn.microsoft.com/en-us/minecraft/creator/reference/content/clientbiomesreference/examples/clientbiomesoverview)
