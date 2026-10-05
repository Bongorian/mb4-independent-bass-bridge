from pathlib import Path
import csv, json, math
import ezdxf
from reportlab.pdfgen import canvas
from reportlab.lib.units import mm
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.cidfonts import UnicodeCIDFont

ROOT=Path(__file__).resolve().parent.parent
pdfmetrics.registerFont(UnicodeCIDFont('HeiseiKakuGo-W5'))
FONT='HeiseiKakuGo-W5'
W,H=297,210
c=canvas.Canvas(str(ROOT/'pdf/MB4_design_and_drawings.pdf'),pagesize=(W*mm,H*mm))
c.setTitle('MB4 4-string modular saddleless bass bridge - Rev B rounded prototype')
PAGE=0
def text(x,y,t,size=3.1,color=(.12,.17,.20)):
    c.setFillColorRGB(*color); c.setFont(FONT,size); c.drawString(x,y,t)
def line(x1,y1,x2,y2,dash=False):
    c.setStrokeColorRGB(.18,.24,.28); c.setLineWidth(.22); c.setDash(1.6,1.1) if dash else c.setDash()
    c.line(x1,y1,x2,y2); c.setDash()
def rect(x,y,w,h,dash=False):
    c.setStrokeColorRGB(.18,.24,.28); c.setLineWidth(.22); c.setDash(1.6,1.1) if dash else c.setDash(); c.rect(x,y,w,h); c.setDash()
def roundrect(x,y,w,h,r):
    c.setStrokeColorRGB(.18,.24,.28); c.setLineWidth(.22); c.setDash(); c.roundRect(x,y,w,h,r)
def circle(x,y,r,dash=False):
    c.setStrokeColorRGB(.18,.24,.28); c.setDash(1,1) if dash else c.setDash(); c.circle(x,y,r); c.setDash()
def slot(x,y,w,l,s):
    c.setStrokeColorRGB(.18,.24,.28); c.setLineWidth(.22); c.roundRect(x-w*s/2,y-l*s/2,w*s,l*s,w*s/2)
def dh(x1,x2,y,caption):
    line(x1,y,x2,y)
    for x in (x1,x2): line(x-1,y-1,x+1,y+1)
    c.setFont(FONT,2.9); c.setFillColorRGB(.12,.17,.20); c.drawCentredString((x1+x2)/2,y+1.7,caption)
def dv(x,y1,y2,caption):
    line(x,y1,x,y2)
    for y in (y1,y2): line(x-1,y-1,x+1,y+1)
    c.saveState(); c.translate(x-2,(y1+y2)/2); c.rotate(90); c.setFont(FONT,2.9); c.drawCentredString(0,0,caption); c.restoreState()
def start(title,subtitle):
    global PAGE; PAGE+=1; c.saveState(); c.scale(mm,mm)
    text(12,194,title,5.8); text(12,185,subtitle,3)
    line(12,180,285,180)
    text(12,8,'MB4 | Rev B | 2026-10-05 | 単位 mm | 試作・見積用',2.6)
    text(252,8,f'{PAGE} / 9',2.6)
def end(): c.restoreState(); c.showPage()
def notes(x,y,rows,size=3.1,leading=6):
    for t in rows: text(x,y,t,size); y-=leading
def datum(x,y):
    line(x-3,y,x+3,y); line(x,y-3,x,y+3); text(x+2,y-5,'原点 (0,0)',2.6)

start('MB4 — 4弦独立サドルレス・ブリッジ','ジャズベ／プレベ想定。汎用M3ステンレス金物と、3種類の切削部品で構成。')
preview=ROOT/'bridge_preview.png'
if preview.exists(): c.drawImage(str(preview),12,37,width=165,height=134,mask='auto')
notes(186,169,[
'4個のモジュールを19 mmピッチで配置',
'ベース幅18 mm／全体幅75 mm',
'ベース奥行82 mm（ねじ棒は最大Y=90）',
'弦軸の参考高さ15〜20 mm',
'キャリッジ移動12 mm／各弦独立',
'裏面：φ12.5 × 深さ1.5のピエゾ用窪み',
'',
'B01 固定ベース：A6061-T6 ×4',
'C01 キャリッジ：A6061-T6 ×4',
'A01 アンカー：C3604黄銅 ×4',
'',
'外周R2〜R3／後壁上面R1。',
'3軸切削＋反転＋側面の穴加工。',
'M3ねじ穴はSTEPでは下穴径を表現。',
'図面のねじ指示を加工時に適用。'],size=3,leading=7)
notes(14,29,['既存5穴には非互換。弦間・弦高・ボディ端までの余白を実機で確認して新規取付。',
'球状／筒状ボールの形・巻き方に応じて実弦で支点を確認。音質・分離度は未検証。'],size=3,leading=6)
end()

