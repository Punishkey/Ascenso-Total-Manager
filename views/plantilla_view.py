import discord
from db.jugador_queries import obtener_plantilla


class PlantillaPaginator(discord.ui.View):
    def __init__(self, club_id):
        super().__init__(timeout=60)
        self.club_id = club_id
        self.jugadores = obtener_plantilla(club_id)
        self.page = 0
        self.per_page = 6
        self.total_pages = (len(self.jugadores) - 1) // self.per_page
        self.update_buttons()

    def get_embed(self):
        start = self.page * self.per_page
        end = start + self.per_page
        pagina = self.jugadores[start:end]

        embed = discord.Embed(title=f"📋 Plantilla (Pág {self.page + 1}/{self.total_pages + 1})",
                              color=discord.Color.green())
        for j in pagina:
            num, nom, pos, est, val = j
            icono = "⭐" if est else ""
            valor_formateado = f"{val:,.0f} €"
            embed.add_field(name=f"#{num} | {pos} - {nom} {icono}",
                            value=f"Valor: {valor_formateado}", inline=False)
        return embed

    def update_buttons(self):
        self.children[0].disabled = (self.page == 0)  # Deshabilita "Anterior" en pág 1
        self.children[1].disabled = (self.page == self.total_pages) # Deshabilita "Siguiente" en última

    @discord.ui.button(label="⬅️ Anterior", style=discord.ButtonStyle.secondary)
    async def anterior(self, interaction: discord.Interaction, _button: discord.ui.Button):
        self.page -= 1
        self.update_buttons()
        await interaction.response.edit_message(embed=self.get_embed(), view=self)

    @discord.ui.button(label="Siguiente ➡️", style=discord.ButtonStyle.secondary)
    async def siguiente(self, interaction: discord.Interaction, _button: discord.ui.Button):
        self.page += 1
        self.update_buttons()  # Actualizamos estado
        await interaction.response.edit_message(embed=self.get_embed(), view=self)