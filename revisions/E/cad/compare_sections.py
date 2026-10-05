"""Nominal cantilever comparison E vs D; not FEA or allowable load.
Rear flange and clamp pads excluded from E section. Actual wood fixings not modeled.
"""
from pathlib import Path
import importlib.util,json,csv
from OCP.BRepGProp import BRepGProp
from OCP.GProp import GProp_GProps
import cadquery as cq
ROOT=Path(__file__).resolve().parent
spec=importlib.util.spec_from_file_location('bridgeE',ROOT/'build_bridge.py');E=importlib.util.module_from_spec(spec);spec.loader.exec_module(E)
D=cq.importers.importStep(str(ROOT/'reference/RevD_B02_base.step')).val()
region=E.box(30,32,30,y=59)
D=D.intersect(region);core=E.STRUCTURAL_CORE.intersect(region);force=350.;records=[]
for z in [3.6+i*.2 for i in range(76)]:
 for rev,part in [('D',D),('E',core)]:
  face=cq.Workplane('XY').newObject([part]).section(z).val();g=GProp_GProps();BRepGProp.SurfaceProperties_s(face.wrapped,g)
  cy=g.CentreOfMass().Y();ix=g.MatrixOfInertia().Value(1,1);bb=face.BoundingBox();mod=ix/max(cy-bb.ymin,bb.ymax-cy)
  records.append({'rev':rev,'z':round(z,2),'area_mm2':g.Mass(),'centroid_y':cy,'Ixx_mm4':ix,'section_modulus_mm3':mod,'nominal_bending_MPa':force*(19-z)/mod})
peaks={r:max((v for v in records if v['rev']==r),key=lambda v:v['nominal_bending_MPa']) for r in ('D','E')}
result={'load_assumption_N_per_string':force,'gap_test_mm':12,'string_axis_mm':20,'screw_axis_mm':19,
 'z_scan_mm':[3.6,18.6],'step_mm':.2,'peak_nominal_bending':peaks,
 'peak_stress_E_over_D':peaks['E']['nominal_bending_MPa']/peaks['D']['nominal_bending_MPa'],
 'mount_layout':{'D':{'front':[0,4],'rear':[[0,78]],'rear_plate_mm':3},'E':{'front':[0,5],'rear':[[-4.5,85],[4.5,85]],'rear_plate_mm':5}},
 'limitations':['nominal section comparison, NOT FEA','rear screw flange and clamp pads excluded',
 'local notch stress, fatigue, preload, base flexibility and body wood excluded','350 N is comparison assumption, not measured or allowable tension','extra rear screw benefits not numerically rated']}
(ROOT/'strength_comparison.json').write_text(json.dumps(result,indent=2))
with (ROOT/'section_scan.csv').open('w',newline='') as f:
 w=csv.DictWriter(f,fieldnames=records[0]);w.writeheader();w.writerows(records)
assert result['peak_stress_E_over_D']<=1.05,'Organic profile regresses nominal wall bending'
print(json.dumps(result,indent=2))
