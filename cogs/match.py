import asyncio
import discord
import random
from discord import app_commands
from discord.ext import commands
from config import EVENTOS_NARRATIVA
from db.club_queries import obtener_nombre_club, obtener_rival_ia, obtener_club_id_por_usuario
from db.jugador_queries import obtener_media_titular, obtener_jugador_aleatorio


async def simular_partido(interaction, club_a_id, nombre_a, club_b_id, nombre_b):
    media_a = obtener_media_titular(club_a_id)
    media_b = obtener_media_titular(club_b_id)

    # Variables para el resumen final (Diccionario para almacenar jugador y su equipo)
    historial_jugadores = {}
    tarjetas_jugadores = []
    posesion_a = 0
    posesion_b = 0

    embed = discord.Embed(title=f"⚽ {nombre_a} vs {nombre_b}", color=discord.Color.green())
    embed.add_field(name=nombre_a, value=f"Media: {media_a}\nGoles: 0", inline=True)
    embed.add_field(name=nombre_b, value=f"Media: {media_b}\nGoles: 0", inline=True)

    msg = await interaction.followup.send(embed=embed)

    goles_a = 0
    goles_b = 0

    for minuto in [5, 10, 15, 20, 25, 30, 35, 40, 45,
                   50, 55, 60, 65, 70, 75, 80, 85, 90]:
        await asyncio.sleep(5)

        # Selección de evento (Pesos ajustados para 18 eventos)
        tipo_evento = random.choices(
            list(EVENTOS_NARRATIVA.keys()),
            weights=[0.03, 0.12, 0.15, 0.10, 0.60]
        )[0]

        # Determinar quién protagoniza el evento basado en medias
        prob_a = media_a / (media_a + media_b)
        protagonista_a = random.random() < prob_a

        club_id = club_a_id if protagonista_a else club_b_id
        club_nombre = nombre_a if protagonista_a else nombre_b

        # Registrar posesión
        if protagonista_a:
            posesion_a += 1
        else:
            posesion_b += 1

        # Obtener datos
        jugador = obtener_jugador_aleatorio(club_id)
        frase = random.choice(EVENTOS_NARRATIVA[tipo_evento])
        texto = frase.format(jugador=jugador, equipo=club_nombre)

        # Registrar estadísticas incluyendo el equipo
        if jugador not in historial_jugadores:
            historial_jugadores[jugador] = {"equipo": club_nombre, "total": 0}
        historial_jugadores[jugador]["total"] += 1

        if tipo_evento == "tarjeta":
            # Elegir aleatoriamente entre amarilla o roja
            tipo_tarjeta = "🟨" if random.random() > 0.2 else "🟥"
            tarjetas_jugadores.append(f"{tipo_tarjeta} Min. {minuto}: {jugador} ({club_nombre})")

        # Cálculo de éxito si es GOL
        if tipo_evento == "gol":
            if random.random() < (media_a / (media_a + media_b) if protagonista_a else media_b / (media_a + media_b)):
                if protagonista_a:
                    goles_a += 1
                else:
                    goles_b += 1
            else:
                texto = f"¡Gran ocasión de {jugador} del equipo {club_nombre}, pero el portero lo evita!"

        # Actualización dinámica
        embed.description = f"**Minuto {minuto}'**: {texto}"
        embed.set_field_at(0, name=nombre_a, value=f"Media: {media_a}\nGoles: {goles_a}", inline=True)
        embed.set_field_at(1, name=nombre_b, value=f"Media: {media_b}\nGoles: {goles_b}", inline=True)

        await msg.edit(embed=embed)

    # --- Resumen Final ---
    total_eventos = posesion_a + posesion_b
    porcentaje_a = int((posesion_a / total_eventos) * 100)
    porcentaje_b = 100 - porcentaje_a

    # Crear barra visual (total de 10 bloques)
    bloques_a = int(porcentaje_a / 10)
    bloques_b = 10 - bloques_a
    barra_posesion = ("█" * bloques_a) + ("░" * bloques_b)

    jugador_estrella = max(historial_jugadores, key=lambda x: historial_jugadores[x]["total"])
    datos_estrella = historial_jugadores[jugador_estrella]

    resumen_embed = discord.Embed(title="📊 Resumen del Partido", color=discord.Color.green())
    resumen_embed.add_field(name="Resultado Final", value=f"**{nombre_a} {goles_a} - {goles_b} {nombre_b}**",
                            inline=False)
    resumen_embed.add_field(name="Posesión del balón", value=f"{nombre_a}: {porcentaje_a}% | {nombre_b}: {porcentaje_b}%\n`{barra_posesion}`",
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

    @app_commands.command(name="partido", description="Juega un partido amistoso contra un club de la IA")
    async def partido(self, interaction: discord.Interaction):
        club_usuario_id = obtener_club_id_por_usuario(interaction.user.id)

        if not club_usuario_id:
            await interaction.response.send_message("❌ Primero debes crear un club usando `/fundar`.",
                                                    ephemeral=True)
            return

        rival_data = obtener_rival_ia(club_usuario_id)
        if not rival_data:
            await interaction.response.send_message("❌ No hay otros clubes disponibles para jugar.", ephemeral=True)
            return

        rival_id, rival_nombre = rival_data
        club_usuario_nombre = obtener_nombre_club(club_usuario_id)

        await interaction.response.defer()
        await simular_partido(interaction, club_usuario_id, club_usuario_nombre, rival_id, rival_nombre)


async def setup(bot):
    await bot.add_cog(MatchCog(bot))