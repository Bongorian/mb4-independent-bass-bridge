"""Rev G: CAD-derived vector shop views and prototype/ordering guide."""
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
 txt(13,8,'MB4 / REV G / 2026-10-05 / mm / PROTOTYPE - RFQ',2.7)
 txt(w-35,8,f'{page} / {total}',2.7)
def end():C.restoreState();C.showPage()
def view(part,projection,x,y,w,h,label):
 s=cq.importers.importStep(str(ROOT/'cad/step'/f'{part}.step')).val()
 nx,ny,nz=projection
 right=(1,0,0) if nx==ny==0 else (-ny,nx,0)
 svg=shop_svg(s,{'xDir':right,'width':w*mm,'height':h*mm,'marginLeft':9,'marginTop':9,'projectionDir':projection,'showAxes':False,'showHidden':True,'strokeWidth':.18,'strokeColor':(30,48,58),'hiddenColor':(175,185,192)})
 drawing=svg2rlg(io.BytesIO(svg.encode()))
 x1,y1,x2,y2=drawing.getBounds();bw,bh=x2-x1,y2-y1;f=min((w-4)/bw,(h-4)/bh)
 C.saveState();C.translate(x+(w-bw*f)/2-x1*f,y+(h-bh*f)/2-y1*f);C.scale(f,f);renderPDF.draw(drawing,C,0,0);C.restoreState()
 txt(x,y+h+3,label,3.2)
def feature_table(x,y,rows,width=195):
 for label,value in rows:
  txt(x,y,label,3.15);txt(x+51,y,value,3.15);ln(x,y-2,x+width,y-2);y-=8
 return y

C=canvas.Canvas(str(PDF/'B05_smooth_base.pdf'),pagesize=(420*mm,297*mm));C.setTitle('MB4 Rev G B05 base - 6061-T6 - 4 required')
start('B05 / SMOOTH BASE','QTY 4 | ALUMINUM 6061-T6 | 18 x 98 x 25 | STEP: B05_smooth_base.step',1,2)
view('B05_smooth_base',(0,0,1),18,65,80,178,'TOP (+Z)')
view('B05_smooth_base',(0,0,-1),106,65,80,178,'BOTTOM (-Z; mirrored Y on screen)')
view('B05_smooth_base',(0,-1,0),22,21,160,35,'FRONT (-Y)')
y=feature_table(204,251,[('DATUM','X=width centre; Y=front; Z=bottom'),('Envelope','W18; L98; max height25'),('Main plate','Z0..3; plan corners R4'),('Front mount','X0 / Y5; D3.8 THRU3'),('Rear mount','X0 / Y93; D3.8 THRU5'),('Both countersinks','D7 x 90 deg; axial depth1.6'),('CSK floor left','Front1.4; rear3.4'),('Clamp threads','2x M3 x 0.5 - 6H THRU6'),('Clamp coordinates','X +/-6; Y54; tap drill D2.5'),('Integral clamp pads','6 x 6; Z3..6; plan R1.5; topR0.4'),('Piezo pocket','Bottom: X0/Y20; D12.5; depth1.5'),('Wire exit','X0..9; Y18.9..21.1; depth1.2'),('Wall position','Y75..81; thickness6'),('Wall slot','X0/Z13; W4.5; totalL16.5 THRU6'),('Washer recess','X +/-4.5; Y81..82; bottomZ2')])
lines(204,y-7,['Threads are pilot-diameter representations in STEP.','Make M3 threads; do not leave them as plain D2.5 bores.','Hole and thread axis locations: +/-0.05 mm.','D3.8 clearance / slotW4.5: +/-0.05 mm.','Other dimensions: ISO 2768-m; geometry from STEP.','Flatness of body seat: 0.05 mm. Ra3.2 target.'],size=3.1,leading=6)
end()
start('B05 / CURVED RIBS AND MACHINING ACCESS','Top, bottom and end setups. No enclosed undercuts. Formed curves and fillets are defined by STEP.',2,2)
view('B05_smooth_base',(-1,0,0),15,151,184,68,'LEFT (-X)')
view('B05_smooth_base',(1,0,0),15,61,184,68,'RIGHT (+X)')
view('B05_smooth_base',(1,-1,1),210,105,187,121,'ISOMETRIC (illustration; not dimensioned)')
lines(210,255,['Wall arch: true R9, centre X0/Z16; apexZ25.','Front and rear wall outside profile edges: R1.4.','Wall/rib vertical inside corners: R2.0.','Outside curved rib rims: R0.8.'],leading=7)
lines(18,45,['Internal wall/floor roots may be eased R0.2 MAX; preserve spring envelope.','Do not enlarge the slot/recess or remove integral ribs without approval.','Remaining cosmetic edges: C0.2 MAX. Thread mouths and countersink seats: C0.1 MAX.'],leading=7)
lines(210,90,['Rear flange: Y88..98, topZ5; outside upper rim R0.9.','Smooth ramp: Y86..88, Z3..5; profile from STEP.','Ribs width3: X[-9,-6] and X[6,9].','Front rib curve: (Y,Z) (68.5,3),(71.75,3),(75,16).','Rear rib curve: (88,5),(84.5,5),(81,16).','Both are quadratic Bezier profiles.','As-machined finish; no polishing of functional seats.','Aluminum threads: gauge M3 x 0.5 - 6H.'],size=3.1,leading=7)
end();C.save()

