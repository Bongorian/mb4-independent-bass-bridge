"""Six orthographic views of the existing Rev K preview scene; no CAD edits."""
from pathlib import Path
import json
import bpy
from mathutils import Vector, Matrix

ROOT = Path(__file__).resolve().parent
OUT = ROOT.parent / 'six_views'
OUT.mkdir(exist_ok=True)
bpy.ops.wm.open_mainfile(filepath=str(ROOT / 'MB4_RevK_preview.blend'))
s = bpy.context.scene
for ob in list(s.objects):
    if ob.type == 'LIGHT':
        bpy.data.objects.remove(ob, do_unlink=True)
    elif ob.name == 'body_reference_only' or 'string_reference' in ob.name:
        ob.hide_render = True

s.render.engine = 'CYCLES'
s.cycles.samples = 32
s.cycles.use_denoising = True
s.render.threads_mode = 'FIXED'
s.render.threads = 12
s.render.resolution_x = 1600
s.render.resolution_y = 1200
s.render.resolution_percentage = 100
s.render.image_settings.file_format = 'PNG'
s.render.image_settings.color_mode = 'RGBA'
s.render.film_transparent = True
s.view_settings.view_transform = 'AgX'
s.world.use_nodes = True
bg = s.world.node_tree.nodes.get('Background')
bg.inputs['Color'].default_value = (.8, .85, .9, 1)
bg.inputs['Strength'].default_value = .7

camera = s.camera
camera.data.type = 'ORTHO'
# In a landscape render, Blender's orthographic scale is the horizontal extent.
camera.data.ortho_scale = 100 * s.render.resolution_x / s.render.resolution_y
camera.data.clip_start = .1
camera.data.clip_end = 1000
center = Vector((0, 43, 12.5))
views = [
    ('01_front', '前面 / ネック側 (-Y)', (0, -1, 0), (0, 0, 1)),
    ('02_rear', '後面 / 調整ネジ側 (+Y)', (0, 1, 0), (0, 0, 1)),
    ('03_left', '左面 (-X)', (-1, 0, 0), (0, 0, 1)),
    ('04_right', '右面 (+X)', (1, 0, 0), (0, 0, 1)),
    ('05_top', '上面 (+Z)', (0, 0, 1), (0, 1, 0)),
    ('06_bottom', '下面 (-Z)', (0, 0, -1), (0, -1, 0)),
]
record = []
for slug, label, eye_tuple, up_tuple in views:
    eye, up = Vector(eye_tuple), Vector(up_tuple)
    right = up.cross(eye).normalized()
    camera.location = center + 220 * eye
    # Camera local axes: X screen right, Y screen up, Z toward viewer.
    camera.rotation_euler = Matrix((right, up, eye)).transposed().to_euler()
    lamps = []
    for name, off, energy, size in [
        ('key', eye*115 - right*65 + up*80, 900000, 90),
        ('fill', eye*95 + right*90 + up*10, 600000, 110),
        ('rim', -eye*65 + right*45 + up*90, 700000, 70),
    ]:
        bpy.ops.object.light_add(type='AREA', location=center + off)
        ob = bpy.context.object
        ob.name = 'six_view_' + name
        ob.data.energy = energy
        ob.data.shape = 'DISK'
        ob.data.size = size
        ob.rotation_euler = (center-ob.location).to_track_quat('-Z', 'Y').to_euler()
        lamps.append(ob)
    s.render.filepath = str(OUT / (slug + '.png'))
    bpy.ops.render.render(write_still=True)
    record.append({'file': slug+'.png', 'label': label, 'camera_from': eye_tuple,
                   'screen_up': up_tuple, 'projection': 'orthographic',
                   'vertical_extent_mm': 100})
    print('SIX_VIEW_COMPLETE', slug, flush=True)
    for ob in lamps:
        bpy.data.objects.remove(ob, do_unlink=True)
(OUT/'views.json').write_text(json.dumps({
    'revision': 'K', 'source': '../cad/MB4_RevK_preview.blend',
    'note': 'Body and long string reference objects hidden for all six views. '
            'Piezo envelopes and ball references remain visible. CAD unchanged.',
    'views': record}, ensure_ascii=False, indent=2)+'\n')
