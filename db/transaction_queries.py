import sqlite3
from datetime import datetime
from config import DB_NAME


def registrar_resultado_partido(club_id, rival_id, goles_propios, goles_rival, gano):
    try:
        conn = sqlite3.connect(DB_NAME)
        cursor = conn.cursor()

        query = """
                INSERT INTO historial_partidos
                    (club_id, rival_id, goles_propios, goles_rival, es_victoria, fecha)
                VALUES (?, ?, ?, ?, ?, ?) \
                """
        cursor.execute(query, (club_id, rival_id, goles_propios, goles_rival, int(gano), datetime.now()))

        conn.commit()
        conn.close()
        return True
    except Exception as e:
        print(f"Error al guardar historial: {e}")
        return False