C=canvas.Canvas(str(PDF/'A06_smooth_anchor.pdf'),pagesize=(420*mm,297*mm));C.setTitle('MB4 Rev G A06 anchor - 6061-T6 - 4 required')
start('A06 / SMOOTH CROWN ANCHOR','QTY 4 | ALUMINUM 6061-T6 | 18 x 50 x max10 | STEP: A06_smooth_anchor.step',1,2)
view('A06_smooth_anchor',(0,0,1),18,90,80,152,'TOP (+Z)')
view('A06_smooth_anchor',(0,0,-1),108,90,80,152,'BOTTOM (-Z; mirrored Y on screen)')
view('A06_smooth_anchor',(-1,0,0),18,22,170,43,'LEFT (-X)')
y=feature_table(203,251,[('DATUM','X=width centre; Y=front; Z=bottom'),('Envelope','W18; L50; body8; crown max10'),('Outside shape','NoseR7; rear plan cornersR3; see STEP'),('Body edge fillets','UpperR0.8; lowerR0.4'),('Integral crown','X0/Y9; D12; topR1.0; rootR0.8'),('Ball cradle','W8 x L11; centreX0/Y11.5'),('Cradle floor','Z2; plan cornersR1.5'),('String slot','W3.4; floorZ3.3; round rear end'),('Crown slot lips','R0.4'),('Height threads','4x M4 x 0.7 - 6H THRU8'),('Height coordinates','X +/-5.25; Y20 and Y27'),('Height tap drill','D3.3 THRU8'),('Clamp slots','X +/-6 / Y40; W3.4 x totalL15.4'),('Side underside relief','X +/-6 / Y40; 6 x 20; depth3; R1.5'),('Central underside window','X0/Y32.5; 4.4 x 15; depth6.3; R1.5')])
lines(203,y-7,['Rear M4 thread: see sheet2 (short tap to open window).','Height thread axes / slot width: +/-0.05 mm.','Other dimensions: ISO 2768-m; geometry from STEP.','Thread mouths / ball shoulders / string contact: C0.1 MAX.','Other remaining edges: C0.2 MAX. Ra3.2 target.'],size=3.1,leading=6)
end()
start('A06 / REAR TAP AND OPEN SCREW WINDOW','M4 x 0.7 - 6H; enter at Y50 in -Y direction. Axis X0/Z4. Tap through into the open underside window.',2,2)
view('A06_smooth_anchor',(0,1,0),18,181,165,53,'REAR (+Y): axial M4 tap / pilotD3.3')
view('A06_smooth_anchor',(1,1,-1),210,150,183,95,'UNDERSIDE ISOMETRIC')
# Centre section at X=0, drawn to scale for the rear mechanism.
s=4;ox=18;oz=105
rect(ox,oz,50*s,8*s)
C.setFillColorRGB(1,1,1);C.setStrokeColorRGB(.19,.28,.34);C.rect(ox+25*s,oz,15*s,6.3*s,fill=1,stroke=1)
C.rect(ox+40*s,oz+2.35*s,10*s,3.3*s,fill=1,stroke=1)
# Draw only rear half, mask front-half which has complex crown/cradle section.
C.setFillColorRGB(1,1,1);C.rect(ox-1,oz-1,25*s+1,8*s+2,fill=1,stroke=0)
ln(ox+25*s,oz+4*s,ox+53*s,oz+4*s,True)
dim(ox+25*s,ox+40*s,oz-9,'OPEN WINDOW Y25..40 (15)')
dim(ox+42*s,ox+50*s,oz+8*s+8,'FULL THREAD LAND: 8 MIN')
txt(18,160,'CENTRE SECTION X=0 - REAR HALF ONLY (pilot-diameter profile)',3.1)
lines(18,74,['1. Drill D3.3 from Y50 to Y38 (12), fully breaking into open window.','2. Tap M4 x 0.7 - 6H through to the window, including partial outlet walls.','3. Require full circumferential thread over Y42..50: 8 mm MIN.','4. Deburr outlet from underside; do not leave an undersized untapped outlet.','5. No blind-hole tip allowance is needed; the outlet is open.'],size=3.15,leading=7)
lines(229,125,['Central window: roofZ6.3, remaining top1.7.','M4 screw major radius2: topZ6, roof clearance0.3.','WindowW4.4: nominal side clearance0.2 each.','Full thread land is outside the window.','Nominal minimum bulk web to height tap:1.05.','','Front screws no longer break into the ball cradle.','Rear height taps remain forward of side reliefY30.','An extra cross pin / retaining ring is not required.','','Tap depth12 = 3 x M4 nominal diameter.','Confirm outlet tapping and tool access at quotation.'],size=3.2,leading=7)
end();C.save()

