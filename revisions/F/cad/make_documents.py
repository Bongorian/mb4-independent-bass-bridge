"""Rev F shop drawings, mm. STEP authoritative for formed outlines."""
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
c.setTitle('MB4 Rev F - single rear fixing, integrated crown, MISUMI hardware'); PAGE=0
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
 text(12,8,'MB4 | Rev F | 2026-10-05 | mm | CNC見積・試作用',2.6);text(260,8,f'{PAGE} / 10',2.6)
def end():c.restoreState();c.showPage()

start('MB4 / Rev F 一穴固定・クラウンアンカー','木部の穴を減らし、丸い保持部と低いスライダーを一体化。ミスミの標準金物に合わせた試作設計。')
if (ROOT/'bridge_preview.png').exists():c.drawImage(str(ROOT/'bridge_preview.png'),12,37,width=165,height=134,mask='auto')
notes(184,169,['各弦独立、弦間19、全幅75 mm','最低弦中心8／最高20 mm（参考）','前後調整12 mm（公称ばね条件）','切削2部品／弦、追加ピン不要','','木ねじ：前1＋後1、4弦で8本','後リブ後方の中央X0/Y85に1穴','後方座面厚5、皿座底残り3.4','','アンカー先端R7＋φ12クラウン','本体高さ8、保持部だけ高さ10','高さ：M4平先×8/12/16、各弦4本','固定：M3×12/16/20/25、各弦2本','後方：M4×30・ねじ長20＋ばね','裏面に各弦のピエゾ窪み'],size=3,leading=7)
notes(14,29,['球端から弦を伸ばす構成はRay Rossのサドルレス方式を参考。独自の一体クラウン式で、音響特性は未評価。','曲線とRはCNC用STEPへ反映。木部・実弦の適合、強度、疲労はまず1弦分の実物で検証。'],size=3,leading=6);end()
start('B04 / 有機形状ベース・取付穴','4個 | A6061-T6 | 18×90×25 | 前側板厚3、固定タップ部6、後方木ねじ座面5')
s=1.35;y0=34
for xc,bottom,label in [(42,False,'上面'),(111,True,'裏面（同じ座標方向）')]:
 text(xc-17,169,label);rect(xc-9*s,y0,18*s,90*s,4*s);line((xc,y0-4),(xc,y0+90*s+4),True)
 for xx,yy in [(0,5),(0,85)]:circle(xc+xx*s,y0+yy*s,1.9*s);circle(xc+xx*s,y0+yy*s,3.5*s)
 for xx in (-6,6):
  circle(xc+xx*s,y0+46*s,1.25*s)
  if not bottom:rect(xc+(xx-3)*s,y0+43*s,6*s,6*s,1*s)
 if bottom:circle(xc,y0+20*s,6.25*s);rect(xc,y0+18.9*s,9*s,2.2*s)
 else:
  rect(xc-9*s,y0+67*s,18*s,6*s,.8*s)
  for xx in (-9,6):rect(xc+xx*s,y0+60.5*s,3*s,6.5*s);rect(xc+xx*s,y0+73*s,3*s,7*s)
  line((xc-9*s,y0+78*s),(xc+9*s,y0+78*s),True);line((xc-9*s,y0+80*s),(xc+9*s,y0+80*s),True)
 dh(xc-9*s,xc+9*s,y0-10,'18');dv(xc-9*s-8,y0,y0+90*s,'90')
notes(155,166,['基準：X=幅中心、Y=前端、Z=ボディ面。','前木ねじ：(0,5)、φ3.8貫通3。','後木ねじ：(0,85)、φ3.8貫通5。','各穴：上面皿φ7、90°、深さ1.6。','前皿座底Z=1.4／後皿座底Z=3.4。','後方平面Z=5、Y=80〜90。','Y=78〜80はZ=3→5の滑らかな遷移。','','固定M3：(±6,46)、貫通6、下穴φ2.5。','パッド：6×6、中心(±6,46)、上端Z6。','裏面ピエゾ：(0,20)、φ12.5深さ1.5。','配線溝：X=0〜9、Y=18.9〜21.1、','裏面深さ1.2、右側面に開放。','','外形平面R4、前側上縁R0.5／下縁R0.2。','後方平面の外周上縁R0.6。STEPを併用。'],size=3,leading=7);end()

