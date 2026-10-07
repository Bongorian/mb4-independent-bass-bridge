"""Rev L: CAD-derived vector shop views of convex surfaces and protected seats."""
from pathlib import Path
import csv, json, math, io
import cadquery as cq
import inspect
_ns=dict(cq.exporters.getSVG.__globals__)
_source=inspect.getsource(cq.exporters.getSVG).replace("coordinate_system = gp_Ax2(gp_Pnt(), gp_Dir(*projectionDir))", "coordinate_system = gp_Ax2(gp_Pnt(), gp_Dir(*projectionDir), gp_Dir(*d[\"xDir\"]))")
exec(_source,_ns)
shop_svg=_ns['getSVG']
import ezdxf
from reportlab.pdfgen import canvas
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.cidfonts import UnicodeCIDFont
from reportlab.lib.units import mm
from reportlab.graphics import renderPDF
from svglib.svglib import svg2rlg
ROOT=Path(__file__).resolve().parent.parent
PDF=ROOT/'pdf';PDF.mkdir(exist_ok=True)
pdfmetrics.registerFont(UnicodeCIDFont('HeiseiKakuGo-W5'))
C=None;JP='HeiseiKakuGo-W5';FONT='Helvetica'
def txt(x,y,t,size=3.1,font=None):
 C.setFillColorRGB(.12,.19,.23);C.setFont(font or FONT,size);C.drawString(x,y,t)
def lines(x,y,rows,size=3.2,leading=6.5,font=None):
 for row in rows:txt(x,y,row,size,font);y-=leading

def ln(x1,y1,x2,y2,dash=False):
 C.setStrokeColorRGB(.19,.28,.34);C.setLineWidth(.22);C.setDash(1.5,1) if dash else C.setDash();C.line(x1,y1,x2,y2);C.setDash()
def rect(x,y,w,h,r=0):
 C.setStrokeColorRGB(.19,.28,.34);C.setLineWidth(.22)
 if r:C.roundRect(x,y,w,h,r)
 else:C.rect(x,y,w,h)
def dim(x1,x2,y,label):
 C.setFillColorRGB(.12,.19,.23)
 ln(x1,y,x2,y)
 for x in (x1,x2):ln(x-1,y-1,x+1,y+1)
 C.setFont(FONT,3);C.drawCentredString((x1+x2)/2,y+1.5,label)
def start(title,sub,page,total,A3=True):
 C.saveState();C.scale(mm,mm);w=420 if A3 else 297;h=297 if A3 else 210
 txt(13,h-16,title,5.2);txt(13,h-25,sub,3.2);ln(13,h-31,w-13,h-31)
 txt(13,8,'MB4 / REV L / 2026-10-07 / mm / PROTOTYPE - RFQ',2.7)
 txt(w-35,8,f'{page} / {total}',2.7)
def end():C.restoreState();C.showPage()
def view(part,projection,x,y,w,h,label):
 s=cq.importers.importStep(str(ROOT/'cad/step'/f'{part}.step')).val()
 nx,ny,nz=projection
 right=(1,0,0) if nx==ny==0 else (-ny,nx,0)
 is_iso=sum(v!=0 for v in projection)>1
 svg=shop_svg(s,{'xDir':right,'width':w*mm,'height':h*mm,'marginLeft':9,'marginTop':9,'projectionDir':projection,'showAxes':False,'showHidden':not is_iso,'strokeWidth':.18,'strokeColor':(30,48,58),'hiddenColor':(175,185,192)})
 drawing=svg2rlg(io.BytesIO(svg.encode()))
 x1,y1,x2,y2=drawing.getBounds();bw,bh=x2-x1,y2-y1;f=min((w-4)/bw,(h-4)/bh)
 C.saveState();C.translate(x+(w-bw*f)/2-x1*f,y+(h-bh*f)/2-y1*f);C.scale(f,f);renderPDF.draw(drawing,C,0,0);C.restoreState()
 txt(x,y+h+3,label,3.2)
def feature_table(x,y,rows,width=195):
 for label,value in rows:
  txt(x,y,label,3.15);txt(x+51,y,value,3.15);ln(x,y-2,x+width,y-2);y-=7
 return y

