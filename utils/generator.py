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
    """
    Genera un diccionario con atributos aleatorios para una posición fija.
    """
    nombre_completo = f"{random.choice(NOMBRES)} {random.choice(APELLIDOS)}"

    # Si es estrella, usamos su número fijo, si no, tomamos el que nos da la lista
    if nombre_completo in ESTRELLAS_CONFIG:
        numero = ESTRELLAS_CONFIG[nombre_completo]["numero"]
    else:
        numero = dorsal_disponible


    edad = random.randint(18, 35)

    # Atributos
    vel = random.randint(50, 90)
    res = random.randint(50, 90)
    anti = random.randint(50, 90)
    sere = random.randint(50, 90)
    trab = random.randint(50, 90)
    pase = random.randint(50, 90)
    ctrl = random.randint(50, 90)
    prof = random.randint(50, 90)
    pot = random.randint(50, 90)

    # Lógica de número de camiseta:
    # Si el nombre generado está en ESTRELLAS_CONFIG, usamos su número.
    # Si no, asignamos un número aleatorio entre 1 y 99.
    if nombre_completo in ESTRELLAS_CONFIG:
        numero = ESTRELLAS_CONFIG[nombre_completo]["numero"]
    else:
        numero = random.randint(1, 99)

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