# Japanese assembly / quotation guide (not uploaded to JLC).
FONT=JP
C=canvas.Canvas(str(PDF/'MB4_RevG_guide.pdf'),pagesize=(297*mm,210*mm));C.setTitle('MB4 Rev G - smooth aluminum prototype guide')
start('MB4 / Rev G 滑らかなアルミブリッジ','外観の丸みと加工確認の修正を一つの版へ。弦間19 mm、各弦独立、4弦でCNC部品8点。',1,4,False)
if (ROOT/'bridge_preview.png').exists():C.drawImage(str(ROOT/'bridge_preview.png'),13,38,165,134,mask='auto')
lines(184,165,['ベース・アンカー：6061-T6','ベース：18×98×25 mm','アンカー：18×50×最高10 mm','全幅：75 mm（弦間19）','','参考弦中心：8〜20 mm','通常前後調整：10 mm','公称最大調整：12 mm','木ねじ：前1＋後1／弦','','クラウン上縁R1.0、根元R0.8','後壁外周R1.4、内側接続R2','本体上縁R0.8、下縁R0.4','低いM3ボタン頭で固定','後方M4ネジ＋バネは継続'],size=3,leading=6.7)
lines(13,27,['長い止まりタップを裏面開放窓への短い貫通タップに変更。高さM4穴は窪みから移動。','画像はCAD実形状。球端・弦・ばね・ピエゾは参考外形。実機適合と耐久性は試作で確認。'],size=3,leading=6);end()
start('加工確認 / JLC向けの修正','STEPの妥当性と組立の干渉を確認済み。加工受託の最終判断・価格はJLCの手動審査で確定。',2,4,False)
lines(13,167,['Rev Fで見つかった点 → Rev Gでの修正','・ボールポケットと前側M4タップが交差 → X±5.25/Y20へ移動、全周の肉を確保。','・後側高さ穴と裏逃げが近い → Y27へ移動、側面逃げの開始Y30より前へ配置。','・後方M4の有効20 mm止まりタップ → 開放窓につなぐ12 mmの加工経路へ短縮。','・リブと壁の内角 → 平面R2で工具が通る形状へ。丸みはSTEPの実ソリッドに反映。','・両CNC部品を6061-T6へ統一。長さはベース90→98、アンカー42→50。','','CAD確認：各部品STEPの再読込、64ソリッドの組立、9組の高さ・前後位置で干渉なし。','M4主径の外周に0.8 mmの材料ガードを確認（高さ穴Z1〜7、後タップY42〜50）。','高さ・固定ねじの選択をg=0〜12で1201点確認。OD6バネと後木ねじの工具域も確認。','','JLCへはB05/A06を別部品として各4個。Threads=YES、6061-T6、As-machinedを指定。','同名のSTEP＋英語PDFを添付。組立STEP・STL・このガイドはアップロードしない。','Rの多い外形は仕上げパスが増える。3軸の複数方向加工を前提に費用・工具到達性を見積確認。','未審査：JLCの受託可否、価格、実弦、支持剛性、木部保持、疲労、ピエゾの分離度。'],size=3.2,leading=7)
lines(13,38,['参照：jlccnc.com/help/article/cnc-machining-ordering-guidelines','jlccnc.com/help/article/cnc-machining-design-guideline','jlccnc.com/help/article/aluminum-6061-cnc-machining'],size=2.9,leading=6)
end()
start('汎用金物と高さ調整','ミスミ型番は同梱のBOM・参照表を使用。ボタン頭の価格は購入時の見積で確認。',3,4,False)
lines(13,167,['前後：SCB4-30（SUS、M4×30、ねじ部20／首下の非ねじ10）＋UY6-20＋小形M4座金。','高さ：MSSFS4-8 / 12 / 16（平先、六角2）。gに合わせて4本／弦を交換。','固定：SSBCB3-12 / 16 / 20、長さ25だけSBCB3-25。頭径5.7、高さ1.65、六角2。','座金：WSJS-SUS-M3（外径6、厚0.5）。高さに合わせて合計厚を選択。','SCB3-12/16/20/25のキャップ頭は同じ首下長で代替可能。価格と納期を比較する。','木ねじ：コノエ270011003520候補（SUS皿3.5×20）。頭径7以下／90°を現物確認。','ピエゾ：各弦φ12以下。接着・配線込み厚1.2以下。木部へ挟み込まず金属裏へ接着。'],size=3.05,leading=7)
for x,t in zip([14,54,94,144,194,245],['g','参考弦中心','高さM4長さ','固定M3長さ','座金合計厚','先端Z']):txt(x,105,t,3.1)
for i,g in enumerate([0,2,4,6,8,10,12]):
 L=next(v for v in [12,16,20,25] if v>=11+g);t=.5*math.ceil((L-11-g+.2)/.5-1e-8);tip=11+g+t-L
 vals=[g,8+g,8 if g<=4 else 12 if g<=8 else 16,L,t,round(tip,2)]
 for x,v in zip([14,54,94,144,194,245],vals):txt(x,95-6.5*i,str(v),3.1)