C=canvas.Canvas(str(PDF/'B10_streamlined_base.pdf'),pagesize=(420*mm,297*mm));C.setTitle('MB4 Rev L B10 base - 6061-T6 - 4 required')
start('B10 / STREAMLINED ARCH BASE','QTY 4 | ALUMINUM 6061-T6 | 18 x 86 x 25 | STEP: B10_streamlined_base.step',1,2)
view('B10_streamlined_base',(0,0,1),18,65,80,178,'TOP (+Z)')
view('B10_streamlined_base',(0,0,-1),106,65,80,178,'BOTTOM (-Z; mirrored Y on screen)')
view('B10_streamlined_base',(0,-1,0),22,21,160,35,'FRONT (-Y)')
y=feature_table(204,251,[('DATUM','X=width centre; Y=front; Z=bottom'),('Envelope','W18; L86; max height25'),('Main plate','Z0..3; planR4; free front upper rimR0.8'),('Front mount','X0 / Y8; D3.8 THRU3'),('Rear mount','X0 / Y81; D3.8 THRU3 at recessed seat'),('Both countersinks','D7 x 90 deg; axial depth1.6'),('CSK floor left','Front1.4; rear1.4'),('Rear head recess','D7.4; depth2 fromZ5 toZ3'),('Rear clearance tray','W8 x L8; centreY80.5; floorZ3; R1.5'),('Clamp threads','2x M3 x 0.5 - 6H THRU6'),('Clamp coordinates','X +/-6; Y36; tap drill D2.5'),('Integral clamp pads','6 x 6; topZ6; rootZ2 into plate; R1.5/topR0.4'),('Piezo pocket','Bottom: X0/Y24; D12.5; depth1.5'),('Wire exit','X0..9; Y22.9..25.1; depth1.2'),('Wall position','Y70.5..76.5; depth6; single R9 arch'),('Wall slot','X0/Z13; W4.5; totalL16.5 THRU6'),('Washer recess','X +/-4.5; Y76.5..77.5; floorZ2, open toZ5')])
lines(204,y-7,['Threads are pilot-diameter representations in STEP.','Make M3 threads; do not leave them as plain D2.5 bores.','Hole and thread axis locations: +/-0.05 mm.','D3.8 clearance / slotW4.5: +/-0.05 mm.','Other dimensions: ISO 2768-m; geometry from STEP.','Flatness of body seat: 0.05 mm. Ra3.2 target.'],size=3.1,leading=6)
end()
start('B10 / SINGLE ARCH AND SWEPT WEBS','Top/bottom/end plus 3D finishing setups. STEP governs convex surfaces; protected planar seats must remain flat.',2,2)
view('B10_streamlined_base',(-1,0,0),15,151,184,68,'LEFT (-X)')
view('B10_streamlined_base',(1,0,0),15,61,184,68,'RIGHT (+X)')
view('B10_streamlined_base',(1,-1,1),210,105,187,121,'ISOMETRIC (illustration; not dimensioned)')
lines(210,255,['One R9 arch centred X0/Z16; apexZ25.','Wall thickness6; exposed arch rimR1.2.','No separate raised washer/spring bosses.','Flat front/rear faces support spring/washer.'],leading=7)
lines(18,45,['Internal wall/floor roots may be eased R0.2 MAX; preserve spring envelope.','Do not enlarge the slot/recess or remove integral ribs without approval.','Remaining cosmetic edges: C0.2 MAX. Thread mouths and countersink seats: C0.1 MAX.'],leading=7)
lines(210,90,['Rear flange: Y76..86, topZ5; free rear end/corners R0.9.','Smooth ramp: Y74..76, Z3..5; profile from STEP.','Ribs width3: X[-9,-6] and X[6,9].','Front swept web: Y64/Z3 to Y72.5/Z16; tip2 into wall.','Rear swept web: Y74.5/Z16 to Y81.5/Z5; tip2 into wall.','Web rootsR2; outerR0.8; innerC0.2 MAX.','Cubic profiles/ramp from STEP; do not replace by triangles.','Aluminum threads: gauge M3 x 0.5 - 6H.'],size=3.1,leading=7)
end();C.save()

