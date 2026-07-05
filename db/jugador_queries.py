from config import POTENCIAL_FACTOR, EDAD_DECLIVE
from db.database import get_connection


def crear_jugador(club_id, nombre, numero, posicion_id, edad, vel, res, anti, sere, trab, pase, ctrl, prof, pot):
    """ Inserta un nuevo jugador en la base de datos usando posicion_id como FK. """

    suma_atributos = vel + res + anti + sere + trab + pase + ctrl
    valor = (suma_atributos * 1000) * (pot / 10)
    es_estrella = 1 if (suma_atributos / 7) > 85 else 0

    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute('''
                   INSERT INTO jugadores (club_id, nombre, numero, posicion_id, edad, velocidad, resistencia,
                                          anticipacion, serenidad, trabajo_equipo, precision_pases,
                                          control_balon, profesionalidad, potencial, valor, es_estrella)
                   VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                   ''', (club_id, nombre, numero, numero, posicion_id, edad, vel, res, anti, sere, trab, pase, ctrl, prof, pot, valor,
                         es_estrella))

    nuevo_jugador_id = cursor.lastrowid

    cursor.execute('''
                   INSERT INTO historico_jugadores
                   (jugador_id, nombre, numero, posicion_id, edad, velocidad_base, resistencia_base,
                    anticipacion_base, serenidad_base, trabajo_equipo_base, precision_pases_base,
                    control_balon_base, profesionalidad_base)
                   VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                   ''',
                   (nuevo_jugador_id, nombre, numero, posicion_id, edad, vel, res, anti, sere, trab, pase, ctrl, prof))

    conn.commit()
    conn.close()


def insertar_jugador_en_cursor(cursor, club_id, data):
    suma = data['vel'] + data['res'] + data['anti'] + data['sere'] + data['trab'] + data['pase'] + data['ctrl']
    valor = (suma * 1000) * (data['pot'] / 10)
    es_estrella = 1 if (suma / 7) > 85 else 0

    cursor.execute('''
                   INSERT INTO jugadores (club_id, nombre, numero, posicion_id, edad, velocidad, resistencia,
                                          anticipacion, serenidad, trabajo_equipo, precision_pases,
                                          control_balon, profesionalidad, potencial, valor, es_estrella)
                   VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                   ''', (club_id, data['nombre'], data['numero'], data['posicion_id'], data['edad'], data['vel'],
                         data['res'],
                         data['anti'], data['sere'], data['trab'], data['pase'], data['ctrl'],
                         data['prof'], data['pot'], valor, es_estrella))

    nuevo_jugador_id = cursor.lastrowid

    cursor.execute('''
                   INSERT INTO historico_jugadores
                   (jugador_id, nombre, numero, posicion_id, edad, velocidad_base, resistencia_base,
                    anticipacion_base, serenidad_base, trabajo_equipo_base, precision_pases_base,
                    control_balon_base, profesionalidad_base)
                   VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                   ''',
                   (nuevo_jugador_id, data['nombre'], data['numero'], data['posicion_id'], data['edad'],
                    data['vel'], data['res'], data['anti'], data['sere'], data['trab'],
                    data['pase'], data['ctrl'], data['prof']))


def obtener_plantilla(club_id):
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute('''
                   SELECT j.numero,
                          j.nombre,
                          p.abreviatura,
                          j.es_estrella,
                          j.valor,
                          ROUND((j.velocidad + j.resistencia + j.anticipacion + j.serenidad +
                                 j.trabajo_equipo + j.precision_pases + j.control_balon +
                                 j.profesionalidad + j.potencial) / 9.0) as media
                   FROM jugadores j
                            JOIN posiciones p ON j.posicion_id = p.id
                   WHERE j.club_id = ?
                   ORDER BY CASE p.abreviatura
                                WHEN 'POR' THEN 1
                                WHEN 'DFC' THEN 2
                                WHEN 'MCD' THEN 3
                                WHEN 'MC' THEN 4
                                WHEN 'EXT' THEN 5
                                WHEN 'DC' THEN 6
                                ELSE 7 END, j.numero
                   ''', (club_id,))

    jugadores = cursor.fetchall()
    conn.close()
    return jugadores


