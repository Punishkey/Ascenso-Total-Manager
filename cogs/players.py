import discord
from discord import app_commands
from discord.ext import commands
from db import club_queries, estadio_queries, jugador_queries
from views.plantilla_view import PlantillaPaginator

class Players(commands.Cog):
    def __init__(self, bot):
        self.bot = bot


    @app_commands.command(name="fundar", description="Funda tu propio club de fútbol")
    async def fundar(self, interaction: discord.Interaction, nombre: str):
        # Verificamos si ya se tiene club
        if club_queries.ya_tiene_club(interaction.user.id):
            await interaction.response.send_message(
                "❌ **Error:** Ya tienes un club fundado. ¡No puedes fundar dos clubes!",
                ephemeral=True
            )
            return
        # Fundamos el club
        try:
            club_id = club_queries.crear_club(interaction.user.id, nombre)
            await interaction.response.send_message(f'¡Club "{nombre}" fundado con éxito! (ID: {club_id})')
        except Exception as e:
            print(f"Error al fundar: {e}")
            await interaction.response.send_message("Hubo un error inesperado al fundar el club.", ephemeral=True)

    @app_commands.command(name="estadio", description="Consulta los datos de tu club y estadio")
    async def estadio(self, interaction: discord.Interaction):
        # Llamamos a nuestra nueva función
        info = estadio_queries.obtener_info_club_y_estadio(interaction.user.id)

        if not info:
            await interaction.response.send_message("❌ No tienes un club fundado. Usa `/fundar` primero.",
                                                    ephemeral=True)
            return

        nombre_club, presupuesto, nombre_estadio, nivel, capacidad = info

        # Creamos el Embed profesional
        embed = discord.Embed(title=f"🏟️ Información de {nombre_club}", color=discord.Color.blue())
        embed.add_field(name="💰 Presupuesto", value=f"{presupuesto} monedas", inline=False)
        embed.add_field(name="📍 Nombre del Estadio", value=nombre_estadio, inline=True)
        embed.add_field(name="⭐ Nivel", value=nivel, inline=True)
        embed.add_field(name="👥 Capacidad", value=f"{capacidad} asientos", inline=True)

        await interaction.response.send_message(embed=embed)

    @app_commands.command(name="plantilla", description="Ver los jugadores de tu equipo")
    async def plantilla(self, interaction: discord.Interaction):
        # Obtener ID del club
        club_id = club_queries.obtener_club_id_por_usuario(interaction.user.id)

        view = PlantillaPaginator(club_id)
        await interaction.response.send_message(embed=view.get_embed(), view=view)

        if not club_id:
            await interaction.response.send_message("❌ No tienes un club fundado. Usa `/fundar` primero.",
                                                    ephemeral=True)
            return

        # Llamamos a la función de jugadores pasando el club_id
        jugadores = jugador_queries.obtener_plantilla(club_id)

        if not jugadores:
            await interaction.response.send_message("Tu plantilla está vacía.", ephemeral=True)
            return

        embed = discord.Embed(title="📋 Plantilla del Club", color=discord.Color.green())

        for j in jugadores:
            # Ahora j contiene: numero, nombre, pos, es_estrella, valor
            numero, nombre, pos, es_estrella, valor = j

            icono = "⭐" if es_estrella else ""
            # Formateamos el título del campo con el dorsal
            field_title = f"#{numero} | {nombre} ({pos}) {icono}"
            field_value = f"Valor: {valor:,} €"

            embed.add_field(name=field_title, value=field_value, inline=False)

        await interaction.response.send_message(embed=embed)

async def setup(bot):
    await bot.add_cog(Players(bot))