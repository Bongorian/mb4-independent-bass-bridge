"""MB4 Rev G: aluminum solids, short rear tap opening into underside relief.
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
 wp=cq.Workplane('YZ')
 if back:
  wp=wp.moveTo(81,3).lineTo(88,3).lineTo(88,5).bezier([(84.5,5),(81,16)],includeCurrent=True).close()
 else:
  wp=wp.moveTo(68.5,3).bezier([(71.75,3),(75,16)],includeCurrent=True).lineTo(75,3).close()
 s=wp.extrude(3).translate((x,0,0)).val()
 edges=[e for e in s.Edges() if e.geomType() in ('BEZIER','BSPLINE')]
 assert len(edges)==2
 return s

def make_wall():
 s=(cq.Workplane('XZ').moveTo(-9,3).lineTo(9,3).lineTo(9,16)
    .threePointArc((0,25),(-9,16)).close().extrude(6).translate((0,81,0)).val())
 edges=[e for e in s.Edges() if e.BoundingBox().ylen<1e-6 and e.Center().z>3.01]
 return s.fillet(1.4,edges)

def rear_flange():
 s=(cq.Workplane('YZ').moveTo(86,2).lineTo(86,3)
    .bezier([(86+2/3,3),(86+4/3,5),(88,5)],includeCurrent=True)
    .lineTo(98,5).lineTo(98,2).close().extrude(18).translate((-9,0,0)).val())
 return s.intersect(rounded_pocket(18,98,5,y=49,r=4))

def round_rear_rim(b):
 r=.9;zc=5-r
 for sign in (-1,1):
  outer=box(r,6,r,x=sign*(9-r/2),y=88,z=zc)
  keep=cyl(2*r,6,(sign*(9-r),88,zc),(0,1,0))
  b=b.cut(outer.cut(keep))
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
 b=finished_blank(18,98,3,4,.2,top=.8).fuse(make_wall()).clean()
 for x in (-9,6):b=b.fuse(gusset(x)).fuse(gusset(x,True))
 b=b.clean()
 corners=[e for e in b.Edges() if e.geomType()=='LINE' and e.BoundingBox().xlen<1e-6
          and e.BoundingBox().ylen<1e-6 and abs(abs(e.Center().x)-6)<1e-6
          and min(abs(e.Center().y-75),abs(e.Center().y-81))<1e-6]
 assert len(corners)==4,[(e.Center().toTuple(),e.Length()) for e in corners]
 b=b.fillet(2,corners).clean()
 print('base corners',b.isValid(),flush=True)
 assert b.isValid(),'inner corner fillets'
 outer_curves=[e for e in b.Edges() if e.geomType() in ('BEZIER','BSPLINE')
               and e.BoundingBox().xlen<1e-6 and abs(abs(e.Center().x)-9)<1e-6]
 assert len(outer_curves)==4
 b=b.fillet(.8,outer_curves).clean()
 print('base outer ribs',b.isValid(),flush=True)
 edges=[e for e in b.Edges() if e.geomType()=='LINE' and abs(e.Center().y-75)<1e-6
        and abs(e.Center().z-3)<1e-6 and e.Length()>5]
 assert len(edges)==1
 b=round_rear_rim(b.fuse(rear_flange()).clean())
 print('base flange',b.isValid(),flush=True)
 for x in (-6,6):b=b.fuse(finished_blank(6,6,3,1.5,0,x=x,y=51,z=3,top=.4))
 for x,y,h in [(0,5,3),(0,93,5)]:
  b=b.cut(cyl(3.8,h,(x,y,0)))
  b=b.cut(cq.Solid.makeCone(1.9,3.5,1.6,V(x,y,h-1.6),V(0,0,1)))
 for x in (-6,6):b=b.cut(cyl(2.5,6,(x,54,0)))
 b=b.cut(cyl(12.5,1.5,(0,20,0)))
 b=b.cut(box(9,2.2,1.2,x=4.5,y=18.9))
 slot=cq.Workplane('XZ').center(0,13).slot2D(16.5,4.5,90).extrude(6).translate((0,81,0)).val()
 b=b.cut(slot).cut(box(9,1,1,y=81,z=2)).clean()
 assert b.isValid() and len(b.Solids())==1
 return b

def anchor_outline():
 return (cq.Workplane('XY').moveTo(-7,7).threePointArc((0,0),(7,7))
  .bezier([(7,9),(9,9),(9,11)],includeCurrent=True)
  .bezier([(9,14),(8.6,15),(8.6,18)],includeCurrent=True)
  .bezier([(8.6,21),(9,22),(9,25)],includeCurrent=True).lineTo(9,47)
  .threePointArc((8.121320344,49.121320344),(6,50)).lineTo(-6,50)
  .threePointArc((-8.121320344,49.121320344),(-9,47)).lineTo(-9,25)
  .bezier([(-9,22),(-8.6,21),(-8.6,18)],includeCurrent=True)
  .bezier([(-8.6,15),(-9,14),(-9,11)],includeCurrent=True)
  .bezier([(-9,9),(-7,9),(-7,7)],includeCurrent=True).close())

HEIGHT_X=5.25
HEIGHT_Y=(20,27)
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
 for x in (-6,6):b=b.cut(rounded_pocket(6,20,3,x=x,y=40,z=0,r=1.5))
 # Rear screw moves through this open underside window after the short tap.
 b=b.cut(rounded_pocket(4.4,15,6.3,y=32.5,z=0,r=1.5))
 for x in (-6,6):
  slot=cq.Workplane('XY').center(x,40).slot2D(15.4,3.4,90).extrude(8).val()
  b=b.cut(slot)
 ANCHOR_BEFORE_TAPS=b.clean()
 for x in (-HEIGHT_X,HEIGHT_X):
  for y in HEIGHT_Y:b=b.cut(cyl(3.3,8,(x,y,0)))
 # Standard tap entering from Y50; drill breaks fully into the underside window.
 b=b.cut(cyl(3.3,12,(0,50,4),(0,-1,0)))
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
COLORS={'B05_smooth_base':cq.Color(.38,.45,.50),'A06_smooth_anchor':cq.Color(.63,.68,.72)}
_spring_cache={}
def spring(length):
 if length not in _spring_cache:
  wire=.35;radius=(6-wire)/2;h=length-wire;pitch=h/10
  path=cq.Wire.makeHelix(pitch,h,radius)
  plane=cq.Plane(origin=(radius,0,0),normal=(0,1,pitch/(2*math.pi*radius)))
  s=cq.Workplane(plane).circle(wire/2).sweep(cq.Workplane().newObject([path]),isFrenet=True).val()
  s=s.rotate((0,0,0),(1,0,0),-90).translate((0,wire/2,0))
  assert s.isValid();_spring_cache[length]=s
 return _spring_cache[length]

def init_parts():
 if not PARTS:
  PARTS.update({'B05_smooth_base':make_base(),'A06_smooth_anchor':make_anchor()})

def module_items(x=0,origin=14,gap=2,reference=True):
 init_parts();items=[]
 def add(n,s,c):items.append((n,s,c))
 steel=cq.Color(.76,.77,.79)
 add('B05_smooth_base',PARTS['B05_smooth_base'].translate((x,0,0)),COLORS['B05_smooth_base'])
 add('A06_smooth_anchor',PARTS['A06_smooth_anchor'].translate((x,origin,3+gap)),COLORS['A06_smooth_anchor'])
 length,stack,tip=clamp_hardware(gap)
 for xx in (-6,6):
  add('clamp_washer_stack',washer(6,3.3,stack,(x+xx,54,11+gap)),steel)
  add('clamp_M3',screw_z(x+xx,54,11+gap+stack,length),steel)
 for xx in (-HEIGHT_X,HEIGHT_X):
  for yy in HEIGHT_Y:
   length,_=jack_hardware(gap)
   add('height_M4',screw_z(x+xx,origin+yy,3+length,length,False,4),steel)
 axis=7+gap
 add('intonation_M4x30',screw_y(x,81.5,axis,30),steel)
 add('intonation_washer',washer(8,4.5,.5,(x,81,axis),(0,1,0)),steel)
 add('compression_spring_REFERENCE',spring(25-origin).translate((x,origin+50,axis)),steel)
 if reference:
  add('string_reference',cyl(1.1,120,(x,origin+6,8+gap),(0,-1,0)),cq.Color(.85,.85,.85))
  ball=cyl(6,4.75,(x-2.375,origin+9,8+gap),(1,0,0)).cut(cyl(2.4,4.75,(x-2.375,origin+9,8+gap),(1,0,0)))
  add('ball_reference_ONLY',ball,cq.Color(.72,.63,.43))
  add('piezo_envelope_ONLY',cyl(12,.7,(x,20,.5)),cq.Color(.7,.38,.13))
 return items

def check():
 init_parts();records=[];walls=[]
 # Major-diameter hole plus 0.8 mm radial guard: cylindrical material test.
 # End chamfers and external rounding are excluded from the axial guard.
 for x in (-HEIGHT_X,HEIGHT_X):
  for y in HEIGHT_Y:
   guard=cyl(5.6,6,(x,y,1)).cut(cyl(4,6,(x,y,1)))
   absent=guard.cut(ANCHOR_BEFORE_TAPS).Volume()
   assert absent<1e-6,('height major-diameter wall',x,y,absent)
   walls.append({'xy':[x,y],'guard_radial_mm':.8,'axial_span_mm':[1,7],'missing_material_mm3':absent})
 a=PARTS['A06_smooth_anchor']
 rear_guard=cyl(5.6,8,(0,50,4),(0,-1,0)).cut(cyl(4,8,(0,50,4),(0,-1,0)))
 missing=rear_guard.cut(a).Volume()
 assert missing<1e-6,('rear full-ring thread land',missing)
 # Tapped diameter is shown as pilot diameter in STEP. Restrict allowed
 # screw intersections to cylindrical mating regions, not entire parts.
 anchor_clear=a
 for x in (-HEIGHT_X,HEIGHT_X):
  for y in HEIGHT_Y:anchor_clear=anchor_clear.cut(cyl(4,8,(x,y,0)))
 anchor_clear=anchor_clear.cut(cyl(4,12,(0,50,4),(0,-1,0)))
 base_clear=PARTS['B05_smooth_base']
 for x in (-6,6):base_clear=base_clear.cut(cyl(3,6,(x,54,0)))
 for cy in (9,10,12,14):
  assert cyl(6,4.75,(-2.375,cy,5),(1,0,0)).intersect(a).Volume()<1e-6,('ball',cy)
 for gap in [i/100 for i in range(1201)]:clamp_hardware(gap);jack_hardware(gap)
 for q,g in itertools.product((8,14,20),(0,6,12)):
  placed=module_items(0,q,g,False)
  base,anchor=placed[0][1],placed[1][1]
  assert base.intersect(anchor).Volume()<1e-6,('parts',q,g)
  clear=[base_clear,anchor_clear.translate((0,q,3+g))]
  for n,h,_ in placed[2:]:
   for i,part in enumerate(clear):
    v=h.intersect(part).Volume();assert v<1e-5,(q,g,n,i,v)
  # Full OD envelope tests spring clearance, independent of visual helix.
  spring_envelope=cyl(6,25-q,(0,q+50,7+g),(0,1,0))
  for i,part in enumerate((base,anchor)):
   v=spring_envelope.intersect(part).Volume();assert v<1e-5,('spring OD envelope',q,g,i,v)
  tip=51.5-q;working=25-q;overlap=min(q-1.5,8)
  assert overlap>=6.5-1e-8 and tip>=31.5-1e-8
  assert 71.5-(q+50)>=1.5-1e-8
  length,stack,clamp_tip=clamp_hardware(g)
  records.append({'q':q,'g':g,'string_axis_height':8+g,'spring_length':working,
    'spring_force_reference_N':(20-working)*.098,'spring_solid_height_margin':working-3.85,
    'rear_full_land_overlap_mm':overlap,'rear_bolt_penetration_mm':q-1.5,
    'plain_shank_gap':71.5-(q+50),'rear_screw_tip_local_y':tip,
    'clamp_length':length,'clamp_washer_stack':stack,'clamp_tip_z':clamp_tip,
    'clamp_thread_engagement':6-clamp_tip,'height_screw_length':jack_hardware(g)[0],
    'height_thread_engagement':jack_hardware(g)[1]})
 rear_items=module_items(0,14,0,False);driver=cyl(6,35,(0,93,5))
 for n,h,_ in rear_items:assert driver.intersect(h).Volume()<1e-5,('rear driver',n)
 return records,walls

def build():
 records,walls=check()
 for n,s in PARTS.items():
  assert s.isValid() and len(s.Solids())==1
  cq.exporters.export(s,str(STEP/(n+'.step')))
  cq.exporters.export(s,str(STL/(n+'.stl')),tolerance=.035,angularTolerance=.12)
 assembly=cq.Assembly(name='MB4_revision_G_mm');manifest=[]
 for i,(x,q,g) in enumerate(zip([-28.5,-9.5,9.5,28.5],[18,16,14,12],[5,4,3,2])):
  for j,(n,s,c) in enumerate(module_items(x,q,g)):
   name=f'S{i+1}_{n}_{j}';assembly.add(s,name=name,color=c)
   f=STL/(name+'.stl');cq.exporters.export(s,str(f),tolerance=.045,angularTolerance=.12)
   manifest.append({'name':name,'file':str(f.relative_to(ROOT)),'color':list(c.toTuple()[:3])})
 assembly.export(str(STEP/'MB4_assembly.step'))
 (ROOT/'scene_manifest.json').write_text(json.dumps(manifest,indent=2))
 imported={}
 for n,old in PARTS.items():
  s=cq.importers.importStep(str(STEP/(n+'.step'))).val()
  assert s.isValid() and abs(s.Volume()-old.Volume())<old.Volume()*1e-6
  bb=s.BoundingBox();imported[n]={'volume_mm3':s.Volume(),'bbox_mm':[bb.xlen,bb.ylen,bb.zlen], 'material':'6061-T6'}
 s=cq.importers.importStep(str(STEP/'MB4_assembly.step')).val()
 assert s.isValid() and len(s.Solids())==len(manifest)
 (ROOT/'scene_manifest.json').write_text(json.dumps(manifest,indent=2))
 (ROOT/'geometry_check.json').write_text(json.dumps({'revision':'G','units':'mm','valid_solids':imported,
  'assembly_solids':len(manifest),'limits':records,'height_tap_wall_guards':walls,
  'rear_tap_guard_radial_mm':.8,'rear_tap_guard_axial_span_y':[42,50],
  'hardware_interference':'passed; only major-diameter cylinders removed at designated tapped holes',
  'spring_full_D6_envelope':'passed at all 9 travel/height conditions',
  'rear_mounts':{'xy':[[0,93]],'driver_clearance':'D6 x35 mm passed'},
  'height_and_clamp_sweep':'1201 heights checked across g=0..12',
  'normal_q_range':[8,18],'nominal_mechanical_q_range':[8,20],
  'thread_wall_nominal_minimum_bulk_mm':1.05,
  'not_verified':['actual supplier CNC acceptance/price','physical strength/fatigue',
    'actual string ball/winding fit and string centre at contact','specific bass fit',
    'piezo pickup isolation/performance','actual spring free-length tolerance and ends'],
  'spring_model':'visual reference, constant pitch; catalogue envelope separately checked'},indent=2))
 print(json.dumps(imported,indent=2));print('Rev G: thread wall / nine assembly conditions / STEP roundtrip passed',flush=True)
if __name__=='__main__':build()
