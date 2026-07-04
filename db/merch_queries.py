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