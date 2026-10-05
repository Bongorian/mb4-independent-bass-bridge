"""Label and arrange the six CAD renders, preserving the rendered geometry."""
from pathlib import Path
import json, zipfile
from PIL import Image, ImageDraw, ImageFont

ROOT = Path(__file__).resolve().parent.parent
OUT = ROOT / 'six_views'
records = json.loads((OUT/'views.json').read_text())
font_path = '/usr/share/fonts/opentype/noto/NotoSansCJK-Regular.ttc'
font = lambda size: ImageFont.truetype(font_path, size, index=0)
label_font, small_font, title_font = font(34), font(23), font(46)
white = OUT / 'labelled'
white.mkdir(exist_ok=True)
for row in records['views']:
    im = Image.open(OUT/row['file']).convert('RGBA')
    assert im.size == (1600,1200)
    box = im.getchannel('A').getbbox()
    assert box and box[0]>0 and box[1]>0 and box[2]<1600 and box[3]<1200, (row['file'],box)
    canvas = Image.new('RGB', (1680,1340), 'white')
    draw = ImageDraw.Draw(canvas)
    draw.text((40,25), row['label'], font=label_font, fill='#1c2a35')
    draw.text((1200,35), 'MB4 / Rev F / 正投影', font=small_font, fill='#586a77')
    canvas.paste(im,(40,95),im)
    canvas.save(white/row['file'])

sheet = Image.new('RGB',(2480,1590),'#e9edf1')
d = ImageDraw.Draw(sheet)
d.text((40,24), 'MB4 / Rev F — 6面プレビュー', font=title_font, fill='#182c3a')
d.text((42,88), '正投影・同倍率  |  前：ネック側 (-Y)  /  後：調整ネジ側 (+Y)', font=small_font, fill='#526575')
arrangement = [0,1,4,2,3,5]
for pos, idx in enumerate(arrangement):
    row = records['views'][idx]
    x,y = 40+(pos%3)*810, 150+(pos//3)*690
    d.rounded_rectangle((x,y,x+780,y+660), radius=14, fill='white')
    d.text((x+20,y+16), row['label'], font=font(28), fill='#203646')
    im=Image.open(OUT/row['file']).convert('RGBA')
    im.thumbnail((760,570),Image.Resampling.LANCZOS)
    sheet.paste(im,(x+10,y+70),im)
d.text((42,1550), '形状確認用：ボディ・長い弦は非表示。ピエゾは参考外形。CAD形状・金物配置はRev Fのまま。', font=small_font, fill='#526575')
sheet.save(OUT/'MB4_RevF_six_views.png')
(OUT/'README.txt').write_text('MB4 Rev F — six orthographic views\n\n'
    '全6面は同倍率の正投影。前面=-Y、後面=+Y、左面=-X、右面=+X、上面=+Z、下面=-Z。\n'
    'ボディと長い弦の参考表示を非表示。ピエゾとボール端は参考外形。CAD形状の変更なし。\n'
    '下面は上向きに見る方向のため、上面と比べて前後が反転する。\n'
    '寸法を測る場合はSTEP・図面を使用。この画像は寸法図ではない。\n',encoding='utf-8')
with zipfile.ZipFile(ROOT/'MB4_RevF_six_views.zip','w',zipfile.ZIP_DEFLATED) as z:
    for row in records['views']:
        z.write(white/row['file'],row['file'])
    for name in ['MB4_RevF_six_views.png','views.json','README.txt']:
        z.write(OUT/name,name)
    for name in ['render_six_views.py','compose_six_views.py']:
        z.write(ROOT/'cad'/name,'source/'+name)
with zipfile.ZipFile(ROOT/'MB4_RevF_six_views.zip') as z:
    assert z.testzip() is None
print('Six PNGs, overview and ZIP verified.')
