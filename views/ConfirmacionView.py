import discord
from db.club_queries import mejorar_estadio_db
import views.estadio_view


class ConfirmacionMejoraView(discord.ui.View):
    def __init__(self, club_id, coste):
        super().__init__(timeout=60)
        self.club_id = club_id
        self.coste = coste

    @discord.ui.button(label="Aceptar", style=discord.ButtonStyle.green)
    async def aceptar(self, interaction: discord.Interaction, _button: discord.ui.Button):
        exito, nuevo_nivel = mejorar_estadio_db(self.club_id)

        if exito:
            # Crear la vista
            view = views.estadio_view.EstadioView(self.club_id, interaction.user.id)
            embed = view.actualizar_embed_inicial(self.club_id, interaction.user.id)

            await interaction.response.edit_message(
                content=f"✅ ¡Tu estadio ha sido mejorado al **Nivel {nuevo_nivel}**!",
                embed=embed,
                view=view
            )
        else:
            await interaction.response.send_message("❌ Error: No tienes saldo suficiente o hubo un problema.",
                                                    ephemeral=True)

    @discord.ui.button(label="Cancelar", style=discord.ButtonStyle.red)
    async def cancelar(self, interaction: discord.Interaction, _button: discord.ui.Button):
        # Crear la vista
        view = views.estadio_view.EstadioView(self.club_id, interaction.user.id)

        embed = view.actualizar_embed_inicial(self.club_id, interaction.user.id)

        await interaction.response.edit_message(
            content="Has cancelado la subida de nivel del estadio.",
            embed=embed,
            view=view
        )