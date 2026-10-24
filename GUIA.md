# Laboratorio de observabilidad y pruebas de rendimiento

ARSW · Escuela Colombiana de Ingeniería Julio Garavito · 2026-2

Duración: 105 minutos. Trabajo en parejas. Entrega al terminar la sesión.
Este laboratorio integra los puntos del taller; no hay una entrega adicional.

## Propósito y escenario
El equipo administra una API de consulta de tableros. Debe demostrar cuándo está disponible, qué rendimiento ofrece y cómo se comporta bajo diferentes cargas. Construya un tablero en Grafana y tome decisiones con evidencia de k6. No necesita programar la aplicación ni instalar complementos de Grafana.

La API Python consulta una base SQLite real y emula una dependencia con una espera de 120 ms. Tiene ocho cupos simultáneos; al agotarse rechaza solicitudes con HTTP 503. La espera es simulada y no corresponde al tiempo de la consulta SQLite. Prometheus recoge métricas cada cinco segundos; una sonda independiente consulta /ready aproximadamente cada dos segundos. Grafana consulta Prometheus. k6 genera tráfico hacia la API.

Objetivo didáctico para carga normal de 20 solicitudes/s: P95 menor de 500 ms, menos de 1 % de errores y más de 99 % de verificaciones correctas. Estos son criterios del ejercicio, no acuerdos contractuales de producción.

## Preparación antes de clase
En un equipo por pareja: Docker Engine o Docker Desktop en ejecución con contenedores Linux y Compose v2, Python 3.10 o superior, navegador y acceso a Internet para la primera descarga. Presupuesto sugerido: 4 GB de RAM disponibles para Docker y 3 GB de disco. No se necesita cuenta en Grafana Cloud ni instalar k6 en el equipo.

Descomprima el kit; abra una terminal en la carpeta estudiantes. En Windows puede usar py en lugar de python. Ejecute, en este orden:

```sh
python scripts/lab.py prepare
python scripts/lab.py up
python scripts/lab.py doctor
```

Espere unos 15 segundos antes de doctor. Si aún hay servicios iniciando, espere y repita. Abra http://localhost:3000 con usuario admin y contraseña arsw-lab-2026. Prometheus ya está configurado como fuente de datos; no hay tablero resuelto. API: http://localhost:8000/api/boards/1. Prometheus: http://localhost:9090.

Compruebe la instalación antes de la sesión. Los puertos 3000, 8000 y 9090 deben estar libres. Use únicamente este entorno local para las pruebas. Las credenciales son didácticas y los puertos están publicados en localhost.

## Distribución de los 105 minutos
| Minutos | Actividad | Evidencia |
|---|---|---|
| 0–10 | Arranque y comprobación | Servicios disponibles |
| 10–35 | Construcción del tablero | Ocho paneles con unidades |
| 35–45 | Falla y recuperación | Captura y explicación |
| 45–70 | Cuatro pruebas automatizadas | Resultados JSON y tabla |
| 70–85 | Experimento de mejora | Comparación antes y después |
| 85–100 | Análisis integrado | Respuestas y conclusión |
| 100–105 | Exportación y entrega | ZIP completo |

## Parte 1 Construir el tablero y observar disponibilidad
1. Ejecute python scripts/lab.py sample para generar tráfico inicial.
2. En Grafana, entre a Dashboards, New dashboard y Add visualization. Seleccione Prometheus; cambie la consulta a Code para pegar PromQL. Cree los ocho paneles de la hoja CONSULTAS.md. Elija Stat para estados y Time series para tendencias. Configure las unidades y las referencias indicadas.
3. Guarde el tablero como ARSW Observabilidad Equipo XX. Use rango de últimos 15 minutos y actualización de 5 segundos. No convierta ausencia de datos en cero: sin tráfico no hay P95 ni porcentaje de errores significativo.
4. Ejecute python scripts/lab.py fault. Durante 30 segundos la API y /ready fallan, pero /metrics sigue respondiendo. Observe el contraste entre up y lab_probe_success. Capture el intervalo de falla y recuperación. Genere tráfico con sample después de recuperarse.
5. Registre disponibilidad observada, intervalo de falla y tiempo aproximado hasta que la sonda vuelve a 1. Explique por qué up=1 no demuestra disponibilidad funcional. No confunda el tiempo de recuperación medido con MTTR histórico.

La disponibilidad de esta práctica es el porcentaje de sondeos exitosos dentro de la ventana de cinco minutos, no un SLA mensual ni una medición de todas las transacciones. Las consultas rate e increase requieren varias muestras. Deje transcurrir al menos un minuto para interpretar tendencias. La resolución de cinco segundos puede ocultar picos breves de ocupación.

## Parte 2 Ejecutar y comparar pruebas de carga
Revise k6/tests.js. Cada iteración envía una solicitud y verifica tanto HTTP 200 como el id del tablero. Los perfiles usan una tasa de llegada; VUs son trabajadores disponibles para sostenerla, no la tasa misma. Ejecute los cuatro escenarios secuencialmente:

```sh
python scripts/lab.py reset
python scripts/lab.py test all
```

