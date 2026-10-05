"""Rev D shop drawings, mm. STEP authoritative for formed outlines."""
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
c.setTitle('MB4 Rev D - reinforced screw and spring prototype'); PAGE=0
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
 text(12,8,'MB4 | Rev D | 2026-10-05 | mm | CNC見積・試作用',2.6);text(260,8,f'{PAGE} / 9',2.6)
def end():c.restoreState();c.showPage()

S=json.loads((ROOT/'cad/strength_comparison.json').read_text())
start('MB4 / Rev D 補強仕様','最低弦中心8 mmを維持し、後壁・固定タップ・アンカー中央の荷重経路を補強。')
if (ROOT/'bridge_preview.png').exists():c.drawImage(str(ROOT/'bridge_preview.png'),12,37,width=165,height=134,mask='auto')
notes(186,167,['弦中心：8〜20 mm／前後12 mm','後方M4×35全ねじ＋圧縮バネ','後壁高さ25 mm（弦高とは別）','左右に前後の一体三角リブ','固定タップ部：厚さ3→6 mm','固定ねじ掛かり：5.3〜5.8 mm','','切削部品は1弦2個','B02 ベース：A6061-T6 ×4','A03 アンカー：C3604 ×4','後尾高さ6→8／裏面に逃げ','固定長穴をX=±6へ移動','','外周R2〜R3、稜線R0.2','各弦ピエゾ用窪みを維持'],size=3,leading=7)
notes(14,29,['追加部品は不要。既存と同じ3軸切削＋反転＋後端穴加工で、リブと局所厚肉を追加。','後壁の公称曲げ応力は簡易比較で約39%減。強度保証・FEAではない。条件と限界は9ページ。'],size=3,leading=6);end()

start('B02 / 補強ベース・上面と裏面','4個 | A6061-T6 | 18×82×25 | 前側板厚3、固定タップ付近のみ厚さ6')
s=1.5;y0=32
for xc,bottom,label in [(42,False,'上面'),(111,True,'裏面（同じ座標方向）')]:
 text(xc-17,167,label);rect(xc-9*s,y0,18*s,82*s,3*s);line((xc,y0-4),(xc,y0+82*s+4),True)
 for yy in (4,78):circle(xc,y0+yy*s,1.9*s);circle(xc,y0+yy*s,3.5*s)
 for xx in (-6,6):
  circle(xc+xx*s,y0+46*s,1.25*s)
  if not bottom:rect(xc+(xx-3)*s,y0+43*s,6*s,6*s,1*s)
 if bottom:
  circle(xc,y0+20*s,6.25*s);rect(xc,y0+18.9*s,9*s,2.2*s)
 else:
  rect(xc-9*s,y0+67*s,18*s,6*s,1*s);rect(xc-4.5*s,y0+73*s,9*s,1*s)
  for xx in (-9,6):
   rect(xc+xx*s,y0+63*s,3*s,4*s);rect(xc+xx*s,y0+73*s,3*s,3*s)
 dh(xc-9*s,xc+9*s,y0-10,'18');dv(xc-9*s-8,y0,y0+82*s,'82')
notes(155,166,['基準：X=幅中心、Y=前端、Z=ボディ面。','取付穴：(0,4)、(0,78)、φ3.8貫通。','上面皿座：φ7、90°、深さ1.6。','固定タップ：(±6,46)、M3×0.5貫通6。','下穴φ2.5、下面はZ=0。','増肉パッド：幅6×長6、中心(±6,46)。','Z=3〜6、平面R1、上面稜線R0.2。','','裏面ピエゾ：(0,20)、φ12.5、深さ1.5。','残り板厚1.5。配線溝X=0〜9、','Y=18.9〜21.1、裏面から深さ1.2。','','後壁：Y=67〜73、Z=3〜25、幅18。','座金逃げ：X=±4.5、Y=73〜74、底Z=2。','リブ・後壁長穴・根元Rは次ページ。','加工公差は6ページ、STEPと併用。'],size=3,leading=7);end()

