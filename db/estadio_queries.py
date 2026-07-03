from db.database import get_connection

def obtener_info_club_y_estadio(user_id):
    conn = get_connection()
    cursor = conn.cursor()
    # Usamos JOIN para traer datos de ambas tablas en una sola consulta
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