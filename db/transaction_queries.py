import sqlite3
from datetime import datetime
from config import DB_NAME


def registrar_resultado_partido(club_id, rival_id, goles_propios, goles_rival):
    goles_propios = int(goles_propios)
    goles_rival = int(goles_rival)
    resultado = 1 if goles_propios > goles_rival else (0 if goles_propios == goles_rival else -1)

    try:
        conn = sqlite3.connect(DB_NAME)
        cursor = conn.cursor()
        query = """
                INSERT INTO historial_partidos
                    (club_id, rival_id, goles_propios, goles_rival, resultado, fecha)
                VALUES (?, ?, ?, ?, ?, ?)
                """
        cursor.execute(query, (club_id, rival_id, goles_propios, goles_rival, resultado, datetime.now()))
        nuevo_id = cursor.lastrowid
        conn.commit()
        conn.close()
        return nuevo_id
    except Exception as e:
        print(f"Error al guardar historial: {e}")
        return None


def obtener_estadisticas_club(club_id):
    try:
        conn = sqlite3.connect(DB_NAME)
        cursor = conn.cursor()
        cursor.execute("SELECT resultado, COUNT(*) FROM historial_partidos WHERE club_id = ? GROUP BY resultado", (club_id,))
        data = cursor.fetchall()
        stats = {"total": 0, "victorias": 0, "empates": 0, "derrotas": 0}

        for res, count in data:
            val = int(res)
            if val == 1: stats["victorias"] = count
            elif val == 0: stats["empates"] = count
            elif val == -1: stats["derrotas"] = count
            stats["total"] += count

        conn.close()
        return stats
    except Exception:
        return {"total": 0, "victorias": 0, "empates": 0, "derrotas": 0}