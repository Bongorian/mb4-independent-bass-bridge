"""Rev E shop drawings, mm. STEP authoritative for formed outlines."""
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
c.setTitle('MB4 Rev E - organic rear-fixing prototype'); PAGE=0
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
 text(12,8,'MB4 | Rev E | 2026-10-05 | mm | CNC見積・試作用',2.6);text(260,8,f'{PAGE} / 10',2.6)
def end():c.restoreState();c.showPage()

S=json.loads((ROOT/'cad/strength_comparison.json').read_text())
start('MB4 / Rev E 曲線・後方左右固定','後壁R9のアーチ、曲線リブ、丸みのあるアンカー。各弦独立、汎用金物、低弦高を維持。')
if (ROOT/'bridge_preview.png').exists():c.drawImage(str(ROOT/'bridge_preview.png'),12,37,width=165,height=134,mask='auto')
notes(186,168,['弦中心8〜20／前後調整12 mm','切削部品2点／弦、合計8点','後方M4×35全ねじ＋圧縮バネ','全幅75／弦間19／奥行90 mm','後壁最高25 mm（弦高とは別）','','後壁頂部：幅18、真円R9','リブ：二次曲線、露出縁R0.6','アンカー外形R3、前上縁R1.2','ベース平面R4、後上縁R0.6','','前1穴＋後2穴／弦、計12本','後方の座面は厚さ5へ増肉','後方左右穴は調整ねじから離す','裏面の個別ピエゾ用窪みを維持'],size=3,leading=7)
notes(14,29,['丸みは加工用STEPに反映。機能座面・タップ・ボール保持肩は必要な平面を残す。','Rev Dからベース奥行82→90。前穴もY4→5へ移動するため、取付テンプレートはRev Eを使用。'],size=3,leading=6);end()

start('B03 / 有機形状ベース・取付穴','4個 | A6061-T6 | 18×90×25 | 前側板厚3、固定タップ部6、後方木ねじ座面5')
s=1.35;y0=34
for xc,bottom,label in [(42,False,'上面'),(111,True,'裏面（同じ座標方向）')]:
 text(xc-17,169,label);rect(xc-9*s,y0,18*s,90*s,4*s);line((xc,y0-4),(xc,y0+90*s+4),True)
 for xx,yy in [(0,5),(-4.5,85),(4.5,85)]:circle(xc+xx*s,y0+yy*s,1.9*s);circle(xc+xx*s,y0+yy*s,3.5*s)
 for xx in (-6,6):
  circle(xc+xx*s,y0+46*s,1.25*s)
  if not bottom:rect(xc+(xx-3)*s,y0+43*s,6*s,6*s,1*s)
 if bottom:circle(xc,y0+20*s,6.25*s);rect(xc,y0+18.9*s,9*s,2.2*s)
 else:
  rect(xc-9*s,y0+67*s,18*s,6*s,.8*s)
  for xx in (-9,6):rect(xc+xx*s,y0+60.5*s,3*s,6.5*s);rect(xc+xx*s,y0+73*s,3*s,7*s)
  line((xc-9*s,y0+78*s),(xc+9*s,y0+78*s),True);line((xc-9*s,y0+80*s),(xc+9*s,y0+80*s),True)
 dh(xc-9*s,xc+9*s,y0-10,'18');dv(xc-9*s-8,y0,y0+90*s,'90')
notes(155,166,['基準：X=幅中心、Y=前端、Z=ボディ面。','前木ねじ：(0,5)、φ3.8貫通3。','後木ねじ：(±4.5,85)、φ3.8貫通5。','各穴：上面皿φ7、90°、深さ1.6。','前皿座底Z=1.4／後皿座底Z=3.4。','後方平面Z=5、Y=80〜90。','Y=78〜80はZ=3→5の滑らかな遷移。','','固定M3：(±6,46)、貫通6、下穴φ2.5。','パッド：6×6、中心(±6,46)、上端Z6。','裏面ピエゾ：(0,20)、φ12.5深さ1.5。','配線溝：X=0〜9、Y=18.9〜21.1、','裏面深さ1.2、右側面に開放。','','外形平面R4、前側上縁R0.5／下縁R0.2。','後方平面の外周上縁R0.6。STEPを併用。'],size=3,leading=7);end()

