# Empiece aquí
1. Lea GUIA.docx o GUIA.md.
2. Antes de clase: python scripts/lab.py prepare
3. Inicie: python scripts/lab.py up
4. Compruebe: python scripts/lab.py doctor
5. Grafana: http://localhost:3000 — admin / arsw-lab-2026
6. Construya paneles con CONSULTAS.md y diligencie ENTREGA.md.

No hay dependencias Python externas. Todos los comandos se ejecutan desde esta carpeta.
Si Python no se reconoce en Windows, use py. Si Docker no conecta, abra Docker Desktop y espere.
Si no hay datos, confirme targets en http://localhost:9090/targets, genere sample y espere un minuto.
Si un puerto está ocupado, cierre el otro servicio. No cambie URLs sin actualizar también los scripts.
Para conservar su tablero exporte el JSON. No use down -v antes de entregar.
Las imágenes fijan versiones de referencia; Python 3.12-slim recibe actualizaciones de parche.

Fuentes técnicas oficiales:
- https://grafana.com/docs/grafana/latest/administration/provisioning/
- https://grafana.com/docs/k6/latest/using-k6/scenarios/executors/ramping-arrival-rate/
- https://grafana.com/docs/k6/latest/using-k6/thresholds/
- https://prometheus.io/docs/practices/histograms/