C=canvas.Canvas(str(PDF/'A10_sculpted_ball_anchor.pdf'),pagesize=(420*mm,297*mm));C.setTitle('MB4 Rev L A10 anchor - 6061-T6 - 4 required')
start('A10 / REFINED BALL-END ANCHOR','QTY 4 | ALUMINUM 6061-T6 | 18 x 55 x max10.5 | STEP: A10_sculpted_ball_anchor.step',1,2)
view('A10_sculpted_ball_anchor',(0,0,1),18,90,80,152,'TOP (+Z)')
view('A10_sculpted_ball_anchor',(0,0,-1),108,90,80,152,'BOTTOM (-Z; mirrored Y on screen)')
view('A10_sculpted_ball_anchor',(-1,0,0),18,22,170,43,'LEFT (-X)')
y=feature_table(203,251,[('DATUM','X=width centre; Y=front; Z=bottom'),('Envelope','W18; L55; max10.5; seat datumZ8'),('Outside shape','NoseR7; rear plan cornersR3; see STEP'),('Front roof','Parabolic XZ: sideZ7.8; apexZ10.5'),('Roof rim / bottom','Upper rimR0.7; lower rimR0.6'),('Ball cradle','W8.2; Y6..15; frontR1.1 / rearR4.1'),('Cradle mouth / floor','True top rimR0.6; floorZ2'),('Load shoulder','Y6; flat frontW6, split by string channel'),('String channel','Front only: W3.4; Y-2..8; floorZ3.3'),('Flow ramp / rear deck','Tangent Bezier rampY21..27.8 to deckZ8'),('Height threads','4x M4 x 0.7 - 6H THRU8'),('Height coordinates','X +/-5.5; Y19 and Y24'),('Height entry wells','D4.2 from convex roof to floorZ8'),('Clamp slots','X +/-6 / Y41; W3.4 x totalL23.4'),('Side underside relief','X +/-6 / Y41.5; 6 x 27; depth3; R1.5'),('Central underside window','X0/Y36; 4.4 x 22; depth6.3; R1.5')])
lines(203,y-7,['Rear M4 thread: see sheet2 (short tap to open window).','Height thread axes / slot width: +/-0.05 mm.','Other dimensions: ISO 2768-m; geometry from STEP.','Thread mouths / ball shoulders / string contact: C0.1 MAX.','Other edges C0.2 MAX. Curved surfaces: Ra3.2 target.'],size=3.1,leading=6)
end()
start('A10 / REAR TAP AND OPEN SCREW WINDOW','M4 x 0.7 - 6H; enter at Y55 in -Y direction. Axis X0/Z4. Tap through into the open underside window.',2,2)
view('A10_sculpted_ball_anchor',(0,1,0),18,181,165,53,'REAR (+Y): axial M4 tap / pilotD3.3')
view('A10_sculpted_ball_anchor',(1,1,-1),210,150,183,95,'UNDERSIDE ISOMETRIC')
# Centre section at X=0, drawn to scale for the rear mechanism.
s=3.5;ox=18;oz=105
rect(ox,oz,55*s,8*s)
C.setFillColorRGB(1,1,1);C.setStrokeColorRGB(.19,.28,.34);C.rect(ox+25*s,oz,22*s,6.3*s,fill=1,stroke=1)
C.rect(ox+47*s,oz+2.35*s,8*s,3.3*s,fill=1,stroke=1)
# Draw only rear half, mask front-half which has complex crown/cradle section.
C.setFillColorRGB(1,1,1);C.rect(ox-1,oz-1,27.8*s+1,8*s+2,fill=1,stroke=0)
ln(ox+25*s,oz+4*s,ox+58*s,oz+4*s,True)
dim(ox+25*s,ox+47*s,oz-9,'OPEN WINDOW Y25..47 (22)')
dim(ox+47*s,ox+55*s,oz+8*s+8,'FULL THREAD LAND: 8 MIN')
txt(18,160,'CENTRE SECTION X=0 - Y27.8..55 FLAT ROOF (front ramp omitted)',3.1)
lines(18,74,['1. Drill D3.3 from Y55 to Y43 (12), fully breaking into open window.','2. Tap M4 x 0.7 - 6H through to the window, including partial outlet walls.','3. Require full circumferential thread over Y47..55: 8 mm MIN.','4. Deburr outlet from underside; do not leave an undersized untapped outlet.','5. No blind-hole tip allowance is needed; the outlet is open.'],size=3.15,leading=7)
lines(229,125,['Central window roofZ6.3; rear deckZ8 (top1.7).','M4 screw major radius2: topZ6, roof clearance0.3.','WindowW4.4: nominal side clearance0.2 each.','Full thread land is outside the window.','Nominal window-to-height-tap bulk:1.5.','','Capsule cradle; trueR0.6 mouth; no redundant rear slit.','Rear height taps remain forward of side reliefY28.','An extra cross pin / retaining ring is not required.','','Tap depth12 = 3 x M4 nominal diameter.','Confirm outlet tapping and tool access at quotation.'],size=3.2,leading=7)
end();C.save()

