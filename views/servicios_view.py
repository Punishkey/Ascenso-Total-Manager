import discord
from db.club_queries import (get_connection, mejorar_servicio_db,
                             check_y_aplicar_mejora_servicio,
                             obtener_tiempo_restante_construccion)
from db.estadio_queries import tiene_tienda_merchandising
from db.jugador_queries import obtener_media_titular
from views.modals import ConfigurarPrecioModal, ConfirmarMejoraServicioModal


class ServiciosView(discord.ui.View):
    def __init__(self, club_id, user_id):
        super().__init__(timeout=60)
        self.club_id = club_id
        self.user_id = user_id
        self.actualizar_estado_botones()

    def actualizar_estado_botones(self):
        check_y_aplicar_mejora_servicio(self.club_id, 'nivel_catering')
        check_y_aplicar_mejora_servicio(self.club_id, 'nivel_tienda')

        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute('SELECT nivel_catering, nivel_tienda FROM estadio_servicios WHERE club_id = ?', (self.club_id,))
        niveles = cursor.fetchone()
        conn.close()

        cat, tienda = niveles if niveles else (1, 0)

        tiempo_cat = obtener_tiempo_restante_construccion(self.club_id, 'catering')
        tiempo_tienda = obtener_tiempo_restante_construccion(self.club_id, 'tienda')

        if tiempo_cat and tiempo_cat != "FINALIZADO":
            self.mejorar_catering.disabled = True
            self.mejorar_catering.label = "Construyendo..."
        else:
            self.mejorar_catering.disabled = (cat >= 10)
            self.mejorar_catering.label = "Mejorar Catering"

        if tiempo_tienda and tiempo_tienda != "FINALIZADO":
            self.mejorar_tienda.disabled = True
            self.mejorar_tienda.label = "Construyendo..."
        else:
            self.mejorar_tienda.disabled = (tienda >= 10)
            self.mejorar_tienda.label = "Mejorar Tienda"

        self.embed = discord.Embed(title="🌭 Servicios del Estadio", color=discord.Color.gold())
        self.embed.add_field(name="Catering", value=f"Nivel: **{cat}**", inline=True)
        self.embed.add_field(name="Tienda", value=f"Nivel: **{tienda}**", inline=True)
        self.embed.description = "Mejora tus servicios para aumentar los ingresos. Las obras tardan 6h + 1h por nivel."

    @discord.ui.button(label="Mejorar Catering", style=discord.ButtonStyle.primary, emoji="🌭")
    async def mejorar_catering(self, interaction: discord.Interaction, _button: discord.ui.Button):
        # Obtenemos nivel actual para el modal
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute('SELECT nivel_catering FROM estadio_servicios WHERE club_id = ?', (self.club_id,))
        nivel = cursor.fetchone()[0]
        conn.close()

        modal = ConfirmarMejoraServicioModal(self.club_id, 'nivel_catering', nivel,
                                             lambda: self._refresh_view(interaction))
        await interaction.response.send_modal(modal)

    @discord.ui.button(label="Mejorar Tienda", style=discord.ButtonStyle.primary, emoji="👕")
    async def mejorar_tienda(self, interaction: discord.Interaction, _button: discord.ui.Button):
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute('SELECT nivel_tienda FROM estadio_servicios WHERE club_id = ?', (self.club_id,))
        nivel = cursor.fetchone()[0]
        conn.close()

        modal = ConfirmarMejoraServicioModal(self.club_id, 'nivel_tienda', nivel,
                                             lambda: self._refresh_view(interaction))
        await interaction.response.send_modal(modal)

    @discord.ui.button(label="Gestionar Precios Camisetas de Todo el Club", style=discord.ButtonStyle.secondary, emoji="💰")
    async def gestionar_precios(self, interaction: discord.Interaction, _button: discord.ui.Button):
        if not tiene_tienda_merchandising(self.club_id):
            await interaction.response.send_message("❌ Debes construir la tienda primero.", ephemeral=True)
            return

        # Obtenemos la media real
        media_club = obtener_media_titular(self.club_id)

        # Pasamos la media real al modal
        await interaction.response.send_modal(ConfigurarPrecioModal(self.club_id, media_club))