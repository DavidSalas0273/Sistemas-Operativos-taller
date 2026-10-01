# Taller de Sistemas Operativos — Gestión de Memoria y Procesos

Colección de 4 scripts en Python que demuestran conceptos fundamentales de Sistemas Operativos: gestión de memoria, jerarquía de caché, paginación virtual y planificación de procesos.

**Requisito único:** `pip install psutil`

---

##Estructura del proyecto

```
Sistemas-Operativos-taller/
├── 1_vigilante_recursos.py   → Monitor de RAM/CPU en tiempo real
├── 2_simulador_cache.py      → Simulación de jerarquía de caché
├── 3_estres_memoria.py       → Forzar paginación virtual (Swap)
├── 4_prioridad_procesos.py   → Scheduling y prioridad de procesos
└── README.md
```

---

## 1. Vigilante de Recursos — Monitor de RAM y CPU

**Concepto:** Gestor de memoria y E/S del SO.

### ¿Qué hace?
Panel de control en tiempo real que muestra cada 2 segundos:
- Uso de CPU global y por núcleo (con barras de color verde/amarillo/rojo)
- RAM total, usada y disponible
- Memoria virtual / Swap
- I/O acumulado de disco y red

Cuando la **RAM supera el 80%** escribe automáticamente una línea en `recursos_log.txt`, simulando el sistema de alertas de un SO.

### Cómo ejecutarlo
```bash
python 1_vigilante_recursos.py
# Presiona Ctrl+C para salir
```

### Resultado de prueba
```
=======================================================
   🖥  VIGILANTE DE RECURSOS — Panel de Control SO
=======================================================

  CPU total: [████████░░░░░░░░░░░░░░░░░░░░░░]  27.3%
    Núcleo 0: [████████████░░░░░░░░] 41.2%
    Núcleo 1: [████░░░░░░░░░░░░░░░░] 14.1%
    ...

  RAM total : [████████████░░░░░░░░░░░░░░░░░░]  42.1%
    Total   : 15.84 GB
    Usada   : 6.67 GB
    Libre   : 9.17 GB

  SWAP/Virtual: [░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░]   0.0%

  Disco  — Lecturas: 4821.3 MB   Escrituras: 2103.7 MB
  Red    — Enviado: 312.4 MB     Recibido: 891.2 MB
```
**Log generado en `recursos_log.txt` cuando RAM > 80%:**
```
[2026-09-30 14:23:11] ⚠ ALERTA RAM  RAM: 83.4%  |  CPU: 61.2%
```

---

## 2. Simulador de Memoria Caché (L1/L2 vs RAM)

**Concepto:** Jerarquía de memoria y optimización.

### ¿Qué hace?
Implementa una caché en memoria usando un diccionario de Python. Lee un archivo de 20 MB y demuestra la diferencia de velocidad entre:
- **MISS (1ª lectura):** accede al disco físico — lento.
- **HIT (lecturas siguientes):** devuelve el dato desde la RAM — casi instantáneo.

Verifica además la integridad del contenido con hash MD5.

### Cómo ejecutarlo
```bash
python 2_simulador_cache.py
```

### Resultado de prueba
```
── LECTURA #1: CACHE MISS (lee del DISCO) ──────────────
  ⏱  [DISCO  ]  Tiempo:    32.963 ms  — 20.00 MB leídos

── LECTURAS #2-6: CACHE HIT (lee de la RAM) ─────────
  ⏱  [CACHÉ 1]  Tiempo:     0.003 ms  — 20.00 MB leídos
  ⏱  [CACHÉ 2]  Tiempo:     0.001 ms  — 20.00 MB leídos
  ⏱  [CACHÉ 3]  Tiempo:     0.000 ms  — 20.00 MB leídos
  ⏱  [CACHÉ 4]  Tiempo:     0.000 ms  — 20.00 MB leídos
  ⏱  [CACHÉ 5]  Tiempo:     0.000 ms  — 20.00 MB leídos

============================================================
  RESULTADO COMPARATIVO
============================================================
  Disco  (1ª lectura):              32.963 ms
  Caché  (promedio 5 lecturas):      0.001 ms
  Aceleración (speedup):          34,336.7x más rápido

  ✓ Integridad OK — disco y caché devuelven el mismo contenido.
```

> **Conclusión:** La caché en RAM es ~34,000x más rápida que el disco. El SO aplica exactamente esta técnica con el *page cache* para evitar accesos constantes al almacenamiento secundario.

---

## 3. Estrés de Memoria y Salto a la Virtual (Paginación)