lines(13,38,['固定先端はZ0.2〜0.7、木部への突出を避ける。公差を含め実測し座金で調整。','ばね自由長20±1.5、許容たわみ15。作動長25−q >= 実測自由長−15。','通常q8〜18の10 mmを推奨。q20までの12 mmは実測ばねが条件を満たす場合のみ。','弦を緩めて高さ・前後を調整し、固定M3を締める。4本の高さねじを均等に当てる。'],size=3,leading=6)
end()
start('取付テンプレート / 1:1','100%で印刷。50 mmチェック枠を実測。Rev G専用、新規穴あけ用。既存Jazz/Pの穴とは非互換。',4,4,False)
x0=72;y0=39
for x in (-28.5,-9.5,9.5,28.5):
 rect(x0+x-9,y0,18,98,4);ln(x0+x,y0-5,x0+x,y0+102,True)
 for yy in [5,93]:
  C.circle(x0+x,y0+yy,1.9);ln(x0+x-2,y0+yy,x0+x+2,y0+yy);ln(x0+x,y0+yy-2,x0+x,y0+yy+2)
for yy in [14,24,26]:ln(x0-37.5,y0+yy,x0+37.5,y0+yy,True)
dim(x0-37.5,x0+37.5,y0-10,'75');rect(218,39,50,50);dim(218,268,27,'50 mm')
lines(142,167,['取付穴：X=弦中心、Y5とY93。','各モジュールの前後穴間距離88。','金属側通し穴φ3.8、皿φ7/90°。','','ボディ穴の位置・深さは実測して決定。','木ねじの下穴径は木材と実物ねじから選ぶ。','既存穴・裏の空洞・木部端を避ける。','','弦を受ける肩：Y=q＋6。','通常Y14〜24、公称最大Y26。','初期の前端位置目安：スケール長−16。','実弦の補正量を確認して位置を確定。','','ピエゾ裏窪み中心：各弦X0/Y20。','配線は窪みから右側面へ逃がせる。','共通の木部による弦間振動は残る。'],size=3,leading=7)
lines(13,21,['まず1弦分で弦端の装填・最低高さ・ねじ・木部保持を検証してから4弦を製作。'],size=3)
end();C.save()

