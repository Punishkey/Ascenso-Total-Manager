import sqlite3
from config import DB_NAME


def init_db():
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    # Tabla de clubes
    cursor.execute('''CREATE TABLE IF NOT EXISTS clubes 
                      (id INTEGER PRIMARY KEY, user_id INTEGER, nombre TEXT, presupuesto INTEGER)''')
    # Tabla de jugadores
    cursor.execute('''CREATE TABLE IF NOT EXISTS jugadores 
                      (id INTEGER PRIMARY KEY, club_id INTEGER, nombre TEXT, posicion TEXT, habilidad INTEGER)''')
    conn.commit()
    conn.close()

def crear_club(user_id, nombre_club):
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute('INSERT INTO clubes (user_id, nombre, presupuesto) VALUES (?, ?, 1000)', (user_id, nombre_club))
    conn.commit()
    club_id = cursor.lastrowid
    conn.close()
    return club_id