start('B04 / アーチ・曲線リブ・接続R','側面曲線は平面スケッチの押出し。3軸切削＋反転＋後端穴加工の範囲で仕上げる。')
# Front outline of the arched wall, exact radii specified; Bezier used for PDF display only.
s=2.8;xc=46;z0=82;k=.55228475
p=c.beginPath();p.moveTo(xc-9*s,z0);p.lineTo(xc+9*s,z0);p.lineTo(xc+9*s,z0+13*s)
p.curveTo(xc+9*s,z0+(13+9*k)*s,xc+9*k*s,z0+22*s,xc,z0+22*s)
p.curveTo(xc-9*k*s,z0+22*s,xc-9*s,z0+(13+9*k)*s,xc-9*s,z0+13*s);p.close();c.drawPath(p)
rect(xc-2.25*s,z0+1.75*s,4.5*s,16.5*s,2.25*s);text(21,157,'後壁正面：頂部R9',3.2)
# Side envelope: coordinates Y60..90, central wall and side ribs superposed.
s=1.85;x0=18;z=25
rect(x0,z,30*s,3*s);rect(x0+7*s,z+3*s,6*s,22*s)
p=c.beginPath();p.moveTo(x0+.5*s,z+3*s)
p.curveTo(x0+(0.5+2/3*3.25)*s,z+3*s,x0+(7-2/3*3.25)*s,z+(16-2/3*13)*s,x0+7*s,z+16*s)
c.drawPath(p)
p=c.beginPath();p.moveTo(x0+20*s,z+5*s)
p.curveTo(x0+(20-2/3*3.5)*s,z+5*s,x0+(13+2/3*3.5)*s,z+(16-2/3*11)*s,x0+13*s,z+16*s);c.drawPath(p)
line((x0+20*s,z+5*s),(x0+30*s,z+5*s));text(14,18,'中央後壁と外側リブを重ねた側面包絡図（簡略）',2.8)
notes(126,169,['後壁：幅18、Y=67〜73、厚6。','X=±9の肩Z=16、頂部Z=25。','頂部真円R9、円中心X=0/Z=16。','前後外周稜線R0.8、中央前根元R0.8。','','リブ幅3：X[-9,-6]、[6,9]。','前上辺：二次Bezier、制御点(Y,Z)','(60.5,3) → (63.75,3) → (67,16)。','後上辺：(80,5) → (76.5,5) → (73,16)。','底面Z=3、露出曲線の2縁R0.6。','','後方の板厚遷移：三次Bezier。','(78,3) → (78+2/3,3) →','(78+4/3,5) → (80,5)。','後壁長穴：中心X0/Z13、幅4.5、全長16.5。','後方M4軸Z=7〜19、座金φ8/4.5/t0.5。'],size=3,leading=7);end()

start('A05 / 一体クラウン・アンカー','4個 | C3604 | 18×42×最高10 | 本体高さ8 | 別部品のピン・横穴・止め輪を追加しない')
s=1.95;y0=66
def anchor_plan(xc,y0,s):
 def pt(x,y):return xc+x*s,y0+y*s
 p=c.beginPath();p.moveTo(*pt(-7,7));k=.55228475
 p.curveTo(*pt(-7,7-7*k),*pt(-7*k,0),*pt(0,0));p.curveTo(*pt(7*k,0),*pt(7,7-7*k),*pt(7,7))
 p.curveTo(*pt(7,9),*pt(9,9),*pt(9,11));p.curveTo(*pt(9,14),*pt(8.6,15),*pt(8.6,18));p.curveTo(*pt(8.6,21),*pt(9,22),*pt(9,25));p.lineTo(*pt(9,39))
 p.curveTo(*pt(9,39+3*k),*pt(6+3*k,42),*pt(6,42));p.lineTo(*pt(-6,42));p.curveTo(*pt(-6-3*k,42),*pt(-9,39+3*k),*pt(-9,39));p.lineTo(*pt(-9,25))
 p.curveTo(*pt(-9,22),*pt(-8.6,21),*pt(-8.6,18));p.curveTo(*pt(-8.6,15),*pt(-9,14),*pt(-9,11));p.curveTo(*pt(-9,9),*pt(-7,9),*pt(-7,7));p.close();c.drawPath(p)
