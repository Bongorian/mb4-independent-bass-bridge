"""Parametric B-rep CAD; mm. Run with cadquery==2.8.0. Threads are tap-drill geometry.
Machining thread specifications are in the PDF/feature CSV, not a mesh.
"""
from pathlib import Path
import json, itertools, csv
import cadquery as cq

ROOT = Path(__file__).resolve().parent
P = json.loads((ROOT/'parameters.json').read_text())
STEP=ROOT/'step'; STL=ROOT/'preview_mesh'; STEP.mkdir(exist_ok=True); STL.mkdir(exist_ok=True)
V=cq.Vector
def box(w,l,h,x=0,y=0,z=0):
    return cq.Workplane('XY').box(w,l,h,centered=(True,False,False)).translate((x,y,z)).val()
def cyl(d,l,origin,direction=(0,0,1)):
    return cq.Solid.makeCylinder(d/2,l,V(*origin),V(*direction))
def capsule(w,total,x,y,z,h):
    return cq.Workplane('XY').center(x,y).slot2D(total,w,90).extrude(h).translate((0,0,z)).val()
def rounded_pocket(w,l,x,y,z,h,r=1.5):
    return cq.Workplane('XY').box(w,l,h,centered=(True,True,False)).edges('|Z').fillet(r).translate((x,y,z)).val()

def finished_blank(w,l,h,outline_r,edge_r=.2,x=0,y=0,z=0,top_r=None):
    """Exact solid fillets, before functional holes. Plan corner R is extruded
    with an ordinary contour pass. Small edge R preserves flat screw lands.
    Bottom perimeter R does not change nominal contact-plane Z.
    """
    wp=cq.Workplane('XY').box(w,l,h,centered=(True,False,False)).edges('|Z').fillet(outline_r)
    wp=wp.faces('>Z').edges().fillet(edge_r if top_r is None else top_r)
    if edge_r: wp=wp.faces('<Z').edges().fillet(edge_r)
    return wp.translate((x,y,z)).val()

def make_base():
    plate=finished_blank(P['base_width'],P['base_length'],5,P['base_outline_radius'],P['external_edge_radius'])
    # Integral tower: rounded corners and a broad comfortable upper edge.
    # Its bottom remains a flat fusion/contact plane, rather than a seam gap.
    tower=finished_blank(18,6,7,P['tower_outline_radius'],0,y=62,z=5,top_r=P['tower_top_radius'])
    b=plate.fuse(tower)
    for y in (4,78):
        b=b.cut(cyl(3.8,5,(0,y,0)))
        b=b.cut(cq.Solid.makeCone(1.9,3.5,1.6,V(0,y,3.4),V(0,0,1)))
    for x in (-4,4):
        b=b.cut(capsule(3.4,15.4,x,48,0,5))
        b=b.cut(rounded_pocket(5.8,22,x,48,0,2.2))
    b=b.cut(cyl(12.5,1.5,(0,20,0)))
    b=b.cut(box(9,2.2,1.2,x=4.5,y=18.9))
    b=b.cut(cyl(3.4,6,(0,62,7.5),(0,1,0)))
    # Clearance for the standard rear washer and hex nuts below z=5.
    b=b.cut(box(8,6,1.5,y=68,z=3.5))
    return b.clean()

def make_carrier():
    b=finished_blank(18,40,5,P['carrier_outline_radius'],P['external_edge_radius'])
    for x in (-4,4): b=b.cut(cyl(3.4,5,(x,34,0)))
    for x in (-6,6): b=b.cut(cyl(2.5,5,(x,3,0))) # M3x0.5 through
    b=b.cut(cyl(2.5,12,(0,40,2.5),(0,-1,0))) # M3x0.5 usable depth 10, drill 12
    # Drill tip is explicitly included, 118 degree point, depth 12.75.
    b=b.cut(cq.Solid.makeCone(1.25,0,0.75,V(0,28,2.5),V(0,-1,0)))
    return b.clean()

