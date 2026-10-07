# Rev L — ボールエンド保持部の再設計

ボールエンドの保持部を、前の平らな肩と奥の大きな半円を持つ一つのカプセル座にしました。上面との入口境界を実形状R0.6でつなぎ、球端の後方へ延びていた不要な細い溝をなくしています。

- 保持窪み：幅8.2、Y6〜15、前内隅R1.1、奥R4.1、底Z2。
- 保持肩Y6と参考弦軸Z5を維持。弦出口は幅3.4・底Z3.3の前方だけです。
- 外径6・幅4.75の参考円筒球端で、縦挿入、前の肩へ寄せる経路、前方抜け止めをCAD確認。
- 参考弦中心8〜20 mm、オクターブ20 mm、ベース86 mmと市販金物を維持。
- B10ベースはRev KのB09と同形状。保持部を変えたA10と版・品番を揃えています。

加工対象はB10_streamlined_baseとA10_sculpted_ball_anchor、6061-T6、各4個です。同名の単品STEPと英文加工図を併用します。最前位置の張り出し15 mm、モジュール全長101 mmです。

## ダウンロード

- `MB4_CNC_prototype_RevL.zip`：CAD・STEP・加工図・部品表・ガイド・Blender・STL・通常／拡大プレビューの一式。
- `MB4_JLCCNC_upload_RevL.zip`：B10/A10単品STEPと同名英文加工図、計4ファイル。
- `MB4_RevL_six_views.zip`：6面プレビューと画像生成ソース。
- `ball_cradle_empty.png`：球端保持座を空の状態で確認するCAD拡大画像。

[README](https://github.com/Bongorian/mb4-independent-bass-bridge#readme)から設計説明・組立・調達・検証・再生成手順を読めます。過去版は保存しています。

## 確認範囲

各部品の有効性とSTEP再読込、9つの位置／高さ条件、1 mm刻み21位置、4本の高さ足、ねじ周辺の材料、機能座面と入口床の縁を確認しました。球端の縦挿入11高さと着座経路11位置を参考形状で検査し、前方へ0.3 mm変位した球端が保持肩に当たることを確認しました。新旧ベースの両方向Boolean差分体積は0です。

弦張力で肩へ保持する開放構造です。締め付けねじや無張力時の上方脱落防止機構は追加していません。実物の球端・巻き部適合、接触、強度・疲労、木部保持、ピエゾ性能、JLCの加工受託・価格は未確認です。CADは試作見積資料であり、発注はしていません。

## 配布物のSHA-256

```text
0f81e32088d3af8071832b93dffd80d3daf665328a75f05430c7ffd8c2e29471  MB4_CNC_prototype_RevL.zip
52262cb1fd562b846dd3924ec171d557de436239c5b17c7e62464229f67fe6eb  MB4_JLCCNC_upload_RevL.zip
172108623f4a4e9c7c14cdda41dab48ba1f72c3cf8765c681fdd490755602e7f  MB4_RevL_six_views.zip
cac7d3ac1d2cf34d5facabf0720da819a4b5480ff3ed958083c93bca99c99a80  ball_cradle_empty.png
```
