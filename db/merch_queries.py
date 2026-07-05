

def actualizar_precio_camiseta(jugador_id, precio):
    conn = get_connection()
    cursor = conn.cursor()
    # Usamos INSERT OR REPLACE para asegurar que siempre exista el registro
    cursor.execute('''
        INSERT OR REPLACE INTO merchandising_jugadores (jugador_id, precio_camiseta) 
        VALUES (?, ?)
    ''', (jugador_id, precio))
    conn.commit()
    conn.close()

def obtener_precio_camiseta(jugador_id):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute('SELECT precio_camiseta FROM merchandising_jugadores WHERE jugador_id = ?', (jugador_id,))
    res = cursor.fetchone()
    conn.close()
    return res[0] if res else 50.0 # Precio por defecto


def actualizar_precio_tienda_club(club_id, nuevo_precio):
    """Actualiza o crea el precio de la camiseta para todos los jugadores del club."""
    conn = get_connection()
    cursor = conn.cursor()

    # Obtenemos todos los IDs de jugadores del club
    cursor.execute("SELECT id FROM jugadores WHERE club_id = ?", (club_id,))
    jugadores = cursor.fetchall()

    for jugador in jugadores:
        jugador_id = jugador[0]

        # Intentamos actualizar
        cursor.execute('''
                       UPDATE merchandising_jugadores
                       SET precio_camiseta = ?
                       WHERE jugador_id = ?
                       ''', (nuevo_precio, jugador_id))

        # Si no se actualizó nada, significa que no existe el registro, así que lo insertamos
        if cursor.rowcount == 0:
            cursor.execute('''
                           INSERT INTO merchandising_jugadores (jugador_id, precio_camiseta, ventas_totales)
                           VALUES (?, ?, 0)
                           ''', (jugador_id, nuevo_precio))

    conn.commit()
    conn.close()

def actualizar_precio_individual(jugador_id, nuevo_precio):
    conn = get_connection()
    cursor = conn.cursor()
    # Intentamos actualizar, si no existe, insertamos (por si el jugador no tenía registro)
    cursor.execute('''
        INSERT INTO merchandising_jugadores (jugador_id, precio_camiseta, ventas_totales)
        VALUES (?, ?, 0)
        ON CONFLICT(jugador_id) DO UPDATE SET precio_camiseta = ?
    ''', (jugador_id, nuevo_precio, nuevo_precio))
    conn.commit()
    conn.close()

def actualizar_precio_producto_catering(club_id, producto, nuevo_precio):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute('''
        INSERT INTO catering_precios (club_id, producto, precio)
        VALUES (?, ?, ?)
        ON CONFLICT(club_id, producto) DO UPDATE SET precio = ?
    ''', (club_id, producto, nuevo_precio, nuevo_precio))
    conn.commit()
    conn.close()

def obtener_precios_catering(club_id):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute('SELECT producto, precio FROM catering_precios WHERE club_id = ?', (club_id,))
    res = cursor.fetchall()
    conn.close()
    return res

def obtener_ventas_catering(club_id):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute('SELECT producto, precio, ventas_totales FROM catering_precios WHERE club_id = ?', (club_id,))
    res = cursor.fetchall()
    conn.close()
    return res # Devuelve [('bebida', 2.0, 50), ...]

def obtener_ventas_tienda(club_id):
    conn = get_connection()
    cursor = conn.cursor()
    # Unimos con la tabla jugadores para obtener el nombre
    cursor.execute('''
        SELECT j.nombre, m.precio_camiseta, m.ventas_totales 
        FROM merchandising_jugadores m
        JOIN jugadores j ON m.jugador_id = j.id
        WHERE j.club_id = ?
    ''', (club_id,))
    res = cursor.fetchall()
    conn.close()
    return res # Devuelve [('Nombre Jugador', 50.0, 10), ...]

from db.database import get_connection

# --- Ventas de Camisetas ---
def registrar_venta_camiseta(jugador_id, cantidad=1):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute('''
        UPDATE merchandising_jugadores 
        SET ventas_totales = ventas_totales + ? 
        WHERE jugador_id = ?
    ''', (cantidad, jugador_id))
    conn.commit()
    conn.close()

# --- Ventas de Catering ---
def registrar_venta_catering(club_id, producto, cantidad=1):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute('''
        UPDATE catering_precios 
        SET ventas_totales = ventas_totales + ? 
        WHERE club_id = ? AND producto = ?
    ''', (cantidad, club_id, producto))
    conn.commit()
    conn.close()

# --- Obtención de Niveles (Añadir a db/club_queries.py) ---
def obtener_niveles_servicios(club_id):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute('SELECT nivel_catering, nivel_tienda FROM estadio_servicios WHERE club_id = ?', (club_id,))
    res = cursor.fetchone()
    conn.close()
    return res if res else (0, 0)

def puede_vender(club_id, tipo_servicio):
    """tipo_servicio: 'catering' o 'tienda'"""
    conn = get_connection()
    cursor = conn.cursor()
    columna = "nivel_catering" if tipo_servicio == 'catering' else "nivel_tienda"
    cursor.execute(f"SELECT {columna} FROM estadio_servicios WHERE club_id = ?", (club_id,))
    res = cursor.fetchone()
    conn.close()
    return res and res[0] >= 1