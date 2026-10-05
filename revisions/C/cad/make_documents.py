"""Rev C shop drawings, mm. STEP authoritative for formed outlines."""
from pathlib import Path
import csv, math, json, shutil
import ezdxf
from reportlab.pdfgen import canvas
from reportlab.lib.units import mm
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.cidfonts import UnicodeCIDFont
ROOT=Path(__file__).resolve().parent.parent
pdfmetrics.registerFont(UnicodeCIDFont('HeiseiKakuGo-W5'));FONT='HeiseiKakuGo-W5'
c=canvas.Canvas(str(ROOT/'pdf/MB4_design_and_drawings.pdf'),pagesize=(297*mm,210*mm))
c.setTitle('MB4 Rev C - low profile screw and spring prototype'); PAGE=0
def text(x,y,t,size=3.1):
 c.setFillColorRGB(.12,.17,.20);c.setFont(FONT,size);c.drawString(x,y,t)
def line(a,b,dash=False):
 c.setStrokeColorRGB(.18,.24,.28);c.setLineWidth(.22);c.setDash(1.5,1) if dash else c.setDash();c.line(*a,*b);c.setDash()
def rect(x,y,w,h,r=0):
 c.setStrokeColorRGB(.18,.24,.28);c.setLineWidth(.22);c.roundRect(x,y,w,h,r) if r else c.rect(x,y,w,h)
def circle(x,y,r): c.setStrokeColorRGB(.18,.24,.28);c.setLineWidth(.22);c.circle(x,y,r)
def dh(x1,x2,y,t):
 line((x1,y),(x2,y))
 for x in (x1,x2):line((x-1,y-1),(x+1,y+1))
 c.setFont(FONT,2.8);c.drawCentredString((x1+x2)/2,y+1.5,t)
def dv(x,y1,y2,t):
 line((x,y1),(x,y2))
 for y in (y1,y2):line((x-1,y-1),(x+1,y+1))
 c.saveState();c.translate(x-2,(y1+y2)/2);c.rotate(90);c.setFont(FONT,2.8);c.drawCentredString(0,0,t);c.restoreState()
def notes(x,y,rows,size=3.1,leading=7):
 for t in rows:text(x,y,t,size);y-=leading

def start(title,subtitle):
 global PAGE;PAGE+=1;c.saveState();c.scale(mm,mm)
 text(12,194,title,5.5);text(12,185,subtitle,3);line((12,180),(285,180))
 text(12,8,'MB4 | Rev C | 2026-10-05 | mm | CNC見積・試作用',2.6);text(260,8,f'{PAGE} / 8',2.6)
def end():c.restoreState();c.showPage()

start('MB4 / 低弦高・ネジ＋バネ仕様','4弦独立／弦間19 mm／裏面ピエゾ対応／サドルレスの試作設計')
if (ROOT/'bridge_preview.png').exists():c.drawImage(str(ROOT/'bridge_preview.png'),12,37,width=165,height=134,mask='auto')
notes(186,167,['弦中心高さ：8〜20 mm（設計値）','前後調整：12 mm、M3ねじ1回転0.5 mm','固定ベース：18 × 82 × 23、板厚3','全体幅75 mm／弦間19 mm','後壁は高さ23 mm（弦高とは別）','','1弦あたり切削部品2個','B01 ベース：A6061-T6 ×4','A02 一体アンカー：C3604 ×4','','後方M3×30全ねじ＋圧縮バネ','高さねじ4本＋固定ねじ2本／弦','外周R2〜R3、稜線R0.2','ピエゾ：各弦のベース裏面に接着'],size=3,leading=7)
notes(14,29,['Rev Bの弦中心15〜20 mmから、Rev Cは8〜20 mmへ。キャリッジとアンカーを一体化。','ボールエンド形状による実際の弦軸差・強度・音響は試作で確認。既存5穴への互換設計ではありません。'],size=3,leading=6);end()

