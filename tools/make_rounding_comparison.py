"""Lay out existing CAD renders; no geometry or image content is repainted."""
from pathlib import Path
import base64,ctypes,ctypes.util

ROOT=Path(__file__).resolve().parent.parent
OUT=ROOT/'docs/assets'
W,H=3200,1630
parts=[f'<svg xmlns="http://www.w3.org/2000/svg" xmlns:xlink="http://www.w3.org/1999/xlink" width="{W}" height="{H}">',
       f'<rect width="{W}" height="{H}" fill="#edf1f4"/>']
def text(x,y,s,size=36,color='#2b4250',weight=400):
    parts.append(f'<text x="{x}" y="{y}" font-family="Noto Sans CJK JP, sans-serif" font-size="{size}" font-weight="{weight}" fill="{color}">{s}</text>')
text(40,85,'MB4 / Rev I → Rev J',65,weight=700)
text(42,139,'全体の丸みを追加  /  20 mmの調整域・低弦高・取付位置を維持',38,color='#647987')
for rev,x,label,caption in [
    ('I',40,'REV I / 改訂前','アーチC0.25・リブC0.25・アンカー上縁R0.8'),
    ('J',1620,'REV J / 丸みを追加','アーチR1.2・リブR0.8・アンカー上縁R1.2')]:
    parts.append(f'<rect x="{x}" y="185" width="1540" height="1335" rx="24" fill="white"/>')
    text(x+28,245,label,45,'#287760' if rev=='J' else '#345a76',700)
    encoded=base64.b64encode((ROOT/'revisions'/rev/'bridge_preview.png').read_bytes()).decode()
    parts.append(f'<image x="{x+24}" y="274" width="1492" height="1212" preserveAspectRatio="xMidYMid meet" xlink:href="data:image/png;base64,{encoded}"/>')
    text(x+28,1577,caption,35)
parts.append('</svg>');svg='\n'.join(parts).encode()
(OUT/'rev-i-to-j.svg').write_bytes(svg)
r=ctypes.CDLL(ctypes.util.find_library('rsvg-2'))
c=ctypes.CDLL(ctypes.util.find_library('cairo'))
g=ctypes.CDLL(ctypes.util.find_library('gobject-2.0'))
r.rsvg_handle_new_with_flags.argtypes=[ctypes.c_int];r.rsvg_handle_new_with_flags.restype=ctypes.c_void_p
r.rsvg_handle_write.argtypes=[ctypes.c_void_p,ctypes.c_void_p,ctypes.c_size_t,ctypes.c_void_p];r.rsvg_handle_write.restype=ctypes.c_int
r.rsvg_handle_close.argtypes=[ctypes.c_void_p,ctypes.c_void_p];r.rsvg_handle_close.restype=ctypes.c_int
r.rsvg_handle_render_cairo.argtypes=[ctypes.c_void_p,ctypes.c_void_p];r.rsvg_handle_render_cairo.restype=ctypes.c_int
c.cairo_image_surface_create.argtypes=[ctypes.c_int,ctypes.c_int,ctypes.c_int];c.cairo_image_surface_create.restype=ctypes.c_void_p
c.cairo_create.argtypes=[ctypes.c_void_p];c.cairo_create.restype=ctypes.c_void_p
c.cairo_surface_write_to_png.argtypes=[ctypes.c_void_p,ctypes.c_char_p];c.cairo_surface_write_to_png.restype=ctypes.c_int
c.cairo_destroy.argtypes=[ctypes.c_void_p];c.cairo_surface_destroy.argtypes=[ctypes.c_void_p];g.g_object_unref.argtypes=[ctypes.c_void_p]
data=ctypes.create_string_buffer(svg);handle=r.rsvg_handle_new_with_flags(1)
assert r.rsvg_handle_write(handle,data,len(svg),None) and r.rsvg_handle_close(handle,None)
surface=c.cairo_image_surface_create(0,W,H);context=c.cairo_create(surface)
assert r.rsvg_handle_render_cairo(handle,context)
assert c.cairo_surface_write_to_png(surface,str(OUT/'rev-i-to-j.png').encode())==0
c.cairo_destroy(context);c.cairo_surface_destroy(surface);g.g_object_unref(handle)
print('Rev I/J comparison: full original renders arranged at the same image scale')
