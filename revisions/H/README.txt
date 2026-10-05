MB4 Rev H / compact base and simple planar webs / 2026-10-05 / mm

CNC parts for4 strings:
B06_compact_base, Aluminum6061-T6, quantity4, 18x86x25.
A06_smooth_anchor, Aluminum6061-T6, quantity4, unchanged local geometry from RevG.
Use the separate single-part STEP and matching PDF files for quotation.
The A06 component drawing is reused unchanged and is labelled RevG; this is intentional.
Do not use B05 or the RevG mounting template for the new base.

今回の変更：
ベースの前端を12 mm詰め、長さ98→86。
後壁を基準にした移動量：前木ねじ15 mm、ピエゾ16 mmをエンド側へ移動。
旧版座標では前木ねじY5→20、ピエゾY20→36、新しいベース前端は旧Y12。
新座標：前木ねじX0/Y8、後木ねじX0/Y81、ピエゾX0/Y24、固定パッドX±6/Y42。
前後木ねじ間73、木部への固定穴は引き続き2個/弦、4弦で計8個。
リブは幅3、上端Z16を維持。上辺を直線、側面を平面へ変更。
複雑な曲面Rの重なりと、リブ根元に入り込んでいたベース上縁のRを除去。
壁とリブの内角R2は工具のために保持。露出斜辺・アーチ稜線・前板上縁はC0.25。
リブとベースの外側面は一枚の平面としてつながる。斜視図では隠れ線を省略。
アンカーのクラウン、丸み、4本の高さねじ、長穴、裏面開放窓は変更なし。
ステンレスねじ、M4×30後方ネジ、ばね、座金もRevGと同じ。

組立：
前木ねじがアンカーの下に入るので、ベースをボディに固定してからアンカーを組む。
前取付穴はアンカーを装着したまま締める用途ではない。取り外す際は先にアンカーを外す。
前の木ねじの頭を皿座へ収め、金属上面から突出しないようにする。
ピエゾを金属裏面の窪みへ接着。φ12以下、接着・配線を含む厚さ1.2以下。
木部まで公称0.3以上離す。ピエゾを木部と金属で挟み込まない。
各弦を個別の高インピーダンス入力で読む。木部を通る弦間の振動は残る。

可動域：
新座標のアンカー前端q=-4..8。通常q=-4..6、10 mm。公称最大12 mmはばね実測条件付き。
ばねの作動長13-q。実測自由長からのたわみ15以下、密着させない。
最も前に出したq=-4では、アンカーの先端がベースより4 mm前へ出る。
このため、最前位置のモジュールの全長は90 mm。ベース板そのものは86 mm。
最低弦中心参考8、最高20。球端や巻き部の実物形状で弦軸の高さは変わり得る。
高さM4平先8/12/16、固定M3長12/16/20/25と座金厚はガイド表から選択。
M4後方の軸Z7..19、頭座Y69.5、先端Y39.5、非ねじ先端Y59.5。
A06の後方タップはY50より、裏面開放窓につながる短い貫通加工。全周ねじ8以上。

CAD確認：
各STEPの再読込有効、64ソリッドの参考組立有効。
9組の高さ/前後位置でCNC部品、金物、ばねOD6包絡を確認。指定タップ主径だけを嵌合域として除外。
高さ・固定ねじの長さと先端をg0..12の1201点で確認。
後木ねじのD6工具域、アンカー取り外し状態での前木ねじのD6工具域を確認。
前木ねじのD7/90皿頭包絡とアンカーに干渉なし。
リブ根元X±8.85/Y59..75.5/Z2.75..2.9の材料帯が切れずにつながることをSTEP上で確認。
M4タップ周囲の0.8 mm材料ガードはRevGの修正を維持。
固定M3の実際の下穴がX±6/Y42でボスを貫通し、その周囲に0.8 mm以上の材料が残ることを確認。
これは形状と干渉の確認であり、荷重下の強度・疲労を保証するものではありません。

JLCへ：
jlc_uploadの部品別ZIPを2種類、各4個で見積。Threads=YES、6061-T6、As-machined。
同名STEP/PDFを添付。組立STEP/STL/画像/ガイドは加工対象としてアップロードしない。
MB4_JLCCNC_upload_RevH.zipは2組のSTEP/PDFだけ。
受託可否、工具到達性、加工費と納期はJLCの手動審査で確定。こちらから送信・発注は未実施。
穴位置の変更に合わせた専用1:1 DXFを同梱。既存Jazz/P Bassの取付穴には非互換。
実弦、ボディ高さ/穴/空洞/厚さ、ねじ・木部保持、疲労、ピエゾ分離度はまず1弦で検証。

再生成：
Python依存はcad/requirements.txt。
python cad/build_bridge.py
blender --background --python-exit-code 1 --python cad/render_bridge.py
blender --background --python-exit-code 1 --python cad/render_six_views.py
python cad/compose_six_views.py
python cad/make_documents.py
python cad/package_outputs.py
PDF作成では利用するPDFスキルのマーカー手順を先に実施。A06のPDFは変更せず流用する。
