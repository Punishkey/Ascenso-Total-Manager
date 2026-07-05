import discord
from config import COSTE_ENTRENAMIENTO, NOMBRE_MONEDA
from db.jugador_queries import obtener_lista_jugadores, entrenar_atributo, obtener_jugador_por_numero, puede_mejorar
from db.club_queries import obtener_presupuesto, restar_dinero


class EntrenamientoView(discord.ui.View):
    def __init__(self, club_id, user_id):
        super().__init__(timeout=None)
        self.club_id = club_id
        self.user_id = user_id
        self.tipo_seleccionado = None
        self.dorsal_seleccionado = None
        self.add_item(TipoEntrenamientoSelect(self))
        self.add_item(JugadorEntrenamientoSelect(club_id, self))
        self.add_item(BotonEntrenar(self))
        self.add_item(BotonVolverEstadio(club_id, user_id))


class TipoEntrenamientoSelect(discord.ui.Select):
    def __init__(self, parent_view):
        self.parent_view = parent_view
        options = [
            discord.SelectOption(label="Velocidad", value="velocidad"),
            discord.SelectOption(label="Resistencia", value="resistencia"),
            discord.SelectOption(label="Pase", value="precision_pases"),
            discord.SelectOption(label="Control", value="control_balon"),
            discord.SelectOption(label="Anticipación", value="anticipacion"),
            discord.SelectOption(label="Serenidad", value="serenidad"),
            discord.SelectOption(label="Trabajo Equipo", value="trabajo_equipo"),
            discord.SelectOption(label="Profesionalidad", value="profesionalidad")
        ]
        super().__init__(placeholder="Tipo de mejora...", options=options, row=0)

    async def callback(self, interaction: discord.Interaction):
        self.parent_view.tipo_seleccionado = self.values[0]
        await interaction.response.send_message(f"Seleccionado: {self.values[0].replace('_', ' ')}", ephemeral=True)


class JugadorEntrenamientoSelect(discord.ui.Select):
    def __init__(self, club_id, parent_view):
        self.parent_view = parent_view
        jugadores = obtener_lista_jugadores(club_id)
        options = [discord.SelectOption(label=f"#{j['numero']} {j['nombre']}", value=str(j['numero'])) for j in
                   jugadores]
        super().__init__(placeholder="Selecciona jugador...", options=options, row=1)

    async def callback(self, interaction: discord.Interaction):
        self.parent_view.dorsal_seleccionado = int(self.values[0])
        await interaction.response.send_message(f"Jugador seleccionado: #{self.values[0]}", ephemeral=True)


class BotonEntrenar(discord.ui.Button):
    def __init__(self, parent_view):
        self.parent_view = parent_view
        super().__init__(label=f"¡Entrenar! ({COSTE_ENTRENAMIENTO} {NOMBRE_MONEDA})", style=discord.ButtonStyle.green,
                         row=2)

    async def callback(self, interaction: discord.Interaction):
        if not self.parent_view.tipo_seleccionado or not self.parent_view.dorsal_seleccionado:
            await interaction.response.send_message("❌ Selecciona tipo y jugador.", ephemeral=True)
            return

        if obtener_presupuesto(self.parent_view.club_id) < COSTE_ENTRENAMIENTO:
            await interaction.response.send_message("❌ Presupuesto insuficiente.", ephemeral=True)
            return

        jugador_data = obtener_jugador_por_numero(self.parent_view.club_id, self.parent_view.dorsal_seleccionado)
        es_posible, mensaje = puede_mejorar(jugador_data, self.parent_view.tipo_seleccionado)

        if not es_posible:
            await interaction.response.send_message(f"❌ {mensaje}", ephemeral=True)
            return

        restar_dinero(self.parent_view.club_id, COSTE_ENTRENAMIENTO)
        entrenar_atributo(jugador_data[0], self.parent_view.tipo_seleccionado, 1)
        await interaction.response.send_message("✅ Entrenamiento completado.", ephemeral=True)


class BotonVolverEstadio(discord.ui.Button):
    def __init__(self, club_id, user_id):
        super().__init__(label="Volver al Estadio", style=discord.ButtonStyle.secondary, row=2)
        self.club_id = club_id
        self.user_id = user_id

    async def callback(self, interaction: discord.Interaction):
        from views.estadio_view import EstadioView
        view = EstadioView(self.club_id, self.user_id)
        await interaction.response.edit_message(content=None,
                                                embed=view.actualizar_embed_inicial(self.club_id, self.user_id),
                                                view=view)