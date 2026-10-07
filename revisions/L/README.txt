MB4 Rev L / refined ball-end cradle / 2026-10-07 / mm

ボールエンド保持部の再設計版。B10_streamlined_baseとA10_sculpted_ball_anchor。
6061-T6、各4個。B10はRev KのB09と同じ形状、版と品番を揃えて再出力。
最新版STEPと同名英文PDFを併用し、旧版のアンカー図面と混ぜない。

保持部
角丸四角形の窪みを、前に平らな保持肩、奥に大きな半円を持つカプセル座へ変更。
幅8.2、前Y6、奥Y15、前の内隅R1.1、奥R4.1（中心Y10.9）。
上面との境界は実形状のR0.6でつなぐ。底Z2、前の保持肩Y6を維持。
弦出口は幅3.4、底Z3.3、Y-2..8の前方だけ。球端の後方へ延びる不要な細溝を削除。
球端は上からY11へ入れ、前のY9へ寄せる。押さえねじで締め付ける構成ではない。
参考球端は外径6・横幅4.75の円筒、軸X、着座中心Y9/Z5。
実際の弦の球端・巻き部寸法は未確定で、互換性と実接触は実弦で確認が必要。
参考モデルの縦挿入、前への移動、保持肩による前方抜け止め、前方弦出口をCAD確認。
無張力時の球端脱落防止や完全な把持を保証するものではない。

継続仕様
ベース18x86x25、アンカー18x55x最高10.5、弦間19、全幅75。
参考弦中心8..20、オクターブ20mm(q=-15..5)、最前位置全長101mm。
高さ穴X+/-5.5/Y19・24、入口D4.2・床Z8、M4タップ深さ8。
木ねじX0/Y8・81、ピエゾX0/Y24、各弦2穴。裏窓と市販金物はRev Kと同じ。
後壁は厚6のR9アーチ、縁R1.2。3mmの曲線リブ、外R0.8、内縦根元R2。
金物M4x45全ねじ、UY6-35、M4平先、M3ボタン頭は従来の候補を継続。
CAD9条件、STEP21移動位置、ねじ肉厚、足の接地、座面・入口床の材料、再読込を確認。
実物強度/疲労・球端適合・ピエゾ性能・JLC工具アクセス/受託/価格は未確認。
加工費と工具の到達性は、STEPと対応図面で手動見積審査を依頼。

再生成
python cad/build_bridge.py
python cad/verify_travel.py
blender --background --python-exit-code 1 --python cad/render_bridge.py
blender --background --python-exit-code 1 --python cad/render_ball_cradle.py
blender --background --python-exit-code 1 --python cad/render_six_views.py
python cad/compose_six_views.py
python cad/make_documents.py
python cad/package_outputs.py
