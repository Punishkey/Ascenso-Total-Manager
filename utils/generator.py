import random
from data.nombres_jugadores import NOMBRES, APELLIDOS, ESTRELLAS_CONFIG


def obtener_estructura_plantilla():
    # 1:POR, 2:DFC, 3:MCD, 4:MC, 5:EXT, 6:DC
    plantilla = [1, 1, 2, 2, 2, 2, 2, 3, 3, 4, 4, 4, 5, 5, 5, 6, 6, 6]
    random.shuffle(plantilla)
    return plantilla


def generar_dorsales_disponibles():
    dorsales = list(range(1, 100))
    dorsales_ocupados = [datos["numero"] for datos in ESTRELLAS_CONFIG.values()]
    dorsales = [d for d in dorsales if d not in dorsales_ocupados]
    random.shuffle(dorsales)
    return dorsales


def generar_jugador_con_posicion(posicion_id, dorsal_disponible):
    nombre_completo = f"{random.choice(NOMBRES)} {random.choice(APELLIDOS)}"
    numero = ESTRELLAS_CONFIG[nombre_completo]["numero"] if nombre_completo in ESTRELLAS_CONFIG else dorsal_disponible
    edad = random.randint(17, 35)

    # Atributos (30-80)
    attrs = {k: random.randint(30, 80) for k in ["vel", "res", "anti", "sere", "trab", "pase", "ctrl", "prof", "pot"]}

    return {
        "nombre": nombre_completo,
        "numero": numero,
        "posicion_id": posicion_id,
        "edad": edad,
        **attrs
    }