start('B02 / 一体リブ・後壁・根元R','左右各2本、計4本の三角リブ。アンカー移動域と工具アクセスを避けて配置。')
# Side view of outer rib envelope in Y-Z coordinates, origin shifted for detail.
s=3.2;x0=21;z0=51
rect(x0,z0,19*s,3*s);rect(x0+7*s,z0+3*s,6*s,22*s)
for pts in [[(3,3),(7,3),(7,15)],[(13,3),(16,3),(13,15)]]:
 p=c.beginPath();p.moveTo(x0+pts[0][0]*s,z0+pts[0][1]*s)
 for yy,zz in pts[1:]:p.lineTo(x0+yy*s,z0+zz*s)
 p.close();c.drawPath(p)
text(20,144,'外側面の包絡図（Y=60を左端に表示）',3.1)
dh(x0+3*s,x0+7*s,z0-10,'前4');dh(x0+7*s,x0+13*s,z0-10,'壁6');dh(x0+13*s,x0+16*s,z0-10,'後3')
dv(x0+19*s+9,z0,z0+25*s,'25')
notes(126,168,['リブX：左−9〜−6、右6〜9（幅3）。','前側の三角断面(Y,Z)：','(63,3)、(67,3)、(67,15)。','後側：(73,3)、(76,3)、(73,15)。','露出した斜辺2縁R0.2／リブ。','前側の後壁根元：中央幅約12、R1。','ベース・後壁・リブ・増肉部を一体切削。','','後壁の平面四隅R1、上面稜線R0.8。','縦長穴中心：X=0、Z=13。','幅4.5、全長16.5、Y方向貫通6。','M4ねじ軸の可動範囲：Z=7〜19。','後方座金：DIN433 M4、φ8/4.3/t0.5。','頭下位置Y=73.5、ねじM4×35全ねじ。','最高位置の座金上端Z=23、後壁上端25。'],size=3.1,leading=7)
notes(14,30,['アンカー最後端は最大Y=62。前リブはY=63からなので、前後調整12 mmを維持する。','ばね外径5は中央に配置。前側根元R1の上端Z=4に対し、最低位置のばね下端Z=4.5。'],size=3,leading=7);end()

start('A03 / 強化アンカー・裏面逃げ','4個 | C3604 | 18×42×10、後尾高さ8 | 後方タップM4、固定長穴X=±6')
s=1.95;y0=66
for xc,bottom,label in [(38,False,'上面'),(99,True,'裏面（同じ座標方向）')]:
 text(xc-15,165,label);rect(xc-9*s,y0,18*s,42*s,2*s)
 line((xc-9*s,y0+22*s),(xc+9*s,y0+22*s),True)
 if bottom:
  for xx in (-6,6):rect(xc+(xx-3)*s,y0+22*s,6*s,20*s,1*s)
 else:
  rect(xc-1.7*s,y0,3.4*s,6*s);rect(xc-4*s,y0+6*s,8*s,16*s,1.5*s)
 for xx in (-6,6):
  for yy in (11,18):circle(xc+xx*s,y0+yy*s,1.25*s)
  rect(xc+(xx-1.7)*s,y0+24.3*s,3.4*s,15.4*s,1.7*s)
 dh(xc-9*s,xc+9*s,y0-8,'18')
