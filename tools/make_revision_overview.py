"""Compose a native SVG poster from the nine unmodified historical CAD renders."""
from pathlib import Path
import base64, json, html, ctypes, ctypes.util, hashlib

ROOT = Path(__file__).resolve().parent.parent
OUT = ROOT / "docs/assets"
W, H = 3600, 4110
REVISIONS = [
    ('A', '初期構成', 15, 3, ['各弦独立・裏面ピエゾの基本構成', 'ベース＋キャリッジ＋黄銅アンカー']),
    ('B', '外周に丸み', 15, 3, ['ベース・アンカーの外周にRを追加', '基本機構と機能寸法を維持']),
    ('C', '低弦高化・2部品化', 8, 2, ['キャリッジとアンカーを一体化', 'ネジ＋バネで12 mmの前後調整']),
    ('D', '後壁と固定部を補強', 8, 2, ['前後リブと厚い固定パッドを追加', '後方調整ネジをM3からM4へ']),
    ('E', 'アーチと曲線リブ', 8, 2, ['後壁をアーチ化・曲線リブを採用', '後方2穴を追加し、ベース長90 mmへ']),
    ('F', '後方1穴・一体クラウン', 8, 2, ['後方2穴を中央1穴へ戻す', '丸いクラウンとミスミ標準金物を採用']),
    ('G', 'アルミ化・加工性を見直し', 8, 2, ['両部品を6061-T6に統一・丸みを追加', '穴の交差を修正、後タップを裏窓へ貫通']),
    ('H', 'ベース短縮・リブを簡潔に', 8, 2, ['前取付穴とピエゾをエンド側へ移動', 'ベース長98→86 mm・リブを平面化']),
    ('I', '調整範囲を20 mmへ', 8, 2, ['長穴を延長、M4×45全ねじ＋長いバネ', 'ベース長86 mmを維持して可動域を拡大']),
]
parts = [f'<svg xmlns="http://www.w3.org/2000/svg" xmlns:xlink="http://www.w3.org/1999/xlink" width="{W}" height="{H}" viewBox="0 0 {W} {H}">',
         '<rect width="3600" height="4110" fill="#edf1f4"/>']
def text(x, y, s, size=34, fill='#273b48', weight=400):
    parts.append(f'<text x="{x}" y="{y}" font-family="Noto Sans CJK JP, sans-serif" font-size="{size}" font-weight="{weight}" fill="{fill}">{html.escape(s)}</text>')
def rect(x,y,w,h,fill,rx=0,stroke=None,sw=1):
    parts.append(f'<rect x="{x}" y="{y}" width="{w}" height="{h}" rx="{rx}" fill="{fill}"'+ (f' stroke="{stroke}" stroke-width="{sw}"' if stroke else '') + '/>')

text(60, 112, 'MB4  /  4弦独立ブリッジの発展', 78, weight=700)
text(64, 175, 'REV. A → I  ｜  左から右、上から下へ  ｜  保存された各版のCADプレビューと変更点', 34, '#5d7280')
rect(3000,55,540,70,'#dcebe6',20)
text(3030,104,'9 REVISIONS  /  2026.10.05',30,'#276b59',600)

