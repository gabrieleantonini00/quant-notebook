"""Vendor the existing pinned KaTeX release for offline mathematical typesetting."""
from pathlib import Path
import io
import tarfile
import urllib.request

ROOT = Path(__file__).resolve().parents[1]
raw = urllib.request.urlopen('https://registry.npmjs.org/katex/-/katex-0.16.11.tgz', timeout=45).read()
target = ROOT / 'assets/vendor/katex'
target.mkdir(parents=True, exist_ok=True)
with tarfile.open(fileobj=io.BytesIO(raw), mode='r:gz') as archive:
    for member in archive.getmembers():
        if member.name.startswith('package/dist/') and member.isfile():
            relative = member.name.removeprefix('package/dist/')
            if '..' in Path(relative).parts:
                raise ValueError('Unsafe archive path')
            if relative.endswith('.map'):
                continue
            out = target / relative
            out.parent.mkdir(parents=True, exist_ok=True)
            out.write_bytes(archive.extractfile(member).read())
    for name in ('package/LICENSE', 'package/README.md'):
        (target / name.split('/')[-1]).write_bytes(archive.extractfile(name).read())
print('Local KaTeX 0.16.11 assets ready.')
