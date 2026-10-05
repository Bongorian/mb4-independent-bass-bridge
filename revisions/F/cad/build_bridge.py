"""MB4 Rev F, mm, CadQuery 2.8.0. Threads are tap-drill placeholders.
Two CNC solids/string: base and integrated anchor/slider. Spring geometry is
illustrative (constant pitch; closed ends simplified), catalogue envelope exact.
"""
from pathlib import Path
import json, itertools, math
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
  h=cyl(5.5,3,(x,y,shoulder)).cut(cq.Workplane('XY').polygon(6,2.8868).extrude(1.6).translate((x,y,shoulder+1.4)).val())
  return s.fuse(h)
 return s.cut(cq.Workplane('XY').polygon(6,1.732 if diameter==3 else 2.3094).extrude(1.5).translate((x,y,shoulder-1.5)).val())
def screw_y(x,y,z,length):
 # M4 x 0.7, standard headD7 H4 / socket3.
 s=cyl(4,length,(x,y,z),(0,-1,0))
 head=cyl(7,4,(x,y,z),(0,1,0))
 socket=cq.Workplane('XZ').polygon(6,3.4641).extrude(2.2).translate((x,y+4,z)).val()
 return s.fuse(head.cut(socket))
def gusset(x,back=False):
 # Quadratic Beziers: simple extruded YZ curves, accessible by 3-axis milling.
 wp=cq.Workplane('YZ')
 if back:
  wp=wp.moveTo(73,3).lineTo(80,3).lineTo(80,5).bezier([(76.5,5),(73,16)],includeCurrent=True).close()
 else:
  wp=wp.moveTo(60.5,3).bezier([(63.75,3),(67,16)],includeCurrent=True).lineTo(67,3).close()
 s=wp.extrude(3).translate((x,0,0)).val()
 curved=[e for e in s.Edges() if e.geomType()=='BEZIER' or e.geomType()=='BSPLINE']
 assert len(curved)==2,[(e.geomType(),e.Length()) for e in s.Edges()]
 return s.fillet(.6,curved)
def make_wall():
 # True R9 crown in XZ, extruded 6 along Y. No free-form loft.
 wp=cq.Workplane('XZ').moveTo(-9,3).lineTo(9,3).lineTo(9,16).threePointArc((0,25),(-9,16)).close().extrude(6).translate((0,73,0))
 s=wp.val()
 perimeter=[e for e in s.Edges() if e.BoundingBox().ylen<1e-6 and e.Center().z>3.01]
 return s.fillet(.8,perimeter)
def rear_flange():
 # Smooth cubic ramp Z3 atY78 to Z5 atY80, then flat screw seats toY90.
 s=cq.Workplane('YZ').moveTo(78,2).lineTo(78,3).bezier([(78+2/3,3),(78+4/3,5),(80,5)],includeCurrent=True).lineTo(90,5).lineTo(90,2).close().extrude(18).translate((-9,0,0)).val()
 return s.intersect(rounded_pocket(18,90,5,y=45,r=4))
def round_rear_rim(b):
 # Analytic R0.6 rolling rim. Explicit cylinders/tori avoid a kernel failure at
 # the tangent junction of the cubic ramp and the rear curved ribs.
 r=.6;zc=5-r
 for sign in (-1,1):
  outer=box(r,6,r,x=sign*(9-r/2),y=80,z=zc)
  keep=cyl(2*r,6,(sign*(9-r),80,zc),(0,1,0))
  b=b.cut(outer.cut(keep))
 outer=box(10,r,r,y=90-r,z=zc)
 keep=cyl(2*r,10,(-5,90-r,zc),(1,0,0))
 b=b.cut(outer.cut(keep))
 for sign in (-1,1):
  center=V(sign*5,86,zc)
  ring=cyl(8,r,center.toTuple()).cut(cyl(8-2*r,r,center.toTuple()))
  torus=cq.Solid.makeTorus(4-r,r,center,V(0,0,1))
  quarter=box(4,4,r,x=sign*7,y=86,z=zc)
  b=b.cut(ring.cut(torus).intersect(quarter))
 return b.clean()
