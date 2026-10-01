"""
=============================================================
  TALLER 1 - Vigilante de Recursos (Monitoreo RAM y CPU)
  Concepto: Gestor de memoria y E/S
=============================================================
  Requiere: pip install psutil
  Corre con: python 1_vigilante_recursos.py
=============================================================
"""

import psutil
import time
import datetime
import os

# ── Configuración ──────────────────────────────────────────
INTERVALO_SEGUNDOS = 2       # Cada cuántos segundos muestrea
UMBRAL_RAM_ALERTA  = 80.0    # % de RAM que dispara alerta y log
UMBRAL_CPU_ALERTA  = 90.0    # % de CPU que dispara alerta visual
LOG_FILE           = "recursos_log.txt"

# ── Utilidades de consola ──────────────────────────────────
def limpiar():
    os.system("cls" if os.name == "nt" else "clear")

def barra(porcentaje: float, ancho: int = 30) -> str:
    """Dibuja una barra de progreso ASCII."""
    llenos = int((porcentaje / 100) * ancho)
    return "[" + "█" * llenos + "░" * (ancho - llenos) + f"] {porcentaje:5.1f}%"

def color(texto: str, porcentaje: float) -> str:
    """Añade color ANSI según el nivel (verde/amarillo/rojo)."""
    if porcentaje < 60:
        return f"\033[92m{texto}\033[0m"   # verde
    elif porcentaje < 80:
        return f"\033[93m{texto}\033[0m"   # amarillo
    else:
        return f"\033[91m{texto}\033[0m"   # rojo

# ── Log en archivo ─────────────────────────────────────────
def escribir_log(ram_pct: float, cpu_pct: float):
    """Guarda una línea en el archivo de log cada vez que RAM > umbral."""
    ahora = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    linea = (
        f"[{ahora}] ⚠ ALERTA RAM  "
        f"RAM: {ram_pct:.1f}%  |  CPU: {cpu_pct:.1f}%\n"
    )
    with open(LOG_FILE, "a", encoding="utf-8") as f:
        f.write(linea)
    return linea.strip()

# ── Panel principal ────────────────────────────────────────
def panel():
    print("\033[H\033[J", end="")   # limpia pantalla sin llamar cls (más suave)
    print("=" * 55)
    print("   🖥  VIGILANTE DE RECURSOS — Panel de Control SO")
    print("=" * 55)

    # ── CPU ──────────────────────────────────────────────
    cpu_pct = psutil.cpu_percent(interval=None)
    # Núcleos individuales
    nucleos = psutil.cpu_percent(percpu=True)
    print(f"\n  CPU total: {color(barra(cpu_pct), cpu_pct)}")
    for i, pct in enumerate(nucleos):
        print(f"    Núcleo {i}: {color(barra(pct, 20), pct)}")

    if cpu_pct >= UMBRAL_CPU_ALERTA:
        print(f"\n  ⚠  CPU EN {cpu_pct:.1f}% — sobrecarga detectada")

    # ── RAM ──────────────────────────────────────────────
    mem = psutil.virtual_memory()
    ram_pct   = mem.percent
    ram_total = mem.total   / (1024 ** 3)
    ram_usada = mem.used    / (1024 ** 3)
    ram_libre = mem.available / (1024 ** 3)

    print(f"\n  RAM total : {color(barra(ram_pct), ram_pct)}")
    print(f"    Total   : {ram_total:.2f} GB")
    print(f"    Usada   : {ram_usada:.2f} GB")
    print(f"    Libre   : {ram_libre:.2f} GB")

    # ── Swap / Memoria virtual ────────────────────────────
    swap = psutil.swap_memory()
    swap_pct = swap.percent
    print(f"\n  SWAP/Virtual: {color(barra(swap_pct), swap_pct)}")
    print(f"    Total   : {swap.total / (1024**3):.2f} GB")
    print(f"    Usada   : {swap.used  / (1024**3):.2f} GB")

    # ── Disco I/O ─────────────────────────────────────────
    disco_io = psutil.disk_io_counters()
    print(f"\n  Disco  — Lecturas: {disco_io.read_bytes  / (1024**2):.1f} MB  "
          f"Escrituras: {disco_io.write_bytes / (1024**2):.1f} MB")

    # ── Red ───────────────────────────────────────────────
    net_io = psutil.net_io_counters()
    print(f"  Red    — Enviado: {net_io.bytes_sent / (1024**2):.1f} MB  "
          f"Recibido: {net_io.bytes_recv / (1024**2):.1f} MB")

    # ── Alerta y log ──────────────────────────────────────
    alerta = ""
    if ram_pct >= UMBRAL_RAM_ALERTA:
        alerta = escribir_log(ram_pct, cpu_pct)
        print(f"\n  \033[91m{'█'*55}")
        print(f"  ⚠  ALERTA: RAM al {ram_pct:.1f}% — registrado en {LOG_FILE}")
        print(f"  {'█'*55}\033[0m")

    print(f"\n  Última actualización: {datetime.datetime.now().strftime('%H:%M:%S')}")
    print(f"  Intervalo: {INTERVALO_SEGUNDOS}s | Umbral alerta RAM: {UMBRAL_RAM_ALERTA}%")
    print("=" * 55)
    print("  Presiona Ctrl+C para salir")

    return ram_pct, cpu_pct

# ── Entrada ────────────────────────────────────────────────
if __name__ == "__main__":
    try:
        import psutil  # noqa: verificación temprana
    except ImportError:
        print("Falta psutil. Ejecuta:  pip install psutil")
        raise SystemExit(1)

    print("Iniciando Vigilante de Recursos...")
    # Primera muestra de CPU necesita una llamada previa (calibra el intervalo)
    psutil.cpu_percent(interval=1)

    try:
        while True:
            ram_pct, cpu_pct = panel()
            time.sleep(INTERVALO_SEGUNDOS)
    except KeyboardInterrupt:
        print("\n\n  Monitor detenido. Log guardado en:", LOG_FILE)
