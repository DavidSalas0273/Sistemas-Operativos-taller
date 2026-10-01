"""
=============================================================
  TALLER 2 - Simulador de Memoria Caché (L1/L2 vs RAM)
  Concepto: Jerarquía de memoria y optimización
=============================================================
  Sin dependencias externas (solo stdlib de Python)
  Corre con: python 2_simulador_cache.py
=============================================================
"""

import time
import os
import hashlib
import random
import string

# ── La "caché" en RAM (simula L1/L2 cache del SO) ──────────
# Clave: ruta del archivo  →  Valor: contenido en RAM
_cache: dict[str, bytes] = {}

# ── Estadísticas ───────────────────────────────────────────
stats = {"hits": 0, "misses": 0}

# ══════════════════════════════════════════════════════════
#  FUNCIONES PRINCIPALES
# ══════════════════════════════════════════════════════════

def leer_archivo(ruta: str) -> bytes:
    """
    Lee un archivo aplicando la política de caché:
      - MISS: lo lee del disco y lo guarda en RAM.
      - HIT : lo devuelve directamente desde la RAM.
    Retorna el contenido en bytes.
    """
    if ruta in _cache:
        stats["hits"] += 1
        return _cache[ruta]         # ← desde RAM (rápido)
    else:
        stats["misses"] += 1
        with open(ruta, "rb") as f:
            datos = f.read()        # ← desde disco (lento)
        _cache[ruta] = datos        # guarda en caché
        return datos

def invalidar(ruta: str):
    """Elimina una entrada de la caché (política de invalidación)."""
    _cache.pop(ruta, None)

def limpiar_cache():
    """Vacía toda la caché."""
    _cache.clear()
    print("  [CACHÉ] Caché limpiada — siguiente lectura va al disco.")

def info_cache():
    """Muestra el tamaño actual de la caché en RAM."""
    total_bytes = sum(len(v) for v in _cache.values())
    print(f"\n  [CACHÉ] Entradas: {len(_cache)} archivos  |  "
          f"Tamaño en RAM: {total_bytes / (1024**2):.2f} MB")
    print(f"  [CACHÉ] Hits: {stats['hits']}  |  Misses: {stats['misses']}")


# ══════════════════════════════════════════════════════════
#  UTILIDADES DE PRUEBA
# ══════════════════════════════════════════════════════════

def generar_archivo_grande(ruta: str, mb: float = 20.0):
    """Crea un archivo de texto con contenido aleatorio del tamaño indicado."""
    objetivo_bytes = int(mb * 1024 * 1024)
    print(f"  Generando archivo de {mb} MB en '{ruta}'... ", end="", flush=True)
    with open(ruta, "wb") as f:
        escrito = 0
        bloque = 65536  # 64 KB por bloque
        while escrito < objetivo_bytes:
            chunk = (
                ''.join(random.choices(string.ascii_letters + string.digits + " \n", k=bloque))
                .encode("utf-8")
            )
            f.write(chunk)
            escrito += len(chunk)
    print("listo.")

def medir(etiqueta: str, funcion, *args) -> tuple:
    """
    Mide el tiempo de ejecución de una función y muestra el resultado.
    Retorna (resultado, tiempo_segundos).
    """
    inicio = time.perf_counter()
    resultado = funcion(*args)
    fin = time.perf_counter()
    elapsed = fin - inicio
    print(f"  ⏱  [{etiqueta}]  Tiempo: {elapsed * 1000:.3f} ms  "
          f"({elapsed:.6f} s)  — {len(resultado) / (1024**2):.2f} MB leídos")
    return resultado, elapsed


# ══════════════════════════════════════════════════════════
#  DEMO PRINCIPAL
# ══════════════════════════════════════════════════════════

def demo():
    ARCHIVO_PRUEBA = "archivo_grande.dat"
    TAMANIO_MB     = 20.0   # ajusta según tu RAM disponible
    REPETICIONES   = 5      # cuántas veces leer desde caché

    sep = "=" * 60

    print(sep)
    print("  SIMULADOR DE CACHÉ EN MEMORIA (L1/L2 vs RAM)")
    print(sep)

    # ── Paso 1: Crear el archivo si no existe ─────────────
    if not os.path.exists(ARCHIVO_PRUEBA):
        generar_archivo_grande(ARCHIVO_PRUEBA, TAMANIO_MB)
    else:
        size_mb = os.path.getsize(ARCHIVO_PRUEBA) / (1024**2)
        print(f"  Archivo existente: '{ARCHIVO_PRUEBA}' ({size_mb:.2f} MB)")

    print()

    # ── Paso 2: PRIMERA lectura (MISS → va al disco) ──────
    print("── LECTURA #1: CACHE MISS (lee del DISCO) ──────────────")
    limpiar_cache()
    _, t_disco = medir("DISCO  ", leer_archivo, ARCHIVO_PRUEBA)
    info_cache()

    print()

    # ── Paso 3: Lecturas siguientes (HIT → desde RAM) ─────
    print(f"── LECTURAS #2-{REPETICIONES+1}: CACHE HIT (lee de la RAM) ─────────")
    tiempos_cache = []
    for i in range(REPETICIONES):
        _, t = medir(f"CACHÉ {i+1}", leer_archivo, ARCHIVO_PRUEBA)
        tiempos_cache.append(t)
    info_cache()

    print()

    # ── Paso 4: Comparación ───────────────────────────────
    t_cache_prom = sum(tiempos_cache) / len(tiempos_cache)
    aceleracion  = t_disco / t_cache_prom if t_cache_prom > 0 else float("inf")

    print(sep)
    print("  RESULTADO COMPARATIVO")
    print(sep)
    print(f"  Disco  (1ª lectura):         {t_disco * 1000:>10.3f} ms")
    print(f"  Caché  (promedio {REPETICIONES} lecturas): {t_cache_prom * 1000:>10.3f} ms")
    print(f"  Aceleración (speedup):       {aceleracion:>10.1f}x más rápido")
    print()
    print("  CONCLUSIÓN:")
    print("  El SO usa esta misma técnica: mantiene páginas de archivos")
    print("  en la RAM (page cache) para evitar accesos lentos al disco.")
    print(sep)

    # ── Paso 5: Verificación de integridad ────────────────
    print("\n  Verificando integridad del contenido...")
    dato_disco = open(ARCHIVO_PRUEBA, "rb").read()
    dato_cache = leer_archivo(ARCHIVO_PRUEBA)
    hash_disco = hashlib.md5(dato_disco).hexdigest()
    hash_cache = hashlib.md5(dato_cache).hexdigest()
    if hash_disco == hash_cache:
        print("  ✓ Integridad OK — disco y caché devuelven el mismo contenido.")
    else:
        print("  ✗ ERROR — los contenidos difieren.")

    # ── Limpieza ──────────────────────────────────────────
    try:
        os.remove(ARCHIVO_PRUEBA)
        print(f"  Archivo temporal '{ARCHIVO_PRUEBA}' eliminado.")
    except OSError:
        pass


if __name__ == "__main__":
    demo()