STRUCTURAL_CORE=None
def make_base():
 global STRUCTURAL_CORE
 b=finished_blank(18,90,3,4,.2,top=.5)
 b=b.fuse(make_wall())
 for xx in (-9,6):b=b.fuse(gusset(xx)).fuse(gusset(xx,True))
 b=b.clean()
 roots=[e for e in b.Edges() if e.geomType()=='LINE' and abs(e.Center().y-67)<1e-6 and abs(e.Center().z-3)<1e-6 and e.Length()>10]
 assert len(roots)==1,[(e.Center().toTuple(),e.Length()) for e in roots]
 b=b.fillet(.8,roots).clean()
 # Cantilever comparison excludes rear screw flange and clamp pads.
 core=b
 b=b.fuse(rear_flange()).clean()
 b=round_rear_rim(b)
 for xx in (-6,6):b=b.fuse(finished_blank(6,6,3,1,0,x=xx,y=43,z=3,top=.2))
 # One front fixing and one central rear fixing, full flat counterseat lands.
 for x,y,h in [(0,5,3),(0,85,5)]:
  b=b.cut(cyl(3.8,h,(x,y,0)))
  b=b.cut(cq.Solid.makeCone(1.9,3.5,1.6,V(x,y,h-1.6),V(0,0,1)))
 for x in (-6,6):b=b.cut(cyl(2.5,6,(x,46,0)))
 b=b.cut(cyl(12.5,1.5,(0,20,0)))
 b=b.cut(box(9,2.2,1.2,x=4.5,y=18.9))
 slot=cq.Workplane('XZ').center(0,13).slot2D(16.5,4.5,90).extrude(6).translate((0,73,0)).val()
 b=b.cut(slot);STRUCTURAL_CORE=core.cut(slot).clean()
 b=b.cut(box(9,1,1,y=73,z=2))
 return b.clean()
def anchor_outline():
 # R7 round nose, tangent cubic waist, R3 rear corners. Width<=18.
 return (cq.Workplane('XY').moveTo(-7,7).threePointArc((0,0),(7,7))
  .bezier([(7,9),(9,9),(9,11)],includeCurrent=True)
  .bezier([(9,14),(8.6,15),(8.6,18)],includeCurrent=True)
  .bezier([(8.6,21),(9,22),(9,25)],includeCurrent=True).lineTo(9,39)
  .threePointArc((8.121320344,41.121320344),(6,42)).lineTo(-6,42)
  .threePointArc((-8.121320344,41.121320344),(-9,39)).lineTo(-9,25)
  .bezier([(-9,22),(-8.6,21),(-8.6,18)],includeCurrent=True)
  .bezier([(-8.6,15),(-9,14),(-9,11)],includeCurrent=True)
  .bezier([(-9,9),(-7,9),(-7,7)],includeCurrent=True).close())
def make_anchor():
 # Low body with integrated circular crown. No separate pin or extra CNC part.
 b=anchor_outline().extrude(8).faces('>Z').edges().fillet(.5).faces('<Z').edges().fillet(.3).val()
 crown=(cq.Workplane('XY').center(0,9).circle(6).extrude(2.4)
        .faces('>Z').edges().fillet(.8).translate((0,0,7.6)).val())
 b=b.fuse(crown).clean()
 roots=[e for e in b.Edges() if e.geomType()=='CIRCLE' and abs(e.Center().z-8)<1e-6 and e.Length()>30]
 assert len(roots)==1,[(e.geomType(),e.Center().toTuple(),e.Length()) for e in roots]
 b=b.fillet(.4,roots).clean()
 # A short top-open cradle leaves a larger rear web before the M4 drill.
 b=b.cut(rounded_pocket(8,11,8,y=11.5,z=2,r=1.5))
 b=b.cut(box(3.4,22,6.7,z=3.3))
 for x in (-5,5):
  for y in (15,20.5):b=b.cut(cyl(3.3,8,(x,y,0)))
 for xx in (-6,6):b=b.cut(rounded_pocket(6,20,3,x=xx,y=32,z=0,r=1))
 for x in (-6,6):
  slot=cq.Workplane('XY').center(x,32).slot2D(15.4,3.4,90).extrude(8).val()
  b=b.cut(slot)
 b=b.cut(cyl(3.3,22,(0,42,4),(0,-1,0)))
 b=b.cut(cq.Solid.makeCone(1.65,0,1.,V(0,20,4),V(0,-1,0)))
 lips=[e for e in b.Edges() if e.geomType()=='LINE' and abs(e.Center().z-10)<1e-6
       and abs(abs(e.Center().x)-1.7)<1e-6 and e.Length()>.5]
 assert len(lips)==2,[(e.geomType(),e.Center().toTuple(),e.Length()) for e in lips]
 return b.fillet(.25,lips).clean()
def jack_hardware(gap):
 # 8-mm supporting body: common flat-point lengths keep 4+ mm engagement.
 length=8 if gap<=4 else (12 if gap<=8 else 16)
 engagement=length-gap
 assert 4-1e-8<=engagement<=8+1e-8
 return length,engagement
