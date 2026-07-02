import sqlite3
from config import DB_NAME


def get_connection():
    return sqlite3.connect(DB_NAME)

def init_db():
    conn = get_connection()
    cursor = conn.cursor()
    # Tabla de clubes
    cursor.execute('''CREATE TABLE IF NOT EXISTS clubes 
                      (id INTEGER PRIMARY KEY, user_id INTEGER, nombre TEXT, presupuesto INTEGER)''')
    # Tabla de jugadores
    cursor.execute('''CREATE TABLE IF NOT EXISTS jugadores 
                      (id INTEGER PRIMARY KEY, club_id INTEGER, nombre TEXT, posicion TEXT, habilidad INTEGER)''')
    # Tabla de estadios
    cursor.execute('''CREATE TABLE IF NOT EXISTS estadios
                      (
                          club_id   INTEGER PRIMARY KEY,
                          nombre    TEXT,
                          nivel     INTEGER,
                          capacidad INTEGER
                      )''')

    conn.commit()
    conn.close()

    print("Base de datos inicializada correctamente.")
