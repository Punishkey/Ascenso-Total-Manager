from db.database import get_connection
from utils.generator import (obtener_estructura_plantilla,
                             generar_jugador_con_posicion,
                             generar_dorsales_disponibles)
from db.jugador_queries import insertar_jugador_en_cursor
from config import (PRESUPUESTO_INICIAL, NIVEL_INICIAL, CAPACIDAD_INICIAL,
                    COSTE_MEJORA_ESTADIO)


def crear_club(user_id, nombre_club):

    conn = get_connection()
    cursor = conn.cursor()

    try:
        # Crear el club
        cursor.execute('INSERT INTO clubes (user_id, nombre, presupuesto) VALUES (?, ?, ?)',
                       (user_id, nombre_club, PRESUPUESTO_INICIAL))
        club_id = cursor.lastrowid

        # Crear el estadio inicial
        cursor.execute('INSERT INTO estadios (club_id, nombre, nivel, capacidad) VALUES (?, ?, ?, ?)',
                       (club_id, f"Estadio de {nombre_club}", NIVEL_INICIAL, CAPACIDAD_INICIAL))

        # Generar 18 jugadores
        estructura = obtener_estructura_plantilla()
        dorsales = generar_dorsales_disponibles()
        for pos_id in estructura:
            data = generar_jugador_con_posicion(pos_id, dorsales.pop(0))
            insertar_jugador_en_cursor(cursor, club_id, data)

        conn.commit()
    except Exception as e:
        conn.rollback()
        raise e
    finally:
        conn.close()

    return club_id


def ya_tiene_club(user_id):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute('SELECT id FROM clubes WHERE user_id = ?', (user_id,))
    resultado = cursor.fetchone()
    conn.close()
    return resultado is not None


def obtener_club_id_por_usuario(user_id):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute('SELECT id FROM clubes WHERE user_id = ?', (user_id,))
    resultado = cursor.fetchone()
    conn.close()
    return resultado[0] if resultado else None

def obtener_info_estadio(club_id):
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute('''
        SELECT nombre, nivel, capacidad, ingresos_base 
        FROM estadios 
        WHERE club_id = ?
    ''', (club_id,))
    resultado = cursor.fetchone()
    conn.close()
    return resultado


def mejorar_estadio_db(club_id):
    conn = get_connection()
    cursor = conn.cursor()

    # 1. Verificar presupuesto y nivel actual
    cursor.execute('SELECT presupuesto FROM clubes WHERE id = ?', (club_id,))
    presupuesto = cursor.fetchone()[0]

    cursor.execute('SELECT nivel FROM estadios WHERE club_id = ?', (club_id,))
    nivel = cursor.fetchone()[0]

    coste = nivel * COSTE_MEJORA_ESTADIO

    if presupuesto >= coste:
        # 2. Actualizar nivel, capacidad y restar dinero
        cursor.execute('UPDATE clubes SET presupuesto = presupuesto - ? WHERE id = ?', (coste, club_id))
        cursor.execute('''
                       UPDATE estadios
                       SET nivel     = nivel + 1,
                           capacidad = capacidad + 2500
                       WHERE club_id = ?
                       ''', (club_id,))
        conn.commit()
        exito = True
    else:
        exito = False

    conn.close()
    return exito, coste

def obtener_info_club_y_estadio_por_club_id(club_id):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute('''
        SELECT c.nombre, c.presupuesto, e.nombre, e.nivel, e.capacidad 
        FROM clubes c
        JOIN estadios e ON c.id = e.club_id
        WHERE c.id = ?
    ''', (club_id,))
    resultado = cursor.fetchone()
    conn.close()
    return resultado