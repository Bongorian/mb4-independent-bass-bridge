"""MB4 Rev K: convex aluminum exterior, protected functional seats and 20mm travel.
Units mm. Threads represented by tap drill holes, specified on matching PDFs.
"""
from pathlib import Path
from OCP.BRepTools import BRepTools
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
 # One smooth swept edge per web; no stacked edge/root decoration.
 if back:
  wp=(cq.Workplane('YZ').moveTo(86.5,3).lineTo(93.5,3).lineTo(93.5,5)
      .bezier([(91.5,5),(87.5,11),(86.5,16)],includeCurrent=True).close())
 else:
  wp=(cq.Workplane('YZ').moveTo(76,3)
      .bezier([(80,3),(83.5,11),(84.5,16)],includeCurrent=True)
      .lineTo(84.5,3).close())
 return wp.extrude(3).translate((x,0,0)).val()

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
 # Integral web roots have no separate groove under the support.
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
 # Single swept web profiles; outer rounding follows the free rim.
 arcs=[e for e in b.Edges() if e.geomType()=='CIRCLE' and e.Center().z>18 and e.BoundingBox().ylen<1e-6]
 assert len(arcs)==2
 b=b.fillet(P['tower_top_radius'],arcs).clean()
 diagonals=[e for e in b.Edges() if e.geomType() in ('BSPLINE','BEZIER') and e.BoundingBox().xlen<1e-6
             and abs(abs(e.Center().x)-9)<1e-6 and e.BoundingBox().ylen>2 and e.BoundingBox().zlen>5]
 assert len(diagonals)==4,('outside diagonals',len(diagonals))
 b=b.fillet(P['rib_exposed_edge_radius'],diagonals).clean()
 # Inner swept rims: C0.2 MAX deburr on drawing, not a fragile tiny
 # rolling blend at the tangent root. Outer R0.8 follows the free plate rim.
 assert b.isValid(),'streamlined swept webs and arch'
 b=round_rear_rim(b)
 print('base flange',b.isValid(),flush=True)
 for x in (-6,6):b=b.fuse(finished_blank(6,6,4,1.5,0,x=x,y=45,z=2,top=.4))
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
 # Plain nose and straight sides: no pinched waist near the height holes.
 return (cq.Workplane('XY').moveTo(-7,7).threePointArc((0,0),(7,7))
  .bezier([(7,9),(9,9),(9,11)],includeCurrent=True).lineTo(9,52)
  .threePointArc((8.121320344,54.121320344),(6,55)).lineTo(-6,55)
  .threePointArc((-8.121320344,54.121320344),(-9,52)).lineTo(-9,11)
  .bezier([(-9,9),(-7,9),(-7,7)],includeCurrent=True).close())

def streamlined_roof_blank():
 # Exact tensor-product Bezier roof. Continuous tangent transitions avoid
 # intersecting domes, a raised spine, or a separate fillet along a crease.
 from OCP.Geom import Geom_BezierSurface
 from OCP.TColgp import TColgp_Array2OfPnt
 from OCP.gp import gp_Pnt
 from OCP.BRepBuilderAPI import BRepBuilderAPI_MakeFace,BRepBuilderAPI_Sewing
 def roof_face(ys,gs):
  poles=TColgp_Array2OfPnt(1,3,1,len(ys))
  for i,(x,f) in enumerate(zip((-9,0,9),(0,2,0)),1):
   for j,(y,g) in enumerate(zip(ys,gs),1):
    poles.SetValue(i,j,gp_Pnt(x,y,8+g*(-.2+2.7*f)))
  return cq.Face(BRepBuilderAPI_MakeFace(Geom_BezierSurface(poles),1e-7).Face())
 def face(wp):return cq.Face.makeFromWires(wp.val())
 faces=[roof_face([0,21],[1,1]),roof_face([21,21+6.8/3,21+13.6/3,27.8],[1,1,0,0]),
        face(cq.Workplane('XY').center(0,41.4).rect(18,27.2).wires()).translate((0,0,8)),
        face(cq.Workplane('XY').center(0,27.5).rect(18,55).wires())]
 side=(cq.Workplane('YZ').moveTo(0,0).lineTo(55,0).lineTo(55,8).lineTo(27.8,8)
       .bezier([(21+13.6/3,8),(21+6.8/3,7.8),(21,7.8)],includeCurrent=True)
       .lineTo(0,7.8).close())
 for x in (-9,9):faces.append(face(side).translate((x,0,0)))
 front=(cq.Workplane('XZ').moveTo(-9,0).lineTo(9,0).lineTo(9,7.8)
        .bezier([(0,13.2),(-9,7.8)],includeCurrent=True).close())
 rear=cq.Workplane('XZ').moveTo(-9,0).lineTo(9,0).lineTo(9,8).lineTo(-9,8).close()
 faces.extend([face(front),face(rear).translate((0,55,0))])
 sew=BRepBuilderAPI_Sewing(1e-6)
 for f in faces:sew.Add(f.wrapped)
 sew.Perform()
 shell=cq.Shape.cast(sew.SewedShape())
 b=cq.Solid.makeSolid(shell).fix()
 assert b.isValid() and len(b.Solids())==1, 'sewn Bezier roof blank'
 assert abs(b.Volume()-8622.72)<1e-3,('roof analytic volume',b.Volume())
 return b

