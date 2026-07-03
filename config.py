# Nombre del archivo de base de datos
DB_NAME = 'manager.db'


# Configuración inicial del club
CAPACIDAD_INICIAL = 5000
NIVEL_INICIAL = 1
PRESUPUESTO_INICIAL = 1000
COSTE_MEJORA_ESTADIO = 1000

# Rango de habilidades (stats) para nuevos jugadores
HABILIDAD_MIN = 50
HABILIDAD_MAX = 85



# PARTIDO
EVENTOS_NARRATIVA = {
    "gol": [
        "¡GOOOL! Gran jugada colectiva que termina en la red.",
        "¡Vaya remate de {jugador} del equipo {equipo}! El balón entra ajustado al palo.",
        "¡Golazo! {jugador} del equipo {equipo} aprovecha el espacio y define con clase."
    ],
    "ocasion": [
        "¡Qué ocasión para {equipo}! El portero la saca con los puños.",
        "{jugador} del equipo {equipo} dispara desde lejos pero el balón se va fuera por poco.",
        "Gran parada del portero tras el remate a bocajarro de {jugador} del equipo {equipo}."
    ],
    "falta": [
        "Falta cometida por {jugador} del equipo {equipo} en una zona peligrosa.",
        "El árbitro pita falta sobre {jugador} del equipo {equipo}. Se caldean los ánimos.",
        "Dura entrada de {jugador} del equipo {equipo}. El árbitro advierte al equipo."
    ],
    "tarjeta": [
        "¡Tarjeta amarilla para {jugador} del equipo {equipo} por juego peligroso!",
        "El árbitro le muestra la tarjeta roja a {jugador} del equipo {equipo}. ¡Se queda con 10!",
    ],
    "disputa": [
        "El partido sigue muy disputado en el centro del campo.",
        "Pase largo de {jugador} del equipo {equipo} que corta la defensa rival.",
        "Mucha presión en la salida de balón por parte de {equipo}."
    ]
}

# Prefijo del bot
PREFIX = '/'