start('B01 / 固定ベース','4個 | A6061-T6 | X=幅中心、Y=前端、Z=ボディ面 | 外周RはSTEP参照')
s=1.5;y0=32
for xc,bottom,label in [(42,False,'上面'),(111,True,'裏面（同じ座標方向）')]:
 text(xc-17,167,label);rect(xc-9*s,y0,18*s,82*s,3*s);line((xc,y0-4),(xc,y0+82*s+4),True)
 for yy in (4,78):circle(xc,y0+yy*s,1.9*s);circle(xc,y0+yy*s,3.5*s)
 for xx in (-4,4):circle(xc+xx*s,y0+46*s,1.25*s)
 if bottom:
  circle(xc,y0+20*s,6.25*s);rect(xc,y0+18.9*s,9*s,2.2*s)
 else:
  rect(xc-9*s,y0+67*s,18*s,6*s,1*s);rect(xc-4*s,y0+73*s,8*s,1*s)
 dh(xc-9*s,xc+9*s,y0-10,'18');dv(xc-9*s-8,y0,y0+82*s,'82')
notes(155,166,['取付穴：(0,4)、(0,78)、φ3.8貫通。','上面皿座：φ7、90°、深さ1.6。','固定タップ：(±4,46)、M3×0.5貫通。','下穴φ2.5。裏側のナット溝は不要。','','ピエゾ窪み：(0,20)、φ12.5、深さ1.5。','残り板厚1.5。窪みは裏面から加工。','配線溝：X=0〜9、Y=18.9〜21.1。','裏面から深さ1.2、右側面に開放。','','後壁：X=±9、Y=67〜73、Z=3〜23。','後方座金の逃げ：X=±4、Y=73〜74。','上面から深さ1、底面Z=2。','外周R3、稜線R0.2。後壁Rは次ページ。','寸法公差・表面仕上げは6ページ。'],size=3.1,leading=7);end()

start('B01 / 後壁・ネジ高さ追従','後壁とベースは一体切削。縦長穴でアンカーの昇降に追従。')
s=3;x=57;y=52
rect(x-9*s,y,18*s,23*s);line((x-9*s,y+3*s),(x+9*s,y+3*s))
rect(x-1.7*s,y+4.3*s,3.4*s,15.4*s,1.7*s)
line((x,y-4),(x,y+23*s+5),True);dh(x-9*s,x+9*s,y-10,'18');dv(x-9*s-10,y,y+23*s,'23')
dv(x+9*s+13,y+4.3*s,y+19.7*s,'長穴 全長15.4');text(18,142,'後壁正面（Y方向）',3.3)
notes(146,165,['長穴中心：(X=0、Z=12)。','長穴幅3.4、全長15.4、Y方向貫通。','中心が上下に動ける範囲：Z=6〜18。','M3ねじ軸高さ＝6＋g、g=0〜12。','','後壁の平面四隅R1、上面外周R0.8。','後壁厚さ6（Y=67〜73）。','座金φ7×内径3.2×厚さ0.5。','座金は後壁背面Y=73に当たる。','頭下位置Y=73.5、M3×30全ねじ。','','最低位置では座金下端がZ=2.5。','ベース後方の逃げ底Z=2で0.5確保。','ばね外径5、下端Z=3.5でベースと0.5離れる。'],size=3.2,leading=8)
notes(14,33,['後壁の総高さ23 mmを維持し、弦高8〜20 mmの全域で後方の調整ねじを利用。','高さを動かす際は弦を緩め、固定ねじ2本と後方ねじも緩めて座金が上下に滑れるようにする。'],size=3,leading=7);end()

start('A02 / 一体型アンカー・スライダー','4個 | C3604 | X=幅中心、Y=前端、Z=下面 | 切削部品を1個に統合')
s=2.2;xc=44;y0=53
rect(xc-9*s,y0,18*s,22*s,2*s);rect(xc-9*s,y0+20*s,18*s,22*s,2*s)
rect(xc-1.7*s,y0,3.4*s,6*s);rect(xc-4*s,y0+6*s,8*s,16*s,1.5*s)
for xx in (-6,6):
 for yy in (11,18):circle(xc+xx*s,y0+yy*s,1.25*s)