dv(14,y0,y0+42*s,'42')
notes(143,167,['前部Y=0〜22、高さ10。後尾Y=20〜42、高さ8。','裏面逃げ：中心(±6,32)、幅6×長20。','下面から深さ3、平面四隅R1。','後尾の中央は下面Z=0から残す。','左右の固定座下面はZ=3、上面Z=8。','','ボールポケット：X=±4、Y=6〜22。','深さ8、底Z=2、四隅R1.5。保持肩Y=6。','弦スリット：幅3.4、底Z=3.3、長い上縁R0.2。','高さタップ：(±6,11)、(±6,18)、M3×0.5貫通。','固定長穴：(±6,32)、幅3.4、全長15.4貫通。','後尾：M4×0.7-6H、X=0、Z=4、後端Y=42。','有効20以上、下穴φ3.3深さ22＋先端1.0。','外周平面R2、上下外周稜線R0.2。'],size=2.95,leading=7)
# Central and clamp-lane sections separately, to make undercut explicit.
x=20;z=28;sx=2
rect(x,z,22*sx,10*sx);rect(x+22*sx,z,20*sx,8*sx)
line((x+22*sx,z+4*sx),(x+42*sx,z+4*sx),True)
text(112,43,'中央断面：後尾高さ8、後方タップ軸Z=4',3)
text(112,34,'固定座断面：後尾のZ=0〜3を逃がす',3)
text(14,19,'裏面逃げの面は増肉パッド上面と最低位置で接触。g>0では高さねじ4本が支持する。',3);end()

start('調整・弦装填・ネジ長さの選択','弦中心H=8＋g。g=0〜12。後尾の裏面逃げは、ベース増肉パッドを避けるための形状。')
notes(14,167,['高さ：M3平先×10（g=0〜6）、M3平先×16（g>6〜12）。ねじ掛かり4以上。','前後：アンカー前端q=8〜20、保持肩Y=q＋6=14〜26。調整幅12。','ばね作動長25−q=17〜5。後方M4ねじ1回転0.7 mm、締めて後へ引き、緩めて前へ押す。','後方M4×35は全ねじを指定。アンカー内ねじ掛かり11.5以上（有効上限19.5を想定）。','ボールはポケット中央Y=14付近から入れ、前肩Y=6まで滑らせる。φ6×厚4.75参考。','後方ねじの先端は最前進時でアンカー内Y=18.5、装填ボール後端Y=17と1.5離れる。','まずベースを木部へ固定し、その後で後方ねじを入れる。後側木ねじの工具スペースを確保。'],leading=7.5)
text(14,104,'固定ねじ2本／弦：M3全ねじ＋DIN433小径座金／スペーサ（外径6以下）',3.6)
for i,t in enumerate(['g (mm)','弦中心H','固定ねじL','座金合計t','先端Z']):text(20+49*i,91,t,3.1)
for j,g in enumerate((0,2,4,6,8,10,12)):
 L=next(v for v in (12,16,20,25) if v>=11+g);t=.5*math.ceil((L-11-g+.2)/.5-1e-8);tip=11+g+t-L
 for i,val in enumerate((g,8+g,L,t,tip)):text(20+49*i,82-6*j,str(val),3)
notes(14,28,['先端Z=11＋g＋t−Lを0.2〜0.7に調整。厚さ6のベース内ねじ掛かり5.3〜5.8。','gと金物厚を実測し、木部への突出を避ける。弦を緩めて調整し、最後に固定ねじ2本を締める。'],size=3,leading=7);end()

rows=[['B02','補強ベース A6061-T6',4,'18×82×25、板3／固定部6'],['A03','強化アンカー C3604',4,'18×42×10、後尾8／裏逃げ3'],['H01','SUS M4×35 六角穴付 全ねじ',4,'A2-70等、頭φ7×4、六角3'],['H02','SUS DIN433 M4座金',4,'φ8/4.3/t0.5、後方用'],['H03','SUS圧縮ばね OD5/線径0.3/自由長20',4,'作動5〜17、内径4.4参考、密着3.15'],['H04','SUS M3平先止めねじ×10',16,'g=0〜6、高さ用、六角1.5'],['H05','SUS M3平先止めねじ×16',16,'g>6〜12への交換セット'],['H06','SUS M3全ねじ×12/16/20/25','8使用','gに応じて5ページから選択'],['H07','SUS DIN433 M3座金／スペーサ','8組','外径6以下、内径3.2、t0.5〜5.5'],['H08','SUS皿木ねじ3.5×20',8,'頭φ7以下、木部厚と下穴は実測'],['P01','ピエゾφ12以下＋接着・配線',4,'実装総厚1.2以下、各弦個別']]
start('部品表・切削・仕上げ','汎用金物を利用。後方だけM4へ変更。固定と高さはM3。小径座金はDIN433を指定。')
for i,t in enumerate(['ID','品名','4弦数量','仕様・選択条件']):text([14,32,159,181][i],168,t,3.2)
for j,row in enumerate(rows):
 for x,val in zip([14,32,159,181],row):text(x,157-8*j,str(val),2.65)