HEIGHT_X=5.5
HEIGHT_Y=(19,24)
ANCHOR_BEFORE_TAPS=None
def make_anchor():
 global ANCHOR_BEFORE_TAPS
 # One continuous Bezier roof with tangent transition to the low rear deck.
 profile=streamlined_roof_blank()
 b=anchor_outline().extrude(12).val().intersect(profile).clean()
 top=[e for e in b.Edges() if e.BoundingBox().zmin>7.79]
 b=b.fillet(.7,top).clean()
 bottom=[e for e in b.Edges() if e.BoundingBox().zmax<1e-6]
 b=b.fillet(.6,bottom).clean()
 b=b.cut(rounded_pocket(8,11,12,y=11.5,z=2,r=1.5))
 # Round-ended slot: the rear vertical corners are no longer square.
 slot=cq.Workplane('XY').center(0,10).slot2D(24,3.4,90).extrude(10).translate((0,0,3.3)).val()
 b=b.cut(slot)
 for x in (-6,6):b=b.cut(rounded_pocket(6,27,3,x=x,y=41.5,z=0,r=1.5))
 # Rear screw moves through this open underside window after the short tap.
 b=b.cut(rounded_pocket(4.4,22,6.3,y=36,z=0,r=1.5))
 for x in (-6,6):
  slot=cq.Workplane('XY').center(x,41).slot2D(23.4,3.4,90).extrude(8).val()
  b=b.cut(slot)
 ANCHOR_BEFORE_TAPS=b.clean()
 for x in (-HEIGHT_X,HEIGHT_X):
  for y in HEIGHT_Y:
   b=b.cut(cyl(3.3,12,(x,y,0)))
   b=b.cut(cyl(4.2,5,(x,y,8))) # Flat entry retains the original 8mm tap depth.
 # Standard tap entering from Y55; drill breaks fully into the underside window.
 b=b.cut(cyl(3.3,12,(0,55,4),(0,-1,0)))
 # Convex roof meets the string cutout; deburr lips C0.1 max on drawing.
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
COLORS={'B09_streamlined_base':cq.Color(.38,.45,.50),'A09_streamlined_anchor':cq.Color(.63,.68,.72)}
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
  PARTS.update({'B09_streamlined_base':make_base(),'A09_streamlined_anchor':make_anchor()})

