"""
=============================================================
  TALLER 3 - Estrés de Memoria y Salto a la Virtual (Paginación)
  Concepto: Memoria Virtual y Archivo de Paginación (Swap)
=============================================================
  Requiere: pip install psutil
  Corre con: python 3_estres_memoria.py

  ⚠  ADVERTENCIA:
     Este script CONSUME MEMORIA DE FORMA PROGRESIVA.
     Tiene límite de seguridad configurable (LIMITE_MB).
     Abre el Administrador de Tareas (Ctrl+Shift+Esc) antes
     de correrlo y observa cómo sube la memoria virtual/swap.
=============================================================
"""

import psutil
import time
import sys
import os

# ── Límite de seguridad ─────────────────────────────────────
# El script se detiene cuando alcanza este uso TOTAL del proceso
LIMITE_MB        = 1500      # MB máximos que puede consumir este proceso
INTERVALO_MS     = 200       # ms entre cada iteración del bucle
CHUNK_SIZE       = 50_000    # strings añadidos por iteración
STRING_TAMANO    = 200       # caracteres por string (~200 bytes cada uno)

# ── Helpers ─────────────────────────────────────────────────
def mb(bytes_val: int) -> float:
    return bytes_val / (1024 ** 2)

def gb(bytes_val: int) -> float:
    return bytes_val / (1024 ** 3)

def barra(pct: float, ancho: int = 25) -> str:
    llenos = int((pct / 100) * ancho)
    return "[" + "█" * llenos + "░" * (ancho - llenos) + f"] {pct:5.1f}%"

def color(texto: str, pct: float) -> str:
    if pct < 60:   return f"\033[92m{texto}\033[0m"
    elif pct < 80: return f"\033[93m{texto}\033[0m"
    else:           return f"\033[91m{texto}\033[0m"

# ── Estado del proceso ──────────────────────────────────────
proc = psutil.Process(os.getpid())

def mem_proceso_mb() -> float:
    """Memoria RSS (física) usada por ESTE proceso en MB."""
    return mb(proc.memory_info().rss)

# ── Bucle principal ─────────────────────────────────────────
def estres():
    contenedor = []          # ← aquí se acumula la memoria
    iteracion  = 0
    inicio     = time.time()

    print("=" * 60)
    print("  ESTRÉS DE MEMORIA — Simulación de Paginación Virtual")
    print("=" * 60)
    print(f"  Límite de seguridad : {LIMITE_MB} MB")
    print(f"  Chunk por iteración : {CHUNK_SIZE} strings × {STRING_TAMANO} chars")
    print(f"  Interval            : {INTERVALO_MS} ms")
    print()
    print("  Abre el Administrador de Tareas ahora (Ctrl+Shift+Esc)")
    print("  y observa 'Memoria' y 'Memoria confirmada' del proceso.")
    print()
    print("  Iniciando en 3 segundos... (Ctrl+C para abortar)")
    time.sleep(3)

    try:
        while True:
            # ── Añade un bloque de strings a la lista ─────────
            bloque = ["X" * STRING_TAMANO] * CHUNK_SIZE
            contenedor.extend(bloque)
            iteracion += 1

            # ── Snapshot del sistema ──────────────────────────
            mem_sys  = psutil.virtual_memory()
            swap_sys = psutil.swap_memory()
            mem_proc = mem_proceso_mb()
            elapsed  = time.time() - inicio
            total_items = len(contenedor)

            ram_pct  = mem_sys.percent
            swap_pct = swap_sys.percent

            # ── Panel ─────────────────────────────────────────
            print(f"\033[H\033[J", end="")      # limpia pantalla
            print("=" * 60)
            print("  ESTRÉS DE MEMORIA — Simulación de Paginación Virtual")
            print("=" * 60)
            print(f"\n  Iteración : {iteracion:,}   |   Tiempo: {elapsed:.1f}s")
            print(f"  Items en lista : {total_items:,}  "
                  f"≈ {total_items * STRING_TAMANO / (1024**2):.1f} MB lógicos")

            print(f"\n  RAM del proceso (RSS)  : {mem_proc:>8.1f} MB")
            print(f"  Límite de seguridad    : {LIMITE_MB:>8} MB")
            uso_pct_limite = (mem_proc / LIMITE_MB) * 100
            print(f"  {color(barra(uso_pct_limite), uso_pct_limite)}")

            print(f"\n  RAM sistema  : {color(barra(ram_pct), ram_pct)}")
            print(f"    Usada  : {mb(mem_sys.used):>8.0f} MB / "
                  f"{gb(mem_sys.total):.1f} GB")
            print(f"    Libre  : {mb(mem_sys.available):>8.0f} MB")

            print(f"\n  SWAP/Virtual : {color(barra(swap_pct), swap_pct)}")
            print(f"    Usada  : {mb(swap_sys.used):>8.0f} MB / "
                  f"{gb(swap_sys.total):.1f} GB")

            # ── Mensaje dinámico según fase ───────────────────
            if swap_pct < 5:
                fase = "🟢  Fase 1: Todo en RAM física (rápido)"
            elif swap_pct < 30:
                fase = "🟡  Fase 2: Paginación iniciada — RAM física casi llena"
            else:
                fase = "🔴  Fase 3: Alta paginación — usando memoria virtual (LENTO)"

            print(f"\n  {fase}")
            print("=" * 60)
            print("  Ctrl+C para detener de forma segura")

            # ── Límite de seguridad ────────────────────────────
            if mem_proc >= LIMITE_MB:
                print(f"\n  ⛔  LÍMITE ALCANZADO ({LIMITE_MB} MB) — deteniendo.")
                break

            time.sleep(INTERVALO_MS / 1000)

    except KeyboardInterrupt:
        print(f"\n\n  Script interrumpido por el usuario.")

    finally:
        # Libera todo para que el SO recupere la memoria
        print(f"  Liberando {mem_proceso_mb():.0f} MB de RAM...")
        contenedor.clear()
        del contenedor
        print("  Memoria liberada. El SO recuperará las páginas.")
        print()
        mem_final = psutil.virtual_memory()
        print(f"  RAM sistema ahora: {mb(mem_final.used):.0f} MB usados  "
              f"({mem_final.percent:.1f}%)")

if __name__ == "__main__":
    try:
        import psutil  # noqa
    except ImportError:
        print("Falta psutil. Ejecuta:  pip install psutil")
        raise SystemExit(1)

    estres()