for xc,bottom,label in [(38,False,'上面'),(99,True,'裏面（同じ座標方向）')]:
 text(xc-15,165,label);anchor_plan(xc,y0,s)
 if bottom:
  for xx in (-6,6):rect(xc+(xx-3)*s,y0+22*s,6*s,20*s,1*s)
 else:
  circle(xc,y0+9*s,6*s);rect(xc-1.7*s,y0,3.4*s,6*s);rect(xc-4*s,y0+6*s,8*s,11*s,1.5*s)
 for xx in (-5,5):
  for yy in (15,20.5):circle(xc+xx*s,y0+yy*s,1.65*s)
 for xx in (-6,6):rect(xc+(xx-1.7)*s,y0+24.3*s,3.4*s,15.4*s,1.7*s)
 dh(xc-9*s,xc+9*s,y0-8,'18')
dv(14,y0,y0+42*s,'42')
notes(143,168,['本体Z0〜8、クラウンのみZ10。','クラウン：中心(0,9)、φ12、','本体と一体、上縁R0.8／根元R0.4。','外形先端R7、後端角R3、くびれはSTEP。','本体上縁R0.5、下面R0.3。','','ポケット：X±4、Y6〜17、底Z2、R1.5。','保持肩Y6、弦溝幅3.4、底Z3.3。','クラウン上の弦溝縁R0.25。','短い窪みで後方タップ前の肉を残す。','','高さM4：(±5,15)、(±5,20.5)、','M4×0.7-6H貫通8、下穴φ3.3。','固定長穴：(±6,32)、幅3.4／全長15.4。','裏面逃げ：(±6,32)、6×20、深さ3、R1。','後方タップ：X0/Z4、Y42より前方、','M4×0.7-6H有効20、φ3.3深22＋先端1。'],size=2.9,leading=7)
rect(20,28,84,16);rect(26,44,24,4,1.6);text(117,43,'側面概念：本体8、クラウン最高10（詳細形状はSTEP）',2.9)
text(14,19,'輪郭図の円弧は描画近似。外形・Rの加工基準はSTEP、穴・タップ・機能寸法は本図とfeatures.csv。',2.9);end()
start('高さ・前後調整 / 標準ねじの選択','高さH=8＋g、g=0〜12。高さの平先はM4、固定用の頭付きねじはM3。混同しないこと。')
notes(14,168,['高さ：M4平先×8（g=0〜4）、×12（4<g<=8）、×16（8<g<=12）。4本／弦。','公称ねじ掛かりL−g=4〜8。上端は本体上面と同じか、埋まる。端の面取りは実物で確認。','前後：アンカー前端q=8〜20、保持肩Y=q＋6=14〜26。M4一回転=0.7 mm。','後方はSCB4-30：M4×30、半ねじ20、首下の非ねじ部10。頭座Y73.5、先端Y43.5。','アンカーへの公称重なり6.5〜18.5。非ねじ部先端Y63.5と最大後端Y62の隙間1.5。','ねじ先端面取り・不完全ねじを含むため、実物の有効掛かり6以上と首下干渉を確認。','参考ボールはポケット中心Y14から入れ、保持肩Y6へ寄せる。後方ねじ先端とは6.5以上離れる。','ばね作動長25−q=17〜5、公称ばね力0.294〜1.47 N。弦張力は後方ねじと固定部で受ける。'],leading=7)
text(14,101,'固定M3の長さと座金・スペーサ合計厚（外径6以下）',3.6)
for i,t in enumerate(['g (mm)','弦中心H','固定ねじL','座金合計t','先端Z']):text(20+49*i,91,t,3.1)
for j,g in enumerate((0,2,4,6,8,10,12)):
 L=next(v for v in (12,16,20,25) if v>=11+g);t=.5*math.ceil((L-11-g+.2)/.5-1e-8);tip=11+g+t-L
 for i,val in enumerate((g,8+g,L,t,tip)):text(20+49*i,82-6*j,str(val),3)
