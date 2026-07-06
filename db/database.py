import sqlite3
from config import DB_NAME


def get_connection():
    return sqlite3.connect(DB_NAME)

def init_db():
    try:
        with sqlite3.connect(DB_NAME) as conn:
            cursor = conn.cursor()
            # Tabla de clubes
            cursor.execute('''CREATE TABLE IF NOT EXISTS clubes 
                              (id INTEGER PRIMARY KEY, user_id INTEGER, nombre TEXT, presupuesto INTEGER)''')
            # Tabla de estadios
            cursor.execute('''CREATE TABLE IF NOT EXISTS estadios
                              (club_id INTEGER PRIMARY KEY,nombre TEXT,nivel INTEGER, capacidad INTEGER, ingresos_base INTEGER, fecha_finalizacion TIMESTAMP DEFAULT NULL, popularidad INTEGER DEFAULT 5)''')
            # Tabla de jugadores
            cursor.execute('''CREATE TABLE IF NOT EXISTS jugadores 
                              (id INTEGER PRIMARY KEY, club_id INTEGER, nombre TEXT, numero INTEGER, posicion_id TEXT, edad INTEGER,
                              velocidad INTEGER, resistencia INTEGER, anticipacion INTEGER, serenidad INTEGER,
                              trabajo_equipo INTEGER, precision_pases INTEGER, control_balon INTEGER,
                              profesionalidad INTEGER, potencial INTEGER, valor INTEGER, es_estrella BOOLEAN DEFAULT 0, FOREIGN KEY (club_id) REFERENCES clubes(id))''')
            # Tabla de posiciones
            cursor.execute('''CREATE TABLE IF NOT EXISTS posiciones 
                              (id INTEGER PRIMARY KEY, abreviatura TEXT UNIQUE, nombre_completo TEXT)''')
            # Crear tabla historial de partidos
            cursor.execute('''CREATE TABLE IF NOT EXISTS historial_partidos
                              (id INTEGER PRIMARY KEY AUTOINCREMENT, club_id INTEGER, rival_id INTEGER, goles_propios INTEGER,goles_rival INTEGER, es_victoria INTEGER, fecha DATETIME, resultado INTEGER DEFAULT 0)''')
            # Crear tabla fichajes
            cursor.execute('''CREATE TABLE IF NOT EXISTS fichajes 
                              (id INTEGER PRIMARY KEY AUTOINCREMENT, jugador_id INTEGER, club_vendedor_id INTEGER, precio INTEGER, fecha_publicacion DATETIME, FOREIGN KEY (jugador_id) REFERENCES jugadores(id), FOREIGN KEY (club_vendedor_id) REFERENCES clubes(id))''')
            # Crear tabla historial Jugadores
            cursor.execute('''CREATE TABLE IF NOT EXISTS historico_jugadores 
                              (id INTEGER PRIMARY KEY AUTOINCREMENT, jugador_id INTEGER, nombre TEXT, numero INTEGER, posicion_id TEXT, edad INTEGER, velocidad_base INTEGER, resistencia_base INTEGER, anticipacion_base INTEGER, serenidad_base INTEGER, trabajo_equipo_base INTEGER, precision_pases_base INTEGER, control_balon_base INTEGER, profesionalidad_base INTEGER, FOREIGN KEY(jugador_id) REFERENCES jugadores(id));''')
            # Crear tabla servicios del estadio
            cursor.execute('''CREATE TABLE IF NOT EXISTS estadio_servicios 
                              (club_id INTEGER PRIMARY KEY, nivel_catering INTEGER DEFAULT 1, nivel_tienda INTEGER DEFAULT 1, fin_catering TEXT DEFAULT NULL, fin_tienda TEXT DEFAULT NULL, FOREIGN KEY(club_id) REFERENCES clubes(id));''')
            # Crear tabla merchandising
            cursor.execute('''CREATE TABLE IF NOT EXISTS merchandising_jugadores (jugador_id INTEGER PRIMARY KEY, precio_camiseta REAL DEFAULT 50.0, ventas_totales INTEGER DEFAULT 0, FOREIGN KEY (jugador_id) REFERENCES jugadores(id));''')
            # Crear tabla eventos partido
            cursor.execute('''CREATE TABLE IF NOT EXISTS eventos_partido (id INTEGER PRIMARY KEY AUTOINCREMENT, partido_id INTEGER, jugador_nombre TEXT, equipo_nombre TEXT, tipo_evento TEXT, minuto INTEGER);''')
            # Crear tabla catering precios
            cursor.execute('''CREATE TABLE IF NOT EXISTS catering_precios (club_id INTEGER NOT NULL, producto TEXT NOT NULL, precio REAL NOT NULL, ventas_totales INTEGER DEFAULT 0, PRIMARY KEY (club_id, producto), FOREIGN KEY (club_id) REFERENCES clubes(id) ON DELETE CASCADE);''')


            # Comprobar si está vacía antes de insertar
            cursor.execute("SELECT count(*) FROM posiciones")
            if cursor.fetchone()[0] == 0:
                posiciones = [
                    (1, 'POR', 'Portero'), (2, 'DFC', 'Defensa Central'),
                    (3, 'MCD', 'Mediocentro'), (4, 'MC', 'Mediocentro'),
                    (5, 'EXT', 'Extremo'), (6, 'DC', 'Delantero')
                ]
                cursor.executemany("INSERT INTO posiciones VALUES (?,?,?)", posiciones)
        print("Base de datos inicializada correctamente.")
    except sqlite3.Error as e:
        print(f"\n❌ ERROR al inicializar la base de datos: {e}")
