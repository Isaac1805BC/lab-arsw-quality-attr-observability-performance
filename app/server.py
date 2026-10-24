"""Servicio didactico: SQLite real, espera de dependencia emulada, 8 slots."""
import json, os, sqlite3, threading, time, resource
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from collections import Counter
LOCK=threading.Lock(); SLOTS=threading.BoundedSemaphore(8)
STATE={'ready':True,'delay_ms':120}; COUNTS=Counter({'200':0,'503':0,'500':0})
ACTIVE=0; N=0; TOTAL=0.; DB_N=0; DB_SUM=0.
BOUNDS=[.005,.01,.025,.05,.1,.15,.25,.5,1,2,5,float('inf')]; BUCKETS=[0]*len(BOUNDS)
DB=os.getenv('LAB_DB','/tmp/lab.sqlite')
with sqlite3.connect(DB) as c:
 c.execute('CREATE TABLE IF NOT EXISTS boards(id INTEGER PRIMARY KEY,title TEXT)')
 c.execute('INSERT OR IGNORE INTO boards VALUES(1,"Tablero ARSW")')
def metrics():
 with LOCK:
  lines=['# TYPE lab_requests_total counter']+[f'lab_requests_total{{status="{s}"}} {v}' for s,v in COUNTS.items()]
  lines+=['# TYPE lab_request_duration_seconds histogram']
  lines += [f'lab_request_duration_seconds_bucket{{le="{b if b!=float("inf") else "+Inf"}"}} {v}' for b,v in zip(BOUNDS,BUCKETS)]
  lines += [f'lab_request_duration_seconds_count {N}',f'lab_request_duration_seconds_sum {TOTAL}',f'lab_active_requests {ACTIVE}','lab_capacity 8',f'lab_db_queries_total {DB_N}',f'lab_db_query_seconds_total {DB_SUM}',f'lab_process_cpu_seconds_total {time.process_time()}',f'lab_process_peak_resident_memory_bytes {resource.getrusage(resource.RUSAGE_SELF).ru_maxrss*1024}']
  return '\n'.join(lines)+'\n'
class Handler(BaseHTTPRequestHandler):
 def log_message(self,*args):pass
 def send(self,status,data,kind='application/json'):
  body=data.encode() if isinstance(data,str) else json.dumps(data).encode()
  self.send_response(status);self.send_header('Content-Type',kind);self.send_header('Content-Length',str(len(body)));self.end_headers()
  try:self.wfile.write(body)
  except (BrokenPipeError,ConnectionResetError):pass
 def do_POST(self):
  if self.path!='/admin/config':return self.send(404,{})
  if self.headers.get('X-Lab-Token')!='arsw-local':return self.send(403,{})
  try:
   data=json.loads(self.rfile.read(min(int(self.headers.get('Content-Length',0)),2048)))
   if set(data)-{'ready','delay_ms'}:raise ValueError()
   if 'ready' in data and type(data['ready']) is not bool:raise ValueError()
   if 'delay_ms' in data and (type(data['delay_ms']) not in (int,float) or not 0<=data['delay_ms']<=1000):raise ValueError()
   with LOCK:STATE.update(data)
   self.send(200,STATE.copy())
  except (ValueError,TypeError):self.send(400,{'error':'config invalida'})
 def do_GET(self):
  global ACTIVE,N,TOTAL,DB_N,DB_SUM
  if self.path=='/metrics':return self.send(200,metrics(),'text/plain; version=0.0.4')
  if self.path=='/health':return self.send(200,{'alive':True})
  if self.path=='/ready':return self.send(200 if STATE['ready'] else 503,{'ready':STATE['ready']})
  if self.path!='/api/boards/1':return self.send(404,{})
  start=time.perf_counter();acquired=False;status=503;body={'error':'no disponible o capacidad agotada'}
  try:
   if STATE['ready'] and SLOTS.acquire(blocking=False):
    acquired=True
    with LOCK:ACTIVE+=1;delay=STATE['delay_ms']/1000
    time.sleep(delay) # Espera simulada de un servicio externo, NO tiempo SQLite.
    t=time.perf_counter()
    with sqlite3.connect(DB) as c:row=c.execute('SELECT id,title FROM boards WHERE id=1').fetchone()
    dt=time.perf_counter()-t
    with LOCK:DB_N+=1;DB_SUM+=dt
    status=200;body={'id':row[0],'title':row[1]}
  except Exception:status=500;body={'error':'interno'}
  finally:
   elapsed=time.perf_counter()-start
   with LOCK:
    if acquired:ACTIVE-=1
    COUNTS[str(status)]+=1;N+=1;TOTAL+=elapsed
    for i,b in enumerate(BOUNDS):
     if elapsed<=b:BUCKETS[i]+=1
   if acquired:SLOTS.release()
  self.send(status,body)
if __name__=='__main__':ThreadingHTTPServer(('0.0.0.0',int(os.getenv('PORT','8000'))),Handler).serve_forever()