start('B01 / 固定ベース','数量4 | A6061-T6 | 18 × 82 × 12、板厚5 | 外周R3、外周稜線R0.2、後壁は9ページ参照')
s=1.55; y0=34
for x0,label,bottom in [(42,'上面',False),(111,'裏面（上面と同じ座標方向）',True)]:
    text(x0-18,169,label,3.2); roundrect(x0-9*s,y0,18*s,82*s,3*s); datum(x0,y0)
    line(x0,y0-4,x0,y0+82*s+3,True)
    for yy in (4,78): circle(x0,y0+yy*s,1.9*s); circle(x0,y0+yy*s,3.5*s, bottom)
    for xx in (-4,4):
        slot(x0+xx*s,y0+48*s,3.4,15.4,s)
        if bottom: c.roundRect(x0+(xx-2.9)*s,y0+37*s,5.8*s,22*s,1.5*s)
    if bottom:
        circle(x0,y0+20*s,6.25*s); rect(x0,y0+18.9*s,9*s,2.2*s)
    else:
        roundrect(x0-9*s,y0+62*s,18*s,6*s,1.5*s)
        roundrect(x0-8*s,y0+63*s,16*s,4*s,.5*s)
        rect(x0-4*s,y0+68*s,8*s,6*s)
    dh(x0-9*s,x0+9*s,y0-10,'18'); dv(x0-9*s-9,y0,y0+82*s,'82')
notes(157,166,[
'基準：X=幅中心、Y=前端、Z=ボディ面。',
'取付穴：(0,4)、(0,78)／φ3.8貫通。',
'皿座：上面φ7、90°、深さ1.6。',
'長穴中心：X=±4、Y=48。',
'長穴：幅3.4、全長15.4、貫通。',
'裏側ナット溝：5.8 × 22 × 深さ2.2。',
'同中心、四隅R1.5。裏面から切削。',
'ピエゾ窪み：(0,20)、φ12.5、深さ1.5。',
'配線溝：X=0〜9、Y=18.9〜21.1。',
'裏面から深さ1.2、右側面に開放。',
'後壁：Y=62〜68、Z=5〜12、幅18。',
'後壁穴：X=0、Z=7.5、φ3.4 Y方向貫通。',
'金物逃げ：X=±4、Y=68〜74。',
'上面から深さ1.5（底Z=3.5）。'],size=2.85,leading=6.7)
text(157,63,'側面（Y-Z）',3.1)
x=157; z=36
rect(x,z,82*s,5*s); rect(x+62*s,z+5*s,6*s,7*s)
line(x+68*s,z+3.5*s,x+74*s,z+3.5*s); line(x+68*s,z+3.5*s,x+68*s,z+5*s); line(x+74*s,z+3.5*s,x+74*s,z+5*s)
line(x+62*s,z+7.5*s,x+68*s,z+7.5*s,True)
dh(x,x+82*s,25,'82'); dv(289,z,z+12*s,'12')
end()

