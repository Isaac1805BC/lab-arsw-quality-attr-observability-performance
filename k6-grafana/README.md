# Ver resultados JSON de k6 en Grafana

Complemento docente del laboratorio ARSW. Lee los JSON que ya están en results/ y los futuros, sin volver a ejecutar las pruebas. No instala paquetes pip ni complementos de Grafana. Conserva los archivos originales y los tableros del estudiante.

## Instalación en Mac con zsh
Descomprima este ZIP y copie la carpeta k6-grafana dentro de estudiantes, al mismo nivel de compose.yaml y results. Abra la terminal en estudiantes con Docker Desktop en ejecución.

```zsh
source .venv/bin/activate
python k6-grafana/install.py
docker compose up -d --build k6-results
docker compose restart prometheus grafana
```

Si el entorno no está creado: python3 -m venv .venv y luego source .venv/bin/activate. El instalador puede ejecutarse otra vez. Conserva un respaldo de prometheus.yml y se detiene si encuentra un override de Compose ajeno al complemento.

Espere unos 15 segundos. Abra http://localhost:3000 y vaya a Dashboards > ARSW Docente > k6 Resultados por ejecucion. Usuario admin, contraseña arsw-lab-2026 (si no la cambió). Seleccione Perfil y Ejecución. Se incluyen todas por defecto. Si una ejecución nueva no aparece en el selector, recargue la página para actualizar sus opciones.

## Qué verá
- P95, P99, tasa de errores, throughput medio y número de solicitudes por ejecución.
- Verificaciones correctas, iteraciones descartadas y estado de los umbrales.
- Fecha de finalización UTC, tomada del archivo compañero -run.json.
- Cantidad de resúmenes leídos y archivos que todavía no se pueden interpretar.

Cada JSON de métricas es una ejecución; el archivo -run.json aporta fechas y código de salida, no es otra prueba. Los nombres de las ejecuciones son los nombres de archivo, incluidos los de antes/después. Los archivos en escritura se reintentan en la siguiente lectura. No se incluyen resultados inventados.

El camino es: results/*.json → lector Python → Prometheus → Grafana. El lector monta results/ en modo solo lectura y no publica un puerto en el Mac.

## Alcance de la lectura
Estos archivos se generaron con handleSummary(): contienen estadísticas agregadas al finalizar cada prueba. No contienen las muestras individuales necesarias para reconstruir una curva de latencia segundo a segundo. Las barras son resultados finales, no tráfico actual. El rango de tiempo de Grafana NO filtra la fecha de ejecución; use los filtros de perfil y ejecución. Las muestras de Prometheus indican cuándo se leyó el resumen, no cuándo ocurrió cada solicitud.

La tasa de errores es una fracción presentada como porcentaje; 0.01 es 1 %. La tasa de verificaciones también se presenta como porcentaje. El throughput incluye respuestas fallidas. Los percentiles se muestran en ms. La ausencia de un campo no se rellena con un resultado exitoso. dropped_iterations ausente se interpreta como cero, según el comportamiento esperado de estos scripts k6.

El estado de umbrales corresponde a todos los umbrales que k6 incluyó en su resumen. El rojo en estrés o pico no significa una mala entrega. Las referencias de color reflejan los objetivos didácticos originales del kit; si modifica los objetivos, debe ajustar también el tablero.

Una serie por ejecución es apropiada para este laboratorio local. Archive JSON antiguos fuera de results/ si acumula muchos; no es un diseño de almacenamiento ilimitado para producción. Los resúmenes reaparecen tras reiniciar Prometheus mientras sigan en results/.

## Diagnóstico
```zsh
docker compose ps
docker compose logs --tail=50 k6-results
docker compose exec k6-results python -c 'import urllib.request; print(urllib.request.urlopen("http://localhost:9102/metrics").read().decode())'
```
En http://localhost:9090/targets debe aparecer k6-results como UP.
En Grafana Explore, consulte lab_k6_summary_files con la fuente Prometheus.
Si hay cero archivos, compruebe que los JSON están directamente en estudiantes/results/ y no en otra subcarpeta. Si el contador de inválidos persiste, compruebe que son resúmenes del kit y no archivos JSON de salida en tiempo real. Si no aparece el dashboard, revise docker compose logs --tail=80 grafana y reinicie Grafana.

## Si ya existe un override de Compose
El instalador se detiene para no sobrescribirlo. Integre este servicio en el override existente:
```yaml
services:
  k6-results:
    build: ./k6-grafana
    volumes:
      - ./results:/results:ro
```
Agregue este job dentro de scrape_configs en monitoring/prometheus.yml:
```yaml
  - job_name: k6-results
    static_configs:
      - targets: ['k6-results:9102']
```
Luego levante k6-results, reinicie Prometheus e importe manualmente k6-grafana/dashboard.json en Grafana (Dashboards > New > Import). No necesita el instalador ni el proveedor automático en esta alternativa.

## Validación
Se probaron localmente lectura, unidades, etiquetas, JSON incompletos, metadatos, instalación repetida y preservación de archivos. El entorno de autoría no dispone de Docker: queda por comprobar la integración y el aspecto final del tablero en el Grafana del equipo del usuario.

Referencias oficiales:
https://grafana.com/docs/k6/latest/results-output/end-of-test/custom-summary/
https://prometheus.io/docs/instrumenting/writing_exporters/
https://grafana.com/docs/grafana/latest/administration/provisioning/