start('B03 / アーチ・曲線リブ・接続R','側面曲線は平面スケッチの押出し。3軸切削＋反転＋後端穴加工の範囲で仕上げる。')
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
notes(126,169,['後壁：幅18、Y=67〜73、厚6。','X=±9の肩Z=16、頂部Z=25。','頂部真円R9、円中心X=0/Z=16。','前後外周稜線R0.8、中央前根元R1。','','リブ幅3：X[-9,-6]、[6,9]。','前上辺：二次Bezier、制御点(Y,Z)','(60.5,3) → (63.75,3) → (67,16)。','後上辺：(80,5) → (76.5,5) → (73,16)。','底面Z=3、露出曲線の2縁R0.6。','','後方の板厚遷移：三次Bezier。','(78,3) → (78+2/3,3) →','(78+4/3,5) → (80,5)。','後壁長穴：中心X0/Z13、幅4.5、全長16.5。','後方M4軸Z=7〜19、座金φ8/4.3/t0.5。'],size=3,leading=7);end()

start('A04 / 丸みのあるアンカー','4個 | C3604 | 18×42×10、後尾高さ8 | 調整・保持寸法はRev Dを維持')
s=1.95;y0=66
for xc,bottom,label in [(38,False,'上面'),(99,True,'裏面（同じ座標方向）')]:
 text(xc-15,165,label);rect(xc-9*s,y0,18*s,42*s,3*s);line((xc-9*s,y0+22*s),(xc+9*s,y0+22*s),True)
 if bottom:
  for xx in (-6,6):rect(xc+(xx-3)*s,y0+22*s,6*s,20*s,1*s)
 else:rect(xc-1.7*s,y0,3.4*s,6*s);rect(xc-4*s,y0+6*s,8*s,16*s,1.5*s)
 for xx in (-6,6):
  for yy in (11,18):circle(xc+xx*s,y0+yy*s,1.25*s)
  rect(xc+(xx-1.7)*s,y0+24.3*s,3.4*s,15.4*s,1.7*s)
 dh(xc-9*s,xc+9*s,y0-8,'18')
dv(14,y0,y0+42*s,'42')
notes(143,167,['前部Y=0〜22、高さ10、前上縁R1.2。','後尾Y=20〜42、高さ8、上縁R0.2。','平面外形R3、下面外周R0.3。','固定ねじ座は平面を優先して小Rにする。','','裏面逃げ：中心(±6,32)、6×20、深さ3、R1。','後尾中央は下面Z0から残す。','ポケット：X=±4、Y=6〜22、底Z2、四隅R1.5。','保持肩Y6、弦スリット幅3.4／底Z3.3。','長い上縁R0.25。','','高さM3：(±6,11)、(±6,18)、貫通10。','固定長穴：(±6,32)、幅3.4、全長15.4貫通。','後尾M4×0.7-6H、軸X0/Z4、後端Y42。','有効20以上、φ3.3下穴深さ22＋先端1.0。'],size=2.95,leading=7)
rect(20,28,44,20);rect(64,28,40,16);line((64,36),(104,36),True)
text(112,43,'中央：後尾高さ8、タップ軸Z4',3);text(112,34,'固定座の裏面Z0〜3は逃げ加工',3)
text(14,19,'R寸法は個別STEPのソリッド形状に反映。穴・座面・肩の機能寸法は図面指示を優先。',3);end()
start('調整・弦装填・ネジ長さの選択','弦中心H=8＋g。g=0〜12。後尾の裏面逃げは、ベース増肉パッドを避けるための形状。')
notes(14,167,['高さ：M3平先×10（g=0〜6）、M3平先×16（g>6〜12）。ねじ掛かり4以上。','前後：アンカー前端q=8〜20、保持肩Y=q＋6=14〜26。調整幅12。','ばね作動長25−q=17〜5。後方M4ねじ1回転0.7 mm、締めて後へ引き、緩めて前へ押す。','後方M4×35は全ねじを指定。アンカー内ねじ掛かり11.5以上（有効上限19.5を想定）。','ボールはポケット中央Y=14付近から入れ、前肩Y=6まで滑らせる。φ6×厚4.75参考。','後方ねじの先端は最前進時でアンカー内Y=18.5、装填ボール後端Y=17と1.5離れる。','ベース固定後に組み付ける。後方左右穴は組立後もφ6ドライバーの進入域を確保。'],leading=7.5)
text(14,104,'固定ねじ2本／弦：M3全ねじ＋DIN433小径座金／スペーサ（外径6以下）',3.6)
for i,t in enumerate(['g (mm)','弦中心H','固定ねじL','座金合計t','先端Z']):text(20+49*i,91,t,3.1)
for j,g in enumerate((0,2,4,6,8,10,12)):
 L=next(v for v in (12,16,20,25) if v>=11+g);t=.5*math.ceil((L-11-g+.2)/.5-1e-8);tip=11+g+t-L
 for i,val in enumerate((g,8+g,L,t,tip)):text(20+49*i,82-6*j,str(val),3)