# Small procurement / feature tables, independent of PDF drawing geometry.
rows=[['B05','Smooth base 6061-T6',4,'18x98x25; STEP + matching PDF'],['A06','Smooth anchor 6061-T6',4,'18x50x10; STEP + matching PDF'],['H01','SCB4-30',4,'M4x30; threaded20/plain10; capheadD7/H4'],['H02','WSJS-SUS-M4',4,'OD8/ID4.5/t0.5'],['H03','UY6-20',4,'SUS304-WPB; OD6/wire0.35/L20/k0.098/solid3.85'],['H04','MSSFS4-8/12/16',16,'4/string; length by g; flat end'],['H05','SSBCB3-12/16/20 or SBCB3-25',8,'2/string; buttonheadD5.7/H1.65; 2mm hex; length by g'],['H06','WSJS-SUS-M3','height dependent','OD6/ID3.3/t0.5; stack by g; OD6 maximum'],['H07','270011003520',8,'SUS flathead wood screw3.5x20; verify headD<=7/90deg'],['P01','Piezo reference envelope',4,'OD<=12; total mounted thickness<=1.2; individual channels']]
with (ROOT/'BOM.csv').open('w',newline='',encoding='utf-8-sig') as f:
 w=csv.writer(f);w.writerow(['ID','item','quantity_for_4_strings','specification']);w.writerows(rows)
features=[['B05','Mounts','X0/Y5 and X0/Y93','D3.8 THRU; CSK D7/90 depth1.6'],['B05','Clamps','X+/-6/Y54','M3x0.5-6H THRU6; pilot2.5'],['B05','Piezo','X0/Y20','Bottom D12.5 depth1.5; wireW2.2 depth1.2'],['B05','Wall','Y75..81','R9 arch apex25; outsideR1.4; wall-rib internalR2'],['B05','Ribs','X[-9,-6] and[6,9]','Outside upper curvesR0.8; STEP geometry'],['A06','Height','X+/-5.25/Y20 and Y27','M4x0.7-6H THRU8; pilot3.3'],['A06','Rear thread','X0/Z4 fromY50 towards-Y','M4x0.7-6H THRU to underside window; pilot3.3 path12; full land8minY42..50; tap all outlet walls'],['A06','Central window','X0/Y32.5','W4.4/L15/depth6.3/R1.5'],['A06','Side relief','X+/-6/Y40','6x20/depth3/R1.5'],['A06','Clamps','X+/-6/Y40','SlotW3.4/totalL15.4'],['A06','Crown','X0/Y9','D12/topZ10/topR1/rootR0.8; body upperR0.8/lowerR0.4']]
with (ROOT/'features.csv').open('w',newline='',encoding='utf-8-sig') as f:
 w=csv.writer(f);w.writerow(['part','feature','coordinates_mm','machining']);w.writerows(features)
d=ezdxf.new('R2010');d.units=4;m=d.modelspace()
for layer,color in [('OUTLINE',7),('MOUNT_CENTER',1),('STRING_CENTER',3),('REFERENCE',4)]:d.layers.new(layer,dxfattribs={'color':color})
for x in (-28.5,-9.5,9.5,28.5):
 left,right,r=x-9,x+9,4
 for a,b in [((left+r,0),(right-r,0)),((right,r),(right,94)),((right-r,98),(left+r,98)),((left,94),(left,r))]:m.add_line(a,b,dxfattribs={'layer':'OUTLINE'})
 for centre,angles in [((right-r,r),(270,360)),((right-r,94),(0,90)),((left+r,94),(90,180)),((left+r,r),(180,270))]:m.add_arc(centre,r,*angles,dxfattribs={'layer':'OUTLINE'})
 m.add_line((x,-5),(x,103),dxfattribs={'layer':'STRING_CENTER'})
 for yy in (5,93):m.add_circle((x,yy),1.9,dxfattribs={'layer':'MOUNT_CENTER'})
for yy in (14,24,26):m.add_line((-37.5,yy),(37.5,yy),dxfattribs={'layer':'REFERENCE'})
m.add_lwpolyline([(50,0),(100,0),(100,50),(50,50)],close=True,dxfattribs={'layer':'REFERENCE'})
m.add_text('REV G / CHECK50mm / 1:1 / NEW HOLES',dxfattribs={'height':2.5,'insert':(50,55),'layer':'REFERENCE'})
d.saveas(ROOT/'MB4_mount_template_1to1.dxf')
print('Rev G: 3 PDFs / CAD-derived vector views / BOM / features / 1:1 DXF created')
