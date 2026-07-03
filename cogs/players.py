import discord
from discord import app_commands
from discord.ext import commands
from db import club_queries, estadio_queries, jugador_queries
from db.transaction_queries import obtener_estadisticas_club
from views.plantilla_view import PlantillaPaginator
from views.estadio_view import EstadioView


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
        # Necesitamos el club_id para inicializar la View
        club_id = club_queries.obtener_club_id_por_usuario(interaction.user.id)

        if not club_id:
            await interaction.response.send_message("❌ No tienes un club fundado. Usa `/fundar` primero.",
                                                    ephemeral=True)
            return

        # Obtenemos info del estadio
        info = estadio_queries.obtener_info_club_y_estadio(interaction.user.id)
        stats = obtener_estadisticas_club(club_id)
        nombre_club, presupuesto, nombre_estadio, nivel, capacidad = info

        # Creamos el Embed profesional
        embed = discord.Embed(title=f"🏟️ Información de {nombre_club}", color=discord.Color.blue())
        embed.add_field(name="💰 Presupuesto", value=f"{presupuesto} monedas", inline=False)
        embed.add_field(name="📍 Nombre del Estadio", value=nombre_estadio, inline=True)
        embed.add_field(name="⭐ Nivel", value=nivel, inline=True)
        embed.add_field(name="👥 Capacidad", value=f"{capacidad} asientos", inline=True)

        historial_str = (
            f"✅ Victorias: {stats.get(1, 0)}\n"
            f"🤝 Empates: {stats.get(0, 0)}\n"
            f"❌ Derrotas: {stats.get(-1, 0)}\n"
            f"📊 Total: {stats.get('total', 0)}"
        )
        embed.add_field(name="🏆 Historial de Partidos", value=historial_str, inline=False)

        view = EstadioView(club_id, interaction.user.id)

        # Se envía con la view correctamente
        await interaction.response.send_message(embed=embed, view=view, ephemeral=True)

    @app_commands.command(name="plantilla", description="Ver los jugadores de tu equipo")
    async def plantilla(self, interaction: discord.Interaction):
        # Obtener ID del club
        club_id = club_queries.obtener_club_id_por_usuario(interaction.user.id)

        if not club_id:
            await interaction.response.send_message("❌ No tienes un club fundado. Usa `/fundar` primero.",
                                                    ephemeral=True)
            return

        # Usamos directamente el paginador
        view = PlantillaPaginator(club_id)

        # Verificamos si hay jugadores para mostrar
        if not view.jugadores:
            await interaction.response.send_message("Tu plantilla está vacía.", ephemeral=True)
            return

        await interaction.response.send_message(embed=view.get_embed(), view=view, ephemeral=True)

    @app_commands.command(name="ficha", description="Ver la ficha técnica detallada de un jugador")
    @app_commands.describe(numero="El número de dorsal del jugador")
    async def ficha(self, interaction: discord.Interaction, numero: int):
        club_id = club_queries.obtener_club_id_por_usuario(interaction.user.id)

        jugador = jugador_queries.obtener_jugador_por_numero(club_id, numero)

        if not jugador:
            await interaction.response.send_message(f"❌ No se encontró ningún jugador con el dorsal #{numero}.",
                                                    ephemeral=True)
            return

        # Desempaquetamos los datos
        (nombre, edad, vel, res, anti, sere, trab, pase, ctrl, prof, pot, valor, estrella) = jugador

        # Calculamos la media
        suma_total = vel + res + anti + sere + trab + pase + ctrl + prof + pot
        media = round(suma_total / 9)

        # Creamos el Embed detallado
        embed = discord.Embed(title=f"⚽ Ficha Técnica: {nombre} (#{numero})", color=discord.Color.blue())
        embed.add_field(name="Información", value=f"Edad: {edad}\nValor: {valor:,.0f} €", inline=False)
        embed.add_field(name="Calificación Global", value=f"⭐ {media}/100", inline=False)
        embed.add_field(name="Atributos",
                        value=f"🏃 Vel: {vel} | 🔋 Res: {res}\n👁️ Anti: {anti} | 🧘 Sere: {sere}\n🤝 Trab: {trab} | 🎯 Pase: {pase}\n⚽ Ctrl: {ctrl}",
                        inline=False)
        embed.add_field(name="Mentalidad", value=f"📈 Potencial: {pot} | 🧠 Prof: {prof}", inline=False)

        if estrella:
            embed.set_footer(text="⭐ Jugador Estrella")

        await interaction.response.send_message(embed=embed)


async def setup(bot):
    await bot.add_cog(Players(bot))