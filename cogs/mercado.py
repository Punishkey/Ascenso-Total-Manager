import discord
from discord import app_commands
from discord.ext import commands
from db import jugador_queries, club_queries
from db.mercado_queries import publicar_jugador
from views.mercado_view import MercadoView


class MercadoCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @app_commands.command(name="vender", description="Pon a un jugador de tu plantilla en el mercado")
    @app_commands.describe(dorsal="El número de dorsal del jugador", precio="Precio de venta en monedas")
    async def vender(self, interaction: discord.Interaction, dorsal: int, precio: int):
        club_id = club_queries.obtener_club_id_por_usuario(interaction.user.id)

        if not club_id:
            await interaction.response.send_message("❌ Primero debes tener un club fundado.", ephemeral=True)
            return

        # Obtenemos al jugador
        jugador = jugador_queries.obtener_jugador_por_numero(club_id, dorsal)
        if not jugador:
            await interaction.response.send_message("❌ No tienes ningún jugador con ese dorsal.", ephemeral=True)
            return

        # Publicamos en mercado
        jugador_id = jugador[0]
        nombre_jugador = jugador[1]
        if publicar_jugador(jugador_id, club_id, precio):
            await interaction.response.send_message(
                f"✅ ¡¡{nombre_jugador} (dorsal #{dorsal}) ha sido puesto en el mercado por {precio} monedas!",
                ephemeral=True)
        else:
            await interaction.response.send_message("❌ Error: Este jugador ya está en el mercado o hubo un problema.",
                                                    ephemeral=True)

    # SE COMENTA YA QUE SE IMPLEMENTA EL MERCADO EN LA VISTA ESTADIO
    # @app_commands.command(name="mercado", description="Accede al mercado de fichajes")
    # async def mercado(self, interaction: discord.Interaction):
    #     # Creamos la vista pasando el ID del usuario
    #     view = MercadoView(interaction.user.id)
    #
    #     # Comprobamos si hay jugadores antes de enviar
    #     if not view.jugadores:
    #         await interaction.response.send_message(
    #             "🛒 El mercado está vacío actualmente. ¡Sé el primero en vender!",
    #             ephemeral=True
    #         )
    #         return
    #
    #     # Enviamos el mercado
    #     await interaction.response.send_message(embed=view.get_embed(), view=view, ephemeral=True)


async def setup(bot):
    await bot.add_cog(MercadoCog(bot))