# Japanese assembly guide and a dimension-consistent travel schematic.
FONT=JP
C=canvas.Canvas(str(PDF/'MB4_RevL_guide.pdf'),pagesize=(297*mm,210*mm));C.setTitle('MB4 Rev L - 20 mm continuous intonation travel')
start('MB4 / Rev L - ボールエンド保持部','半円の奥と丸い入口を持つ保持座。後部の不要な溝をなくし、20 mm調整・最低8 mmを維持。',1,4,False)
if (ROOT/'bridge_preview.png').exists():C.drawImage(str(ROOT/'bridge_preview.png'),13,38,165,134,mask='auto')
lines(184,165,['材質：6061-T6／両部品','ベース：18×86×25 mm','アンカー：18×55×最高10.5 mm','全幅：75 mm（弦間19）','','連続調整：20 mm','アンカー前端q：-15〜5','参考弦中心：8〜20 mm','木ねじ：前1＋後1／弦','','調整ボルト：M4×45 全ねじ','ばね：ミスミUY6-35','高さ調整：M4平先4本／弦','固定：低いM3ボタン頭2本','保持肩Y6・底Z2を維持'],size=3,leading=6.7)
lines(13,27,['最前位置ではアンカーがベース前端より15 mm張り出す。最前位置のモジュール全長は101 mm。','ベースを先にボディへ固定。球端・弦・ばね・ピエゾは参考外形。実機適合・耐久性は未検証。'],size=3,leading=6);end()
start('20 mmの可動域 / 機構と成立条件','qはベース前端Y0から見たアンカー前端。固定M3を緩め、後方M4を回して連続調整する。',2,4,False)
lines(13,167,['アンカー長穴：幅3.4、全長23.4。M3軸中心の移動は20 mm、端部に片側0.2 mm余裕。','固定パッドX±6/Y36、高さねじX±5.5/Y19・24。高さ穴の入口φ4.2、床Z8。','後壁Y70.5〜76.5は単純なR9アーチ。前後縁R1.2、リブは一続きの曲線。追加の座ボスはない。','短い後方タップ：全周ねじY47〜55の8 mm、裏開放窓Y25〜47につながる。','M4×45は全ねじ品を使用。半ねじSCB4-45では非ねじ部がアンカーへ入り、成立しない。'],size=3.05,leading=7)
# Side schematic, shared mm scale. Cosmetic fillets omitted explicitly.
def travel_row(q,y):
 sc=1.9; ox=48; oz=y
 def X(v):return ox+sc*v
 def Z(v):return oz+sc*v
 rect(X(0),Z(0),86*sc,3*sc)
 rect(X(70.5),Z(3),6*sc,22*sc)
 rect(X(q),Z(5),55*sc,10.5*sc)
 for yy in (19,24):ln(X(q+yy),Z(3),X(q+yy),Z(8))
 ln(X(32),Z(9),X(77),Z(9));rect(X(77),Z(5.5),4*sc,7*sc)
 # Compression spring envelope is shown by a zigzag, not a production spring model.
 a,b=q+55,70.5
 pts=[(X(a+(b-a)*i/18),Z(9+(1.5 if i%2 else -1.5))) for i in range(19)]
 for p1,p2 in zip(pts,pts[1:]):ln(*p1,*p2)
 ln(X(q+6),Z(0)-5,X(q+6),Z(15)+4,True)
 txt(13,Z(20),f'q = {q}',3.2)
 txt(X(q+6)-6,Z(15)+6,'弦の肩',2.8)
 txt(13,Z(0)-9,f'ばね作動長 {15.5-q:g} mm / 前側張り出し {max(0,-q):g} mm',3.0)