PARTS={'B04_single_rear_base':make_base(),'A05_crown_anchor':make_anchor()}
COLORS={'B04_single_rear_base':cq.Color(.32,.39,.43),'A05_crown_anchor':cq.Color(.72,.53,.23)}
_spring_cache={}
def spring(length):
 if length not in _spring_cache:
  wire=P['spring_wire_diameter'];radius=(P['spring_outer_diameter']-wire)/2
  h=length-wire;pitch=h/P['spring_total_turns_reference']
  path=cq.Wire.makeHelix(pitch,h,radius)
  plane=cq.Plane(origin=(radius,0,0),normal=(0,1,pitch/(2*math.pi*radius)))
  s=cq.Workplane(plane).circle(wire/2).sweep(cq.Workplane().newObject([path]),isFrenet=True).val()
  s=s.rotate((0,0,0),(1,0,0),-90).translate((0,wire/2,0))
  assert s.isValid()
  _spring_cache[length]=s
 return _spring_cache[length]
def clamp_hardware(gap):
 # Standard lengths. Half-mm washer stacks leave tips 0.2..0.7 above body.
 length=next(v for v in (12,16,20,25) if v>=11+gap-1e-8)
 stack=.5*math.ceil((length-(11+gap)+.2)/.5-1e-8)
 tip=11+gap+stack-length
 assert .19999<=tip<=.70001
 return length,stack,tip
def module_items(x=0,origin=14,gap=2,reference=True):
 items=[]
 def add(name,shape,color):items.append((name,shape,color))
 steel=cq.Color(.76,.77,.79)
 add('B04_single_rear_base',PARTS['B04_single_rear_base'].translate((x,0,0)),COLORS['B04_single_rear_base'])
 add('A05_crown_anchor',PARTS['A05_crown_anchor'].translate((x,origin,3+gap)),COLORS['A05_crown_anchor'])
 length,stack,tip=clamp_hardware(gap)
 for xx in (-6,6):
  add('clamp_washer_stack',washer(6,3.3,stack,(x+xx,46,11+gap)),steel)
  add('clamp_M3',screw_z(x+xx,46,11+gap+stack,length),steel)
 for xx in (-5,5):
  for yy in (15,20.5):
   jack_length,_=jack_hardware(gap)
   # Bottom bears Z3; upper end remains at/below anchor top.
   add('height_M4',screw_z(x+xx,origin+yy,3+jack_length,jack_length,False,4),steel)
 axis=7+gap
 add('intonation_M4x30',screw_y(x,73.5,axis,30),steel)
 add('intonation_washer',washer(8,4.5,.5,(x,73,axis),(0,1,0)),steel)
 sl=67-(origin+42)
 add('compression_spring_REFERENCE',spring(sl).translate((x,origin+42,axis)),steel)
 if reference:
  add('string_reference',cyl(1.1,120,(x,origin+6,8+gap),(0,-1,0)),cq.Color(.85,.85,.85))
  ball=cyl(6,4.75,(x-2.375,origin+9,8+gap),(1,0,0)).cut(cyl(2.4,4.75,(x-2.375,origin+9,8+gap),(1,0,0)))
  add('ball_reference_ONLY',ball,cq.Color(.78,.65,.34))
  add('piezo_envelope_ONLY',cyl(12,.7,(x,20,.5)),cq.Color(.7,.38,.13))
 return items
