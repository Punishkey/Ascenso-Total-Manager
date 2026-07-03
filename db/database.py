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
    # Tabla de estadios
    cursor.execute('''CREATE TABLE IF NOT EXISTS estadios
                      (club_id INTEGER PRIMARY KEY,nombre TEXT,nivel INTEGER, capacidad INTEGER, ingresos_base INTEGER)''')
    # Tabla de jugadores
    cursor.execute('''CREATE TABLE IF NOT EXISTS jugadores 
                      (id INTEGER PRIMARY KEY, club_id INTEGER, nombre TEXT, numero INTEGER, posicion_id TEXT, edad INTEGER,
                      velocidad INTEGER, resistencia INTEGER, anticipacion INTEGER, serenidad INTEGER,
                      trabajo_equipo INTEGER, precision_pases INTEGER, control_balon INTEGER,
                      profesionalidad INTEGER, potencial INTEGER, valor INTEGER, es_estrella BOOLEAN DEFAULT 0, FOREIGN KEY (club_id) REFERENCES clubes(id))''')
    cursor.execute('''CREATE TABLE IF NOT EXISTS posiciones 
                      (id INTEGER PRIMARY KEY, abreviatura TEXT UNIQUE, nombre_completo TEXT)''')
    # Crear tabla de posiciones
    cursor.execute('''CREATE TABLE IF NOT EXISTS posiciones
                      (id INTEGER PRIMARY KEY, abreviatura TEXT, nombre_completo TEXT)''')
    # Crear tabla historial de partidos
    cursor.execute('''CREATE TABLE IF NOT EXISTS historial_partidos
                      (id INTEGER PRIMARY KEY AUTOINCREMENT, club_id INTEGER, rival_id INTEGER, goles_propios INTEGER,goles_rival INTEGER, es_victoria BOOLEAN, fecha DATETIME, resultado INTEGER DEFAULT 0)''')


    # Comprobar si está vacía antes de insertar
    cursor.execute("SELECT count(*) FROM posiciones")
    if cursor.fetchone()[0] == 0:
        posiciones = [
            (1, 'POR', 'Portero'), (2, 'DFC', 'Defensa Central'),
            (3, 'MCD', 'Mediocentro'), (4, 'MC', 'Mediocentro'),
            (5, 'EXT', 'Extremo'), (6, 'DC', 'Delantero')
        ]
        cursor.executemany("INSERT INTO posiciones VALUES (?,?,?)", posiciones)

    conn.commit()
    conn.close()

    print("Base de datos inicializada correctamente.")
