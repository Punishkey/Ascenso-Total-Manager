import discord
from db.jugador_queries import obtener_plantilla


class PlantillaPaginator(discord.ui.View):
    def __init__(self, club_id):
        super().__init__(timeout=60)
        self.club_id = club_id
        self.jugadores = obtener_plantilla(club_id)
        self.page = 0
        self.per_page = 6
        self.total_pages = (len(self.jugadores) - 1) // self.per_page if self.jugadores else 0
        self.update_buttons()

    def get_embed(self):
        start = self.page * self.per_page
        end = start + self.per_page
        pagina = self.jugadores[start:end]

        embed = discord.Embed(title=f"📋 Plantilla (Pág {self.page + 1}/{self.total_pages + 1})",
                              color=discord.Color.green())

        for j in pagina:
            # Desempaquetamos incluyendo la media
            num, nom, pos, est, val, media = j
            icono = "⭐" if est else ""
            valor_formateado = f"{val:,.0f} €"

            # Mostramos la Media y el Valor en el mismo campo
            field_name = f"#{num} | {nom} ({pos}) {icono}"
            field_value = f"Media: **{int(media)}** | Valor: {valor_formateado}"

            embed.add_field(name=field_name, value=field_value, inline=False)

        return embed

    def update_buttons(self):
        # Evitamos errores si no hay jugadores
        if self.total_pages < 0:
            return
        self.children[0].disabled = (self.page == 0)
        self.children[1].disabled = (self.page >= self.total_pages)

    @discord.ui.button(label="⬅️ Anterior", style=discord.ButtonStyle.secondary)
    async def anterior(self, interaction: discord.Interaction, _button: discord.ui.Button):
        if self.page > 0:
            self.page -= 1
            self.update_buttons()
            await interaction.response.edit_message(embed=self.get_embed(), view=self)

    @discord.ui.button(label="Siguiente ➡️", style=discord.ButtonStyle.secondary)
    async def siguiente(self, interaction: discord.Interaction, _button: discord.ui.Button):
        if self.page < self.total_pages:
            self.page += 1
            self.update_buttons()
            await interaction.response.edit_message(embed=self.get_embed(), view=self)