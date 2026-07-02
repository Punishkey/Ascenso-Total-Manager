import random
from data.nombres_jugadores import NOMBRES, APELLIDOS


def obtener_estructura_plantilla():
    """
    Define la composición equilibrada de la plantilla:
    1:POR, 2:DFC, 3:MCD, 4:MC, 5:EXT, 6:DC
    """
    plantilla = [1, 1, 2, 2, 2, 2, 2, 3, 3, 4, 4, 4, 5, 5, 5, 6, 6, 6]
    random.shuffle(plantilla)
    return plantilla


def generar_jugador_con_posicion(posicion_id):
    """
    Genera un diccionario con atributos aleatorios para una posición fija.
    """
    nombre_completo = f"{random.choice(NOMBRES)} {random.choice(APELLIDOS)}"
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

    return {
        "nombre": nombre_completo,
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