notes(14,28,['先端Z=11＋g＋t−Lを0.2〜0.7に調整。厚さ6のベース内ねじ掛かり5.3〜5.8。','gと金物厚を実測し、木部への突出を避ける。弦を緩めて調整し、最後に固定ねじ2本を締める。'],size=3,leading=7);end()

rows=[['B03','曲線ベース A6061-T6',4,'18×90×25、板3／固定6／後座5'],['A04','丸形アンカー C3604',4,'18×42×10、後尾8／裏逃げ3'],['H01','SUS M4×35 六角穴付 全ねじ',4,'A2-70等、頭φ7×4、六角3'],['H02','SUS DIN433 M4座金',4,'φ8/4.3/t0.5、後方用'],['H03','SUS圧縮ばね OD5/線径0.3/自由長20',4,'作動5〜17、内径4.4参考、密着3.15'],['H04','SUS M3平先止めねじ×10',16,'g=0〜6、高さ用、六角1.5'],['H05','SUS M3平先止めねじ×16',16,'g>6〜12への交換セット'],['H06','SUS M3全ねじ×12/16/20/25','8使用','gに応じて5ページから選択'],['H07','SUS DIN433 M3座金／スペーサ','8組','外径6以下、内径3.2、t0.5〜5.5'],['H08','SUS皿木ねじ3.5×20',12,'頭φ7以下、木部厚と下穴は実測'],['P01','ピエゾφ12以下＋接着・配線',4,'実装総厚1.2以下、各弦個別']]
start('部品表・切削・仕上げ','金物規格はRev Dを維持。木ねじは前4＋後8＝12本。小径座金はDIN433を指定。')
for i,t in enumerate(['ID','品名','4弦数量','仕様・選択条件']):text([14,32,159,181][i],168,t,3.2)
for j,row in enumerate(rows):
 for x,val in zip([14,32,159,181],row):text(x,157-8*j,str(val),2.65)
notes(14,60,['ばね参考：MBA CS-0500-0200-03-S4-C。内径4.4参考にM4を通す。作動長・実寸を確認。','一般寸法±0.10、機能穴・座標±0.05、外周小R±0.05。M3×0.5／M4×0.7-6H。','接触平面は平面度0.05、Ra3.2目安。残る穴口・溝縁はC0.1以下でバリ取り。','3軸切削＋反転＋後端穴加工。曲線リブ・各R・後方増肉を加工。パス増加による費用は見積確認。','タップ・接触面を保護して表面処理。工具アクセス・最小工具径・タップ出口を加工先で確認。','座金厚の公差は実測してネジ長を合わせる。高い位置での支持剛性・緩みは試作評価。'],size=3,leading=7);end()

