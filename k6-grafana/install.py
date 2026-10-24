"""Run from estudiantes: python k6-grafana/install.py. No pip required."""
from pathlib import Path
import shutil
HERE=Path(__file__).resolve().parent
ROOT=HERE.parent
PROM=ROOT/'monitoring/prometheus.yml'
OVERRIDE=ROOT/'compose.override.yaml'
MARK='# ARSW k6 JSON addon'
expected=[ROOT/'compose.yaml',ROOT/'results',PROM,ROOT/'monitoring/grafana/datasources/prometheus.yaml']
if not all(p.exists() for p in expected):raise SystemExit('Coloque la carpeta k6-grafana dentro de estudiantes, junto a compose.yaml y results/.')
conf=PROM.read_text()
if 'scrape_configs:' not in conf:raise SystemExit('No se reconoce prometheus.yml. No se modifico nada.')
# Avoid shadowing an existing, potentially user-authored override.
for name in ['compose.override.yaml','compose.override.yml','docker-compose.override.yml','docker-compose.override.yaml']:
 p=ROOT/name
 if p.exists() and (p!=OVERRIDE or MARK not in p.read_text()):raise SystemExit(f'Ya existe {name}. No se sobrescribe. Integre el servicio indicado en README.md manualmente.')
if 'job_name: k6-results' in conf and MARK not in conf:raise SystemExit('Ya existe un job k6-results ajeno a este complemento. No se modifico nada.')
provider=ROOT/'monitoring/grafana/dashboards/arsw-k6.yaml'
dashboard=ROOT/'monitoring/grafana/k6-dashboards/arsw-k6-resumen.json'
for p in (provider,dashboard):
 if p.exists() and not (ROOT/'.arsw-k6-installed').exists():raise SystemExit(f'Ya existe {p.name}; no se sobrescribe.')
if MARK not in conf:
 backup=PROM.with_name('prometheus.yml.before-k6')
 if not backup.exists():shutil.copy2(PROM,backup)
 PROM.write_text(conf.rstrip()+'\n  '+MARK+'\n  - job_name: k6-results\n    static_configs:\n      - targets: ["k6-results:9102"]\n')
OVERRIDE.write_text(MARK+'\nservices:\n  k6-results:\n    build: ./k6-grafana\n    volumes:\n      - ./results:/results:ro\n')
provider.parent.mkdir(parents=True,exist_ok=True)
provider.write_text('''apiVersion: 1
providers:
  - name: ARSW k6 summaries
    orgId: 1
    folder: ARSW Docente
    type: file
    disableDeletion: true
    updateIntervalSeconds: 10
    allowUiUpdates: false
    options:
      path: /etc/grafana/provisioning/k6-dashboards
''')
dashboard.parent.mkdir(parents=True,exist_ok=True);shutil.copy2(HERE/'dashboard.json',dashboard)
(ROOT/'.arsw-k6-installed').write_text('1\n')
print('Complemento instalado; results/ y los tableros existentes se conservan.')
print('Ahora ejecute:')
print('docker compose up -d --build k6-results')
print('docker compose restart prometheus grafana')
print('Luego abra http://localhost:3000 > Dashboards > ARSW Docente > k6 Resultados por ejecucion')
