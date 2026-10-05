"""MB4 Rev I: aluminum solids, short rear tap opening into underside relief.
Units mm. Threads represented by tap drill holes, specified on matching PDFs.
"""
from pathlib import Path
import json, math, itertools
import cadquery as cq
ROOT=Path(__file__).resolve().parent
P=json.loads((ROOT/'parameters.json').read_text())
STEP=ROOT/'step';STL=ROOT/'preview_mesh'
STEP.mkdir(exist_ok=True);STL.mkdir(exist_ok=True)
V=cq.Vector
def box(w,l,h,x=0,y=0,z=0):
 return cq.Workplane('XY').box(w,l,h,centered=(True,False,False)).translate((x,y,z)).val()
def cyl(d,l,p,axis=(0,0,1)):
 return cq.Solid.makeCylinder(d/2,l,V(*p),V(*axis))
def rounded_pocket(w,l,h,x=0,y=0,z=0,r=1.5):
 return cq.Workplane('XY').box(w,l,h,centered=(True,True,False)).edges('|Z').fillet(r).translate((x,y,z)).val()
def finished_blank(w,l,h,r,edge=.2,x=0,y=0,z=0,top=None):
 wp=cq.Workplane('XY').box(w,l,h,centered=(True,False,False)).edges('|Z').fillet(r)
 wp=wp.faces('>Z').edges().fillet(edge if top is None else top)
 if edge:wp=wp.faces('<Z').edges().fillet(edge)
 return wp.translate((x,y,z)).val()
def washer(od,id,t,xyz,axis=(0,0,1)):
 return cyl(od,t,xyz,axis).cut(cyl(id,t,xyz,axis))
def screw_z(x,y,shoulder,length,head=True,diameter=3):
 s=cyl(diameter,length,(x,y,shoulder-length))
 if head:
  h=cq.Workplane('XY').circle(2.85).extrude(1.65).edges('>Z').fillet(1.15).translate((x,y,shoulder)).val()
  # Reference button-head envelope D5.7/H1.65, 2 mm hex socket.
  h=h.cut(cq.Workplane('XY').polygon(6,2.3094).extrude(1.1).translate((x,y,shoulder+.55)).val())
  return s.fuse(h)
 return s.cut(cq.Workplane('XY').polygon(6,1.732 if diameter==3 else 2.3094).extrude(1.5).translate((x,y,shoulder-1.5)).val())
def screw_y(x,y,z,length):
 # M4 x 0.7, standard headD7 H4 / socket3.
 s=cyl(4,length,(x,y,z),(0,-1,0))
 head=cyl(7,4,(x,y,z),(0,1,0))
 socket=cq.Workplane('XZ').polygon(6,3.4641).extrude(2.2).translate((x,y+4,z)).val()
 return s.fuse(head.cut(socket))

def gusset(x, back=False):
 # Simple planar webs: no Bezier bulges or stacked edge fillets.
 points=[(88.5,3),(93.5,3),(93.5,5),(88.5,16)] if back else [(78,3),(82.5,16),(82.5,3)]
 return cq.Workplane('YZ').polyline(points).close().extrude(3).translate((x,0,0)).val()

def make_wall():
 return (cq.Workplane('XZ').moveTo(-9,3).lineTo(9,3).lineTo(9,16)
    .threePointArc((0,25),(-9,16)).close().extrude(6).translate((0,88.5,0)).val())

def rear_flange():
 s=(cq.Workplane('YZ').moveTo(86,2).lineTo(86,3)
    .bezier([(86+2/3,3),(86+4/3,5),(88,5)],includeCurrent=True)
    .lineTo(98,5).lineTo(98,2).close().extrude(18).translate((-9,0,0)).val())
 return s.intersect(rounded_pocket(18,86,5,y=55,r=4))

def round_rear_rim(b):
 r=.9;zc=5-r
 # No side-rim rounding beneath the relocated rear webs.
 outer=box(10,r,r,y=98-r,z=zc)
 b=b.cut(outer.cut(cyl(2*r,10,(-5,98-r,zc),(1,0,0))))
 for sign in (-1,1):
  center=V(sign*5,94,zc)
  ring=cyl(8,r,center.toTuple()).cut(cyl(8-2*r,r,center.toTuple()))
  torus=cq.Solid.makeTorus(4-r,r,center,V(0,0,1))
  quarter=box(4,4,r,x=sign*7,y=94,z=zc)
  b=b.cut(ring.cut(torus).intersect(quarter))
 return b.clean()