travel_row(-15,80);travel_row(5,23)
lines(230,111,['側面模式図','同倍率・寸法関係は','CADと一致。','','丸みや金物の細部は','省略しています。','',' qの差：20 mm','肩の位置も20 mm移動。'],size=2.8,leading=6)
end()
start('汎用金物 / 公差と高さ調整','価格と在庫は注文時に確認。ミスミ参照URLとメーカー仕様を同梱。',3,4,False)
lines(13,167,['前後：NBK SNSS-M4-45-FT（ミスミSNSS-M4X45-FT）。SUSXM7、全ねじM4×45、頭φ7×4。','ばね：UY6-35。SUS304-WPB、外径6、線径0.4、自由長35±1.5、ばね定数0.098 N/mm。','許容たわみ26.25、密着長参考6.8。作動長10.5〜30.5、最大公差時のたわみ26.0で範囲内。','最長の作動長30.5でも、短い個体の自由長33.5に対し3 mmの予圧が残る。','高さ：MSSFS4-8 / 12 / 16（平先、六角2）。固定：SSBCB3-12 / 16 / 20、25のみSBCB3-25。','座金：M3は外径6・厚0.5を積層。後方M4は外径8・厚0.5。木ねじは皿3.5×20候補。'],size=3.0,leading=7)
for x,t in zip([14,54,94,144,194,245],['隙間g','参考弦中心','高さM4長さ','固定M3長さ','座金合計厚','先端Z']):txt(x,113,t,3.1)
for i,g in enumerate([0,2,4,6,8,10,12]):
 L=next(v for v in [12,16,20,25] if v>=11+g);t=.5*math.ceil((L-11-g+.2)/.5-1e-8);tip=11+g+t-L
 for x,v in zip([14,54,94,144,194,245],[g,8+g,8 if g<=4 else 12 if g<=8 else 16,L,t,round(tip,2)]):txt(x,102-6.5*i,str(v),3.1)
lines(13,44,['ベース固定を先に行う。後木ねじの皿頭座はZ3、逃げトレーは深さ2の上面開放加工。','組立後の後木ねじへの工具は調整ボルトと重なる。脱着時は先にアンカー・調整ボルトを外す。','CAD確認：全9端・中間条件で金物／部品／ばね包絡が干渉しない。4本の高さねじは全接地。','M4周囲の0.8 mm材料ガード、M3実下穴、STEP再読込を検証。荷重・疲労は実機で確認。'],size=2.95,leading=7)
end()
start('取付テンプレート / 1:1','100%印刷し、50 mm枠を実測。木ねじ穴とピエゾ位置はRev Hと共通。既存Jazz/Pの穴への互換は未確認。',4,4,False)
x0=72;y0=42
for x in (-28.5,-9.5,9.5,28.5):
 rect(x0+x-9,y0,18,86,4);ln(x0+x,y0-18,x0+x,y0+90,True)
 for yy in [8,81]:
  C.circle(x0+x,y0+yy,1.9);ln(x0+x-2,y0+yy,x0+x+2,y0+yy);ln(x0+x,y0+yy-2,x0+x,y0+yy+2)
for yy in [-9,11]:ln(x0-37.5,y0+yy,x0+37.5,y0+yy,True)
dim(x0-37.5,x0+37.5,y0-19,'75');rect(218,39,50,50);dim(218,268,27,'50 mm')
lines(142,167,['取付穴：X=弦中心、Y8とY81。','前後の穴間距離73。通しφ3.8。','前後の皿座φ7/90°、頭座Z3。','後方はφ7.4深さ2の逃げを追加。','','ピエゾ裏窪み：X0/Y24、φ12.5。','φ12以下、接着・配線込み厚1.2以下。','木部へ挟み込まず金属裏へ接着。','','弦の肩：Y=q＋6、範囲Y-9〜11。','補正0〜20 mmに置く場合の目安：','ベース前端＝スケール長＋9 mm。','これは球端参考モデルからの位置。','実際の弦・ネックで取付位置を確定。','','JLC：B10とA10を別々に各4個。','6061-T6／Threads=YES／As-machined。','STEP＋同名PDFで手動見積審査。'],size=3,leading=6.8)
lines(13,17,['ボディ穴の位置・下穴径・深さは木材と実物ねじで決定。受託可否・価格・実機適合・強度は未確定。'],size=2.95)
end();C.save()

# Small procurement / feature tables, independent of PDF drawing geometry.
rows=[['B10','Streamlined arch base 6061-T6',4,'18x86x25; STEP + matching PDF'],['A10','Refined ball-end anchor 6061-T6',4,'18x55x10.5; STEP + matching PDF'],['H01','SNSS-M4X45-FT',4,'M4x45; FULL THREAD required; capheadD7/H4'],['H02','WSJS-SUS-M4',4,'OD8/ID4.5/t0.5'],['H03','UY6-35',4,'SUS304-WPB; OD6/wire0.4/L35+/-1.5/k0.098/solid6.8/deflection26.25'],['H04','MSSFS4-8/12/16',16,'4/string; length by g; flat end'],['H05','SSBCB3-12/16/20 or SBCB3-25',8,'2/string; buttonheadD5.7/H1.65; 2mm hex; length by g'],['H06','WSJS-SUS-M3','height dependent','OD6/ID3.3/t0.5; stack by g; OD6 maximum'],['H07','270011003520',8,'SUS flathead wood screw3.5x20; verify headD<=7/90deg'],['P01','Piezo reference envelope',4,'OD<=12; total mounted thickness<=1.2; individual channels']]
with (ROOT/'BOM.csv').open('w',newline='',encoding='utf-8-sig') as f:
 w=csv.writer(f);w.writerow(['ID','item','quantity_for_4_strings','specification']);w.writerows(rows)