| Perfil | Tráfico ofrecido | Duración | Pregunta experimental |
|---|---|---|---|
| carga | 20 solicitudes/s | 1 min | ¿Cumple el objetivo normal? |
| estres | 20 → 60 → 120 → 20 solicitudes/s | 2 min | ¿Cuándo se degrada y se recupera? |
| pico | 20 → 160 → 20 solicitudes/s | 90 s | ¿Tolera un aumento abrupto? |
| duracion | 20 solicitudes/s | 4 min | ¿Hay deriva visible a carga constante? |

La suite tarda aproximadamente nueve minutos, incluidos cierres. La duración es una versión reducida de una prueba de resistencia o soak: cuatro minutos no permiten concluir estabilidad durante horas, ausencia de fugas ni fiabilidad de producción.

Cada ejecución crea un JSON de métricas y un archivo -run.json con inicio y fin UTC. No borre los resultados originales. El código 99 de k6 indica umbrales incumplidos; es evidencia esperable en estrés o pico. Otro código exige revisar la ejecución. No se califica que todo quede verde, sino que el experimento y la interpretación sean correctos.

Complete la tabla de ENTREGA.md para los cuatro perfiles. En el JSON use metrics.http_req_duration.values["p(95)"] (milisegundos), http_req_failed.values.rate (fracción), http_reqs.values.rate (solicitudes/s) y dropped_iterations.values.count, si existe. Si no existe dropped_iterations, registre 0. Si es mayor que cero, el generador no logró iniciar toda la carga programada: no atribuya automáticamente el resultado a la API.

Compare las ventanas exactas de las pruebas en Grafana con las horas UTC registradas. El P95 de k6 mide desde el cliente; el histograma del servidor estima el tiempo interno, excluye parte del transporte y usa intervalos. No tienen por qué ser idénticos. El P95 global de un escenario tampoco equivale al promedio de sus P95 por minuto.

## Experimento de mejora
Use la primera prueba de estrés como línea base. Prediga qué ocurrirá al reducir la espera simulada de la dependencia a 60 ms, manteniendo ocho cupos y el mismo perfil. Ejecute:

```sh
python scripts/lab.py improve
python scripts/lab.py test estres
python scripts/lab.py reset
```

Compare errores, throughput, P95 y recuperación antes y después. Mantenga equipo, perfil, versión y configuración restante iguales. Una aproximación de capacidad es cupos / tiempo de servicio: 8/0.12 ≈ 67 solicitudes/s frente a 8/0.06 ≈ 133; son referencias teóricas, no resultados garantizados. Esta intervención emula una mejora en la dependencia; no demuestra una optimización real de SQLite ni escalamiento horizontal.

## Preguntas integradas del taller
Responda en ENTREGA.md, en dos o tres frases por pregunta, usando sus evidencias:
1. ¿Qué significa P95 y por qué un promedio bajo puede esconder solicitudes lentas? Interprete su P95 de carga con unidad y ventana.
2. Durante la falla, ¿por qué up puede valer 1 y el sondeo funcional 0? ¿Cuál usaría para informar al usuario sobre disponibilidad?
3. ¿Cuál es la diferencia entre carga, estrés, pico y duración? Vincule cada prueba con una observación concreta.
4. Si CPU está baja y aumentan rechazos, ¿qué otra limitación puede existir en esta API? Relacione espera, cupos, tasa y VUs.
5. ¿La mejora cumplió su predicción? ¿Qué experimento adicional necesitaría para afirmar escalabilidad o estabilidad prolongada?

## Entrega en clase y evaluación
Entregue un solo ZIP llamado ARSW_Lab_EquipoXX.zip con ENTREGA.md diligenciado, dashboard.json exportado, carpeta results completa y tres capturas: tablero normal, falla/recuperación y estrés antes/después (esta última puede ser una composición de dos capturas). Incluya nombres de integrantes y características del equipo. No entregue volúmenes de Docker ni una captura como sustituto del JSON.

En Grafana, abra el tablero guardado y use la opción de exportar JSON en Settings/JSON Model o Export, según la interfaz. Guarde como dashboard.json. Verifique que puede importarlo en Dashboards, New, Import y que conserva Prometheus como fuente. Exporte antes de borrar volúmenes. El comando python scripts/lab.py down apaga los servicios y conserva el volumen de Grafana; no conserva el histórico de Prometheus al recrearlo.

| Criterio | Puntos sobre 5 | Evidencia de logro |
|---|---|---|
| Arranque reproducible | 0.50 | Configuración, equipo e identificación |
| Tablero de observabilidad | 1.50 | Ocho paneles correctos, unidades y rangos |
| Disponibilidad y recuperación | 0.75 | Falla observada y distinción up/sondeo |
| Cuatro pruebas automatizadas | 1.00 | Perfiles, JSON y tabla completos |
| Mejora y análisis integrado | 1.00 | Comparación controlada y cinco respuestas |
| Entrega reproducible | 0.25 | JSON importable y archivos organizados |

Crédito parcial por evidencia correcta aunque un umbral falle. Panel sin unidad o consulta incorrecta no obtiene el puntaje completo. Las conclusiones deben reconocer limitaciones y no inventar mediciones.