notes(14,29,['先端Z=11＋g＋t−Lを0.2〜0.7に合わせ、木部への突出を防ぐ。寸法公差を含め実測調整。','ばね自由長±1.5：作動長>=実測自由長−15。5 mmは公称許容端で、ロットによって調整幅を縮める。'],size=3,leading=7);end()
rows=[['B04','一穴・曲線ベース A6061-T6',4,'18×90×25、板3／固定6／後座5'],['A05','一体クラウン C3604',4,'18×42×10、本体8／裏逃げ3'],['H01','SCB4-30 SUS M4×30 半ねじ',4,'ねじ部20、頭φ7×4／六角3'],['H02','WSJS-SUS-M4 小形座金',4,'φ8/4.5/t0.5、後方用'],['H03','UY6-20 または E-GUY6-20',4,'OD6/線径0.35/L20、k0.098 N/mm'],['H04','MSSFS4-8/12/16 SUS平先','16使用','高さ用、六角2、gで交換'],['H05','SCB3-12/16/20/25 SUS',8,'固定用、gに応じ5頁から選択'],['H06','SUS小径座金／スペーサ','8組','OD6以下／ID3.2以上、合計t選択'],['H07','SUS皿木ねじ 3.5×20',8,'前4＋後4、頭φ7以下／90°'],['P01','ピエゾφ12以下＋接着・配線',4,'実装総厚1.2以下、各弦個別']]
start('部品表 / CNC発注・標準品購入','丸みは一体切削。CNC部品は8点、木部の固定穴は8個。購入品は同封のMISUMI選定表を参照。')
for i,t in enumerate(['ID','品名','4弦数量','仕様・選択条件']):text([14,32,159,181][i],168,t,3.2)
for j,row in enumerate(rows):
 for x,val in zip([14,32,159,181],row):text(x,157-8*j,str(val),2.65)
notes(14,66,['一般寸法±0.10、機能穴・座標±0.05、指定R±0.05。M3×0.5／M4×0.7-6H。','接触平面は平面度0.05、Ra3.2目安。残る穴口・溝縁はC0.1以下でバリ取り。','3軸切削＋反転＋後端穴加工。曲線リブ・各Rは工具パスが増えるため加工先で見積確認。','STEPのタップは下穴表現。組立STEPの金物・ばね・弦・ピエゾは参考外形で発注対象外。','後方ねじの半ねじは使用可能。高さ・長さを変えた場合は首下とタップの干渉を再確認。','実弦ボール・巻き部、支持剛性、ねじと木部の保持力、音響は1弦試作で確認する。'],size=3,leading=7);end()
start('取付テンプレート / 1:1','A4横・100%で印刷。50 mm枠を実測。Rev F専用の新規穴あけ用。Rev Eの後方左右2穴を中央1穴へ変更。')
x0=78;y0=58
for x in (-28.5,-9.5,9.5,28.5):
 rect(x0+x-9,y0,18,90,4);line((x0+x,y0-12),(x0+x,y0+90),True)
 for xx,yy in ((0,5),(0,85)):
  circle(x0+x+xx,y0+yy,1.9);line((x0+x+xx-2,y0+yy),(x0+x+xx+2,y0+yy));line((x0+x+xx,y0+yy-2),(x0+x+xx,y0+yy+2))
 circle(x0+x+7,y0+20,1.5)
