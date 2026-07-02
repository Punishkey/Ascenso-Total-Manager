from db.database import get_connection
from config import PRESUPUESTO_INICIAL

def crear_club(user_id, nombre_club):
    conn = get_connection()
    cursor = conn.cursor()

    # Crear el club
    cursor.execute('INSERT INTO clubes (user_id, nombre, presupuesto) VALUES (?, ?, ?)',
                   (user_id, nombre_club, PRESUPUESTO_INICIAL))
    club_id = cursor.lastrowid

    # Crear el estadio
    cursor.execute('INSERT INTO estadios (club_id, nombre, nivel, capacidad) VALUES (?, ?, ?, ?)',
                   (club_id, f"Estadio de {nombre_club}", 1, 5000))
    
    conn.commit()
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