manifest=[]
CW, CH, GAP = 1136, 1190, 36
for i,(rev,title,minheight,nparts,lines) in enumerate(REVISIONS):
    x=60+(i%3)*(CW+GAP); y=225+(i//3)*(CH+GAP)
    folder=ROOT/'revisions'/rev
    p=folder/'bridge_preview.png'
    params=json.loads((folder/'cad/parameters.json').read_text())
    length=int(params['base_length'])
    accent='#297962' if rev=='I' else '#335a76'
    rect(x,y,CW,CH,'#fff',24,accent if rev=='I' else '#dbe3e8',5 if rev=='I' else 2)
    rect(x+25,y+25,194,63,accent,14)
    text(x+45,y+72,'REV. '+rev,43,'#fff',700)
    text(x+245,y+73,title,43,'#233b49',700)
    raw=p.read_bytes()
    uri='data:image/png;base64,'+base64.b64encode(raw).decode()
    # Whole original image, no trimming, repainting or synthesized CAD geometry.
    parts.append(f'<image x="{x+24}" y="{y+109}" width="1088" height="884" preserveAspectRatio="xMidYMid meet" xlink:href="{uri}"/>')
    text(x+30,y+1044,f'ベース {length} mm   /   最低弦中心 {minheight} mm   /   切削 {nparts}部品・各弦',32,accent,600)
    text(x+32,y+1104,lines[0],34,'#293f4d')
    text(x+32,y+1155,lines[1],34,'#293f4d')
    manifest.append({'revision':rev,'title':title,'preview':str(p.relative_to(ROOT)),
      'sha256':hashlib.sha256(raw).hexdigest(),'base_length_mm':length,
      'minimum_reference_string_centre_mm':minheight,'CNC_parts_per_string':nparts,
      'changes':lines,'sources':[str((folder/'cad/parameters.json').relative_to(ROOT)),
          str(next(folder.glob('README.*')).relative_to(ROOT))]})

text(64,3932,'寸法は設計値。最低弦中心は参考ボールの軸に基づく。画像の縮尺・組立位置は各版で異なります。',31,'#5d7280')
text(64,3987,'Rev G・H：通常10 mm、条件付き最大12 mm。Rev I：20 mm設計、前方限界では15 mm張り出し、全長101 mm。',31,'#5d7280')
text(64,4042,'全版とも試作設計。加工受託・実機強度の認定を示す一覧ではありません。出典：各版の保存CAD／README。',29,'#758793')
parts.append('</svg>')
svg='\n'.join(parts).encode()
(OUT/'revision-history.svg').write_bytes(svg)
(OUT/'revision_history.json').write_text(json.dumps(manifest,ensure_ascii=False,indent=2)+'\n')

# Render the new vector layout through the workstation's SVG/Cairo libraries.
g=ctypes.CDLL(ctypes.util.find_library('gobject-2.0'))
r=ctypes.CDLL(ctypes.util.find_library('rsvg-2'))
c=ctypes.CDLL(ctypes.util.find_library('cairo'))
r.rsvg_handle_new_with_flags.argtypes=[ctypes.c_int]
r.rsvg_handle_new_with_flags.restype=ctypes.c_void_p
r.rsvg_handle_write.argtypes=[ctypes.c_void_p,ctypes.c_void_p,ctypes.c_size_t,ctypes.c_void_p]
r.rsvg_handle_write.restype=ctypes.c_int
r.rsvg_handle_close.argtypes=[ctypes.c_void_p,ctypes.c_void_p]
r.rsvg_handle_close.restype=ctypes.c_int
r.rsvg_handle_render_cairo.argtypes=[ctypes.c_void_p,ctypes.c_void_p]
r.rsvg_handle_render_cairo.restype=ctypes.c_int
c.cairo_image_surface_create.argtypes=[ctypes.c_int,ctypes.c_int,ctypes.c_int]
c.cairo_image_surface_create.restype=ctypes.c_void_p
c.cairo_create.argtypes=[ctypes.c_void_p];c.cairo_create.restype=ctypes.c_void_p
c.cairo_scale.argtypes=[ctypes.c_void_p,ctypes.c_double,ctypes.c_double]
c.cairo_surface_write_to_png.argtypes=[ctypes.c_void_p,ctypes.c_char_p]
c.cairo_surface_write_to_png.restype=ctypes.c_int
c.cairo_destroy.argtypes=[ctypes.c_void_p]
c.cairo_surface_destroy.argtypes=[ctypes.c_void_p]
g.g_object_unref.argtypes=[ctypes.c_void_p]
data=ctypes.create_string_buffer(svg)
handle=r.rsvg_handle_new_with_flags(1)  # Unlimited parser size for nine embedded renders.
assert handle
assert r.rsvg_handle_write(handle,data,len(svg),None)
assert r.rsvg_handle_close(handle,None)
for name,scale in [('revision-history.png',1.0),('revision-history-preview.png',0.5)]:
    surf=c.cairo_image_surface_create(0,int(W*scale),int(H*scale))
    context=c.cairo_create(surf);c.cairo_scale(context,scale,scale)
    assert r.rsvg_handle_render_cairo(handle,context)
    assert c.cairo_surface_write_to_png(surf,str(OUT/name).encode())==0
    c.cairo_destroy(context);c.cairo_surface_destroy(surf)
    print(name,(OUT/name).stat().st_size,'bytes')
g.g_object_unref(handle)