**Concepto:** Memoria Virtual y Archivo de Paginación (Swap).

### ¿Qué hace?
Llena progresivamente una lista con millones de strings en un bucle, forzando al SO a agotar la RAM física y comenzar a usar la memoria virtual (Swap/página). Incluye un **límite de seguridad de 1,500 MB** para no bloquear la máquina.

Muestra en pantalla las 3 fases del proceso de paginación:
- **Fase 1:** Todo en RAM física (rápido)
- **Fase 2:** Paginación iniciada, RAM física casi llena
- **Fase 3:** Alta paginación, usando memoria virtual (lento)

### Cómo ejecutarlo
```bash
# Abre el Administrador de Tareas (Ctrl+Shift+Esc) ANTES de correr
python 3_estres_memoria.py
# Ctrl+C para detener de forma segura
```

>  **Advertencia:** El script se detiene automáticamente al llegar a 1,500 MB. Al salir libera toda la memoria consumida.

### Resultado de prueba
```
  Iteración : 847   |   Tiempo: 14.3s
  Items en lista : 42,350,000  ≈ 8,470.0 MB lógicos

  RAM del proceso (RSS)  :   1,421.8 MB
  Límite de seguridad    :   1,500   MB
  [████████████████████████████░░] 94.8%

  RAM sistema  : [████████████████████████░░░░░░]  82.3%
    Usada  :   13,030 MB / 15.8 GB
    Libre  :    2,810 MB

  SWAP/Virtual : [██████░░░░░░░░░░░░░░░░░░░░░░░░]  19.7%
    Usada  :    3,218 MB / 16.4 GB

   Fase 2: Paginación iniciada — RAM física casi llena
```
**Al terminar:**
```
    LÍMITE ALCANZADO (1500 MB) — deteniendo.
  Liberando 1,498 MB de RAM...
  Memoria liberada. El SO recuperará las páginas.
  RAM sistema ahora: 7,842 MB usados (49.5%)
```

---

## 4. Prioridad de Procesos (Scheduling)

**Concepto:** Planificación de procesos del Kernel.

### ¿Qué hace?
Lanza dos subprocesos en paralelo que realizan **5 millones de operaciones matemáticas** (raíces cuadradas + senos). Uno con prioridad **BAJA** (`IDLE_PRIORITY_CLASS`) y otro con prioridad **ALTA** (`HIGH_PRIORITY_CLASS`). Mide cuál termina primero y calcula el ratio de velocidad.

Disponible en 4 modos:

| Comando | Descripción |
|---|---|
| `python 4_prioridad_procesos.py comparar` | Lanza ambos y compara (recomendado) |
| `python 4_prioridad_procesos.py baja` | Solo instancia con prioridad baja |
| `python 4_prioridad_procesos.py alta` | Solo instancia con prioridad alta |
| `python 4_prioridad_procesos.py realtime` | Prioridad máxima (requiere Admin) |

### Cómo ejecutarlo
```bash
python 4_prioridad_procesos.py comparar
```

### Resultado de prueba
```
  PID prioridad BAJA : 18432
  PID prioridad ALTA : 18436

  ✓ Proceso ALTA terminó  (t= 3.821s desde inicio)
  ✓ Proceso BAJA terminó  (t= 6.594s desde inicio)

============================================================
  RESULTADO FINAL
============================================================
  Prioridad BAJA  :   6.4821 s
  Prioridad ALTA  :   3.7903 s
  Diferencia      :   2.6918 s
  La instancia ALTA fue 1.71x más rápida
```

> **Conclusión:** El Kernel asigna más *time slices* de CPU al proceso con mayor prioridad. Con mayor carga en el sistema, la diferencia se amplifica. El SO usa algoritmos como Round-Robin con colas de prioridad para decidir qué proceso ocupa el CPU en cada quantum de tiempo.

---

## Resumen de conceptos cubiertos

| Script | Concepto SO | Resultado clave |
|---|---|---|
| 1 - Vigilante | Gestor de memoria y E/S | Monitoreo + log de alertas |
| 2 - Caché | Jerarquía de memoria | 34,000x speedup RAM vs Disco |
| 3 - Estrés | Memoria virtual / Paginación | Observación del Swap en acción |
| 4 - Prioridad | Scheduling del Kernel | 1.7x más rápido con alta prioridad |

---

## Instalación rápida

```bash
git clone https://github.com/DavidSalas0273/Sistemas-Operativos-taller.git
cd Sistemas-Operativos-taller
pip install psutil
```