notes(14,60,['ばね参考：MBA CS-0500-0200-03-S4-C。内径4.4参考にM4を通す。作動長・実寸を確認。','一般寸法±0.10、機能穴・座標±0.05、外周小R±0.05。M3×0.5／M4×0.7-6H。','接触平面は平面度0.05、Ra3.2目安。残る穴口・溝縁はC0.1以下でバリ取り。','3軸切削＋反転＋後端穴加工。リブ斜面・根元Rと、アンカー裏面逃げの加工パスを追加。','タップ・接触面を保護して表面処理。工具アクセス・最小工具径・タップ出口を加工先で確認。','座金厚の公差は実測してネジ長を合わせる。高い位置での支持剛性・緩みは試作評価。'],size=3,leading=7);end()

start('取付テンプレート / 1:1','A4横・100%で印刷。50 mm枠を実測。Rev Cと同じ外形・弦間・木部取付穴位置。')
x0=78;y0=58
for x in (-28.5,-9.5,9.5,28.5):
 rect(x0+x-9,y0,18,82,3);line((x0+x,y0-12),(x0+x,y0+90),True)
 for yy in (4,78):circle(x0+x,y0+yy,1.9);line((x0+x-3,y0+yy),(x0+x+3,y0+yy));line((x0+x,y0+yy-3),(x0+x,y0+yy+3))
 circle(x0+x+7,y0+20,1.5)
for yy in (14,26):line((x0-37.5,y0+yy),(x0+37.5,y0+yy),True)
dh(x0-37.5,x0+37.5,y0-18,'全幅75');dh(x0-28.5,x0-9.5,y0+96,'19')
rect(210,36,50,50);dh(210,260,22,'チェック50 mm')
notes(152,169,['各弦取付穴Y=4、78。','φ3.8は金属の通し穴径。','木部下穴は木材・ねじから選ぶ。','','配線落とし候補：X＋7、Y=20、φ3。','内部配線経路を確認して位置を決定。','','前端位置はナットから','スケール長−16を初期候補とする。','実弦の補正量を肩Y=14〜26で合わせ、','穴あけ前に取付位置を確定する。','既存5穴とは非互換、新規穴あけ用。'],size=3,leading=7)
text(14,27,'DXFも同じmm座標。弦間・ボディ端までの余白・既存穴との距離を実測して取付。',3);end()

start('ピエゾ・組立・試作評価','機構の独立と音響的な分離は別。ピエゾは各弦のベース裏面に接着する。')
notes(14,166,['ピエゾ：φ12以下、接着・配線を含む厚さ1.2以下。窪み深さ1.5で木部から0.3以上離す。','各素子を個別バッファで読み出す。共通木部を経由する機械的クロストークは残る。','必要な分離度と低域感度は1弦ずつ弾いて4ch録音で確認する。','','最初はB02/A03各1個。実弦のボール保持・装填・巻き部分の擦れ・弦軸高さを確認。','ベース固定後、アンカー・高さねじ・固定ねじ・ばね・後方M4を組み付ける。','g=0〜12の全域で、座金／スペーサ厚と固定ねじ先端の突出を確認する。','弦を緩める→固定ねじを緩める→高さ→オクターブ→固定ねじを締める。','弦を徐々に張り、後壁・ねじ・ボール・アンカーの移動と緩みを確認する。','弦張力は後方ねじが受ける。ばねは位置決め用であり、弦張力を支える要素ではない。','実物の強度・疲労・木ねじ保持力・音響は未検証。試験で締付条件と許容使用条件を決める。','φ6参考ボールで弦中心8＋gを設定。実弦のボール／巻き形状で実際の弦軸は変わり得る。','','後壁高さはRev Cの23から25へ増加。最大弦高20でのM4座金の当たり面を確保。','切削部品数は2個／弦。リブとパッドはベースから一体で削り出す。'],size=3.1,leading=7)
notes(14,44,['参照：MBA Springs catalogue p.20／使用ばねの作動長・密着長・内径。','https://files.minibearings.au/pdf/catalogues/Springs.pdf','Accu DIN433 M3/M4座金・M4×35全ねじ、NBK JIS B1176ねじ頭寸法表。','型番例・参照URLは部品選定メモ hardware_sources.txt に記載。'],size=2.8,leading=6);end()

