"""Rev H: CAD-derived vector shop views and prototype/ordering guide."""
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
 txt(13,8,'MB4 / REV H / 2026-10-05 / mm / PROTOTYPE - RFQ',2.7)
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
  txt(x,y,label,3.15);txt(x+51,y,value,3.15);ln(x,y-2,x+width,y-2);y-=8
 return y

C=canvas.Canvas(str(PDF/'B06_compact_base.pdf'),pagesize=(420*mm,297*mm));C.setTitle('MB4 Rev H B06 base - 6061-T6 - 4 required')
start('B06 / SMOOTH BASE','QTY 4 | ALUMINUM 6061-T6 | 18 x 86 x 25 | STEP: B06_compact_base.step',1,2)
view('B06_compact_base',(0,0,1),18,65,80,178,'TOP (+Z)')
view('B06_compact_base',(0,0,-1),106,65,80,178,'BOTTOM (-Z; mirrored Y on screen)')
view('B06_compact_base',(0,-1,0),22,21,160,35,'FRONT (-Y)')
y=feature_table(204,251,[('DATUM','X=width centre; Y=front; Z=bottom'),('Envelope','W18; L86; max height25'),('Main plate','Z0..3; planR4; free front upper rimC0.25'),('Front mount','X0 / Y8; D3.8 THRU3'),('Rear mount','X0 / Y81; D3.8 THRU5'),('Both countersinks','D7 x 90 deg; axial depth1.6'),('CSK floor left','Front1.4; rear3.4'),('Clamp threads','2x M3 x 0.5 - 6H THRU6'),('Clamp coordinates','X +/-6; Y42; tap drill D2.5'),('Integral clamp pads','6 x 6; Z3..6; plan R1.5; topR0.4'),('Piezo pocket','Bottom: X0/Y24; D12.5; depth1.5'),('Wire exit','X0..9; Y22.9..25.1; depth1.2'),('Wall position','Y63..69; thickness6'),('Wall slot','X0/Z13; W4.5; totalL16.5 THRU6'),('Washer recess','X +/-4.5; Y69..70; bottomZ2')])
lines(204,y-7,['Threads are pilot-diameter representations in STEP.','Make M3 threads; do not leave them as plain D2.5 bores.','Hole and thread axis locations: +/-0.05 mm.','D3.8 clearance / slotW4.5: +/-0.05 mm.','Other dimensions: ISO 2768-m; geometry from STEP.','Flatness of body seat: 0.05 mm. Ra3.2 target.'],size=3.1,leading=6)
end()
start('B06 / PLAIN WEBS AND MACHINING ACCESS','Top, bottom and end setups. No enclosed undercuts. Straight web faces and specified edge breaks are defined by STEP.',2,2)
view('B06_compact_base',(-1,0,0),15,151,184,68,'LEFT (-X)')
view('B06_compact_base',(1,0,0),15,61,184,68,'RIGHT (+X)')
view('B06_compact_base',(1,-1,1),210,105,187,121,'ISOMETRIC (illustration; not dimensioned)')
lines(210,255,['Wall arch: true R9, centre X0/Z16; apexZ25.','Arch rim and exposed web diagonals: C0.25.','Wall/rib vertical inside corners: R2.0.','Coplanar web/base side face; no stacked rim fillets.'],leading=7)
lines(18,45,['Internal wall/floor roots may be eased R0.2 MAX; preserve spring envelope.','Do not enlarge the slot/recess or remove integral ribs without approval.','Remaining cosmetic edges: C0.2 MAX. Thread mouths and countersink seats: C0.1 MAX.'],leading=7)
lines(210,90,['Rear flange: Y76..86, topZ5; outside upper rim R0.9.','Smooth ramp: Y74..76, Z3..5; profile from STEP.','Ribs width3: X[-9,-6] and X[6,9].','Front web slope: (Y,Z) (58.5,3) to (63,16).','Rear web slope: (69,16) to (76,5).','Integral planar webs, 3 mm thick; no under-root rim groove.','As-machined finish; no polishing of functional seats.','Aluminum threads: gauge M3 x 0.5 - 6H.'],size=3.1,leading=7)
end();C.save()