start('取付テンプレート / 1:1','A4横・100%で印刷。50 mm枠を実測。Rev E専用の新規穴あけ用。前版の取付穴パターンとは異なる。')
x0=78;y0=58
for x in (-28.5,-9.5,9.5,28.5):
 rect(x0+x-9,y0,18,90,4);line((x0+x,y0-12),(x0+x,y0+90),True)
 for xx,yy in ((0,5),(-4.5,85),(4.5,85)):
  circle(x0+x+xx,y0+yy,1.9);line((x0+x+xx-2,y0+yy),(x0+x+xx+2,y0+yy));line((x0+x+xx,y0+yy-2),(x0+x+xx,y0+yy+2))
 circle(x0+x+7,y0+20,1.5)
for yy in (14,26):line((x0-37.5,y0+yy),(x0+37.5,y0+yy),True)
dh(x0-37.5,x0+37.5,y0-18,'全幅75');dh(x0-28.5,x0-9.5,y0+96,'19')
rect(210,36,50,50);dh(210,260,22,'チェック50 mm')
notes(152,169,['各弦：前(0,5)、後(±4.5,85)。','φ3.8は金属の通し穴径。','木部下穴は木材・ねじから選ぶ。','','配線落とし候補：X＋7、Y=20、φ3。','内部配線経路を確認して位置を決定。','','前端位置はナットから','スケール長−16を初期候補とする。','実弦の補正量を肩Y=14〜26で合わせ、','穴あけ前に取付位置を確定する。','既存5穴とは非互換、新規穴あけ用。'],size=3,leading=7)
text(14,27,'DXFも同じmm座標。弦間・ボディ端までの余白・既存穴との距離を実測して取付。',3);end()

start('ピエゾ・組立・試作評価','機構の独立と音響的な分離は別。ピエゾは各弦のベース裏面に接着する。')
notes(14,166,['ピエゾ：φ12以下、接着・配線を含む厚さ1.2以下。窪み深さ1.5で木部から0.3以上離す。','各素子を個別バッファで読み出す。共通木部を経由する機械的クロストークは残る。','必要な分離度と低域感度は1弦ずつ弾いて4ch録音で確認する。','','最初はB03/A04各1個。実弦のボール保持・装填・巻き部分の擦れ・弦軸高さを確認。','ベース固定後、アンカー・高さねじ・固定ねじ・ばね・後方M4を組み付ける。','g=0〜12の全域で、座金／スペーサ厚と固定ねじ先端の突出を確認する。','弦を緩める→固定ねじを緩める→高さ→オクターブ→固定ねじを締める。','弦を徐々に張り、後壁・ねじ・ボール・アンカーの移動と緩みを確認する。','弦張力は後方ねじが受ける。ばねは位置決め用であり、弦張力を支える要素ではない。','実物の強度・疲労・木ねじ保持力・音響は未検証。試験で締付条件と許容使用条件を決める。','φ6参考ボールで弦中心8＋gを設定。実弦のボール／巻き形状で実際の弦軸は変わり得る。','','後壁最大高さ25・最小弦高8を維持。ボディ端・既存穴・内部空洞を実測する。','切削部品数は2個／弦。リブとパッドはベースから一体で削り出す。'],size=3.1,leading=7)
notes(14,44,['参照：MBA Springs catalogue p.20／使用ばねの作動長・密着長・内径。','https://files.minibearings.au/pdf/catalogues/Springs.pdf','Accu DIN433 M3/M4座金・M4×35全ねじ、NBK JIS B1176ねじ頭寸法表。','型番例・参照URLは部品選定メモ hardware_sources.txt に記載。'],size=2.8,leading=6);end()

start('後方左右固定 / 採用理由と座面','後リブの後ろに固定穴を設け、中央のオクターブねじから工具進入域を離す。')
if (ROOT/'bridge_rear_preview.png').exists():c.drawImage(str(ROOT/'bridge_rear_preview.png'),12,37,width=165,height=134,mask='auto')
notes(184,169,['Rev D：後方中央1穴、Y78。','調整ねじ頭と工具進入域が近い。','','Rev E：後方左右2穴、Y85。','中心X=±4.5、左右間隔9。','リブ後端Y80より後ろに置く。','φ6ドライバーの縦進入を確認。','','後方平面厚5、皿座深さ1.6。','皿座底から下面まで3.4を確保。','前側は厚3、皿座底まで1.4。','','左右固定で基部の回転を抑える。','木部の保持力・締付条件は未評価。','ねじ追加による強度倍率は未算定。'],size=3,leading=7)
notes(14,29,['1弦：前1本＋後2本＝3本。4弦で12本。新規取付穴のため、既存穴・空洞・木部厚を確認。','3.5×20木ねじの埋込み目安は前17／後15 mm。実際の頭形状・先端・木部厚で下穴を決める。'],size=3,leading=6);end()

