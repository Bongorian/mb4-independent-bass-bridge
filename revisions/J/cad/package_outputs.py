"""Prepare upload pairs and a verified complete prototype archive."""
from pathlib import Path
import json, hashlib, shutil, zipfile
ROOT=Path(__file__).resolve().parent.parent
UPLOAD=ROOT/'jlc_upload';UPLOAD.mkdir(exist_ok=True)
names=['B08_rounded_base','A08_rounded_anchor']
manifest=[]
for name in names:
 pair=[]
 for src in [ROOT/'cad/step'/f'{name}.step',ROOT/'pdf'/f'{name}.pdf']:
  dest=UPLOAD/src.name;shutil.copy2(src,dest);pair.append(dest)
  manifest.append({'name':src.name,'size_bytes':src.stat().st_size,'sha256':hashlib.sha256(src.read_bytes()).hexdigest()})
 with zipfile.ZipFile(UPLOAD/f'{name}_JLC.zip','w',zipfile.ZIP_DEFLATED) as z:
  for p in pair:z.write(p,p.name)
with zipfile.ZipFile(ROOT/'MB4_JLCCNC_upload_RevJ.zip','w',zipfile.ZIP_DEFLATED) as z:
 for name in names:
  for ext in ['step','pdf']:z.write(UPLOAD/f'{name}.{ext}',f'{name}.{ext}')
(ROOT/'file_manifest.json').write_text(json.dumps({'revision':'J','units':'mm','upload_parts':manifest,'supplier_status':'not submitted; manual review pending'},indent=2)+'\n')
# No caches, intermediate renders, logs or recursively included archives.
with zipfile.ZipFile(ROOT/'MB4_CNC_prototype_RevJ.zip','w',zipfile.ZIP_DEFLATED) as z:
 for p in sorted(ROOT.rglob('*')):
  if not p.is_file():continue
  rel=p.relative_to(ROOT)
  if 'qa' in rel.parts or '__pycache__' in rel.parts or p.suffix in ('.log','.blend1','.zip'):continue
  z.write(p,str(Path('MB4_RevJ')/rel))
for p in [ROOT/'MB4_JLCCNC_upload_RevJ.zip',ROOT/'MB4_CNC_prototype_RevJ.zip',ROOT/'MB4_RevJ_six_views.zip',*[UPLOAD/f'{n}_JLC.zip' for n in names]]:
 with zipfile.ZipFile(p) as z:
  assert z.testzip() is None,p
  if p.name=='MB4_JLCCNC_upload_RevJ.zip':
   assert sorted(z.namelist())==sorted(f'{n}.{ext}' for n in names for ext in ['pdf','step'])
  print(p.name,p.stat().st_size,'bytes',len(z.namelist()),'files: CRC passed')
# DXF has exactly eight body mounting circles at the intended coordinates.
import ezdxf
m=ezdxf.readfile(ROOT/'MB4_mount_template_1to1.dxf').modelspace()
circles=list(m.query('CIRCLE[layer=="MOUNT_CENTER"]'))
assert len(circles)==8
assert sorted((round(c.dxf.center.x,3),round(c.dxf.center.y,3)) for c in circles)==sorted((x,y) for x in [-28.5,-9.5,9.5,28.5] for y in [8,81])
print('DXF: eight mount holes / revised Y81 / mm units passed')
