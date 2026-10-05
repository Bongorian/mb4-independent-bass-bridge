"""Nominal section comparison, no FEA and no allowable load determination.
350N/string is a comparison assumption. Rear wall is an ideal fixed cantilever.
Exact CAD horizontal section areas/inertias, major-diameter slot envelope included.
No notch factor, base flexibility, screw preload, fatigue or wood anchor analysis.
"""
from pathlib import Path
import importlib.util,json,csv
from OCP.BRepGProp import BRepGProp
from OCP.GProp import GProp_GProps
import cadquery as cq
ROOT=Path(__file__).resolve().parent

def module(path,name):
 spec=importlib.util.spec_from_file_location(name,path);m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m);return m
D=module(ROOT/'build_bridge.py','bridgeD')
Cpath=ROOT/'reference/RevC_B01_base.step'
if not Cpath.exists(): raise SystemExit('Rev C reference STEP needed for comparison only; rebuild is independent.')
C=cq.importers.importStep(str(Cpath)).val();Dbase=D.PARTS['B02_reinforced_base'];force=350.
# Restrict sections to rear wall/ribs. Clamp pads must not enter inertia.
region=D.box(30,20,30,y=62)
C=C.intersect(region);Dbase=Dbase.intersect(region)
records=[]
for height in [3.6+i*.2 for i in range(76)]:
 for rev,part,axis in [('C',C,18.),('D',Dbase,19.)]:
  section=cq.Workplane('XY').newObject([part]).section(height).val()
  props=GProp_GProps();BRepGProp.SurfaceProperties_s(section.wrapped,props)
  cen=props.CentreOfMass();ix=props.MatrixOfInertia().Value(1,1)
  bb=section.BoundingBox();extent=max(cen.Y()-bb.ymin,bb.ymax-cen.Y());modulus=ix/extent
  nominal=force*max(axis-height,0)/modulus
  records.append({'rev':rev,'z':round(height,2),'area_mm2':props.Mass(),'centroid_y':cen.Y(),
   'Ixx_mm4':ix,'section_modulus_mm3':modulus,'nominal_bending_MPa':nominal})
# Choose same Z domain below minimum test axis18; geometry and loads differ by1mm.
peak={rev:max([r for r in records if r['rev']==rev],key=lambda r:r['nominal_bending_MPa']) for rev in ('C','D')}
Cspine=4.6*6-3.141592653589793*1.5**2
Dspine=6*3+8.6*5-3.141592653589793*2**2
result={'load_assumption_N_per_string':force,'gap_test_mm':12,'max_string_axis_mm':20,
 'rear_screw_axes_mm':{'C':18,'D':19},'z_scan_mm':[3.6,18.6],'z_step_mm':.2,
 'peak_nominal_bending':peak,'peak_stress_D_over_C':peak['D']['nominal_bending_MPa']/peak['C']['nominal_bending_MPa'],
 'central_spine_net_area_estimate_mm2':{'C':Cspine,'D':Dspine,'ratio':Dspine/Cspine},
 'screw_tensile_area_mm2':{'M3':5.03,'M4':8.78,'ratio':8.78/5.03},
 'clamp_engagement_mm':{'C':[2.3,2.8],'D':[5.3,5.8]},
 'limitations':['nominal cantilever section comparison, NOT FEA','geometry-dependent local notch stress omitted',
 'rigid base idealization; screws, preload, fatigue, body wood not modeled','350N chosen comparison assumption, actual string load not measured'],
 'source_screw_area':'Bossard f-009-en.pdf, metric coarse-thread tensile stress areas'}
(ROOT/'strength_comparison.json').write_text(json.dumps(result,indent=2))
with (ROOT/'section_scan.csv').open('w',newline='') as f:
 w=csv.DictWriter(f,fieldnames=records[0].keys());w.writeheader();w.writerows(records)
print(json.dumps(result,indent=2))
