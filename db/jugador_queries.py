from db.database import get_connection


def crear_jugador(club_id, nombre, numero, posicion_id, edad, vel, res, anti, sere, trab, pase, ctrl, prof, pot):
    """ Inserta un nuevo jugador en la base de datos usando posicion_id como FK. """

    # Calculamos la media de atributos para el valor y la estrella
    suma_atributos = vel + res + anti + sere + trab + pase + ctrl
    # Fórmula sencilla: (Suma * 1000) * (potencial / 10)
    valor = (suma_atributos * 1000) * (pot / 10)

    # Si la media de los atributos técnicos/físicos es > 85, es estrella
    es_estrella = 1 if (suma_atributos / 7) > 85 else 0

    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute('''
                   INSERT INTO jugadores (club_id, nombre, numero, posicion_id, edad, velocidad, resistencia,
                                          anticipacion, serenidad, trabajo_equipo, precision_pases,
                                          control_balon, profesionalidad, potencial, valor, es_estrella)
                   VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                   ''', (club_id, nombre, numero, posicion_id, edad, vel, res, anti, sere, trab, pase, ctrl, prof, pot, valor,
                         es_estrella))
    conn.commit()
    conn.close()


def insertar_jugador_en_cursor(cursor, club_id, data):
    # Cálculo interno
    suma = data['vel'] + data['res'] + data['anti'] + data['sere'] + data['trab'] + data['pase'] + data['ctrl']
    valor = (suma * 1000) * (data['pot'] / 10)
    es_estrella = 1 if (suma / 7) > 85 else 0

    cursor.execute('''
                   INSERT INTO jugadores (club_id, nombre, numero, posicion_id, edad, velocidad, resistencia,
                                          anticipacion, serenidad, trabajo_equipo, precision_pases,
                                          control_balon, profesionalidad, potencial, valor, es_estrella)
                   VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                   ''', (club_id, data['nombre'], data['numero'], data['posicion_id'], data['edad'], data['vel'], data['res'],
                         data['anti'], data['sere'], data['trab'], data['pase'], data['ctrl'],
                         data['prof'], data['pot'], valor, es_estrella))

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

    # Seleccionamos todas las columnas necesarias para la ficha
    cursor.execute('''
                   SELECT nombre,
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