def check():
 records=[]
 # Rear driver access: D6 envelope, even with all adjustment hardware fitted.
 rear_items=module_items(0,14,0,False)
 for x in (0,):
  tool=cyl(6,35,(x,85,5))
  for name,shape,_ in rear_items:
   assert tool.intersect(shape).Volume()<1e-5,('rear driver access',x,name)
 for cy in (9,10,12,14):
  ball=cyl(6,4.75,(-2.375,cy,5),(1,0,0))
  assert ball.intersect(PARTS['A05_crown_anchor']).Volume()<1e-6,('ball path',cy)
 for g in [i/100 for i in range(1201)]:
  clamp_hardware(g);jack_hardware(g)
 for q,g in itertools.product((8,14,20),(0,6,12)):
  placed=module_items(0,q,g,False)
  solids=[s for n,s,c in placed[:2]]
  inter=solids[0].intersect(solids[1]).Volume()
  assert inter<1e-6,(q,g,'CNC interference',inter)
  for name,hardware,_ in placed[2:]:
   for i,part in enumerate(solids):
    mating=(i==1 and name in ('height_M4','intonation_M4x30')) or (i==0 and name=='clamp_M3')
    if not mating:
     volume=hardware.intersect(part).Volume()
     assert volume<1e-5,(q,g,name,i,volume)
  working=25-q;engagement=q-1.5
  assert P['spring_min_working_length']<=working<P['spring_free_length']
  assert working-P['spring_solid_height']>=1.15-1e-6
  assert min(engagement,19.5)>=6.5-1e-6
  # Half-thread M4x30: plain shank ends Y63.5, never enters the tap.
  shank_gap=63.5-(q+42);assert shank_gap>=1.5-1e-6
  # Ball loading centreY14, rearY17; forward-most screw tipY23.5.
  tip_local=43.5-q;assert tip_local>=23.5-1e-6
  length,stack,tip=clamp_hardware(g)
  records.append({'q':q,'g':g,'string_axis_height':8+g,'spring_length':working,
   'spring_force_reference_N':(20-working)*P['spring_rate_n_per_mm'],'solid_height_margin':working-P['spring_solid_height'],
   'intonation_thread_overlap':min(engagement,19.5),'plain_shank_gap':shank_gap,'screw_tip_local_y':tip_local,
   'clamp_length':length,'clamp_washer_stack':stack,'clamp_tip_z':tip,'clamp_thread_engagement':6-tip,'height_screw_length':jack_hardware(g)[0],'height_thread_engagement':jack_hardware(g)[1]})
 return records
def build():
 records=check()
 for n,s in PARTS.items():
  assert s.isValid() and len(s.Solids())==1,n
  cq.exporters.export(s,str(STEP/(n+'.step')))
  cq.exporters.export(s,str(STL/(n+'.stl')),tolerance=.035,angularTolerance=.12)
 a=cq.Assembly(name='MB4_revision_F_mm');manifest=[]
 pitch=P['string_pitch']
 for i,(x,q,g) in enumerate(zip([pitch*k for k in (-1.5,-.5,.5,1.5)],[18,16,14,12],[5,4,3,2])):
  for j,(n,s,c) in enumerate(module_items(x,q,g)):
   name=f'S{i+1}_{n}_{j}';a.add(s,name=name,color=c)
   f=STL/(name+'.stl');cq.exporters.export(s,str(f),tolerance=.05,angularTolerance=.15)
   manifest.append({'name':name,'file':str(f.relative_to(ROOT)),'color':list(c.toTuple()[:3])})
 a.export(str(STEP/'MB4_assembly.step'))
 imported={}
 for n,old in PARTS.items():
  s=cq.importers.importStep(str(STEP/(n+'.step'))).val()
  assert s.isValid() and abs(s.Volume()-old.Volume())<1e-4
  bb=s.BoundingBox();imported[n]={'volume_mm3':s.Volume(),'bbox_mm':[bb.xlen,bb.ylen,bb.zlen]}
 assembly=cq.importers.importStep(str(STEP/'MB4_assembly.step')).val()
 assert assembly.isValid() and len(assembly.Solids())==len(manifest)
 (ROOT/'scene_manifest.json').write_text(json.dumps(manifest,indent=2))
 (ROOT/'geometry_check.json').write_text(json.dumps({'revision':P['revision'],'units':'mm',
  'valid_solids':imported,'assembly_solids':len(manifest),'limits':records,
  'hardware_interference':'passed; mating threads excluded',
  'rear_mounts':{'xy_mm':[[0,85]],'seat_z_mm':5,'driver_clearance':'D6 x35 vertical envelope passed with adjustment hardware present'},
  'front_mount_xy_mm':[0,5],
  'ball_reference':'D6 x thickness4.75 cylinder: 4 cradle positions clear, floorZ2',
  'clamp_tip_sweep':'1201 heights in 0..12: tipsZ0.2..0.7',
  'height_jack_sweep':'1201 heights in 0..12: M4 length8/12/16, engagement4..8; top flush or recessed',
  'anchor_features':{'crown_diameter':12,'crown_center_xy':[0,9],'body_top_z':8,'crown_top_z':10,'height_taps_xy':[[x,y] for x in (-5,5) for y in (15,20.5)],'cradle_y':[6,17]},
  'spring_model':'constant-pitch reference only; verify purchased spring ends and load curve',
  'not_tested':['physical ball/winding fit','strength/fatigue','acoustic/piezo output','specific bass fit']},indent=2))
 print(json.dumps(imported,indent=2));print('9 travel/height conditions passed; assembly valid')
if __name__=='__main__':build()