def obtener_jugador_por_numero(club_id, numero):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute('''
                   SELECT id,
                          nombre,
                          edad,
                          velocidad,
                          resistencia,
                          anticipacion,
                          serenidad,
                          trabajo_equipo,
                          precision_pases,
                          control_balon,
                          profesionalidad,
                          potencial,
                          valor,
                          es_estrella
                   FROM jugadores
                   WHERE club_id = ?
                     AND numero = ?
                   ''', (club_id, numero))

    jugador = cursor.fetchone()
    conn.close()
    return jugador


def obtener_media_titular(club_id):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute('''
                   SELECT AVG(media)
                   FROM (SELECT (velocidad + resistencia + anticipacion + 
                                 serenidad + trabajo_equipo + precision_pases + 
                                 control_balon + profesionalidad + 
                                 potencial) / 9.0 as media
                         FROM jugadores
                         WHERE club_id = ?
                         ORDER BY media DESC
                         LIMIT 11)
                   ''', (club_id,))

    resultado = cursor.fetchone()[0]
    conn.close()
    return round(resultado, 2) if resultado else 0


def obtener_jugador_aleatorio(club_id):
    try:
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT nombre FROM jugadores WHERE club_id = ? ORDER BY RANDOM() LIMIT 1", (club_id,))
        resultado = cursor.fetchone()
        conn.close()
        return resultado[0] if resultado else "Un jugador desconocido"
    except Exception as e:
        print(f"Error al obtener jugador aleatorio: {e}")
        return "El equipo"


def obtener_lista_jugadores(club_id):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT nombre, numero FROM jugadores WHERE club_id = ? ORDER BY numero", (club_id,))
    resultados = cursor.fetchall()
    conn.close()
    return [{"nombre": fila[0], "numero": fila[1]} for fila in resultados]


def entrenar_atributo(jugador_id, atributo, cantidad):
    conn = get_connection()
    cursor = conn.cursor()
    query = f"UPDATE jugadores SET {atributo} = {atributo} + ? WHERE id = ?"
    cursor.execute(query, (cantidad, jugador_id))
    conn.commit()
    conn.close()


def puede_mejorar(jugador, atributo):
    mapa_atributos = {
        "velocidad": 3, "resistencia": 4, "anticipacion": 5,
        "serenidad": 6, "trabajo_equipo": 7, "precision_pases": 8,
        "control_balon": 9, "profesionalidad": 10
    }

    idx = mapa_atributos.get(atributo)
    if idx is None: return False, "Atributo no reconocido."

    edad = jugador[2]
    valor_actual = jugador[idx]
    potencial = jugador[11]
    techo = potencial * POTENCIAL_FACTOR

    if valor_actual >= techo:
        return False, f"El jugador ha llegado a su límite de potencial ({techo}) en {atributo}."

    if edad >= EDAD_DECLIVE:
        return False, "El jugador es demasiado veterano y ha dejado de progresar."

    return True, "Progreso permitido."


def obtener_jugador_con_historico(club_id, numero):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute('''
                   SELECT j.*,
                          h.velocidad_base,
                          h.resistencia_base,
                          h.anticipacion_base,
                          h.serenidad_base,
                          h.trabajo_equipo_base,
                          h.precision_pases_base,
                          h.control_balon_base,
                          h.profesionalidad_base
                   FROM jugadores j
                            JOIN historico_jugadores h ON j.id = h.jugador_id
                   WHERE j.club_id = ?
                     AND j.numero = ?
                   ''', (club_id, numero))

    data = cursor.fetchone()
    conn.close()
    return data


def obtener_id_jugador_aleatorio(club_id):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute('SELECT id FROM jugadores WHERE club_id = ? ORDER BY RANDOM() LIMIT 1', (club_id,))
    res = cursor.fetchone()
    conn.close()
    return res[0] if res else None