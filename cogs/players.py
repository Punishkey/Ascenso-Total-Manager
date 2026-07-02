import discord
from discord import app_commands
from discord.ext import commands
import database


class Players(commands.Cog):
    def __init__(self, bot):
        self.bot = bot


    @app_commands.command(name="fundar", description="Funda tu propio club de fútbol")
    async def fundar(self, interaction: discord.Interaction, nombre: str):
        # Llamamos a la lógica
        club_id = database.crear_club(interaction.user.id, nombre)

        await interaction.response.send_message(f'¡Club "{nombre}" fundado con éxito! (ID: {club_id})')


async def setup(bot):
    await bot.add_cog(Players(bot))