start('C01 / キャリッジ','数量4 | A6061-T6 | 18 × 40 × 5 | 外周R2、外周の上下稜線R0.2 | 穴位置・支持面高さは維持')
s=2.3; x=45; y=69
text(25,168,'上面',3.2); roundrect(x-9*s,y,18*s,40*s,2*s); datum(x,y)
for xx in (-6,6): circle(x+xx*s,y+3*s,1.25*s)
for xx in (-4,4): circle(x+xx*s,y+34*s,1.7*s)
line(x,y+27.25*s,x,y+40*s,True)
dh(x-9*s,x+9*s,y-9,'18'); dv(x-9*s-10,y,y+40*s,'40')
text(105,160,'側面（Y-Z）',3.2); rect(105,134,40*s,5*s)
line(105+28*s,134+2.5*s,105+40*s,134+2.5*s,True)
dh(105,105+40*s,124,'40'); dv(202,134,134+5*s,'5')
text(226,160,'後面（X-Z）',3.2); rect(232-9*s,134,18*s,5*s); circle(232,134+2.5*s,1.25*s)
notes(105,111,[
'基準：X=幅中心、Y=キャリッジ前端、Z=下面。',
'アンカー固定用：(±6,3)、M3 × 0.5 貫通、2箇所。',
'移動固定用：(±4,34)、φ3.4 貫通、2箇所。',
'後面ねじ：X=0、Z=2.5、Y方向 M3 × 0.5。',
'有効ねじ深さ10以上。φ2.5の円筒下穴深さ12＋ドリル先端0.75。',
'CADの後面穴は下穴形状。止めねじではなく張力受けのねじ棒を固定。',
'後面穴軸から上下面まで2.5。タップ後の残り肉は約1 mm。'],size=3.05,leading=8)
notes(14,31,['ベース上の固定ねじ：M3 × 10 + 厚さ0.5ワッシャ + DIN562薄形四角ナット。',
'ナット5.5角 × 厚さ1.8。穴軸はベースのY=42〜54を移動。裏側溝に先にナットを入れる。'],size=3.05,leading=7)
end()

start('A01 / ボールエンド・アンカー','数量4 | C3604快削黄銅 | 18 × 26 × 10 | 外周R2、外周上下稜線R0.2、スリット上縁R0.2')
s=3; x=43; y=85
text(20,168,'上面',3.2); roundrect(x-9*s,y,18*s,26*s,2*s); datum(x,y)
rect(x-1.7*s,y,3.4*s,26*s)
line(x-4*s,y+6*s,x-4*s,y+26*s,True); line(x+4*s,y+6*s,x+4*s,y+26*s,True)
line(x-4*s,y+6*s,x-1.7*s,y+6*s,True); line(x+1.7*s,y+6*s,x+4*s,y+6*s,True)
for xx in (-6,6):
    for yy in (11,22): circle(x+xx*s,y+yy*s,1.25*s)
    circle(x+xx*s,y+3*s,1.7*s)
dh(x-9*s,x+9*s,y-8,'18'); dv(x-9*s-8,y,y+26*s,'26')
text(112,168,'側面（Y-Z）',3.2); rect(112,125,26*s,10*s)
for zz in (1,9): line(112+6*s,125+zz*s,112+26*s,125+zz*s,True)
line(112,125+5*s,112+26*s,125+5*s,True)
dh(112,112+6*s,114,'座面まで6'); dh(112+6*s,112+26*s,105,'穴深さ20')
text(220,168,'後面（X-Z）',3.2); rect(240-9*s,125,18*s,10*s); circle(240,125+5*s,4*s)
# Draw the union of the bore and open slot, without fictitious internal edges.
meet=5+math.sqrt(4**2-1.7**2)
c.setFillColorRGB(1,1,1); c.rect(240-1.7*s,125+meet*s,3.4*s,(10-meet)*s+.6,stroke=0,fill=1)
for xx in (-1.7,1.7): line(240+xx*s,125+meet*s,240+xx*s,125+10*s)
notes(14,62,[
'基準：X=幅中心、Y=前端、Z=下面。後面穴：X=0、Z=5、φ8、Y=26から深さ20。',
'開放スリット：幅3.4、全長26、底Z=3.3。上面から深さ6.7（R1.7端の工具逃げは部品外）。',
'高さ調整： (±6,11)、(±6,22)、4 × M3 × 0.5 貫通。保持ねじ：(±6,3)、2 × φ3.4 貫通。',
'ボールは後方から挿入し、Y=6の穴底肩で保持。弦は前方に水平に出す。後方穴は塞がない。',
'参考ボール外径6、厚さ4.75を仮定。最小厚さ3.8以上が条件。実弦で抜け・噛み込みを確認。',
'弦と巻き部分がスリット底・側壁に触れる場合はサドルレス条件が成立しない。最初の1個で検証。'],size=3.05,leading=7)
end()

