"""Ejecutar desde la carpeta estudiantes. Python 3.10+; Docker Compose v2."""
import argparse,datetime,json,pathlib,subprocess,time,urllib.request
ROOT=pathlib.Path(__file__).resolve().parents[1]
def compose(*args,check=True):return subprocess.run(['docker','compose',*args],cwd=ROOT,check=check)
def get(url):
 with urllib.request.urlopen(url,timeout=5) as r:return r.read()
def config(**kwargs):
 req=urllib.request.Request('http://localhost:8000/admin/config',json.dumps(kwargs).encode(),{'Content-Type':'application/json','X-Lab-Token':'arsw-local'})
 print(urllib.request.urlopen(req,timeout=5).read().decode())
def test(profile):
 stamp=datetime.datetime.now(datetime.timezone.utc).strftime('%Y%m%dT%H%M%S%fZ');run=f'{profile}-{stamp}'
 start=datetime.datetime.now(datetime.timezone.utc).isoformat()
 r=compose('run','--rm','-e',f'PROFILE={profile}','-e',f'RUN_ID={run}','k6','run','/scripts/tests.js',check=False)
 end=datetime.datetime.now(datetime.timezone.utc).isoformat()
 (ROOT/'results'/f'{run}-run.json').write_text(json.dumps({'profile':profile,'start_utc':start,'end_utc':end,'exit_code':r.returncode},indent=2))
 if r.returncode not in (0,99):raise SystemExit(f'Error de ejecucion k6: {r.returncode}; revise logs')
 print('Umbrales incumplidos: analizar evidencia.' if r.returncode==99 else 'Umbrales cumplidos.')
p=argparse.ArgumentParser();p.add_argument('action',choices=['prepare','up','doctor','sample','fault','reset','improve','test','down']);p.add_argument('profile',nargs='?',choices=['carga','estres','pico','duracion','all']);a=p.parse_args()
(ROOT/'results').mkdir(exist_ok=True)
if a.action=='prepare':compose('--profile','test','pull','--ignore-buildable');compose('build')
elif a.action=='up':compose('up','-d','--build','app','probe','prometheus','grafana')
elif a.action=='doctor':
 compose('config','--quiet');compose('ps')
 for url in ['http://localhost:8000/api/boards/1','http://localhost:8000/metrics','http://localhost:9090/-/ready','http://localhost:3000/api/health']:
  print(url,get(url)[:180].decode())
 targets=json.loads(get('http://localhost:9090/api/v1/targets'))['data']['activeTargets']
 assert len(targets)==2 and all(t['health']=='up' for t in targets),'Espere 15 s y vuelva a ejecutar doctor'
 print('OK: ambos targets UP. Ejecute prueba carga y compruebe Grafana antes de clase.')
elif a.action=='sample':
 for _ in range(100):get('http://localhost:8000/api/boards/1');time.sleep(.05)
elif a.action=='fault':
 try:config(ready=False);print('Falla de negocio durante 30 s; /metrics sigue disponible.');time.sleep(30)
 finally:config(ready=True)
elif a.action=='reset':config(ready=True,delay_ms=120)
elif a.action=='improve':config(ready=True,delay_ms=60)
elif a.action=='test':
 if not a.profile:p.error('test requiere carga, estres, pico, duracion o all')
 for profile in (['carga','estres','pico','duracion'] if a.profile=='all' else [a.profile]):test(profile)
elif a.action=='down':compose('down')
