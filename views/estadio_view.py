import discord
from db.club_queries import obtener_info_estadio
from views.plantilla_view import PlantillaPaginator
from views.ConfirmacionView import ConfirmacionMejoraView


class EstadioSelect(discord.ui.Select):
    def __init__(self, club_id):
        self.club_id = club_id
        options = [
            discord.SelectOption(label="Mejorar Estadio", value="upgrade", emoji="🏗️"),
            discord.SelectOption(label="Renombrar Estadio", value="rename", emoji="✍️"),
            discord.SelectOption(label="Ver Plantilla", value="plantilla", emoji="📋"),
        ]
        super().__init__(placeholder="Selecciona una acción...", options=options)

    async def callback(self, interaction: discord.Interaction):
        if self.values[0] == "upgrade":
            info = obtener_info_estadio(self.club_id)
            nivel_actual, capacidad_actual = info[1], info[2]
            coste = nivel_actual * 1000

            embed = discord.Embed(title="🏗️ Confirmar Mejora de Estadio", color=discord.Color.orange())
            embed.add_field(name="Estado Actual", value=f"Nivel {nivel_actual} | {capacidad_actual} asientos",
                            inline=False)
            embed.add_field(name="Tras la Mejora",
                            value=f"Nivel {nivel_actual + 1} | {capacidad_actual + 2500} asientos", inline=False)
            embed.add_field(name="💰 Coste", value=f"{coste} monedas", inline=False)

            await interaction.response.edit_message(embed=embed, view=ConfirmacionMejoraView(self.club_id, coste))

        elif self.values[0] == "plantilla":
            view = PlantillaPaginator(self.club_id)
            await interaction.response.edit_message(content="Aquí tienes tu plantilla:", embed=view.get_embed(),
                                                    view=view)

        elif self.values[0] == "rename":
            from views.modals import RenombrarEstadioModal
            await interaction.response.send_modal(RenombrarEstadioModal(self.club_id))


class EstadioView(discord.ui.View):
    def __init__(self, club_id):
        super().__init__(timeout=60)
        self.add_item(EstadioSelect(club_id))