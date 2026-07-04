import discord
from db.jugador_queries import obtener_plantilla
from utils.ficha_utils import mostrar_ficha_jugador


class PlantillaSelect(discord.ui.Select):
    def __init__(self, jugadores_pagina, club_id):
        self.club_id = club_id
        options = [
            discord.SelectOption(label=f"Ficha: {j[1]} (#{j[0]})", value=str(j[0]))
            for j in jugadores_pagina
        ]
        super().__init__(placeholder="Selecciona un jugador para ver su ficha...", options=options, row=2)

    async def callback(self, interaction: discord.Interaction):
        await mostrar_ficha_jugador(interaction, self.club_id, int(self.values[0]))


class PlantillaPaginator(discord.ui.View):
    def __init__(self, club_id, user_id):
        super().__init__(timeout=60)
        self.club_id = club_id
        self.user_id = user_id
        self.jugadores = obtener_plantilla(club_id)
        self.page = 0
        self.per_page = 6
        self.total_pages = (len(self.jugadores) - 1) // self.per_page if self.jugadores else 0
        self.update_view()

    def get_embed(self):
        start = self.page * self.per_page
        end = start + self.per_page
        pagina_actual = self.jugadores[start:end]

        embed = discord.Embed(title=f"📋 Plantilla (Pág {self.page + 1}/{self.total_pages + 1})",
                              color=discord.Color.green())

        for j in pagina_actual:
            num, nom, pos, est, val, media = j
            icono = "⭐" if est else ""
            field_name = f"#{num} | {nom} ({pos}) {icono}"
            field_value = f"Media: **{int(media)}** | Valor: {val:,.0f} €"
            embed.add_field(name=field_name, value=field_value, inline=False)
        return embed

    def update_view(self):
        self.update_buttons()
        # Eliminar selects previos
        for item in [i for i in self.children if isinstance(i, PlantillaSelect)]:
            self.remove_item(item)

        start = self.page * self.per_page
        end = start + self.per_page
        pagina_actual = self.jugadores[start:end]

        if pagina_actual:
            self.add_item(PlantillaSelect(pagina_actual, self.club_id))

    def update_buttons(self):
        if self.total_pages < 0: return
        self.children[1].disabled = (self.page == 0)  # Anterior
        self.children[2].disabled = (self.page >= self.total_pages)  # Siguiente

    @discord.ui.button(label="⬅️ Volver a Estadio", style=discord.ButtonStyle.primary, row=1)
    async def volver_estadio(self, interaction: discord.Interaction, _button: discord.ui.Button):
        from views.estadio_view import EstadioView
        view = EstadioView(self.club_id, self.user_id)
        await interaction.response.edit_message(content=None, embed=view.actualizar_embed_inicial(self.club_id, self.user_id), view=view)

    @discord.ui.button(label="⬅️ Anterior", style=discord.ButtonStyle.secondary, row=0)
    async def anterior(self, interaction: discord.Interaction, _button: discord.ui.Button):
        self.page -= 1
        self.update_view()
        await interaction.response.edit_message(embed=self.get_embed(), view=self)

    @discord.ui.button(label="Siguiente ➡️", style=discord.ButtonStyle.secondary, row=0)
    async def siguiente(self, interaction: discord.Interaction, _button: discord.ui.Button):
        self.page += 1
        self.update_view()
        await interaction.response.edit_message(embed=self.get_embed(), view=self)