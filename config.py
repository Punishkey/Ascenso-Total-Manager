# Nombre del archivo de base de datos
DB_NAME = 'manager.db'


# Configuración inicial del club
NOMBRE_MONEDA = "keycoins"
NOMBRE_MONEDA_ESPECIAL = "Gaecoins"
CAPACIDAD_INICIAL = 5000
CAPACIDAD_POR_NIVEL = 2500
NIVEL_INICIAL = 1
PRESUPUESTO_INICIAL = 1000
COSTE_MEJORA_ESTADIO = 1000
TIEMPO_MEJORA_ESTADIO = 6
COSTE_MEJORA_SERVICIOS = 20000
NIVEL_MAXIMO_MEJORA_SERVICIOS = 10

# Rango de habilidades (stats) para nuevos jugadores
HABILIDAD_MIN = 46
HABILIDAD_MAX = 60

# Camisetas
# Media 60 = 40 Keycoins.
# Media 99 (una estrella top) = 150 Keycoins.
# Precio = 40 + (Media - 60) * 2.82
# Si Media = 60:40 + (0) = 40.
# Si Media = 99:40 + (39 * 2.82) approx 150.





# ENTRENAMIENTO

# --- Configuración de Desarrollo de Jugadores ---
EDAD_JOVEN = 24           # Edad hasta la que suben sin penalizaciones
EDAD_DECLIVE = 32         # Edad a partir de la cual empiezan a bajar atributos físicos
POTENCIAL_FACTOR = 10     # Multiplicador del potencial para definir el techo (pot 8 * 10 = 80)
COSTE_ENTRENAMIENTO = 100


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
        "entrada peligrosa de {jugador} del equipo {equipo}.",
        "discusión fuerte de {jugador} del equipo {equipo} con el árbitro.",
        "{jugador} del equipo {equipo} corta un contraataque con falta."
    ],
    "disputa": [
        "El partido sigue muy disputado en el centro del campo.",
        "Pase largo de {jugador} del equipo {equipo} que corta la defensa rival.",
        "Mucha presión en la salida de balón por parte de {equipo}."
    ]
}

BONUS_RESULTADO = 100
BASE_POR_PARTIDO = 200

# Prefijo del bot
PREFIX = '/'