start('補強の比較 / 計算条件と限界','同じ仮荷重・同じ最大弦高で比較。公称断面応力の改善を示すもので、許容荷重の決定ではありません。')
notes(14,168,['比較条件：水平350 N／弦（仮定）、g=12、弦中心高さ20。後壁を固定端の片持ち梁とする。','ねじ軸高さはRev C=18、Rev D=19。各高さの曲げモーメントM=350×(ねじ軸Z−断面Z)。','後壁＋リブの実CAD断面をZ=3.6〜18.6、0.2刻みで切断し、面積・重心・Ixxを取得。','断面係数W=Ixx／最大外縁距離、公称曲げ応力σ=M／W。固定パッドは断面計算から除く。'],leading=7)
cols=[16,141,188,239]
for x,t in zip(cols,['比較項目','Rev C','Rev D','比・変化']):text(x,127,t,3.5)
pc=S['peak_nominal_bending']['C'];pd=S['peak_nominal_bending']['D']
comparison=[['後壁 最大公称曲げ応力',f"{pc['nominal_bending_MPa']:.1f} MPa",f"{pd['nominal_bending_MPa']:.1f} MPa",'約39%低下'],['最大応力の断面Z',f"{pc['z']:.1f} mm",f"{pd['z']:.1f} mm",'条件を含め比較'],['後尾中央の有効断面概算','20.5 mm2','48.4 mm2','約2.36倍'],['後方ねじ 引張応力断面積','M3: 5.03 mm2','M4: 8.78 mm2','約1.75倍'],['固定M3 ねじ掛かり','2.3〜2.8 mm','5.3〜5.8 mm','3 mm増加']]
for j,row in enumerate(comparison):
 for x,t in zip(cols,row):text(x,115-9*j,t,3)
notes(14,61,['中央断面概算：C=4.6×6−π×1.5²、D=6×3＋8.6×5−π×2²。後方ねじ谷径相当を控除。','ねじ応力断面積：Bossard metric coarse-thread table。構造全体の耐荷重倍率ではありません。','局所応力集中、ねじ締付け、接触・支持剛性、疲労、木部、実弦張力は計算に含まない。','FEAや実験による強度保証は未実施。350 Nは比較用仮定で、推奨張力・許容荷重ではない。','再計算コード compare_sections.py、断面CSVと strength_comparison.json を収録。'],size=3,leading=7)
text(14,20,'出典：Bossard f-009-en.pdf（Materials screws & nuts）。部品出典URLは hardware_sources.txt。',2.7);end();c.save()
with (ROOT/'BOM.csv').open('w',encoding='utf-8-sig',newline='') as f:
 w=csv.writer(f);w.writerow(['ID','品名','4弦数量','仕様']);w.writerows(rows)