def make_base():
 # No pre-rounded upper rim under the webs: one coplanar outer side face.
 blank=(cq.Workplane('XY').box(18,86,3,centered=(True,False,False))
        .edges('|Z').fillet(4).faces('<Z').edges().fillet(.2).translate((0,12,0)).val())
 b=blank.fuse(make_wall()).clean()
 for x in (-9,6):b=b.fuse(gusset(x)).fuse(gusset(x,True))
 b=b.fuse(rear_flange()).clean()
 assert b.isValid(),"raw rear flange fusion"
 corners=[e for e in b.Edges() if e.geomType()=='LINE' and e.BoundingBox().xlen<1e-6
          and e.BoundingBox().ylen<1e-6 and abs(abs(e.Center().x)-6)<1e-6
          and min(abs(e.Center().y-82.5),abs(e.Center().y-88.5))<1e-6]
 assert len(corners)==4,[(e.Center().toTuple(),e.Length()) for e in corners]
 b=b.fillet(2,corners).clean()
 print('base corners',b.isValid(),flush=True)
 assert b.isValid(),'inner corner fillets'
 # One small planar edge break per exposed diagonal, no complex rolling blends.
 diagonals=[e for e in b.Edges() if e.geomType()=='LINE' and e.BoundingBox().xlen<1e-6
             and abs(abs(e.Center().x)-9)<1e-6 and e.BoundingBox().ylen>3 and e.BoundingBox().zlen>8]
 assert len(diagonals)==4
 arcs=[e for e in b.Edges() if e.geomType()=='CIRCLE' and e.Center().z>18 and e.BoundingBox().ylen<1e-6]
 assert len(arcs)==2,[(e.Center().toTuple(),e.Length()) for e in arcs]
 plate=[e for e in b.Edges() if e.BoundingBox().zlen<1e-6 and abs(e.Center().z-3)<1e-6
        and e.Center().y<77.99 and (e.geomType()=='CIRCLE' or abs(abs(e.Center().x)-9)<1e-6 or e.Center().y<12.01)]
 b=b.chamfer(.25,None,diagonals+arcs+plate).clean()
 assert b.isValid(),'plain webs and arch'
 b=round_rear_rim(b)
 print('base flange',b.isValid(),flush=True)
 for x in (-6,6):b=b.fuse(finished_blank(6,6,3,1.5,0,x=x,y=45,z=3,top=.4))
 for x,y,h in [(0,20,3),(0,93,3)]:
  b=b.cut(cyl(3.8,h,(x,y,0)))
  b=b.cut(cq.Solid.makeCone(1.9,3.5,1.6,V(x,y,h-1.6),V(0,0,1)))
 b=b.cut(rounded_pocket(8,8,2,y=92.5,z=3,r=1.5)) # Top-open rear bolt head clearance tray.
 b=b.cut(cyl(7.4,2,(0,93,3))) # Rear wood screw head seat recessed to Z3.
 for x in (-6,6):b=b.cut(cyl(2.5,6,(x,48,0))) # Internal G datum; final Y36 after translation.
 b=b.cut(cyl(12.5,1.5,(0,36,0)))
 b=b.cut(box(9,2.2,1.2,x=4.5,y=34.9))
 slot=cq.Workplane('XZ').center(0,13).slot2D(16.5,4.5,90).extrude(6).translate((0,88.5,0)).val()
 b=b.cut(slot).cut(box(9,1,3,y=88.5,z=2)).clean()
 assert b.isValid() and len(b.Solids())==1
 return b.translate((0,-12,0))