def module_items(x=0,origin=2,gap=2,reference=True):
 init_parts();items=[]
 def add(n,s,c):items.append((n,s,c))
 steel=cq.Color(.76,.77,.79)
 add('B09_streamlined_base',PARTS['B09_streamlined_base'].translate((x,0,0)),COLORS['B09_streamlined_base'])
 add('A09_streamlined_anchor',PARTS['A09_streamlined_anchor'].translate((x,origin,3+gap)),COLORS['A09_streamlined_anchor'])
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
  assert bore.intersect(PARTS['B09_streamlined_base']).Volume()<1e-6,('M3 actual through bore',x,36)
  guard=cyl(4.6,5.2,(x,36,.4)).cut(cyl(3,5.2,(x,36,.4)))
  assert guard.cut(PARTS['B09_streamlined_base']).Volume()<1e-6,('M3 threaded boss wall',x,36)
 for sign in (-1,1):
  probe=box(.15,14.5,.15,x=sign*8.85,y=66.5,z=2.75)
  absent=probe.cut(PARTS['B09_streamlined_base']).Volume()
  assert absent<1e-6,('continuous web/base root material band',sign,absent)
 # Major-diameter hole plus 0.8 mm radial guard: cylindrical material test.
 # End chamfers and external rounding are excluded from the axial guard.
 for x in (-HEIGHT_X,HEIGHT_X):
  for y in HEIGHT_Y:
   guard=cyl(5.6,6,(x,y,1)).cut(cyl(4,6,(x,y,1)))
   absent=guard.cut(ANCHOR_BEFORE_TAPS).Volume()
   assert absent<1e-6,('height major-diameter wall',x,y,absent)
   walls.append({'xy':[x,y],'guard_radial_mm':.8,'axial_span_mm':[1,7],'missing_material_mm3':absent})
 a=PARTS['A09_streamlined_anchor']
 rear_guard=cyl(5.6,8,(0,55,4),(0,-1,0)).cut(cyl(4,8,(0,55,4),(0,-1,0)))
 missing=rear_guard.cut(a).Volume()
 assert missing<1e-6,('rear full-ring thread land',missing)
 # Tapped diameter is shown as pilot diameter in STEP. Restrict allowed
 # screw intersections to cylindrical mating regions, not entire parts.
 anchor_clear=a
 for x in (-HEIGHT_X,HEIGHT_X):
  for y in HEIGHT_Y:anchor_clear=anchor_clear.cut(cyl(4,8,(x,y,0)))
 anchor_clear=anchor_clear.cut(cyl(4,12,(0,55,4),(0,-1,0)))
 base_clear=PARTS['B09_streamlined_base']
 for x in (-6,6):base_clear=base_clear.cut(cyl(3,6,(x,36,0)))
 for cy in (9,10,12,14):
  assert cyl(6,4.75,(-2.375,cy,5),(1,0,0)).intersect(a).Volume()<1e-6,('ball',cy)
 for gap in [i/100 for i in range(1201)]:clamp_hardware(gap);jack_hardware(gap)
 for q,g in itertools.product((-15,-5,5),(0,6,12)):
  for x in (-HEIGHT_X,HEIGHT_X):
   for yy in HEIGHT_Y:
    foot=cyl(4,.1,(x,q+yy,2.9))
    assert foot.cut(PARTS['B09_streamlined_base']).Volume()<1e-6,('height foot full support',q,x,yy)
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
 # Access mouths must remain separate, with 0.5mm radial floor material.
 for xx in (-HEIGHT_X,HEIGHT_X):
  for cy in HEIGHT_Y:
   ring=cyl(5.2,.04,(xx,cy,8.01)).cut(cyl(4.2,.04,(xx,cy,8.01)))
   absent=ring.cut(a).Volume()
   assert absent<1e-6,('closed access mouth floor ring',xx,cy,absent)
 # Contact witnesses on protected seats, excluding the screw clearance slots.
 for cy in range(31,52,5):
  for xx in (-6,6):
   for side in (-1,1):
    witness=box(.4,1,.05,x=xx+side*2.0,y=cy-.5,z=7.95)
    assert witness.cut(a).Volume()<1e-6,('flat M3 washer track contact',xx,cy,side)
 for g in (0,6,12):
  for x in (-3,3):
   witness=box(.2,.05,.2,x=x,y=76.45,z=6.9+g)
   assert witness.cut(PARTS['B09_streamlined_base']).Volume()<1e-6,('rear washer flat seat',x,g)
  for x in (-2.7,2.7):
   witness=box(.1,.05,.1,x=x,y=70.5,z=6.95+g)
   assert witness.cut(PARTS['B09_streamlined_base']).Volume()<1e-6,('spring flat seat',x,g)
 rear_items=module_items(0,2,0,False);driver=cyl(6,35,(0,81,5))
 assert driver.intersect(PARTS['B09_streamlined_base']).Volume()<1e-5,('rear driver with anchor/intonation screw removed')
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
 assert tool.intersect(PARTS['B09_streamlined_base']).Volume()<1e-6
 return records,walls

def build():
 records,walls=check()
 for n,s in PARTS.items():
  assert s.isValid() and len(s.Solids())==1
  cq.exporters.export(s,str(STEP/(n+'.step')))
  cq.exporters.export(s,str(STL/(n+'.stl')),tolerance=.035,angularTolerance=.12)
 assembly=cq.Assembly(name='MB4_revision_K_mm');manifest=[]
 for i,(x,q,g) in enumerate(zip([-28.5,-9.5,9.5,28.5],[3,1,-1,-3],[5,4,3,2])):
  for j,(n,s,c) in enumerate(module_items(x,q,g)):
   name=f'S{i+1}_{n}_{j}';assembly.add(s,name=name,color=c)
   f=STL/(name+'.stl');cq.exporters.export(s,str(f),tolerance=.045,angularTolerance=.12)
   manifest.append({'name':name,'file':str(f.relative_to(ROOT)),'color':list(c.toTuple()[:3])})
 assembly.export(str(STEP/'MB4_assembly.step'))
 (ROOT/'scene_manifest.json').write_text(json.dumps(manifest,indent=2))
 verify_exports(records,walls,manifest)