# Japanese assembly / quotation guide (not uploaded to JLC).
FONT=JP
C=canvas.Canvas(str(PDF/'MB4_RevH_guide.pdf'),pagesize=(297*mm,210*mm));C.setTitle('MB4 Rev H - smooth aluminum prototype guide')
start('MB4 / Rev H 短いベース・簡潔なリブ','前側の取付穴・ピエゾを後ろへ寄せ、ベースを12 mm短縮。弦間19 mm、各弦独立、4弦でCNC部品8点。',1,4,False)
if (ROOT/'bridge_preview.png').exists():C.drawImage(str(ROOT/'bridge_preview.png'),13,38,165,134,mask='auto')
lines(184,165,['ベース・アンカー：6061-T6','ベース：18×86×25 mm','アンカー：18×50×最高10 mm','全幅：75 mm（弦間19）','','参考弦中心：8〜20 mm','通常前後調整：10 mm','公称最大調整：12 mm','木ねじ：前1＋後1／弦','','クラウン上縁R1.0、根元R0.8','リブは平面、内角R2／外縁C0.25','本体上縁R0.8、下縁R0.4','低いM3ボタン頭で固定','後方M4ネジ＋バネは継続'],size=3,leading=6.7)
lines(13,27,['前木ねじはアンカーの下へ移動。ベースを先にボディへ固定し、後からアンカーを組む。','画像はCAD実形状。球端・弦・ばね・ピエゾは参考外形。実機適合と耐久性は試作で確認。'],size=3,leading=6);end()
start('短縮とリブ整理 / 確認結果','アンカーA06はRev Gと同形状。ねじ・バネ・高さ調整範囲を保ち、ベースB06を変更。',2,4,False)
lines(13,167,['Rev G → Rev H：前端を12 mm詰め、ベース長98→86。全幅75 mmは維持。','前木ねじ：旧版の同じ基準でY5→20、エンド側へ15 mm移動。','ピエゾ：旧版の同じ基準でY20→36、エンド側へ16 mm移動。','新版の前端をY0に取り直すため、新座標は前木ねじY8、ピエゾY24、後木ねじY81。','','リブ上辺は直線、側面は平面。幅3と最高Z16を維持し、複雑な外縁の曲面Rを廃止。','内角R2は工具の逃げとして維持。外縁C0.25、根元とベース側面は連続した平面。','斜視図は隠れ線を省略して、見えている形を簡潔に表示。','','CAD確認：STEP再読込、9組の高さ・前後位置で干渉なし。高さ・固定ねじを1201点確認。M3下穴の貫通も検証。','前木ねじの皿頭包絡とアンカーが干渉しないこと、アンカーなしで工具が入ることを確認。','前側を最大まで出すと、アンカー先端はベース前端より4 mm出る。通常範囲はq=-4〜6。','公称最大q=8はばねの実測が必要。参考弦中心8〜20 mm。実機適合・強度は未評価。','','JLCへはB06/A06を別部品として各4個。Threads=YES、6061-T6、As-machined。','同名STEP＋英語PDFを添付。加工受託・工具到達性・価格は手動審査で確定。','前取付穴がアンカーの下へ移るため、組み付け後の取付穴への工具アクセスは想定しない。'],size=3.1,leading=7)
lines(13,38,['参照：jlccnc.com/help/article/cnc-machining-ordering-guidelines','jlccnc.com/help/article/cnc-machining-design-guideline','jlccnc.com/help/article/aluminum-6061-cnc-machining'],size=2.9,leading=6)
end()
start('汎用金物と高さ調整','ミスミ型番は同梱のBOM・参照表を使用。ボタン頭の価格は購入時の見積で確認。',3,4,False)
lines(13,167,['前後：SCB4-30（SUS、M4×30、ねじ部20／首下の非ねじ10）＋UY6-20＋小形M4座金。','高さ：MSSFS4-8 / 12 / 16（平先、六角2）。gに合わせて4本／弦を交換。','固定：SSBCB3-12 / 16 / 20、長さ25だけSBCB3-25。頭径5.7、高さ1.65、六角2。','座金：WSJS-SUS-M3（外径6、厚0.5）。高さに合わせて合計厚を選択。','SCB3-12/16/20/25のキャップ頭は同じ首下長で代替可能。価格と納期を比較する。','木ねじ：コノエ270011003520候補（SUS皿3.5×20）。頭径7以下／90°を現物確認。','ピエゾ：各弦φ12以下。接着・配線込み厚1.2以下。木部へ挟み込まず金属裏へ接着。'],size=3.05,leading=7)
for x,t in zip([14,54,94,144,194,245],['g','参考弦中心','高さM4長さ','固定M3長さ','座金合計厚','先端Z']):txt(x,105,t,3.1)
for i,g in enumerate([0,2,4,6,8,10,12]):
 L=next(v for v in [12,16,20,25] if v>=11+g);t=.5*math.ceil((L-11-g+.2)/.5-1e-8);tip=11+g+t-L
 vals=[g,8+g,8 if g<=4 else 12 if g<=8 else 16,L,t,round(tip,2)]
 for x,v in zip([14,54,94,144,194,245],vals):txt(x,95-6.5*i,str(v),3.1)
lines(13,38,['固定先端はZ0.2〜0.7、木部への突出を避ける。公差を含め実測し座金で調整。','ばね自由長20±1.5、許容たわみ15。作動長13−q >= 実測自由長−15。','通常q=-4〜6の10 mmを推奨。q=8までの12 mmは実測ばねが条件を満たす場合のみ。','弦を緩めて高さ・前後を調整し、固定M3を締める。4本の高さねじを均等に当てる。'],size=3,leading=6)
end()
start('取付テンプレート / 1:1','100%で印刷。50 mmチェック枠を実測。Rev H専用、新規穴あけ用。既存Jazz/Pの穴とは非互換。',4,4,False)
x0=72;y0=39
for x in (-28.5,-9.5,9.5,28.5):
 rect(x0+x-9,y0,18,86,4);ln(x0+x,y0-5,x0+x,y0+90,True)
 for yy in [8,81]:
  C.circle(x0+x,y0+yy,1.9);ln(x0+x-2,y0+yy,x0+x+2,y0+yy);ln(x0+x,y0+yy-2,x0+x,y0+yy+2)
