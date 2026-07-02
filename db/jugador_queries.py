from db.database import get_connection


def crear_jugador(club_id, nombre, posicion_id, edad, vel, res, anti, sere, trab, pase, ctrl, prof, pot):
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
                   INSERT INTO jugadores (club_id, nombre, posicion_id, edad, velocidad, resistencia,
                                          anticipacion, serenidad, trabajo_equipo, precision_pases,
                                          control_balon, profesionalidad, potencial, valor, es_estrella)
                   VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                   ''', (club_id, nombre, posicion_id, edad, vel, res, anti, sere, trab, pase, ctrl, prof, pot, valor,
                         es_estrella))
    conn.commit()
    conn.close()


def insertar_jugador_en_cursor(cursor, club_id, data):
    # Cálculo interno
    suma = data['vel'] + data['res'] + data['anti'] + data['sere'] + data['trab'] + data['pase'] + data['ctrl']
    valor = (suma * 1000) * (data['pot'] / 10)
    es_estrella = 1 if (suma / 7) > 85 else 0

    cursor.execute('''
                   INSERT INTO jugadores (club_id, nombre, posicion_id, edad, velocidad, resistencia,
                                          anticipacion, serenidad, trabajo_equipo, precision_pases,
                                          control_balon, profesionalidad, potencial, valor, es_estrella)
                   VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                   ''', (club_id, data['nombre'], data['posicion_id'], data['edad'], data['vel'], data['res'],
                         data['anti'], data['sere'], data['trab'], data['pase'], data['ctrl'],
                         data['prof'], data['pot'], valor, es_estrella))

def obtener_plantilla(club_id):
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute('''
                   SELECT j.nombre, COALESCE(p.abreviatura, 'N/A'), j.es_estrella, j.valor
                   FROM jugadores j
                            LEFT JOIN posiciones p ON j.posicion_id = p.id
                   WHERE j.club_id = ?
                   ''', (club_id,))

    jugadores = cursor.fetchall()

    conn.close()
    return jugadores