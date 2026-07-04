import sqlite3
from config import DB_NAME

def publicar_jugador(jugador_id, club_vendedor_id, precio):
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()

    cursor.execute("SELECT id FROM fichajes WHERE jugador_id = ?", (jugador_id,))
    if cursor.fetchone():
        return False  # Ya está en venta

    cursor.execute("""
        INSERT INTO fichajes (jugador_id, club_vendedor_id, precio, fecha_publicacion)
        VALUES (?, ?, ?, CURRENT_TIMESTAMP)
    """, (jugador_id, club_vendedor_id, precio))
    conn.commit()
    conn.close()
    return True


def obtener_jugadores_en_mercado():
    """Obtiene los jugadores en mercado junto con su media calculada."""
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    # Calculamos la media al vuelo sumando todos los atributos
    query = """
            SELECT f.id,
                   j.nombre,
                   j.posicion_id,
                   f.precio,
                   IFNULL(c.nombre, 'Club Desconocido'),
                   (j.velocidad + j.resistencia + j.anticipacion + j.serenidad +
                    j.trabajo_equipo + j.precision_pases + j.control_balon +
                    j.profesionalidad + j.potencial) / 9.0
            FROM fichajes f
                     LEFT JOIN jugadores j ON f.jugador_id = j.id
                     LEFT JOIN clubes c ON f.club_vendedor_id = c.id \
            """

    cursor.execute(query)
    resultados = cursor.fetchall()
    conn.close()
    return resultados


def ejecutar_compra(fichaje_id, comprador_club_id):
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    try:
        # Obtenemos datos del fichaje
        cursor.execute("SELECT jugador_id, club_vendedor_id, precio FROM fichajes WHERE id = ?", (fichaje_id,))
        fichaje = cursor.fetchone()
        if not fichaje: return False, "No existe el fichaje."
        jugador_id, vendedor_id, precio = fichaje

        # Verificamos presupuesto del comprador
        cursor.execute("SELECT presupuesto FROM clubes WHERE id = ?", (comprador_club_id,))
        presupuesto = cursor.fetchone()[0]
        if presupuesto < precio: return False, "Saldo insuficiente."

        # Realizamos la transacción
        cursor.execute("UPDATE clubes SET presupuesto = presupuesto - ? WHERE id = ?", (precio, comprador_club_id))
        cursor.execute("UPDATE clubes SET presupuesto = presupuesto + ? WHERE id = ?", (precio, vendedor_id))
        cursor.execute("UPDATE jugadores SET club_id = ? WHERE id = ?", (comprador_club_id, jugador_id))
        cursor.execute("DELETE FROM fichajes WHERE id = ?", (fichaje_id,))

        conn.commit()
        return True, "Compra realizada con éxito."
    except Exception as e:
        conn.rollback()
        return False, str(e)
    finally:
        conn.close()

def retirar_jugador_mercado(fichaje_id):
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute("DELETE FROM fichajes WHERE id = ?", (fichaje_id,))
    conn.commit()
    conn.close()

def obtener_club_vendedor_id(fichaje_id):
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute("SELECT club_vendedor_id FROM fichajes WHERE id = ?", (fichaje_id,))
    result = cursor.fetchone()
    conn.close()
    return result[0] if result else None

def obtener_jugadores_en_venta_del_club(club_id):
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute("""
        SELECT f.id, j.nombre, f.precio
        FROM fichajes f
        JOIN jugadores j ON f.jugador_id = j.id
        WHERE f.club_vendedor_id = ?
    """, (club_id,))
    resultados = cursor.fetchall()
    conn.close()
    return resultados