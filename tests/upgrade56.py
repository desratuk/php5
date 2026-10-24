"""State and packaged-FPM checks for disposable upgrade/rollback containers."""
import hashlib,json,os,socket,stat,struct,subprocess,sys,time
from pathlib import Path
out=Path('/out')
def run(*args):return subprocess.check_output(args).decode()
def snapshot(label):
 files={}
 for p in sorted(Path('/etc/php/5.6').rglob('*')):
  s=p.lstat();v={'mode':stat.S_IMODE(s.st_mode),'uid':s.st_uid,'gid':s.st_gid}
  if p.is_symlink():v['target']=os.readlink(p)
  elif p.is_file():v['sha256']=hashlib.sha256(p.read_bytes()).hexdigest()
  else:continue
  files[str(p)]=v
 packages=dict(l.split('\t') for l in run('dpkg-query','-W','-f=${binary:Package}\t${Version}\n').splitlines())
 separate={}
 for ext in ('igbinary','imagick','memcached','msgpack','redis'):
  p=Path('/usr/lib/php/20131226')/(ext+'.so');assert p.is_file(),p
  separate[ext]=hashlib.sha256(p.read_bytes()).hexdigest()
 data={'configs':files,'packages':packages,'extensions':separate,'cli_modules':run('php5.6','-m'),'fpm_modules':run('php-fpm5.6','-m'),'version':run('php5.6','-r','echo PHP_VERSION;')}
 (out/(label+'.json')).write_text(json.dumps(data,indent=2))
def compare(label):
 before=json.loads((out/'before.json').read_text());after=json.loads((out/(label+'.json')).read_text())
 assert all(after['configs'].get(k)==v for k,v in before['configs'].items()),'Original config content/metadata changed'
 for k in ('extensions','cli_modules','fpm_modules'):assert before[k]==after[k],k+' changed'
 core={'php5.6-'+x for x in 'bcmath cli common curl dev fpm gd gmp imap intl json mbstring mcrypt mysql opcache pgsql readline soap sqlite3 xml zip'.split()}
 for name,ver in before['packages'].items():
  if label=='upgraded' and name.split(':')[0] in core:assert after['packages'][name]=='5.6.40-105+tlb1~ubuntu20.04.1',name
  else:assert after['packages'].get(name)==ver,('Package changed',name)
 if label=='rollback':
  assert before==after,'Rollback did not restore exact baseline snapshot'
 (out/(label+'-preservation.json')).write_text(json.dumps({'status':'passed','original_config_entries':len(before['configs']),'config_content_ownership_modes_symlinks':'preserved','cli_fpm_modules':'unchanged','five_separate_extension_packages_and_binaries':'unchanged','package_state':'exact baseline' if label=='rollback' else '21 core upgrades; previous other packages unchanged'},indent=2))
def fpm(label):
 subprocess.run(['php-fpm5.6','-t'],check=True)
 root=Path('/tmp/upgrade56');root.mkdir(exist_ok=True);root.chmod(0o755)
 probe=root/'probe.php'
 probe.write_text('''<?php
$a=array('probe'=>42);$i=new Imagick();$i->newImage(1,1,new ImagickPixel('white'));
if (igbinary_unserialize(igbinary_serialize($a))!==$a || msgpack_unpack(msgpack_pack($a))!==$a || !($m=new Memcached()) || !($r=new Redis()) || $i->getImageWidth()!==1) { http_response_code(500); exit('extension failure'); }
echo json_encode(array('version'=>PHP_VERSION,'memory_limit'=>ini_get('memory_limit'),'extensions'=>'passed'));
''');probe.chmod(0o644)
 sock=Path('/run/php/php5.6-fpm.sock');proc=subprocess.Popen(['php-fpm5.6','-F'])
 try:
  for _ in range(100):
   if sock.exists():break
   assert proc.poll() is None,'Packaged FPM exited'
   time.sleep(.1)
  assert Path('/run/php/php5.6-fpm.pid').read_text().strip()==str(proc.pid),'PID file mismatch'
  params={'SCRIPT_FILENAME':str(probe),'REQUEST_METHOD':'GET','SERVER_PROTOCOL':'HTTP/1.1','GATEWAY_INTERFACE':'CGI/1.1','SERVER_NAME':'localhost','SERVER_PORT':'80'}
  data=b''.join(bytes([len(k),len(v)])+k.encode()+v.encode() for k,v in params.items())
  def record(kind,b):return struct.pack('!BBHHBB',1,kind,1,len(b),0,0)+b
  with socket.socket(socket.AF_UNIX) as s:
   s.settimeout(15);s.connect(str(sock));s.sendall(record(1,struct.pack('!HB5x',1,0))+record(4,data)+record(4,b'')+record(5,b''));raw=b''
   def read(n):
    b=b''
    while len(b)<n:
     x=s.recv(n-len(b));assert x,'Unexpected EOF';b+=x
    return b
   while True:
    _,kind,_,length,pad,_=struct.unpack('!BBHHBB',read(8));part=read(length);read(pad)
    if kind==6:raw+=part
    if kind==3:break
  result=json.loads(raw.split(b'\r\n\r\n',1)[1]);assert result['version']==run('php5.6','-r','echo PHP_VERSION;');assert result['memory_limit']=='192M';assert result['extensions']=='passed'
  (out/(label+'-packaged-fpm.json')).write_text(json.dumps(result,indent=2))
 finally:
  proc.terminate();proc.wait(timeout=10)
if sys.argv[1]=='snapshot':snapshot(sys.argv[2])
elif sys.argv[1]=='compare':compare(sys.argv[2])
elif sys.argv[1]=='fpm':fpm(sys.argv[2])
