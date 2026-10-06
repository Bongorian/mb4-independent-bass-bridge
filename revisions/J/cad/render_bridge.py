"""Blender presentation scene, dimensions in mm. Meshes are preview only."""
import bpy, json, math
from pathlib import Path
from mathutils import Vector
ROOT=Path(__file__).resolve().parent
bpy.ops.object.select_all(action='SELECT'); bpy.ops.object.delete(use_global=False)
def material(name,color,metal=0,rough=.35):
    m=bpy.data.materials.new(name); m.diffuse_color=(*color,1); m.use_nodes=True
    bs=m.node_tree.nodes.get('Principled BSDF'); bs.inputs['Base Color'].default_value=(*color,1); bs.inputs['Metallic'].default_value=metal; bs.inputs['Roughness'].default_value=rough
    return m
for row in json.loads((ROOT/'scene_manifest.json').read_text()):
    bpy.ops.wm.stl_import(filepath=str(ROOT/row['file']))
    ob=bpy.context.object; ob.name=row['name']; ob.data.materials.append(material(ob.name,row['color'],.72,.24))
    # CAD-generated fillets only; smoothing is presentation, not a mesh bevel.
    for poly in ob.data.polygons: poly.use_smooth=True
    ob.data.set_sharp_from_angle(angle=math.radians(35))
    mod=ob.modifiers.new('CAD planar normal weighting','WEIGHTED_NORMAL');mod.keep_sharp=True;mod.weight=50
wood=material('body_surface',(.20,.115,.055),0,.55)
bpy.ops.mesh.primitive_cube_add(size=1,location=(0,0,-4)); ob=bpy.context.object; ob.name='body_reference_only'; ob.scale=(118,220,8); ob.data.materials.append(wood)
bevel=ob.modifiers.new('body_round','BEVEL'); bevel.width=6; bevel.segments=5
def target(ob,point): ob.rotation_euler=(Vector(point)-ob.location).to_track_quat('-Z','Y').to_euler()
bpy.ops.object.camera_add(location=(135,-128,144)); camera=bpy.context.object; target(camera,(0,25,8)); camera.data.type='ORTHO'; camera.data.ortho_scale=142; bpy.context.scene.camera=camera
for name,pos,energy,size in [('key',(30,-20,190),850000,95),('fill',(-120,-50,100),450000,100),('rim',(30,160,150),850000,80)]:
    bpy.ops.object.light_add(type='AREA',location=pos); ob=bpy.context.object; ob.name=name; ob.data.energy=energy; ob.data.shape='DISK'; ob.data.size=size; target(ob,(0,20,0))
s=bpy.context.scene; s.unit_settings.system='METRIC'; s.unit_settings.scale_length=.001
s.render.engine='CYCLES'; s.cycles.samples=32; s.render.threads_mode='FIXED'; s.render.threads=12; s.cycles.use_denoising=True
s.world.color=(.45,.45,.45); s.render.resolution_x=1600; s.render.resolution_y=1300; s.render.resolution_percentage=100
s.view_settings.view_transform='AgX'; s.render.image_settings.file_format='PNG'
s.render.filepath=str(ROOT.parent/'bridge_preview.png')
bpy.ops.wm.save_as_mainfile(filepath=str(ROOT/'MB4_RevJ_preview.blend'))
bpy.ops.render.render(write_still=True)
print('Rendered',s.render.filepath)
camera.location=(115,165,135);target(camera,(0,41,7));camera.data.ortho_scale=135
s.render.filepath=str(ROOT.parent/'bridge_rear_preview.png');bpy.ops.render.render(write_still=True)
print('Rear fixing view',s.render.filepath)
