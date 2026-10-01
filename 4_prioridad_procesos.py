"""
=============================================================
  TALLER 4 - Prioridad de Procesos (Scheduling)
  Concepto: Planificación de procesos del Kernel
=============================================================
  Requiere: pip install psutil
  Corre con:
    python 4_prioridad_procesos.py baja         ← prioridad baja
    python 4_prioridad_procesos.py alta         ← prioridad alta/tiempo-real
    python 4_prioridad_procesos.py comparar     ← lanza ambas y mide
=============================================================
  En Windows las prioridades disponibles son (psutil):
    IDLE_PRIORITY_CLASS          → "idle"    (la más baja)
    BELOW_NORMAL_PRIORITY_CLASS  → "below_normal"
    NORMAL_PRIORITY_CLASS        → "normal"  (por defecto)
    ABOVE_NORMAL_PRIORITY_CLASS  → "above_normal"
    HIGH_PRIORITY_CLASS          → "high"
    REALTIME_PRIORITY_CLASS      → "realtime" (la más alta — úsala con cuidado)
=============================================================
"""

import psutil
import os
import sys
import time
import subprocess
import math

# ── Configuración del trabajo pesado ───────────────────────
# Cambia N_OPERACIONES para más o menos trabajo
N_OPERACIONES = 5_000_000   # sumas/raíces cuadradas

# Mapa legible de prioridades (Windows)
PRIORIDADES = {
    "baja"   : psutil.IDLE_PRIORITY_CLASS,
    "normal" : psutil.NORMAL_PRIORITY_CLASS,
    "alta"   : psutil.HIGH_PRIORITY_CLASS,
    "realtime": psutil.REALTIME_PRIORITY_CLASS,
}


# ══════════════════════════════════════════════════════════
#  CÁLCULO PESADO (trabajo que hace el proceso)
# ══════════════════════════════════════════════════════════

def calculo_pesado() -> float:
    """
    Realiza N_OPERACIONES sumas de raíces cuadradas.
    Es puro uso de CPU — ideal para ver el efecto del scheduler.
    """
    acumulador = 0.0
    for i in range(1, N_OPERACIONES + 1):
        acumulador += math.sqrt(i) * math.sin(i) / (i + 1)
    return acumulador


# ══════════════════════════════════════════════════════════
#  MODO WORKER — este proceso aplica su prioridad y trabaja
# ══════════════════════════════════════════════════════════

def modo_worker(nivel: str):
    proc = psutil.Process(os.getpid())

    if nivel not in PRIORIDADES:
        print(f"  Nivel desconocido '{nivel}'. Usa: {list(PRIORIDADES.keys())}")
        sys.exit(1)

    # ── Aplica la prioridad ───────────────────────────────
    try:
        proc.nice(PRIORIDADES[nivel])
        prioridad_real = proc.nice()
    except psutil.AccessDenied:
        print(f"  ⚠  Sin permisos para aplicar prioridad '{nivel}'.")
        print("     En Windows, 'realtime' requiere ejecutar como Administrador.")
        print("     Continuando con prioridad normal...\n")
        prioridad_real = proc.nice()

    pid = os.getpid()
    print("=" * 50)
    print(f"  PID            : {pid}")
    print(f"  Nivel pedido   : {nivel}")
    print(f"  Prioridad real : {prioridad_real}")
    print(f"  Operaciones    : {N_OPERACIONES:,}")
    print("=" * 50)
    print("  Iniciando cálculo pesado...")

    inicio = time.perf_counter()
    resultado = calculo_pesado()
    fin = time.perf_counter()

    elapsed = fin - inicio
    print(f"  ✓ Cálculo completado en {elapsed:.4f} segundos")
    print(f"  Resultado (checksum): {resultado:.6f}")
    print("=" * 50)

    # Imprime en formato machine-readable para el modo comparar
    # (última línea del stdout)
    print(f"__RESULTADO__{nivel}__{elapsed:.6f}")


# ══════════════════════════════════════════════════════════
#  MODO COMPARAR — lanza dos subprocesos y compara tiempos
# ══════════════════════════════════════════════════════════

