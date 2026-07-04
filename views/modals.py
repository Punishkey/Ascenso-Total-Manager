import discord
from db.estadio_queries import renombrar_estadio_db


class RenombrarEstadioModal(discord.ui.Modal, title="Renombrar Estadio"):
    nuevo_nombre = discord.ui.TextInput(
        label="Nuevo nombre del estadio",
        style=discord.TextStyle.short,
        placeholder="Ej: Nuevo Santiago Bernabéu",
        required=True,
        min_length=3,
        max_length=50,
    )

    def __init__(self, club_id):
        super().__init__()
        self.club_id = club_id

    async def on_submit(self, interaction: discord.Interaction):
        exito = renombrar_estadio_db(self.club_id, self.nuevo_nombre.value)

        if exito:
            from views.estadio_view import EstadioView
            view = EstadioView(self.club_id, interaction.user.id)
            embed = view.actualizar_embed_inicial(self.club_id, interaction.user.id)

            await interaction.response.edit_message(
                content=None,
                embed=embed,
                view=view
            )
        else:
            await interaction.response.send_message("❌ Error al renombrar el estadio.", ephemeral=True)