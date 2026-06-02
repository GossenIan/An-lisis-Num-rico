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
# CONFIGURACIÓN DEL DRAGÓN DORADO
# ==========================

PHI = (1 + math.sqrt(5)) / 2

# Escalas del dragón dorado.
# El primer segmento es más largo y el segundo más corto.
R1 = (1 / PHI) ** (1 / PHI)
R2 = R1 ** 2

# Ángulos del dragón dorado.
# No son 90° como en el dragón de Heighway normal.
ANGULO_1 = math.acos((1 + R1**2 - R2**2) / (2 * R1))
ANGULO_2 = math.acos((1 + R2**2 - R1**2) / (2 * R2))


# ==========================
# FUNCIONES BÁSICAS
# ==========================

def interpolar(p1: Punto, p2: Punto, progreso: float) -> Punto:
    return (
        p1[0] + (p2[0] - p1[0]) * progreso,
        p1[1] + (p2[1] - p1[1]) * progreso
    )


def punto_sobre_segmento(p1: Punto, p2: Punto, proporcion: float) -> Punto:
    """
    Devuelve un punto ubicado sobre el segmento p1-p2.

    proporcion = 0   -> p1
    proporcion = 1   -> p2
    proporcion = 0.5 -> punto medio

    En el dragón dorado NO usamos siempre 0.5.
    Usamos R1 o R2 según el tipo de giro.
    """
    return (
        p1[0] + (p2[0] - p1[0]) * proporcion,
        p1[1] + (p2[1] - p1[1]) * proporcion
    )


def punto_doblado_dorado(p1: Punto, p2: Punto, signo: int) -> Punto:
    """
    Calcula el punto de quiebre del dragón dorado.

    En el dragón normal:
        - se usa el punto medio
        - se dobla con un ángulo de 90°

    En el dragón dorado:
        - los segmentos no tienen la misma longitud
        - los ángulos dependen de la razón áurea
    """
    dx = p2[0] - p1[0]
    dy = p2[1] - p1[1]

    distancia = math.hypot(dx, dy)
    angulo_base = math.atan2(dy, dx)

    if signo == 1:
        # Primer tipo de doblez:
        # segmento largo primero, giro hacia un lado.
        distancia_nueva = distancia * R1
        angulo_nuevo = angulo_base + ANGULO_1
    else:
        # Segundo tipo de doblez:
        # segmento corto primero, giro hacia el otro lado.
        distancia_nueva = distancia * R2
        angulo_nuevo = angulo_base - ANGULO_2

    return (
        p1[0] + distancia_nueva * math.cos(angulo_nuevo),
        p1[1] + distancia_nueva * math.sin(angulo_nuevo)
    )


# ==========================
# GENERACIÓN DEL DRAGÓN DORADO
# ==========================

def transformar_segmento(p1: Punto, p2: Punto, indice: int, progreso: float) -> List[Punto]:
    """
    Transforma un segmento en dos segmentos.

    progreso = 0:
        el segmento todavía está recto.

    progreso = 1:
        el segmento ya se dobló formando el dragón dorado.
    """
    if indice % 2 == 0:
        signo = 1
        proporcion_recta = R1
    else:
        signo = -1
        proporcion_recta = R2

    punto_recto = punto_sobre_segmento(p1, p2, proporcion_recta)
    punto_doblado = punto_doblado_dorado(p1, p2, signo)

    punto_animado = interpolar(punto_recto, punto_doblado, progreso)

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

    # Fondo oscuro para que el dorado destaque.
    fig.patch.set_facecolor("#071b2a")
    ax.set_facecolor("#071b2a")

    linea, = ax.plot([], [], linewidth=1.2)

    ax.set_aspect("equal")
    ax.axis("off")
    ax.set_title(
        "Fractal del dragón dorado",
        fontsize=14,
        color="#ffd700",
        pad=15
    )

    # Generamos todos los dragones una sola vez para que sea más liviano.
    dragones_por_orden = {}

    for orden in range(ORDEN_MAXIMO + 1):
        dragones_por_orden[orden] = generar_dragon(orden)

    # Paleta dorada: arranca naranja y termina oro brillante.
    colores = [
        "#8c4b00",
        "#a85f00",
        "#c77800",
        "#d99000",
        "#e6a800",
        "#f2c230",
        "#ffd700",
        "#ffe066",
        "#ffec99",
        "#fff2b2",
        "#ffd700",
        "#f6c343",
        "#e8a317",
        "#d89000",
        "#c47a00",
        "#ffcc33",
        "#ffd700",
    ]

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
        fontsize=12,
        color="#ffd700"
    )

    datos = ax.text(
        0.03,
        0.90,
        f"φ = {PHI:.5f} | r1 = {R1:.3f} | r2 = {R2:.3f}",
        transform=ax.transAxes,
        fontsize=9,
        color="#ffec99"
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
        linea.set_color(colores[iteracion_mostrada % len(colores)])

        return linea, texto, datos

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