def make_anchor():
    b=finished_blank(18,26,10,P['anchor_outline_radius'],P['external_edge_radius'])
    b=b.cut(cyl(P['ball_bore_diameter'],20,(0,26,5),(0,-1,0)))
    # 3-axis open slot: no contact saddle. Full gauge and winding must clear it.
    b=b.cut(box(3.4,26,6.7,y=0,z=3.3))
    for x in (-6,6):
        for y in (11,22): b=b.cut(cyl(2.5,10,(x,y,0))) # M3x0.5 jacks
        b=b.cut(cyl(3.4,10,(x,3,0))) # hold-down bolts
    # Only the upper mouth is softened; the minimum slot width, floor,
    # ball seat at Y=6, and ball bore stay at their Rev A dimensions.
    lip_edges=[e for e in b.Edges() if e.geomType()=='LINE'
               and abs(e.Center().z-10)<1e-6
               and abs(abs(e.Center().x)-1.7)<1e-6 and e.Length()>20]
    assert len(lip_edges)==2, 'anchor upper lip edge selection changed'
    b=b.fillet(P['anchor_slot_lip_radius'],lip_edges)
    return b.clean()

PARTS={'B01_base':make_base(),'C01_carrier':make_carrier(),'A01_anchor':make_anchor()}
COLORS={'B01_base':cq.Color(.32,.39,.43),'C01_carrier':cq.Color(.57,.63,.66),'A01_anchor':cq.Color(.72,.53,.23)}
def loc(shape,x,y,z): return shape.translate((x,y,z))
def screw_vertical(x,y,shoulder,length,head=True,washer=0):
    s=cyl(3,length,(x,y,shoulder-length))
    if head:
        h=cyl(5.5,3,(x,y,shoulder)).cut(cq.Workplane('XY').polygon(6,2.8868).extrude(1.6).translate((x,y,shoulder+1.4)).val())
        s=s.fuse(h)
    else:
        s=s.cut(cq.Workplane('XY').polygon(6,1.732).extrude(1.5).translate((x,y,shoulder-1.5)).val())
    return s
def washer(dout,din,t,pos,axis=(0,0,1)):
    return cyl(dout,t,pos,axis).cut(cyl(din,t,pos,axis))
def nut_y(x,y,z):
    # across flats 5.5; polygon extruded along -Y then positioned
    s=cq.Workplane('XZ').polygon(6,6.35085).extrude(2.4).translate((x,y+2.4,z)).val()
    return s.cut(cyl(2.5,2.4,(x,y,z),(0,1,0)))

def module_items(x=0,origin=14,gap=2):
    items=[]
    def add(n,s,c): items.append((n,s,c))
    for name,z,y in [('B01_base',0,0),('C01_carrier',5,origin),('A01_anchor',10+gap,origin)]:
        add(name,loc(PARTS[name],x,y,z),COLORS[name])
    steel=cq.Color(.76,.77,.79)
    for xx in (-4,4):
        add('slide_clamp',screw_vertical(x+xx,origin+34,10.5,10),steel)
        add('slide_washer',washer(7,3.2,.5,(x+xx,origin+34,10)),steel)
        n=box(5.5,5.5,1.8,x=x+xx,y=origin+34-2.75,z=.4).cut(cyl(2.5,1.8,(x+xx,origin+34,.4)))
        add('DIN562_nut',n,steel)
    for xx in (-6,6):
        for yy in (11,22): add('height_M3x10',screw_vertical(x+xx,origin+yy,20,10,False),steel)
        shim=(1 if gap<1 else 0) if gap<=3 else 2
        length=16 if gap<=3 else 20
        if shim: add('hold_shim',washer(6,3.2,shim,(x+xx,origin+3,20+gap)),steel)
        add('hold_M3',screw_vertical(x+xx,origin+3,20+gap+shim,length),steel)
    rodstart=origin+30
    add('intonation_M3x40',cyl(3,40,(x,rodstart,7.5),(0,1,0)),steel)
    add('intonation_washer',washer(7,3.2,.5,(x,68,7.5),(0,1,0)),steel)
    add('intonation_nut',nut_y(x,68.5,7.5),steel)
    add('intonation_jam_nut',nut_y(x,70.9,7.5),steel)
    # Witness axis is nominal: no purported universal ball-end/string endpoint.
    add('string_reference',cyl(1.1,120,(x,origin+6,15+gap),(0,-1,0)),cq.Color(.85,.85,.85))
    add('piezo_envelope_ONLY',cyl(12,.7,(x,20,.5)),cq.Color(.70,.38,.13))
    return items

