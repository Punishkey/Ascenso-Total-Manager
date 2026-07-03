import sqlite3
from datetime import datetime
from config import DB_NAME


def registrar_resultado_partido(club_id, rival_id, goles_propios, goles_rival, gano):
    # Determinamos el resultado numérico para el registro
    if goles_propios > goles_rival:
        resultado = 1
    elif goles_propios == goles_rival:
        resultado = 0
    else:
        resultado = -1

    try:
        conn = sqlite3.connect(DB_NAME)
        cursor = conn.cursor()

        query = """
                INSERT INTO historial_partidos
                    (club_id, rival_id, goles_propios, goles_rival, resultado, fecha)
                VALUES (?, ?, ?, ?, ?, ?) \
                """
        cursor.execute(query, (club_id, rival_id, goles_propios, goles_rival, resultado, datetime.now()))

        conn.commit()
        conn.close()
        return True
    except Exception as e:
        print(f"Error al guardar historial: {e}")
        return False


def obtener_estadisticas_club(club_id):
    """
    Retorna un diccionario con: total, victorias, empates, derrotas
    """
    try:
        conn = sqlite3.connect(DB_NAME)
        cursor = conn.cursor()

        # Obtenemos el conteo agrupado por resultado
        cursor.execute("""
                       SELECT resultado, COUNT(*)
                       FROM historial_partidos
                       WHERE club_id = ?
                       GROUP BY resultado
                       """, (club_id,))

        data = cursor.fetchall()
        stats = {1: 0, 0: 0, -1: 0, "total": 0}

        for res, count in data:
            stats[res] = count
            stats["total"] += count

        conn.close()
        return {"total": stats["total"], "victorias": stats[1], "empates": stats[0], "derrotas": stats[-1]}
    except Exception as e:
        print(f"Error al obtener estadísticas: {e}")
        return {"total": 0, "victorias": 0, "empates": 0, "derrotas": 0}