features=[
 ['B02','blank','18 x 82; plateZ0..3; walltop25','A6061-T6; outlineR3; edgeR0.2'],
 ['B02','mount','(0,4),(0,78)','D3.8 THRU3; CSK D7 90deg depth1.6'],
 ['B02','clamp pads','(+/-6,46)','6x6 topZ6; planR1 top edgeR0.2; integral'],
 ['B02','clamp taps','(+/-6,46)','M3x0.5-6H THRU6; drillD2.5'],
 ['B02','piezo','(0,20)','bottom D12.5 depth1.5; remaining1.5'],
 ['B02','wire','X0..9 Y18.9..21.1','bottom depth1.2; side open'],
 ['B02','wall','Y67..73 Z3..25','outlineR1; topR0.8; front central rootR1'],
 ['B02','front gussets','X[-9,-6] and[6,9]','YZ triangles (63,3),(67,3),(67,15); exposed diagonalsR0.2'],
 ['B02','rear gussets','X[-9,-6] and[6,9]','YZ triangles (73,3),(76,3),(73,15); exposed diagonalsR0.2'],
 ['B02','rear slot','X0 Z13','width4.5 total16.5 THRU6; axesZ7..19'],
 ['B02','rear washer clearance','X+/-4.5 Y73..74','top depth1; floorZ2'],
 ['A03','blank','18 x 42; frontY0..22 H10; tailY20..42 H8','C3604; outerR2 edgesR0.2'],
 ['A03','ball cradle','X+/-4 Y6..22','depth8 floorZ2; planR1.5; shoulderY6'],
 ['A03','string slot','X+/-1.7 Y0..22','floorZ3.3; two long top lipsR0.2'],
 ['A03','height taps','(+/-6,11),(+/-6,18)','M3x0.5-6H THRU10; drillD2.5'],
 ['A03','clamp slots','(+/-6,32)','width3.4 total15.4 THRU8; actual clamp lane materialZ3..8'],
 ['A03','under relief','(+/-6,32)','6x20 depth3 from bottom; plan cornersR1; sides open'],
 ['A03','rear tap','X0 Z4 fromY42 towards-Y','M4x0.7-6H usable20 min; drillD3.3 depth22+point1.0']]
with (ROOT/'features.csv').open('w',encoding='utf-8-sig',newline='') as f:
 w=csv.writer(f);w.writerow(['part','feature','location_mm','machining']);w.writerows(features)
# Same wood mounting pattern, self-contained DXF generator.
d=ezdxf.new('R2010');d.units=4;m=d.modelspace()
for layer,color in [('OUTLINE',7),('MOUNT_CENTER',1),('STRING_CENTER',3),('WIRE_OPTIONAL',5),('REFERENCE',4)]:d.layers.new(layer,dxfattribs={'color':color})
for x in (-28.5,-9.5,9.5,28.5):
 r=3;left=x-9;right=x+9
 for a,b in [((left+r,0),(right-r,0)),((right,r),(right,82-r)),((right-r,82),(left+r,82)),((left,82-r),(left,r))]:m.add_line(a,b,dxfattribs={'layer':'OUTLINE'})
 for center,angles in [((right-r,r),(270,360)),((right-r,82-r),(0,90)),((left+r,82-r),(90,180)),((left+r,r),(180,270))]:m.add_arc(center,r,*angles,dxfattribs={'layer':'OUTLINE'})
 m.add_line((x,-8),(x,90),dxfattribs={'layer':'STRING_CENTER'})
 for yy in (4,78):m.add_circle((x,yy),1.9,dxfattribs={'layer':'MOUNT_CENTER'})
 m.add_circle((x+7,20),1.5,dxfattribs={'layer':'WIRE_OPTIONAL'})
for yy in (14,26):m.add_line((-37.5,yy),(37.5,yy),dxfattribs={'layer':'REFERENCE'})
m.add_lwpolyline([(50,0),(100,0),(100,50),(50,50)],close=True,dxfattribs={'layer':'REFERENCE'})
m.add_text('CHECK 50 mm; PRINT 1:1; NEW HOLES',dxfattribs={'height':2.5,'insert':(50,55),'layer':'REFERENCE'})
m.add_text('FRONT DATUM Y=0; NUT DISTANCE: SCALE - 16 mm (INITIAL)',dxfattribs={'height':2.5,'insert':(-37.5,-18),'layer':'REFERENCE'})
d.saveas(ROOT/'MB4_mount_template_1to1.dxf')
print('9-page Rev D drawings, BOM, feature list, DXF complete')