start('曲線リブの比較 / Rev D → Rev E','丸みを付けながら断面を確保。同じ仮荷重での公称断面応力比較。FEA・許容荷重評価ではありません。')
notes(14,168,['比較条件：水平350 N／弦（仮定）、g=12、弦中心20、ねじ軸19。固定端の片持ち梁モデル。','後壁＋リブのCAD断面をZ=3.6〜18.6、0.2刻みで切断。面積・重心・Ixxを取得。','M=350×(19−Z)、断面係数W=Ixx／最大外縁距離、公称曲げ応力σ=M／W。','固定パッド・Rev Eの後方増肉フランジを除外。後方2本固定の効果は数値評価していない。'],leading=7)
pd=S['peak_nominal_bending']['D'];pe=S['peak_nominal_bending']['E'];ratio=S['peak_stress_E_over_D']
cols=[16,143,193,243]
for x,t in zip(cols,['比較項目','Rev D','Rev E','変化']):text(x,127,t,3.5)
comparison=[['ベース奥行','82 mm','90 mm','＋8 mm'],['木ねじ本数／弦','2','3','後方左右に配置'],['後方座面厚／皿座底残り','3 / 1.4 mm','5 / 3.4 mm','＋2 mm'],['後壁 最大公称曲げ応力',f"{pd['nominal_bending_MPa']:.1f} MPa",f"{pe['nominal_bending_MPa']:.1f} MPa",f'{(1-ratio)*100:.1f}%低下'],['最大応力の断面Z',f"{pd['z']:.1f} mm",f"{pe['z']:.1f} mm",'ピーク位置が移動'],['最低弦中心高さ','8 mm','8 mm','維持']]
for j,row in enumerate(comparison):
 for x,t in zip(cols,row):text(x,115-9*j,t,2.9)
notes(14,54,['上記の割合は公称応力だけの比較。構造全体の耐荷重・疲労寿命・安全率を示すものではない。','局所応力集中、接触、ねじ締付け、疲労、基板変形、木部、実弦張力は計算に含まない。','350 Nは比較用仮定であり、実測張力・推奨張力・許容荷重ではない。実物試作で検証する。','再計算コード compare_sections.py、section_scan.csv、strength_comparison.json を収録。'],size=3,leading=7);end();c.save()
with (ROOT/'BOM.csv').open('w',encoding='utf-8-sig',newline='') as f:
 w=csv.writer(f);w.writerow(['ID','品名','4弦数量','仕様']);w.writerows(rows)