def anchor_outline():
 return (cq.Workplane('XY').moveTo(-7,7).threePointArc((0,0),(7,7))
  .bezier([(7,9),(9,9),(9,11)],includeCurrent=True)
  .bezier([(9,14),(8.6,15),(8.6,18)],includeCurrent=True)
  .bezier([(8.6,21),(9,22),(9,25)],includeCurrent=True).lineTo(9,52)
  .threePointArc((8.121320344,54.121320344),(6,55)).lineTo(-6,55)
  .threePointArc((-8.121320344,54.121320344),(-9,52)).lineTo(-9,25)
  .bezier([(-9,22),(-8.6,21),(-8.6,18)],includeCurrent=True)
  .bezier([(-8.6,15),(-9,14),(-9,11)],includeCurrent=True)
  .bezier([(-9,9),(-7,9),(-7,7)],includeCurrent=True).close())

HEIGHT_X=5.7
HEIGHT_Y=(19,25)
ANCHOR_BEFORE_TAPS=None
def make_anchor():
 global ANCHOR_BEFORE_TAPS
 b=anchor_outline().extrude(8).faces('>Z').edges().fillet(.8).faces('<Z').edges().fillet(.4).val()
 crown=(cq.Workplane('XY').center(0,9).circle(6).extrude(2.4)
        .faces('>Z').edges().fillet(1.0).translate((0,0,7.6)).val())
 b=b.fuse(crown).clean()
 roots=[e for e in b.Edges() if e.geomType()=='CIRCLE' and abs(e.Center().z-8)<1e-6 and e.Length()>30]
 assert len(roots)==1
 b=b.fillet(.8,roots).clean()
 b=b.cut(rounded_pocket(8,11,8,y=11.5,z=2,r=1.5))
 # Round-ended slot: the rear vertical corners are no longer square.
 slot=cq.Workplane('XY').center(0,10).slot2D(24,3.4,90).extrude(6.7).translate((0,0,3.3)).val()
 b=b.cut(slot)
 for x in (-6,6):b=b.cut(rounded_pocket(6,27,3,x=x,y=41.5,z=0,r=1.5))
 # Rear screw moves through this open underside window after the short tap.
 b=b.cut(rounded_pocket(4.4,22,6.3,y=36,z=0,r=1.5))
 for x in (-6,6):
  slot=cq.Workplane('XY').center(x,41).slot2D(23.4,3.4,90).extrude(8).val()
  b=b.cut(slot)
 ANCHOR_BEFORE_TAPS=b.clean()
 for x in (-HEIGHT_X,HEIGHT_X):
  for y in HEIGHT_Y:b=b.cut(cyl(3.3,8,(x,y,0)))
 # Standard tap entering from Y55; drill breaks fully into the underside window.
 b=b.cut(cyl(3.3,12,(0,55,4),(0,-1,0)))
 lips=[e for e in b.Edges() if e.geomType()=='LINE' and abs(e.Center().z-10)<1e-6
       and abs(abs(e.Center().x)-1.7)<1e-6 and e.Length()>.5]
 assert len(lips)==2
 b=b.fillet(.4,lips).clean()
 assert b.isValid() and len(b.Solids())==1
 return b

def jack_hardware(gap):
 length=8 if gap<=4 else (12 if gap<=8 else 16)
 engagement=length-gap
 assert 4-1e-8<=engagement<=8+1e-8
 return length,engagement

def clamp_hardware(gap):
 length=next(v for v in (12,16,20,25) if v>=11+gap-1e-8)
 stack=.5*math.ceil((length-(11+gap)+.2)/.5-1e-8)
 tip=11+gap+stack-length
 assert .19999<=tip<=.70001
 return length,stack,tip

PARTS={}
COLORS={'B07_long_travel_base':cq.Color(.38,.45,.50),'A07_long_travel_anchor':cq.Color(.63,.68,.72)}
_spring_cache={}
def spring(length):
 if length not in _spring_cache:
  wire=.4;radius=(6-wire)/2;h=length-wire;pitch=h/15
  path=cq.Wire.makeHelix(pitch,h,radius)
  plane=cq.Plane(origin=(radius,0,0),normal=(0,1,pitch/(2*math.pi*radius)))
  s=cq.Workplane(plane).circle(wire/2).sweep(cq.Workplane().newObject([path]),isFrenet=True).val()
  s=s.rotate((0,0,0),(1,0,0),-90).translate((0,wire/2,0))
  assert s.isValid();_spring_cache[length]=s
 return _spring_cache[length]

