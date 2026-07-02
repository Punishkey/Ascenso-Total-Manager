from db.database import get_connection


def crear_jugador(club_id, nombre, posicion, edad, vel, res, anti, sere, trab, pase, ctrl, prof, pot):
    # Calculamos la media de atributos para el valor y la estrella
    suma_atributos = vel + res + anti + sere + trab + pase + ctrl
    # Fórmula sencilla: (Suma * 1000) * (potencial / 10)
    valor = (suma_atributos * 1000) * (pot / 10)

    # Si la media de los atributos técnicos/físicos es > 85, es estrella
    es_estrella = 1 if (suma_atributos / 7) > 85 else 0

    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute('''
                   INSERT INTO jugadores (club_id, nombre, posicion, edad, velocidad, resistencia,
                                          anticipacion, serenidad, trabajo_equipo, precision_pases,
                                          control_balon, profesionalidad, potencial, valor, es_estrella)
                   VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                   ''', (club_id, nombre, posicion, edad, vel, res, anti, sere, trab, pase, ctrl, prof, pot, valor,
                         es_estrella))
    conn.commit()
    conn.close()

def obtener_plantilla(club_id):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute('SELECT nombre, posicion, es_estrella, valor FROM jugadores WHERE club_id = ?', (club_id,))
    jugadores = cursor.fetchall()
    conn.close()
    return jugadores