from datetime import datetime

from db.database import get_connection

def obtener_info_club_y_estadio(user_id):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute('''
        SELECT c.nombre, c.presupuesto, e.nombre, e.nivel, e.capacidad 
        FROM clubes c
        JOIN estadios e ON c.id = e.club_id
        WHERE c.user_id = ?
    ''', (user_id,))
    resultado = cursor.fetchone()
    conn.close()
    return resultado

def renombrar_estadio_db(club_id, nuevo_nombre):
    try:
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute("UPDATE estadios SET nombre = ? WHERE club_id = ?", (nuevo_nombre, club_id))
        conn.commit()
        conn.close()
        return True
    except:
        return False

def tiene_tienda_merchandising(club_id):
    """Verifica si el club tiene nivel de tienda > 0."""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute('SELECT nivel_tienda FROM estadio_servicios WHERE club_id = ?', (club_id,))
    res = cursor.fetchone()
    conn.close()
    return res[0] > 0 if res and res[0] is not None else False


def obtener_tiempo_restante(fecha_fin_str):
    """
    Recibe la fecha como string (ISO format) y devuelve el tiempo restante.
    """
    if not fecha_fin_str:
        return None

    fecha_fin = datetime.fromisoformat(fecha_fin_str)
    ahora = datetime.now()

    if ahora >= fecha_fin:
        return "¡Listo!"

    restante = fecha_fin - ahora
    horas, rem = divmod(int(restante.total_seconds()), 3600)
    minutos, _ = divmod(rem, 60)
    return f"{horas}h {minutos}m"

def obtener_configuracion_partido(club_id):
    conn = get_connection()
    cursor = conn.cursor()
    # Obtenemos capacidad, precio y popularidad
    cursor.execute('''
        SELECT capacidad, precio_entrada, popularidad, nivel 
        FROM estadios WHERE club_id = ?
    ''', (club_id,))
    res = cursor.fetchone()
    conn.close()
    return res if res else (1500, 10, 5, 1) # Valores por defecto si no existe


def actualizar_popularidad_partido(club_id, es_victoria):
    conn = get_connection()
    cursor = conn.cursor()

    # Obtenemos la popularidad actual
    cursor.execute("SELECT popularidad FROM estadios WHERE club_id = ?", (club_id,))
    res = cursor.fetchone()

    if res:
        popularidad_actual = res[0]
        # +2 si gana, -2 si pierde. Mantenemos el rango entre 0 y 100.
        cambio = 2 if es_victoria else -2
        nueva_popularidad = max(0, min(100, popularidad_actual + cambio))

        cursor.execute("UPDATE estadios SET popularidad = ? WHERE club_id = ?", (nueva_popularidad, club_id))
        conn.commit()
        conn.close()
        return cambio

    conn.close()
    return 0

def tiene_spa(club_id):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT spa_nivel FROM estadio_instalaciones WHERE club_id = ?", (club_id,))
    res = cursor.fetchone()
    conn.close()
    return res and res[0] > 0


def calcular_coste_spa(nivel_actual):
    # Nivel 0 -> 1 cuesta 20k. Aumenta progresivamente.
    return 20000 + (nivel_actual * 10000)


def calcular_tiempo_construccion(nivel_estadio):
    # Regla: 2 horas + 1 hora por nivel de estadio
    horas = 2 + nivel_estadio
    return horas


def obtener_datos_spa(club_id):
    inicializar_instalaciones(club_id)
    conn = get_connection()
    cursor = conn.cursor()
    # Obtenemos nivel del spa y nivel del estadio
    cursor.execute('''SELECT i.spa_nivel, i.fecha_ultima_construccion, e.nivel
                      FROM estadios e
                      LEFT JOIN estadio_instalaciones i ON e.club_id = i.club_id
                      WHERE e.club_id = ?''', (club_id,))
    data = cursor.fetchone()
    conn.close()

    if not data: return {"nivel": 0, "fecha_fin": None, "nivel_estadio": 1}
    return {"nivel": data[0], "fecha_fin": data[1], "nivel_estadio": data[2]}

def inicializar_instalaciones(club_id):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("INSERT OR IGNORE INTO estadio_instalaciones (club_id, spa_nivel) VALUES (?, 0)", (club_id,))
    conn.commit()
    conn.close()