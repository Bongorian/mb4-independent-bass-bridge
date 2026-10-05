"""MB4 Rev D, mm, CadQuery 2.8.0. Threads are tap-drill placeholders.
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
def screw_z(x,y,shoulder,length,head=True):
 s=cyl(3,length,(x,y,shoulder-length))
 if head:
  h=cyl(5.5,3,(x,y,shoulder)).cut(cq.Workplane('XY').polygon(6,2.8868).extrude(1.6).translate((x,y,shoulder+1.4)).val())
  return s.fuse(h)
 return s.cut(cq.Workplane('XY').polygon(6,1.732).extrude(1.5).translate((x,y,shoulder-1.5)).val())
def screw_y(x,y,z,length):
 # M4 x 0.7, standard headD7 H4 / socket3.
 s=cyl(4,length,(x,y,z),(0,-1,0))
 head=cyl(7,4,(x,y,z),(0,1,0))
 socket=cq.Workplane('XZ').polygon(6,3.4641).extrude(2.2).translate((x,y+4,z)).val()
 return s.fuse(head.cut(socket))
def gusset(x,back=False):
 points=[(73,3),(76,3),(73,15)] if back else [(63,3),(67,3),(67,15)]
 s=cq.Workplane('YZ').polyline(points).close().extrude(3).translate((x,0,0)).val()
 # Only exposed diagonal edges; leave foot and wall contact faces whole.
 diagonal=[e for e in s.Edges() if e.geomType()=='LINE' and len(e.Vertices())==2
           and abs(e.Vertices()[0].Y-e.Vertices()[1].Y)>1
           and abs(e.Vertices()[0].Z-e.Vertices()[1].Z)>1]
 assert len(diagonal)==2
 return s.fillet(.2,diagonal)
def make_base():
 b=finished_blank(18,82,3,3)
 b=b.fuse(finished_blank(18,6,22,1.0,0,y=67,z=3,top=.8))
 for xx in (-6,6):
  b=b.fuse(finished_blank(6,6,3,1,0,x=xx,y=43,z=3,top=.2))
 for xx in (-9,6):
  b=b.fuse(gusset(xx)).fuse(gusset(xx,True))
 b=b.clean()
 roots=[e for e in b.Edges() if e.geomType()=='LINE'
        and abs(e.Center().y-67)<1e-6 and abs(e.Center().z-3)<1e-6 and e.Length()>10]
 assert len(roots)==1,[(e.Center().toTuple(),e.Length()) for e in roots]
 b=b.fillet(1,roots).clean()
 for y in (4,78):
  b=b.cut(cyl(3.8,3,(0,y,0)))
  b=b.cut(cq.Solid.makeCone(1.9,3.5,1.6,V(0,y,1.4),V(0,0,1)))
 for x in (-6,6):
  b=b.cut(cyl(2.5,6,(x,46,0))) # M3x0.5 through6 reinforced pads
 b=b.cut(cyl(12.5,1.5,(0,20,0)))
 b=b.cut(box(9,2.2,1.2,x=4.5,y=18.9))
 # Vertical capsule: centre axis rises from Z7 to Z19.
 slot=cq.Workplane('XZ').center(0,13).slot2D(16.5,4.5,90).extrude(6).translate((0,73,0)).val()
 b=b.cut(slot)
 # OD8 rear washer clearance at minimum axis Z7.
 b=b.cut(box(9,1,1,y=73,z=2))
 return b.clean()
def make_anchor():
 front=finished_blank(18,22,10,2)
 # overlap the rear tail with the front block to keep one solid, no joint.
 tail=finished_blank(18,22,8,2,y=20)
 b=front.fuse(tail)
 b=b.cut(rounded_pocket(8,16,8,y=14,z=2,r=1.5)) # top-machined open cradle
 b=b.cut(box(3.4,22,6.7,z=3.3))
 # Open cradle accepts ball from above; front shoulder Y6 retains it.
 for x in (-6,6):
  for y in (11,18): b=b.cut(cyl(2.5,10,(x,y,0)))
 # Raised underside tracks clear fixed reinforced pads, keep central spine full.
 for xx in (-6,6):b=b.cut(rounded_pocket(6,20,3,x=xx,y=32,z=0,r=1))
 for x in (-6,6):
  slot=cq.Workplane('XY').center(x,32).slot2D(15.4,3.4,90).extrude(8).val()
  b=b.cut(slot)
 # Tap rear web Y22..42. M4 drill22 + point1.0, tap usable20 minimum.
 b=b.cut(cyl(3.3,22,(0,42,4),(0,-1,0)))
 b=b.cut(cq.Solid.makeCone(1.65,0,1.,V(0,20,4),V(0,-1,0)))
 lips=[e for e in b.Edges() if e.geomType()=='LINE' and abs(e.Center().z-10)<1e-6
       and abs(abs(e.Center().x)-1.7)<1e-6 and e.Length()>5]
 assert len(lips)==2,len(lips)
 b=b.fillet(.2,lips)
 return b.clean()
PARTS={'B02_reinforced_base':make_base(),'A03_strengthened_anchor':make_anchor()}
COLORS={'B02_reinforced_base':cq.Color(.32,.39,.43),'A03_strengthened_anchor':cq.Color(.72,.53,.23)}
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
 add('B02_reinforced_base',PARTS['B02_reinforced_base'].translate((x,0,0)),COLORS['B02_reinforced_base'])
 add('A03_strengthened_anchor',PARTS['A03_strengthened_anchor'].translate((x,origin,3+gap)),COLORS['A03_strengthened_anchor'])
 length,stack,tip=clamp_hardware(gap)
 for xx in (-6,6):
  add('clamp_washer_stack',washer(6,3.2,stack,(x+xx,46,11+gap)),steel)
  add('clamp_M3',screw_z(x+xx,46,11+gap+stack,length),steel)
 for xx in (-6,6):
  for yy in (11,18):
   jack_length=10 if gap<=6 else 16
   # Bottom bears Z3; upper end remains at/below anchor top.
   add('height_M3',screw_z(x+xx,origin+yy,3+jack_length,jack_length,False),steel)
 axis=7+gap
 add('intonation_M4x35',screw_y(x,73.5,axis,35),steel)
 add('intonation_washer',washer(8,4.3,.5,(x,73,axis),(0,1,0)),steel)
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
 for cy in (9,10,12,14):
  ball=cyl(6,4.75,(-2.375,cy,5),(1,0,0))
  assert ball.intersect(PARTS['A03_strengthened_anchor']).Volume()<1e-6,('ball path',cy)
 for g in [i/100 for i in range(1201)]:clamp_hardware(g)
 for q,g in itertools.product((8,14,20),(0,6,12)):
  placed=module_items(0,q,g,False)
  solids=[s for n,s,c in placed[:2]]
  inter=solids[0].intersect(solids[1]).Volume()
  assert inter<1e-6,(q,g,'CNC interference',inter)
  for name,hardware,_ in placed[2:]:
   for i,part in enumerate(solids):
    mating=(i==1 and name in ('height_M3','intonation_M4x35')) or (i==0 and name=='clamp_M3')
    if not mating:
     volume=hardware.intersect(part).Volume()
     assert volume<1e-5,(q,g,name,i,volume)
  working=25-q;engagement=q+3.5
  assert P['spring_min_working_length']<=working<P['spring_free_length']
  assert working-P['spring_solid_height']>=1.85-1e-6
  assert min(engagement,19.5)>=11.5-1e-6
  # Ball loading centreY14, rearY17; forward-most screw tipY18.5.
  tip_local=38.5-q;assert tip_local>=18.5-1e-6
  length,stack,tip=clamp_hardware(g)
  records.append({'q':q,'g':g,'string_axis_height':8+g,'spring_length':working,
   'spring_force_reference_N':(20-working)*.1,'solid_height_margin':working-3.15,
   'intonation_thread_overlap':min(engagement,19.5),'screw_tip_local_y':tip_local,
   'clamp_length':length,'clamp_washer_stack':stack,'clamp_tip_z':tip,'clamp_thread_engagement':6-tip})
 return records
def build():
 records=check()
 for n,s in PARTS.items():
  assert s.isValid() and len(s.Solids())==1,n
  cq.exporters.export(s,str(STEP/(n+'.step')))
  cq.exporters.export(s,str(STL/(n+'.stl')),tolerance=.035,angularTolerance=.12)
 a=cq.Assembly(name='MB4_revision_D_mm');manifest=[]
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
  'ball_reference':'D6 x thickness4.75 cylinder: 4 cradle positions clear, floorZ2',
  'clamp_tip_sweep':'1201 heights in 0..12: tipsZ0.2..0.7',
  'spring_model':'constant-pitch reference only; verify purchased spring ends and load curve',
  'not_tested':['physical ball/winding fit','strength/fatigue','acoustic/piezo output','specific bass fit']},indent=2))
 print(json.dumps(imported,indent=2));print('9 travel/height conditions passed; assembly valid')
if __name__=='__main__':build()
