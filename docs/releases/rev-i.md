# Rev I — 20 mm調整とRev A〜Iの設計資料

各弦独立・ピエゾ対応の4弦ベース用ブリッジの試作設計です。ベース長86 mmのままオクターブ調整範囲を20 mmへ拡大したRev Iと、Rev A〜Iの保存CAD・図面・開発履歴を公開します。

[README](https://github.com/Bongorian/mb4-independent-bass-bridge#readme)から設計説明、組立・調整、加工・部品調達、検証範囲、再生成手順へ進めます。

## 添付ファイル

- `MB4_CNC_prototype_RevI.zip`：元のRev Iフルパッケージ。STEP、加工PDF、部品表、ガイド、CADソース、STL、Blenderモデル、プレビュー。元の配布ディレクトリ構成を保持しています。
- `MB4_JLCCNC_upload_RevI.zip`：B07ベースとA07アンカーの単品STEP＋英文加工図、計4ファイル。2種類を各4個で見積依頼します。
- `MB4_RevI_six_views.zip`：6面プレビューと視点情報・生成ソース。
- `revision-history.png`：Rev A〜Iの発展一覧、3600×4110 px。

GitHubのSource code ZIP/TARは整理後のリポジトリ全体で、A〜Iの保存データと新しい説明資料を含みます。元のフルパッケージとファイル配置が異なります。

## 仕様と評価段階

両切削部品はアルミ6061-T6、弦間19 mm、各弦2部品、参考弦中心8〜20 mm。前方限界ではアンカーが15 mm張り出し、モジュール全長101 mmです。後方はM4×45全ねじとUY6-35ばねを使用します。

CADの干渉確認・STEP再読込を実施しています。荷重・疲労・実弦適合・木部保持・ピエゾの感度と分離度は未評価です。JLCの見積・加工受託・発注は未実施です。旧版の部品や図面と混ぜないでください。

## 添付ファイルのSHA-256

```text
319a7b376d95de474a8513af2a0e5a0c840293bac8c61157ca2935c93aa96914  MB4_CNC_prototype_RevI.zip
324d667b94bea5a883e1dbc90f82b83b5c560085ba9352a642665661eed917d0  MB4_JLCCNC_upload_RevI.zip
baa7da487169ea34584f2419ecf6429733881d2921c9ffcfaab547fe5ae87ecc  MB4_RevI_six_views.zip
ae5dc7ef1dc507fb8415ac4d3a79e0a0bd267b09a514d441e56a566cd063f4fe  revision-history.png
```
