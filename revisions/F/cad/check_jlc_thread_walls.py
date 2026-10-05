"""Spot checks of material surrounding nominal M4 thread crests in Rev F.

This is a geometric review, not a thread strength analysis or supplier approval.
"""
from pathlib import Path
import json
import cadquery as cq

ROOT = Path(__file__).resolve().parent.parent
s = cq.importers.importStep(str(ROOT/'cad/step/A05_crown_anchor.step')).val()
results = []
for x in (-5, 5):
    for y in (15, 20.5):
        for direction, dx, dy in [('toward_cradle', -2.02 if x>0 else 2.02, 0),
                                  ('outer_side', 2.02 if x>0 else -2.02, 0),
                                  ('rearward', 0, 2.02)]:
            for z in (1, 3, 6):
                xyz = (x+dx, y+dy, z)
                results.append({'hole_center_xy_mm': [x,y], 'direction':direction,
                                'xyz_mm':xyz, 'material_present':s.isInside(cq.Vector(*xyz), 1e-6)})
out = {'part':'A05_crown_anchor', 'revision':'F', 'nominal_thread_major_diameter_mm':4,
       'probe_radius_mm':2.02, 'results':results,
       'finding':'Front height holes open into the ball pocket above its Z2 floor. '
                 'Rear holes also approach the bottom relief. '
                 'Full-thickness cylindrical tap assumptions are not valid.',
       'limitations':'Finite spot checks; no thread geometry, strength, CAM toolpath or supplier acceptance analysis.'}
(ROOT/'jlc_thread_wall_check.json').write_text(json.dumps(out,ensure_ascii=False,indent=2)+'\n')
for row in results:
    if not row['material_present']:
        print('Open to cavity:', row['hole_center_xy_mm'],row['direction'],row['xyz_mm'],flush=True)
