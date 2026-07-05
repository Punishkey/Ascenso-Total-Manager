import discord
from discord import app_commands
from discord.ext import commands
from db import club_queries
from views.menu_view import enviar_manual_tutorial
from views.estadio_view import EstadioView


class Players(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @app_commands.command(name="comenzar", description="Comando inicial de Ascenso Total Manager")
    async def comenzar(self, interaction: discord.Interaction):
        await enviar_manual_tutorial(interaction)

    @app_commands.command(name="estadio", description="Consulta los datos de tu club y estadio")
    async def estadio(self, interaction: discord.Interaction):
        club_id = club_queries.obtener_club_id_por_usuario(interaction.user.id)

        if not club_id:
            await interaction.response.send_message("❌ No tienes un club fundado. Usa `/comenzar` primero.",
                                                    ephemeral=True)
            return

        view = EstadioView(club_id, interaction.user.id)
        embed = view.actualizar_embed_inicial(club_id, interaction.user.id)

        await interaction.response.send_message(embed=embed, view=view, ephemeral=True)


async def setup(bot):
    await bot.add_cog(Players(bot))