for yy in (14,26):line((x0-37.5,y0+yy),(x0+37.5,y0+yy),True)
dh(x0-37.5,x0+37.5,y0-18,'全幅75');dh(x0-28.5,x0-9.5,y0+96,'19')
rect(210,36,50,50);dh(210,260,22,'チェック50 mm')
notes(152,169,['各弦：前(0,5)、後(0,85)。','φ3.8は金属の通し穴径。','木部下穴は木材・ねじから選ぶ。','','配線落とし候補：X＋7、Y=20、φ3。','内部配線経路を確認して位置を決定。','','前端位置はナットから','スケール長−16を初期候補とする。','実弦の補正量を肩Y=14〜26で合わせ、','穴あけ前に取付位置を確定する。','既存5穴とは非互換、新規穴あけ用。'],size=3,leading=7)
text(14,27,'DXFも同じmm座標。弦間・ボディ端までの余白・既存穴との距離を実測して取付。',3);end()

start('ピエゾ・組立・実物確認','各弦独立の金属モジュール。共通の木部を通る振動は残るため、4chで分離度を評価する。')
notes(14,166,['裏面窪みφ12.5／深さ1.5。φ12以下の素子を金属裏面へ接着。厚さ総計1.2以下。','木部まで0.3以上離し、素子を木部に挟んで圧壊させない。底板の残り厚1.5。','各素子を個別の高入力インピーダンス・バッファで読み出し、1弦ずつ弾いて4ch録音。','','まずB04/A05を各1個試作。実弦のボール・結び・巻き部・弦軸高さを確認。','ベースを前後2本の木ねじで固定後、アンカー・高さM4・固定M3・ばね・後方M4を組む。','固定M3の長さと座金合計厚は5頁で選択し、先端が木部へ出ないよう実測する。','弦を緩める → 固定M3を緩める → 高さ → オクターブ → 固定M3を締める。','4本の高さねじを均等に当てる。最大高さで支持のガタ・横揺れ・ねじの緩みを確認。','','ばねは前後位置を戻すための小荷重部品。弦張力をばねの許容荷重と比較しない。','弦張力を徐々に加え、保持肩・後方ねじ・壁・木ねじの変位と緩みを確認。','φ6×厚4.75の円筒ボールは参考。実弦により弦中心8＋gは変わり得る。','特定のJazz/P Bassへの適合、既存穴、木部厚、裏側の空洞は実測する。','','Ray Ross参照：Deviserの開発者説明 https://www.deviser.co.jp/rayross/about','本案はボール保持クラウンと高さねじの構造。Ray Rossのtone pin機構そのものではない。','同じ音質・低摩擦・弦寿命を保証するものではなく、試作後に評価する。'],size=3.05,leading=7);end()
start('後方中央1穴 / リブを残して木部の穴を削減','各弦：前X0/Y5＋後X0/Y85。4弦合計8本。前後の穴間距離80 mm。')
if (ROOT/'bridge_rear_preview.png').exists():c.drawImage(str(ROOT/'bridge_rear_preview.png'),12,37,width=165,height=134,mask='auto')
notes(184,169,['Rev E：後方左右2穴、計12本。','Rev F：後方中央1穴、計8本。','4本減、既存左右穴の転用は想定外。','','後リブの後端Y80より5 mm後。','後方座面厚5を維持。','皿φ7・90°・深さ1.6。','皿座底から下面まで3.4。','','奥行90を維持して工具域を残す。','組立状態でφ6ドライバーを確認。','2本固定でも回転の抑制は必要。','ボディとの面接触と木ねじで受ける。','','強度の倍率・許容張力は未算定。','ねじ1本追加での強度保証はしない。'],size=3,leading=7)
notes(14,29,['全R・曲線リブは実ソリッド。後壁中央前根元はR0.8にしてOD6ばねの最低位置を逃がす。','木ねじの頭・皿角・木部下穴・埋込みは現物で照合。加工図のφ3.8は金属側の通し穴。'],size=3,leading=6);end()
start('MISUMI参照 / 購入数と納期で安さを比較','2026-10-05の公開価格。税別。納期割引は購入時に指定が必要。送料・価格・出荷日は注文時に確認。')
price_rows=[['部品','数量条件','通常単価','納期割引単価','発注例'],['UY6-20','1 / 4〜9個','250円','125 / 87円','1弦125円／4弦348円'],['E-GUY6-20','10個以上・10個単位','78円','未確認','10個780円（予備6個）'],['SCB4-30','10〜29本','77円','19円','10本190円（使用4本）'],['SCB3-16','10〜29本','55円','15円','10本150円（使用8本）'],['MSSFS4-8','10〜199本','117円','38円','高さ低域用／4本×4弦'],['MSSFS4-12','10〜199本','118円','38円','高さ中域用・必要数で比較'],['MSSFS4-16','10〜199本','118円','38円','高さ高域用・必要数で比較']]
for j,row in enumerate(price_rows):
 for x,t in zip([14,73,126,171,224],row):text(x,168-9*j,t,2.85)