start('組立断面・調整','弦高はネック／ボディの現物寸法と照合。弦を緩めて調整し、固定ねじは最後に締める。')
x0=20; y0=112; s=2.1; q=14; g=2
text(20,170,'中央模式図（Y-Z）：表示状態 q=14、g=2、参考弦軸H=17',3.2)
rect(x0,y0,82*s,5*s); rect(x0+62*s,y0+5*s,6*s,7*s)
rect(x0+q*s,y0+5*s,40*s,5*s); rect(x0+q*s,y0+(10+g)*s,26*s,10*s)
rect(x0+(q+6)*s,y0+(11+g)*s,20*s,8*s)
line(x0+q*s,y0+(13.3+g)*s,x0+(q+6)*s,y0+(13.3+g)*s)
line(x0-8,y0+(15+g)*s,x0+(q+8)*s,y0+(15+g)*s)
line(x0+(q+30)*s,y0+7.5*s,x0+(q+70)*s,y0+7.5*s)
line(x0+(q+30)*s,y0+6.0*s,x0+(q+70)*s,y0+6.0*s)
text(20,153,'← ナット側（前）',3); text(161,153,'後 →',3)
text(30,100,'ボディ面 Z=0',3); dh(x0,x0+(q+6)*s,91,'参考支点Y=q+6'); dv(202,y0,y0+17*s,'H=15+g')
text(218,167,'裏面ピエゾの参考外形',3.0)
circle(246,143,18.75); circle(246,143,18,True); rect(246,139.7,27,6.6)
notes(216,115,['窪みφ12.5 × 深さ1.5', '参考素子φ12 × 厚さ0.7', '接着・配線込みで1.2以下', '金属面への短絡を防ぐ', 'ボディで素子を圧迫しない'],size=2.8,leading=6)
notes(14,75,[
'前後調整：キャリッジ前端 q=8〜20。支点目安Y=14〜26。後ろのM3ナットで位置を合わせ、',
'四角ナットを使う上側2本のM3 × 10でキャリッジを固定。後ろの2個のナットをジャムロック。',
'高さ調整：4本のM3 × 10平先止めねじで隙間 g=0〜5。前後左右をそろえて、傾斜を抑える。',
'アンカー保持：2本のM3ボルトを下のキャリッジへ固定。底突きさせないため、次の金物を選ぶ。',
'g=0〜1未満：M3 × 16 + 厚さ1.0ワッシャ（0.5を2枚）。ねじ込み4〜5。',
'g=1〜3：M3 × 16、ワッシャなし。ねじ込み3〜5。',
'g=3超〜5：M3 × 20 + 厚さ2.0ワッシャ（0.5を4枚）。ねじ込み3〜5。',
'キャリッジの厚さは5。ボルト先端が下面を越えないことを組立時に確認。寸法公差分の余裕を取る。'],size=3.05,leading=7)
end()

start('部品表・加工指示','発注はB01／C01／A01の個別STEPとこのPDFをセットで。試作1弦分→実弦確認→4弦分が推奨。')
rows=[
('B01','固定ベース A6061-T6','4','18×82×12'),('C01','キャリッジ A6061-T6','4','18×40×5'),('A01','アンカー C3604','4','18×26×10'),
('H01','M3×10 平先 六角穴付き止めねじ SUS','16','高さ調整'),('H02','M3×16 六角穴付きボルト SUS','8','アンカー保持 g<=3'),('H03','M3×20 六角穴付きボルト SUS','8予備','アンカー保持 g>3'),
('H04','M3×10 六角穴付きボルト SUS','8','キャリッジ固定'),('H05','M3 DIN562 薄形四角ナット SUS','8','5.5角×厚さ1.8'),('H06','M3全ねじ棒 SUS、長さ40','4','キャリッジへ10ねじ込む'),
('H07','M3六角ナット SUS','8','後面調整＋ジャムロック'),('H08','M3平座金 φ7×厚さ0.5 SUS','12','固定用8、後面用4'),('H09','M3小形平座金 φ6×厚さ0.5 SUS','32予備','アンカー保持用の長さ合わせ'),
('H10','3.5×20 皿木ねじ SUS','8','頭φ7以下／下穴は木部に合わせる'),('P01','φ12以下・接着型ピエゾ接触センサ','4別途','参考外形、品番未確定')]
yy=167
for label,desc,qty,remark in rows:
    text(14,yy,label,3); text(31,yy,desc,3); text(173,yy,qty,3); text(205,yy,remark,2.85); line(14,yy-2,282,yy-2); yy-=7.7
