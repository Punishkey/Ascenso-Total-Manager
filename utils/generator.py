import random
from data.nombres_jugadores import NOMBRES, APELLIDOS, ESTRELLAS_CONFIG


def obtener_estructura_plantilla():
    """
    Define la composición equilibrada de la plantilla:
    1:POR, 2:DFC, 3:MCD, 4:MC, 5:EXT, 6:DC
    """
    plantilla = [1, 1, 2, 2, 2, 2, 2, 3, 3, 4, 4, 4, 5, 5, 5, 6, 6, 6]
    random.shuffle(plantilla)
    return plantilla

def generar_dorsales_disponibles():
    # Creamos una lista del 1 al 99
    dorsales = list(range(1, 100))
    # Excluimos los números que ya están asignados a las estrellas fijas
    # Esto evita conflictos con las estrellas que tienen número predefinido
    dorsales_ocupados = [datos["numero"] for datos in ESTRELLAS_CONFIG.values()]
    dorsales = [d for d in dorsales if d not in dorsales_ocupados]
    random.shuffle(dorsales)
    return dorsales

def generar_jugador_con_posicion(posicion_id, dorsal_disponible):
    nombre_completo = f"{random.choice(NOMBRES)} {random.choice(APELLIDOS)}"

    # Lógica de número de camiseta (Única y correcta)
    if nombre_completo in ESTRELLAS_CONFIG:
        numero = ESTRELLAS_CONFIG[nombre_completo]["numero"]
    else:
        numero = dorsal_disponible # Usamos el que viene del pop(0)

    edad = random.randint(17, 35)

    # Atributos ajustados (30-80) para media 50-60
    vel = random.randint(30, 80)
    res = random.randint(30, 80)
    anti = random.randint(30, 80)
    sere = random.randint(30, 80)
    trab = random.randint(30, 80)
    pase = random.randint(30, 80)
    ctrl = random.randint(30, 80)
    prof = random.randint(30, 80)
    pot = random.randint(30, 80)

    return {
        "nombre": nombre_completo,
        "numero": numero,
        "posicion_id": posicion_id,
        "edad": edad,
        "vel": vel,
        "res": res,
        "anti": anti,
        "sere": sere,
        "trab": trab,
        "pase": pase,
        "ctrl": ctrl,
        "prof": prof,
        "pot": pot
    }