notes(14,94,['標準品の納期割引は10日目表示。早さ優先なら通常納期と総額で比較する。','E-GSCBは200本等、E-GMSSFSは500本等の最低注文数。1本の安さだけで選ばない。','高さねじをM4へ統一：MSSFS4-8/12/16を選択でき、M3×16の1000本箱を回避。','座金・スペーサはOD6以下。安価な大径M3座金へ置換すると隣のモジュールと干渉し得る。','リンクと追加型番・価格はhardware_sources.txt / MISUMI_purchase_options.csv。'],leading=7)
notes(14,51,['ばね：OD6、線径0.35、内径公称5.3、自由長20、k0.098 N/mm、密着3.85、許容たわみ15。','自由長公差±1.5。作動長>=実測自由長−15を確認（例L21.5なら最短6.5、q最大18.5）。','CAD確認：2部品STEP再読込／64ソリッド、9調整条件、1201高さ、球装填4位置、後方工具域。','確認範囲：ねじは下穴・円筒表現。嵌合ねじ・公差・ばね端形状・実物強度／疲労／音響は未検証。','Rev Eの簡易応力比較値は本版へ転用しない。本版の後方1穴・M4支持を実物で確認する。'],size=3,leading=7);end();c.save()
with (ROOT/'BOM.csv').open('w',encoding='utf-8-sig',newline='') as f:
 w=csv.writer(f);w.writerow(['ID','品名','4弦数量','仕様']);w.writerows(rows)
