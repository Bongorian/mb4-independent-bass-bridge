"""Close-up views of actual CAD meshes, loaded and unloaded reference cradle."""
from pathlib import Path
import bpy,math
from mathutils import Vector
ROOT=Path(__file__).resolve().parent
bpy.ops.wm.open_mainfile(filepath=str(ROOT/'MB4_RevL_preview.blend'))
s=bpy.context.scene
for ob in s.objects:
 if ob.type in ('MESH','CURVE'):
  ob.hide_render=not (ob.name.startswith('S2_') and ('A10_' in ob.name or 'ball_reference' in ob.name or 'string_reference' in ob.name))
cam=s.camera;cam.location=(9,-18,49)
target=Vector((-9.5,11,11));cam.rotation_euler=(target-cam.location).to_track_quat('-Z','Y').to_euler();cam.data.ortho_scale=29
s.render.resolution_x=1600;s.render.resolution_y=1250;s.render.resolution_percentage=100
s.cycles.samples=48
for loaded,filename in [(False,'ball_cradle_empty.png'),(True,'ball_cradle_loaded.png')]:
 for ob in s.objects:
  if ob.name.startswith('S2_') and ('ball_reference' in ob.name or 'string_reference' in ob.name):ob.hide_render=not loaded
 s.render.filepath=str(ROOT.parent/filename);bpy.ops.render.render(write_still=True)
 print('BALL_CRADLE_RENDER',filename,flush=True)
