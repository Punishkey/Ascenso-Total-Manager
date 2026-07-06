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