def verify_exports(records,walls,manifest):
 imported={};roundtrip=[]
 for n,old in PARTS.items():
  s=cq.importers.importStep(str(STEP/(n+'.step'))).val()
  print('STEP_CHECK',n,s.isValid(),s.Volume(),old.Volume(),abs(s.Volume(1e-8)-old.Volume(1e-8))/old.Volume(1e-8),flush=True)
  # Curved fillet trims can change the numerical volume integration after STEP
  # reparametrisation. Verify actual solids by two-way Boolean difference too.
  difference_a=old.cut(s);difference_b=s.cut(old)
  assert difference_a.isValid() and difference_b.isValid()
  removed=difference_a.Volume(1e-8);added=difference_b.Volume(1e-8)
  relative=abs(s.Volume(1e-8)-old.Volume(1e-8))/old.Volume(1e-8)
  # Cached STL triangulations inflate bounding boxes at mesh tolerance.
  # Remove only the mesh cache before the exact B-rep comparison.
  BRepTools.Clean_s(old.wrapped);BRepTools.Clean_s(s.wrapped)
  a,b=old.BoundingBox(),s.BoundingBox()
  bbox_difference=max(abs(getattr(a,k)-getattr(b,k)) for k in ('xmin','xmax','ymin','ymax','zmin','zmax'))
  # Volume integration on trimmed spline faces remains a diagnostic:
  # Tight integration tolerance can still leave numerical differences.
  # Shape equivalence is gated by the strict Boolean
  # differences and exact B-rep bounds, rather than this mass estimate.
  assert s.isValid() and math.isfinite(relative) and s.Volume()>0
  assert abs(removed)<1e-6 and abs(added)<1e-6 and bbox_difference<1e-5,(n,removed,added,bbox_difference)
  roundtrip.append({'part':n,'relative_volume_integration_difference':relative,
    'native_minus_step_volume_mm3':removed,'step_minus_native_volume_mm3':added,
    'maximum_bbox_coordinate_difference_mm':bbox_difference})
  bb=s.BoundingBox();imported[n]={'volume_mm3':s.Volume(1e-8),'bbox_mm':[bb.xlen,bb.ylen,bb.zlen], 'material':'6061-T6'}
 s=cq.importers.importStep(str(STEP/'MB4_assembly.step')).val()
 assert s.isValid() and len(s.Solids())==len(manifest)
 (ROOT/'scene_manifest.json').write_text(json.dumps(manifest,indent=2))
 (ROOT/'geometry_check.json').write_text(json.dumps({'revision':'K','units':'mm','valid_solids':imported,
  'assembly_solids':len(manifest),'step_roundtrip':roundtrip,'limits':records,'height_tap_wall_guards':walls,
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
  'convex_surfaces':{'anchor_roof':'single Bezier roof: front parabolic XZ7.8+2.7*(1-(X/9)^2); tangent rampY21..27.8 to full-width deckZ8; no spine or intersecting domes','wall':'single R9 arch, thickness6, exposed arch rimsR1.2; no added seat bosses','anchor_max_height_mm':10.5,'height_access_mouths':'D4.2, axesX+/-5.5,Y19/24; closed floor ring radial0.5 passed','functional_contact_witnesses':'M3 tracks at5 positions; M4 washer and spring lands at3 heights passed'},
  'cosmetic_edge_radii_mm':{'arch':P['tower_top_radius'],'rib_outer':P['rib_exposed_edge_radius'],'rib_inner':P['rib_inside_edge_radius'],'free_front_rim':P['base_front_top_edge_radius'],'anchor_top':P['anchor_front_top_edge_radius'],'anchor_bottom':P['anchor_bottom_edge_radius'],'crown_top':P['anchor_crown_top_radius'],'crown_root':P['anchor_crown_root_radius']},
  'not_verified':['actual supplier CNC acceptance/price','physical strength/fatigue',
    'actual string ball/winding fit and string centre at contact','specific bass fit',
    'piezo pickup isolation/performance','actual spring free-length tolerance and ends'],
  'spring_model':'visual reference, constant pitch; catalogue envelope separately checked'},indent=2))
 print(json.dumps(imported,indent=2));print('Rev K: thread wall / nine assembly conditions / STEP roundtrip passed',flush=True)
if __name__=='__main__':
 import sys
 if '--verify-existing' in sys.argv:
  records,walls=check()
  manifest=json.loads((ROOT/'scene_manifest.json').read_text())
  verify_exports(records,walls,manifest)
 else:build()
