# Rev K — 流線的な外形と高さ穴の縁

丸い前部から低い後部へ滑らかにつながる上面と、単純なアーチ・曲線リブを持つ試作版です。アンカー中央の盛り上がった筋や、支柱の別の座ボスを設けず、穴の縁が外周や隣の加工部へ切れない形に整理しました。

- 上面は連続したBezier面、後部は一段の固定平面Z8。上限10.5 mm（切欠き後のSTEP最高値は約10.42 mm）。
- 後壁は厚さ6のR9アーチ、前後縁R1.2。一続きの3 mm曲線リブを支柱内部へ2 mm重ね、固定パッド根元も底板へつなげます。
- 高さ穴をアンカー座標X±5.5/Y19・24へ移し、入口φ4.2・床Z8に変更。床周囲0.5 mm、タップ主径周囲0.8 mmの材料をCAD確認。
- ベース86 mm、参考弦中心8〜20 mm、オクターブ20 mm、木ねじ・ピエゾ位置、市販金物候補を維持。

加工対象はB09_streamlined_baseとA09_streamlined_anchor、両方6061-T6、各4個です。最新版の単品STEPと同名英文PDFを併用してください。前方限界の張り出し15 mm、モジュール全長101 mmです。

## ダウンロード

- `MB4_CNC_prototype_RevK.zip`：CAD・STEP・図面・部品表・ガイド・Blender・STL・プレビューの一式。
- `MB4_JLCCNC_upload_RevK.zip`：B09/A09の単品STEP＋同名英文加工図、計4ファイル。
- `MB4_RevK_six_views.zip`：6面プレビューと画像生成ソース。
- `rev-j-to-k.png`：Rev JとKの同条件のCADレンダー比較。

[README](https://github.com/Bongorian/mb4-independent-bass-bridge#readme)から設計説明・組立・調達・検証・再生成手順を読めます。過去版は保存しています。

## 確認範囲

9つの位置／高さ条件、1 mm刻み21位置、入口床の縁とねじ周囲の材料、高さ足の接地、座面接触、STEP再読込を確認しました。元CADとSTEPの両方向の形状差分は0、外形座標差は1e-5 mm未満です。体積数値積分は診断値として記録します。

曲面仕上げの加工量は増えます。JLCの工具到達性・受託可否・価格、実物の強度・疲労・弦の球端適合・木部保持・ピエゾ性能は未確認です。STEP＋対応図面で手動見積審査を依頼する資料です。

## 配布物のSHA-256

```text
04e64b7c81280b9260a139cd08f7b878d53910644a1df4d1c6e72b4872af992e  MB4_CNC_prototype_RevK.zip
0aff2bb30ec78b04c7777be666f19021fa927c6372cc8626bd08be98724e24f5  MB4_JLCCNC_upload_RevK.zip
40939c0831099249c68dbce3949f1855e0372b30fb1f3a133ace95b778d89680  MB4_RevK_six_views.zip
6c2ca22163dc0604c4ab6a724325f499ec6b36fb4377719d1634a07c94e5cb18  rev-j-to-k.png
```