for xx in (-4,4):rect(xc+(xx-1.7)*s,y0+24.3*s,3.4*s,15.4*s,1.7*s)
line((xc,y0-3),(xc,y0+42*s+4),True);dh(xc-9*s,xc+9*s,y0-10,'18');dv(xc-9*s-8,y0,y0+42*s,'42')
text(23,163,'上面',3.2)
notes(104,167,['前ブロック：幅18、Y=0〜22、高さ10。','後尾：幅18、Y=20〜42、高さ6。前部と一体。','丸め：平面四隅R2、外周上下稜線R0.2。','','ボール保持ポケット：幅8、Y=6〜22。','上面から深さ8、底Z=2、四隅R1.5。','弦スリット：幅3.4、Y=0〜22、底Z=3.3。','長い上側2縁はR0.2。その他穴口はC0.1以下。','上面開放。φ6のボール中心はZ=5。','前肩Y=6で弦張力を受ける。','','高さタップ：(±6,11)、(±6,18)、M3×0.5貫通。','固定長穴：中心(±4,32)、幅3.4、全長15.4貫通。','後尾のタップ：X=0、Z=3、Y=42から前向き。','M3×0.5有効20、下穴φ2.5深さ22＋先端0.75。','必要工具アクセス：上面・下面・後端。'],size=3.1,leading=7)
# side profile diagram
sx=2;x0=20;z0=24
rect(x0,z0,22*sx,10*sx);rect(x0+22*sx,z0,20*sx,6*sx)
line((x0+6*sx,z0+2*sx),(x0+22*sx,z0+2*sx),True);line((x0+6*sx,z0+10*sx),(x0+22*sx,z0+10*sx),True)
line((x0+22*sx,z0+3*sx),(x0+42*sx,z0+3*sx),True)
text(112,35,'側面：ポケット底Z=2／後方タップ軸Z=3',3)
end()

start('調整・弦の装填・固定ねじの長さ','gはアンカー下面とベース上面の隙間。最低位置g=0ではアンカー下面がベースに接触。')
notes(14,167,['弦中心高さ H=3＋g＋5=8＋g mm。設計範囲g=0〜12、H=8〜20。','高さねじ：M3平先×10（g=0〜6）、M3平先×16（g>6〜12）。ねじ掛かり4 mm以上。','4本の高さねじを揃えて上げ下げする。ねじ上端は前ブロック上面以下に収める。','前後位置q=8〜20（アンカー前端Y）。保持肩Y=q＋6=14〜26。','ばね作動長＝67−(q＋42)=25−q=17〜5。M3×30の後方ねじを締めると後ろへ引く。','後方ねじを緩めるとばねが前へ押す。弦張力をばねで受ける設計ではない。','ボールは開放ポケットに入れて前方の肩まで滑らせる。φ6×厚4.75の筒状ボールを基準に確認。','ボール厚はスリット幅3.4より大きいこと。巻き部分の径・長さ・弦軸は実弦で確認する。'],leading=7.5)
text(14,99,'固定ねじ2本／弦：M3全ねじ＋座金／標準スペーサで頭下厚を合わせる',3.7)
for i,t in enumerate(['g (mm)','弦中心H','固定ねじL','座金合計t','先端Z']):text(20+49*i,86,t,3.1)
for j,g in enumerate((0,2,4,6,8,10,12)):
 L=next(v for v in (10,12,16,20,25) if v>=9+g);t=.5*math.ceil((L-9-g+.2)/.5-1e-8);tip=9+g+t-L
 for i,val in enumerate((g,8+g,L,t,tip)):text(20+49*i,77-6*j,str(val),3)
notes(14,27,['先端Z=9＋g＋t−Lを0.2〜0.7に調整（木部へ突出させない）。ベース内の掛かり2.3〜2.8。','高さ変更後に長さ・座金厚を再確認。弦を緩めて調整し、最後に固定ねじ2本を軽く締める。'],size=3,leading=6);end()

