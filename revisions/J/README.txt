MB4 Rev J / rounded exterior, 20 mm travel / 2026-10-06 / mm

Rev Iの機構と取付位置を維持し、外周と後壁・リブ・アンカーの稜線を丸めた試作改訂。
加工対象：B08_rounded_baseとA08_rounded_anchor。6061-T6、各4個。
単品STEPと同名英文PDFを併用。Rev Iの加工図とは混ぜない。

外形の変更
後壁アーチの前後縁：C0.25からR1.2。
リブ外側の斜辺：C0.25からR0.8。内側の斜辺：R0.5を追加。
自由な前板上縁：C0.25からR0.5。下面外縁R0.2と後端R0.9は維持。
アンカー上縁R0.8からR1.2、下縁R0.4からR0.6。
クラウン上縁R1.0からR1.2、根元R0.8からR0.6。
高さ2 mmのクラウン内で上縁と根元のRを重ねない組合せ。
リブの基本形は平面のまま。二次曲線の膨らみ・段差・根元下の溝は設けない。

維持する寸法
ベース18x86x25、アンカー18x55x最高10、弦間19、全幅75。
オクターブ20 mm（q=-15..5）、参考弦中心8..20（g=0..12）。
最前位置の前方張り出し15 mm、モジュール全長101 mm。
木ねじX0/Y8・81、裏面ピエゾX0/Y24、取付は各弦2穴、計8穴。
M4高さX+/-5.7/Y19・25、M3長穴X+/-6/Y41、固定パッドY36。
後壁Y70.5..76.5、幅3のリブ、壁との内角R2を維持。
球受け、保持肩、長穴、裏窓、ねじ座、接着面を機能寸法として保護。
金物はRev Iと共通：SNSS-M4X45-FT全ねじ、UY6-35、M4平先、M3ボタン頭。

組立
アンカーと後方ボルトを付ける前に前後の木ねじでベースを固定する。
球端や巻き部の実物で適合と弦中心を確認。調整時は弦とM3固定を緩める。
ピエゾはphi12以下、接着配線込み厚1.2以下、金属裏へ接着し木部と挟まない。
具体的な加工受託・価格・実機強度・疲労・ピエゾ分離度は未確認。

再生成
python cad/build_bridge.py
python cad/verify_travel.py
blender --background --python-exit-code 1 --python cad/render_bridge.py
blender --background --python-exit-code 1 --python cad/render_six_views.py
python cad/compose_six_views.py
python cad/make_documents.py
python cad/package_outputs.py
Python依存はcad/requirements.txt。生成後は同じ版のSTEP・図面・プレビューを確認。