features=[['A10','Ball cradle','X0; Y6..15; floorZ2','W8.2; flat frontW6 atY6; frontR1.1; rearR4.1 centredY10.9; true roof-mouthR0.6'],['A10','Front string channel','X0; Y-2..8; floorZ3.3','W3.4; overlaps cradle; no rear slit; contact lipsC0.1 MAX'],['B10','Mounts','X0/Y8 and X0/Y81','D3.8 THRU; CSK D7/90 depth1.6 atZ3; rear top-open D7.4 depth2 and8x8 trayfloorZ3'],['B10','Clamps','X+/-6/Y36','M3x0.5-6H THRU6; pilot2.5'],['B10','Piezo','X0/Y24','Bottom D12.5 depth1.5; wireW2.2 depth1.2'],['B10','Wall','Y70.5..76.5','Single R9 arch, thickness6; exposed arch rimR1.2; wall/web vertical rootsR2; no raised bosses'],['B10','Ribs','X[-9,-6] and[6,9]','Width3, single swept cubic front rawY64..72.5/rear rawY74.5..81.5; tips lap2 into wall; outerR0.8, inner C0.2 MAX unmodelled; see STEP for exact curves'],['A10','Height','X+/-5.5/Y19 and Y24','M4x0.7-6H fromZ8 toZ0; pilot3.3; top accessD4.2 toZ8; isolated mouth with floor radial guard0.5'],['A10','Rear thread','X0/Z4 fromY55 towards-Y','M4x0.7-6H THRU to underside window; pilot3.3 path12; full land8minY47..55; tap all outlet walls'],['A10','Central window','X0/Y36','W4.4/L22/depth6.3/R1.5'],['A10','Side relief','X+/-6/Y41.5','6x27/depth3/R1.5'],['A10','Clamps','X+/-6/Y41','SlotW3.4/totalL23.4'],['A10','Convex roof','Front Z7.8+2.7*(1-(X/9)^2); Y0..21','Single Bezier roof, front parabolic XZ, smooth tangent rampY21..27.8 to rear deckZ8; rimR0.7 bottomR0.6; no raised spine or waist; STEP governs']]
with (ROOT/'features.csv').open('w',newline='',encoding='utf-8-sig') as f:
 w=csv.writer(f);w.writerow(['part','feature','coordinates_mm','machining']);w.writerows(features)
d=ezdxf.new('R2010');d.units=4;m=d.modelspace()
for layer,color in [('OUTLINE',7),('MOUNT_CENTER',1),('STRING_CENTER',3),('REFERENCE',4)]:d.layers.new(layer,dxfattribs={'color':color})
for x in (-28.5,-9.5,9.5,28.5):
 left,right,r=x-9,x+9,4
 for a,b in [((left+r,0),(right-r,0)),((right,r),(right,82)),((right-r,86),(left+r,86)),((left,82),(left,r))]:m.add_line(a,b,dxfattribs={'layer':'OUTLINE'})
 for centre,angles in [((right-r,r),(270,360)),((right-r,82),(0,90)),((left+r,82),(90,180)),((left+r,r),(180,270))]:m.add_arc(centre,r,*angles,dxfattribs={'layer':'OUTLINE'})
 m.add_line((x,-5),(x,91),dxfattribs={'layer':'STRING_CENTER'})
 for yy in (8,81):m.add_circle((x,yy),1.9,dxfattribs={'layer':'MOUNT_CENTER'})
for yy in (-9,11):m.add_line((-37.5,yy),(37.5,yy),dxfattribs={'layer':'REFERENCE'})
m.add_lwpolyline([(50,0),(100,0),(100,50),(50,50)],close=True,dxfattribs={'layer':'REFERENCE'})
m.add_text('REV L / CHECK50mm / 1:1 / NEW HOLES',dxfattribs={'height':2.5,'insert':(50,55),'layer':'REFERENCE'})
d.saveas(ROOT/'MB4_mount_template_1to1.dxf')
print('Rev L: 3 matching PDFs / BOM / features / 1:1 DXF created')