for yy in [2,12,14]:ln(x0-37.5,y0+yy,x0+37.5,y0+yy,True)
dim(x0-37.5,x0+37.5,y0-10,'75');rect(218,39,50,50);dim(218,268,27,'50 mm')
lines(142,167,['取付穴：X=弦中心、Y8とY81。','各モジュールの前後穴間距離73。','金属側通し穴φ3.8、皿φ7/90°。','','ボディ穴の位置・深さは実測して決定。','木ねじの下穴径は木材と実物ねじから選ぶ。','既存穴・裏の空洞・木部端を避ける。','','弦を受ける肩：Y=q＋6。','通常Y2〜12、公称最大Y14。','初期の前端位置目安：スケール長−4。','実弦の補正量を確認して位置を確定。','','ピエゾ裏窪み中心：各弦X0/Y24。','配線は窪みから右側面へ逃がせる。','共通の木部による弦間振動は残る。'],size=3,leading=7)
lines(13,21,['組立順：ベース固定 → 配線 → アンカー・ばね・調整ねじ。前木ねじの頭は完全に皿座へ収める。'],size=3)
end();C.save()

# Small procurement / feature tables, independent of PDF drawing geometry.
rows=[['B06','Smooth base 6061-T6',4,'18x86x25; STEP + matching PDF'],['A06','Smooth anchor 6061-T6',4,'18x50x10; STEP + matching PDF'],['H01','SCB4-30',4,'M4x30; threaded20/plain10; capheadD7/H4'],['H02','WSJS-SUS-M4',4,'OD8/ID4.5/t0.5'],['H03','UY6-20',4,'SUS304-WPB; OD6/wire0.35/L20/k0.098/solid3.85'],['H04','MSSFS4-8/12/16',16,'4/string; length by g; flat end'],['H05','SSBCB3-12/16/20 or SBCB3-25',8,'2/string; buttonheadD5.7/H1.65; 2mm hex; length by g'],['H06','WSJS-SUS-M3','height dependent','OD6/ID3.3/t0.5; stack by g; OD6 maximum'],['H07','270011003520',8,'SUS flathead wood screw3.5x20; verify headD<=7/90deg'],['P01','Piezo reference envelope',4,'OD<=12; total mounted thickness<=1.2; individual channels']]
with (ROOT/'BOM.csv').open('w',newline='',encoding='utf-8-sig') as f:
 w=csv.writer(f);w.writerow(['ID','item','quantity_for_4_strings','specification']);w.writerows(rows)
features=[['B06','Mounts','X0/Y8 and X0/Y81','D3.8 THRU; CSK D7/90 depth1.6'],['B06','Clamps','X+/-6/Y42','M3x0.5-6H THRU6; pilot2.5'],['B06','Piezo','X0/Y24','Bottom D12.5 depth1.5; wireW2.2 depth1.2'],['B06','Wall','Y63..69','R9 arch apex25; arch/web edgesC0.25; wall-rib internalR2'],['B06','Ribs','X[-9,-6] and[6,9]','Straight web faces; diagonalC0.25; STEP geometry'],['A06','Height','X+/-5.25/Y20 and Y27','M4x0.7-6H THRU8; pilot3.3'],['A06','Rear thread','X0/Z4 fromY50 towards-Y','M4x0.7-6H THRU to underside window; pilot3.3 path12; full land8minY42..50; tap all outlet walls'],['A06','Central window','X0/Y32.5','W4.4/L15/depth6.3/R1.5'],['A06','Side relief','X+/-6/Y40','6x20/depth3/R1.5'],['A06','Clamps','X+/-6/Y40','SlotW3.4/totalL15.4'],['A06','Crown','X0/Y9','D12/topZ10/topR1/rootR0.8; body upperR0.8/lowerR0.4']]
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
for yy in (2,12,14):m.add_line((-37.5,yy),(37.5,yy),dxfattribs={'layer':'REFERENCE'})
m.add_lwpolyline([(50,0),(100,0),(100,50),(50,50)],close=True,dxfattribs={'layer':'REFERENCE'})
m.add_text('REV H / CHECK50mm / 1:1 / NEW HOLES',dxfattribs={'height':2.5,'insert':(50,55),'layer':'REFERENCE'})
d.saveas(ROOT/'MB4_mount_template_1to1.dxf')
print('Rev H: 2 new PDFs / unchanged A06 drawing / CAD-derived vector views / BOM / features / 1:1 DXF created')