rows=[['B01','固定ベース A6061-T6',4,'18×82×23、板厚3、一体切削'],['A02','一体アンカー C3604',4,'18×42×10、後尾高さ6'],['H01','SUS M3×30 六角穴付 全ねじ',4,'後方調整用、頭φ5.5×3、六角2.5'],['H02','SUS M3用座金 φ7/3.2/t0.5',4,'後方ねじ用'],['H03','SUS圧縮ばね OD5/線径0.3/自由長20',4,'使用長5〜17、密着長3.15、定数0.1 N/mm'],['H04','SUS M3平先止めねじ×10',16,'g=0〜6、高さ用、六角1.5'],['H05','SUS M3平先止めねじ×16',16,'g>6〜12用の交換セット'],['H06','SUS M3全ねじ×10/12/16/20/25','8使用','高さに応じて5ページから選択'],['H07','SUS M3座金／標準スペーサ','8組','OD7以下、ID3.2程度、合計t0.5〜5.5'],['H08','SUS皿木ねじ3.5×20',8,'頭φ7以下、木部厚・下穴は実測'],['P01','ピエゾφ12以下＋接着・配線',4,'実装総厚1.2以下、接触センサとして接着']]
start('部品表・切削と仕上げ','ねじ類は一般的なステンレス製。ばねは作動範囲と密着長を指定して選ぶ。')
for i,t in enumerate(['ID','品名','4弦数量','仕様・選択条件']):text([14,32,159,181][i],168,t,3.2)
for j,row in enumerate(rows):
 y=157-8*j
 for x,val in zip([14,32,159,181],row):text(x,y,str(val),2.65)
notes(14,59,['ばね参考：MBA CS-0500-0200-03-S4-C。同じ外径・自由長でも作動長の異なる品は代用不可。','ばねは定ピッチの外観参考モデル。購入品の閉じ端・実寸・荷重曲線を確認して選ぶ。','一般寸法±0.10、機能穴・座標±0.05、外周小R±0.05。ねじM3×0.5-6H。','接触平面は平面度0.05、Ra3.2目安。穴口C0.1以下でバリ取り。ボール肩は削り過ぎない。','3軸加工＋反転＋後端穴加工。後端M3穴は長いため切粉排出・工具保持を加工先で確認。','塗装／表面処理は別見積。タップ・接触面をマスク。黄銅は軽い研磨、アルミは任意のアルマイト。'],size=3,leading=7);end()

start('取付テンプレート / 1:1','A4横・原寸100%で印刷。50 mm枠を実測してから使用。配置は実機測定後に決める。')
x0=78;y0=58
for x in (-28.5,-9.5,9.5,28.5):
 rect(x0+x-9,y0,18,82,3);line((x0+x,y0-12),(x0+x,y0+90),True)
 for yy in (4,78):circle(x0+x,y0+yy,1.9);line((x0+x-3,y0+yy),(x0+x+3,y0+yy));line((x0+x,y0+yy-3),(x0+x,y0+yy+3))
 circle(x0+x+7,y0+20,1.5)
for yy in (14,26):line((x0-37.5,y0+yy),(x0+37.5,y0+yy),True)
dh(x0-37.5,x0+37.5,y0-18,'全幅75');dh(x0-28.5,x0-9.5,y0+96,'19')
rect(210,36,50,50);dh(210,260,22,'チェック50 mm')
notes(152,169,['各弦中心Xに取付穴2個：Y=4、78。','φ3.8は金属の通し穴径。','木部の下穴径は材質・木ねじで選ぶ。','','側方小丸：配線落とし穴候補','各弦X＋7、Y=20、φ3参考。','ボディ内部に配線を通す位置は実測。','','ナットから前端基準までの距離：','スケール長−16 mmを初期候補とする。','各弦の補正量が肩Y=14〜26に入るよう、','弦を張った仮配置で位置を決める。','既存5穴と新規穴の距離も確認。'],size=3,leading=7)
text(14,27,'DXFは同じmm座標、輪郭は直線と円弧。取付穴を開ける前にスケールと弦間を再確認。',3);end()

