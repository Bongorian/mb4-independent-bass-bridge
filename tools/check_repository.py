"""Verify documentation links and preserved release assets; no CAD dependencies."""
from pathlib import Path
import hashlib, json, re, zipfile
from urllib.parse import unquote, urlsplit

ROOT = Path(__file__).resolve().parent.parent

def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()

def main():
    records = json.loads((ROOT / 'revisions/file-manifest.json').read_text())
    for row in records['files']:
        p = ROOT / row['path']
        assert p.is_file(), row['path']
        assert p.stat().st_size == row['size_bytes'], row['path']
        assert sha(p) == row['sha256'], row['path']
    print(f"Preserved revision assets: {len(records['files'])} SHA-256 matches")

    for rev in 'ABCDEFGHIJKL':
        folder = ROOT / 'revisions' / rev
        assert (folder / 'bridge_preview.png').is_file(), rev
        assert (folder / 'cad/build_bridge.py').is_file(), rev
        assert list((folder / 'cad/step').glob('*.step')), rev
        assert list((folder / 'pdf').glob('*.pdf')), rev
    print('Revision A-L: source, preview, STEP and PDF present')

    markdown = [ROOT / 'README.md', *sorted((ROOT / 'docs').rglob('*.md')),
                ROOT / 'downloads/README.md']
    links = 0
    for p in markdown:
        for value in re.findall(r'!?\[[^\]]*\]\(([^)]+)\)', p.read_text()):
            target = value.split(' "', 1)[0].strip('<>')
            parsed = urlsplit(target)
            if parsed.scheme or not parsed.path:
                continue
            local = p.parent / unquote(parsed.path)
            assert local.exists(), f'{p.relative_to(ROOT)} -> {target}'
            links += 1
    print(f'Local documentation links: {links} valid')

    latest=records.get('latest_revision','I')
    r = ROOT / 'revisions' / latest
    expected = {f'{name}.{ext}' for name in records['latest_parts']
                for ext in ('step', 'pdf')}
    package = ROOT / f'downloads/MB4_JLCCNC_upload_Rev{latest}.zip'
    with zipfile.ZipFile(package) as z:
        assert z.testzip() is None
        assert set(z.namelist()) == expected
        for name in expected:
            path = r / ('cad/step' if name.endswith('.step') else 'pdf') / name
            assert z.read(name) == path.read_bytes(), name
    with zipfile.ZipFile(ROOT / f'downloads/MB4_Rev{latest}_six_views.zip') as z:
        assert z.testzip() is None
        for name in ('01_front.png', '02_rear.png', '03_left.png', '04_right.png',
                     '05_top.png', '06_bottom.png', f'MB4_Rev{latest}_six_views.png'):
            assert name in z.namelist(), name
    print(f'Rev {latest} ZIPs: CRC passed; quotation STEP/PDF match canonical files')

    p = json.loads((r / 'cad/parameters.json').read_text())
    assert p['base_length'] == 86 and p['anchor_length'] == 55
    assert p['intonation_bolt_length'] == 45
    sweep = json.loads((r / 'cad/travel_sweep_check.json').read_text())
    assert sweep['q_max'] - sweep['q_min'] == 20
    assert sweep['positions_checked'] == 21
    print(f'Latest revision: {latest} / base86 / anchor55 / bolt45 / travel20 verified')

if __name__ == '__main__':
    main()