def build():
    for n,s in PARTS.items():
        assert s.isValid() and len(s.Solids())==1, n
        cq.exporters.export(s,str(STEP/(n+'.step')))
        cq.exporters.export(s,str(STL/(n+'.stl')),tolerance=.035,angularTolerance=.12)
    scene=cq.Assembly(name='MB4_revision_B_mm')
    manifest=[]
    pitch=P['string_pitch']
    for i,(x,origin,gap) in enumerate(zip([pitch*k for k in (-1.5,-.5,.5,1.5)],[18,16,14,12],[3,2.5,2,1.5])):
        for j,(n,s,c) in enumerate(module_items(x,origin,gap)):
            label=f'S{i+1}_{n}_{j}'
            scene.add(s,name=label,color=c)
            fn=STL/(label+'.stl'); cq.exporters.export(s,str(fn),tolerance=.05,angularTolerance=.15)
            manifest.append({'name':label,'file':str(fn.relative_to(ROOT)),'color':[c.toTuple()[k] for k in range(3)]})
    scene.export(str(STEP/'MB4_assembly.step'))
    (ROOT/'scene_manifest.json').write_text(json.dumps(manifest,indent=2))
    # Test all allowed limits and nominal positions for machined-part interferences.
    check=[]
    for origin,gap in itertools.product((8,14,20),(0,2.5,5)):
        shapes=[PARTS['B01_base'],loc(PARTS['C01_carrier'],0,origin,5),loc(PARTS['A01_anchor'],0,origin,10+gap)]
        intersections=[a.intersect(b).Volume() for a,b in itertools.combinations(shapes,2)]
        assert max(intersections)<1e-6,(origin,gap,intersections)
        check.append({'carrier_y':origin,'height_gap':gap,'intersection_mm3':intersections})
        # Hardware against unrelated machined parts. Threaded mating overlaps
        # are expected because threads are represented by their tap-drill bore.
        for name,hardware,_ in module_items(0,origin,gap)[3:]:
            if name in ('string_reference','piezo_envelope_ONLY'): continue
            for part,shape in zip(('B01_base','C01_carrier','A01_anchor'),shapes):
                mating=(part=='C01_carrier' and name in ('hold_M3','intonation_M3x40')) or (part=='A01_anchor' and name=='height_M3x10')
                if not mating:
                    volume=hardware.intersect(shape).Volume()
                    assert volume<1e-5,(origin,gap,name,part,volume)
    imported={}
    for n in PARTS:
        s=cq.importers.importStep(str(STEP/(n+'.step'))).val()
        assert s.isValid() and abs(s.Volume()-PARTS[n].Volume())<1e-4
        bb=s.BoundingBox(); imported[n]={'volume_mm3':s.Volume(),'bbox_mm':[bb.xlen,bb.ylen,bb.zlen]}
    (ROOT/'geometry_check.json').write_text(json.dumps({'units':'mm','valid_solids':imported,'limit_checks':check,'hardware_unrelated_part_interference':'passed at 9 range combinations; mating thread overlaps excluded','thread_geometry':'tap drill only; see drawing','not_tested':['physical string termination','strength by FEA/test','piezo transfer function','specific bass fit']},indent=2))
    print(json.dumps(imported,indent=2))
if __name__=='__main__': build()
