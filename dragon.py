import math
from typing import List, Tuple

import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation


Punto = Tuple[float, float]


# ==========================
# CONFIGURACIÓN
# ==========================

ORDEN_MAXIMO = 16
LARGO_INICIAL = 16

# Cantidad de pasos intermedios entre una iteración y la siguiente.
# Más grande = movimiento más suave, pero también más pesado.
FRAMES_TRANSICION = 25

# Pausa cuando termina cada iteración.
PAUSA_ENTRE_ITERACIONES = 12

# Velocidad de la animación.
# Más chico = más rápido.
INTERVALO_MS = 25


# ==========================
# FUNCIONES BÁSICAS
# ==========================

def punto_medio(p1: Punto, p2: Punto) -> Punto:
    return (
        (p1[0] + p2[0]) / 2,
        (p1[1] + p2[1]) / 2
    )


def interpolar(p1: Punto, p2: Punto, progreso: float) -> Punto:
    return (
        p1[0] + (p2[0] - p1[0]) * progreso,
        p1[1] + (p2[1] - p1[1]) * progreso
    )


def punto_doblado(p1: Punto, p2: Punto, signo: int) -> Punto:
    medio = punto_medio(p1, p2)

    dx = p2[0] - p1[0]
    dy = p2[1] - p1[1]

    perpendicular = (
        -dy / 2,
        dx / 2
    )

    return (
        medio[0] + signo * perpendicular[0],
        medio[1] + signo * perpendicular[1]
    )


# ==========================
# GENERACIÓN DEL DRAGÓN
# ==========================

def transformar_segmento(p1: Punto, p2: Punto, indice: int, progreso: float) -> List[Punto]:
    """
    Transforma un segmento en dos segmentos.

    progreso = 0:
        el segmento todavía está recto.

    progreso = 1:
        el segmento ya se dobló.
    """
    medio = punto_medio(p1, p2)

    if indice % 2 == 0:
        signo = 1
    else:
        signo = -1

    doblado = punto_doblado(p1, p2, signo)

    punto_animado = interpolar(medio, doblado, progreso)

    return [p1, punto_animado, p2]


def transformar_dragon(puntos: List[Punto], progreso: float) -> List[Punto]:
    nuevos_puntos = []

    for i in range(len(puntos) - 1):
        p1 = puntos[i]
        p2 = puntos[i + 1]

        segmento = transformar_segmento(p1, p2, i, progreso)

        if i == 0:
            nuevos_puntos.extend(segmento)
        else:
            nuevos_puntos.extend(segmento[1:])

    return nuevos_puntos


def generar_dragon(orden: int) -> List[Punto]:
    puntos = [
        (-LARGO_INICIAL / 2, 0),
        (LARGO_INICIAL / 2, 0)
    ]

    for _ in range(orden):
        puntos = transformar_dragon(puntos, 1)

    return puntos


# ==========================
# PREPARAR FRAMES
# ==========================

def preparar_frames():
    frames = []

    for orden in range(ORDEN_MAXIMO + 1):
        for _ in range(PAUSA_ENTRE_ITERACIONES):
            frames.append((orden, None))

        if orden < ORDEN_MAXIMO:
            for paso in range(FRAMES_TRANSICION + 1):
                progreso = paso / FRAMES_TRANSICION
                frames.append((orden, progreso))

    return frames


# ==========================
# ANIMACIÓN
# ==========================

def animar():
    fig, ax = plt.subplots(figsize=(7, 7))

    linea, = ax.plot([], [], linewidth=1.2)

    ax.set_aspect("equal")
    ax.axis("off")
    ax.set_title("Fractal del dragón de Heighway", fontsize=14)

    # Generamos todos los dragones una sola vez para que sea más liviano.
    dragones_por_orden = {}

    for orden in range(ORDEN_MAXIMO + 1):
        dragones_por_orden[orden] = generar_dragon(orden)

    # Colores distintos para cada iteración.
    colores = plt.cm.turbo(
        [i / ORDEN_MAXIMO for i in range(ORDEN_MAXIMO + 1)]
    )

    # Calculamos límites automáticos usando la última iteración.
    dragon_final = dragones_por_orden[ORDEN_MAXIMO]

    xs_final = [p[0] for p in dragon_final]
    ys_final = [p[1] for p in dragon_final]

    margen = 0.8

    ax.set_xlim(min(xs_final) - margen, max(xs_final) + margen)
    ax.set_ylim(min(ys_final) - margen, max(ys_final) + margen)

    texto = ax.text(
        0.03,
        0.95,
        "",
        transform=ax.transAxes,
        fontsize=12
    )

    frames = preparar_frames()

    def actualizar(frame):
        orden, progreso = frame

        puntos_base = dragones_por_orden[orden]

        if progreso is None:
            puntos = puntos_base
            iteracion_mostrada = orden
            texto.set_text(f"Iteración: {orden}")
        else:
            puntos = transformar_dragon(puntos_base, progreso)
            iteracion_mostrada = orden + 1
            texto.set_text(f"Iteración: {orden} → {orden + 1}")

        xs = [p[0] for p in puntos]
        ys = [p[1] for p in puntos]

        linea.set_data(xs, ys)

        # Cambia el color según la iteración.
        linea.set_color(colores[iteracion_mostrada])

        return linea, texto

    animacion = FuncAnimation(
        fig,
        actualizar,
        frames=frames,
        interval=INTERVALO_MS,
        repeat=True,
        blit=True
    )

    plt.show()


if __name__ == "__main__":
    animar()