def modo_comparar():
    print("=" * 60)
    print("  COMPARATIVA DE PRIORIDADES DE PROCESO")
    print("=" * 60)
    print(f"  Se lanzarán DOS instancias del script en paralelo:")
    print(f"    • Instancia A : prioridad BAJA   (idle)")
    print(f"    • Instancia B : prioridad ALTA   (high)")
    print(f"  Operaciones por instancia: {N_OPERACIONES:,}")
    print()
    print("  NOTA: En Windows, para 'realtime' ejecuta como Administrador.")
    print("  Si no tienes permisos, el script usará prioridad normal.")
    print()
    print("  Lanzando... (Ctrl+C para cancelar)")
    print("=" * 60)

    script = os.path.abspath(__file__)
    python = sys.executable

    t_global_inicio = time.perf_counter()

    # ── Lanza ambos procesos a la vez ─────────────────────
    proc_baja = subprocess.Popen(
        [python, script, "baja"],
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True
    )
    proc_alta = subprocess.Popen(
        [python, script, "alta"],
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True
    )

    print(f"  PID prioridad BAJA : {proc_baja.pid}")
    print(f"  PID prioridad ALTA : {proc_alta.pid}")
    print()

    # ── Espera a que terminen ambos ───────────────────────
    stdout_baja, stderr_baja = proc_baja.communicate()
    t_baja_fin = time.perf_counter()
    print(f"  ✓ Proceso BAJA terminó  (t={t_baja_fin - t_global_inicio:.3f}s desde inicio)")

    stdout_alta, stderr_alta = proc_alta.communicate()
    t_alta_fin = time.perf_counter()
    print(f"  ✓ Proceso ALTA terminó  (t={t_alta_fin - t_global_inicio:.3f}s desde inicio)")

    # ── Extrae tiempos de los subprocesos ─────────────────
    def extraer_tiempo(stdout: str, nivel: str) -> float:
        for linea in stdout.splitlines():
            if linea.startswith(f"__RESULTADO__{nivel}__"):
                return float(linea.split("__")[-1])
        return -1.0

    t_baja = extraer_tiempo(stdout_baja, "baja")
    t_alta = extraer_tiempo(stdout_alta, "alta")

    # ── Resultado ─────────────────────────────────────────
    print()
    print("=" * 60)
    print("  RESULTADO FINAL")
    print("=" * 60)

    if t_baja > 0 and t_alta > 0:
        diferencia = t_baja - t_alta
        if diferencia > 0:
            ganador = "ALTA"
            ratio = t_baja / t_alta
            print(f"  Prioridad BAJA  : {t_baja:.4f} s")
            print(f"  Prioridad ALTA  : {t_alta:.4f} s")
            print(f"  Diferencia      : {diferencia:.4f} s")
            print(f"  La instancia ALTA fue {ratio:.2f}x más rápida")
        else:
            ganador = "BAJA"
            ratio = t_alta / t_baja
            print(f"  Prioridad BAJA  : {t_baja:.4f} s")
            print(f"  Prioridad ALTA  : {t_alta:.4f} s")
            print(f"  Diferencia      : {abs(diferencia):.4f} s")
            print(f"  Resultado inesperado: BAJA fue {ratio:.2f}x más rápida")
            print(f"  (Posible causa: sin permisos, ambas corrieron en normal)")
    else:
        print("  No se pudo extraer los tiempos. Salida bruta:")
        print("  BAJA:", stdout_baja[-300:] if stdout_baja else stderr_baja[-300:])
        print("  ALTA:", stdout_alta[-300:] if stdout_alta else stderr_alta[-300:])

    print()
    print("  CONCLUSIÓN:")
    print("  El Kernel asigna más tiempo de CPU a procesos con mayor")
    print("  prioridad. Con carga en el sistema, la diferencia crece.")
    print("  El SO usa algoritmos como Round-Robin con prioridades para")
    print("  decidir qué proceso ocupa el CPU en cada quantum de tiempo.")
    print("=" * 60)


# ══════════════════════════════════════════════════════════
#  ENTRADA
# ══════════════════════════════════════════════════════════

if __name__ == "__main__":
    try:
        import psutil  # noqa
    except ImportError:
        print("Falta psutil. Ejecuta:  pip install psutil")
        sys.exit(1)

    modo = sys.argv[1].lower() if len(sys.argv) > 1 else "comparar"

    if modo == "comparar":
        modo_comparar()
    elif modo in PRIORIDADES:
        modo_worker(modo)
    else:
        print(f"Uso:")
        print(f"  python {os.path.basename(__file__)} baja")
        print(f"  python {os.path.basename(__file__)} alta")
        print(f"  python {os.path.basename(__file__)} normal")
        print(f"  python {os.path.basename(__file__)} realtime   (requiere Admin)")
        print(f"  python {os.path.basename(__file__)} comparar   (lanza ambos)")
        sys.exit(1)
