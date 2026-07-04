import asyncio
import discord
import random
from discord import app_commands
from discord.ext import commands
from config import EVENTOS_NARRATIVA
from db.club_queries import obtener_nombre_club, obtener_rival_ia, obtener_club_id_por_usuario
from db.jugador_queries import obtener_media_titular, obtener_jugador_aleatorio
from db.transaction_queries import registrar_resultado_partido


async def simular_partido(interaction, club_a_id, nombre_a, club_b_id, nombre_b):
    media_a = obtener_media_titular(club_a_id)
    media_b = obtener_media_titular(club_b_id)

    historial_jugadores = {}
    estado_tarjetas = {}  # Inicializado fuera del bucle
    tarjetas_jugadores = []
    posesion_a = 0
    posesion_b = 0

    embed = discord.Embed(title=f"⚽ {nombre_a} vs {nombre_b}", color=discord.Color.green())
    embed.add_field(name=nombre_a, value=f"Media: {media_a:.1f}\nGoles: 0", inline=True)
    embed.add_field(name=nombre_b, value=f"Media: {media_b:.1f}\nGoles: 0", inline=True)

    msg = await interaction.followup.send(embed=embed)

    goles_a = 0
    goles_b = 0

    for minuto in [5, 10, 15, 20, 25, 30, 35, 40, 45,
                   50, 55, 60, 65, 70, 75, 80, 85, 90]:
        await asyncio.sleep(5)

        tipo_evento = random.choices(
            list(EVENTOS_NARRATIVA.keys()),
            weights=[0.03, 0.12, 0.15, 0.10, 0.60]
        )[0]

        prob_a = media_a / (media_a + media_b)
        protagonista_a = random.random() < prob_a

        club_id = club_a_id if protagonista_a else club_b_id
        club_nombre = nombre_a if protagonista_a else nombre_b

        if protagonista_a:
            posesion_a += 1
        else:
            posesion_b += 1

        jugador = obtener_jugador_aleatorio(club_id)

        # Corrección: Incrementar historial siempre
        if jugador not in historial_jugadores:
            historial_jugadores[jugador] = {"equipo": club_nombre, "total": 0}
        historial_jugadores[jugador]["total"] += 1

        texto = ""  # Inicializar variable de texto

        if tipo_evento == "tarjeta":
            # Inicializar jugador en estado_tarjetas
            if jugador not in estado_tarjetas:
                estado_tarjetas[jugador] = {"amarillas": 0, "expulsado": False}

            # Si ya fue expulsado, ignoramos el evento
            if estado_tarjetas[jugador]["expulsado"]:
                continue

            es_roja_directa = random.random() < 0.2

            if es_roja_directa:
                estado_tarjetas[jugador]["expulsado"] = True
                tipo_tarjeta = "🟥"
                nombre_tarjeta = "Roja"
            else:
                estado_tarjetas[jugador]["amarillas"] += 1
                if estado_tarjetas[jugador]["amarillas"] >= 2:
                    estado_tarjetas[jugador]["expulsado"] = True
                    tipo_tarjeta = "🟥"
                    nombre_tarjeta = "Roja (por doble amarilla)"
                else:
                    tipo_tarjeta = "🟨"
                    nombre_tarjeta = "Amarilla"

            texto = f"{tipo_tarjeta} **{nombre_tarjeta}**: El árbitro amonesta a {jugador} del equipo {club_nombre}."

            registro = f"{tipo_tarjeta} {nombre_tarjeta} | Min. {minuto}: {jugador} ({club_nombre})"
            if registro not in tarjetas_jugadores:
                tarjetas_jugadores.append(registro)

            if estado_tarjetas[jugador]["expulsado"]:
                if protagonista_a:
                    media_a -= 5
                else:
                    media_b -= 5

        elif tipo_evento == "gol":
            frase = random.choice(EVENTOS_NARRATIVA[tipo_evento])
            if random.random() < (media_a / (media_a + media_b) if protagonista_a else media_b / (media_a + media_b)):
                texto = frase.format(jugador=jugador, equipo=club_nombre)
                if protagonista_a:
                    goles_a += 1
                else:
                    goles_b += 1
            else:
                texto = f"¡Gran ocasión de {jugador} del equipo {club_nombre}, pero el portero lo evita!"
        else:
            # Eventos normales (falta, disputa, ocasion)
            frase = random.choice(EVENTOS_NARRATIVA[tipo_evento])
            texto = frase.format(jugador=jugador, equipo=club_nombre)

        embed.description = f"**Minuto {minuto}'**: {texto}"
        embed.set_field_at(0, name=nombre_a, value=f"Media: {media_a:.1f}\nGoles: {goles_a}", inline=True)
        embed.set_field_at(1, name=nombre_b, value=f"Media: {media_b:.1f}\nGoles: {goles_b}", inline=True)

        await msg.edit(embed=embed)

    # Registro en BD
    registrar_resultado_partido(club_a_id, club_b_id, goles_a, goles_b)

    # --- Resumen Final ---
    total_eventos = posesion_a + posesion_b
    porcentaje_a = int((posesion_a / total_eventos) * 100) if total_eventos > 0 else 50
    porcentaje_b = 100 - porcentaje_a
    bloques_a = int(porcentaje_a / 10)
    barra_posesion = ("█" * bloques_a) + ("░" * (10 - bloques_a))

    jugador_estrella = max(historial_jugadores, key=lambda x: historial_jugadores[x]["total"])
    datos_estrella = historial_jugadores[jugador_estrella]

    resumen_embed = discord.Embed(title="📊 Resumen del Partido", color=discord.Color.green())
    resumen_embed.add_field(name="Resultado Final", value=f"**{nombre_a} {goles_a} - {goles_b} {nombre_b}**",
                            inline=False)
    resumen_embed.add_field(name="Posesión del balón",
                            value=f"{nombre_a}: {porcentaje_a}% | {nombre_b}: {porcentaje_b}%\n`{barra_posesion}`",
                            inline=False)
    resumen_embed.add_field(name="Jugador Destacado",
                            value=f"⭐ {jugador_estrella} ({datos_estrella['equipo']}) con {datos_estrella['total']} intervenciones",
                            inline=False)

    if tarjetas_jugadores:
        resumen_embed.add_field(name="Tarjetas Mostradas", value="\n".join(tarjetas_jugadores), inline=False)
    else:
        resumen_embed.add_field(name="Tarjetas Mostradas", value="Partido limpio.", inline=False)

    await interaction.followup.send(embed=resumen_embed)


class MatchCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.jugadores_en_partido = set()

    @app_commands.command(name="partido", description="Juega un partido amistoso contra un club de la IA")
    async def partido(self, interaction: discord.Interaction):
        user_id = interaction.user.id
        if user_id in self.jugadores_en_partido:
            await interaction.response.send_message("❌ ¡Ya tienes un partido en curso! Espera a que termine.",
                                                    ephemeral=True)
            return

        club_usuario_id = obtener_club_id_por_usuario(interaction.user.id)
        if not club_usuario_id:
            await interaction.response.send_message("❌ Primero debes crear un club usando `/comenzar`.", ephemeral=True)
            return

        rival_data = obtener_rival_ia(club_usuario_id)
        if not rival_data:
            await interaction.response.send_message("❌ No hay otros clubes disponibles para jugar.", ephemeral=True)
            return

        rival_id, rival_nombre = rival_data
        club_usuario_nombre = obtener_nombre_club(club_usuario_id)

        self.jugadores_en_partido.add(user_id)
        await interaction.response.defer()

        try:
            await simular_partido(interaction, club_usuario_id, club_usuario_nombre, rival_id, rival_nombre)
        finally:
            self.jugadores_en_partido.remove(user_id)


async def setup(bot):
    await bot.add_cog(MatchCog(bot))