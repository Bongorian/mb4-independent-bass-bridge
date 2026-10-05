from pathlib import Path
import sys,json,itertools
ROOT=Path(__file__).resolve().parent
sys.path.insert(0,str(ROOT))
import build_bridge as b
rows=[]
for q,g in itertools.product((8,14,20),(0,6,12)):
 items=b.module_items(0,q,g,False)
 full=b.cyl(6,25-q,(0,q+42,7+g),(0,1,0))
 tool=b.cyl(6,35,(0,85,5))
 for name,s,col in items:
  if name in b.PARTS:assert full.intersect(s).Volume()<1e-5,(q,g,name,'full spring envelope')
  assert tool.intersect(s).Volume()<1e-5,(q,g,name,'rear driver')
 rows.append({'q':q,'g':g,'catalogue_OD6_envelope':'clear','rear_D6_driver':'clear'})
# Washer 0.5 stack selection can exceed purchased thickness tolerances;
# CAD nominal result is checked, actual stacking must be measured.
result={'revision':'F','cases':rows,'spring_ID_nominal':5.3,'spring_ID_at_OD_lower_limit_reference':4.8,'bolt_diameter':4,'minimum_plain_shank_gap_nominal':1.5,'minimum_thread_overlap_nominal':6.5,'height_tap':'M4x0.7 THRU8','limitations':'nominal dimensions; no physical tolerance/strength certification'}
(ROOT/'catalogue_envelope_check.json').write_text(json.dumps(result,indent=2)+'\n')
print('9 full catalogue spring envelopes and rear driver conditions clear')
