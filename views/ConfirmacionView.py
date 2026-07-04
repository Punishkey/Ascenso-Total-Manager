import discord
from db.club_queries import mejorar_estadio_db
from views.embed_utils import crear_embed_base
import views.estadio_view


class ConfirmacionMejoraView(discord.ui.View):
    def __init__(self, club_id, coste):
        super().__init__(timeout=60)
        self.club_id = club_id
        self.coste = coste

    @discord.ui.button(label="Aceptar", style=discord.ButtonStyle.green)
    async def aceptar(self, interaction: discord.Interaction, _button: discord.ui.Button):
        # Intentamos mejorar
        exito, _ = mejorar_estadio_db(self.club_id)

        if exito:
            view = views.estadio_view.EstadioView(self.club_id, interaction.user.id)

            await interaction.response.edit_message(
                embed=crear_embed_base(self.club_id),
                view=view
            )
        else:
            # Si falla, avisamos pero no rompemos la interacción
            await interaction.response.send_message("❌ Error: No tienes saldo suficiente o hubo un problema.",
                                                    ephemeral=True)

    @discord.ui.button(label="Cancelar", style=discord.ButtonStyle.red)
    async def cancelar(self, interaction: discord.Interaction, _button: discord.ui.Button):
        view = views.estadio_view.EstadioView(self.club_id, interaction.user.id)

        await interaction.response.edit_message(
            embed=crear_embed_base(self.club_id),
            view=view
        )