features=[
 ['B04','blank','18 x 90; plateZ0..3; max25','A6061-T6; planR4; front topR0.5 bottomR0.2'],
 ['B04','front mount','(0,5)','D3.8 THRU3; CSK D7 90deg depth1.6; remaining1.4'],
 ['B04','rear mount','(0,85)','D3.8 THRU5; CSK D7 90deg depth1.6; remaining3.4'],
 ['B04','rear flange','Y80..90 topZ5','outer top rimR0.6; cubic ramp Y78..80 Z3..5; see STEP'],
 ['B04','ramp Bezier control YZ','(78,3); (78+2/3,3); (78+4/3,5); (80,5)','cubic profile extruded width18'],
 ['B04','clamp pads','(+/-6,46)','6x6 topZ6; planR1 topR0.2; integral'],
 ['B04','clamp taps','(+/-6,46)','M3x0.5-6H THRU6; drillD2.5'],
 ['B04','piezo','(0,20)','bottom D12.5 depth1.5; remaining1.5'],
 ['B04','wire','X0..9 Y18.9..21.1','bottom depth1.2; side open'],
 ['B04','wall','Y67..73; shouldersZ16; apexZ25','XZ crownR9 center(0,16); front/back profileR0.8; front central rootR0.8'],
 ['B04','front ribs','X[-9,-6] and[6,9]','YZ quadratic Bezier (60.5,3),(63.75,3),(67,16); floorZ3; exposed curved edgesR0.6'],
 ['B04','rear ribs','X[-9,-6] and[6,9]','YZ quadratic Bezier (80,5),(76.5,5),(73,16); floorZ3; exposed curved edgesR0.6'],
 ['B04','rear slot','X0 Z13','width4.5 total16.5 THRU6; axesZ7..19'],
 ['B04','rear washer clearance','X+/-4.5 Y73..74','floorZ2'],
 ['A05','blank','18x42; bodyZ0..8; crown topZ10','C3604; noseR7; waist Beziers and rearR3: STEP; upperR0.5; lowerR0.3'],
 ['A05','crown','center(0,9); D12; topZ10','integral boss; upperR0.8 rootR0.4'],
 ['A05','ball cradle','X+/-4 Y6..17','floorZ2; planR1.5; shoulderY6'],
 ['A05','string slot','X+/-1.7 Y0..22','floorZ3.3; crown upper lipsR0.25'],
 ['A05','height taps','(+/-5,15),(+/-5,20.5)','M4x0.7-6H THRU8; drillD3.3'],
 ['A05','clamp slots','(+/-6,32)','width3.4 total15.4; clamp lane materialZ3..8'],
 ['A05','under relief','(+/-6,32)','6x20 depth3; planR1; sides open'],
 ['A05','rear tap','X0 Z4 fromY42 towards-Y','M4x0.7-6H usable20 min; drillD3.3 depth22+point1.0']]
with (ROOT/'features.csv').open('w',encoding='utf-8-sig',newline='') as f:
 w=csv.writer(f);w.writerow(['part','feature','location_mm','machining']);w.writerows(features)
d=ezdxf.new('R2010');d.units=4;m=d.modelspace()
for layer,color in [('OUTLINE',7),('MOUNT_CENTER',1),('STRING_CENTER',3),('WIRE_OPTIONAL',5),('REFERENCE',4)]:d.layers.new(layer,dxfattribs={'color':color})
for x in (-28.5,-9.5,9.5,28.5):
 r=4;left=x-9;right=x+9
 for a,b in [((left+r,0),(right-r,0)),((right,r),(right,90-r)),((right-r,90),(left+r,90)),((left,90-r),(left,r))]:m.add_line(a,b,dxfattribs={'layer':'OUTLINE'})
 for center,angles in [((right-r,r),(270,360)),((right-r,90-r),(0,90)),((left+r,90-r),(90,180)),((left+r,r),(180,270))]:m.add_arc(center,r,*angles,dxfattribs={'layer':'OUTLINE'})
 m.add_line((x,-8),(x,98),dxfattribs={'layer':'STRING_CENTER'})
 for xx,yy in ((0,5),(0,85)):m.add_circle((x+xx,yy),1.9,dxfattribs={'layer':'MOUNT_CENTER'})
 m.add_circle((x+7,20),1.5,dxfattribs={'layer':'WIRE_OPTIONAL'})
for yy in (14,26):m.add_line((-37.5,yy),(37.5,yy),dxfattribs={'layer':'REFERENCE'})
m.add_lwpolyline([(50,0),(100,0),(100,50),(50,50)],close=True,dxfattribs={'layer':'REFERENCE'})
m.add_text('CHECK 50 mm; PRINT 1:1; REV F NEW HOLES',dxfattribs={'height':2.5,'insert':(50,55),'layer':'REFERENCE'})
m.add_text('FRONT DATUM Y=0; NUT DISTANCE: SCALE - 16 mm (INITIAL)',dxfattribs={'height':2.5,'insert':(-37.5,-18),'layer':'REFERENCE'})
d.saveas(ROOT/'MB4_mount_template_1to1.dxf')
print('10-page Rev F drawings, BOM, feature list, DXF complete')
