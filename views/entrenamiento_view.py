import discord

from config import COSTE_ENTRENAMIENTO
from db.jugador_queries import obtener_lista_jugadores, entrenar_atributo, obtener_jugador_por_numero, puede_mejorar
from db.club_queries import obtener_club_id_por_usuario, obtener_presupuesto, restar_dinero


class EntrenamientoView(discord.ui.View):
    def __init__(self, club_id, user_id):
        super().__init__(timeout=60)
        self.club_id = club_id
        self.user_id = user_id
        self.tipo_seleccionado = None
        self.dorsal_seleccionado = None

        self.add_item(TipoEntrenamientoSelect(self))
        self.add_item(JugadorEntrenamientoSelect(club_id, self))
        self.add_item(BotonEntrenar(self))
        self.add_item(BotonVolverEstadio())


class TipoEntrenamientoSelect(discord.ui.Select):
    def __init__(self, parent_view):
        self.parent_view = parent_view
        options = [
            discord.SelectOption(label="Físico: Velocidad", value="velocidad"),
            discord.SelectOption(label="Físico: Resistencia", value="resistencia"),
            discord.SelectOption(label="Técnico: Pase", value="precision_pases"),
            discord.SelectOption(label="Técnico: Control", value="control_balon"),
            discord.SelectOption(label="Mental: Anticipación", value="anticipacion"),
            discord.SelectOption(label="Mental: Serenidad", value="serenidad"),
            discord.SelectOption(label="Mental: Trabajo Equipo", value="trabajo_equipo"),
            discord.SelectOption(label="Mental: Profesionalidad", value="profesionalidad")
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
        self.procesando = False
        super().__init__(label=f"¡Entrenar ahora! ({COSTE_ENTRENAMIENTO} monedas)", style=discord.ButtonStyle.green, row=2)

    async def callback(self, interaction: discord.Interaction):
        # Evitar doble clic
        if self.procesando:
            return

        # Validación inicial
        if not self.parent_view.tipo_seleccionado or not self.parent_view.dorsal_seleccionado:
            await interaction.response.send_message("❌ Selecciona tipo y jugador primero.", ephemeral=True)
            return

        self.procesando = True

        # Verificar presupuesto
        if obtener_presupuesto(self.parent_view.club_id) < COSTE_ENTRENAMIENTO:
            await interaction.response.send_message(f"❌ No tienes suficientes monedas. Necesitas {COSTE_ENTRENAMIENTO}.",
                                                    ephemeral=True)
            self.procesando = False
            return

        # Obtener datos y VALIDAR desarrollo (Regla de Potencial/Edad)
        jugador_data = obtener_jugador_por_numero(self.parent_view.club_id, self.parent_view.dorsal_seleccionado)
        if not jugador_data:
            await interaction.response.send_message("❌ Error: No se encontró el jugador.", ephemeral=True)
            self.procesando = False
            return

        # Comprobación de límites de crecimiento
        es_posible, mensaje = puede_mejorar(jugador_data, self.parent_view.tipo_seleccionado)
        if not es_posible:
            await interaction.response.send_message(f"❌ {mensaje}", ephemeral=True)
            self.procesando = False
            return

        # Ejecutar mejora
        jugador_id = jugador_data[0]
        restar_dinero(self.parent_view.club_id, COSTE_ENTRENAMIENTO)
        entrenar_atributo(jugador_id, self.parent_view.tipo_seleccionado, 1)

        await interaction.response.send_message(
            f"✅ ¡Entrenamiento completado! El jugador ha mejorado su atributo {self.parent_view.tipo_seleccionado.replace('_', ' ')}.",
            ephemeral=True)
        self.procesando = False


class BotonVolverEstadio(discord.ui.Button):
    def __init__(self):
        super().__init__(label="Volver al Estadio", style=discord.ButtonStyle.secondary, row=2)

    async def callback(self, interaction: discord.Interaction):
        from views.estadio_view import EstadioView
        club_id = obtener_club_id_por_usuario(interaction.user.id)
        view = EstadioView(club_id, interaction.user.id)
        await interaction.response.edit_message(
            content=None,
            embed=view.actualizar_embed_inicial(),
            view=view
        )