def init_parts():
 if not PARTS:
  PARTS.update({'B07_long_travel_base':make_base(),'A07_long_travel_anchor':make_anchor()})

def module_items(x=0,origin=2,gap=2,reference=True):
 init_parts();items=[]
 def add(n,s,c):items.append((n,s,c))
 steel=cq.Color(.76,.77,.79)
 add('B07_long_travel_base',PARTS['B07_long_travel_base'].translate((x,0,0)),COLORS['B07_long_travel_base'])
 add('A07_long_travel_anchor',PARTS['A07_long_travel_anchor'].translate((x,origin,3+gap)),COLORS['A07_long_travel_anchor'])
 length,stack,tip=clamp_hardware(gap)
 for xx in (-6,6):
  add('clamp_washer_stack',washer(6,3.3,stack,(x+xx,36,11+gap)),steel)
  add('clamp_M3',screw_z(x+xx,36,11+gap+stack,length),steel)
 for xx in (-HEIGHT_X,HEIGHT_X):
  for yy in HEIGHT_Y:
   length,_=jack_hardware(gap)
   add('height_M4',screw_z(x+xx,origin+yy,3+length,length,False,4),steel)
 axis=7+gap
 add('intonation_M4x45_FULL_THREAD',screw_y(x,77,axis,45),steel)
 add('intonation_washer',washer(8,4.5,.5,(x,76.5,axis),(0,1,0)),steel)
 add('compression_spring_REFERENCE',spring(15.5-origin).translate((x,origin+55,axis)),steel)
 if reference:
  add('string_reference',cyl(1.1,120,(x,origin+6,8+gap),(0,-1,0)),cq.Color(.85,.85,.85))
  ball=cyl(6,4.75,(x-2.375,origin+9,8+gap),(1,0,0)).cut(cyl(2.4,4.75,(x-2.375,origin+9,8+gap),(1,0,0)))
  add('ball_reference_ONLY',ball,cq.Color(.72,.63,.43))
  add('piezo_envelope_ONLY',cyl(12,.7,(x,24,.5)),cq.Color(.7,.38,.13))
 return items