features=[
 ['B03','blank','18 x 90; plateZ0..3; max25','A6061-T6; planR4; front topR0.5 bottomR0.2'],
 ['B03','front mount','(0,5)','D3.8 THRU3; CSK D7 90deg depth1.6; remaining1.4'],
 ['B03','rear mounts','(+/-4.5,85)','D3.8 THRU5; CSK D7 90deg depth1.6; remaining3.4'],
 ['B03','rear flange','Y80..90 topZ5','outer top rimR0.6; cubic ramp Y78..80 Z3..5; see STEP'],
 ['B03','ramp Bezier control YZ','(78,3); (78+2/3,3); (78+4/3,5); (80,5)','cubic profile extruded width18'],
 ['B03','clamp pads','(+/-6,46)','6x6 topZ6; planR1 topR0.2; integral'],
 ['B03','clamp taps','(+/-6,46)','M3x0.5-6H THRU6; drillD2.5'],
 ['B03','piezo','(0,20)','bottom D12.5 depth1.5; remaining1.5'],
 ['B03','wire','X0..9 Y18.9..21.1','bottom depth1.2; side open'],
 ['B03','wall','Y67..73; shouldersZ16; apexZ25','XZ crownR9 center(0,16); front/back profileR0.8; front central rootR1'],
 ['B03','front ribs','X[-9,-6] and[6,9]','YZ quadratic Bezier (60.5,3),(63.75,3),(67,16); floorZ3; exposed curved edgesR0.6'],
 ['B03','rear ribs','X[-9,-6] and[6,9]','YZ quadratic Bezier (80,5),(76.5,5),(73,16); floorZ3; exposed curved edgesR0.6'],
 ['B03','rear slot','X0 Z13','width4.5 total16.5 THRU6; axesZ7..19'],
 ['B03','rear washer clearance','X+/-4.5 Y73..74','floorZ2'],
 ['A04','blank','18x42; frontY0..22 H10; tailY20..42 H8','C3604; planR3; front upperR1.2; lowerR0.3; tail upperR0.2'],
 ['A04','ball cradle','X+/-4 Y6..22','floorZ2; planR1.5; shoulderY6'],
 ['A04','string slot','X+/-1.7 Y0..22','floorZ3.3; long upper lipsR0.25'],
 ['A04','height taps','(+/-6,11),(+/-6,18)','M3x0.5-6H THRU10; drillD2.5'],
 ['A04','clamp slots','(+/-6,32)','width3.4 total15.4; clamp lane materialZ3..8'],
 ['A04','under relief','(+/-6,32)','6x20 depth3; planR1; sides open'],
 ['A04','rear tap','X0 Z4 fromY42 towards-Y','M4x0.7-6H usable20 min; drillD3.3 depth22+point1.0']]
with (ROOT/'features.csv').open('w',encoding='utf-8-sig',newline='') as f:
 w=csv.writer(f);w.writerow(['part','feature','location_mm','machining']);w.writerows(features)
d=ezdxf.new('R2010');d.units=4;m=d.modelspace()
for layer,color in [('OUTLINE',7),('MOUNT_CENTER',1),('STRING_CENTER',3),('WIRE_OPTIONAL',5),('REFERENCE',4)]:d.layers.new(layer,dxfattribs={'color':color})
for x in (-28.5,-9.5,9.5,28.5):
 r=4;left=x-9;right=x+9
 for a,b in [((left+r,0),(right-r,0)),((right,r),(right,90-r)),((right-r,90),(left+r,90)),((left,90-r),(left,r))]:m.add_line(a,b,dxfattribs={'layer':'OUTLINE'})
 for center,angles in [((right-r,r),(270,360)),((right-r,90-r),(0,90)),((left+r,90-r),(90,180)),((left+r,r),(180,270))]:m.add_arc(center,r,*angles,dxfattribs={'layer':'OUTLINE'})
 m.add_line((x,-8),(x,98),dxfattribs={'layer':'STRING_CENTER'})
 for xx,yy in ((0,5),(-4.5,85),(4.5,85)):m.add_circle((x+xx,yy),1.9,dxfattribs={'layer':'MOUNT_CENTER'})
 m.add_circle((x+7,20),1.5,dxfattribs={'layer':'WIRE_OPTIONAL'})
for yy in (14,26):m.add_line((-37.5,yy),(37.5,yy),dxfattribs={'layer':'REFERENCE'})
m.add_lwpolyline([(50,0),(100,0),(100,50),(50,50)],close=True,dxfattribs={'layer':'REFERENCE'})
m.add_text('CHECK 50 mm; PRINT 1:1; REV E NEW HOLES',dxfattribs={'height':2.5,'insert':(50,55),'layer':'REFERENCE'})
m.add_text('FRONT DATUM Y=0; NUT DISTANCE: SCALE - 16 mm (INITIAL)',dxfattribs={'height':2.5,'insert':(-37.5,-18),'layer':'REFERENCE'})
d.saveas(ROOT/'MB4_mount_template_1to1.dxf')
print('10-page Rev E drawings, BOM, feature list, DXF complete')
