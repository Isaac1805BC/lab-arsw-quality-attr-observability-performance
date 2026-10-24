# Evidencia del laboratorio ARSW
Equipo: ___ · Integrantes: ___ · Fecha: ___
Equipo anfitrión, SO, CPU, RAM y recursos asignados a Docker: ___
Versiones Docker/Compose: ___ · Hipótesis: ___

## Tablero y disponibilidad
Nombre del dashboard: ___
Hora UTC de falla/recuperación: ___ · Ventana: ___
Disponibilidad observada: ___ % · Recuperación aproximada: ___ s
Interpretación de up y sonda: ___

## Pruebas
| Ejecución y hora UTC | Tasa ofrecida req/s | Throughput req/s | P95 k6 ms | P95 servidor s y ventana | Error % | Iteraciones descartadas | Recuperación observada |
|---|---|---|---|---|---|---|---|
| carga | 20 | | | | | | |
| estres base | 20–120–20 | | | | | | |
| pico | 20–160–20 | | | | | | |
| duracion | 20 | | | | | | |
| estres mejora | 20–120–20 | | | | | | |

## Comparación controlada
Predicción: ___
Qué cambió y qué se mantuvo: ___
Evidencia antes/después: ___
Conclusión y limitación: ___

## Preguntas integradas
1. P95 frente a promedio: ___
2. Disponibilidad funcional frente a lectura de métricas: ___
3. Cuatro tipos de prueba y sus observaciones: ___
4. CPU, espera, cupos, tasa y VUs: ___
5. Mejora y siguiente experimento: ___

## Archivos incluidos
- dashboard.json
- results/ (cinco ejecuciones; métricas y tiempos)
- capturas/ (normal, falla y comparación)
