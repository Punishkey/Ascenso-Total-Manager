from db.database import get_connection

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