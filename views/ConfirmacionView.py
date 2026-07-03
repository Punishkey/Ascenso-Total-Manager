import discord
from db.club_queries import mejorar_estadio_db
from views.embed_utils import crear_embed_estadio
# Usamos un import diferido o directo
import views.estadio_view

class ConfirmacionMejoraView(discord.ui.View):
    def __init__(self, club_id, coste):
        super().__init__(timeout=60)
        self.club_id = club_id
        self.coste = coste

    @discord.ui.button(label="Aceptar", style=discord.ButtonStyle.green)
    async def aceptar(self, interaction: discord.Interaction, _button: discord.ui.Button):
        exito, _ = mejorar_estadio_db(self.club_id)
        if exito:
            await interaction.response.edit_message(
                embed=crear_embed_estadio(self.club_id),
                view=views.estadio_view.EstadioView(self.club_id)
            )
        else:
            await interaction.response.send_message("❌ Error: No tienes saldo suficiente.", ephemeral=True)

    @discord.ui.button(label="Cancelar", style=discord.ButtonStyle.red)
    async def cancelar(self, interaction: discord.Interaction, _button: discord.ui.Button):
        await interaction.response.edit_message(
            embed=crear_embed_estadio(self.club_id),
            view=views.estadio_view.EstadioView(self.club_id)
        )