def check():
 init_parts();records=[];walls=[]
 # Verify actual pilot bores, before removing nominal threaded mating material.
 for x in (-6,6):
  bore=cyl(2.48,6,(x,36,0))
  assert bore.intersect(PARTS['B07_long_travel_base']).Volume()<1e-6,('M3 actual through bore',x,36)
  guard=cyl(4.6,5.2,(x,36,.4)).cut(cyl(3,5.2,(x,36,.4)))
  assert guard.cut(PARTS['B07_long_travel_base']).Volume()<1e-6,('M3 threaded boss wall',x,36)
 for sign in (-1,1):
  probe=box(.15,14.5,.15,x=sign*8.85,y=66.5,z=2.75)
  absent=probe.cut(PARTS['B07_long_travel_base']).Volume()
  assert absent<1e-6,('continuous web/base root material band',sign,absent)
 # Major-diameter hole plus 0.8 mm radial guard: cylindrical material test.
 # End chamfers and external rounding are excluded from the axial guard.
 for x in (-HEIGHT_X,HEIGHT_X):
  for y in HEIGHT_Y:
   guard=cyl(5.6,6,(x,y,1)).cut(cyl(4,6,(x,y,1)))
   absent=guard.cut(ANCHOR_BEFORE_TAPS).Volume()
   assert absent<1e-6,('height major-diameter wall',x,y,absent)
   walls.append({'xy':[x,y],'guard_radial_mm':.8,'axial_span_mm':[1,7],'missing_material_mm3':absent})
 a=PARTS['A07_long_travel_anchor']
 rear_guard=cyl(5.6,8,(0,55,4),(0,-1,0)).cut(cyl(4,8,(0,55,4),(0,-1,0)))
 missing=rear_guard.cut(a).Volume()
 assert missing<1e-6,('rear full-ring thread land',missing)
 # Tapped diameter is shown as pilot diameter in STEP. Restrict allowed
 # screw intersections to cylindrical mating regions, not entire parts.
 anchor_clear=a
 for x in (-HEIGHT_X,HEIGHT_X):
  for y in HEIGHT_Y:anchor_clear=anchor_clear.cut(cyl(4,8,(x,y,0)))
 anchor_clear=anchor_clear.cut(cyl(4,12,(0,55,4),(0,-1,0)))
 base_clear=PARTS['B07_long_travel_base']
 for x in (-6,6):base_clear=base_clear.cut(cyl(3,6,(x,36,0)))
 for cy in (9,10,12,14):
  assert cyl(6,4.75,(-2.375,cy,5),(1,0,0)).intersect(a).Volume()<1e-6,('ball',cy)
 for gap in [i/100 for i in range(1201)]:clamp_hardware(gap);jack_hardware(gap)
 for q,g in itertools.product((-15,-5,5),(0,6,12)):
  for x in (-HEIGHT_X,HEIGHT_X):
   for yy in HEIGHT_Y:
    foot=cyl(4,.1,(x,q+yy,2.9))
    assert foot.cut(PARTS['B07_long_travel_base']).Volume()<1e-6,('height foot full support',q,x,yy)
  placed=module_items(0,q,g,False)
  base,anchor=placed[0][1],placed[1][1]
  assert base.intersect(anchor).Volume()<1e-6,('parts',q,g)
  clear=[base_clear,anchor_clear.translate((0,q,3+g))]
  for n,h,_ in placed[2:]:
   for i,part in enumerate(clear):
    v=h.intersect(part).Volume();assert v<1e-5,(q,g,n,i,v)
  # Full OD envelope tests spring clearance, independent of visual helix.
  spring_envelope=cyl(6,15.5-q,(0,q+55,7+g),(0,1,0))
  for i,part in enumerate((base,anchor)):
   v=spring_envelope.intersect(part).Volume();assert v<1e-5,('spring OD envelope',q,g,i,v)
  tip=32-q;working=15.5-q;overlap=min(q+23,8)
  assert overlap>=8-1e-8 and tip>=27-1e-8
  assert 33.5-working>=3-1e-8 and 36.5-working<=26.25+1e-8
  assert working>=10.5-1e-8
  length,stack,clamp_tip=clamp_hardware(g)
  records.append({'q':q,'g':g,'string_axis_height':8+g,'spring_length':working,
    'spring_force_reference_N':(35-working)*.098,'spring_solid_height_margin':working-6.8,
    'rear_full_land_overlap_mm':overlap,'rear_bolt_penetration_mm':q+23,
    'thread_type':'full thread required','rear_screw_tip_local_y':tip,'spring_worst_tolerance_deflection':36.5-working,'spring_allowable_deflection':26.25,
    'clamp_length':length,'clamp_washer_stack':stack,'clamp_tip_z':clamp_tip,
    'clamp_thread_engagement':6-clamp_tip,'height_screw_length':jack_hardware(g)[0],
    'height_thread_engagement':jack_hardware(g)[1]})
 rear_items=module_items(0,2,0,False);driver=cyl(6,35,(0,81,5))
 assert driver.intersect(PARTS['B07_long_travel_base']).Volume()<1e-5,('rear driver with anchor/intonation screw removed')
 rear_head=cq.Solid.makeCone(1.9,3.5,1.6,V(0,81,1.4),V(0,0,1))
 for q,g in itertools.product((-15,-5,5),(0,6,12)):
  for n,h,_ in module_items(0,q,g,False)[1:]:
   assert rear_head.intersect(h).Volume()<1e-5,('rear flush wood head',q,g,n)
 # Screw head is flush in D7/90 CSK; verify a conservative metal head envelope.
 front_head=cq.Solid.makeCone(1.9,3.5,1.6,V(0,8,1.4),V(0,0,1))
 for q,g in itertools.product((-15,-5,5),(0,6,12)):
  v=front_head.intersect(a.translate((0,q,3+g))).Volume()
  assert v<1e-6,('flush front fixing head',q,g,v)
 # With the anchor removed, front driver access must be clear.
 tool=cyl(6,35,(0,8,3))
 assert tool.intersect(PARTS['B07_long_travel_base']).Volume()<1e-6
 return records,walls