start('ピエゾ・試作評価・設計の限界','加工・取付の判断に必要な項目。CAD検証と実物の評価を分けて記録する。')
notes(14,166,['ピエゾ：各弦ベース裏面の窪みに接着。φ12以下、接着・配線を含む総厚1.2以下。','窪み深さ1.5のため、木部から0.3以上離す。荷重でセラミックを挟み潰す構成にはしない。','各素子に個別の高入力インピーダンスバッファを置き、4ch出力／ミキサーへ。','共通の木部を経由する機械的クロストークは残る。個別素子だけで完全分離は保証できない。','','最初は1弦分を加工。ボールの脱落・装填・巻き部分の当たり・調整時の傾きを確認する。','3 mmベースのタップは掛かりが短い。締付力、ねじロックの必要性、耐久性を現物で評価する。','後方タップ軸の上下肉厚は薄い部分で約1.5。後壁・アンカーの張力負荷を段階的に確認する。','CADの干渉検査は強度保証ではない。張力・疲労・木部保持力の試験は未実施。','φ6ボールが底Z=2に接すると弦軸Z=5となる設計。実弦のボール／巻き形状で実際の最低高さが変わる可能性がある。','ネック角度、指板R、必要弦高、既存取付穴、ボディ端までの余白は実機で確認する。','','調整順：弦を緩める→固定ねじを緩める→弦高を合わせる→オクターブを合わせる→固定。','最低位置では下面全体が接触。高い位置では4本の高さねじが支え、固定ねじで浮きを抑える。'],size=3.1,leading=7)
notes(14,54,['参照：Deviser Ray Ross Bass Bridge (4Strings)／サドルレス構造の考え方。','https://www.deviser.co.jp/products/ray-ross-bass-bridge-4strings','ばね参考：MBA CS-0500-0200-03-S4-C 商品仕様（調査日2026-10-05）。','https://files.minibearings.au/pdf/catalogues/Springs.pdf (p.20)','寸法・型番はRFQ／features.csv／加工用STEPと合わせて確認。STEPのねじ穴はφ2.5下穴表現。'],size=2.8,leading=6);end();c.save()
with (ROOT/'BOM.csv').open('w',encoding='utf-8-sig',newline='') as f:
 w=csv.writer(f);w.writerow(['ID','品名','4弦数量','仕様']);w.writerows(rows)
features=[
 ['B01','blank','18 x 82; plate Z0..3; tower topZ23','A6061-T6; outlineR3; edgesR0.2'],
 ['B01','mount','(0,4),(0,78)','D3.8 THRU; top CSK D7 90deg depth1.6'],
 ['B01','clamp taps','(+/-4,46)','M3x0.5-6H THRU plate3; tap drillD2.5'],
 ['B01','piezo','(0,20)','bottom D12.5 depth1.5; remaining1.5'],
 ['B01','wire','X0..9 Y18.9..21.1','bottom depth1.2; side open'],
 ['B01','tower','Y67..73 Z3..23','outlineR1; topR0.8'],
 ['B01','vertical rear slot','X0 Z12','width3.4 total15.4 THRU alongY; screw axesZ6..18'],
 ['B01','rear washer clearance','X-4..4 Y73..74','top depth1; floorZ2'],
 ['A02','blank','18 x 42; front Y0..22 H10; tailY20..42 H6','C3604; one solid; outerR2; edgeR0.2'],
 ['A02','ball cradle','X+/-4 Y6..22','top pocket depth8 floorZ2; cornerR1.5; shoulderY6'],
 ['A02','string slot','X+/-1.7 Y0..22','floorZ3.3; top long lipsR0.2'],
 ['A02','height taps','(+/-6,11),(+/-6,18)','M3x0.5-6H THRU10; drillD2.5'],
 ['A02','clamp slots','(+/-4,32)','width3.4 total15.4 THRU6; slot center travelY26..38'],
 ['A02','rear intonation tap','X0 Z3 fromY42 towards-Y','M3x0.5-6H usable20 min; drillD2.5 depth22 + point0.75']]
with (ROOT/'features.csv').open('w',encoding='utf-8-sig',newline='') as f:
 w=csv.writer(f);w.writerow(['part','feature','location_mm','machining']);w.writerows(features)
# Regenerate the exact rounded mounting pattern.
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

print('8-page Rev C drawings, BOM, features and mounting DXF complete')
