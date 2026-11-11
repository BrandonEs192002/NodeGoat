"""Rebuild JSHint bundles with complete patched Lodash, retaining licenses."""
import base64,gzip,hashlib,io,json,pathlib,tarfile,tempfile,urllib.request
versions={'jshint':'2.13.6','lodash':'4.18.1'}
provenance={}
with tempfile.TemporaryDirectory() as temp:
 root=pathlib.Path(temp)
 for name,version in versions.items():
  with urllib.request.urlopen(f'https://registry.npmjs.org/{name}/{version}') as response: meta=json.load(response)
  with urllib.request.urlopen(meta['dist']['tarball']) as response: data=response.read()
  algorithm,digest=meta['dist']['integrity'].split('-',1)
  assert base64.b64encode(hashlib.new(algorithm,data).digest()).decode()==digest
  dest=root/name;dest.mkdir()
  with tarfile.open(fileobj=io.BytesIO(data),mode='r:gz') as archive:archive.extractall(dest,filter='data')
  provenance[name]={'version':version,'url':meta['dist']['tarball'],'integrity':meta['dist']['integrity'],'sha256':hashlib.sha256(data).hexdigest()}
 package=root/'jshint/package'
 lodash=(root/'lodash/package/lodash.js').read_text()
 for filename in ['jshint.js','jshint-rhino.js']:
  p=package/'dist'/filename;s=p.read_text()
  start=s.index('/**\n * @license\n * Lodash')
  end=s.index('\n}).call(this,typeof global',start)
  assert "var VERSION = '4.17.21'" in s[start:end]
  s=s[:start]+lodash.rstrip()+'\n'+s[end:]
  assert "var VERSION = '4.17.21'" not in s
  p.write_text(s)
  provenance[filename]={'sha256':hashlib.sha256(p.read_bytes()).hexdigest()}
 (package/'S07-PATCH.txt').write_text('Upstream JSHint 2.13.6; both browser/Rhino bundles rebuilt with complete Lodash 4.18.1 to remediate CVE-2026-4800 and CVE-2025-13465. Original licenses retained. Source version remains 2.13.6; archive integrity identifies this local patch.\n')
 target=pathlib.Path('vendor/jshint-2.13.6-s07.tgz')
 with target.open('wb') as file:
  with gzip.GzipFile(filename='',mode='wb',fileobj=file,mtime=0) as compressed:
   with tarfile.open(fileobj=compressed,mode='w') as archive:
    for p in sorted(package.rglob('*')):
     if not p.is_file():continue
     info=archive.gettarinfo(str(p),str(p.relative_to(root/'jshint')))
     info.uid=info.gid=0;info.uname=info.gname='';info.mtime=0
     with p.open('rb') as source:archive.addfile(info,source)
 provenance['output']={'file':str(target),'sha256':hashlib.sha256(target.read_bytes()).hexdigest()}
 pathlib.Path('vendor/jshint-provenance.json').write_text(json.dumps(provenance,indent=2)+'\n')
 print(json.dumps(provenance,indent=2))