def build():
 records,walls=check()
 for n,s in PARTS.items():
  assert s.isValid() and len(s.Solids())==1
  cq.exporters.export(s,str(STEP/(n+'.step')))
  cq.exporters.export(s,str(STL/(n+'.stl')),tolerance=.035,angularTolerance=.12)
 assembly=cq.Assembly(name='MB4_revision_I_mm');manifest=[]
 for i,(x,q,g) in enumerate(zip([-28.5,-9.5,9.5,28.5],[3,1,-1,-3],[5,4,3,2])):
  for j,(n,s,c) in enumerate(module_items(x,q,g)):
   name=f'S{i+1}_{n}_{j}';assembly.add(s,name=name,color=c)
   f=STL/(name+'.stl');cq.exporters.export(s,str(f),tolerance=.045,angularTolerance=.12)
   manifest.append({'name':name,'file':str(f.relative_to(ROOT)),'color':list(c.toTuple()[:3])})
 assembly.export(str(STEP/'MB4_assembly.step'))
 (ROOT/'scene_manifest.json').write_text(json.dumps(manifest,indent=2))
 imported={}
 for n,old in PARTS.items():
  s=cq.importers.importStep(str(STEP/(n+'.step'))).val()
  print('STEP_CHECK',n,s.isValid(),s.Volume(),old.Volume(),abs(s.Volume(1e-8)-old.Volume(1e-8))/old.Volume(1e-8),flush=True)
  assert s.isValid() and abs(s.Volume(1e-8)-old.Volume(1e-8))<old.Volume(1e-8)*1e-6
  bb=s.BoundingBox();imported[n]={'volume_mm3':s.Volume(1e-8),'bbox_mm':[bb.xlen,bb.ylen,bb.zlen], 'material':'6061-T6'}
 s=cq.importers.importStep(str(STEP/'MB4_assembly.step')).val()
 assert s.isValid() and len(s.Solids())==len(manifest)
 (ROOT/'scene_manifest.json').write_text(json.dumps(manifest,indent=2))
 (ROOT/'geometry_check.json').write_text(json.dumps({'revision':'I','units':'mm','valid_solids':imported,
  'assembly_solids':len(manifest),'limits':records,'height_tap_wall_guards':walls,
  'rear_tap_guard_radial_mm':.8,'rear_tap_guard_axial_span_y':[47,55],
  'hardware_interference':'passed; only major-diameter cylinders removed at designated tapped holes',
  'base_M3_bores':'actual D2.5 through bores at X+/-6,Y36 passed; radial material guard 0.8 mm passed',
  'spring_full_D6_envelope':'passed at all 9 travel/height conditions',
  'rear_mounts':{'xy':[[0,81]],'driver_clearance':'D6 x35 mm passed before anchor/intonation screw installation','head_seat_z':3,'counterbore_D7_4_depth':2},
  'web_root_band':'passed: continuous outer material at X+/-8.85,Y66.5..81,Z2.75..2.9',
  'front_mount':{'xy':[0,8],'installation':'fix base before installing anchor','D6_driver_without_anchor':'passed'},
  'piezo_center_xy':[0,24],
  'front_limit_anchor_overhang_mm':15,
  'height_and_clamp_sweep':'1201 heights checked across g=0..12',
  'normal_q_range':[-15,5],'nominal_mechanical_q_range':[-15,5],'travel_mm':20,'spring_tolerance_envelope':'35 +/-1.5 mm; working 10.5..30.5; max deflection26 <=26.25 mm',
  'thread_wall_nominal_minimum_bulk_mm':.9,
  'not_verified':['actual supplier CNC acceptance/price','physical strength/fatigue',
    'actual string ball/winding fit and string centre at contact','specific bass fit',
    'piezo pickup isolation/performance','actual spring free-length tolerance and ends'],
  'spring_model':'visual reference, constant pitch; catalogue envelope separately checked'},indent=2))
 print(json.dumps(imported,indent=2));print('Rev I: thread wall / nine assembly conditions / STEP roundtrip passed',flush=True)
if __name__=='__main__':build()
