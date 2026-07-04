import discord
from db.jugador_queries import obtener_lista_jugadores


class EntrenamientoView(discord.ui.View):
    def __init__(self, club_id, user_id):
        super().__init__(timeout=60)
        self.club_id = club_id
        self.user_id = user_id

        # Añadimos los selectores directamente aquí
        self.add_item(TipoEntrenamientoSelect())
        self.add_item(JugadorEntrenamientoSelect(club_id))
        self.add_item(BotonVolverEstadio())


class TipoEntrenamientoSelect(discord.ui.Select):
    def __init__(self):
        options = [
            discord.SelectOption(label="Físico (Vel/Res)", value="velocidad"),
            discord.SelectOption(label="Técnico (Pase/Ctrl)", value="precision_pases")
        ]
        super().__init__(placeholder="Selecciona el tipo de mejora...", options=options, row=0)

    async def callback(self, interaction: discord.Interaction):
        await interaction.response.send_message(f"Has seleccionado: {self.values[0]}", ephemeral=True)


class JugadorEntrenamientoSelect(discord.ui.Select):
    def __init__(self, club_id):
        jugadores = obtener_lista_jugadores(club_id)
        options = [discord.SelectOption(label=f"#{j['numero']} {j['nombre']}", value=str(j['numero'])) for j in
                   jugadores]
        super().__init__(placeholder="Selecciona al jugador...", options=options, row=1)

    async def callback(self, interaction: discord.Interaction):
        await interaction.response.send_message(f"Has seleccionado al jugador #{self.values[0]}", ephemeral=True)


class BotonVolverEstadio(discord.ui.Button):
    def __init__(self):
        super().__init__(label="Volver al Estadio", style=discord.ButtonStyle.secondary, row=2)

    async def callback(self, interaction: discord.Interaction):
        from views.estadio_view import EstadioView
        from db.club_queries import obtener_club_id_por_usuario

        club_id = obtener_club_id_por_usuario(interaction.user.id)
        view = EstadioView(club_id, interaction.user.id)

        await interaction.response.edit_message(
            content=None,
            embed=view.actualizar_embed_inicial(),
            view=view
        )