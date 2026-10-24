# Hoja de consultas PromQL

Copie cada expresión en el modo Code de Grafana. Construya y justifique los paneles.

## 1 Lectura del servicio
Stat; 0 rojo, 1 verde
```promql
up{job="app"}
```

## 2 Disponibilidad funcional actual
Stat; 0 rojo, 1 verde
```promql
lab_probe_success
```

## 3 Disponibilidad observada en 5 minutos
Porcentaje 0–100
```promql
100 * increase(lab_probe_successes_total[5m]) / increase(lab_probe_attempts_total[5m])
```

## 4 Errores HTTP
Porcentaje; línea de referencia 1
```promql
100 * sum(rate(lab_requests_total{status=~"5.."}[1m])) / sum(rate(lab_requests_total[1m]))
```

## 5 Throughput total
Solicitudes/s; incluye respuestas fallidas
```promql
sum(rate(lab_requests_total[1m]))
```

## 6 P95 del servidor
Segundos; referencia 0.5
```promql
histogram_quantile(0.95, sum by (le) (rate(lab_request_duration_seconds_bucket[1m])))
```

## 7 Ocupación de capacidad
Porcentaje 0–100; muestra cada 5 s
```promql
100 * lab_active_requests / lab_capacity
```

## 8 CPU del proceso
Porcentaje de un núcleo; puede superar 100
```promql
100 * rate(lab_process_cpu_seconds_total[1m])
```

## Opcional SQLite
Tiempo medio real de consulta, en segundos:
```promql
rate(lab_db_query_seconds_total[1m]) / rate(lab_db_queries_total[1m])
```
Este valor NO incluye la espera artificial de la dependencia.
