from db.database import get_connection
from utils.generator import (obtener_estructura_plantilla,
                             generar_jugador_con_posicion,
                             generar_dorsales_disponibles)
from db.jugador_queries import insertar_jugador_en_cursor
from config import (PRESUPUESTO_INICIAL, NIVEL_INICIAL, CAPACIDAD_INICIAL,
                    COSTE_MEJORA_ESTADIO, COSTE_MEJORA_SERVICIOS, NIVEL_MAXIMO_MEJORA_SERVICIOS, TIEMPO_MEJORA_ESTADIO)
from datetime import datetime, timedelta


def crear_club(user_id, nombre_club):
    conn = get_connection()
    cursor = conn.cursor()
    try:
        cursor.execute('INSERT INTO clubes (user_id, nombre, presupuesto) VALUES (?, ?, ?)',
                       (user_id, nombre_club, PRESUPUESTO_INICIAL))
        club_id = cursor.lastrowid
        cursor.execute('INSERT INTO estadios (club_id, nombre, nivel, capacidad) VALUES (?, ?, ?, ?)',
                       (club_id, f"Estadio del {nombre_club}", NIVEL_INICIAL, CAPACIDAD_INICIAL))
        cursor.execute('INSERT INTO estadio_servicios (club_id) VALUES (?)', (club_id,))
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
        cursor.execute('SELECT presupuesto FROM clubes WHERE id = ?', (club_id,))
        presupuesto = cursor.fetchone()[0]
        cursor.execute('SELECT nivel FROM estadios WHERE club_id = ?', (club_id,))
        nivel_actual = cursor.fetchone()[0]
        coste = nivel_actual * COSTE_MEJORA_ESTADIO
        if presupuesto >= coste:
            return True, nivel_actual
        else:
            return False, nivel_actual
    except Exception as e:
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
    cursor.execute("SELECT id, nombre FROM clubes WHERE id != ? ORDER BY RANDOM() LIMIT 1", (usuario_club_id,))
    rival = cursor.fetchone()
    conn.close()
    return rival


def obtener_presupuesto(club_id):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute('SELECT presupuesto FROM clubes WHERE id = ?', (club_id,))
    resultado = cursor.fetchone()
    conn.close()
    return resultado[0] if resultado else 0


def restar_dinero(club_id, cantidad):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute('UPDATE clubes SET presupuesto = presupuesto - ? WHERE id = ?', (cantidad, club_id))
    conn.commit()
    conn.close()


def obtener_tiempo_restante_construccion(club_id, tipo_servicio=None):
    conn = get_connection()
    cursor = conn.cursor()
    if tipo_servicio:
        campo = "fin_catering" if tipo_servicio == 'catering' else "fin_tienda"
        cursor.execute(f'SELECT {campo} FROM estadio_servicios WHERE club_id = ?', (club_id,))
    else:
        cursor.execute('SELECT fecha_finalizacion FROM estadios WHERE club_id = ?', (club_id,))

    resultado = cursor.fetchone()
    if not resultado or resultado[0] is None:
        conn.close()
        return None

    fecha_fin = datetime.fromisoformat(resultado[0])
    ahora = datetime.now()
    if ahora >= fecha_fin:
        conn.close()
        return "FINALIZADO"

    delta = fecha_fin - ahora
    horas, rem = divmod(int(delta.total_seconds()), 3600)
    minutos, _ = divmod(rem, 60)
    conn.close()
    return f"{horas}h {minutos}m"


def check_y_aplicar_mejora(club_id):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute('SELECT fecha_finalizacion, nivel FROM estadios WHERE club_id = ?', (club_id,))
    res = cursor.fetchone()
    if res and res[0]:
        fecha_fin = datetime.fromisoformat(res[0])
        if datetime.now() >= fecha_fin:
            cursor.execute('''
                           UPDATE estadios
                           SET nivel              = nivel + 1,
                               capacidad          = capacidad + 2500,
                               fecha_finalizacion = NULL
                           WHERE club_id = ?
                           ''', (club_id,))
            conn.commit()
            conn.close()
            return True
    conn.close()
    return False


def check_y_aplicar_mejora_servicio(club_id, tipo_servicio):
    conn = get_connection()
    cursor = conn.cursor()
    campo_fin = "fin_catering" if tipo_servicio == 'nivel_catering' else "fin_tienda"
    cursor.execute(f'SELECT {campo_fin}, {tipo_servicio} FROM estadio_servicios WHERE club_id = ?', (club_id,))
    res = cursor.fetchone()
    if res and res[0]:
        fecha_fin = datetime.fromisoformat(res[0])
        if datetime.now() >= fecha_fin:
            cursor.execute(f'''
                UPDATE estadio_servicios 
                SET {tipo_servicio} = {tipo_servicio} + 1, 
                    {campo_fin} = NULL 
                WHERE club_id = ?
            ''', (club_id,))
            conn.commit()
            conn.close()
            return True
    conn.close()
    return False


def calcular_ingresos_por_servicios(club_id, asistentes):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute('SELECT nivel_catering, nivel_tienda FROM estadio_servicios WHERE club_id = ?', (club_id,))
    res = cursor.fetchone()
    if not res:
        conn.close()
        return 0
    nivel_catering, nivel_tienda = res
    ingresos = asistentes * (nivel_catering * 2 + nivel_tienda * 1)
    conn.close()
    return ingresos


def mejorar_servicio_db(club_id, tipo_servicio):
    conn = get_connection()
    cursor = conn.cursor()
    try:
        cursor.execute('SELECT nivel FROM estadios WHERE club_id = ?', (club_id,))
        res_estadio = cursor.fetchone()
        nivel_estadio = res_estadio[0] if res_estadio else 1

        cursor.execute(f'SELECT {tipo_servicio} FROM estadio_servicios WHERE club_id = ?', (club_id,))
        res_serv = cursor.fetchone()
        nivel_actual = res_serv[0] if res_serv else 1

        if nivel_actual >= NIVEL_MAXIMO_MEJORA_SERVICIOS:
            return False, "Nivel máximo alcanzado"

        coste = COSTE_MEJORA_SERVICIOS + nivel_estadio

        cursor.execute('SELECT presupuesto FROM clubes WHERE id = ?', (club_id,))
        res_presupuesto = cursor.fetchone()
        presupuesto = res_presupuesto[0] if res_presupuesto else 0

        if presupuesto >= coste:
            duracion = timedelta(hours=TIEMPO_MEJORA_ESTADIO + nivel_actual)
            fecha_fin = (datetime.now() + duracion).isoformat()
            campo_fin = "fin_catering" if tipo_servicio == 'nivel_catering' else "fin_tienda"

            cursor.execute('UPDATE clubes SET presupuesto = presupuesto - ? WHERE id = ?', (coste, club_id))
            cursor.execute(f'UPDATE estadio_servicios SET {campo_fin} = ? WHERE club_id = ?', (fecha_fin, club_id))
            conn.commit()
            return True, "Obras iniciadas"
        else:
            return False, "Fondos insuficientes"

    except Exception as e:
        conn.rollback()
        return False, f"Error interno: {str(e)}"
    finally:
        conn.close()
