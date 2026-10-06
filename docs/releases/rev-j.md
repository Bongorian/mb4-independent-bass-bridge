# Rev J — 外周・アーチ・リブとアンカーの丸み

Rev Iの機構を維持し、外周と後壁・リブ・アンカーの稜線を一定Rで丸めた試作版です。

- 後壁アーチ縁R1.2、リブ外側R0.8・内側R0.5、自由な前板上縁R0.5。
- アンカー上縁R1.2・下縁R0.6、クラウン上縁R1.2・根元R0.6。
- ベース長86 mm、20 mmのオクターブ調整、参考弦中心8〜20 mm、穴位置・ピエゾ位置・金物はRev Iと共通。
- リブの基本面は簡潔な平面を維持。曲線の膨らみや根元下の溝は追加していません。

加工対象はB08_rounded_baseとA08_rounded_anchor、両方6061-T6、各4個です。新しい単品STEPと同名の英文加工図を併用してください。前方限界ではアンカーが15 mm張り出し、モジュール全長101 mmです。

## ダウンロード

- `MB4_CNC_prototype_RevJ.zip`：CAD・STEP・図面・部品表・ガイド・Blender・STL・プレビューの一式。
- `MB4_JLCCNC_upload_RevJ.zip`：B08/A08の単品STEP＋同名英文PDF、計4ファイル。
- `MB4_RevJ_six_views.zip`：6面プレビューと生成ソース。
- `rev-i-to-j.png`：Rev IとJの比較画像。

[README](https://github.com/Bongorian/mb4-independent-bass-bridge#readme)に、文脈なしで読める設計説明・組立・調達・検証・再生成手順を整理しています。過去版は開発履歴として保存しています。

## 確認範囲

9つの前後位置・高さ条件、1 mm刻み21位置、M4周辺材料、高さ足の接地、STEP再読込を確認しました。丸みの曲面について元ソリッドとSTEPの両方向Boolean差分は体積0、外形座標差は1e-5 mm未満です。

一定Rの仕上げパスは増えます。JLCの加工受託・工具到達性・価格、実物の強度・疲労・球端適合・木部保持・ピエゾ性能は未確認です。Rev Iの図面とは混ぜないでください。

## SHA-256

```text
7b65bbe42676a487e3f9052490c8d40ead28eaad107a8ed2b524325313ed0627  MB4_CNC_prototype_RevJ.zip
ab7b4e9c57ca968b28b27881d6b1a4822d5bbc315503f346f7cf4f189f40c46a  MB4_JLCCNC_upload_RevJ.zip
ab24897194916a0cecbef8d11a3664640be46f4d6773b3b2e711626f29d4ee69  MB4_RevJ_six_views.zip
d7162a3460deec55edbec67f03354f49b57dc14550c576853ecbbd51c6a71e0d  rev-i-to-j.png
```
