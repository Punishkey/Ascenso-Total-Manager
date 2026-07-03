import discord
from db.club_queries import obtener_info_club_y_estadio_por_club_id


def crear_embed_estadio(club_id):
    info = obtener_info_club_y_estadio_por_club_id(club_id)
    nombre_club, presupuesto, nombre_estadio, nivel, capacidad = info

    embed = discord.Embed(title=f"🏟️ Información de {nombre_club}", color=discord.Color.blue())
    embed.add_field(name="💰 Presupuesto", value=f"{presupuesto} monedas", inline=False)
    embed.add_field(name="📍 Nombre del Estadio", value=nombre_estadio, inline=True)
    embed.add_field(name="⭐ Nivel", value=str(nivel), inline=True)
    embed.add_field(name="👥 Capacidad", value=f"{capacidad} asientos", inline=True)
    return embed