notes(14,49,[
'一般公差：指定なし±0.10。ねじ位置・ボール穴・弦スリット・ナット溝は±0.05。',
'キャリッジ下面、ベース上面、アンカー下面は平面度0.05、Ra3.2以下を目標。',
'指定RはSTEPソリッドに実形状を反映。残る加工縁はC0.1以下でバリ取り、座面を損なわない。',
'ねじ山はSTEPで省略。ボール座肩は維持しバリのみ除去。初回は表面処理なし。R一覧は9ページ。',
'参考張力は1弦250 N、4弦1000 N。構造の設計目安で、強度試験・疲労試験を実施した値ではない。'],size=3.05,leading=7)
end()

start('取付テンプレート / 原寸 1:1','印刷は「実際のサイズ／100%」。50 mmチェック枠を定規で確認。既存穴との重なりも必ず確認。')
cx=99; yy=56
for xx in (-28.5,-9.5,9.5,28.5):
    roundrect(cx+xx-9,yy,18,82,3)
    for sy in (4,78):
        circle(cx+xx,yy+sy,1.9); line(cx+xx-3,yy+sy,cx+xx+3,yy+sy); line(cx+xx,yy+sy-3,cx+xx,yy+sy+3)
    line(cx+xx,yy-7,cx+xx,yy+84,True)
    circle(cx+xx+7,yy+20,1.5,True)
line(cx-37.5,yy+14,cx+37.5,yy+14,True); line(cx-37.5,yy+26,cx+37.5,yy+26,True)
dh(cx-28.5,cx-9.5,yy-12,'19'); dh(cx-9.5,cx+9.5,yy-12,'19'); dh(cx+9.5,cx+28.5,yy-12,'19')
dh(cx-37.5,cx+37.5,yy+91,'75'); dv(cx-49,yy,yy+82,'82')
text(62,154,'E                 A                 D                 G',3)
text(61,32,'前端基準 Y=0：ナットから S−16 の位置を初期目安とする。',3)
text(61,25,'34インチ（S=863.6）なら 847.6 mm。実弦で補正位置を確認。',3)
rect(198,52,50,50); dh(198,248,44,'50 mm チェック枠')
notes(180,162,['取付穴：各弦中心Xに2個', '前側Y=4、後側Y=78', 'φ3.8は金属の通し穴径。', '木部の下穴径は別途選ぶ。', '', '破線丸：配線落とし穴の候補', '各弦X+7、Y=20、φ3参考', '配線溝下でボディ内へ引く。', '位置・経路は内部配線を確認。'],size=3,leading=7)
end()

start('試作確認・ピエゾ配線・参照','これはCNC見積・試作を具体化する設計。特定のジャズベ／プレベへの取付保証は実測後に判断。')
notes(14,167,[
'1. まず1弦分（B01/C01/A01各1個）を加工。ボールエンドの最大外形、抜け止め、巻き部分の',
'   クリアランスを確認する。強い折れや弦の擦れ、隣の金物との干渉があれば設計寸法を修正する。',
'2. ボディ表面からの必要弦高を実測。15 mm未満が必要なら高さ寸法を再設計する。',
'   既存ブリッジ穴と新規穴の距離・木部の厚さ・ボディ端までの余白を確認。下穴は木材に合わせる。',
'3. 木部への固定後、張力を徐々に上げる。キャリッジ、ボール、ねじの移動や緩みを確認する。',
'   M3や黄銅タップは過大に締めない。必要締付力は現物と金物強度に基づいて決める。',
'4. オクターブは開放／12フレットで合わせる。巻き部分が振動する設計なので、弦銘柄と交換後に',
'   音程・余韻を再確認する。メーカーが示す音質改善を本設計の保証として扱わない。',
'5. ピエゾは荷重を直接受けるサンドイッチ構造ではなく、裏面に接着する接触センサ。',
'   φ12以下、配線・接着層を含む実装厚1.2以下を目安に、絶縁と0.3以上の木部クリアランスを確保。',
'   セラミックの点荷重を避ける。振動伝達、接着位置、低域感度は実験で選ぶ。',
'6. E/A/D/G各ピエゾ → 各高入力インピーダンスのバッファ → 個別出力／ミキサー。',
'   初期検討は入力1〜10 MΩ程度。低域の必要帯域と素子容量から決める。抵抗だけの直接並列接続は',
'   各弦を独立に読み出せない。シールド・ストレインリリーフ・ブリッジアースも設ける。',
'7. 1本ずつ弾いた時の全4chを録音し、隣弦への混入を測る。固定ベース＋共通木部経由の機械的',
'   クロストークは残る。MIDI等で強い分離が必要なら荷重経路に専用センサを置く設計へ変更する。'],size=3.03,leading=7)
notes(14,48,[
'参照：Deviser “Ray Ross Bass Bridge (4Strings)” ／ サドルレス構造・調整の考え方。',
'https://www.deviser.co.jp/products/ray-ross-bass-bridge-4strings',
'PLOS ONE 2023, The acoustical behavior of a bass guitar bridge with no saddles, doi:10.1371/journal.pone.0292515',
'Accu HFSN-M3-A2（DIN562寸法）／ NBK 六角穴付き止めねじ寸法表（M3ピッチ0.5）。'],size=2.65,leading=6)
end()

