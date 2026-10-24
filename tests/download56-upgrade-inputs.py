"""Download exact archived test binaries; verify pinned sizes and SHA256."""
import concurrent.futures,hashlib,json,urllib.request
from pathlib import Path
root=Path(__file__).resolve().parents[1]
manifest=json.loads((root/'tests/php56-upgrade-inputs.json').read_text())
base='https://ondrej-ppa-php.program-language.mirror.naxonet.net/ubuntu/pool/main/'
def fetch(item):
 group,name,meta=item
 package=name.split('_')[0]
 if group.startswith('baseline6'):source='p/php5.6'
 elif group=='baseline-extensions':
  ext=package.removeprefix('php5.6-');source='p/php-'+('msgpack-5' if ext=='msgpack' else ext)
 else:source='libz/libzip' if package=='libzip4' else 'p/pcre3'
 dest=root/'out56'/group;dest.mkdir(parents=True,exist_ok=True)
 data=urllib.request.urlopen(base+source+'/'+name,timeout=120).read()
 assert len(data)==meta['size'] and hashlib.sha256(data).hexdigest()==meta['sha256'],name
 (dest/name).write_bytes(data)
items=[(g,n,m) for g,entries in manifest.items() for n,m in entries.items()]
with concurrent.futures.ThreadPoolExecutor(max_workers=6) as pool:list(pool.map(fetch,items))
for group,entries in manifest.items():
 (root/'out56'/group/'SHA256SUMS').write_text(''.join(m['sha256']+'  '+n+'\n' for n,m in entries.items()))
print('Verified',len(items),'archived package inputs')
