from db.database import get_connection
from utils.generator import (obtener_estructura_plantilla,
                             generar_jugador_con_posicion,
                             generar_dorsales_disponibles)
from db.jugador_queries import insertar_jugador_en_cursor
from config import (PRESUPUESTO_INICIAL, NIVEL_INICIAL, CAPACIDAD_INICIAL,
                    COSTE_MEJORA_ESTADIO)
from datetime import datetime


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

def obtener_nombre_club(club_id):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT nombre FROM clubes WHERE id = ?", (club_id,))
    resultado = cursor.fetchone()
    conn.close()
    return resultado[0] if resultado else "Desconocido"


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

    try:
        # Usamos transacciones para mayor seguridad
        cursor.execute('BEGIN TRANSACTION')

        # Verificar datos (bloqueamos la fila para evitar condiciones de carrera)
        cursor.execute('SELECT presupuesto FROM clubes WHERE id = ?', (club_id,))
        presupuesto = cursor.fetchone()[0]

        cursor.execute('SELECT nivel FROM estadios WHERE club_id = ?', (club_id,))
        nivel_actual = cursor.fetchone()[0]

        coste = nivel_actual * COSTE_MEJORA_ESTADIO

        if presupuesto >= coste:
            nuevo_nivel = nivel_actual + 1

            # Actualizar
            cursor.execute('UPDATE clubes SET presupuesto = presupuesto - ? WHERE id = ?', (coste, club_id))
            cursor.execute('''
                           UPDATE estadios
                           SET nivel     = nivel + 1,
                               capacidad = capacidad + 2500
                           WHERE club_id = ?
                           ''', (club_id,))

            conn.commit()
            return True, nuevo_nivel  # Devolvemos el nivel nuevo
        else:
            return False, nivel_actual

    except Exception as e:
        conn.rollback()  # Si algo falla, deshacemos todo
        print(f"Error en mejora de estadio: {e}")
        return False, None
    finally:
        conn.close()

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

def obtener_rival_ia(usuario_club_id):
    conn = get_connection()
    cursor = conn.cursor()
    # Filtramos por id
    cursor.execute("SELECT id, nombre FROM clubes WHERE id != ? ORDER BY RANDOM() LIMIT 1", (usuario_club_id,))
    rival = cursor.fetchone()
    conn.close()
    return rival

def obtener_presupuesto(club_id):
    """Devuelve el presupuesto actual del club."""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute('SELECT presupuesto FROM clubes WHERE id = ?', (club_id,))
    resultado = cursor.fetchone()
    conn.close()
    return resultado[0] if resultado else 0

def restar_dinero(club_id, cantidad):
    """Resta una cantidad al presupuesto del club."""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute('UPDATE clubes SET presupuesto = presupuesto - ? WHERE id = ?', (cantidad, club_id))
    conn.commit()
    conn.close()


from datetime import datetime


def obtener_tiempo_restante_construccion(club_id):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute('SELECT fecha_finalizacion FROM estadios WHERE club_id = ?', (club_id,))
    resultado = cursor.fetchone()

    if not resultado or resultado[0] is None:
        conn.close()
        return None

    fecha_fin = datetime.fromisoformat(resultado[0])
    ahora = datetime.now()

    if ahora >= fecha_fin:
        # Limpieza automática si ya pasó el tiempo
        cursor.execute('UPDATE estadios SET fecha_finalizacion = NULL WHERE club_id = ?', (club_id,))
        conn.commit()
        conn.close()
        return "FINALIZADO"

    conn.close()
    delta = fecha_fin - ahora
    horas, rem = divmod(int(delta.total_seconds()), 3600)
    minutos, _ = divmod(rem, 60)

    return f"{horas}h {minutos}m"


def check_y_aplicar_mejora(club_id):
    conn = get_connection()
    cursor = conn.cursor()
    # Obtenemos fecha y nivel actual
    cursor.execute('SELECT fecha_finalizacion, nivel FROM estadios WHERE club_id = ?', (club_id,))
    res = cursor.fetchone()

    if res and res[0]:
        fecha_fin = datetime.fromisoformat(res[0])
        # Si el tiempo ya pasó
        if datetime.now() >= fecha_fin:
            # Aplicamos la mejora: Nivel + 1, Capacidad + 2500, limpiamos fecha
            cursor.execute('''
                           UPDATE estadios
                           SET nivel              = nivel + 1,
                               capacidad          = capacidad + 2500,
                               fecha_finalizacion = NULL
                           WHERE club_id = ?
                           ''', (club_id,))
            conn.commit()
            conn.close()
            return True  # Retornamos True porque se acaba de aplicar una mejora

    conn.close()
    return False