start('Rev B / R寸法と外観仕上げ','Rは表示用の平滑化ではなく、加工用STEPのソリッド形状に反映。外形の最大寸法と主要穴座標は維持。')
notes(14,168,[
'B01 固定ベース：平面外形の四隅R3。板部分の外周上下稜線R0.2。',
'B01 後壁：平面外形の四隅R1.5、上面外周稜線R1。根元はベースと一体。',
'C01 キャリッジ：平面外形の四隅R2。外周の上下稜線R0.2。',
'A01 アンカー：平面外形の四隅R2。外周の上下稜線R0.2。',
'A01 開放スリット：長手方向の上側2本の縁にR0.2。最小幅3.4と底Z=3.3は維持。',
'',
'ねじ頭の座面付近は小Rに抑え、大きな丸みで座面を削り込まない。',
'ボール保持肩Y=6、φ8穴、ねじ穴・長穴・ナット溝・ピエゾ窪みはRev Aと同じ。',
'接触平面のZ高さは維持。外周端だけを丸める。既存の金物と調整範囲を継続して使う。'],size=3.3,leading=8)
notes(14,76,[
'加工：平面外周Rは通常の輪郭加工。稜線RはRカッター／ボールエンドミル等で仕上げる。',
'三次元の自由曲面・新しい旋盤部品は追加しない。工具経路と保持方法は加工業者が決定。',
'大Rの外形輪郭公差は±0.10、R0.2の稜線仕上げは±0.05を目安。指定Rは省略しない。',
'残る穴口・窪みの縁はC0.1以下でバリ取り。ボール保持肩と機能寸法を維持する。',
'2D図は小Rと側面Rの遷移を簡略表示。R一覧とSTEPの形状を合わせて加工する。',
'ソリッドの妥当性、STEP読戻し、9条件の部品・金物干渉、座面と機能穴の維持を確認。'],size=3.15,leading=8)
end(); c.save()

with (ROOT/'BOM.csv').open('w',encoding='utf-8-sig',newline='') as f:
    writer=csv.writer(f); writer.writerow(['ID','品名・材質','4弦分の数量','備考']); writer.writerows(rows)
features=[
['B01','blank','18 x 82 x 12; plate z0..5','','A6061-T6'],
['B01','mount','(0,4), (0,78)','D3.8 THRU; CSK D7 90deg depth1.6','2'],
['B01','slide slot','(+/-4,48)','width3.4 total length15.4 THRU','2'],
['B01','nut channel','(+/-4,48)','5.8 x 22 depth2.2 from bottom; R1.5','2'],
['B01','piezo pocket','(0,20)','D12.5 depth1.5 from bottom','1'],
['B01','wire channel','x0..9 y18.9..21.1','depth1.2 from bottom','right edge open'],
['B01','tower','y62..68 z5..12','width18','1'],
['B01','tower hole','x0 z7.5','D3.4 THRU along Y','1'],
['B01','rear clearance','x-4..4 y68..74','top pocket depth1.5; floor z3.5','1'],
['C01','blank','18 x 40 x 5','','A6061-T6'],
['C01','hold tapped holes','(+/-6,3)','M3x0.5 THRU; tap drill D2.5','2'],
['C01','clamp clearance','(+/-4,34)','D3.4 THRU','2'],
['C01','rear tap','x0 z2.5 y40 inward','M3x0.5 usable depth10; cylindrical drill12 plus point .75','1'],
['A01','blank','18 x 26 x 10','','C3604'],
['A01','ball bore','x0 z5 from rear y26','D8 depth20 along -Y; seat y6','1'],
['A01','string slot','x+/-1.7 y0..26','width3.4; bottom z3.3; depth6.7 from top','open top'],
['A01','height taps','(+/-6,11), (+/-6,22)','M3x0.5 THRU; tap drill D2.5','4'],
['A01','hold clearance','(+/-6,3)','D3.4 THRU','2']]
features.extend([
['B01','outline fillet','four vertical corners','R3 constant along plate height','Rev B'],
['B01','plate edge fillet','top/bottom outer perimeter','R0.2','functional pockets not rounded'],
['B01','tower fillet','four vertical corners / top perimeter','R1.5 / R1.0','integral tower root preserved'],
['C01','outer fillet','four vertical corners / top+bottom perimeter','R2 / R0.2','screw lands retained'],
['A01','outer fillet','four vertical corners / top+bottom perimeter','R2 / R0.2','screw lands retained'],
['A01','slot mouth fillet','two long upper edges x+/-1.7 z10','R0.2','seat / minimum slot width / floor preserved']])
with (ROOT/'features.csv').open('w',encoding='utf-8-sig',newline='') as f:
    writer=csv.writer(f); writer.writerow(['part','feature','location_mm','machining','notes']);writer.writerows(features)

d=ezdxf.new('R2010'); d.units=4; m=d.modelspace()
for layer,color in [('OUTLINE',7),('MOUNT_CENTER',1),('STRING_CENTER',3),('WIRE_OPTIONAL',5),('REFERENCE',4)]: d.layers.new(layer,dxfattribs={'color':color})
for x in (-28.5,-9.5,9.5,28.5):
    # Rounded outline as exact DXF lines/arcs; mounting centers unchanged.
    r=3; left=x-9; right=x+9
    for a,b in [((left+r,0),(right-r,0)),((right,r),(right,82-r)),((right-r,82),(left+r,82)),((left,82-r),(left,r))]:
        m.add_line(a,b,dxfattribs={'layer':'OUTLINE'})
    for center,angles in [((right-r,r),(270,360)),((right-r,82-r),(0,90)),((left+r,82-r),(90,180)),((left+r,r),(180,270))]:
        m.add_arc(center,r,*angles,dxfattribs={'layer':'OUTLINE'})
    m.add_line((x,-8),(x,90),dxfattribs={'layer':'STRING_CENTER'})
    for y in (4,78):
        m.add_circle((x,y),1.9,dxfattribs={'layer':'MOUNT_CENTER'})
        m.add_line((x-3,y),(x+3,y),dxfattribs={'layer':'MOUNT_CENTER'})
        m.add_line((x,y-3),(x,y+3),dxfattribs={'layer':'MOUNT_CENTER'})
    m.add_circle((x+7,20),1.5,dxfattribs={'layer':'WIRE_OPTIONAL'})
for y in (14,26):m.add_line((-37.5,y),(37.5,y),dxfattribs={'layer':'REFERENCE'})
m.add_lwpolyline([(50,0),(100,0),(100,50),(50,50)],close=True,dxfattribs={'layer':'REFERENCE'})
m.add_text('CHECK 50 mm; PRINT 1:1; NEW HOLES',dxfattribs={'height':2.5,'insert':(50,55),'layer':'REFERENCE'})
m.add_text('FRONT DATUM Y=0; NUT DISTANCE: SCALE - 16 mm (INITIAL)',dxfattribs={'height':2.5,'insert':(-37.5,-18),'layer':'REFERENCE'})
d.saveas(ROOT/'MB4_mount_template_1to1.dxf')
print('Created 9-page Rev B PDF, rounded DXF, BOM and feature table')
